# migrations/002_gear_slots.py
import sqlite3

async def apply(cursor):
    """
    Migration 002: Adds gear slots for players and a charm slot for pets.
    """
    async def column_exists(table, column):
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = $1 AND column_name = $2
        );
        """
        return await cursor.fetchval(query, table, column)

    # --- Migration for Player Gear Slots ---
    if not await column_exists('players', 'equipped_head'):
        await cursor.execute("ALTER TABLE players ADD COLUMN equipped_head TEXT")
    if not await column_exists('players', 'equipped_tunic'):
        await cursor.execute("ALTER TABLE players ADD COLUMN equipped_tunic TEXT")
    if not await column_exists('players', 'equipped_boots'):
        await cursor.execute("ALTER TABLE players ADD COLUMN equipped_boots TEXT")
    if not await column_exists('players', 'equipped_accessory'):
        await cursor.execute("ALTER TABLE players ADD COLUMN equipped_accessory TEXT")

    # --- Migration for Pet Charm Slot ---
    if not await column_exists('pets', 'equipped_charm'):
        await cursor.execute("ALTER TABLE pets ADD COLUMN equipped_charm TEXT")