# --- cogs/gameplay/quests.py (Updated) ---
import discord
from discord import app_commands
from discord.ext import commands
from data.quests import QUESTS


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Quests(bot))