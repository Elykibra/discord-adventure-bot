# cogs/adventure.py

import discord
import traceback
import random
import math
from discord import app_commands
from discord.ext import commands

# --- REFACTORED IMPORTS ---
from data.towns import TOWNS
from data.pets import PET_DATABASE, ENCOUNTER_TABLES
from data.items import ITEMS
from data.abilities import SHARED_PASSIVES_BY_TYPE
from data.explore_events import get_zone_events, get_zone_loot
from utils.helpers import get_status_bar, get_town_embed, check_quest_progress, get_notification
from core.battle_engine import BattleState  # <-- Key Change: Importing from core
from .resources import ACTION_COSTS
from .views.towns import TownView, WildsView
from .views.combat import CombatView


class Adventure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='adventure', description='Opens the menu for your current location.')
    async def adventure_menu(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        if not player_data:
            return await interaction.followup.send("You have not started your adventure! Use `/start` to begin.",
                                                   ephemeral=True)

        location_id = player_data.get('current_location', 'oakhavenOutpost')
        location_data = TOWNS.get(location_id, {})
        view = None
        embed = None

        if location_data.get('is_wilds', False):
            view = WildsView(self.bot, interaction, location_id)
            embed = view.embed
        else:
            embed = await get_town_embed(self.bot, interaction.user.id, location_id)
            view = TownView(self.bot, interaction, location_id)
            await view.initial_setup()

        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            embed.set_footer(text=status_bar)

        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        if view:
            view.message = message

    async def explore(self, interaction: discord.Interaction, location_id: str, view_context=None):
        # This function's internal logic is already quite good.
        # The main change is that the things it calls (like CombatView, check_quest_progress)
        # are now correctly located in the new structure.
        user_id = interaction.user.id
        try:
            await interaction.response.defer()
            db_cog = self.bot.get_cog('Database')
            player_data = await db_cog.get_player(user_id)

            explore_cost = ACTION_COSTS.get("explore", {}).get("energy", 0)
            if player_data['energy'] < explore_cost:
                no_energy_message = get_notification("ACTION_FAIL_NO_ENERGY", cost=explore_cost)
                if view_context:
                    await view_context.update_with_activity_log([no_energy_message])
                return

            resource_cog = self.bot.get_cog('Resources')
            if resource_cog:
                await resource_cog.spend_resources(user_id, "explore")

            # 1. Check for the "Well-Rested" buff
            energy_percentage = player_data.get('energy', 100) / player_data.get('max_energy', 100)
            is_well_rested = energy_percentage >= 0.9  # 90-100% energy

            # 2. Check for zone flavor events
            zone_events = get_zone_events(location_id)
            has_flavor_events = bool(zone_events)

            # 3. Adjust the encounter weights
            pet_chance = 35
            if is_well_rested:
                pet_chance += 5
            # If the zone has flavor events, carve out 20% from item/nothing for them
            if has_flavor_events:
                outcome_keys = ["item", "pet", "flavor_event", "nothing"]
                outcome_weights = [35, pet_chance, 20, 10]
            else:
                outcome_keys = ["item", "pet", "nothing"]
                outcome_weights = [45, pet_chance, 20]

            active_quests = await db_cog.get_active_quests(user_id)
            is_on_tutorial_battle_step = any(
                q['quest_id'] == 'a_guildsmans_first_steps' and q['progress'].get('count', 0) == 3 for q in
                active_quests
            )
            if is_on_tutorial_battle_step:
                outcome = "tutorial_pet"
            else:
                outcome = random.choices(outcome_keys, weights=outcome_weights, k=1)[0]

            activity_log_list = []
            if is_well_rested:
                activity_log_list.append(get_notification("PLAYER_BUFF_WELL_RESTED"))

            if outcome == "flavor_event":
                chosen_event = random.choices(
                    zone_events,
                    weights=[e.get("weight", 5) for e in zone_events],
                    k=1
                )[0]
                await self._handle_flavor_event(interaction, user_id, db_cog, chosen_event, activity_log_list, view_context)
                return

            if outcome == "item" or outcome == "nothing":
                activity_log_text = ""
                if outcome == "item":
                    item_id, qty = get_zone_loot(location_id)
                    await db_cog.add_item_to_inventory(user_id, item_id, qty)
                    activity_log_text = get_notification("EXPLORE_FIND_ITEM", quantity=qty,
                                                         item_name=ITEMS[item_id]['name'])

                    quest_updates = await check_quest_progress(self.bot, user_id, "item_pickup", {"item_id": item_id})
                    if quest_updates:
                        await interaction.followup.send(
                            embed=discord.Embed(description="\n\n".join(quest_updates), color=discord.Color.gold()),
                            ephemeral=True)
                else:
                    activity_log_text = get_notification("EXPLORE_FIND_NOTHING")

                # Find the active TownView and call its new update helper.
                if view_context:
                    await view_context.update_with_activity_log([activity_log_text])
                return

            elif outcome == "tutorial_pet" or outcome == "pet":

                player_roster = await db_cog.get_all_pets(user_id)
                main_pet_id = player_data.get('main_pet_id')

                # Make sure the main pet is always first in the roster for BattleState
                main_pet_idx = next((i for i, p in enumerate(player_roster) if p['pet_id'] == main_pet_id), None)
                if main_pet_idx is None or not player_roster:
                    await interaction.followup.send("You have no pets! Use `/start` to begin your adventure.", ephemeral=True)
                    return
                if main_pet_idx != 0:
                    player_roster.insert(0, player_roster.pop(main_pet_idx))

                active_player_pet = player_roster[0]
                if active_player_pet['current_hp'] <= 0:
                    await interaction.followup.send("Your main pet is unable to battle! Heal it at an inn before exploring.", ephemeral=True)
                    return

                if outcome == "tutorial_pet":
                    chosen_species_name, level = "Pineling", 1
                else:
                    time_of_day = player_data.get('day_of_cycle', 'morning')
                    # Map 4 phases to encounter table keys (day/night)
                    # Encounter tables can add 'morning'/'noon'/etc keys later for unique spawns
                    encounter_key = 'night' if time_of_day == 'night' else 'day'
                    possible_pet_names = (ENCOUNTER_TABLES.get(location_id, {}).get(time_of_day)
                                          or ENCOUNTER_TABLES.get(location_id, {}).get(encounter_key, []))
                    if not possible_pet_names:
                        # (Graceful handling for no pets found)
                        return
                    chosen_species_name = random.choice(possible_pet_names)
                    level = random.randint(3, 5)

                wild_pet_base = PET_DATABASE.get(chosen_species_name)
                if not wild_pet_base:
                    await interaction.followup.send(f"Error: Pet data for {chosen_species_name} not found.",
                                                    ephemeral=True)
                    return

                # Pet generation logic (stats, passive, skills)
                assigned_passive = None
                if wild_pet_base['rarity'] in ["Common", "Uncommon"]:
                    pet_type = wild_pet_base['pet_type']
                    if isinstance(pet_type, list): pet_type = random.choice(pet_type)
                    possible_passives = SHARED_PASSIVES_BY_TYPE.get(pet_type, [])
                    if possible_passives: assigned_passive = random.choice(possible_passives)
                else:
                    assigned_passive = wild_pet_base.get('passive_ability')
                base_stats = {stat: random.randint(val[0], val[1]) for stat, val in
                              wild_pet_base["base_stat_ranges"].items()}
                growth_rates = wild_pet_base["growth_rates"]
                calculated_stats = {stat: math.floor(base_stats[stat] + (level - 1) * growth_rates[stat]) for stat in
                                    base_stats}
                skill_learn_data = wild_pet_base.get('skill_tree', {})
                all_learnable_skills = []
                for lvl, skills in skill_learn_data.items():
                    if level >= int(lvl):
                        if isinstance(skills, list):
                            all_learnable_skills.extend(skills)
                        elif isinstance(skills, dict) and "choice" in skills:
                            all_learnable_skills.append(random.choice(skills['choice']))
                active_skills = all_learnable_skills[-4:] if all_learnable_skills else ["pound"]
                wild_pet_instance = {
                    "species": wild_pet_base['species'], "rarity": wild_pet_base['rarity'],
                    "pet_type": wild_pet_base['pet_type'], "level": level,
                    "personality": wild_pet_base.get('personality', 'Aggressive'),
                    "current_hp": calculated_stats['hp'], "max_hp": calculated_stats['hp'],
                    "attack": calculated_stats['attack'], "defense": calculated_stats['defense'],
                    "special_attack": calculated_stats['special_attack'],
                    "special_defense": calculated_stats['special_defense'],
                    "speed": calculated_stats['speed'], "skills": active_skills,
                    "passive_ability": assigned_passive,
                    "base_hp": base_stats['hp'],
                    "base_attack": base_stats['attack'],
                    "base_defense": base_stats['defense'],
                    "base_special_attack": base_stats['special_attack'],
                    "base_special_defense": base_stats['special_defense'],
                    "base_speed": base_stats['speed']
                }

                wild_pet_instance['is_gloom_touched'] = wild_pet_base.get('is_gloom_touched', False)


                resource_cog = self.bot.get_cog('Resources')
                if resource_cog:
                    await resource_cog.spend_resources(user_id, "battle")

                spectator_embed = discord.Embed(title="⚔️ A battle is starting...", description="Loading...",
                                                color=discord.Color.dark_grey())
                spectator_message = await interaction.channel.send(embed=spectator_embed)

                # Create the CombatView, passing it all the necessary information
                combat_view = CombatView(
                    bot=self.bot,
                    user_id=user_id,
                    player_roster=player_roster, # Pass the full roster
                    wild_pet=wild_pet_instance,
                    spectator_message=spectator_message,
                    parent_interaction=interaction,
                    origin_location_id=location_id,
                    view_context=view_context,
                    initial_log_message=f"A wild Level {wild_pet_instance['level']} **{wild_pet_instance['species']}** appeared!"
                )

                control_message = await interaction.followup.send("⚔️ **It's your turn!**", view=combat_view,
                                                                  ephemeral=True)

                combat_view.message = control_message  # The view now controls this private message
                await combat_view.initial_setup()

        except Exception as e:
            print(f"--- [FATAL ERROR] An exception occurred in explore: {e} ---")
            traceback.print_exc()
            try:
                await interaction.followup.send(
                    f"⚠️ An error occurred while exploring: `{type(e).__name__}: {e}`\nPlease try again.",
                    ephemeral=True
                )
            except Exception:
                pass


    async def _handle_flavor_event(self, interaction, user_id, db_cog, event, prefix_logs, view_context):
        """
        Handles a flavor event dict from explore_events.py.
        Applies outcomes and updates the view with the event text.
        Choice events send a followup with buttons.
        """
        event_type = event.get("type", "flavor")
        text = event.get("text", "")
        outcome = event.get("outcome", {})

        log_list = list(prefix_logs)

        # Apply outcome to flavor/loot/hazard/pet_sighting events immediately
        if event_type != "choice":
            log_list.append(text)
            await self._apply_event_outcome(user_id, db_cog, outcome, log_list)
            if view_context:
                await view_context.update_with_activity_log(log_list)
            return

        # --- Choice event: show buttons ---
        choices = event.get("choices", [])
        if not choices:
            log_list.append(text)
            if view_context:
                await view_context.update_with_activity_log(log_list)
            return

        embed = discord.Embed(
            description=f"*{text}*",
            color=discord.Color.dark_teal()
        )
        embed.set_footer(text="What do you do?")

        choice_view = ExploreChoiceView(
            bot=self.bot,
            user_id=user_id,
            db_cog=db_cog,
            choices=choices,
            prefix_logs=prefix_logs,
            view_context=view_context,
        )
        msg = await interaction.followup.send(embed=embed, view=choice_view, ephemeral=True)
        choice_view.message = msg

    async def _apply_event_outcome(self, user_id, db_cog, outcome, log_list):
        """Applies an event outcome dict to the player/pet. Appends results to log_list."""
        if not outcome:
            return

        player_data = await db_cog.get_player(user_id)

        # Energy change
        if "energy" in outcome:
            delta = outcome["energy"]
            current = player_data.get("energy", 0)
            max_e = player_data.get("max_energy", 10)
            new_energy = max(0, min(max_e, current + delta))
            await db_cog.update_player(user_id, energy=new_energy)
            if delta > 0:
                log_list.append(f"*(+{delta} Energy)*")
            elif delta < 0:
                log_list.append(f"*({delta} Energy)*")

        # HP change (as % of max HP)
        if "hp" in outcome:
            pct = outcome["hp"]  # e.g. -8 means lose 8% of max HP
            if player_data.get("main_pet_id"):
                pet_data = await db_cog.get_pet(player_data["main_pet_id"])
                if pet_data:
                    delta_hp = max(1, int(pet_data["max_hp"] * abs(pct) / 100))
                    if pct < 0:
                        new_hp = max(1, pet_data["current_hp"] - delta_hp)
                        await db_cog.update_pet(pet_data["pet_id"], current_hp=new_hp)
                        log_list.append(f"*({pct}% HP — {pet_data['name']} takes a hit)*")
                    else:
                        new_hp = min(pet_data["max_hp"], pet_data["current_hp"] + delta_hp)
                        await db_cog.update_pet(pet_data["pet_id"], current_hp=new_hp)
                        log_list.append(f"*(+{pct}% HP restored to {pet_data['name']})*")

        # Item grant or cost
        if "item" in outcome:
            item_cfg = outcome["item"]
            item_id = item_cfg.get("item_id")
            qty = item_cfg.get("qty", 1)
            if item_id and qty != 0:
                item_name = ITEMS.get(item_id, {}).get("name", item_id)
                if qty > 0:
                    await db_cog.add_item_to_inventory(user_id, item_id, qty)
                    log_list.append(f"*(+{qty}× {item_name})*")
                else:
                    # Negative qty = cost; silently skip if player doesn't have it
                    await db_cog.remove_item_from_inventory(user_id, item_id, abs(qty))
                    log_list.append(f"*(-{abs(qty)}× {item_name})*")


class ExploreChoiceView(discord.ui.View):
    """Temporary view for choice-based explore events."""

    def __init__(self, bot, user_id, db_cog, choices, prefix_logs, view_context):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.db_cog = db_cog
        self.choices = choices
        self.prefix_logs = prefix_logs
        self.view_context = view_context
        self.message = None

        for i, choice in enumerate(choices):
            label = choice.get("label", f"Option {i+1}")
            emoji = choice.get("emoji")
            btn = discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.secondary,
                custom_id=str(i)
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, index: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("This isn't your event.", ephemeral=True)
            await interaction.response.defer()
            self.stop()
            if self.message:
                try:
                    await self.message.delete()
                except Exception:
                    pass

            choice = self.choices[index]
            outcome = choice.get("outcome", {})
            result_text = choice.get("text", "")

            log_list = list(self.prefix_logs)
            log_list.append(result_text)

            adventure_cog = self.bot.get_cog('Adventure')
            if adventure_cog:
                await adventure_cog._apply_event_outcome(self.user_id, self.db_cog, outcome, log_list)

            if self.view_context:
                await self.view_context.update_with_activity_log(log_list)
        return callback

    async def on_timeout(self):
        # If player doesn't choose, quietly dismiss
        if self.message:
            try:
                await self.message.delete()
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(Adventure(bot))