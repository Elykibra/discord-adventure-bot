# migrations/011_add_last_town_id.py

async def apply(cursor):
    """
    Migration 011: Adds last_town_id to players table.

    Tracks the last full town the player was in.
    Used for defeat respawn — if a player is defeated at a Remnant,
    they are sent back to their last known town.
    """
    await cursor.execute("""
        ALTER TABLE players
        ADD COLUMN IF NOT EXISTS last_town_id TEXT DEFAULT 'oakhavenOutpost'
    """)
