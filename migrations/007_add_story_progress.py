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

    if not await column_exists('players', 'section_id'):
        await conn.execute("ALTER TABLE players ADD COLUMN section_id TEXT DEFAULT 'section_0'")

    if not await column_exists('players', 'story_step_id'):
        await conn.execute("ALTER TABLE players ADD COLUMN story_step_id TEXT DEFAULT 'intro_1'")
