# migrations/012_add_player_counters.py

async def apply(cursor):
    """
    Migration 012: Adds a generic per-player counter table.

    Used for tracking arbitrary numeric progress that doesn't fit the
    boolean player_flags table — e.g. how many times a player has visited
    a specific location (for dwell/visit-based on_enter triggers), how
    many times they've rested somewhere, repeatable-task tallies, etc.

    Each (player_id, counter_key) pair holds a single integer value.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_counters (
            player_id BIGINT NOT NULL,
            counter_key TEXT NOT NULL,
            value INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (player_id, counter_key)
        )
    """)
