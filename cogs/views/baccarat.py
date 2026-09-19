# cogs/views/baccarat.py
#
# Baccarat table: a single persistent view that plays solo or as a
# group with zero difference in code path — a table with one person
# still cycles bet -> auto-deal -> result -> next round on its own.
# No buy-in, no table-held stack: each bet deducts straight from the
# bettor's wallet the moment it's placed, and winnings credit straight
# back at resolution — same "DB only at checkpoints" approach as the
# other casino games, just with lighter checkpoints since there's no
# multi-round chip custody to track.
#
# Betting window: the countdown arms the moment the first bet of a
# round lands, using whoever's seated *at that instant* as the
# "expected bettors" for this round (register_bet's expected_bettors
# snapshot). Anyone who joins the table after that moment is still
# free to also bet this round, but isn't required to for the round to
# resolve early — they just don't block the "everyone's in" shortcut.
# That's what keeps a late joiner from stalling an otherwise-finished
# round, and it's also what makes solo play deal instantly: a lone
# host's own bet always satisfies "everyone expected has bet."
#
# Busy-guard follows the same pattern as the dungeon/blackjack/poker
# views: a `busy` flag checked in interaction_check, released via
# rebuild_items(). Bet modals bypass interaction_check (a Discord
# limitation, not a choice), so they check/set busy manually.

import asyncio
import time
import traceback

import discord

from data.baccarat import play_round, resolve_bet_amount, hand_value, PAYOUTS
from data.poker import new_shuffled_deck, format_cards

MIN_BET = 10
MAX_PLAYERS = 10
BETTING_WINDOW_SECONDS = 20
REVEAL_DELAY_SECONDS = 1.2  # pause between each dealt-card reveal — same idea as Blackjack's dealer draw delay

SIDE_LABELS = {"player": "Player", "banker": "Banker", "tie": "Tie"}
SIDE_EMOJI = {"player": "🔵", "banker": "🔴", "tie": "🟢"}


class BaccaratPlayer:
    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name


class BaccaratTableView(discord.ui.View):
    def __init__(self, db_cog, host: discord.Member):
        super().__init__(timeout=None)  # a table can sit open a while between rounds
        self.db_cog = db_cog
        self.host_id = host.id
        self.players: list[BaccaratPlayer] = [BaccaratPlayer(host.id, host.display_name)]
        self.bets: dict[int, dict] = {}  # user_id -> {"side": ..., "amount": ...} for the round in progress
        self.expected_bettors: set = set()  # snapshotted when the first bet of a round lands
        self.last_result: dict | None = None
        self.message: discord.Message | None = None
        self.closed = False
        self.busy = False

        self.betting_token = 0
        self.betting_task: asyncio.Task | None = None
        self.betting_deadline: float | None = None  # unix timestamp — live countdown in the embed

        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item) -> None:
        print(f"[Baccarat] Error in {item.__class__.__name__} (user {interaction.user.id}):")
        traceback.print_exception(type(error), error, error.__traceback__)
        self.busy = False
        try:
            message = "Something went wrong processing that — please try again."
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            pass

    def find_player(self, user_id: int) -> BaccaratPlayer | None:
        return next((p for p in self.players if p.user_id == user_id), None)

    # --- Betting window timer ---
    def cancel_betting_timer(self):
        if self.betting_task and not self.betting_task.done():
            self.betting_task.cancel()
        self.betting_task = None

    def start_betting_timer(self):
        self.cancel_betting_timer()
        self.betting_token += 1
        self.betting_deadline = time.time() + BETTING_WINDOW_SECONDS
        self.betting_task = asyncio.create_task(self._betting_timeout_watcher(self.betting_token))

    async def _betting_timeout_watcher(self, token: int):
        try:
            await asyncio.sleep(BETTING_WINDOW_SECONDS)
        except asyncio.CancelledError:
            return
        if token != self.betting_token or self.closed or not self.bets:
            return
        await self.resolve_round()
        frames = self._reveal_frames()
        if self.message:
            try:
                await self.message.edit(embed=frames[0], view=self)
            except discord.HTTPException:
                pass
        await self.animate_remaining_reveal(frames[1:])

    # --- Betting / resolution ---
    def register_bet(self, user_id: int, side: str, amount: int) -> bool:
        """Records a bet (assumes the caller already handled the wallet
        deduction). Arms the timer on the first bet of a round. Returns
        True if every expected bettor has now bet — the round should
        resolve immediately rather than waiting out the countdown."""
        is_first_bet = not self.bets
        self.bets[user_id] = {"side": side, "amount": amount}
        if is_first_bet:
            self.expected_bettors = {p.user_id for p in self.players}
            self.start_betting_timer()
        return bool(self.expected_bettors) and self.expected_bettors.issubset(self.bets.keys())

    async def resolve_round(self):
        """Deals the round and pays out every live bet. Money is fully
        settled by the time this returns, but busy stays True (doesn't
        call rebuild_items()) — the caller always follows this with the
        reveal animation, and releasing the lock early would let a new
        bet start a second round whose message edits would race with
        this one's animation still playing out."""
        self.busy = True
        self.cancel_betting_timer()
        deck = new_shuffled_deck()
        result = play_round(deck)
        outcome = result["outcome"]

        payout_lines = []
        for user_id, bet in self.bets.items():
            player = self.find_player(user_id)
            name = player.name if player else str(user_id)
            credit = resolve_bet_amount(bet["side"], bet["amount"], outcome)
            if credit > 0:
                await self.db_cog.add_chips(user_id, credit)
            net = credit - bet["amount"]
            net_text = f"+{net:,}" if net > 0 else (f"{net:,}" if net < 0 else "push")
            payout_lines.append(f"{name} bet {SIDE_LABELS[bet['side']]} {bet['amount']:,} — {net_text}")

        self.last_result = {**result, "payout_lines": payout_lines}
        self.bets = {}
        self.expected_bettors = set()
        self.betting_deadline = None

    def _reveal_frames(self) -> list:
        """Builds the sequence of embeds for the post-round reveal, each
        showing progressively more of the already-resolved hands — same
        idea as how online casino Baccarat deals visibly one card at a
        time instead of just announcing the winner. The outcome/payout
        line only appears in build_embed()'s normal state, shown as the
        final step after this sequence finishes, so the result lands a
        beat after the last card rather than all at once."""
        r = self.last_result
        header = [f"🪑 {p.name}{' 👑' if p.user_id == self.host_id else ''}" for p in self.players]

        def hand_line(label, cards):
            if not cards:
                return f"{label}: *(waiting)*"
            return f"{label}: {format_cards(cards)}  =  **{hand_value(cards)}**"

        def frame(note, player_cards, banker_cards):
            embed = discord.Embed(title="🎴 Baccarat Table", description=f"🎴 *{note}*", color=discord.Color.dark_gold())
            embed.add_field(name=f"Players ({len(self.players)})", value="\n".join(header), inline=False)
            embed.add_field(
                name="Cards", value=hand_line("Player", player_cards) + "\n" + hand_line("Banker", banker_cards),
                inline=False,
            )
            return embed

        frames = [
            frame("Dealing...", [], []),
            frame("Dealing Player's cards...", r["player"][:2], []),
            frame("Dealing Banker's cards...", r["player"][:2], r["banker"][:2]),
        ]
        if len(r["player"]) > 2:
            frames.append(frame("Player draws a third card...", r["player"], r["banker"][:2]))
        if len(r["banker"]) > 2:
            frames.append(frame("Banker draws a third card...", r["player"], r["banker"]))
        return frames

    async def animate_remaining_reveal(self, frames: list):
        """Plays out reveal frames after the first one (already shown by
        the caller, since it needs to happen immediately — an interaction
        response, or the first message.edit() from the timeout watcher).
        Ends on build_embed()'s real, persistent state. The `finally`
        guarantees busy releases (via rebuild_items()) no matter which
        exit path this takes, since resolve_round() deliberately left it
        held for this entire animation."""
        try:
            for embed in frames:
                await asyncio.sleep(REVEAL_DELAY_SECONDS)
                if not self.message:
                    return
                try:
                    await self.message.edit(embed=embed, view=self)
                except discord.HTTPException:
                    return
            await asyncio.sleep(REVEAL_DELAY_SECONDS)
        finally:
            self.rebuild_items()
        if self.message:
            try:
                await self.message.edit(embed=self.build_embed(), view=self)
            except discord.HTTPException:
                pass

    async def close_table(self):
        """Refunds any live bet from the round in progress (it'll never
        resolve now), then closes the table."""
        for user_id, bet in self.bets.items():
            await self.db_cog.add_chips(user_id, bet["amount"])
        self.bets = {}
        self.expected_bettors = set()
        self.players = []
        self.closed = True
        self.cancel_betting_timer()
        self.betting_deadline = None
        self.rebuild_items()
        self.stop()

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        if self.closed:
            return
        self.add_item(BetButton("player"))
        self.add_item(BetButton("banker"))
        self.add_item(BetButton("tie"))
        self.add_item(JoinTableButton())
        self.add_item(LeaveTableButton())

    def build_embed(self) -> discord.Embed:
        if self.closed:
            return discord.Embed(
                title="🎴 Baccarat Table — Closed",
                description="*Table closed — any live bet has been refunded.*",
                color=discord.Color.dark_grey(),
            )

        if self.betting_deadline:
            status = f"⏱️ Round deals <t:{int(self.betting_deadline)}:R>"
        elif not self.bets:
            status = "*Waiting for a bet — the round deals automatically once one comes in.*"
        else:
            status = None  # bets exist but no deadline shouldn't happen — they're set/cleared together

        embed = discord.Embed(title="🎴 Baccarat Table", description=status, color=discord.Color.dark_gold())

        # One line per player showing their current bet right next to their
        # name, rather than a separate list a reader has to cross-reference.
        player_lines = []
        for p in self.players:
            crown = " 👑" if p.user_id == self.host_id else ""
            bet = self.bets.get(p.user_id)
            if bet:
                bet_text = f"{SIDE_EMOJI[bet['side']]} {SIDE_LABELS[bet['side']]} — {bet['amount']:,} chips"
            else:
                bet_text = "*no bet yet*"
            player_lines.append(f"🪑 **{p.name}**{crown} — {bet_text}")
        embed.add_field(name=f"Players ({len(self.players)})", value="\n".join(player_lines), inline=False)

        if self.last_result:
            r = self.last_result
            outcome_label = SIDE_LABELS[r["outcome"]]
            natural_tag = " (Natural!)" if r["natural"] else ""
            embed.add_field(
                name="🏆 Last Round",
                value=(
                    f"Player {format_cards(r['player'])}  =  **{r['player_total']}**\n"
                    f"Banker {format_cards(r['banker'])}  =  **{r['banker_total']}**\n"
                    f"**{outcome_label} wins{natural_tag}**"
                ),
                inline=False,
            )
            if r["payout_lines"]:
                embed.add_field(name="💰 Payouts", value="\n".join(r["payout_lines"]), inline=False)

        embed.set_footer(text=f"Banker pays {PAYOUTS['banker']}:1 (5% commission) · Tie pays {PAYOUTS['tie']:.0f}:1")
        return embed


class BetModal(discord.ui.Modal, title="Place Bet"):
    amount = discord.ui.TextInput(label="Bet amount", placeholder="e.g. 100", max_length=10)

    def __init__(self, table_view: "BaccaratTableView", side: str):
        super().__init__(title=f"Bet on {SIDE_LABELS[side]}")
        self.table_view = table_view
        self.side = side

    async def on_submit(self, interaction: discord.Interaction):
        view = self.table_view
        if view.busy:
            return await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)

        player = view.find_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("You're not seated at this table — join first.", ephemeral=True)

        try:
            amount = int(self.amount.value)
        except ValueError:
            return await interaction.response.send_message("Bet amount must be a number.", ephemeral=True)
        if amount < MIN_BET:
            return await interaction.response.send_message(f"Minimum bet is {MIN_BET:,} chips.", ephemeral=True)

        # Defer now, before any slow work — everything from here on can
        # involve several sequential DB round-trips (wallet lookup, the
        # bet deduction, and if this bet completes the round, one more
        # per bettor being paid out in resolve_round()). Left undeferred,
        # that chain can take longer than Discord's 3-second interaction
        # ack window, which kills the interaction token outright (seen
        # live as `discord.errors.NotFound: Unknown interaction`).
        # Deferring a modal-submit interaction acknowledges immediately
        # as a "deferred update," which is what lets edit_original_response()
        # below still work no matter how long the DB work actually takes.
        await interaction.response.defer()

        wallet = await view.db_cog.get_or_create_wallet(interaction.user.id)
        if amount > wallet["balance"]:
            return await interaction.followup.send(
                f"You don't have {amount:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )

        view.busy = True

        # Changing an existing bet this round refunds the old amount first —
        # nothing's deducted twice, and nothing needs to track a "diff."
        existing = view.bets.get(interaction.user.id)
        if existing:
            await view.db_cog.add_chips(interaction.user.id, existing["amount"])
        await view.db_cog.add_chips(interaction.user.id, -amount)

        should_resolve = view.register_bet(interaction.user.id, self.side, amount)
        if should_resolve:
            await view.resolve_round()
            frames = view._reveal_frames()
            await interaction.edit_original_response(embed=frames[0], view=view)
            await view.animate_remaining_reveal(frames[1:])
        else:
            view.rebuild_items()
            await interaction.edit_original_response(embed=view.build_embed(), view=view)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        """Modals dispatch errors separately from the View's own on_error —
        without this, discord.py's default handler just logs to stderr and
        leaves the player with no feedback at all, and (worse) leaves
        view.busy stuck True forever if the failure happened after it was
        set, locking the whole table. Same reasoning as Poker's RaiseModal."""
        print(f"[Baccarat] Error in BetModal (user {interaction.user.id}):")
        traceback.print_exception(type(error), error, error.__traceback__)
        self.table_view.busy = False
        self.table_view.rebuild_items()
        try:
            message = "Something went wrong placing that bet — please try again."
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            pass


class BetButton(discord.ui.Button):
    def __init__(self, side: str):
        super().__init__(
            label=SIDE_LABELS[side], style=discord.ButtonStyle.primary, emoji=SIDE_EMOJI[side]
        )
        self.side = side

    async def callback(self, interaction: discord.Interaction):
        view: BaccaratTableView = self.view
        player = view.find_player(interaction.user.id)
        view.busy = False  # a modal takes over from here
        if not player:
            return await interaction.response.send_message("You're not seated at this table — join first.", ephemeral=True)
        await interaction.response.send_modal(BetModal(view, self.side))


class JoinTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Join Table", style=discord.ButtonStyle.success, emoji="➕")

    async def callback(self, interaction: discord.Interaction):
        view: BaccaratTableView = self.view
        if view.find_player(interaction.user.id):
            view.busy = False
            return await interaction.response.send_message("You're already at this table.", ephemeral=True)
        if len(view.players) >= MAX_PLAYERS:
            view.busy = False
            return await interaction.response.send_message("Table is full.", ephemeral=True)

        view.players.append(BaccaratPlayer(interaction.user.id, interaction.user.display_name))
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class LeaveTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Leave Table", style=discord.ButtonStyle.secondary, emoji="🚪")

    async def callback(self, interaction: discord.Interaction):
        view: BaccaratTableView = self.view
        player = view.find_player(interaction.user.id)
        if not player:
            view.busy = False
            return await interaction.response.send_message("You're not at this table.", ephemeral=True)

        if player.user_id == view.host_id:
            # No host-succession concept — the host leaving closes the table
            # outright, same as Poker. Any live bet this round is refunded.
            await view.close_table()
            return await interaction.response.edit_message(embed=view.build_embed(), view=view)

        existing = view.bets.pop(interaction.user.id, None)
        if existing:
            await view.db_cog.add_chips(interaction.user.id, existing["amount"])
        view.expected_bettors.discard(interaction.user.id)
        view.players.remove(player)
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


async def create_table(interaction: discord.Interaction):
    """No buy-in step — unlike Poker, Baccarat bets deduct straight from
    the wallet per round rather than sitting in a table-held stack, so
    there's nothing to collect before the table can open."""
    db_cog = interaction.client.get_cog('Database')
    view = BaccaratTableView(db_cog, interaction.user)

    await interaction.response.edit_message(
        embed=discord.Embed(
            title="🎴 Table Created!",
            description="Your table is live in the channel below — invite others to Join, or just place a bet yourself.",
            color=discord.Color.gold(),
        ),
        view=None,
    )

    message = await interaction.channel.send(
        content=f"🎴 {interaction.user.mention} opened a Baccarat table!",
        embed=view.build_embed(),
        view=view,
    )
    view.message = message
