# migrations/014_add_casino_wallets.py

async def apply(cursor):
    """
    Migration 014: Adds the casino wallet system.

    Uses its own "chips" currency, separate from the adventure game's
    players.coins — this powers the standalone /casino economy (daily
    bonus, casino games, the dungeon roguelike) and intentionally never
    touches RPG player data.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_wallets (
            user_id BIGINT PRIMARY KEY,
            balance BIGINT NOT NULL DEFAULT 1000,
            daily_streak INTEGER NOT NULL DEFAULT 0,
            last_daily_claim TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
