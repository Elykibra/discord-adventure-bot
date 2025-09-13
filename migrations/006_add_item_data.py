# migrations/006_add_item_data.py

async def apply(cursor):
    """
    Migration 006: Adds a JSONB column to player_items for dynamic item data.
    """
    # Using JSONB is efficient for querying in PostgreSQL
    await cursor.execute('''
        ALTER TABLE player_items ADD COLUMN IF NOT EXISTS item_data JSONB;
    ''')