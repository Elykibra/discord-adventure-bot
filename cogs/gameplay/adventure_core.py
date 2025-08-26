# --- cogs/gameplay/adventure_core.py (Definitive Final Version) ---
import discord, traceback, random, math
from discord import app_commands
from discord.ext import commands
from data.towns import towns
from data.pets import PET_DATABASE, ENCOUNTER_TABLES
from cogs.utils.helpers import get_status_bar, get_town_embed, _pet_tuple_to_dict, check_quest_progress
from cogs.utils.views_towns import TownView, WildsView  # All views now come from one place
from cogs.utils.views_combat import CombatView
from data.items import ITEMS

class Adventure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='adventure', description='Opens the menu for your current location.')
    async def adventure_menu(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        location_id = player_data.get('current_location', 'oakhavenOutpost')
        location_data = towns.get(location_id, {})

        view = None # Define view as None initially

        if location_data.get('is_wilds', False):
            embed = discord.Embed(title=f"Location: {location_data.get('name')}",
                                  description=location_data.get('description'), color=discord.Color.dark_green())
            view = WildsView(self.bot, interaction, location_id)
        else:
            embed = await get_town_embed(self.bot, interaction.user.id, location_id)
            view = TownView(self.bot, interaction, location_id)

        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            embed.set_footer(text=status_bar)

        # Send the message and then immediately store it in the view.
        # This is the most reliable way to get the message object.
        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        if view:
            view.message = message

    async def explore(self, interaction: discord.Interaction, location_id: str):
        """Handles the logic for what happens when a player explores a wilds area."""
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)

        energy_cost = 10
        if player_data['current_energy'] < energy_cost:
            return await interaction.followup.send("You don't have enough energy to explore.", ephemeral=True)

        await db_cog.update_player(interaction.user.id, current_energy=player_data['current_energy'] - energy_cost)

        outcome = random.choices(["item", "pet", "nothing"], weights=[45, 35, 20], k=1)[0]

        if outcome == "item":
            item_id = "sun_kissed_berries"
            quantity = 1
            item_data = ITEMS.get(item_id)
            await db_cog.add_item_to_inventory(interaction.user.id, item_id, quantity)
            await interaction.followup.send(f"🌲 You searched the area and found **{quantity}x {item_data['name']}**!",
                                            ephemeral=True)

            # --- THE FIX: Capture and send quest updates ---
            quest_updates = await check_quest_progress(self.bot, interaction.user.id, "item_pickup", {"item_id": item_id})
            if quest_updates:
                # Combine all quest update messages into one embed
                full_description = "\n\n".join(quest_updates)
                quest_embed = discord.Embed(
                    description=full_description,
                    color=discord.Color.gold()
                )
                # Send the quest update as a separate followup message
                await interaction.followup.send(embed=quest_embed, ephemeral=True)
            # --- END OF FIX ---

            await check_quest_progress(self.bot, interaction.user.id, "item_pickup", {"item_id": item_id})

        elif outcome == "pet":
            player_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
            if not player_pet_data or player_pet_data['current_hp'] <= 0:
                return await interaction.followup.send("Your main pet is unable to battle! Heal it before exploring.",
                                                       ephemeral=True)

            # --- REFACTOR: Use the new Encounter Tables and Pet Database ---
            time_of_day = player_data.get('day_of_cycle', 'day')

            # 1. Get a list of possible pet NAMES from the encounter table
            possible_pet_names = ENCOUNTER_TABLES.get(location_id, {}).get(time_of_day, [])
            if not possible_pet_names:
                return await interaction.followup.send("You searched the area but didn't encounter any wild pets.",
                                                       ephemeral=True)

            chosen_species_name = random.choice(possible_pet_names)

            # 2. Look up the full pet data from the master PET_DATABASE
            wild_pet_base = PET_DATABASE.get(chosen_species_name)
            if not wild_pet_base:
                return await interaction.followup.send(f"Error: Pet data for {chosen_species_name} not found.",
                                                       ephemeral=True)

            level = random.randint(3, 5)
            base_stats = {stat: random.randint(val[0], val[1]) for stat, val in
                          wild_pet_base["base_stat_ranges"].items()}
            growth_rates = wild_pet_base["growth_rates"]
            calculated_stats = {stat: math.floor(base_stats[stat] + (level - 1) * growth_rates[stat]) for stat in
                                base_stats}

            all_learnable_skills = []
            skill_learn_data = wild_pet_base.get('skill_tree', {})
            for lvl_req_str, skills in skill_learn_data.items():
                if level >= int(lvl_req_str):
                    if isinstance(skills, list):
                        all_learnable_skills.extend(skills)
                    elif isinstance(skills, dict) and "choice" in skills:
                        all_learnable_skills.append(random.choice(skills["choice"]))

            active_skills = all_learnable_skills[-4:]
            if not active_skills:
                active_skills.append("scratch")

            wild_pet_instance = {
                "species": wild_pet_base['species'], "rarity": wild_pet_base['rarity'],
                "pet_type": wild_pet_base['pet_type'],
                "level": level, "current_hp": calculated_stats['hp'], "max_hp": calculated_stats['hp'],
                "attack": calculated_stats['attack'], "defense": calculated_stats['defense'],
                "special_attack": calculated_stats['special_attack'],
                "special_defense": calculated_stats['special_defense'],
                "speed": calculated_stats['speed'],
                "skills": active_skills
            }

            combat_view = CombatView(self.bot, interaction.user.id, player_pet_data, wild_pet_instance, None)
            embed = await combat_view.get_battle_embed(
                f"A wild Level {level} **{wild_pet_instance['species']}** appeared!")

            message = await interaction.followup.send(embed=embed, view=combat_view, ephemeral=True)
            combat_view.message = message

        else:  # outcome == "nothing"
            await interaction.followup.send("You searched the area but found nothing of interest.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Adventure(bot))