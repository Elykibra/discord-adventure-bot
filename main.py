import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from typing import List

# The version constant is now imported from its new location.
from utils.constants import VERSION

# Load environment variables from a .env file.
load_dotenv(".env")

# --- CONFIGURATION ---
TOKEN: str = os.getenv("DISCORD_TOKEN")
GUILD_IDS_STR: str = os.getenv("GUILD_IDS")
COGS_TO_LOAD = [
    "cogs.gameplay.adventure_core",
    "cogs.systems.database",
    "cogs.systems.game",
    "cogs.systems.general",
    "cogs.systems.welcome",
    "cogs.gameplay.character",
    "cogs.gameplay.crafting",
    "cogs.gameplay.quests",
    "cogs.gameplay.minigames",
    "cogs.gameplay.events",
    "cogs.systems.time",
    "cogs.systems.admin",
]

# --- BOT SETUP ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- HELPER FUNCTIONS ---
async def load_cogs():
    """Loads all cogs from the COGS_TO_LOAD list."""
    print("--- Loading Cogs ---")
    for cog in COGS_TO_LOAD:
        try:
            await bot.load_extension(cog)
            print(f"  > Loaded cog: {cog}")
        except Exception as e:
            print(f"  > Failed to load cog {cog}: {type(e).__name__} - {e}")
    print("--------------------")

async def sync_commands():
    """Syncs slash commands to specific guilds or globally."""
    print("--- Syncing Commands ---")
    guild_ids: List[int] = []
    if GUILD_IDS_STR:
        guild_ids = [int(g.strip()) for g in GUILD_IDS_STR.split(',') if g.strip().isdigit()]

    if guild_ids:
        for guild_id in guild_ids:
            try:
                my_guild = discord.Object(id=guild_id)
                synced = await bot.tree.sync(guild=my_guild)
                print(f"  > Synced {len(synced)} command(s) to guild {guild_id}")
            except Exception as e:
                print(f"  > Failed to sync to guild {guild_id}: {e}")
    else:
        try:
            synced = await bot.tree.sync()
            print(f"  > Globally synced {len(synced)} command(s)")
        except Exception as e:
            print(f"  > An error with global syncing occurred: {e}")
    print("----------------------")


# --- BOT EVENTS ---
@bot.event
async def on_ready():
    """This event fires when the bot is connected to Discord."""
    print(f'Bot {bot.user.name} is ready! Version: {VERSION}')
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    await load_cogs()
    await sync_commands()

# --- MAIN EXECUTION ---
async def main():
    """The main function to start and run the bot."""
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file.")
        return  # Exit gracefully

    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shut down by user.")