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

    async def add_player(self, user_id: int, username: str, gender: str) -> None:
        """Adds a new player to the database."""

        def _sync_add_player(uid: int, uname: str, ugender: str):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            unlocked_towns = json.dumps(["oakhavenOutpost"])
            cursor.execute(
                '''INSERT INTO players (user_id, username, gender, unlocked_towns)
                   VALUES (?, ?, ?, ?)''',
                (uid, uname, ugender, unlocked_towns)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_add_player, user_id, username, gender)

    async def get_player_and_pet_data(self, user_id: int) -> dict | None:
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

                # This is the new, corrected block
                if main_pet_data:
                    if 'skills' in main_pet_data and isinstance(main_pet_data['skills'], str):
                        main_pet_data['skills'] = json.loads(main_pet_data['skills'])
                    if 'pet_type' in main_pet_data and isinstance(main_pet_data['pet_type'], str) and main_pet_data[
                        'pet_type'].startswith('['):
                        main_pet_data['pet_type'] = json.loads(main_pet_data['pet_type'])

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

    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a player by their user ID."""
        def _sync_get_player(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE user_id = ?', (uid,))
            result = cursor.fetchone()
            conn.close()
            if result:
                result['unlocked_towns'] = json.loads(result.get('unlocked_towns', '[]'))
            return result
        return await asyncio.to_thread(_sync_get_player, user_id)

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

    async def get_active_quests(self, user_id: int) -> list[dict[str, any]]:
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

    async def add_item_to_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        """
        Adds an item to a player's inventory, or increases the quantity if it already exists.
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

    async def add_quest(self, user_id: int, quest_id: str, progress: dict | None = None) -> None:
        """Adds a quest to a player's active quest list."""

        def _sync_add_quest(uid: int, q_id: str, prog: dict | None):
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

    async def update_quest_progress(self, user_id: int, quest_id: str, new_progress: dict[str, any]) -> None:
        """Updates the progress of an active quest."""

        def _sync_update_progress(uid: int, q_id: str, progress: dict[str, any]):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE player_quests SET progress = ? WHERE user_id = ? AND quest_id = ?',
                (json.dumps(progress), uid, q_id)
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_update_progress, user_id, quest_id, new_progress)

    async def get_pet(self, pet_id: int) -> dict | None:
        """Retrieves a single pet by its ID and returns it as a dictionary."""

        def _sync_get_pet(pid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (pid,))
            pet_dict = cursor.fetchone()
            conn.close()

            # The 'skills' column is stored as a JSON string, so we parse it
            if pet_dict:
                if 'skills' in pet_dict and isinstance(pet_dict['skills'], str):
                    pet_dict['skills'] = json.loads(pet_dict['skills'])
                if 'pet_type' in pet_dict and isinstance(pet_dict['pet_type'], str) and pet_dict['pet_type'].startswith('['):
                    pet_dict['pet_type'] = json.loads(pet_dict['pet_type'])
            return pet_dict

        return await asyncio.to_thread(_sync_get_pet, pet_id)

    async def get_player_inventory(self, user_id: int) -> list[dict[str, any]]:
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

    async def get_all_pets(self, user_id: int) -> list[dict[str, any]]:
        """Retrieves all pets owned by a specific user."""

        def _sync_get_user_pets(uid: int):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pets WHERE owner_id = ?', (uid,))
            results = cursor.fetchall()
            conn.close()

            # Parse the skills JSON string for every pet
            for pet in results:
                if 'pet_type' in pet and isinstance(pet['pet_type'], str) and pet[
                    'pet_type'].startswith('['):
                    pet['pet_type'] = json.loads(pet['pet_type'])
            return results

        return await asyncio.to_thread(_sync_get_user_pets, user_id)

    async def update_pet(self, pet_id: int, **kwargs: any) -> None:
        """Updates a pet's data in the database with keyword arguments."""

        def _sync_update_pet(pid: int, updates: dict[str, any]):
            if not updates:
                return

            # Handle the conversion of the skills list to a JSON string for saving
            if 'skills' in updates and isinstance(updates['skills'], list):
                updates['skills'] = json.dumps(updates['skills'])

            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(pid)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'UPDATE pets SET {set_clause} WHERE pet_id = ?', tuple(values))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_update_pet, pet_id, kwargs)

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

    async def remove_item_from_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        """
        Removes a specified quantity of an item from a player's inventory.
        Removes the item entirely if the quantity drops to 0 or less.
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

    async def add_pet(
            self, owner_id: int, name: str, species: str, description: str, rarity: str, pet_type: str,
            skills: list, current_hp: int, max_hp: int, attack: int, defense: int, special_attack: int,
            special_defense: int, speed: int, base_hp: int, base_attack: int, base_defense: int,
            base_special_attack: int, base_special_defense: int, base_speed: int,
            passive_ability: str | None = None
    ) -> int:
        """Adds a new pet to the database for a given owner."""

        def _sync_add_pet(
                oid: int, p_name: str, p_species: str, desc: str, rar: str, p_type: str,
                p_skills: list, p_chp: int, p_mhp: int, p_atk: int, p_def: int, p_satk: int,
                p_sdef: int, p_spd: int, p_bhp: int, p_batk: int, p_bdef: int,
                p_bsatk: int, p_bsdef: int, p_bspd: int, p_passive: str | None
        ) -> int:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            skills_json = json.dumps(p_skills if p_skills else [])
            pet_type_json = json.dumps(p_type)

            cursor.execute(
                '''INSERT INTO pets (owner_id, name, species, description, rarity, pet_type, skills,
                                     current_hp, max_hp, attack, defense, special_attack, special_defense, speed,
                                     base_hp, base_attack, base_defense, base_special_attack, base_special_defense,
                                     base_speed, is_in_party, passive_ability)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)''',
                (
                    oid, p_name, p_species, desc, rar, pet_type_json, skills_json, p_chp, p_mhp, p_atk, p_def, p_satk,
                    p_sdef, p_spd, p_bhp, p_batk, p_bdef, p_bsatk, p_bsdef, p_bspd, p_passive
                )
            )
            conn.commit()
            lastrowid = cursor.lastrowid
            conn.close()
            return lastrowid

        return await asyncio.to_thread(
            _sync_add_pet, owner_id, name, species, description, rarity, pet_type,
            skills, current_hp, max_hp, attack, defense, special_attack,
            special_defense, speed, base_hp, base_attack, base_defense,
            base_special_attack, base_special_defense, base_speed, passive_ability
        )

    async def set_main_pet(self, user_id: int, pet_id: int) -> None:
        """Sets a pet as the player's main pet."""

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

    async def delete_player_data(self, user_id: int) -> None:
        """
        Deletes all data associated with a player for a full reset.
        """

        def _sync_delete_player(uid: int):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete from all tables where the user_id exists
            cursor.execute('DELETE FROM players WHERE user_id = ?', (uid,))
            cursor.execute('DELETE FROM pets WHERE owner_id = ?', (uid,))
            cursor.execute('DELETE FROM player_items WHERE user_id = ?', (uid,))
            cursor.execute('DELETE FROM player_quests WHERE user_id = ?', (uid,))
            cursor.execute('DELETE FROM player_crests WHERE user_id = ?', (uid,))

            conn.commit()
            conn.close()

        await asyncio.to_thread(_sync_delete_player, user_id)

    async def get_player_by_username(self, username: str) -> dict | None:
        """Retrieves a player by their username."""

        def _sync_get_player_by_username(uname: str):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE username = ?', (uname,))
            result = cursor.fetchone()
            conn.close()
            return result

        return await asyncio.to_thread(_sync_get_player_by_username, username)

    async def set_game_channel_id(self, channel_id: int) -> None:
        """Saves the game channel ID to the database."""

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

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Database(bot))