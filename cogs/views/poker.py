# cogs/views/poker.py
#
# Texas Hold'em — Phase 2: table creation and the lobby (stake selection,
# Join/Leave, host Start). Dealing, betting rounds, and showdown land in
# later phases on top of this. Buy-ins/cash-outs are the only points that
# touch the database — same "DB only at checkpoints" approach as the
# dungeon and blackjack.
#
# Every button here guards against double-click races the same way the
# dungeon and blackjack views do: a `busy` flag checked in interaction_check,
# released once the view reaches a new stable state via rebuild_items().
# Unlike those views, multiple *different* people are meant to interact with
# this one (anyone can Join/Leave), so the guard is table-wide rather than
# tied to a single owner.

import discord

from data.poker import STAKE_TIERS

MIN_PLAYERS_TO_START = 2
MAX_PLAYERS = 6
MIN_CUSTOM_BUY_IN = 20
MIN_CUSTOM_SMALL_BLIND = 1


class PokerPlayer:
    def __init__(self, user_id: int, name: str, stack: int):
        self.user_id = user_id
        self.name = name
        self.stack = stack


class PokerTableView(discord.ui.View):
    def __init__(self, db_cog, host: discord.Member, stake: dict):
        super().__init__(timeout=None)  # a lobby can sit open for a while waiting on players
        self.db_cog = db_cog
        self.host_id = host.id
        self.stake = stake
        self.players: list[PokerPlayer] = [PokerPlayer(host.id, host.display_name, stake["buy_in"])]
        self.started = False
        self.message: discord.Message | None = None
        self.busy = False
        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def find_player(self, user_id: int) -> PokerPlayer | None:
        return next((p for p in self.players if p.user_id == user_id), None)

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        if self.started:
            return
        self.add_item(JoinTableButton())
        self.add_item(LeaveTableButton())
        self.add_item(StartTableButton())

    def build_embed(self) -> discord.Embed:
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
        if not self.started:
            if len(self.players) >= MIN_PLAYERS_TO_START:
                embed.set_footer(text="Waiting for the host to start...")
            else:
                embed.set_footer(text=f"Need at least {MIN_PLAYERS_TO_START} players to start.")
        return embed


class JoinTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Join Table", style=discord.ButtonStyle.success, emoji="➕")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view

        if view.find_player(interaction.user.id):
            view.busy = False
            return await interaction.response.send_message("You're already seated.", ephemeral=True)
        if len(view.players) >= MAX_PLAYERS:
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
        view.players.append(PokerPlayer(interaction.user.id, interaction.user.display_name, view.stake["buy_in"]))
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class LeaveTableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Leave Table", style=discord.ButtonStyle.secondary, emoji="🚪")

    async def callback(self, interaction: discord.Interaction):
        view: PokerTableView = self.view
        player = view.find_player(interaction.user.id)
        if not player:
            view.busy = False
            return await interaction.response.send_message("You're not seated at this table.", ephemeral=True)

        if player.user_id == view.host_id:
            # No host-succession concept yet — the host leaving closes the
            # table outright and everyone gets their buy-in back.
            for p in view.players:
                await view.db_cog.add_chips(p.user_id, p.stack)
            view.players.clear()
            view.started = True  # reuse "started" to also mean "closed" — rebuild_items() clears all buttons either way
            view.busy = False
            for item in view.children:
                item.disabled = True
            embed = view.build_embed()
            embed.description += "\n\n*Host left — table closed, buy-ins refunded.*"
            view.stop()
            return await interaction.response.edit_message(embed=embed, view=view)

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

        # Dealing/betting rounds are the next phase — this confirms the lobby
        # itself (stakes, join, leave, buy-ins) works end-to-end on its own
        # before anything is built on top of it.
        view.busy = False
        await interaction.response.send_message(
            "🚧 Dealing isn't wired up yet — that's the next phase. The lobby itself is fully working, though!",
            ephemeral=True,
        )


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
