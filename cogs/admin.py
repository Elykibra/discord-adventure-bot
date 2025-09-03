# cogs/admin.py

import discord
from discord import app_commands
from discord.ext import commands
import math
import random

# --- REFACTORED IMPORTS ---
# The data imports are already correct. We just need to fix the view import.
from data.items import ITEMS
from data.towns import towns
from data.pets import PET_DATABASE
from data.skills import PET_SKILLS
from data.quests import QUESTS
from .views.combat import CombatView # <-- Path updated for new structure


class ResetView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.message = None

    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')

        # This will perform a full reset of the player's data
        await db_cog.delete_player_data(self.user_id)

        for item in self.children:
            item.disabled = True

        await interaction.edit_original_response(
            content="Your character has been successfully reset. You can now use `/start` to begin a new adventure.",
            view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(content="Reset cancelled.", view=self)
        self.stop()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='heal', description='(Admin Only) Heals your main pet to full HP.')
    @commands.is_owner()
    async def heal(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        main_pet_id = player_data.get('main_pet_id')
        if not main_pet_id:
            return await interaction.followup.send("You do not have a main pet to heal.", ephemeral=True)
        main_pet = await db_cog.get_pet(main_pet_id)
        await db_cog.update_pet(main_pet_id, current_hp=main_pet['max_hp'])
        await interaction.followup.send(f"Your pet, **{main_pet['name']}**, has been fully healed!", ephemeral=True)

    @app_commands.command(name='energy', description='(Admin Only) Restores your energy to full.')
    @commands.is_owner()
    async def energy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        await db_cog.update_player(interaction.user.id, current_energy=player_data['max_energy'])
        await interaction.followup.send(f"Your energy has been fully restored!", ephemeral=True)

    @app_commands.command(name='learnskill', description='(Admin Only) Teaches your main pet a skill.')
    @commands.is_owner()
    async def learn_skill(self, interaction: discord.Interaction, skill_id: str):
        await interaction.response.defer(ephemeral=True)
        if skill_id not in PET_SKILLS:
            return await interaction.followup.send(f"Error: Skill ID '{skill_id}' not found.", ephemeral=True)

        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        main_pet_id = player_data.get('main_pet_id')
        if not main_pet_id:
            return await interaction.followup.send("You do not have a main pet.", ephemeral=True)

        main_pet = await db_cog.get_pet(main_pet_id)
        pet_skills = main_pet.get('skills', [])

        if skill_id in pet_skills:
            return await interaction.followup.send(f"Your pet already knows {PET_SKILLS[skill_id]['name']}.",
                                                   ephemeral=True)

        pet_skills.append(skill_id)
        await db_cog.update_pet(main_pet_id, skills=pet_skills)
        await interaction.followup.send(
            f"Your pet, **{main_pet['name']}**, has learned **{PET_SKILLS[skill_id]['name']}**!", ephemeral=True)

    @app_commands.command(name='encounter', description='(Admin Only) Starts a battle with a specific pet.')
    @commands.is_owner()
    async def encounter(self, interaction: discord.Interaction, species: str, level: int = 5):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        # --- THIS IS THE FIXED LOGIC ---
        # Find the pet data from the new PET_DATABASE
        pet_base_data = PET_DATABASE.get(species)

        if not pet_base_data:
            return await interaction.followup.send(f"Error: Pet species '{species}' not found in PET_DATABASE.", ephemeral=True)

        # Generate stats for the wild pet
        base_stats = {stat: random.randint(val[0], val[1]) for stat, val in pet_base_data["base_stat_ranges"].items()}
        growth_rates = pet_base_data["growth_rates"]
        calculated_stats = {stat: math.floor(base_stats[stat] + (level - 1) * growth_rates[stat]) for stat in
                            base_stats}

        wild_pet = {
            "species": pet_base_data['species'], "rarity": pet_base_data['rarity'],
            "pet_type": pet_base_data['pet_type'],
            "level": level, "current_hp": calculated_stats['hp'], "max_hp": calculated_stats['hp'],
            "attack": calculated_stats['attack'], "defense": calculated_stats['defense'],
            "special_attack": calculated_stats['special_attack'],
            "special_defense": calculated_stats['special_defense'],
            "speed": calculated_stats['speed'], "personality": pet_base_data.get('personality', 'Aggressive'),
            "skills": pet_base_data.get('skills', ['scratch'])
        }

        player_pet = await db_cog.get_pet((await db_cog.get_player(interaction.user.id)).get('main_pet_id'))

        combat_view = CombatView(self.bot, interaction.user.id, player_pet, wild_pet, None)
        initial_embed = await combat_view.get_battle_embed(
            f"A wild level {level} {wild_pet['species']} appears for testing!")
        message = await interaction.followup.send(embed=initial_embed, view=combat_view, ephemeral=True)
        combat_view.message = message

    @app_commands.command(name='additem', description='(Admin Only) Adds an item to your inventory.')
    @commands.is_owner()
    async def add_item(self, interaction: discord.Interaction, item_id: str, quantity: int = 1):
        """Adds a specified quantity of an item to the player's inventory."""
        await interaction.response.defer(ephemeral=True)
        if item_id not in ITEMS:
            return await interaction.followup.send(f"Error: Item ID '{item_id}' not found.", ephemeral=True)

        db_cog = self.bot.get_cog('Database')
        await db_cog.add_item_to_inventory(interaction.user.id, item_id, quantity)
        await interaction.followup.send(f"Successfully added {quantity}x {ITEMS[item_id]['name']} to your inventory.",
                                        ephemeral=True)

    @app_commands.command(name='addcoins', description='(Admin Only) Adds coins to your balance.')
    @commands.is_owner()
    async def add_coins(self, interaction: discord.Interaction, amount: int):
        """Adds a specified amount of coins to the player's balance."""
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        await db_cog.add_coins(interaction.user.id, amount)
        player_data = await db_cog.get_player(interaction.user.id)
        await interaction.followup.send(
            f"Successfully added {amount} coins. Your new balance is {player_data['coins']}.", ephemeral=True)

    @app_commands.command(name='setlevel', description='(Admin Only) Sets your main pet to a specific level.')
    @commands.is_owner()
    async def set_level(self, interaction: discord.Interaction, level: int):
        """Sets the player's main pet to a specific level and recalculates its stats."""
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(interaction.user.id)
        main_pet_id = player_data.get('main_pet_id')

        if not main_pet_id:
            return await interaction.followup.send("You do not have a main pet.", ephemeral=True)

        # We can reuse the add_xp function's logic. We'll set the level directly
        # and then call add_xp with 0 to trigger the stat recalculation.
        await db_cog.update_pet(main_pet_id, level=level - 1, xp=0)
        updated_pet, _ = await db_cog.add_xp(main_pet_id, 0)  # Triggers level up to the target level and stat recalc

        await interaction.followup.send(
            f"Your pet, **{updated_pet['name']}**, is now Level {updated_pet['level']}. Its stats have been updated.",
            ephemeral=True)

    @app_commands.command(name='teleport', description='(Admin Only) Teleports you to any town.')
    @commands.is_owner()
    async def teleport(self, interaction: discord.Interaction, town_id: str):
        """Instantly changes the player's current location."""
        await interaction.response.defer(ephemeral=True)
        if town_id not in towns:
            return await interaction.followup.send(f"Error: Town ID '{town_id}' not found.", ephemeral=True)

        db_cog = self.bot.get_cog('Database')
        await db_cog.update_player(interaction.user.id, current_location=town_id)
        await interaction.followup.send(f"You have teleported to **{towns[town_id]['name']}**.", ephemeral=True)

    # You would expand this with subcommands for start, complete, reset, etc.
    @app_commands.command(name='quest', description='(Admin Only) Manipulate a quest.')
    @commands.is_owner()
    async def quest(self, interaction: discord.Interaction, action: str, quest_id: str):
        """Starts or completes a quest for the player."""
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        if action.lower() == 'start':
            await db_cog.add_quest(interaction.user.id, quest_id)
            await interaction.followup.send(f"Quest '{quest_id}' started.", ephemeral=True)
        elif action.lower() == 'complete':
            await db_cog.complete_quest(interaction.user.id, quest_id)
            await interaction.followup.send(f"Quest '{quest_id}' completed.", ephemeral=True)
        else:
            await interaction.followup.send("Invalid action. Use 'start' or 'complete'.", ephemeral=True)

    @add_item.error
    @add_coins.error
    @set_level.error
    @teleport.error
    @quest.error
    async def admin_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.NotOwner):
            await interaction.response.send_message("This is an admin-only command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred.", ephemeral=True)
            print(f"Admin command error: {error}")

    @app_commands.command(name='reset', description='(Admin Only) Resets your character to start over.')
    @commands.is_owner()
    async def reset(self, interaction: discord.Interaction):
        """Resets the player's character, pets, inventory, and quests."""

        view = ResetView(self.bot, interaction.user.id)

        embed = discord.Embed(
            title="⚠️ Character Reset Confirmation ⚠️",
            description="Are you sure you want to completely reset your character? This will delete your player, all your pets, your inventory, and your quest progress. **This action cannot be undone.**",
            color=discord.Color.red()
        )

        message = await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(Admin(bot))