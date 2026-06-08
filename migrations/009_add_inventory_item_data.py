# migrations/009_add_inventory_item_data.py

async def apply(conn):
    """
    Migration 009: Add item_data JSONB column to inventory table.
    The inventory table was created fresh in migration 008 without this column,
    but the codebase uses it for unique items like Skill Tomes.
    Also ensure player_quests table exists.
    """

    async def column_exists(table: str, column: str) -> bool:
        return await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name=$1 AND column_name=$2)",
            table, column
        )

    async def table_exists(table: str) -> bool:
        return await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name=$1)",
            table
        )

    # Add item_data to inventory if missing
    if not await column_exists('inventory', 'item_data'):
        await conn.execute("ALTER TABLE inventory ADD COLUMN item_data JSONB")

    # Ensure player_quests table exists
    if not await table_exists('player_quests'):
        await conn.execute("""
            CREATE TABLE player_quests (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                quest_id TEXT NOT NULL,
                progress JSONB DEFAULT '{"status": "in_progress", "count": 0}',
                UNIQUE (user_id, quest_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        """)

    # Ensure player_crests table exists
    if not await table_exists('player_crests'):
        await conn.execute("""
            CREATE TABLE player_crests (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                crest_name TEXT NOT NULL,
                UNIQUE (user_id, crest_name),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        """)

    # Ensure pet_skill_library table exists
    if not await table_exists('pet_skill_library'):
        await conn.execute("""
            CREATE TABLE pet_skill_library (
                id BIGSERIAL PRIMARY KEY,
                pet_id BIGINT NOT NULL,
                skill_id TEXT NOT NULL,
                UNIQUE (pet_id, skill_id),
                FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE
            )
        """)

    # Ensure player_recipes table exists
    if not await table_exists('player_recipes'):
        await conn.execute("""
            CREATE TABLE player_recipes (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                recipe_id TEXT NOT NULL,
                UNIQUE (user_id, recipe_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        """)
