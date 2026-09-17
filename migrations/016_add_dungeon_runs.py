# migrations/016_add_dungeon_runs.py

async def apply(cursor):
    """
    Migration 016: Adds dungeon_runs, a history log of completed dungeon
    attempts (died or cashed out), used later for /profile stats and any
    leaderboard.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS dungeon_runs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            floor_reached INTEGER NOT NULL,
            outcome TEXT NOT NULL,
            chips_won INTEGER NOT NULL,
            weapon_key TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
