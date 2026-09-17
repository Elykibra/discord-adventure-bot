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

from data.baccarat import play_round, resolve_bet_amount, PAYOUTS
from data.poker import new_shuffled_deck, format_cards

MIN_BET = 10
MAX_PLAYERS = 10
BETTING_WINDOW_SECONDS = 20

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
        if self.message:
            try:
                await self.message.edit(embed=self.build_embed(), view=self)
            except discord.HTTPException:
                pass

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
        """Deals the round and pays out every live bet. Pure state
        mutation — callers decide how to actually show the result (an
        interaction response, or editing the message directly when
        triggered by the timeout watcher, which has no interaction)."""
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
        self.rebuild_items()

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

        lines = [f"🪑 {p.name}{' 👑' if p.user_id == self.host_id else ''}" for p in self.players]
        description = f"**Players ({len(self.players)}):**\n" + "\n".join(lines)

        if self.bets:
            bet_lines = []
            for p in self.players:
                bet = self.bets.get(p.user_id)
                if bet:
                    bet_lines.append(f"{SIDE_EMOJI[bet['side']]} {p.name}: {SIDE_LABELS[bet['side']]} — {bet['amount']:,} chips")
            description += "\n\n**Bets this round:**\n" + "\n".join(bet_lines)
            if self.betting_deadline:
                description += f"\n\n⏱️ Round deals <t:{int(self.betting_deadline)}:R>"
        else:
            description += "\n\n*Waiting for a bet — the round deals automatically once one comes in.*"

        if self.last_result:
            r = self.last_result
            outcome_label = SIDE_LABELS[r["outcome"]]
            natural_tag = " (Natural!)" if r["natural"] else ""
            description += (
                f"\n\n🏆 **Last round:** Player {format_cards(r['player'])} = {r['player_total']}   |   "
                f"Banker {format_cards(r['banker'])} = {r['banker_total']}\n"
                f"**{outcome_label} wins{natural_tag}**"
            )
            if r["payout_lines"]:
                description += "\n" + "\n".join(r["payout_lines"])

        embed = discord.Embed(title="🎴 Baccarat Table", description=description, color=discord.Color.dark_gold())
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

        wallet = await view.db_cog.get_or_create_wallet(interaction.user.id)
        if amount > wallet["balance"]:
            return await interaction.response.send_message(
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
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class BetButton(discord.ui.Button):
    def __init__(self, side: str):
        super().__init__(
            label=f"Bet {SIDE_LABELS[side]}", style=discord.ButtonStyle.primary, emoji=SIDE_EMOJI[side]
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
