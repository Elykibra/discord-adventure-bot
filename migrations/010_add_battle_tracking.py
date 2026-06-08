async def apply(conn):
    """
    Adds spectator_message_id and spectator_channel_id to the players table
    so orphaned battle panels can be cleaned up on bot restart.
    """
    await conn.execute("""
        ALTER TABLE players
        ADD COLUMN IF NOT EXISTS spectator_message_id BIGINT DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS spectator_channel_id BIGINT DEFAULT NULL
    """)
