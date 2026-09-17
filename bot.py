import discord, os, asyncio
import asyncpg
from discord.ext import commands
from core import config
from core.repository import MemoryRepository, SqlRepository
from core.validator import validate_all

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
    """A real global sync (no per-guild loop) — propagates to every guild
    the bot is in over time (up to ~an hour per Discord's own docs),
    instead of hitting the tight per-guild bulk-overwrite rate limit on
    every single restart. For instant updates in one server while
    testing, use the admin /sync command instead (cogs/admin.py) — it
    does its own guild-scoped sync on demand, so this one doesn't need
    to (and shouldn't) also race to do that on every boot."""
    print("--- Syncing Commands (GLOBAL) ---")
    try:
        synced = await bot.tree.sync()
        print(f"  > Synced {len(synced)} global command(s).")
    except Exception as e:
        print(f"  > An error with syncing occurred: {e}")
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

        # 4) Load the rest of the cogs (skip __init__.py and database.py)
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
    # Run this ONCE after the bot is fully ready (guilds are cached) — not
    # on every gateway reconnect, which also fires on_ready but isn't a
    # fresh process start.
    if getattr(bot, "_did_global_cleanup", False):
        return
    bot._did_global_cleanup = True

    # 1) Register the global command set. Deliberately just this — no
    # per-guild clear/resync loop here anymore (removed after it and the
    # admin /sync command repeatedly hit Discord's per-guild command
    # rate limit together during a day of frequent redeploys). Run
    # /sync in a server when you want that server updated immediately.
    await sync_commands_global(bot)

    # 2) Clean up any orphaned battle spectator messages from before the restart
    db_cog = bot.get_cog('Database')
    if db_cog:
        try:
            orphaned = await db_cog.get_all_active_battles()
            for record in orphaned:
                try:
                    channel = bot.get_channel(record['spectator_channel_id'])
                    if channel:
                        msg = await channel.fetch_message(record['spectator_message_id'])
                        await msg.delete()
                except Exception:
                    pass
                await db_cog.clear_active_battle(record['user_id'])
            if orphaned:
                print(f"🧹 Cleaned up {len(orphaned)} orphaned battle panel(s).")
        except Exception as e:
            print(f"⚠️ Battle cleanup error: {e}")

        # 3) Refund any poker tables left mid-session by a restart. Poker
        # keeps its live state in memory only, same as Blackjack/Dungeon —
        # this is just the stacks safety net (see migrations/018), not a
        # recovery of the in-progress hand itself. Also try to close out
        # the old table message so its buttons don't just silently eat
        # clicks — the View object behind them is gone after a restart,
        # so discord.py discards any interaction with nothing to route it
        # to, which looks to a player like the bot hung.
        try:
            orphaned_tables = await db_cog.get_all_poker_snapshots()
            for snapshot in orphaned_tables:
                for user_id_str, stack in snapshot["stacks"].items():
                    if stack > 0:
                        await db_cog.add_chips(int(user_id_str), stack)

                try:
                    channel_id = snapshot.get("channel_id")
                    if channel_id:
                        channel = bot.get_channel(channel_id)
                        if channel:
                            msg = await channel.fetch_message(int(snapshot["table_key"]))
                            await msg.edit(
                                embed=discord.Embed(
                                    title="🃏 Poker Table — Closed",
                                    description=(
                                        "*The bot restarted while this table was active — "
                                        "everyone's buy-in has been refunded. Open a new table to keep playing.*"
                                    ),
                                    color=discord.Color.dark_grey(),
                                ),
                                view=None,
                            )
                except Exception:
                    pass  # best-effort — the refund above already happened either way

                await db_cog.clear_poker_snapshot(snapshot["table_key"])
            if orphaned_tables:
                print(f"🃏 Refunded {len(orphaned_tables)} orphaned poker table(s) after restart.")
        except Exception as e:
            print(f"⚠️ Poker snapshot recovery error: {e}")

bot.run(config.DISCORD_TOKEN)


