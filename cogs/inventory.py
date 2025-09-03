# cogs/inventory.py
import discord
from discord import app_commands
from discord.ext import commands
from .views.inventory import BagView


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Opens your item bag.")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_data = await db_cog.get_player(interaction.user.id)
        if not player_data:
            return await interaction.followup.send("You don't have a character. Use `/start` to create one.",
                                                   ephemeral=True)

        inventory_data = await db_cog.get_player_inventory(interaction.user.id)

        view = BagView(self.bot, interaction.user.id, player_data, inventory_data)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Inventory(bot))