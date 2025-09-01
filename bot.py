import discord
from discord.ext import commands
import os

from core import config

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Auto-load all cogs in /cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run(config.DISCORD_TOKEN)
