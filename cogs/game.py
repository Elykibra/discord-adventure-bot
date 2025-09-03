# cogs/game.py
# Handles the /start command for new players.

import discord
from discord import app_commands
from discord.ext import commands
import random
import traceback

# --- REFACTORED IMPORTS ---
from utils.constants import PET_DESCRIPTIONS
from data.pets import PET_DATABASE
from utils.helpers import get_pet_image_url, get_status_bar
from data.abilities import STARTER_TALENTS

# A helper list to get only the starter pets from the database
STARTER_PETS_LIST = [pet for pet in PET_DATABASE.values() if pet.get('rarity') == 'Starter']


# --- StartModal Class ---
# The logic inside this class is already good. No changes needed.
# A modal to collect the user's desired username.
class StartModal(discord.ui.Modal, title="Guild Registration"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.username_input = discord.ui.TextInput(
            label="Choose an in-game username",
            placeholder="Enter your username (max 20 characters)...",
            max_length=20,
            required=True
        )
        self.add_item(self.username_input)

# --- GenderSelectView Class ---
# The logic inside this class is already good. No changes needed.
class GenderSelectView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.gender = None
        self.message = None

# --- StarterPetView Class ---
# The logic inside this class is already good. No changes needed.
class StarterPetView(discord.ui.View):
    def __init__(self, bot, user_id, username, gender):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.gender = gender
        self.message = None
        self.selected_pet_data = None

        # --- REFACTOR FIX ---
        # Use the new STARTER_PETS_LIST we created at the top of the file
        options = [discord.SelectOption(label=pet['species'], value=pet['species']) for pet in STARTER_PETS_LIST]
        self.pet_select = discord.ui.Select(placeholder="Choose your starter pet...", options=options)
        self.pet_select.callback = self.pet_select_callback
        self.add_item(self.pet_select)

        self.confirm_button = discord.ui.Button(label="Confirm Choice", style=discord.ButtonStyle.green, disabled=True)
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)

# --- TalentChoiceView Class ---
# The logic inside this class is already good. No changes needed.
class TalentChoiceView(discord.ui.View):
    def __init__(self, bot, user_id, pet_id, pet_species, final_embed):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.pet_id = pet_id
        self.pet_species = pet_species
        self.final_embed = final_embed

        # --- THIS IS THE NEW UI LOGIC ---
        # Get the list of talents for the chosen starter pet
        talents = STARTER_TALENTS.get(self.pet_species, [])

        # Create a list of SelectOptions for the dropdown
        options = [
            discord.SelectOption(
                label=talent['name'],
                # Use the mechanic description to explain what the talent does
                description=talent['mechanic_desc'][:100],  # Descriptions are limited to 100 characters
                value=talent['mechanic_name']  # Store the mechanic name in the value
            ) for talent in talents
        ]

        # Create the dropdown (Select) component
        talent_select = discord.ui.Select(
            placeholder="Choose your pet's Innate Talent...",
            options=options
        )
        talent_select.callback = self.talent_select_callback
        self.add_item(talent_select)

# --- The Main Cog ---
class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='start', description='Begin your journey as a Guild Adventurer!')
    async def start_adventure(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.response.send_message(
                "Database is not loaded. Please contact an administrator.",
                ephemeral=True
            )
        player_data = await db_cog.get_player(interaction.user.id)
        if player_data and player_data.get('main_pet_id'):
            return await interaction.response.send_message(
                    "You have already started your adventure! Use `/adventure` to open your menu.",
                    ephemeral=True
            )
        if player_data:
            username = player_data.get('username')
            gender = player_data.get('gender')
            pet_selection_view = StarterPetView(self.bot, interaction.user.id, username, gender)
            await interaction.response.send_message(
                    "It seems you have not chosen a starter pet yet. Please select your first companion.",
                    view=pet_selection_view,
                    ephemeral=True
                )
            pet_selection_view.message = await interaction.original_response()
            return
        modal = StartModal(self.bot)
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Game(bot))