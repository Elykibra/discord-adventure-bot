# cogs/casino.py

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

from .views.dungeon import DungeonRunView, ENTRY_FEE as DUNGEON_ENTRY_FEE
from .views.blackjack import BlackjackBetView, blackjack_bet_embed
from .views.poker import StakeSelectView
from .views.baccarat import create_table as create_baccarat_table
from .views.slots import SlotsBetView, slots_bet_embed
from .views.video_poker import VideoPokerBetView, video_poker_bet_embed
from data.weapons import WEAPON_CATALOG, STARTER_WEAPON, format_damage_range, trait_display, tier_display
from data.permanent_stats import PERMANENT_STATS, MAX_STAT_LEVEL, cost_for_next_level, format_effect

DAILY_COOLDOWN = timedelta(hours=24)
DAILY_STREAK_GRACE = timedelta(hours=48)  # reclaim within this window to keep the streak alive
DAILY_BASE_AMOUNT = 250
DAILY_STREAK_BONUS_PER_DAY = 15
DAILY_STREAK_BONUS_CAP_DAYS = 10  # streak day 10+ all grant the same max bonus


def daily_amount_for_streak(streak: int) -> int:
    bonus_days = min(streak - 1, DAILY_STREAK_BONUS_CAP_DAYS - 1)
    return DAILY_BASE_AMOUNT + bonus_days * DAILY_STREAK_BONUS_PER_DAY


def casino_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=discord.Color.gold())


class CasinoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Balance", value="balance", emoji="💰",
                                  description="Check your chip balance"),
            discord.SelectOption(label="Daily Bonus", value="daily", emoji="🎁",
                                  description="Claim your daily chips"),
            discord.SelectOption(label="Armory", value="armory", emoji="🔫",
                                  description="Buy and equip weapons"),
            discord.SelectOption(label="Stats", value="stats", emoji="📈",
                                  description="Permanent dungeon upgrades"),
            discord.SelectOption(label="Dungeon", value="dungeon", emoji="🗝️",
                                  description=f"Enter a run for {DUNGEON_ENTRY_FEE} chips"),
            discord.SelectOption(label="Blackjack", value="blackjack", emoji="🃏",
                                  description="Play a hand against the dealer"),
            discord.SelectOption(label="Poker", value="poker", emoji="♠️",
                                  description="Open a Texas Hold'em table"),
            discord.SelectOption(label="Baccarat", value="baccarat", emoji="🎴",
                                  description="Bet Player, Banker, or Tie — solo or with others"),
            discord.SelectOption(label="Slots", value="slots", emoji="🎰",
                                  description="Pull the lever, match all three"),
            discord.SelectOption(label="Solo Poker", value="video_poker", emoji="♦️",
                                  description="Jacks or Better — choose your hold, then draw"),
        ]
        super().__init__(placeholder="What would you like to do?", options=options)

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')

        if self.values[0] == "poker":
            view = StakeSelectView()
            embed = casino_embed("🃏 Poker", "Pick a stake to open a new table, or set your own.")
            await interaction.response.edit_message(embed=embed, view=view)
            return

        if self.values[0] == "baccarat":
            await create_baccarat_table(interaction)
            return

        if self.values[0] == "slots":
            wallet = await db_cog.get_or_create_wallet(interaction.user.id)
            view = SlotsBetView(wallet["balance"])
            await interaction.response.edit_message(embed=slots_bet_embed(wallet["balance"]), view=view)
            return

        if self.values[0] == "video_poker":
            wallet = await db_cog.get_or_create_wallet(interaction.user.id)
            view = VideoPokerBetView(wallet["balance"])
            await interaction.response.edit_message(embed=video_poker_bet_embed(wallet["balance"]), view=view)
            return

        if self.values[0] == "armory":
            view = await ArmoryView.create(db_cog, interaction.user.id)
            await interaction.response.edit_message(embed=view.build_embed(), view=view)
            return

        if self.values[0] == "stats":
            view = await StatsView.create(db_cog, interaction.user.id)
            await interaction.response.edit_message(embed=view.build_embed(), view=view)
            return

        if self.values[0] == "dungeon":
            await self._handle_dungeon_entry(db_cog, interaction)
            return

        if self.values[0] == "blackjack":
            wallet = await db_cog.get_or_create_wallet(interaction.user.id)
            view = BlackjackBetView(wallet["balance"])
            await interaction.response.edit_message(embed=blackjack_bet_embed(wallet["balance"]), view=view)
            return

        if self.values[0] == "balance":
            embed = await self._handle_balance(db_cog, interaction.user.id)
        else:
            embed = await self._handle_daily(db_cog, interaction.user.id)

        # Both of these branches stay on this SAME CasinoView instance
        # (self.view) rather than handing off to a new one, so — unlike
        # every branch above — the lock needs releasing here for the menu
        # to stay usable afterward.
        self.view.busy = False
        await interaction.response.edit_message(embed=embed, view=self.view)

    async def _handle_balance(self, db_cog, user_id: int) -> discord.Embed:
        wallet = await db_cog.get_or_create_wallet(user_id)
        return casino_embed("💰 Balance", f"You have **{wallet['balance']:,} chips**.")

    async def _handle_dungeon_entry(self, db_cog, interaction: discord.Interaction):
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < DUNGEON_ENTRY_FEE:
            self.view.busy = False
            await interaction.response.send_message(
                f"You need {DUNGEON_ENTRY_FEE:,} chips to enter the dungeon — "
                f"you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return

        await db_cog.add_chips(interaction.user.id, -DUNGEON_ENTRY_FEE)
        stat_levels = await db_cog.get_stat_levels(interaction.user.id)
        view = DungeonRunView(db_cog, interaction.user.id, wallet["equipped_weapon"], stat_levels)
        await interaction.response.edit_message(embed=view.build_embed(), view=view)
        view.message = await interaction.original_response()

    async def _handle_daily(self, db_cog, user_id: int) -> discord.Embed:
        wallet = await db_cog.get_or_create_wallet(user_id)
        now = datetime.now(timezone.utc)
        last_claim = wallet["last_daily_claim"]

        if last_claim is not None:
            elapsed = now - last_claim
            if elapsed < DAILY_COOLDOWN:
                remaining = DAILY_COOLDOWN - elapsed
                hours, rem_seconds = divmod(int(remaining.total_seconds()), 3600)
                minutes = rem_seconds // 60
                return casino_embed(
                    "🎁 Daily Bonus",
                    f"You've already claimed today. Come back in **{hours}h {minutes}m**.",
                )
            streak = wallet["daily_streak"] + 1 if elapsed < DAILY_STREAK_GRACE else 1
        else:
            streak = 1

        amount = daily_amount_for_streak(streak)
        new_balance = await db_cog.set_daily_claim(user_id, amount, streak)

        day_word = "day" if streak == 1 else "days"
        return casino_embed(
            "🎁 Daily Bonus Claimed!",
            f"You received **{amount:,} chips** (streak: {streak} {day_word}).\n"
            f"New balance: **{new_balance:,} chips**.",
        )


class WeaponSelect(discord.ui.Select):
    def __init__(self, armory_view: "ArmoryView"):
        options = []
        for key, weapon in WEAPON_CATALOG.items():
            if key == armory_view.equipped:
                status = "Equipped"
            elif key in armory_view.owned:
                status = "Owned"
            elif weapon["cost"] == 0:
                status = "Free"
            else:
                status = f"{weapon['cost']:,} chips"
            options.append(discord.SelectOption(
                label=weapon["name"], value=key, emoji=weapon["emoji"], description=status,
                default=(key == armory_view.selected),
            ))
        super().__init__(placeholder="Choose a weapon to view", options=options)

    async def callback(self, interaction: discord.Interaction):
        view: ArmoryView = self.view
        view.selected = self.values[0]
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class BuyButton(discord.ui.Button):
    def __init__(self, cost: int):
        super().__init__(label=f"Buy for {cost:,} chips", style=discord.ButtonStyle.success, emoji="🛒")
        self.cost = cost

    async def callback(self, interaction: discord.Interaction):
        view: ArmoryView = self.view
        wallet = await view.db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.cost:
            view.busy = False
            await interaction.response.send_message(
                f"You need {self.cost:,} chips for this — you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return

        await view.db_cog.buy_weapon(interaction.user.id, view.selected, self.cost)
        view.owned.add(view.selected)
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class EquipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Equip", style=discord.ButtonStyle.primary, emoji="✅")

    async def callback(self, interaction: discord.Interaction):
        view: ArmoryView = self.view
        await view.db_cog.set_equipped_weapon(interaction.user.id, view.selected)
        view.equipped = view.selected
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to Casino", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        embed = casino_embed("🎰 Casino", "Pick an option below to get started.")
        view = CasinoView()
        await interaction.response.edit_message(embed=embed, view=view)
        view.message = interaction.message


class ArmoryView(discord.ui.View):
    def __init__(self, db_cog, owned: set, equipped: str):
        super().__init__(timeout=180)
        self.db_cog = db_cog
        self.owned = owned
        self.equipped = equipped
        self.selected = None
        self.rebuild_items()

    @classmethod
    async def create(cls, db_cog, user_id: int) -> "ArmoryView":
        wallet = await db_cog.get_or_create_wallet(user_id)
        owned = set(await db_cog.get_owned_weapons(user_id)) | {STARTER_WEAPON}
        return cls(db_cog, owned, wallet["equipped_weapon"])

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False  # reaching a new stable item state releases the lock
        self.clear_items()
        self.add_item(WeaponSelect(self))
        if self.selected:
            weapon = WEAPON_CATALOG[self.selected]
            if self.selected == self.equipped:
                pass  # already equipped, nothing to do
            elif self.selected in self.owned:
                self.add_item(EquipButton())
            else:
                self.add_item(BuyButton(weapon["cost"]))
        self.add_item(BackButton())

    def build_embed(self) -> discord.Embed:
        if not self.selected:
            lines = []
            for key, weapon in WEAPON_CATALOG.items():
                tag = " (Equipped)" if key == self.equipped else " (Owned)" if key in self.owned else ""
                cost_text = "Free" if weapon["cost"] == 0 else f"{weapon['cost']:,} chips"
                lines.append(f"{weapon['emoji']} **{weapon['name']}** — {cost_text}{tag}")
            embed = casino_embed("🔫 Armory", "Pick a weapon below to see its stats.\n\n" + "\n".join(lines))
            return embed

        weapon = WEAPON_CATALOG[self.selected]
        status = "Equipped" if self.selected == self.equipped else "Owned" if self.selected in self.owned else "Not owned"
        description = (
            f"*{tier_display(weapon)}*\n\n"
            f"{weapon['description']}\n\n"
            f"**Damage:** {format_damage_range(weapon)}\n"
            f"**Hits per round:** {weapon['hits_per_round']}\n"
            f"**Trait:** {trait_display(weapon)}\n"
            f"**Status:** {status}"
        )
        return casino_embed(f"{weapon['emoji']} {weapon['name']}", description)


class StatSelect(discord.ui.Select):
    def __init__(self, stats_view: "StatsView"):
        options = []
        for key, stat in PERMANENT_STATS.items():
            level = stats_view.levels.get(key, 0)
            status = "MAXED" if level >= MAX_STAT_LEVEL else f"Level {level}/{MAX_STAT_LEVEL}"
            options.append(discord.SelectOption(
                label=stat["name"], value=key, emoji=stat["emoji"], description=status,
                default=(key == stats_view.selected),
            ))
        super().__init__(placeholder="Choose a stat to upgrade", options=options)

    async def callback(self, interaction: discord.Interaction):
        view: StatsView = self.view
        view.selected = self.values[0]
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class UpgradeStatButton(discord.ui.Button):
    def __init__(self, cost: int):
        super().__init__(label=f"Upgrade for {cost:,} chips", style=discord.ButtonStyle.success, emoji="⬆️")
        self.cost = cost

    async def callback(self, interaction: discord.Interaction):
        view: StatsView = self.view
        wallet = await view.db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.cost:
            view.busy = False
            await interaction.response.send_message(
                f"You need {self.cost:,} chips for this — you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return

        new_level = await view.db_cog.buy_stat_level(interaction.user.id, view.selected, self.cost)
        view.levels[view.selected] = new_level
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class StatsView(discord.ui.View):
    def __init__(self, db_cog, levels: dict):
        super().__init__(timeout=180)
        self.db_cog = db_cog
        self.levels = levels
        self.selected = None
        self.rebuild_items()

    @classmethod
    async def create(cls, db_cog, user_id: int) -> "StatsView":
        levels = await db_cog.get_stat_levels(user_id)
        return cls(db_cog, levels)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False  # reaching a new stable item state releases the lock
        self.clear_items()
        self.add_item(StatSelect(self))
        if self.selected:
            level = self.levels.get(self.selected, 0)
            if level < MAX_STAT_LEVEL:
                self.add_item(UpgradeStatButton(cost_for_next_level(level)))
        self.add_item(BackButton())

    def build_embed(self) -> discord.Embed:
        if not self.selected:
            lines = []
            for key, stat in PERMANENT_STATS.items():
                level = self.levels.get(key, 0)
                status = "MAXED" if level >= MAX_STAT_LEVEL else f"Level {level}/{MAX_STAT_LEVEL}"
                lines.append(f"{stat['emoji']} **{stat['name']}** — {status}")
            return casino_embed(
                "📈 Stats", "Permanent upgrades for the dungeon — never reset.\n\n" + "\n".join(lines)
            )

        stat = PERMANENT_STATS[self.selected]
        level = self.levels.get(self.selected, 0)
        current_effect = format_effect(self.selected, level)
        description = f"{stat['description']}\n\n**Current level:** {level}/{MAX_STAT_LEVEL}\n**Current bonus:** {current_effect}"
        if level < MAX_STAT_LEVEL:
            next_effect = format_effect(self.selected, level + 1)
            cost = cost_for_next_level(level)
            description += f"\n**Next level:** {next_effect} — {cost:,} chips"
        else:
            description += "\n\n**This stat is fully maxed.**"

        return casino_embed(f"{stat['emoji']} {stat['name']}", description)


class ExitButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Exit", style=discord.ButtonStyle.secondary, emoji="🚪")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()


class CasinoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.message: discord.Message | None = None
        self.busy = False
        self.add_item(CasinoSelect())
        self.add_item(ExitButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    async def on_timeout(self):
        """Grey out the menu once nobody's left to use it — otherwise the
        dropdown and Exit button stay up looking live, and touching a
        dead one just gets Discord's "didn't respond in time" error
        instead of anything happening."""
        if not self.message:
            return
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="casino", description="Open the casino menu.")
    async def casino(self, interaction: discord.Interaction):
        embed = casino_embed("🎰 Casino", "Pick an option below to get started.")
        view = CasinoView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(Casino(bot))
