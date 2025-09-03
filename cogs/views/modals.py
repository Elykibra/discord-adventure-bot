# cogs/views/modals.py
# This file contains all the Discord UI modal classes for the game.

import discord

# --- REFACTORED IMPORTS ---
# The helpers and other data this file might need should be imported
# from their new top-level locations.
from utils.helpers import get_status_bar


class RenamePetModal(discord.ui.Modal, title="Rename Your Pet"):
    """
    A modal for renaming a pet.
    The logic inside this class was already solid and needs no changes.
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
            return await interaction.followup.send("Database not loaded. Please contact an administrator.")

        new_name = self.new_name_input.value
        try:
            await db_cog.update_pet(self.pet_id, name=new_name)
            await interaction.followup.send(f"You have renamed **{self.old_name}** to **{new_name}**!", ephemeral=True)

            # Refresh the parent view with the new pet name
            self.parent_view.main_pet_data = await db_cog.get_pet(self.pet_id)
            # Recreate the main_pet object with new data in the parent view
            self.parent_view.main_pet.__init__(self.parent_view.main_pet_data)
            new_embed = await self.parent_view.get_pet_status_embed()
            await self.parent_view.message.edit(embed=new_embed, view=self.parent_view)
        except Exception as e:
            print(f"ERROR: An error occurred in RenamePetModal.on_submit: {e}")
            await interaction.followup.send(f"An error occurred while renaming your pet: {e}", ephemeral=True)