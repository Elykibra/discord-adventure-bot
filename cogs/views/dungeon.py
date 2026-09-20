# cogs/views/dungeon.py
#
# The dungeon run: room-by-room push-your-luck exploration, round-by-round
# autobattler combat using the equipped weapon, and — new — in-run level-up
# skill picks (Risk of Rain 2 / Gunfire Reborn style stacking upgrades).
# Skills are entirely temporary: they reset when the run ends, win or lose.
# Permanent progression (spent between runs) is a separate, later piece.
#
# Every button defers its interaction first and uses edit_original_response
# for all subsequent updates, because Fight (and now level-up picks) need
# several sequential edits — an interaction can only be "responded to" once,
# so this keeps every button's update flow consistent.
#
# Permanent stats (bought between runs, never reset) seed the *starting*
# values of the same fields the in-run skills modify — a run's build is
# permanent bonuses plus whatever skills got picked this run, stacked.

import asyncio
import discord
import random

from data.dungeon_floors import (
    get_theme_for_floor, get_rooms_per_floor, roll_mob_for_floor,
    is_boss_floor, get_boss_for_floor, maybe_roll_mini_boss, maybe_roll_event,
)
from data.weapons import WEAPON_CATALOG
from data.dungeon_skills import SKILL_POOL, draw_skill_choices, DODGE_CAP
from data.permanent_stats import PERMANENT_STATS
from data.casino_badges import format_new_badge_field
from data.casino_cosmetics import TAUNTS

ENTRY_FEE = 100
STARTING_HP = 100
CASH_OUT_FROM_ROOM = 2
REST_HEAL_FRACTION = 0.25
SEARCH_TRAP_CHANCE = 0.3
RUN_TIMEOUT_SECONDS = 600

MAX_COMBAT_ROUNDS = 20
ROUND_DELAY_SECONDS = 1.2
COMBAT_LOG_LINES_SHOWN = 6
LEVELUP_CHOICES_OFFERED = 3

# Mob trait tuning — see data/dungeon_floors.py for which mobs carry which trait.
ARMORED_DAMAGE_REDUCTION = 0.25  # "armored": takes 25% less damage from the player
EXECUTE_HP_THRESHOLD = 0.3       # "execute": bonus damage triggers below this HP fraction
EXECUTE_DAMAGE_MULTIPLIER = 1.75
CURSE_TICK_DAMAGE = 3            # "cursed": guaranteed extra damage each round, dodge or not


class DungeonRunView(discord.ui.View):
    def __init__(self, db_cog, user_id: int, weapon_key: str, stat_levels: dict | None = None,
                 *, taunt_key: str | None = None):
        super().__init__(timeout=RUN_TIMEOUT_SECONDS)
        self.db_cog = db_cog
        self.user_id = user_id
        self.weapon_key = weapon_key
        self.taunt_key = taunt_key
        stat_levels = stat_levels or {}

        vitality = stat_levels.get("vitality", 0) * PERMANENT_STATS["vitality"]["value_per_level"]
        luck = stat_levels.get("luck", 0) * PERMANENT_STATS["luck"]["value_per_level"]
        greed = stat_levels.get("greed", 0) * PERMANENT_STATS["greed"]["value_per_level"]

        self.max_hp = STARTING_HP + int(vitality)
        self.hp = self.max_hp
        self.floor = 1
        self.room_in_floor = 1
        self.room_number = 1
        self.banked = 0
        self.last_event = "You step into the dungeon. Choose your move."
        self.finished = False
        self.message: discord.Message | None = None

        # In-run build — resets every run, stacks across level-ups this run
        # on top of the permanent bonuses seeded above.
        self.skills: list[str] = []
        self.damage_bonus = 0.0
        self.lifesteal_bonus = 0.0
        self.extra_hits = 0
        self.loot_bonus = greed
        self.dodge_chance = min(DODGE_CAP, luck)
        self.regen_per_room = 0
        self.has_second_wind = False

        self.pending_levelup = False
        self.levelup_choices: list[str] = []
        self.boss_floor_pending = False

        # Guards against double-clicking a button before the previous click's
        # response has landed — Discord sends each click as a separate
        # interaction, so without this a fast double-click on Search (or
        # anything else) could resolve the same room twice.
        self.busy = False

        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message(
                "Still resolving your last move — hang on a second.", ephemeral=True
            )
            return False
        self.busy = True
        return True

    # --- Skills / build ---
    def apply_skill(self, skill_key: str):
        skill = SKILL_POOL[skill_key]
        self.skills.append(skill_key)
        kind, value = skill["type"], skill["value"]

        if kind == "max_hp":
            self.max_hp += value
            self.hp = min(self.max_hp, self.hp + value)
        elif kind == "lifesteal_pct":
            self.lifesteal_bonus += value
        elif kind == "damage_pct":
            self.damage_bonus += value
        elif kind == "extra_hits":
            self.extra_hits += value
        elif kind == "loot_pct":
            self.loot_bonus += value
        elif kind == "dodge_pct":
            self.dodge_chance = min(DODGE_CAP, self.dodge_chance + value)
        elif kind == "regen_per_room":
            self.regen_per_room += value
        elif kind == "second_wind":
            self.has_second_wind = True

    def take_damage(self, amount: int, *, ignore_dodge: bool = False) -> dict:
        """Applies incoming damage, respecting dodge and Second Wind.
        Returns {'dodged', 'died', 'second_wind'} — self.hp is already updated.
        ignore_dodge is for mobs with the pierce_dodge trait (e.g. ranged attackers)."""
        if not ignore_dodge and self.dodge_chance > 0 and random.random() < self.dodge_chance:
            return {"dodged": True, "died": False, "second_wind": False}

        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            if self.has_second_wind:
                self.has_second_wind = False
                self.hp = 1
                return {"dodged": False, "died": False, "second_wind": True}
            return {"dodged": False, "died": True, "second_wind": False}
        return {"dodged": False, "died": False, "second_wind": False}

    def apply_loot_bonus(self, amount: int) -> int:
        return int(amount * (1 + self.loot_bonus))

    # --- View state ---
    def rebuild_items(self):
        self.busy = False  # reaching a new stable button state releases the lock
        self.clear_items()
        if self.finished:
            return
        if self.pending_levelup:
            for key in self.levelup_choices:
                self.add_item(LevelUpButton(key))
            return
        if self.boss_floor_pending:
            self.add_item(BossFightButton())
            return
        self.add_item(FightButton())
        self.add_item(SearchButton())
        self.add_item(RestButton())
        if self.room_number >= CASH_OUT_FROM_ROOM:
            self.add_item(CashOutButton())
        if self.skills:
            self.add_item(BuildSelect(self.skills))

    def build_embed(self) -> discord.Embed:
        theme = get_theme_for_floor(self.floor)
        color = discord.Color.dark_grey() if self.finished and self.hp <= 0 else \
            discord.Color.green() if self.finished else \
            discord.Color.blurple() if self.pending_levelup else discord.Color.dark_gold()

        embed = discord.Embed(
            title=f"🗝️ Dungeon — Floor {self.floor} ({theme['name']})",
            description=self.last_event,
            color=color,
        )
        embed.add_field(name="HP", value=f"{self.hp}/{self.max_hp}", inline=True)
        embed.add_field(name="Banked", value=f"{self.banked:,} chips", inline=True)
        embed.add_field(name="Room", value=f"{self.room_in_floor}/{get_rooms_per_floor(self.floor)}", inline=True)

        if self.skills:
            embed.add_field(name="Build", value=f"{len(self.skills)} active — see the dropdown below", inline=True)

        return embed

    async def push_update(self, interaction: discord.Interaction):
        """Edits the run message. Call after interaction.response.defer()."""
        await interaction.edit_original_response(embed=self.build_embed(), view=self)

    async def offer_levelup(self, interaction: discord.Interaction):
        self.pending_levelup = True
        self.levelup_choices = draw_skill_choices(self.skills, LEVELUP_CHOICES_OFFERED)
        choice_lines = "\n".join(
            f"{SKILL_POOL[key]['emoji']} **{SKILL_POOL[key]['name']}** — {SKILL_POOL[key]['description']}"
            for key in self.levelup_choices
        )
        self.last_event += f"\n\n**Level Up!** Choose an upgrade:\n{choice_lines}"
        self.rebuild_items()
        await self.push_update(interaction)

    async def advance_room(self, interaction: discord.Interaction):
        self.room_number += 1
        self.room_in_floor += 1
        leveled_up = False

        if self.room_in_floor > get_rooms_per_floor(self.floor):
            self.room_in_floor = 1
            self.floor += 1
            self.last_event += f"\n\n**You descend to Floor {self.floor}.**"
            leveled_up = True
            if is_boss_floor(self.floor):
                self.boss_floor_pending = True

        if self.regen_per_room > 0 and self.hp < self.max_hp:
            healed = min(self.regen_per_room, self.max_hp - self.hp)
            self.hp += healed
            self.last_event += f"\n🩹 Passive regen heals **{healed} HP**."

        if not leveled_up:
            event = maybe_roll_event()
            if event:
                if event["type"] == "loot":
                    amount = self.apply_loot_bonus(random.randint(*event["value"]))
                    self.banked += amount
                    self.last_event += f"\n\n{event['text']} (+{amount} chips)"
                elif event["type"] == "heal":
                    healed = min(event["value"], self.max_hp - self.hp)
                    self.hp += healed
                    self.last_event += f"\n\n{event['text']}" + (f" (+{healed} HP)" if healed > 0 else "")
                else:
                    self.last_event += f"\n\n{event['text']}"

        if leveled_up:
            await self.offer_levelup(interaction)
            return

        self.rebuild_items()
        await self.push_update(interaction)

    async def advance_past_boss(self, interaction: discord.Interaction):
        """Called after a boss is defeated — skips straight to the next floor
        (the boss fight replaces that floor's normal rooms entirely)."""
        self.room_number += 1
        self.floor += 1
        self.room_in_floor = 1
        self.last_event += f"\n\n**The way opens. You descend to Floor {self.floor}.**"
        self.rebuild_items()
        await self.push_update(interaction)

    async def end_run(self, interaction: discord.Interaction, *, died: bool):
        self.finished = True
        payout = 0 if died else self.banked
        if payout > 0:
            await self.db_cog.add_chips(self.user_id, payout)
        await self.db_cog.log_dungeon_run(
            self.user_id, self.floor, "died" if died else "cashed_out", payout, self.weapon_key
        )
        new_badges = await self.db_cog.record_game_result(
            self.user_id, "dungeon", wagered=ENTRY_FEE, won=payout, is_win=(not died)
        )

        if died:
            self.last_event += (
                f"\n\n💀 **You died on Floor {self.floor}.** "
                f"You lost the {self.banked:,} chips banked this run."
            )
        else:
            self.last_event += f"\n\n✅ **Cashed out on Floor {self.floor}.** {payout:,} chips added to your wallet."

        self.rebuild_items()
        embed = self.build_embed()
        badge_field = format_new_badge_field(new_badges)
        if badge_field:
            embed.add_field(name=badge_field[0], value=badge_field[1], inline=False)
        if self.taunt_key:
            embed.add_field(name="💬 Taunt", value=TAUNTS[self.taunt_key]["text"], inline=False)
        result_view = DungeonResultView(self.user_id)
        message = await interaction.edit_original_response(embed=embed, view=result_view)
        result_view.message = message
        self.stop()

    async def on_timeout(self):
        if self.finished or not self.message:
            return
        self.finished = True
        payout = self.banked
        if payout > 0:
            await self.db_cog.add_chips(self.user_id, payout)
        await self.db_cog.log_dungeon_run(self.user_id, self.floor, "cashed_out", payout, self.weapon_key)
        new_badges = await self.db_cog.record_game_result(
            self.user_id, "dungeon", wagered=ENTRY_FEE, won=payout, is_win=True
        )
        self.last_event += f"\n\n⏱️ **Auto-cashed out after inactivity.** {payout:,} chips added to your wallet."
        self.rebuild_items()
        embed = self.build_embed()
        badge_field = format_new_badge_field(new_badges)
        if badge_field:
            embed.add_field(name=badge_field[0], value=badge_field[1], inline=False)
        if self.taunt_key:
            embed.add_field(name="💬 Taunt", value=TAUNTS[self.taunt_key]["text"], inline=False)
        result_view = DungeonResultView(self.user_id)
        try:
            await self.message.edit(embed=embed, view=result_view)
            result_view.message = self.message
        except discord.HTTPException:
            pass


async def start_run(interaction: discord.Interaction, db_cog, wallet: dict):
    """Deducts the entry fee and starts a fresh run — shared by the
    initial /casino entry and Play Again after a previous run ends.
    `wallet` is the caller's already-fetched wallet dict (used for its
    balance-sufficiency check just before calling this), so this
    doesn't re-fetch it — just needs the equipped_weapon it already has.

    Callers must defer the interaction before calling this — it does
    two more DB round-trips (the deduction, then stat levels) before
    there's anything to respond with, which on top of whatever the
    caller already awaited can outlast Discord's 3-second interaction
    window if nothing acked it first."""
    await db_cog.add_chips(interaction.user.id, -ENTRY_FEE)
    stat_levels = await db_cog.get_stat_levels(interaction.user.id)
    view = DungeonRunView(
        db_cog, interaction.user.id, wallet["equipped_weapon"], stat_levels,
        taunt_key=wallet.get("equipped_taunt"),
    )
    message = await interaction.edit_original_response(embed=view.build_embed(), view=view)
    view.message = message


class DungeonPlayAgainButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label=f"Play Again ({ENTRY_FEE:,})", style=discord.ButtonStyle.success, emoji="🗝️")

    async def callback(self, interaction: discord.Interaction):
        view: DungeonResultView = self.view
        db_cog = interaction.client.get_cog('Database')
        # Defer first — this callback's own wallet lookup plus start_run()'s
        # two more DB calls chain to three sequential round-trips before
        # anything responds, the same risk class fixed live in casino.py's
        # Profile/Armory/Stats/dungeon-entry paths.
        await interaction.response.defer()
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < ENTRY_FEE:
            view.busy = False
            await interaction.followup.send(
                f"You need {ENTRY_FEE:,} chips to enter the dungeon again — "
                f"you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return
        await start_run(interaction, db_cog, wallet)


class DungeonBackToCasinoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to Casino", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        from cogs.casino import casino_embed, CasinoView  # local import avoids a circular import
        embed = casino_embed("🎰 Casino", "Pick an option below to get started.")
        view = CasinoView()
        await interaction.response.edit_message(embed=embed, view=view)
        view.message = interaction.message


class DungeonResultView(discord.ui.View):
    """Shown once a run ends (died, cashed out, or auto-cashed-out on
    timeout) — lets the player start a fresh run or head back to the
    casino, same Play Again / Back to Casino pattern as every other
    solo game. No ownership check needed: this message is the same
    ephemeral one the player used to enter /casino in the first place,
    so nobody else can ever see or click it."""

    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.busy = False
        self.message: discord.Message | None = None
        self.add_item(DungeonPlayAgainButton())
        self.add_item(DungeonBackToCasinoButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    async def on_timeout(self):
        """Grey out Play Again / Back to Casino once nobody's left to
        click them — same close pattern as every other result view."""
        if not self.message:
            return
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass


class BuildSelect(discord.ui.Select):
    """Purely informational — lets a player browse their current run's build
    (with real descriptions, shown natively by Discord's dropdown) without
    the main embed growing a line for every skill picked up over the run."""

    def __init__(self, skills: list[str]):
        counts: dict[str, int] = {}
        for key in skills:
            counts[key] = counts.get(key, 0) + 1

        options = []
        for key, count in counts.items():
            skill = SKILL_POOL[key]
            label = skill["name"] + (f" x{count}" if count > 1 else "")
            options.append(discord.SelectOption(
                label=label, value=key, emoji=skill["emoji"], description=skill["description"][:100],
            ))

        super().__init__(placeholder=f"📋 View your build ({len(skills)} active)", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Nothing to apply — the dropdown's own descriptions are the point.
        # Still release the busy lock interaction_check took, since this
        # path never reaches rebuild_items().
        view: DungeonRunView = self.view
        view.busy = False
        await interaction.response.defer()


class LevelUpButton(discord.ui.Button):
    def __init__(self, skill_key: str):
        skill = SKILL_POOL[skill_key]
        super().__init__(label=skill["name"], style=discord.ButtonStyle.primary, emoji=skill["emoji"])
        self.skill_key = skill_key

    async def callback(self, interaction: discord.Interaction):
        view: DungeonRunView = self.view
        await interaction.response.defer()

        skill = SKILL_POOL[self.skill_key]
        view.apply_skill(self.skill_key)
        view.last_event = f"{skill['emoji']} You gained **{skill['name']}**! {skill['description']}"
        view.pending_levelup = False
        view.levelup_choices = []
        view.rebuild_items()
        await view.push_update(interaction)


async def resolve_combat(view: "DungeonRunView", interaction: discord.Interaction, mob: dict, *, intro: str) -> dict:
    """Runs a full round-by-round fight against `mob` (a normal roll, a mini-boss, or a boss —
    all share the same {name, emoji, hp, damage, trait} shape). Applies loot to view.banked on a
    win. Does NOT advance run state afterward — the caller decides what happens next.
    Returns {'won': bool, 'died': bool}."""
    weapon = WEAPON_CATALOG[view.weapon_key]
    mob_hp = mob["hp"]
    max_mob_hp = mob["hp"]
    trait = mob["trait"]
    log = [intro]

    base_lifesteal = weapon.get("trait_value", 0) if weapon["trait"] == "lifesteal" else 0
    total_lifesteal = base_lifesteal + view.lifesteal_bonus
    total_hits = weapon["hits_per_round"] + view.extra_hits

    for item in view.children:
        item.disabled = True
    view.last_event = "\n".join(log)
    await view.push_update(interaction)

    round_number = 1
    while mob_hp > 0 and view.hp > 0 and round_number <= MAX_COMBAT_ROUNDS:
        await asyncio.sleep(ROUND_DELAY_SECONDS)

        dmg_lo, dmg_hi = weapon["damage"]
        damage_dealt = 0
        for _ in range(total_hits):
            if mob_hp <= 0:
                break
            hit = int(random.randint(dmg_lo, dmg_hi) * (1 + view.damage_bonus))
            if trait == "armored":
                hit = int(hit * (1 - ARMORED_DAMAGE_REDUCTION))
            mob_hp = max(0, mob_hp - hit)
            damage_dealt += hit

        heal_note = ""
        if total_lifesteal > 0 and damage_dealt > 0:
            heal = int(damage_dealt * total_lifesteal)
            if heal > 0:
                view.hp = min(view.max_hp, view.hp + heal)
                heal_note = f" (healed {heal} HP)"

        armor_note = " (armored — reduced)" if trait == "armored" else ""
        log.append(f"**Round {round_number}:** You deal {damage_dealt} damage{armor_note}{heal_note}. "
                   f"{mob['name']} HP: {mob_hp}/{max_mob_hp}")

        if mob_hp <= 0:
            break

        # "slow" mobs only swing on even rounds — hit hard, but rarely.
        if trait == "slow" and round_number % 2 == 1:
            log.append(f"{mob['emoji']} {mob['name']} winds up a heavy strike...")
            view.last_event = "\n".join(log[-COMBAT_LOG_LINES_SHOWN:])
            await view.push_update(interaction)
            round_number += 1
            continue

        mob_dmg = random.randint(*mob["damage"])
        if trait == "execute" and view.hp / view.max_hp <= EXECUTE_HP_THRESHOLD:
            mob_dmg = int(mob_dmg * EXECUTE_DAMAGE_MULTIPLIER)

        result = view.take_damage(mob_dmg, ignore_dodge=(trait == "pierce_dodge"))
        if result["dodged"]:
            log.append(f"💨 You dodge the {mob['emoji']} {mob['name']}'s attack!")
        elif result["second_wind"]:
            log.append(f"🌬️ The {mob['emoji']} {mob['name']} lands a lethal blow — "
                       f"**Second Wind** saves you at 1 HP!")
        elif trait == "execute" and mob_dmg > 0:
            log.append(f"💀 The {mob['emoji']} {mob['name']} senses your weakness and strikes for "
                       f"**{mob_dmg} damage**! Your HP: {view.hp}/{view.max_hp}")
        else:
            log.append(f"{mob['emoji']} {mob['name']} hits you for {mob_dmg}. Your HP: {view.hp}/{view.max_hp}")

        # "cursed" mobs also land a small guaranteed tick, dodge or not — on top of the above.
        if trait == "cursed" and not result["died"]:
            curse = view.take_damage(CURSE_TICK_DAMAGE, ignore_dodge=True)
            if curse["second_wind"]:
                log.append("🌬️ A lingering curse should have finished you — **Second Wind** saves you at 1 HP!")
            elif curse["died"]:
                log.append(f"🔮 A lingering curse saps the last of your strength for **{CURSE_TICK_DAMAGE}**.")
            else:
                log.append(f"🔮 A lingering curse saps **{CURSE_TICK_DAMAGE}** HP regardless. "
                           f"Your HP: {view.hp}/{view.max_hp}")
            if curse["died"] or curse["second_wind"]:
                result = curse

        view.last_event = "\n".join(log[-COMBAT_LOG_LINES_SHOWN:])
        await view.push_update(interaction)

        if result["died"]:
            break
        round_number += 1

    if view.hp <= 0:
        view.last_event = "\n".join(log[-COMBAT_LOG_LINES_SHOWN:])
        return {"won": False, "died": True}

    if mob_hp <= 0:
        base_loot = random.randint(20, 40) + view.floor * 5
        loot = view.apply_loot_bonus(int(base_loot * mob.get("loot_multiplier", 1.0)))
        view.banked += loot
        log.append(f"🎉 You defeated the {mob['emoji']} **{mob['name']}** and found **{loot} chips**!")
        view.last_event = "\n".join(log[-COMBAT_LOG_LINES_SHOWN:])
        return {"won": True, "died": False}

    log.append("The fight drags on... you disengage and move on.")
    view.last_event = "\n".join(log[-COMBAT_LOG_LINES_SHOWN:])
    return {"won": False, "died": False}


class FightButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Fight", style=discord.ButtonStyle.danger, emoji="⚔️")

    async def callback(self, interaction: discord.Interaction):
        view: DungeonRunView = self.view
        await interaction.response.defer()

        mini_boss = maybe_roll_mini_boss(view.floor)
        mob = mini_boss or roll_mob_for_floor(view.floor)
        intro = (f"⭐ A {mob['emoji']} **{mob['name']}** appears — this one's tougher than usual!"
                 if mini_boss else f"A {mob['emoji']} **{mob['name']}** blocks your path!")

        result = await resolve_combat(view, interaction, mob, intro=intro)
        if result["died"]:
            await view.end_run(interaction, died=True)
        else:
            await view.advance_room(interaction)


class BossFightButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Fight Boss", style=discord.ButtonStyle.danger, emoji="👑")

    async def callback(self, interaction: discord.Interaction):
        view: DungeonRunView = self.view
        await interaction.response.defer()

        boss = get_boss_for_floor(view.floor)
        intro = f"👑 **BOSS: {boss['name']}**\n{boss.get('description', '')}"

        result = await resolve_combat(view, interaction, boss, intro=intro)
        if result["died"]:
            await view.end_run(interaction, died=True)
        else:
            view.boss_floor_pending = False
            await view.advance_past_boss(interaction)


class SearchButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Search", style=discord.ButtonStyle.primary, emoji="🔍")

    async def callback(self, interaction: discord.Interaction):
        view: DungeonRunView = self.view
        await interaction.response.defer()

        if random.random() < SEARCH_TRAP_CHANCE:
            dmg = random.randint(5, 10)
            result = view.take_damage(dmg)
            if result["dodged"]:
                view.last_event = "🔍 It was a trap — but you dodged it entirely!"
            elif result["second_wind"]:
                view.last_event = "🔍 It was a trap! The blast should have killed you — **Second Wind** saves you at 1 HP!"
            elif result["died"]:
                view.last_event = f"🔍 It was a trap! You took **{dmg} damage**."
                await view.end_run(interaction, died=True)
                return
            else:
                view.last_event = f"🔍 It was a trap! You took **{dmg} damage**."
        else:
            loot = view.apply_loot_bonus(random.randint(10, 25))
            view.banked += loot
            view.last_event = f"🔍 You found a stash of **{loot} chips**."
        await view.advance_room(interaction)


class RestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Rest", style=discord.ButtonStyle.secondary, emoji="💤")

    async def callback(self, interaction: discord.Interaction):
        view: DungeonRunView = self.view
        await interaction.response.defer()

        heal = int(view.max_hp * REST_HEAL_FRACTION)
        view.hp = min(view.max_hp, view.hp + heal)
        view.last_event = f"💤 You rest and recover **{heal} HP**."
        await view.advance_room(interaction)


class CashOutButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cash Out", style=discord.ButtonStyle.success, emoji="💰")

    async def callback(self, interaction: discord.Interaction):
        view: DungeonRunView = self.view
        await interaction.response.defer()
        await view.end_run(interaction, died=False)
