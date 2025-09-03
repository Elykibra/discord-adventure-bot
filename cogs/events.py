# cogs/events.py

import discord
from discord import app_commands
from discord.ext import commands

class Events(commands.Cog):
    """A cog for managing global game events."""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="event", description="Get information about the current global event.")
    async def event_info(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎉 There are no active global events right now. Check back later!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Events(bot))