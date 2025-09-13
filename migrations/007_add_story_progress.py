# migrations/007_add_story_progress.py

async def apply(conn):
    """
    Migration 007: Add story progress fields to players for Section 0 (and beyond).
    Postgres (asyncpg) style.
    """

    async def column_exists(table: str, column: str) -> bool:
        q = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = $1 AND column_name = $2
        );
        """
        return await conn.fetchval(q, table, column)

    if not await column_exists('players', 'session_message_id'):
        await conn.execute("ALTER TABLE players ADD COLUMN session_message_id BIGINT")

    # optional: backfill or normalize values if needed
    # e.g., set all existing players to tutorial start:
    # await conn.execute("UPDATE players SET section_id = 'section_0', story_step_id = 'intro_1' WHERE section_id IS NULL OR story_step_id IS NULL")
