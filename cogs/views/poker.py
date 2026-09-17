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

import discord

from data.poker import STAKE_TIERS, new_shuffled_deck, format_cards, best_hand_from_7, hand_name

MIN_PLAYERS_TO_START = 2
MAX_PLAYERS = 6
MIN_CUSTOM_BUY_IN = 20
MIN_CUSTOM_SMALL_BLIND = 1

STAGE_NAMES = ["Pre-Flop", "Flop", "Turn", "River", "Showdown"]


class PokerPlayer:
    def __init__(self, user_id: int, name: str, stack: int):
        self.user_id = user_id
        self.name = name
        self.stack = stack
        self.hole: list = []
        self.folded = False
        self.bet = 0     # this betting round's contribution so far
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
            self.resolve_fold_win()
            return "fold_win"

        if self.round_complete():
            return self.advance_stage()

        self.turn_idx = self.first_active_from((self.turn_idx + 1) % len(self.players))
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
        self.stage = 4
        self.pot = 0
        self._remove_busted()

    def resolve_showdown(self):
        active = self.active_players()
        best = None
        winners = []
        for p in active:
            rank = best_hand_from_7(p.hole + self.community)
            if best is None or rank > best:
                best = rank
                winners = [p]
            elif rank == best:
                winners.append(p)

        share = self.pot // len(winners)
        leftover = self.pot - share * len(winners)  # odd chips — see note below
        for i, w in enumerate(winners):
            w.stack += share + (leftover if i == 0 else 0)  # simplest odd-chip rule: first winner gets the remainder

        names = ", ".join(f"{w.name} ({hand_name(best)})" for w in winners)
        self.result_text = f"🏆 **Showdown!** {names} — wins {share:,} each." if len(winners) > 1 \
            else f"🏆 **{winners[0].name}** wins **{self.pot:,} chips** with a {hand_name(best)}!"
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
                description="*Host left — table closed, buy-ins refunded.*",
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
            embed.set_footer(text=f"{self.players[self.turn_idx].name}'s turn to act")
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
            view.rebuild_items()
            return await interaction.response.edit_message(embed=view.build_embed(), view=view)

        if player.user_id == view.host_id:
            # No host-succession concept yet — the host leaving closes the
            # table outright and everyone (seated or still pending) gets
            # their buy-in back.
            for p in view.players + view.pending:
                await view.db_cog.add_chips(p.user_id, p.stack)
            view.players.clear()
            view.pending.clear()
            view.closed = True
            view.rebuild_items()
            view.stop()
            return await interaction.response.edit_message(embed=view.build_embed(), view=view)

        await view.db_cog.add_chips(interaction.user.id, player.stack)
        view.players.remove(player)
        view.rebuild_items()
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
        view.advance_after_action()
        view.rebuild_items()
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
            view.pot += call_amount
        player.acted = True

        view.advance_after_action()
        view.rebuild_items()
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

        view.busy = True
        added = target - player.bet
        player.stack -= added
        player.bet = target
        view.pot += added
        view.min_raise_increment = max(target - view.current_bet, view.min_raise_increment)
        view.current_bet = target
        player.acted = True
        for p in view.players:
            if p is not player and not p.folded and p.stack > 0:
                p.acted = False  # a raise reopens action for everyone else

        view.advance_after_action()
        view.rebuild_items()
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


class StakeSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for stake in STAKE_TIERS.values():
            self.add_item(StakePresetButton(stake))
        self.add_item(CustomStakeButton())


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
