# migrations/017_add_casino_stats.py

async def apply(cursor):
    """
    Migration 017: Adds casino_stats — permanent, between-run dungeon
    upgrades (Vitality/Luck/Greed) bought with chips. Separate from
    in-run skills (data/dungeon_skills.py), which reset every run.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_stats (
            user_id BIGINT NOT NULL,
            stat_key TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, stat_key)
        )
    """)
