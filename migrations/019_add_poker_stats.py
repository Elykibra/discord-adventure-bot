# migrations/019_add_poker_stats.py

async def apply(cursor):
    """
    Migration 019: Adds poker_stats (lifetime per-player totals) and
    poker_hand_history (a short server-wide log of resolved hands), for
    the "My Stats" button in the Poker stake picker. Separate from
    casino_stats (permanent dungeon upgrades) — unrelated system.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS poker_stats (
            user_id BIGINT PRIMARY KEY,
            hands_played INTEGER NOT NULL DEFAULT 0,
            hands_won INTEGER NOT NULL DEFAULT 0,
            net_chips BIGINT NOT NULL DEFAULT 0,
            biggest_pot_won BIGINT NOT NULL DEFAULT 0
        )
    """)
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS poker_hand_history (
            id SERIAL PRIMARY KEY,
            table_key TEXT NOT NULL,
            stake_name TEXT NOT NULL,
            pot BIGINT NOT NULL,
            winners_summary TEXT NOT NULL,
            resolved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
