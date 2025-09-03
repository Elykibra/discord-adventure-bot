# cogs/systems/database.py (Refactored)
# This file handles all database interactions using SQLite.

import sqlite3
import json
from discord.ext import commands
import asyncio
from typing import Any, Dict, List, Optional
from data.items import ITEMS

# --- REFACTOR ---
# We now import our Pet class from the core game logic layer.
from core.pet_system import Pet


class Database(commands.Cog):
    """
    A cog for handling all database interactions using SQLite.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = 'game.db'
        self._create_tables_sync()
        self._run_migrations()
        self._populate_items_sync()

    # No changes needed for these internal setup methods
    def _get_table_info(self, cursor, table_name):
        """Helper to get column names of a table."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        return {row[1] for row in cursor.fetchall()}

    def _run_migrations(self):
        """Adds new columns to existing tables without deleting data."""
        print("--- Running Database Migrations ---")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # --- Migration for Player Gear Slots ---
        player_columns = self._get_table_info(cursor, 'players')

        if 'equipped_head' not in player_columns:
            print("  > Migrating players table: Adding 'equipped_head'")
            cursor.execute("ALTER TABLE players ADD COLUMN equipped_head TEXT")

        if 'equipped_charm' not in player_columns:
            print("  > Migrating players table: Adding 'equipped_charm'")
            cursor.execute("ALTER TABLE players ADD COLUMN equipped_charm TEXT")

        # You can add more 'if' blocks here for future columns.
        # Example:
        # if 'equipped_body' not in player_columns:
        #     print("  > Migrating players table: Adding 'equipped_body'")
        #     cursor.execute("ALTER TABLE players ADD COLUMN equipped_body TEXT")

        conn.commit()
        conn.close()
        print("--- Migrations Complete ---")

    def _create_tables_sync(self):
        """
        Synchronously creates tables. This is only called on bot startup.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # The 'players' table has been updated with new columns for the game's new mechanics.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS players
                       (
                           user_id
                           INTEGER
                           PRIMARY
                           KEY,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           gender
                           TEXT,
                           coins
                           INTEGER
                           DEFAULT
                           0,
                           reputation
                           INTEGER
                           DEFAULT
                           0,
                           main_pet_id
                           INTEGER,
                           current_location
                           TEXT
                           DEFAULT
                           'oakhavenOutpost',
                           unlocked_towns
                           TEXT
                           DEFAULT
                           '["oakhavenOutpost"]',
                           main_quest_progress
                           INTEGER
                           DEFAULT
                           0,
                           current_energy
                           INTEGER
                           DEFAULT
                           100,
                           max_energy
                           INTEGER
                           DEFAULT
                           100,
                           day_of_cycle
                           TEXT
                           DEFAULT
                           'day',
                           -- NEW GEAR SLOTS --
                           equipped_head TEXT,
                           equipped_charm TEXT,
                           -- Add other slots like body, feet, etc. here in the future --
                           version
                           TEXT
                           DEFAULT
                           '4.0.0'
                       )
                       ''')

        # The 'pets' table has been updated with a new skills column
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS pets
                       (
                           pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                           owner_id INTEGER,
                           name TEXT NOT NULL,
                           species TEXT NOT NULL,
                           description TEXT,
                           rarity TEXT NOT NULL,
                           pet_type TEXT NOT NULL,
                           level INTEGER DEFAULT 1,
                           xp INTEGER DEFAULT 0,
                           current_hp INTEGER DEFAULT 1,
                           max_hp INTEGER DEFAULT 1,
                           attack INTEGER DEFAULT 1,
                           defense INTEGER DEFAULT 1,
                           special_attack INTEGER DEFAULT 1,
                           special_defense INTEGER DEFAULT 1,
                           speed INTEGER DEFAULT 1,
                           base_hp INTEGER DEFAULT 1,
                           base_attack INTEGER DEFAULT 1,
                           base_defense INTEGER DEFAULT 1,
                           base_special_attack INTEGER DEFAULT 1,
                           base_special_defense INTEGER DEFAULT 1,
                           base_speed INTEGER DEFAULT 1,
                           hunger INTEGER DEFAULT 100,
                           skills TEXT DEFAULT '[]',
                           is_in_party INTEGER DEFAULT 1,
                           passive_ability TEXT,
                           FOREIGN KEY(owner_id) REFERENCES players(user_id) ON DELETE SET NULL
                       )
                       ''')

        # Create a table to track specific guild crests earned by each player.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS player_crests
                       (
                           user_id
                           INTEGER,
                           crest_name
                           TEXT
                           NOT
                           NULL,
                           PRIMARY
                           KEY
                       (
                           user_id,
                           crest_name
                       ),
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES players
                       (
                           user_id
                       ) ON DELETE CASCADE
                           )
                       ''')

        # --- SCHEMA CHANGE ---
        # The 'items' table now uses item_id as the primary key for better data integrity.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS items
                       (
                           item_id
                           TEXT
                           PRIMARY
                           KEY,
                           name
                           TEXT,
                           description
                           TEXT,
                           category
                           TEXT,
                           price
                           INTEGER
                       )
                       ''')

        # --- SCHEMA CHANGE ---
        # The player_inventory table is renamed to player_items and references item_id.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS player_items
                       (
                           user_id
                           INTEGER,
                           item_id
                           TEXT
                           NOT
                           NULL,
                           quantity
                           INTEGER
                           DEFAULT
                           1,
                           PRIMARY
                           KEY
                       (
                           user_id,
                           item_id
                       ),
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES players
                       (
                           user_id
                       ) ON DELETE CASCADE,
                           FOREIGN KEY
                       (
                           item_id
                       ) REFERENCES items
                       (
                           item_id
                       )
                           )
                       ''')

        # Create a table for global settings, like the game channel ID
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS settings
                       (
                           key
                           TEXT
                           PRIMARY
                           KEY,
                           value
                           TEXT
                       )
                       ''')

        # New table for quests
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS player_quests
                       (
                           user_id
                           INTEGER,
                           quest_id
                           TEXT
                           NOT
                           NULL,
                           progress
                           TEXT
                           DEFAULT
                           '{"status": "in_progress", "count": 0}',
                           PRIMARY
                           KEY
                       (
                           user_id,
                           quest_id
                       ),
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES players
                       (
                           user_id
                       ) ON DELETE CASCADE
                           )
                       ''')

        conn.commit()
        conn.close()

    def _populate_items_sync(self):
        """
        Synchronously populates the 'items' table with data from data/items.py.
        This is only called once on bot startup.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Use the new ITEMS dictionary and the updated table schema.
        for item_id, item_data in ITEMS.items():
            cursor.execute(
                '''INSERT
                OR IGNORE INTO items (item_id, name, description, category, price)
                   VALUES (?, ?, ?, ?, ?)''',
                (item_id, item_data.get('name'), item_data.get('description'),
                 item_data.get('category'), item_data.get('price'))
            )
        conn.commit()
        conn.close()

    def _dict_factory(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
        """Helper function to convert a query result to a dictionary."""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # No changes are needed for the other database functions (get_player, add_item, etc.)
    # as they are already just reading and writing data.
    # ... (all other functions like get_player, add_player, update_pet, add_item, etc. remain the same) ...
    async def get_player_and_pet_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetches a player's data and their main pet's data in a single operation.
        This is a new helper function for the status bar implementation.
        """

        def _sync_get_data(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE user_id = ?', (uid,))
            player_data = cursor.fetchone()
            if not player_data:
                conn.close()
                return None
            player_data['unlocked_towns'] = json.loads(player_data.get('unlocked_towns', '[]'))
            main_pet_id = player_data.get('main_pet_id')
            main_pet_data = None
            if main_pet_id:
                cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (main_pet_id,))
                main_pet_data = cursor.fetchone()
            conn.close()
            return {'player_data': player_data, 'main_pet_data': main_pet_data}

        return await asyncio.to_thread(_sync_get_data, user_id)

    async def add_xp(self, pet_id: int, amount: int) -> tuple:
        """
        Adds XP to a pet by using the core Pet class to handle game logic.
        Returns the updated pet dictionary and a boolean indicating if a level up occurred.
        """

        def _sync_add_xp(p_id: int, xp_amount: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (p_id,))
            pet_data = cursor.fetchone()
            if not pet_data:
                conn.close()
                return None, False

            # --- REFACTORED LOGIC ---
            # 1. Create a Pet object from the loaded data
            pet_object = Pet(pet_data)

            # 2. Use the Pet object to handle the level-up logic
            leveled_up = pet_object.add_xp(xp_amount)

            # 3. Get the updated data back from the object
            data_to_save = pet_object.to_dict_for_saving()

            # 4. Save the simplified data back to the database
            cursor.execute('''UPDATE pets
                              SET level           = ?,
                                  xp              = ?,
                                  max_hp          = ?,
                                  current_hp      = ?,
                                  attack          = ?,
                                  defense         = ?,
                                  special_attack  = ?,
                                  special_defense = ?,
                                  speed           = ?
                              WHERE pet_id = ?''',
                           (data_to_save['level'], data_to_save['xp'], data_to_save['max_hp'],
                            data_to_save['current_hp'], data_to_save['attack'], data_to_save['defense'],
                            data_to_save['special_attack'], data_to_save['special_defense'],
                            data_to_save['speed'], p_id))

            conn.commit()

            # Fetch the fully updated pet to return it
            cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (p_id,))
            updated_pet = cursor.fetchone()
            if updated_pet and 'skills' in updated_pet:
                updated_pet['skills'] = json.loads(updated_pet['skills'])

            conn.close()
            return updated_pet, leveled_up

        return await asyncio.to_thread(_sync_add_xp, pet_id, amount)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Database(bot))