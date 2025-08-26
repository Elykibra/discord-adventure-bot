import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv

## --- REFACTORING CHANGES ---
# The version constant is now imported from its new location.
from cogs.utils.constants import VERSION

# Load environment variables from a .env file.
load_dotenv(".env")

# Retrieve bot token and guild IDs from the environment.
TOKEN: str = os.getenv("DISCORD_TOKEN")
GUILD_IDS: str = os.getenv("GUILD_IDS")
 
if not TOKEN:
    print("Error: DISCORD_TOKEN not found in .env file.")
    exit()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

## --- FIX: Removed the obsolete towns and shop cogs ---
COGS = [
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


async def load_cogs():
    """Loads all cogs from the COGS list."""
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")
            print(f"Error type: {type(e).__name__}")


@bot.event
async def on_ready():
    """This event fires when the bot is connected to Discord."""
    print(f'Bot {bot.user.name} is ready! Version: {VERSION}')
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    await load_cogs()

    try:
        if GUILD_IDS:
            guild_ids_list = [int(g.strip()) for g in GUILD_IDS.split(',') if g.strip().isdigit()]
            if guild_ids_list:
                for guild_id in guild_ids_list:
                    try:
                        my_guild = discord.Object(id=guild_id)
                        synced_commands = await bot.tree.sync(guild=my_guild)
                        print(f"Synced {len(synced_commands)} command(s) to guild {guild_id}")
                    except Exception as e:
                        print(f"Failed to sync to guild {guild_id}: {e}")
            else:
                print("No valid guild IDs found in .env file. Falling back to global sync.")
                synced_commands = await bot.tree.sync()
                print(f"Globally synced {len(synced_commands)} command(s)")
        else:
            synced_commands = await bot.tree.sync()
            print(f"Globally synced {len(synced_commands)} command(s)")
    except Exception as e:
        print("An error with syncing application commands has occurred:", e)

    try:
        command = bot.tree.get_command('adventure')
        if command:
            print("Successfully found the /adventure command in the command tree.")
        else:
            print("ERROR: Could not find the /adventure command. It may not be synced correctly.")
    except Exception as e:
        print(f"ERROR: A fatal error occurred while checking for the /adventure command: {e}")


async def main():
    """The main function to start and run the bot."""
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
