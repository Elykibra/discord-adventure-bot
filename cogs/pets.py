# cogs/pets.py
import discord
from discord import app_commands
from discord.ext import commands
# We can reuse the view from the character cog's view file
from .views.character import PetView, SetMainPetView


class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pets", description="Manage and view your companions.")
    async def pets(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_data = await db_cog.get_player(interaction.user.id)
        if not player_data or not player_data.get('main_pet_id'):
            return await interaction.followup.send("You don't have any pets yet!", ephemeral=True)

        main_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
        all_pets_data = await db_cog.get_all_pets(interaction.user.id)

        view = PetView(self.bot, interaction.user.id, main_pet_data, all_pets_data)
        embed = await view.get_pet_status_embed()

        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = message


async def setup(bot):
    await bot.add_cog(Pets(bot))