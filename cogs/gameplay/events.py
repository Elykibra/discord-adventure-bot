# cogs/gameplay/events.py
# This cog is designed for global or special events that occur periodically.

import discord
from discord.ext import commands
import random


class Events(commands.Cog):
    """
    A cog for managing global game events.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="event_info", help="Get information about the current global event.")
    async def event_info(self, ctx):
        """
        Displays information about the active global event.
        """
        # This is a placeholder for a future feature.
        # You would implement logic here to check if an event is active
        # and then display a custom embed with details about it.
        event_active = False  # Placeholder
        if event_active:
            embed = discord.Embed(
                title="Global Event: The Gloom Approaches",
                description="A strange fog is slowly creeping over the land, making wild pets more aggressive but also more valuable.",
                color=discord.Color.dark_purple()
            )
            embed.add_field(name="Effect",
                            value="Wild pets have 10% more attack, but a 20% higher chance to drop rare loot.")
            await ctx.send(embed=embed)
        else:
            await ctx.send("There is no active global event at the moment.")


async def setup(bot):
    await bot.add_cog(Events(bot))