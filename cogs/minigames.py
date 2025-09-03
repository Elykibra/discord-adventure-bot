# cogs/minigames.py

import discord
from discord import app_commands
from discord.ext import commands


class Minigames(commands.Cog):
    """A cog for fun mini-games a player can engage in."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fish", description="Go fishing and see what you can catch!")
    async def fish(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎣 The fishing mini-game is coming soon!", ephemeral=True)

    # You can add other minigame commands here in the future.


async def setup(bot):
    await bot.add_cog(Minigames(bot))