# --- cogs/utils/views_modals.py ---
# This file contains all the Discord UI modal classes for the game.

import discord

# --- REFACTORING FIX ---
# Removed ITEM_DATA and ITEM_CATEGORIES from this import as they are no longer used in this file.
from cogs.utils.constants import PET_DESCRIPTIONS, CREST_DATA, \
    UNEARNED_CREST_EMOJI, RANK_DISPLAY_DATA
from cogs.utils.helpers import get_pet_image_url, _pet_tuple_to_dict, _create_progress_bar, get_player_rank_info, \
    get_status_bar
from data.pets import ENCOUNTER_TABLES # Import from the new data/pets.py file


# --- Modals ---
class RenamePetModal(discord.ui.Modal, title="Rename Your Pet"):
    """
    A modal for renaming a pet.
    """

    def __init__(self, bot, pet_id, old_name, parent_view):
        super().__init__()
        self.bot = bot
        self.pet_id = pet_id
        self.old_name = old_name
        self.parent_view = parent_view
        self.new_name_input = discord.ui.TextInput(
            label="New Pet Name",
            placeholder=f"Enter a new name for {self.old_name}...",
            max_length=20,
            required=True
        )
        self.add_item(self.new_name_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            print("LOG: Database cog not found in RenamePetModal.on_submit")
            return await interaction.followup.send("Database not loaded. Please contact an administrator.")
        new_name = self.new_name_input.value
        try:
            print(f"LOG: Attempting to rename pet ID {self.pet_id} to {new_name}")
            await db_cog.update_pet(self.pet_id, name=new_name)
            await interaction.followup.send(f"You have renamed **{self.old_name}** to **{new_name}**!", ephemeral=True)
            print("LOG: Renaming successful. Updating parent view.")
            self.parent_view.main_pet = await db_cog.get_pet(self.pet_id)
            new_embed = await self.parent_view.get_pet_status_embed(self.parent_view.main_pet)
            try:
                await self.parent_view.message.edit(embed=new_embed, view=self.parent_view)
            except discord.errors.NotFound:
                pass  # Message was likely deleted
        except Exception as e:
            print(f"ERROR: An error occurred in RenamePetModal.on_submit: {e}")
            await interaction.followup.send(f"An error occurred while renaming your pet: {e}", ephemeral=True)
