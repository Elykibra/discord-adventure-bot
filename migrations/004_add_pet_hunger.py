# migrations/004_add_pet_hunger.py

async def apply(cursor):
    """
    Migration 004: Adds the hunger attribute to the pets table.
    """
    async def column_exists(table, column):
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = $1 AND column_name = $2
        );
        """
        return await cursor.fetchval(query, table, column)

    if not await column_exists('pets', 'hunger'):
        # Adds the new column and sets the default for existing pets to 100.
        await cursor.execute("ALTER TABLE pets ADD COLUMN hunger INTEGER DEFAULT 100")