import discord, os, asyncio
import asyncpg
from discord.ext import commands
from core import config
from core.repository import MemoryRepository, SqlRepository
from core.validator import validate_all
from core.narrative import Narrative
from data.section_0.story import STORY as STORY_SECTION_0

async def force_clear_all_guild_commands(bot: commands.Bot):
    """
    Remove ANY previously-synced guild-scoped commands in every guild the bot is in.
    Run this AFTER the bot is ready (guild cache is populated).
    """
    print("— Force-clearing ALL guild-scoped commands (post-ready) —")
    cleared_any = False
    for guild in bot.guilds:
        try:
            bot.tree.clear_commands(guild=guild)           # wipe per-guild commands
            await bot.tree.sync(guild=guild)                # push the wipe
            print(f"  > Cleared guild commands for {guild.id} ({guild.name})")
            cleared_any = True
        except Exception as e:
            print(f"  > Failed to clear guild {guild.id}: {e}")
    if not cleared_any:
        print("  > No guilds to clear (cache empty or not in any guild)")

async def build_repo():
    has_db = all([config.DB_HOST, config.DB_PORT, config.DB_USER, config.DB_PASSWORD, config.DB_NAME])
    if not has_db:
        return MemoryRepository()

    pool = await asyncpg.create_pool(
        host=config.DB_HOST,
        port=int(config.DB_PORT or 5432),
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        min_size=1,
        max_size=5,
        command_timeout=30,
    )
    return SqlRepository(pool)

async def sync_commands_global(bot: commands.Bot):
    print("--- Syncing Commands (GLOBAL) ---")
    try:
        await bot.tree.sync()
        print("  > Globally synced commands")
    except Exception as e:
        print(f"  > An error with global syncing occurred: {e}")
    print("----------------------")

class GuildBot(commands.Bot):
    async def setup_hook(self):
        # 1) validate content first
        validate_all()

        # 2) Load DB cog FIRST so it creates the Postgres pool / runs migrations
        try:
            await self.load_extension('cogs.database')
            print('  > Loaded cog: database.py (migrations will run here)')
        except Exception as e:
            print(f'  > Failed to load database cog: {e}')

        # 3) Use the pool from the Database cog for the Repository
        db_cog = self.get_cog("Database")
        pool = getattr(db_cog, "pool", None)
        if pool:
            self.repo = SqlRepository(pool)
            print("  > Repository: SqlRepository (asyncpg pool from Database cog)")
        else:
            self.repo = MemoryRepository()
            print("  > Repository: MemoryRepository (no DB pool found)")

        # 4) Narratives
        self.narratives = {"section_0": Narrative(STORY_SECTION_0, self.repo)}

        # 5) Load the rest of the cogs (skip __init__.py and database.py)
        for filename in os.listdir('./cogs'):
            if not filename.endswith('.py'):
                continue
            if filename in ('__init__.py', 'database.py'):
                continue
            modname = filename[:-3]
            try:
                await self.load_extension(f'cogs.{modname}')
                print(f'  > Loaded cog: {filename}')
            except Exception as e:
                print(f'  > Failed to load cog {filename}: {e}')

        print("✅ Startup complete — ready for commands.")

# intents & bot
intents = discord.Intents.default()
bot = GuildBot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    # Run the cleanup ONCE after the bot is fully ready (guilds are cached)
    if getattr(bot, "_did_global_cleanup", False):
        return
    bot._did_global_cleanup = True

    # 1) Wipe all per-guild commands everywhere
    await force_clear_all_guild_commands(bot)

    # 2) Register ONLY the global set
    await sync_commands_global(bot)

    print("🧹 Guild-scoped commands cleared. Global commands are now the single source.")

bot.run(config.DISCORD_TOKEN)


