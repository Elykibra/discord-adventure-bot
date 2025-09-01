# --- cogs/gameplay/adventure_core.py (Definitive Final Version) ---
import discord, traceback, random, math
from discord import app_commands
from discord.ext import commands
from data.towns import towns
from data.pets import PET_DATABASE, ENCOUNTER_TABLES
from cogs.utils.helpers import get_status_bar, get_town_embed, _pet_tuple_to_dict, check_quest_progress
from cogs.utils.views_towns import TownView, WildsView
from cogs.utils.views_combat import CombatView
from data.items import ITEMS
from data.abilities import SHARED_PASSIVES_BY_TYPE


class Adventure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.exploring_users = set()

    @app_commands.command(name='adventure', description='Opens the menu for your current location.')
    async def adventure_menu(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        if not player_data:
            return await interaction.followup.send("You have not started your adventure! Use `/start` to begin.", ephemeral=True)

        location_id = player_data.get('current_location', 'oakhavenOutpost')
        location_data = towns.get(location_id, {})
        view = None
        embed = None

        if location_data.get('is_wilds', False):
            view = WildsView(self.bot, interaction, location_id)
            embed = view.embed
        else:
            embed = await get_town_embed(self.bot, interaction.user.id, location_id)
            view = TownView(self.bot, interaction, location_id)

        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            embed.set_footer(text=status_bar)

        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        if view:
            view.message = message

    async def explore(self, interaction: discord.Interaction, location_id: str, view_context=None):
        user_id = interaction.user.id
        print("\n--- [DEBUG] Main explore function initiated ---")
        try:
            await interaction.response.defer()
            db_cog = self.bot.get_cog('Database')
            player_data = await db_cog.get_player(user_id)
            energy_cost = 10
            if player_data['current_energy'] < energy_cost:
                await interaction.followup.send("You don't have enough energy to explore.", ephemeral=True)
                return
            await db_cog.update_player(user_id, current_energy=player_data['current_energy'] - energy_cost)
            active_quests = await db_cog.get_active_quests(user_id)
            is_on_tutorial_battle_step = any(
                q['quest_id'] == 'a_guildsmans_first_steps' and q['progress'].get('count', 0) == 3 for q in
                active_quests
            )
            if is_on_tutorial_battle_step:
                outcome = "tutorial_pet"
            else:
                outcome = random.choices(["item", "pet", "nothing"], weights=[45, 35, 20], k=1)[0]

            if outcome == "item" or outcome == "nothing":
                activity_log_text = ""
                if outcome == "item":
                    item_id = "sun_kissed_berries"
                    await db_cog.add_item_to_inventory(user_id, item_id, 1)
                    activity_log_text = f"🌲 You searched the area and found **1x {ITEMS[item_id]['name']}**!"
                    quest_updates = await check_quest_progress(self.bot, user_id, "item_pickup", {"item_id": item_id})
                    if quest_updates:
                        await interaction.followup.send(
                            embed=discord.Embed(description="\n\n".join(quest_updates), color=discord.Color.gold()),
                            ephemeral=True)
                else:
                    activity_log_text = f"💨 You searched the area but found nothing of interest."

                # Find the active TownView and call its new update helper.
                if view_context:
                    await view_context.update_with_activity_log(activity_log_text)
                return

            elif outcome == "tutorial_pet" or outcome == "pet":
                player_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
                if not player_pet_data or player_pet_data['current_hp'] <= 0:
                    await interaction.followup.send("Your main pet is unable to battle! Heal it before exploring.",
                                                    ephemeral=True)
                    return

                if outcome == "tutorial_pet":
                    chosen_species_name, level = "Pineling", 1
                else:
                    time_of_day = player_data.get('day_of_cycle', 'day')
                    possible_pet_names = ENCOUNTER_TABLES.get(location_id, {}).get(time_of_day, [])
                    if not possible_pet_names:
                        # (Graceful handling for no pets found)
                        return
                    chosen_species_name = random.choice(possible_pet_names)
                    level = random.randint(3, 5)

                wild_pet_base = PET_DATABASE.get(chosen_species_name)
                if not wild_pet_base:
                    await interaction.followup.send(f"Error: Pet data for {chosen_species_name} not found.", ephemeral=True)
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
                wild_pet_instance = {"species": wild_pet_base['species'], "rarity": wild_pet_base['rarity'],
                                     "pet_type": wild_pet_base['pet_type'], "level": level,
                                     "current_hp": calculated_stats['hp'], "max_hp": calculated_stats['hp'],
                                     "attack": calculated_stats['attack'], "defense": calculated_stats['defense'],
                                     "special_attack": calculated_stats['special_attack'],
                                     "special_defense": calculated_stats['special_defense'],
                                     "speed": calculated_stats['speed'], "skills": active_skills,
                                     "passive_ability": assigned_passive}

                # Ensure the Gloom-Touched status is carried over into the battle instance.
                wild_pet_instance['is_gloom_touched'] = wild_pet_base.get('is_gloom_touched', False)

                combat_message = await interaction.channel.send(
                    f"A wild pet appears before {interaction.user.mention}...",
                    silent=True
                )

                if view_context is None:
                    # This is a simplified way to find the active view.
                    # A more robust system might use a dictionary mapping user_id to active views.
                    for view in self.bot.persistent_views:
                        if isinstance(view, WildsView) and view.user_id == user_id:
                            view_context = view
                            break

                # 2. Create the CombatView, passing the new message to it.
                combat_view = CombatView(self.bot, user_id, player_pet_data, wild_pet_instance, combat_message,
                                         interaction, location_id, view_context)
        except Exception as e:
            print(f"--- [FATAL ERROR] An exception occurred in explore: {e} ---")
            traceback.print_exc()

        finally:
            if user_id in self.exploring_users:
                self.exploring_users.remove(user_id)

async def setup(bot):
    await bot.add_cog(Adventure(bot))