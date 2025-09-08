import discord
from discord.ext import commands
import os

from core import config

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def sync_commands():
    """Syncs slash commands to specific guilds or globally."""
    print("--- Syncing Commands ---")

    # Use the GUILD_IDS list directly from your config
    if config.GUILD_IDS:
        for guild_id in config.GUILD_IDS:
            try:
                guild = discord.Object(id=guild_id)
                await bot.tree.sync(guild=guild)
                print(f"  > Synced commands to guild {guild_id}")
            except Exception as e:
                print(f"  > Failed to sync to guild {guild_id}: {e}")
    else:
        # Sync globally if no guild IDs are provided
        try:
            await bot.tree.sync()
            print("  > Globally synced commands")
        except Exception as e:
            print(f"  > An error with global syncing occurred: {e}")

    print("----------------------")


@bot.event
async def on_ready():
    """This event fires when the bot is connected and ready."""
    print(f'✅ Logged in as {bot.user.name}')
    print('------')

    # Load all cogs first, so the bot knows about all your commands
    print("--- Loading Cogs ---")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'  > Loaded cog: {filename}')
            except Exception as e:
                print(f'  > Failed to load cog {filename}: {e}')
    print("--------------------")

    # Now, sync the commands after they have all been loaded
    await sync_commands()


bot.run(config.DISCORD_TOKEN)