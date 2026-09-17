# migrations/020_add_poker_snapshot_channel.py

async def apply(cursor):
    """
    Migration 020: Adds channel_id to poker_session_snapshots.

    The restart-recovery cleanup (see poker_session_snapshots' own
    migration, 018) refunds everyone's chips from an orphaned table, but
    couldn't actually reach the old table message to say so — clicking
    its buttons after a restart just gets silently discarded by
    discord.py (the in-memory View is gone), which looks to a player
    like the bot hung. Storing the channel alongside the table's message
    id lets the recovery step fetch and edit that message to clearly
    show it's closed instead of leaving it looking alive.
    """
    await cursor.execute("""
        ALTER TABLE poker_session_snapshots ADD COLUMN IF NOT EXISTS channel_id BIGINT
    """)
