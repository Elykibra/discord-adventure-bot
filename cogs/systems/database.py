# --- cogs/systems/database.py (Updated to v4.2.0) ---
# This file handles all database interactions using SQLite.
# It has been updated to reflect the new centralized item data structure.

import sqlite3
import json
from discord.ext import commands
import asyncio
from typing import Any, Dict, List, Optional
import math  # <--- FIX: ADD THIS LINE
from data.pets import PET_DATABASE
from data.items import ITEMS

class Database(commands.Cog):
    """
    A cog for handling all database interactions using SQLite.
    Each database operation now creates its own connection and cursor
    to ensure thread safety when used with asyncio.to_thread.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = 'game.db'
        self._create_tables_sync()
        self._run_migrations()
        self._populate_items_sync()

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

    async def add_player(self, user_id: int, username: str, gender: str) -> None:
        """
        Adds a new player to the database with all new default values.
        """

        def _sync_add_player(uid: int, uname: str, ugender: str):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            unlocked_towns = json.dumps(["oakhavenOutpost"])
            cursor.execute(
                '''INSERT INTO players (user_id, username, gender, current_location, unlocked_towns,
                                        main_quest_progress, current_energy, max_energy)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (uid, uname, ugender, 'oakhavenOutpost', unlocked_towns, 0, 100, 100)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_add_player, user_id, username, gender)

    async def add_player_crest(self, user_id: int, crest_name: str) -> None:
        """
        Adds a specific guild crest to a player's collection.
        """

        def _sync_add_crest(uid: int, crest: str):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO player_crests (user_id, crest_name) VALUES (?, ?)', (uid, crest))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
            finally:
                conn.close()

        await asyncio.to_thread(_sync_add_crest, user_id, crest_name)

    async def get_player_crests(self, user_id: int) -> List[str]:
        """
        Retrieves all guild crests a player has earned.
        """

        def _sync_get_crests(uid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT crest_name FROM player_crests WHERE user_id = ?', (uid,))
            results = cursor.fetchall()
            conn.close()
            return [result[0] for result in results]

        return await asyncio.to_thread(_sync_get_crests, user_id)

    async def count_player_crests(self, user_id: int) -> int:
        """
        Counts the number of crests a player has earned.
        """

        def _sync_count_crests(uid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM player_crests WHERE user_id = ?', (uid,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0

        return await asyncio.to_thread(_sync_count_crests, user_id)

    async def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a player by their username.
        """

        def _sync_get_player_by_username(uname: str):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE username = ?', (uname,))
            result = cursor.fetchone()
            conn.close()
            return result

        return await asyncio.to_thread(_sync_get_player_by_username, username)

    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a player by their user ID. Returns the result as a dictionary.
        Also handles JSON parsing for 'unlocked_towns'.
        """

        def _sync_get_player(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE user_id = ?', (uid,))
            result = cursor.fetchone()
            conn.close()
            if result and 'unlocked_towns' in result:
                result['unlocked_towns'] = json.loads(result['unlocked_towns'])
            return result

        return await asyncio.to_thread(_sync_get_player, user_id)

    async def get_top_players(self, limit: int = 10) -> List[tuple]:
        """
        Retrieves the top players based on their coin count.
        """

        def _sync_get_top_players(num_players: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT username, coins FROM players ORDER BY coins DESC LIMIT ?',
                (num_players,)
            )
            results = cursor.fetchall()
            conn.close()
            return results

        return await asyncio.to_thread(_sync_get_top_players, limit)

    async def delete_player_data(self, user_id: int) -> None:
        """
        Deletes all data associated with a player for a full reset.
        """

        def _sync_delete_player(uid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete from all tables where the user_id exists to ensure a clean wipe
            cursor.execute('DELETE FROM players WHERE user_id = ?', (uid,))
            cursor.execute('DELETE FROM pets WHERE owner_id = ?', (uid,))
            cursor.execute('DELETE FROM player_items WHERE user_id = ?', (uid,))
            cursor.execute('DELETE FROM player_quests WHERE user_id = ?', (uid,))
            cursor.execute('DELETE FROM player_crests WHERE user_id = ?', (uid,))

            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_delete_player, user_id)

    async def add_pet(self, owner_id: int, name: str, species: str, description: str, rarity: str, pet_type: str,
                      skills: list, current_hp: int, max_hp: int, attack: int, defense: int, special_attack: int,
                      special_defense: int, speed: int,
                      base_hp: int, base_attack: int, base_defense: int, base_special_attack: int,
                      base_special_defense: int, base_speed: int,
                      passive_ability: Optional[str] = None) -> int: # Add the new optional parameter

        def _sync_add_pet(oid: int, pet_name: str, pet_species: str, desc: str, rar: str, p_type: str,
                          pet_skills: list, p_current_hp: int, p_max_hp: int, p_atk: int, p_def: int, p_sp_atk: int,
                          p_sp_def: int, p_spd: int,
                          p_base_hp: int, p_base_atk: int, p_base_def: int, p_base_sp_atk: int, p_base_sp_def: int,
                          p_base_spd: int, p_passive: Optional[str]) -> int:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            skills_json = json.dumps(pet_skills if pet_skills else [])

            # ADDED 'is_in_party' to the INSERT statement
            cursor.execute(
                '''INSERT INTO pets (owner_id, name, species, description, rarity, pet_type, skills,
                                     current_hp, max_hp, attack, defense, special_attack, special_defense, speed,
                                     base_hp, base_attack, base_defense, base_special_attack, base_special_defense,
                                     base_speed, is_in_party, passive_ability)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)''',
                (oid, pet_name, pet_species, desc, rar, p_type, skills_json,
                 p_current_hp, p_max_hp, p_atk, p_def, p_sp_atk, p_sp_def, p_spd,
                 p_base_hp, p_base_atk, p_base_def, p_base_sp_atk, p_base_sp_def, p_base_spd, p_passive)
            )
            conn.commit()
            lastrowid = cursor.lastrowid
            conn.close()
            return lastrowid

        return await asyncio.to_thread(_sync_add_pet, owner_id, name, species, description, rarity, pet_type,
                                       skills, current_hp, max_hp, attack, defense, special_attack, special_defense,
                                       speed,
                                       base_hp, base_attack, base_defense, base_special_attack, base_special_defense,
                                       base_speed, passive_ability)

    async def get_pet(self, pet_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single pet by its ID and returns it as a dictionary.
        """
        from utils.helpers import _pet_tuple_to_dict  # Import the helper

        def _sync_get_pet(pid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (pid,))
            result = cursor.fetchone()
            conn.close()
            # --- FIX: Convert the tuple to a dictionary before returning ---
            pet_dict = _pet_tuple_to_dict(result)
            if pet_dict and 'skills' in pet_dict:
                pet_dict['skills'] = json.loads(pet_dict['skills'])
            return pet_dict

        return await asyncio.to_thread(_sync_get_pet, pet_id)

    async def get_all_pets(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all pets owned by a specific user.
        """

        def _sync_get_user_pets(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pets WHERE owner_id = ?', (uid,))
            results = cursor.fetchall()
            conn.close()
            # --- FIX: Parse the skills JSON string for every pet ---
            for pet in results:
                if 'skills' in pet:
                    pet['skills'] = json.loads(pet['skills'])
            return results

        return await asyncio.to_thread(_sync_get_user_pets, user_id)

    async def get_main_pet_id(self, user_id: int) -> Optional[int]:
        def _sync_get_main_pet_id(uid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT main_pet_id FROM players WHERE user_id = ?', (uid,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None

        return await asyncio.to_thread(_sync_get_main_pet_id, user_id)

    async def set_main_pet(self, user_id: int, pet_id: int) -> None:
        def _sync_set_main_pet(uid: int, pid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE players SET main_pet_id = ? WHERE user_id = ?',
                (pid, uid)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_set_main_pet, user_id, pet_id)

    async def update_player(self, user_id: int, **kwargs: Any) -> None:
        """
        Updates a player's data in the database with keyword arguments.
        Handles the JSON conversion for 'unlocked_towns' before saving.
        """

        def _sync_update_player(uid: int, updates: Dict[str, Any]):
            if not updates:
                return
            if 'unlocked_towns' in updates:
                updates['unlocked_towns'] = json.dumps(updates['unlocked_towns'])
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(uid)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'UPDATE players SET {set_clause} WHERE user_id = ?', tuple(values))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_update_player, user_id, kwargs)

    async def update_pet(self, pet_id: int, **kwargs: Any) -> None:
        def _sync_update_pet(pid: int, updates: Dict[str, Any]):
            if not updates:
                return
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(pid)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'UPDATE pets SET {set_clause} WHERE pet_id = ?', tuple(values))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_update_pet, pet_id, kwargs)

    async def update_pet_health(self, pet_id: int, new_health: int) -> None:
        """
        Updates a pet's current health.
        """

        def _sync_update_pet_health(pid: int, health: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE pets SET current_health = ? WHERE pet_id = ?',
                (health, pid)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_update_pet_health, pet_id, new_health)

    async def get_game_channel_id(self) -> Optional[str]:
        def _sync_get_game_channel_id():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = "game_channel_id"')
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None

        return await asyncio.to_thread(_sync_get_game_channel_id)

    async def set_game_channel_id(self, channel_id: int) -> None:
        def _sync_set_game_channel_id(cid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                ("game_channel_id", str(cid))
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_set_game_channel_id, channel_id)

    async def get_player_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the player's inventory, returning a list of dictionaries
        with 'item_id' and 'quantity'.
        """

        def _sync_get_player_inventory(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT item_id, quantity FROM player_items WHERE user_id = ?', (uid,))
            results = cursor.fetchall()
            conn.close()
            return results

        return await asyncio.to_thread(_sync_get_player_inventory, user_id)

    async def add_item_to_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        """
        Adds an item to a player's inventory, or increases the quantity if it already exists.
        Uses item_id instead of item_name.
        """

        def _sync_add_item(uid: int, i_id: str, qty: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO player_items (user_id, item_id, quantity)
                   VALUES (?, ?, ?) ON CONFLICT(user_id, item_id) DO
                UPDATE SET quantity = quantity + excluded.quantity''',
                (uid, i_id, qty)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_add_item, user_id, item_id, quantity)

    async def remove_item_from_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        """
        Removes a specified quantity of an item from a player's inventory.
        Removes the item entirely if the quantity drops to 0 or less.
        Uses item_id instead of item_name.
        """

        def _sync_remove_item(uid: int, i_id: str, qty: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE player_items SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?',
                (qty, uid, i_id)
            )
            cursor.execute(
                'DELETE FROM player_items WHERE user_id = ? AND item_id = ? AND quantity <= 0',
                (uid, i_id)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_remove_item, user_id, item_id, quantity)

    async def get_main_pet_info(self, pet_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves the main pet's info for the profile embed.
        """

        def _sync_get_main_pet_info(pid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT name, species FROM pets WHERE pet_id = ?', (pid,))
            result = cursor.fetchone()
            conn.close()
            return result

        return await asyncio.to_thread(_sync_get_main_pet_info, pet_id)

    async def add_coins(self, user_id: int, amount: int) -> None:
        """Adds a specified amount of coins to a player's balance."""

        def _sync_add_coins(uid: int, coins: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE players SET coins = coins + ? WHERE user_id = ?',
                (coins, uid)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_add_coins, user_id, amount)

    async def remove_coins(self, user_id: int, amount: int) -> None:
        """Removes a specified amount of coins from a player's balance."""

        def _sync_remove_coins(uid: int, coins: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE players SET coins = MAX(0, coins - ?) WHERE user_id = ?',
                (coins, uid)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_remove_coins, user_id, amount)

    async def add_quest(self, user_id: int, quest_id: str, progress: Optional[Dict[str, Any]] = None) -> None:
        """Adds a quest to a player's active quest list with optional starting progress."""

        def _sync_add_quest(uid: int, q_id: str, prog: Optional[Dict[str, Any]]):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if prog is None:
                prog = {"status": "in_progress", "count": 0}

            progress_json = json.dumps(prog)

            cursor.execute(
                '''INSERT INTO player_quests (user_id, quest_id, progress)
                   VALUES (?, ?, ?) ON CONFLICT(user_id, quest_id) DO NOTHING''',
                (uid, q_id, progress_json)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_add_quest, user_id, quest_id, progress)

    async def get_active_quests(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves a player's active quests."""

        def _sync_get_quests(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM player_quests WHERE user_id = ?', (uid,))
            results = cursor.fetchall()
            conn.close()
            for r in results:
                r['progress'] = json.loads(r['progress'])
            return results

        return await asyncio.to_thread(_sync_get_quests, user_id)

    async def update_quest_progress(self, user_id: int, quest_id: str, new_progress: Dict[str, Any]) -> None:
        """Updates the progress of an active quest."""

        def _sync_update_progress(uid: int, q_id: str, progress: Dict[str, Any]):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE player_quests SET progress = ? WHERE user_id = ? AND quest_id = ?',
                (json.dumps(progress), uid, q_id)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_update_progress, user_id, quest_id, new_progress)

    async def complete_quest(self, user_id: int, quest_id: str) -> None:
        """Removes a completed quest from a player's active quest list."""

        def _sync_complete_quest(uid: int, q_id: str):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM player_quests WHERE user_id = ? AND quest_id = ?',
                (uid, q_id)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_complete_quest, user_id, quest_id)

    async def add_xp(self, pet_id: int, amount: int) -> tuple:
        """
        Adds XP to a pet, handles leveling up, and recalculates all 6 stats.
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

            new_xp = pet_data['xp'] + xp_amount
            xp_for_next_level = pet_data['level'] * 100
            leveled_up = False

            if new_xp >= xp_for_next_level:
                leveled_up = True
                new_level = pet_data['level'] + 1
                xp_over = new_xp - xp_for_next_level

                # This part is now correct!
                pet_base_data = PET_DATABASE.get(pet_data['species'])

                if pet_base_data:
                    growth_rates = pet_base_data['growth_rates']

                    # This part will now work because 'math' is imported
                    new_max_hp = math.floor(pet_data['base_hp'] + (new_level - 1) * growth_rates['hp'])
                    new_attack = math.floor(pet_data['base_attack'] + (new_level - 1) * growth_rates['attack'])
                    new_defense = math.floor(pet_data['base_defense'] + (new_level - 1) * growth_rates['defense'])
                    new_sp_attack = math.floor(
                        pet_data['base_special_attack'] + (new_level - 1) * growth_rates['special_attack'])
                    new_sp_defense = math.floor(
                        pet_data['base_special_defense'] + (new_level - 1) * growth_rates['special_defense'])
                    new_speed = math.floor(pet_data['base_speed'] + (new_level - 1) * growth_rates['speed'])

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
                                   (new_level, xp_over, new_max_hp, new_max_hp, new_attack, new_defense,
                                    new_sp_attack, new_sp_defense, new_speed, p_id))
                else:
                    cursor.execute('UPDATE pets SET level = ?, xp = ? WHERE pet_id = ?', (new_level, xp_over, p_id))
            else:
                cursor.execute('UPDATE pets SET xp = ? WHERE pet_id = ?', (new_xp, p_id))

            conn.commit()

            cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (p_id,))
            updated_pet = cursor.fetchone()
            if updated_pet and 'skills' in updated_pet:
                updated_pet['skills'] = json.loads(updated_pet['skills'])

            conn.close()
            return updated_pet, leveled_up

        return await asyncio.to_thread(_sync_add_xp, pet_id, amount)

    async def equip_item(self, user_id: int, item_id: str, slot: str):
        """Equips an item to a specified slot for a player."""

        def _sync_equip(uid, i_id, eq_slot):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # The column name is dynamically created from the slot (e.g., 'equipped_head')
            column_name = f"equipped_{eq_slot}"

            # This uses a safe way to update a column dynamically
            cursor.execute(
                f"UPDATE players SET {column_name} = ? WHERE user_id = ?",
                (i_id, uid)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_equip, user_id, item_id, slot)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Database(bot))