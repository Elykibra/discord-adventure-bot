# cogs/casino.py

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

from .views.dungeon import start_run as start_dungeon_run, ENTRY_FEE as DUNGEON_ENTRY_FEE
from .views.blackjack import BlackjackBetView, blackjack_bet_embed
from .views.poker import StakeSelectView
from .views.baccarat import create_table as create_baccarat_table
from .views.slots import SlotsBetView, slots_bet_embed
from .views.video_poker import VideoPokerBetView, video_poker_bet_embed
from data.weapons import WEAPON_CATALOG, STARTER_WEAPON, format_damage_range, trait_display, tier_display
from data.permanent_stats import PERMANENT_STATS, MAX_STAT_LEVEL, cost_for_next_level, format_effect
from data.casino_games import CASINO_GAMES
from data.casino_badges import CASINO_BADGES, format_new_badge_field
from data.casino_cosmetics import COSMETIC_CATEGORIES, TITLES, WEAPON_SKINS
from data.casino_leaderboards import LEADERBOARD_CATEGORIES

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
            discord.SelectOption(label="Profile", value="profile", emoji="👤",
                                  description="Balance, loadout, stats, and lifetime performance"),
            discord.SelectOption(label="Balance", value="balance", emoji="💰",
                                  description="Check your chip balance"),
            discord.SelectOption(label="Daily Bonus", value="daily", emoji="🎁",
                                  description="Claim your daily chips"),
            discord.SelectOption(label="Armory", value="armory", emoji="🔫",
                                  description="Buy and equip weapons"),
            discord.SelectOption(label="Stats", value="stats", emoji="📈",
                                  description="Permanent dungeon upgrades"),
            discord.SelectOption(label="Leaderboard", value="leaderboard", emoji="🏆",
                                  description="See how you stack up against everyone else"),
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

        if self.values[0] == "profile":
            # Defer first — ProfileView.create() makes three sequential DB
            # calls before there's anything to show, and left un-acked that
            # chain can (and, live, did) outlast Discord's 3-second
            # interaction window. Same lesson as Baccarat's BetModal fix
            # earlier this session.
            await interaction.response.defer()
            view = await ProfileView.create(db_cog, interaction.user)
            await interaction.edit_original_response(embed=view.build_embed(), view=view)
            return

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
            await interaction.response.edit_message(
                embed=slots_bet_embed(wallet["balance"], wallet.get("equipped_slot_theme")), view=view
            )
            return

        if self.values[0] == "video_poker":
            wallet = await db_cog.get_or_create_wallet(interaction.user.id)
            view = VideoPokerBetView(wallet["balance"])
            await interaction.response.edit_message(embed=video_poker_bet_embed(wallet["balance"]), view=view)
            return

        if self.values[0] == "armory":
            # Defer first — two sequential DB calls (wallet + owned
            # weapons) before responding, same risk class as Profile above.
            await interaction.response.defer()
            view = await ArmoryView.create(db_cog, interaction.user.id)
            await interaction.edit_original_response(embed=view.build_embed(), view=view)
            return

        if self.values[0] == "stats":
            await interaction.response.defer()
            view = await StatsView.create(db_cog, interaction.user.id)
            await interaction.edit_original_response(embed=view.build_embed(), view=view)
            return

        if self.values[0] == "leaderboard":
            # Defer first — the default category's top-10 query plus the
            # requester's rank query chain to two sequential DB calls
            # before responding, same risk class as Profile/Armory/Stats.
            await interaction.response.defer()
            view = await LeaderboardView.create(db_cog, interaction.user.id)
            await interaction.edit_original_response(embed=view.build_embed(), view=view)
            return

        if self.values[0] == "dungeon":
            await self._handle_dungeon_entry(db_cog, interaction)
            return

        if self.values[0] == "blackjack":
            wallet = await db_cog.get_or_create_wallet(interaction.user.id)
            view = BlackjackBetView(wallet["balance"])
            await interaction.response.edit_message(embed=blackjack_bet_embed(wallet["balance"]), view=view)
            return

        # Defer first — _handle_daily's successful-claim path chains
        # three sequential DB calls (wallet + set_daily_claim + badge
        # check, added after this branch was first written) before
        # there's anything to respond with, which live outlasted
        # Discord's 3-second interaction window and killed it outright —
        # same lesson as every other multi-call branch above. Deferred
        # uniformly here since Balance and Daily Bonus share this
        # response tail.
        await interaction.response.defer()
        if self.values[0] == "balance":
            embed = await self._handle_balance(db_cog, interaction.user.id)
        else:
            embed = await self._handle_daily(db_cog, interaction.user.id)

        # Both of these branches stay on this SAME CasinoView instance
        # (self.view) rather than handing off to a new one, so — unlike
        # every branch above — the lock needs releasing here for the menu
        # to stay usable afterward.
        self.view.busy = False
        await interaction.edit_original_response(embed=embed, view=self.view)

    async def _handle_balance(self, db_cog, user_id: int) -> discord.Embed:
        wallet = await db_cog.get_or_create_wallet(user_id)
        return casino_embed("💰 Balance", f"You have **{wallet['balance']:,} chips**.")

    async def _handle_dungeon_entry(self, db_cog, interaction: discord.Interaction):
        # Defer first — this call plus start_dungeon_run()'s own two DB
        # calls chain to three sequential round-trips before anything
        # responds, same risk class as Profile/Armory above.
        await interaction.response.defer()
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < DUNGEON_ENTRY_FEE:
            self.view.busy = False
            await interaction.followup.send(
                f"You need {DUNGEON_ENTRY_FEE:,} chips to enter the dungeon — "
                f"you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return

        await start_dungeon_run(interaction, db_cog, wallet)

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
        # Streak badges (Daily Grinder, Casino Royalty) trigger off the streak
        # itself, not a game result, so they're checked directly here rather
        # than via record_game_result.
        new_badges = await db_cog.check_and_award_badges(user_id)

        day_word = "day" if streak == 1 else "days"
        embed = casino_embed(
            "🎁 Daily Bonus Claimed!",
            f"You received **{amount:,} chips** (streak: {streak} {day_word}).\n"
            f"New balance: **{new_balance:,} chips**.",
        )
        badge_field = format_new_badge_field(new_badges)
        if badge_field:
            embed.add_field(name=badge_field[0], value=badge_field[1], inline=False)
        return embed


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


def _format_leaderboard_value(category: dict, row: dict) -> str:
    value = int(row["value"] or 0)  # SUM(bigint) comes back as Decimal via asyncpg — normalize to int
    noun = category["noun"]

    if category["unit"] == "chips_with_game":
        game_label = CASINO_GAMES.get(row.get("game_key"), {}).get("label", "a game")
        return f"{value:,} {noun} ({game_label})"
    if category["unit"] == "count":
        plural = noun if value == 1 else noun + "s"
        return f"{value:,} {plural}"
    if category["signed"]:
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:,} {noun}"
    return f"{value:,} {noun}"


class LeaderboardSelect(discord.ui.Select):
    def __init__(self, lb_view: "LeaderboardView"):
        options = [
            discord.SelectOption(
                label=category["label"], value=key, emoji=category["emoji"],
                default=(key == lb_view.category_key),
            )
            for key, category in LEADERBOARD_CATEGORIES.items()
        ]
        super().__init__(placeholder="Choose a leaderboard", options=options)

    async def callback(self, interaction: discord.Interaction):
        view: LeaderboardView = self.view
        # Defer first — switching categories re-runs both the top-10 query
        # and the requester's rank query (two sequential DB calls) before
        # there's anything to show, the same risk class as every other
        # 2+-call casino navigation path.
        await interaction.response.defer()
        await view.load_category(self.values[0])
        view.rebuild_items()
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class LeaderboardView(discord.ui.View):
    """One view for every leaderboard category (mirrors ArmoryView/
    StatsView's single-view-rebuilds-its-own-embed shape) — picking a
    category from the dropdown re-queries and redraws in place, no
    drill-down step like the Cosmetics Shop needs."""

    def __init__(self, db_cog, user_id: int, category_key: str, rows: list, user_rank: int):
        super().__init__(timeout=180)
        self.db_cog = db_cog
        self.user_id = user_id
        self.category_key = category_key
        self.rows = rows
        self.user_rank = user_rank
        self.busy = False
        self.rebuild_items()

    @staticmethod
    async def _load(db_cog, user_id: int, category_key: str):
        category = LEADERBOARD_CATEGORIES[category_key]
        rows = await getattr(db_cog, category["list_method"])(limit=10)
        rank = await getattr(db_cog, category["rank_method"])(user_id)
        return rows, rank

    @classmethod
    async def create(cls, db_cog, user_id: int, category_key: str = "richest") -> "LeaderboardView":
        rows, rank = await cls._load(db_cog, user_id, category_key)
        return cls(db_cog, user_id, category_key, rows, rank)

    async def load_category(self, category_key: str):
        self.category_key = category_key
        self.rows, self.user_rank = await self._load(self.db_cog, self.user_id, category_key)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        self.add_item(LeaderboardSelect(self))
        self.add_item(BackButton())

    def build_embed(self) -> discord.Embed:
        category = LEADERBOARD_CATEGORIES[self.category_key]
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        lines = [
            f"{medals.get(i, f'{i}.')} <@{row['user_id']}> — {_format_leaderboard_value(category, row)}"
            for i, row in enumerate(self.rows, start=1)
        ]
        if not lines:
            lines.append("Nobody's on the board yet — be the first!")

        rank_line = "You're #1! 🎉" if self.user_rank == 1 else f"Your rank: **#{self.user_rank}**"
        description = "\n".join(lines) + "\n\n" + rank_line
        return casino_embed(f"{category['emoji']} {category['label']}", description)


class CosmeticItemSelect(discord.ui.Select):
    def __init__(self, cat_view: "CosmeticCategoryView"):
        options = []
        for key, item in cat_view.items.items():
            if key == cat_view.equipped:
                status = "Equipped"
            elif key in cat_view.owned:
                status = "Owned"
            else:
                status = f"{item['price']:,} chips"
            options.append(discord.SelectOption(
                label=item["name"], value=key, emoji=item.get("emoji"), description=status,
                default=(key == cat_view.selected),
            ))
        super().__init__(placeholder="Choose an item to view", options=options)

    async def callback(self, interaction: discord.Interaction):
        view: CosmeticCategoryView = self.view
        view.selected = self.values[0]
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class CosmeticBuyButton(discord.ui.Button):
    def __init__(self, cost: int):
        super().__init__(label=f"Buy for {cost:,} chips", style=discord.ButtonStyle.success, emoji="🛒")
        self.cost = cost

    async def callback(self, interaction: discord.Interaction):
        view: CosmeticCategoryView = self.view
        # Defer first — new code, applies this session's interaction-timeout
        # lesson from the start rather than repeating the older Armory
        # BuyButton's un-deferred shape (get_or_create_wallet then, on the
        # happy path, a second DB call before ever responding).
        await interaction.response.defer()
        wallet = await view.db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.cost:
            view.busy = False
            await interaction.followup.send(
                f"You need {self.cost:,} chips for this — you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return

        await view.db_cog.buy_cosmetic(interaction.user.id, view.selected, self.cost)
        view.owned.add(view.selected)
        view.rebuild_items()
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class CosmeticEquipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Equip", style=discord.ButtonStyle.primary, emoji="✅")

    async def callback(self, interaction: discord.Interaction):
        view: CosmeticCategoryView = self.view
        await interaction.response.defer()
        await view.db_cog.set_equipped_cosmetic(interaction.user.id, view.wallet_column, view.selected)
        view.equipped = view.selected
        view.rebuild_items()
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class ShopBackButton(discord.ui.Button):
    """Back from a category view to the Shop's own category list — distinct
    from BackButton (Casino) and ProfileView's Back (Profile)."""

    def __init__(self):
        super().__init__(label="Back to Shop", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        view = ShopView()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class CosmeticCategoryView(discord.ui.View):
    """Generic across every cosmetic category — one class, not one per
    category, parameterized by category_key. Mirrors ArmoryView's exact
    shape (create/interaction_check/rebuild_items/build_embed)."""

    def __init__(self, db_cog, category_key: str, owned: set, equipped: str | None):
        super().__init__(timeout=180)
        self.db_cog = db_cog
        self.category_key = category_key
        category = COSMETIC_CATEGORIES[category_key]
        self.items = category["items"]
        self.wallet_column = category["wallet_column"]
        self.label = category["label"]
        self.owned = owned
        self.equipped = equipped
        self.selected = None
        self.rebuild_items()

    @classmethod
    async def create(cls, db_cog, user_id: int, category_key: str) -> "CosmeticCategoryView":
        wallet = await db_cog.get_or_create_wallet(user_id)
        owned = await db_cog.get_owned_cosmetics(user_id)
        wallet_column = COSMETIC_CATEGORIES[category_key]["wallet_column"]
        return cls(db_cog, category_key, owned, wallet.get(wallet_column))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False  # reaching a new stable item state releases the lock
        self.clear_items()
        self.add_item(CosmeticItemSelect(self))
        if self.selected:
            if self.selected == self.equipped:
                pass  # already equipped, nothing to do
            elif self.selected in self.owned:
                self.add_item(CosmeticEquipButton())
            else:
                self.add_item(CosmeticBuyButton(self.items[self.selected]["price"]))
        self.add_item(ShopBackButton())

    def build_embed(self) -> discord.Embed:
        category_emoji = COSMETIC_CATEGORIES[self.category_key]["emoji"]

        if not self.selected:
            lines = []
            for key, item in self.items.items():
                tag = " (Equipped)" if key == self.equipped else " (Owned)" if key in self.owned else ""
                emoji = item.get("emoji", "")
                applies_to = f" — for {WEAPON_CATALOG[item['weapon_key']]['name']}" if "weapon_key" in item else ""
                lines.append(f"{emoji} **{item['name']}** — {item['price']:,} chips{tag}{applies_to}")
            return casino_embed(
                f"{category_emoji} {self.label}", "Pick an item below to see details.\n\n" + "\n".join(lines)
            )

        item = self.items[self.selected]
        status = "Equipped" if self.selected == self.equipped else "Owned" if self.selected in self.owned else "Not owned"
        emoji = item.get("emoji", "")
        description = f"{item['description']}\n\n**Price:** {item['price']:,} chips\n**Status:** {status}"
        if "weapon_key" in item:
            description += f"\n**Applies to:** {WEAPON_CATALOG[item['weapon_key']]['name']} (only while that weapon is equipped)"
        return casino_embed(f"{emoji} {item['name']}", description)


class ShopCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category["label"], value=key, emoji=category["emoji"])
            for key, category in COSMETIC_CATEGORIES.items()
        ]
        super().__init__(placeholder="Choose a category to browse", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = interaction.client.get_cog('Database')
        cat_view = await CosmeticCategoryView.create(db_cog, interaction.user.id, self.values[0])
        await interaction.edit_original_response(embed=cat_view.build_embed(), view=cat_view)


class ShopBackToProfileButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to Profile", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = interaction.client.get_cog('Database')
        view = await ProfileView.create(db_cog, interaction.user)
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class ShopView(discord.ui.View):
    """The cosmetics shop's top-level category picker — reached from
    Profile's Cosmetics button."""

    def __init__(self):
        super().__init__(timeout=180)
        self.busy = False
        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        self.add_item(ShopCategorySelect())
        self.add_item(ShopBackToProfileButton())

    def build_embed(self) -> discord.Embed:
        lines = [f"{category['emoji']} **{category['label']}**" for category in COSMETIC_CATEGORIES.values()]
        return casino_embed("🎨 Cosmetics Shop", "Pick a category below to browse.\n\n" + "\n".join(lines))


class ProfileArmoryButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Armory", style=discord.ButtonStyle.secondary, emoji="🔫")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = interaction.client.get_cog('Database')
        view = await ArmoryView.create(db_cog, interaction.user.id)
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class ProfileStatsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stats", style=discord.ButtonStyle.secondary, emoji="📈")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = interaction.client.get_cog('Database')
        view = await StatsView.create(db_cog, interaction.user.id)
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class ProfileCosmeticsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cosmetics", style=discord.ButtonStyle.secondary, emoji="🎨")

    async def callback(self, interaction: discord.Interaction):
        view = ShopView()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class ProfileView(discord.ui.View):
    def __init__(self, db_cog, display_name: str, wallet: dict, stat_levels: dict, game_stats: dict,
                 earned_badges: list[str]):
        super().__init__(timeout=180)
        self.db_cog = db_cog
        self.display_name = display_name
        self.wallet = wallet
        self.stat_levels = stat_levels
        self.game_stats = game_stats  # game_key -> stats dict, one entry per CASINO_GAMES key
        self.earned_badges = earned_badges
        self.busy = False
        self.rebuild_items()

    @classmethod
    async def create(cls, db_cog, user) -> "ProfileView":
        wallet = await db_cog.get_or_create_wallet(user.id)
        stat_levels = await db_cog.get_stat_levels(user.id)
        raw_stats = await db_cog.get_all_game_stats(user.id)
        earned_badges = await db_cog.get_earned_badges(user.id)

        game_stats = {}
        for key in CASINO_GAMES:
            game_stats[key] = raw_stats.get(key) or {
                "plays": 0, "wins": 0, "total_wagered": 0, "total_won": 0,
                "net_chips": 0, "biggest_win": 0, "extra": {},
            }

        return cls(db_cog, user.display_name, wallet, stat_levels, game_stats, earned_badges)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False  # reaching a new stable item state releases the lock
        self.clear_items()
        self.add_item(ProfileArmoryButton())
        self.add_item(ProfileStatsButton())
        self.add_item(ProfileCosmeticsButton())
        self.add_item(BackButton())

    def build_embed(self) -> discord.Embed:
        wallet = self.wallet
        weapon = WEAPON_CATALOG[wallet["equipped_weapon"]]
        streak = wallet["daily_streak"]

        lines = []
        title_key = wallet.get("equipped_title")
        if title_key:
            lines += [f"*{TITLES[title_key]['name']}*", ""]

        weapon_skin_key = wallet.get("equipped_weapon_skin")
        if weapon_skin_key and WEAPON_SKINS[weapon_skin_key]["weapon_key"] == wallet["equipped_weapon"]:
            skin = WEAPON_SKINS[weapon_skin_key]
            loadout_line = f"{skin['emoji']} {skin['name']}"
        else:
            loadout_line = f"{weapon['emoji']} {weapon['name']}"

        lines += [
            "**💰 Wallet**",
            f"Balance: **{wallet['balance']:,} chips**",
            f"Daily streak: **{streak} day{'s' if streak != 1 else ''}**",
            "",
            "**🔫 Loadout**",
            loadout_line,
            "",
            "**🎖️ Badges**",
        ]
        earned_set = set(self.earned_badges)
        if not earned_set:
            lines.append("No badges earned yet — keep playing to unlock some!")
        else:
            for key, badge in CASINO_BADGES.items():
                if key in earned_set:
                    lines.append(f"{badge['emoji']} **{badge['name']}** — {badge['description']}")
        locked_count = len(CASINO_BADGES) - len(earned_set)
        if locked_count > 0:
            lines.append(f"🔒 {locked_count} more to discover")

        lines += [
            "",
            "**📈 Permanent Stats**",
        ]
        for key, stat in PERMANENT_STATS.items():
            level = self.stat_levels.get(key, 0)
            lines.append(f"{stat['emoji']} {stat['name']}: Level {level}/{MAX_STAT_LEVEL}")

        lines += [
            "",
            "**🎨 Cosmetics**",
        ]
        lines += self._equipped_cosmetics_lines()

        lines += [
            "",
            "**📊 Career Highlights**",
        ]
        lines.append(self._career_highlight_line())
        lines.append(self._favorite_game_line())

        lines += [
            "",
            "**🎲 Lifetime Performance**",
        ]
        for key, info in CASINO_GAMES.items():
            stats = self.game_stats[key]
            if stats["plays"] == 0:
                lines.append(f"{info['emoji']} **{info['label']}** — Not played yet")
                continue
            win_rate = stats["wins"] / stats["plays"] * 100
            net = stats["net_chips"]
            net_text = f"+{net:,}" if net >= 0 else f"{net:,}"
            plays_word = "play" if stats["plays"] == 1 else "plays"
            lines.append(
                f"{info['emoji']} **{info['label']}** — {stats['plays']:,} {plays_word}, "
                f"{win_rate:.0f}% win rate, net {net_text}"
            )

        return casino_embed(f"👤 {self.display_name}'s Casino Profile", "\n".join(lines))

    def _equipped_cosmetics_lines(self) -> list[str]:
        lines = []
        for category in COSMETIC_CATEGORIES.values():
            cosmetic_key = self.wallet.get(category["wallet_column"])
            if not cosmetic_key:
                continue
            item = category["items"][cosmetic_key]
            emoji = item.get("emoji", "")
            lines.append(f"{category['emoji']} {category['label']}: {emoji} {item['name']}".replace("  ", " "))
        if not lines:
            return ["Nothing equipped yet — visit the shop!"]
        return lines

    def _career_highlight_line(self) -> str:
        best_key, best_win = None, 0
        for key, stats in self.game_stats.items():
            if stats["biggest_win"] > best_win:
                best_key, best_win = key, stats["biggest_win"]
        if best_key is None:
            return "🏆 Biggest win ever: None yet — go get your first big win!"
        label = CASINO_GAMES[best_key]["label"]
        return f"🏆 Biggest win ever: **{best_win:,} chips** ({label})"

    def _favorite_game_line(self) -> str:
        best_key, best_plays = None, 0
        for key, stats in self.game_stats.items():
            if stats["plays"] > best_plays:
                best_key, best_plays = key, stats["plays"]
        if best_key is None:
            return "❤️ Favorite game: Haven't picked one yet"
        info = CASINO_GAMES[best_key]
        plays_word = "play" if best_plays == 1 else "plays"
        return f"❤️ Favorite game: {info['emoji']} {info['label']} ({best_plays:,} {plays_word})"


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
