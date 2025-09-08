# migrations/002_gear_slots.py
import sqlite3

def apply(cursor: sqlite3.Cursor):
    """
    Migration 002: Adds gear slots for players and a charm slot for pets.
    """

    def _get_table_info(cur, table_name):
        cur.execute(f"PRAGMA table_info({table_name})")
        return {row[1] for row in cur.fetchall()}

    # --- Migration for Player Gear Slots ---
    player_columns = _get_table_info(cursor, 'players')

    if 'equipped_head' not in player_columns:
        cursor.execute("ALTER TABLE players ADD COLUMN equipped_head TEXT")
    if 'equipped_tunic' not in player_columns:
        cursor.execute("ALTER TABLE players ADD COLUMN equipped_tunic TEXT")
    if 'equipped_boots' not in player_columns:
        cursor.execute("ALTER TABLE players ADD COLUMN equipped_boots TEXT")
    if 'equipped_accessory' not in player_columns:
        cursor.execute("ALTER TABLE players ADD COLUMN equipped_accessory TEXT")

    # --- Migration for Pet Charm Slot ---
    pet_columns = _get_table_info(cursor, 'pets')
    if 'equipped_charm' not in pet_columns:
        cursor.execute("ALTER TABLE pets ADD COLUMN equipped_charm TEXT")