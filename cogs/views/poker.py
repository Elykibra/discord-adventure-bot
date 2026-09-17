# cogs/views/poker.py
#
# Texas Hold'em — Phase 2 (table creation/lobby) + Phase 3 (dealing hole
# cards, posting blinds, the private "View My Hand" reveal). Betting rounds
# and showdown land in later phases on top of this. Buy-ins/cash-outs are
# the only points that touch the database — same "DB only at checkpoints"
# approach as the dungeon and blackjack; nothing mid-hand writes to it.
#
# Every button here guards against double-click races the same way the
# dungeon and blackjack views do: a `busy` flag checked in interaction_check,
# released once the view reaches a new stable state via rebuild_items().
# Unlike those views, multiple *different* people are meant to interact with
# this one (anyone can Join/Leave), so the guard is table-wide rather than
# tied to a single owner.

import asyncio

import discord

from data.poker import STAKE_TIERS, new_shuffled_deck, format_cards, best_hand_from_7, hand_name

MIN_PLAYERS_TO_START = 2
MAX_PLAYERS = 6
MIN_CUSTOM_BUY_IN = 20
MIN_CUSTOM_SMALL_BLIND = 1
TURN_TIMEOUT_SECONDS = 30

STAGE_NAMES = ["Pre-Flop", "Flop", "Turn", "River", "Showdown"]


class PokerPlayer:
    def __init__(self, user_id: int, name: str, stack: int):
        self.user_id = user_id
        self.name = name
        self.stack = stack
        self.hole: list = []
        self.folded = False
        self.bet = 0          # this betting round's contribution so far
        self.contributed = 0  # this whole hand's contribution — drives side-pot eligibility
        self.acted = False


class PokerTableView(discord.ui.View):
    def __init__(self, db_cog, host: discord.Member, stake: dict):
        super().__init__(timeout=None)  # a lobby can sit open for a while waiting on players
        self.db_cog = db_cog
        self.host_id = host.id
        self.stake = stake
        self.players: list[PokerPlayer] = [PokerPlayer(host.id, host.display_name, stake["buy_in"])]
        self.pending: list[PokerPlayer] = []  # joined mid-session — seated in at the next deal, not this one
        self.started = False
        self.closed = False
        self.message: discord.Message | None = None
        self.table_key: str | None = None  # set once the table's message exists — see save_snapshot()
        self.busy = False
        self.hand_number = 0

        # Set once dealing happens — see deal_hand().
        self.deck: list = []
        self.community: list = []
        self.pot = 0
        self.dealer_idx = 0
        self.sb_idx = 0
        self.bb_idx = 0
        self.stage = 0  # index into STAGE_NAMES; >=4 means the hand is fully resolved
        self.current_bet = 0
        self.min_raise_increment = 0
        self.turn_idx = 0
        self.result_text = ""
        self._pending_hand_result: dict | None = None  # set by resolve_fold_win/resolve_showdown — see record_hand_stats()

        # Per-turn auto-fold timer — see start_turn_timer()/cancel_turn_timer().
        # turn_token is bumped every time the "current turn" changes, so a
        # timer that fires after the turn has already moved on (acted upon
        # manually, or already timed out once) can tell it's stale and no-op.
        self.turn_token = 0
        self.turn_task: asyncio.Task | None = None

        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def find_player(self, user_id: int) -> PokerPlayer | None:
        return next((p for p in self.players if p.user_id == user_id), None)

    def deal_hand(self):
        """Shuffles, deals 2 hole cards to everyone, and posts blinds.
        The dealer button starts on the last seated player for the table's
        first hand (arbitrary — there's no "previous" position yet), then
        rotates one seat per hand after that. Note this rotates by *index*,
        not by tracking the same physical seat across busts/new joins — a
        reasonable simplification rather than a fully seat-stable button."""
        self.deck = new_shuffled_deck()
        for p in self.players:
            p.hole = [self.deck.pop(), self.deck.pop()]
            p.folded = False
            p.bet = 0
            p.contributed = 0
            p.acted = False

        n = len(self.players)
        if self.hand_number == 0:
            self.dealer_idx = n - 1
        else:
            self.dealer_idx = (self.dealer_idx + 1) % n
        self.hand_number += 1

        if n == 2:
            # Heads-up plays by different rules: the dealer posts the small
            # blind (and acts first preflop), the other player posts the big
            # blind. The general n+1/n+2 formula below is for 3+ players.
            self.sb_idx = self.dealer_idx
            self.bb_idx = (self.dealer_idx + 1) % n
        else:
            self.sb_idx = (self.dealer_idx + 1) % n
            self.bb_idx = (self.dealer_idx + 2) % n

        sb_player = self.players[self.sb_idx]
        bb_player = self.players[self.bb_idx]
        sb_amount = min(self.stake["small_blind"], sb_player.stack)
        bb_amount = min(self.stake["big_blind"], bb_player.stack)
        sb_player.stack -= sb_amount
        bb_player.stack -= bb_amount
        sb_player.bet = sb_amount
        bb_player.bet = bb_amount
        sb_player.contributed = sb_amount
        bb_player.contributed = bb_amount
        self.pot = sb_amount + bb_amount

        self.community = []
        self.stage = 0
        self.current_bet = bb_amount
        self.min_raise_increment = self.stake["big_blind"]
        self.result_text = ""

        # Preflop action starts left of the big blind (3+ players), or with
        # the dealer/SB in heads-up (see the heads-up note above).
        start = self.dealer_idx if n == 2 else (self.bb_idx + 1) % n
        self.turn_idx = self.first_active_from(start)
        self.start_turn_timer()

    # --- Per-turn timeout ---
    def cancel_turn_timer(self):
        if self.turn_task and not self.turn_task.done():
            self.turn_task.cancel()
        self.turn_task = None

    def start_turn_timer(self):
        """(Re)arms the auto-fold timer for whoever's turn it is right now.
        Safe to call freely — always cancels any previous timer first, and
        bumps turn_token so a previous timer waking up later recognizes
        it's stale and does nothing."""
        self.cancel_turn_timer()
        self.turn_token += 1
        self.turn_task = asyncio.create_task(self._turn_timeout_watcher(self.turn_token))

    async def _turn_timeout_watcher(self, token: int):
        try:
            await asyncio.sleep(TURN_TIMEOUT_SECONDS)
        except asyncio.CancelledError:
            return
        if token != self.turn_token or self.closed or not self.started or self.stage >= 4:
            return
        if not self.players or self.turn_idx >= len(self.players):
            return  # the player on the clock left mid-hand — nothing sane to auto-act on
        await self._auto_act_timeout()

    async def _auto_act_timeout(self):
        player = self.players[self.turn_idx]
        call_amount = self.current_bet - player.bet
        if call_amount > 0:
            player.folded = True
            note = f"⏱️ **{player.name}** took too long and was auto-folded."
        else:
            note = f"⏱️ **{player.name}** took too long and auto-checked."
        player.acted = True

        result = self.advance_after_action()
        self.rebuild_items()
        self.result_text = f"{note}\n\n{self.result_text}" if self.result_text else note

        if self.message:
            try:
                await self.message.edit(embed=self.build_embed(), view=self)
            except discord.HTTPException:
                pass
        if result in ("fold_win", "showdown"):
            await self.save_snapshot()
            await self.record_hand_stats()

    # --- Restart safety net (see migrations/018) ---
    def current_stacks(self) -> dict:
        stacks = {str(p.user_id): p.stack for p in self.players}
        stacks.update({str(p.user_id): p.stack for p in self.pending})
        return stacks

    async def save_snapshot(self):
        if not self.table_key:
            return
        await self.db_cog.save_poker_snapshot(self.table_key, self.current_stacks())

    async def clear_snapshot(self):
        if not self.table_key:
            return
        await self.db_cog.clear_poker_snapshot(self.table_key)

    async def close_and_refund(self):
        """Shared close path for both an explicit host-leave and an
        auto-close when the table's dwindled below playable — refunds
        everyone still seated/pending, closes the view, and stops the
        timer/snapshot from lingering after nobody can act on them again.
        Can run mid-hand (nothing currently stops someone from leaving
        while a hand's in progress), so any chips already bet into
        self.pot this hand get split among whoever's still seated first —
        otherwise that money would just vanish, credited to nobody."""
        if self.pot > 0 and self.players:
            share = self.pot // len(self.players)
            leftover = self.pot - share * len(self.players)
            for i, p in enumerate(self.players):
                p.stack += share + (leftover if i == 0 else 0)
            self.pot = 0

        for p in self.players + self.pending:
            await self.db_cog.add_chips(p.user_id, p.stack)
        self.players.clear()
        self.pending.clear()
        self.closed = True
        self.cancel_turn_timer()
        self.rebuild_items()
        self.stop()
        await self.clear_snapshot()

    # --- Stats & history ---
    async def record_hand_stats(self):
        """Persists the outcome of the hand that just resolved — see the
        _pending_hand_result set by resolve_fold_win()/resolve_showdown().
        Called from the same checkpoints as save_snapshot()."""
        data = self._pending_hand_result
        self._pending_hand_result = None
        if not data:
            return
        await self.db_cog.record_poker_hand(
            self.table_key or "unknown", self.stake["name"], data["pot"], data["players"]
        )

    # --- Turn / round-state helpers ---
    def first_active_from(self, start_idx: int) -> int:
        """The first player at/after start_idx who can still act (not folded, has chips)."""
        n = len(self.players)
        for step in range(n):
            idx = (start_idx + step) % n
            p = self.players[idx]
            if not p.folded and p.stack > 0:
                return idx
        return start_idx

    def active_players(self) -> list:
        return [p for p in self.players if not p.folded]

    def can_act_players(self) -> list:
        return [p for p in self.players if not p.folded and p.stack > 0]

    def round_complete(self) -> bool:
        active = self.active_players()
        if len(active) <= 1:
            return True
        can_act = self.can_act_players()
        if not can_act:
            return True  # everyone left is all-in — nothing more to bet
        return all(p.acted and p.bet == self.current_bet for p in can_act)

    def advance_after_action(self):
        """Called after any Fold/Check/Call/Raise resolves. Returns one of
        'fold_win', 'showdown', or 'continue' — the caller decides what to
        show based on that."""
        active = self.active_players()
        if len(active) <= 1:
            self.cancel_turn_timer()
            self.resolve_fold_win()
            return "fold_win"

        if self.round_complete():
            result = self.advance_stage()
            if result == "continue":
                self.start_turn_timer()
            else:
                self.cancel_turn_timer()
            return result

        self.turn_idx = self.first_active_from((self.turn_idx + 1) % len(self.players))
        self.start_turn_timer()
        return "continue"

    def advance_stage(self) -> str:
        """Moves to the next stage (dealing community cards as needed),
        resetting betting for the new round. If fewer than 2 players can
        still act (the rest are all-in), keeps advancing automatically
        straight through to showdown rather than waiting on betting that
        can't happen."""
        for p in self.players:
            p.bet = 0
            p.acted = False
        self.current_bet = 0
        self.min_raise_increment = self.stake["big_blind"]
        self.stage += 1

        if self.stage == 1:
            self.community += [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        elif self.stage == 2:
            self.community.append(self.deck.pop())
        elif self.stage == 3:
            self.community.append(self.deck.pop())
        elif self.stage >= 4:
            self.resolve_showdown()
            return "showdown"

        n = len(self.players)
        start = self.bb_idx if n == 2 else self.sb_idx
        self.turn_idx = self.first_active_from(start)

        if len(self.can_act_players()) < 2 and len(self.active_players()) > 1:
            # Everyone left is all-in — run out the rest of the board with no more betting.
            return self.advance_stage()
        return "continue"

    def _remove_busted(self):
        """Drops anyone at 0 chips after the hand just resolved. Only ever
        called once a hand is fully over — mid-hand all-ins (stack 0 but
        still in the pot) must never be removed before showdown pays out."""
        busted = [p for p in self.players if p.stack <= 0]
        for p in busted:
            self.players.remove(p)
        if busted:
            names = ", ".join(p.name for p in busted)
            self.result_text += f"\n💀 **Busted out:** {names}"

    def resolve_fold_win(self):
        winner = self.active_players()[0]
        winner.stack += self.pot
        self.result_text = f"🏆 **{winner.name}** wins **{self.pot:,} chips** — everyone else folded."
        self._pending_hand_result = {
            "pot": self.pot,
            "players": [
                {"user_id": p.user_id, "name": p.name, "contributed": p.contributed,
                 "won": self.pot if p is winner else 0}
                for p in self.players
            ],
        }
        self.stage = 4
        self.pot = 0
        self._remove_busted()

    def compute_pots(self) -> list:
        """Splits self.pot into a main pot plus one side pot per distinct
        all-in amount among the players still active. A player who went
        all-in short only ever contests chips up to what they personally
        put in — whatever the other players bet beyond that forms a side
        pot those short-stacked players aren't eligible to win. Folded
        players' chips still count toward whichever layer(s) they
        contributed to; they just aren't in `eligible` for any of them."""
        active = self.active_players()
        if not active:
            return []

        contributors = [p for p in self.players if p.contributed > 0]
        levels = sorted(set(p.contributed for p in active))

        pots = []
        prev_level = 0
        for level in levels:
            layer_contributors = [p for p in contributors if p.contributed > prev_level]
            layer_amount = sum(min(p.contributed, level) - prev_level for p in layer_contributors)
            eligible = [p for p in active if p.contributed >= level]
            if layer_amount > 0:
                pots.append({"amount": layer_amount, "eligible": eligible})
            prev_level = level

        # Defensive: a folded player's contribution should never realistically
        # exceed every remaining active player's (folding only ever happens in
        # response to a bet an active player already matched or made), but if
        # some edge case ever produced that anyway, don't let the excess
        # silently vanish — fold it into the top pot rather than lose chips.
        accounted = sum(p["amount"] for p in pots)
        leftover = sum(p.contributed for p in contributors) - accounted
        if leftover > 0:
            if pots:
                pots[-1]["amount"] += leftover
            else:
                # Every active player's contributed level was 0 (e.g. blind
                # posters folded before anyone else put money in) — no tier
                # exists to attach the leftover to, so give everyone still
                # active a shot at it rather than losing it.
                pots.append({"amount": leftover, "eligible": active})
        return pots

    def resolve_showdown(self):
        active = self.active_players()
        ranks = {p.user_id: best_hand_from_7(p.hole + self.community) for p in active}
        pots = self.compute_pots()

        won_amounts = {p.user_id: 0 for p in active}
        pot_lines = []
        for i, pot in enumerate(pots):
            eligible = pot["eligible"]
            best = max(ranks[p.user_id] for p in eligible)
            winners = [p for p in eligible if ranks[p.user_id] == best]
            share = pot["amount"] // len(winners)
            leftover = pot["amount"] - share * len(winners)  # simplest odd-chip rule: first winner gets the remainder
            for j, w in enumerate(winners):
                take = share + (leftover if j == 0 else 0)
                w.stack += take
                won_amounts[w.user_id] += take

            label = "Main pot" if i == 0 else f"Side pot {i}"
            names = ", ".join(f"{w.name} ({hand_name(best)})" for w in winners)
            pot_lines.append(f"**{label}** ({pot['amount']:,}): {names}")

        # Real showdown convention: everyone who saw it through to the end
        # shows their hand, winners and losers alike — that's the whole
        # dramatic point, and it's different from folding, where a player
        # never has to reveal what they had.
        reveal_lines = []
        for p in active:
            won = won_amounts[p.user_id]
            won_text = f" — **+{won:,}**" if won > 0 else ""
            reveal_lines.append(f"🂠 {p.name}: {format_cards(p.hole)} ({hand_name(ranks[p.user_id])}){won_text}")

        self.result_text = "🏆 **Showdown!**\n" + "\n".join(pot_lines) + "\n\n" + "\n".join(reveal_lines)
        self._pending_hand_result = {
            "pot": self.pot,
            "players": [
                {"user_id": p.user_id, "name": p.name, "contributed": p.contributed,
                 "won": won_amounts.get(p.user_id, 0)}
                for p in self.players
            ],
        }
        self.pot = 0
        self._remove_busted()

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        if self.closed:
            return
        if not self.started:
            self.add_item(JoinTableButton())
            self.add_item(LeaveTableButton())
            self.add_item(StartTableButton())
            return

        # Joining stays open even mid-session — new arrivals wait in the
        # pending queue for the next deal rather than sitting mid-hand.
        self.add_item(JoinTableButton())
        self.add_item(ViewHandButton())
        if self.stage < 4:
            self.add_item(FoldButton())
            self.add_item(CheckCallButton(self))
            self.add_item(RaiseButton())
        else:
            self.add_item(LeaveTableButton())
            self.add_item(NextHandButton())

    def build_embed(self) -> discord.Embed:
        if self.closed:
            embed = discord.Embed(
                title=f"🃏 Poker Table — {self.stake['name']}",
                description="*Table closed — everyone's buy-in has been refunded.*",
                color=discord.Color.dark_grey(),
            )
            return embed

        if not self.started:
            lines = []
            for p in self.players:
                tag = " 👑" if p.user_id == self.host_id else ""
                lines.append(f"🪑 {p.name}{tag} — {p.stack:,} chips")

            embed = discord.Embed(
                title=f"🃏 Poker Table — {self.stake['name']}",
                description=(
                    f"**Buy-in:** {self.stake['buy_in']:,} chips\n"
                    f"**Blinds:** {self.stake['small_blind']:,} / {self.stake['big_blind']:,}\n\n"
                    f"**Players ({len(self.players)}/{MAX_PLAYERS}):**\n" + "\n".join(lines)
                ),
                color=discord.Color.gold(),
            )
            if len(self.players) >= MIN_PLAYERS_TO_START:
                embed.set_footer(text="Waiting for the host to start...")
            else:
                embed.set_footer(text=f"Need at least {MIN_PLAYERS_TO_START} players to start.")
            return embed

        lines = []
        for i, p in enumerate(self.players):
            tags = []
            if i == self.dealer_idx:
                tags.append("D")
            if i == self.sb_idx:
                tags.append("SB")
            if i == self.bb_idx:
                tags.append("BB")
            if self.stage < 4 and i == self.turn_idx and not p.folded:
                tags.append("👉")
            tag_text = f" ({'/'.join(tags)})" if tags else ""

            status = ""
            if p.folded:
                status = " — folded"
            elif p.stack == 0:
                status = " — all-in"
            elif p.bet > 0:
                status = f" — bet {p.bet:,}"

            lines.append(f"🪑 {p.name}{tag_text} — {p.stack:,} chips{status}")

        community_text = format_cards(self.community) if self.community else "*(none yet)*"

        description = (
            f"**Pot:** {self.pot:,} chips\n"
            f"**Community:** {community_text}\n\n"
            f"**Players:**\n" + "\n".join(lines)
        )
        if self.pending:
            pending_names = ", ".join(p.name for p in self.pending)
            description += f"\n\n⏳ **Waiting to join next hand:** {pending_names}"
        if self.result_text:
            description += f"\n\n{self.result_text}"

        embed = discord.Embed(
            title=f"🃏 Poker Table — {self.stake['name']} ({STAGE_NAMES[self.stage]})",
            description=description,
            color=discord.Color.green() if self.stage >= 4 else discord.Color.dark_gold(),
        )
        if self.stage < 4:
            embed.set_footer(
                text=f"{self.players[self.turn_idx].name}'s turn to act "
                     f"(auto-folds after {TURN_TIMEOUT_SECONDS}s of inactivity)"
            )
        else:
            embed.set_footer(text="Between hands — host can deal the next one, or anyone can leave.")
        return embed


class JoinTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Join Table", style=discord.ButtonStyle.success, emoji="➕")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view

        already_seated = view.find_player(interaction.user.id) is not None
        already_pending = any(p.user_id == interaction.user.id for p in view.pending)
        if already_seated or already_pending:
            view.busy = False
            return await interaction.response.send_message(
                "You're already seated (or waiting to join).", ephemeral=True
            )
        if len(view.players) + len(view.pending) >= MAX_PLAYERS:
            view.busy = False
            return await interaction.response.send_message("Table is full.", ephemeral=True)

        wallet = await view.db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < view.stake["buy_in"]:
            view.busy = False
            return await interaction.response.send_message(
                f"You need {view.stake['buy_in']:,} chips to buy in — you have {wallet['balance']:,}.",
                ephemeral=True,
            )

        await view.db_cog.add_chips(interaction.user.id, -view.stake["buy_in"])
        new_player = PokerPlayer(interaction.user.id, interaction.user.display_name, view.stake["buy_in"])

        if view.started:
            # A hand may be in progress — new arrivals wait for the next deal.
            view.pending.append(new_player)
        else:
            view.players.append(new_player)

        view.rebuild_items()
        await view.save_snapshot()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class LeaveTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Leave Table", style=discord.ButtonStyle.secondary, emoji="🚪")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        player = view.find_player(interaction.user.id)

        if not player:
            # Maybe they're only in the pending queue (joined mid-session,
            # haven't been seated in for a hand yet).
            pending_player = next((p for p in view.pending if p.user_id == interaction.user.id), None)
            if not pending_player:
                view.busy = False
                return await interaction.response.send_message("You're not seated at this table.", ephemeral=True)
            await view.db_cog.add_chips(interaction.user.id, pending_player.stack)
            view.pending.remove(pending_player)

            # If the table already started and this leave drops it below a
            # playable headcount, don't leave it stranded forever waiting on
            # a "Next Hand" nobody can click — close it out the same as a
            # host-leave. A fresh, never-started lobby with just the host is
            # normal (still waiting for people to join) and stays open.
            if view.started and len(view.players) + len(view.pending) < MIN_PLAYERS_TO_START:
                await view.close_and_refund()
                return await interaction.response.edit_message(embed=view.build_embed(), view=view)

            view.rebuild_items()
            await view.save_snapshot()
            return await interaction.response.edit_message(embed=view.build_embed(), view=view)

        if player.user_id == view.host_id:
            # No host-succession concept yet — the host leaving closes the
            # table outright and everyone (seated or still pending) gets
            # their buy-in back.
            await view.close_and_refund()
            return await interaction.response.edit_message(embed=view.build_embed(), view=view)

        await view.db_cog.add_chips(interaction.user.id, player.stack)
        view.players.remove(player)

        if view.started and len(view.players) + len(view.pending) < MIN_PLAYERS_TO_START:
            await view.close_and_refund()
            return await interaction.response.edit_message(embed=view.build_embed(), view=view)

        view.rebuild_items()
        await view.save_snapshot()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class StartTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Start Game", style=discord.ButtonStyle.primary, emoji="▶️")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        if interaction.user.id != view.host_id:
            view.busy = False
            return await interaction.response.send_message("Only the host can start the table.", ephemeral=True)
        if len(view.players) < MIN_PLAYERS_TO_START:
            view.busy = False
            return await interaction.response.send_message(
                f"Need at least {MIN_PLAYERS_TO_START} players to start.", ephemeral=True
            )

        view.started = True
        view.deal_hand()
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class NextHandButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next Hand", style=discord.ButtonStyle.primary, emoji="🔁")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        if interaction.user.id != view.host_id:
            view.busy = False
            return await interaction.response.send_message("Only the host can deal the next hand.", ephemeral=True)

        # Check the combined count before touching anything — merging
        # pending players in only to bail out on the player-count check
        # would leave the public embed stale (they'd stay shown as
        # "pending" until some other action happened to refresh it).
        if len(view.players) + len(view.pending) < MIN_PLAYERS_TO_START:
            view.busy = False
            return await interaction.response.send_message(
                f"Need at least {MIN_PLAYERS_TO_START} players to continue — waiting for more to join.",
                ephemeral=True,
            )

        if view.pending:
            view.players.extend(view.pending)
            view.pending = []

        view.deal_hand()
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class ViewHandButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="View My Hand", style=discord.ButtonStyle.secondary, emoji="🂠")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        player = view.find_player(interaction.user.id)
        view.busy = False  # purely informational — never reaches rebuild_items()
        if not player:
            return await interaction.response.send_message("You're not seated at this table.", ephemeral=True)

        await interaction.response.send_message(
            f"🂠 Your hand: **{format_cards(player.hole)}**", ephemeral=True
        )


def _reject_if_not_turn(view: "PokerTableView", user_id: int):
    """Shared turn-gate for the action buttons. Returns an error string if the
    click is invalid, or None if the click is for the correct player."""
    player = view.find_player(user_id)
    if not player:
        return "You're not seated at this table."
    if player.folded:
        return "You've already folded this hand."
    if view.stage >= 4:
        return "This hand is already over."
    if view.players[view.turn_idx].user_id != user_id:
        return "It's not your turn."
    return None


class FoldButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Fold", style=discord.ButtonStyle.danger, emoji="✋")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        error = _reject_if_not_turn(view, interaction.user.id)
        if error:
            view.busy = False
            return await interaction.response.send_message(error, ephemeral=True)

        player = view.find_player(interaction.user.id)
        player.folded = True
        player.acted = True
        result = view.advance_after_action()
        view.rebuild_items()
        if result in ("fold_win", "showdown"):
            await view.save_snapshot()
            await view.record_hand_stats()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class CheckCallButton(discord.ui.Button):
    def __init__(self, view: "PokerTableView"):
        call_amount = 0
        if view.stage < 4 and view.players:
            current_player = view.players[view.turn_idx]
            call_amount = max(0, view.current_bet - current_player.bet)
        if call_amount > 0:
            label, emoji = f"Call {call_amount:,}", "📞"
        else:
            label, emoji = "Check", "✔️"
        super().__init__(label=label, style=discord.ButtonStyle.primary, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        error = _reject_if_not_turn(view, interaction.user.id)
        if error:
            view.busy = False
            return await interaction.response.send_message(error, ephemeral=True)

        player = view.find_player(interaction.user.id)
        call_amount = min(view.current_bet - player.bet, player.stack)
        if call_amount > 0:
            player.stack -= call_amount
            player.bet += call_amount
            player.contributed += call_amount
            view.pot += call_amount
        player.acted = True

        result = view.advance_after_action()
        view.rebuild_items()
        if result in ("fold_win", "showdown"):
            await view.save_snapshot()
            await view.record_hand_stats()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class RaiseModal(discord.ui.Modal, title="Raise"):
    amount = discord.ui.TextInput(label="Raise to (total bet this round)", placeholder="e.g. 100", max_length=10)

    def __init__(self, poker_view: "PokerTableView", player: PokerPlayer):
        super().__init__()
        self.poker_view = poker_view
        self.player = player

    async def on_submit(self, interaction: discord.Interaction):
        view = self.poker_view
        player = self.player

        if view.busy:
            return await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
        error = _reject_if_not_turn(view, player.user_id)
        if error:
            return await interaction.response.send_message(f"{error} (the raise didn't go through)", ephemeral=True)

        try:
            target = int(self.amount.value)
        except ValueError:
            return await interaction.response.send_message("Amount must be a number.", ephemeral=True)

        max_possible = player.bet + player.stack
        min_valid = view.current_bet + view.min_raise_increment

        if target <= view.current_bet:
            return await interaction.response.send_message(
                f"Raise must be more than the current bet ({view.current_bet:,}).", ephemeral=True
            )
        if target > max_possible:
            return await interaction.response.send_message(
                f"You only have {max_possible:,} chips available this round.", ephemeral=True
            )
        if target < min_valid and target < max_possible:
            return await interaction.response.send_message(
                f"Raise must be to at least {min_valid:,} (or go all-in with {max_possible:,}).", ephemeral=True
            )

        # A short all-in below a full raise (only reachable here when
        # target == max_possible, per the validation above) is an
        # "incomplete" raise by standard rules: the amount to call still
        # rises to it, but it doesn't reopen betting for players who've
        # already matched the previous bet — they only get to call the
        # small top-up or fold, not raise again off of it. A full raise
        # reopens the action for everyone as before.
        is_full_raise = target >= min_valid
        raise_increment = target - view.current_bet

        view.busy = True
        added = target - player.bet
        player.stack -= added
        player.bet = target
        player.contributed += added
        view.pot += added
        view.current_bet = target
        if is_full_raise:
            view.min_raise_increment = max(raise_increment, view.min_raise_increment)
        player.acted = True
        if is_full_raise:
            for p in view.players:
                if p is not player and not p.folded and p.stack > 0:
                    p.acted = False  # a full raise reopens action for everyone else

        result = view.advance_after_action()
        view.rebuild_items()
        if result in ("fold_win", "showdown"):
            await view.save_snapshot()
            await view.record_hand_stats()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class RaiseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Raise", style=discord.ButtonStyle.success, emoji="⬆️")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        error = _reject_if_not_turn(view, interaction.user.id)
        if error:
            view.busy = False
            return await interaction.response.send_message(error, ephemeral=True)

        player = view.find_player(interaction.user.id)
        if player.stack <= 0:
            view.busy = False
            return await interaction.response.send_message("You're all-in — nothing left to raise with.", ephemeral=True)

        # A modal takes over from here instead of rebuild_items() — release
        # the lock now. RaiseModal.on_submit re-validates it's still this
        # player's turn before touching any state, since the table can move
        # on while the modal is open.
        view.busy = False
        await interaction.response.send_modal(RaiseModal(view, player))


class StakePresetButton(discord.ui.Button):
    def __init__(self, stake: dict):
        super().__init__(
            label=f"{stake['name']} ({stake['buy_in']:,} chips, {stake['small_blind']}/{stake['big_blind']})",
            style=discord.ButtonStyle.primary,
        )
        self.stake = stake

    async def callback(self, interaction: discord.Interaction):
        await create_table(interaction, self.stake)


class CustomStakeModal(discord.ui.Modal, title="Custom Table"):
    buy_in = discord.ui.TextInput(label="Buy-in (chips)", placeholder="e.g. 750", max_length=10)
    small_blind = discord.ui.TextInput(label="Small Blind", placeholder="e.g. 15", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            buy_in = int(self.buy_in.value)
            small_blind = int(self.small_blind.value)
        except ValueError:
            return await interaction.response.send_message("Buy-in and Small Blind must be numbers.", ephemeral=True)

        if buy_in < MIN_CUSTOM_BUY_IN or small_blind < MIN_CUSTOM_SMALL_BLIND:
            return await interaction.response.send_message(
                f"Buy-in must be at least {MIN_CUSTOM_BUY_IN} and Small Blind at least {MIN_CUSTOM_SMALL_BLIND}.",
                ephemeral=True,
            )
        if small_blind * 2 > buy_in:
            return await interaction.response.send_message(
                "Small Blind is too high relative to the buy-in — you'd barely get a hand in.", ephemeral=True
            )

        stake = {
            "name": "Custom Table", "buy_in": buy_in,
            "small_blind": small_blind, "big_blind": small_blind * 2,
        }
        await create_table(interaction, stake)


class CustomStakeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Custom Table", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CustomStakeModal())


class PokerStatsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="My Stats", style=discord.ButtonStyle.secondary, emoji="📊")

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        stats = await db_cog.get_poker_stats(interaction.user.id)
        recent = await db_cog.get_recent_poker_hands(5)

        played = stats["hands_played"]
        win_rate = f"{stats['hands_won'] / played * 100:.0f}%" if played else "—"
        net = stats["net_chips"]
        net_text = f"+{net:,}" if net >= 0 else f"{net:,}"

        description = (
            f"**Hands played:** {played:,}\n"
            f"**Hands won:** {stats['hands_won']:,} ({win_rate})\n"
            f"**Net chips (lifetime):** {net_text}\n"
            f"**Biggest pot won:** {stats['biggest_pot_won']:,}"
        )
        if recent:
            lines = "\n".join(
                f"• {h['stake_name']} — pot {h['pot']:,}: {h['winners_summary']}" for h in recent
            )
            description += f"\n\n**Recent hands (server-wide):**\n{lines}"

        embed = discord.Embed(title="📊 Your Poker Stats", description=description, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed, ephemeral=True)


class StakeSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for stake in STAKE_TIERS.values():
            self.add_item(StakePresetButton(stake))
        self.add_item(CustomStakeButton())
        self.add_item(PokerStatsButton())


async def create_table(interaction: discord.Interaction, stake: dict):
    db_cog = interaction.client.get_cog('Database')
    wallet = await db_cog.get_or_create_wallet(interaction.user.id)
    if wallet["balance"] < stake["buy_in"]:
        await interaction.response.send_message(
            f"You need {stake['buy_in']:,} chips to open this table — you have {wallet['balance']:,}.",
            ephemeral=True,
        )
        return

    await db_cog.add_chips(interaction.user.id, -stake["buy_in"])
    view = PokerTableView(db_cog, interaction.user, stake)

    await interaction.response.edit_message(
        embed=discord.Embed(
            title="🃏 Table Created!",
            description="Your table is live in the channel below — invite others to Join!",
            color=discord.Color.gold(),
        ),
        view=None,
    )

    message = await interaction.channel.send(
        content=f"🃏 {interaction.user.mention} opened a Poker table!",
        embed=view.build_embed(),
        view=view,
    )
    view.message = message
    view.table_key = str(message.id)
    await view.save_snapshot()
