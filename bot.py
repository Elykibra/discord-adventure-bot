import discord
from discord.ext import commands
import os

from core import config

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """This event fires when the bot is connected and ready."""
    print(f'✅ Logged in as {bot.user.name}')
    print('------')

    # Move your cog-loading for loop here
    print("--- Loading Cogs ---")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                # The await keyword is now correctly inside an async function
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'  > Loaded cog: {filename}')
            except Exception as e:
                print(f'  > Failed to load cog {filename}: {e}')
    print("--------------------")

bot.run(config.DISCORD_TOKEN)