# migrations/023_add_casino_badges.py

async def apply(cursor):
    """
    Migration 023: Adds casino_badges — one row per (user, badge) the
    player has earned. Badges are milestone achievements evaluated
    against casino_wallets/casino_game_stats (see data/casino_badges.py
    for the catalog and conditions), so this table only needs to record
    which ones a player has already unlocked and when — no other columns,
    same "no migration needed to add a new badge" reasoning as
    casino_game_stats' game_key design.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_badges (
            user_id BIGINT NOT NULL,
            badge_key TEXT NOT NULL,
            earned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (user_id, badge_key)
        )
    """)
