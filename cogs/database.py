# cogs/systems/database.py (Fully Refactored & Complete)
# Handles all database interactions using SQLite.

import os
import importlib.util
import sqlite3
import json
import asyncio
from discord.ext import commands
from typing import Any, Dict, List, Optional

from data.items import ITEMS
from core.pet_system import Pet


class Database(commands.Cog):
    """
    A cog for handling all database interactions using SQLite.
    It uses a version-controlled migration system for schema management.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = 'game.db'

        # --- 1. Run all setup tasks using temporary, safe connections ---
        print("--- Initializing Database ---")
        self._initialize_schema_version()
        self._run_migrations()
        self._populate_items_sync()
        print("--- Database Initialization Complete ---")

        # --- 2. Open the persistent runtime connection for the bot ---
        # check_same_thread=False is necessary for use with asyncio.to_thread
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = self._dict_factory
        self.cursor = self.conn.cursor()

    def _dict_factory(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
        """Helper function to convert a query result to a dictionary."""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _initialize_schema_version(self):
        """Ensures the schema_version table exists. This is the first step."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    version INTEGER NOT NULL
                )
            ''')
            cursor.execute("INSERT OR IGNORE INTO schema_version (id, version) VALUES (1, 0)")
            conn.commit()

    def _run_migrations(self):
        """Applies all pending database migrations in order."""
        print("--- Running Database Migrations ---")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version WHERE id = 1")
            current_version = cursor.fetchone()[0]
            print(f"Current database version: {current_version}")

            migration_files = sorted([f for f in os.listdir('migrations') if f.endswith('.py')])
            for filename in migration_files:
                script_version = int(filename.split('_')[0])
                if script_version > current_version:
                    print(f"  > Applying migration {filename}...")
                    spec = importlib.util.spec_from_file_location(filename, f"migrations/{filename}")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    try:
                        module.apply(cursor)
                        cursor.execute("UPDATE schema_version SET version = ? WHERE id = 1", (script_version,))
                        conn.commit()
                        print(f"  > Success. Database is now at version {script_version}.")
                    except Exception as e:
                        print(f"  > [FATAL ERROR] Migration {filename} failed: {e}")
                        conn.rollback()
                        break
        print("--- Migrations Complete ---")

    def _populate_items_sync(self):
        """Populates the 'items' table from the ITEMS dictionary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for item_id, item_data in ITEMS.items():
                cursor.execute(
                    '''INSERT OR IGNORE INTO items (item_id, name, description, category, price)
                       VALUES (?, ?, ?, ?, ?)''',
                    (item_id, item_data.get('name'), item_data.get('description'),
                     item_data.get('category'), item_data.get('price'))
                )
            conn.commit()

    def cog_unload(self):
        """Close the connection when the cog is unloaded."""
        self.conn.close()

    # --- Player Management ---

    async def add_player(self, user_id: int, username: str, gender: str) -> None:
        """Adds a new player to the database."""

        def _sync_add_player():
            unlocked_towns = json.dumps(["oakhavenOutpost"])
            self.cursor.execute(
                '''INSERT INTO players (user_id, username, gender, unlocked_towns)
                   VALUES (?, ?, ?, ?)''',
                (user_id, username, gender, unlocked_towns)
            )
            self.conn.commit()

        await asyncio.to_thread(_sync_add_player)

    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a player by their user ID."""

        def _sync_get_player():
            self.cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            if result:
                result['unlocked_towns'] = json.loads(result.get('unlocked_towns', '[]'))
            return result

        return await asyncio.to_thread(_sync_get_player)

    async def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves a player by their username."""

        def _sync_get_player_by_username():
            self.cursor.execute('SELECT * FROM players WHERE username = ?', (username,))
            return self.cursor.fetchone()

        return await asyncio.to_thread(_sync_get_player_by_username)

    async def update_player(self, user_id: int, **kwargs: Any) -> None:
        """Updates a player's data with keyword arguments."""

        def _sync_update_player():
            if not kwargs:
                return
            if 'unlocked_towns' in kwargs:
                kwargs['unlocked_towns'] = json.dumps(kwargs['unlocked_towns'])

            set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]

            self.cursor.execute(f'UPDATE players SET {set_clause} WHERE user_id = ?', tuple(values))
            self.conn.commit()

        await asyncio.to_thread(_sync_update_player)

    async def add_coins(self, user_id: int, amount: int) -> None:
        """Adds a specified amount of coins to a player's balance."""

        def _sync_add_coins():
            self.cursor.execute('UPDATE players SET coins = coins + ? WHERE user_id = ?', (amount, user_id))
            self.conn.commit()

        await asyncio.to_thread(_sync_add_coins)

    async def delete_player_data(self, user_id: int) -> None:
        """Deletes all data associated with a player for a full reset."""

        def _sync_delete_player():
            self.cursor.execute('DELETE FROM players WHERE user_id = ?', (user_id,))
            self.cursor.execute('DELETE FROM pets WHERE owner_id = ?', (user_id,))
            self.cursor.execute('DELETE FROM player_items WHERE user_id = ?', (user_id,))
            self.cursor.execute('DELETE FROM player_quests WHERE user_id = ?', (user_id,))
            self.cursor.execute('DELETE FROM player_crests WHERE user_id = ?', (user_id,))
            self.conn.commit()

        await asyncio.to_thread(_sync_delete_player)

    # --- Pet Management ---

    async def add_pet(self, owner_id: int, name: str, species: str, description: str, rarity: str, pet_type: any,
                      skills: list, current_hp: int, max_hp: int, attack: int, defense: int, special_attack: int,
                      special_defense: int, speed: int, base_hp: int, base_attack: int, base_defense: int,
                      base_special_attack: int, base_special_defense: int, base_speed: int,
                      passive_ability: Optional[str] = None) -> int:
        """Adds a new pet to the database for a given owner."""

        def _sync_add_pet() -> int:
            skills_json = json.dumps(skills if skills else [])
            pet_type_to_save = json.dumps(pet_type) if isinstance(pet_type, list) else pet_type

            self.cursor.execute(
                '''INSERT INTO pets (owner_id, name, species, description, rarity, pet_type, skills,
                                     current_hp, max_hp, attack, defense, special_attack, special_defense, speed,
                                     base_hp, base_attack, base_defense, base_special_attack, base_special_defense,
                                     base_speed, is_in_party, passive_ability)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)''',
                (owner_id, name, species, description, rarity, pet_type_to_save, skills_json, current_hp, max_hp,
                 attack,
                 defense, special_attack, special_defense, speed, base_hp, base_attack, base_defense,
                 base_special_attack, base_special_defense, base_speed, passive_ability)
            )
            self.conn.commit()
            return self.cursor.lastrowid

        return await asyncio.to_thread(_sync_add_pet)

    async def get_pet(self, pet_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single pet by its ID."""

        def _sync_get_pet():
            self.cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (pet_id,))
            pet_dict = self.cursor.fetchone()
            if pet_dict:
                if 'skills' in pet_dict and isinstance(pet_dict['skills'], str):
                    pet_dict['skills'] = json.loads(pet_dict['skills'])
                if 'pet_type' in pet_dict and isinstance(pet_dict['pet_type'], str) and pet_dict['pet_type'].startswith(
                        '['):
                    pet_dict['pet_type'] = json.loads(pet_dict['pet_type'])
            return pet_dict

        return await asyncio.to_thread(_sync_get_pet)

    async def get_all_pets(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves all pets owned by a specific user."""

        def _sync_get_user_pets():
            self.cursor.execute('SELECT * FROM pets WHERE owner_id = ?', (user_id,))
            results = self.cursor.fetchall()
            for pet in results:
                if 'skills' in pet and isinstance(pet['skills'], str):
                    pet['skills'] = json.loads(pet['skills'])
                if 'pet_type' in pet and isinstance(pet['pet_type'], str) and pet['pet_type'].startswith('['):
                    pet['pet_type'] = json.loads(pet['pet_type'])
            return results

        return await asyncio.to_thread(_sync_get_user_pets)

    async def update_pet(self, pet_id: int, **kwargs: Any) -> None:
        """Updates a pet's data with keyword arguments."""

        def _sync_update_pet():
            if not kwargs:
                return
            if 'skills' in kwargs and isinstance(kwargs['skills'], list):
                kwargs['skills'] = json.dumps(kwargs['skills'])

            set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [pet_id]

            self.cursor.execute(f'UPDATE pets SET {set_clause} WHERE pet_id = ?', tuple(values))
            self.conn.commit()

        await asyncio.to_thread(_sync_update_pet)

    async def set_main_pet(self, user_id: int, pet_id: int) -> None:
        """Sets a pet as the player's main pet."""

        def _sync_set_main_pet():
            self.cursor.execute('UPDATE players SET main_pet_id = ? WHERE user_id = ?', (pet_id, user_id))
            self.conn.commit()

        await asyncio.to_thread(_sync_set_main_pet)

    async def add_xp(self, pet_id: int, amount: int) -> tuple:
        """Adds XP to a pet using the core Pet class and returns the updated pet and level-up status."""

        def _sync_add_xp():
            self.cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (pet_id,))
            pet_data = self.cursor.fetchone()
            if not pet_data:
                return None, False

            pet_object = Pet(pet_data)
            leveled_up = pet_object.add_xp(amount)
            data_to_save = pet_object.to_dict_for_saving()

            self.cursor.execute(
                '''UPDATE pets SET level=?, xp=?, max_hp=?, current_hp=?, attack=?,
                                   defense=?, special_attack=?, special_defense=?, speed=?
                   WHERE pet_id = ?''',
                (data_to_save['level'], data_to_save['xp'], data_to_save['max_hp'], data_to_save['current_hp'],
                 data_to_save['attack'], data_to_save['defense'], data_to_save['special_attack'],
                 data_to_save['special_defense'], data_to_save['speed'], pet_id)
            )
            self.conn.commit()

            # Fetch the fully updated pet to return
            self.cursor.execute('SELECT * FROM pets WHERE pet_id = ?', (pet_id,))
            updated_pet = self.cursor.fetchone()
            if updated_pet and 'skills' in updated_pet:
                updated_pet['skills'] = json.loads(updated_pet['skills'])

            return updated_pet, leveled_up

        return await asyncio.to_thread(_sync_add_xp)

    # --- Inventory & Item Management ---

    async def add_item_to_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        """Adds an item to a player's inventory or increases its quantity."""

        def _sync_add_item():
            self.cursor.execute(
                '''INSERT INTO player_items (user_id, item_id, quantity)
                   VALUES (?, ?, ?) ON CONFLICT(user_id, item_id) DO
                   UPDATE SET quantity = quantity + excluded.quantity''',
                (user_id, item_id, quantity)
            )
            self.conn.commit()

        await asyncio.to_thread(_sync_add_item)

    async def remove_item_from_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        """Removes a specified quantity of an item from a player's inventory."""

        def _sync_remove_item():
            self.cursor.execute(
                'UPDATE player_items SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?',
                (quantity, user_id, item_id)
            )
            self.cursor.execute(
                'DELETE FROM player_items WHERE user_id = ? AND item_id = ? AND quantity <= 0',
                (user_id, item_id)
            )
            self.conn.commit()

        await asyncio.to_thread(_sync_remove_item)

    async def get_player_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves a player's inventory."""

        def _sync_get_inventory():
            self.cursor.execute('SELECT item_id, quantity FROM player_items WHERE user_id = ?', (user_id,))
            return self.cursor.fetchall()

        return await asyncio.to_thread(_sync_get_inventory)

    # --- Quest & Crest Management ---

    async def add_quest(self, user_id: int, quest_id: str, progress: Optional[Dict] = None) -> None:
        """Adds a quest to a player's active quest list."""

        def _sync_add_quest():
            prog_json = json.dumps(progress or {"status": "in_progress", "count": 0})
            self.cursor.execute(
                '''INSERT OR IGNORE INTO player_quests (user_id, quest_id, progress)
                   VALUES (?, ?, ?)''',
                (user_id, quest_id, prog_json)
            )
            self.conn.commit()

        await asyncio.to_thread(_sync_add_quest)

    async def get_active_quests(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves a player's active quests."""

        def _sync_get_quests():
            self.cursor.execute('SELECT * FROM player_quests WHERE user_id = ?', (user_id,))
            results = self.cursor.fetchall()
            for r in results:
                r['progress'] = json.loads(r['progress'])
            return results

        return await asyncio.to_thread(_sync_get_quests)

    async def update_quest_progress(self, user_id: int, quest_id: str, new_progress: Dict[str, Any]) -> None:
        """Updates the progress of an active quest."""

        def _sync_update_progress():
            self.cursor.execute(
                'UPDATE player_quests SET progress = ? WHERE user_id = ? AND quest_id = ?',
                (json.dumps(new_progress), user_id, quest_id)
            )
            self.conn.commit()

        await asyncio.to_thread(_sync_update_progress)

    async def get_player_crests(self, user_id: int) -> List[str]:
        """Retrieves all guild crests a player has earned."""

        def _sync_get_crests():
            self.cursor.execute('SELECT crest_name FROM player_crests WHERE user_id = ?', (user_id,))
            return [row['crest_name'] for row in self.cursor.fetchall()]

        return await asyncio.to_thread(_sync_get_crests)

    async def count_player_crests(self, user_id: int) -> int:
        """Counts the number of crests a player has earned."""

        def _sync_count_crests():
            self.cursor.execute('SELECT COUNT(*) FROM player_crests WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            return result['COUNT(*)'] if result else 0

        return await asyncio.to_thread(_sync_count_crests)

    # --- Combined & Game Settings ---

    async def get_player_and_pet_data(self, user_id: int) -> Optional[Dict]:
        """Fetches a player's data and their main pet's data in a single operation."""

        def _sync_get_data():
            player_data = asyncio.run(self.get_player(user_id))
            if not player_data:
                return None

            main_pet_data = None
            main_pet_id = player_data.get('main_pet_id')
            if main_pet_id:
                main_pet_data = asyncio.run(self.get_pet(main_pet_id))

            return {'player_data': player_data, 'main_pet_data': main_pet_data}

        return await asyncio.to_thread(_sync_get_data)

    async def set_game_channel_id(self, channel_id: int) -> None:
        """Saves the game channel ID to the database."""

        def _sync_set_id():
            self.cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                ("game_channel_id", str(channel_id))
            )
            self.conn.commit()

        await asyncio.to_thread(_sync_set_id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Database(bot))