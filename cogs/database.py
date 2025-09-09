# cogs/database.py (PostgreSQL Version)
import os
import importlib.util
import json
import asyncio
import asyncpg
from discord.ext import commands
from typing import Any, Dict, List, Optional

from core import config
from data.items import ITEMS
from core.pet_system import Pet


class Database(commands.Cog):
    """
    A cog for handling all database interactions using asyncpg.
    It uses a version-controlled migration system for schema management.
    """

    def __init__(self, bot: commands.Bot, pool: asyncpg.Pool):
        self.bot = bot
        self.pool = pool

    @classmethod
    async def create(cls, bot: commands.Bot):
        """A factory method to create an instance of the Database cog with an active connection pool."""
        pool = await asyncpg.create_pool(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        print("--- Successfully connected to PostgreSQL database. ---")
        self = cls(bot, pool)
        await self._run_migrations()
        await self._populate_items()
        return self

    async def _run_migrations(self):
        """Applies all pending database migrations in order."""
        print("--- Running Database Migrations ---")
        async with self.pool.acquire() as conn:
            # Ensure schema_version table exists
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY,
                    version INTEGER NOT NULL
                )
            ''')
            await conn.execute("INSERT INTO schema_version (id, version) VALUES (1, 0) ON CONFLICT (id) DO NOTHING")

            current_version = await conn.fetchval("SELECT version FROM schema_version WHERE id = 1")
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
                        async with conn.transaction():
                            await module.apply(conn)
                            await conn.execute("UPDATE schema_version SET version = $1 WHERE id = 1", script_version)
                        print(f"  > Success. Database is now at version {script_version}.")
                    except Exception as e:
                        print(f"  > [FATAL ERROR] Migration {filename} failed: {e}")
                        break
        print("--- Migrations Complete ---")

    async def _populate_items(self):
        """Populates the 'items' table from the ITEMS dictionary."""
        async with self.pool.acquire() as conn:
            for item_id, item_data in ITEMS.items():

                # --- THIS IS THE FIX ---
                # We check if the category is a list and convert it to a JSON string if it is.
                category = item_data.get('category')
                if isinstance(category, list):
                    category = json.dumps(category)

                await conn.execute(
                    '''INSERT INTO items (item_id, name, description, category, price)
                       VALUES ($1, $2, $3, $4, $5) ON CONFLICT (item_id) DO NOTHING''',
                    item_id, item_data.get('name'), item_data.get('description'),
                    category,  # Use the potentially converted category here
                    item_data.get('price')
                )

    def cog_unload(self):
        """Close the connection pool when the cog is unloaded."""
        asyncio.create_task(self.pool.close())

    def _record_to_dict(self, record: Optional[asyncpg.Record]) -> Optional[Dict[str, Any]]:
        """Helper to convert a single asyncpg.Record to a dictionary."""
        if record is None:
            return None
        return dict(record)

    def _records_to_list_of_dicts(self, records: List[asyncpg.Record]) -> List[Dict[str, Any]]:
        """Helper to convert a list of asyncpg.Record objects to a list of dictionaries."""
        return [dict(r) for r in records]

    # --- Player Management ---
    async def add_player(self, user_id: int, username: str, gender: str) -> None:
        unlocked_towns_json = json.dumps(["oakhavenOutpost"])
        await self.pool.execute(
            'INSERT INTO players (user_id, username, gender, unlocked_towns) VALUES ($1, $2, $3, $4)',
            user_id, username, gender, unlocked_towns_json
        )

    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        record = await self.pool.fetchrow('SELECT * FROM players WHERE user_id = $1', user_id)
        player = self._record_to_dict(record)
        if player and 'unlocked_towns' in player and isinstance(player['unlocked_towns'], str):
            player['unlocked_towns'] = json.loads(player['unlocked_towns'])
        return player

    async def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        record = await self.pool.fetchrow('SELECT * FROM players WHERE username = $1', username)
        return self._record_to_dict(record)

    async def update_player(self, user_id: int, **kwargs: Any) -> None:
        if not kwargs: return
        if 'unlocked_towns' in kwargs:
            kwargs['unlocked_towns'] = json.dumps(kwargs['unlocked_towns'])

        set_clauses = [f"{key} = ${i + 1}" for i, key in enumerate(kwargs.keys())]
        values = list(kwargs.values()) + [user_id]
        query = f'UPDATE players SET {", ".join(set_clauses)} WHERE user_id = ${len(values)}'
        await self.pool.execute(query, *values)

    async def add_coins(self, user_id: int, amount: int) -> None:
        await self.pool.execute('UPDATE players SET coins = coins + $1 WHERE user_id = $2', amount, user_id)

    async def delete_player_data(self, user_id: int) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('DELETE FROM player_items WHERE user_id = $1', user_id)
                await conn.execute('DELETE FROM player_quests WHERE user_id = $1', user_id)
                await conn.execute('DELETE FROM player_crests WHERE user_id = $1', user_id)
                await conn.execute('DELETE FROM pets WHERE owner_id = $1', user_id)
                await conn.execute('DELETE FROM players WHERE user_id = $1', user_id)

    async def get_all_players(self) -> List[Dict[str, Any]]:
        records = await self.pool.fetch('SELECT user_id, username FROM players ORDER BY username')
        return self._records_to_list_of_dicts(records)

    async def add_recipe_to_player(self, user_id: int, recipe_id: str) -> None:
        """Adds a learned recipe to a player's recipe book."""
        query = '''INSERT INTO player_recipes (user_id, recipe_id)
                   VALUES ($1, $2) ON CONFLICT DO NOTHING'''
        await self.pool.execute(query, user_id, recipe_id)

    async def get_player_recipes(self, user_id: int) -> List[str]:
        """Retrieves a list of recipe IDs a player has learned."""
        records = await self.pool.fetch('SELECT recipe_id FROM player_recipes WHERE user_id = $1', user_id)
        return [row['recipe_id'] for row in records]

    # --- Pet Management ---
    async def add_pet(self, owner_id: int, name: str, species: str, description: str, rarity: str, pet_type: any,
                      skills: list, current_hp: int, max_hp: int, attack: int, defense: int, special_attack: int,
                      special_defense: int, speed: int, base_hp: int, base_attack: int, base_defense: int,
                      base_special_attack: int, base_special_defense: int, base_speed: int,
                      passive_ability: Optional[str] = None) -> int:
        skills_json = json.dumps(skills if skills else [])
        pet_type_to_save = json.dumps(pet_type) if isinstance(pet_type, list) else pet_type
        query = '''INSERT INTO pets (owner_id, name, species, description, rarity, pet_type, skills,
                                     current_hp, max_hp, attack, defense, special_attack, special_defense, speed,
                                     base_hp, base_attack, base_defense, base_special_attack, base_special_defense,
                                     base_speed, passive_ability)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
                   RETURNING pet_id'''
        return await self.pool.fetchval(
            query, owner_id, name, species, description, rarity, pet_type_to_save, skills_json,
            current_hp, max_hp, attack, defense, special_attack, special_defense, speed,
            base_hp, base_attack, base_defense, base_special_attack, base_special_defense,
            base_speed, passive_ability
        )

    async def get_pet(self, pet_id: int) -> Optional[Dict[str, Any]]:
        record = await self.pool.fetchrow('SELECT * FROM pets WHERE pet_id = $1', pet_id)
        pet_dict = self._record_to_dict(record)
        if pet_dict:
            if 'skills' in pet_dict and isinstance(pet_dict['skills'], str):
                pet_dict['skills'] = json.loads(pet_dict['skills'])
            if 'pet_type' in pet_dict and isinstance(pet_dict['pet_type'], str) and pet_dict['pet_type'].startswith(
                    '['):
                pet_dict['pet_type'] = json.loads(pet_dict['pet_type'])
        return pet_dict

    async def get_all_pets(self, user_id: int) -> List[Dict[str, Any]]:
        records = await self.pool.fetch('SELECT * FROM pets WHERE owner_id = $1', user_id)
        pet_list = self._records_to_list_of_dicts(records)
        for pet in pet_list:
            if 'skills' in pet and isinstance(pet['skills'], str):
                pet['skills'] = json.loads(pet['skills'])
            if 'pet_type' in pet and isinstance(pet['pet_type'], str) and pet['pet_type'].startswith('['):
                pet['pet_type'] = json.loads(pet['pet_type'])
        return pet_list

    async def update_pet(self, pet_id: int, **kwargs: Any) -> None:
        if not kwargs: return
        if 'skills' in kwargs and isinstance(kwargs['skills'], list):
            kwargs['skills'] = json.dumps(kwargs['skills'])
        set_clauses = [f"{key} = ${i + 1}" for i, key in enumerate(kwargs.keys())]
        values = list(kwargs.values()) + [pet_id]
        query = f'UPDATE pets SET {", ".join(set_clauses)} WHERE pet_id = ${len(values)}'
        await self.pool.execute(query, *values)

    async def set_main_pet(self, user_id: int, pet_id: int) -> None:
        await self.pool.execute('UPDATE players SET main_pet_id = $1 WHERE user_id = $2', pet_id, user_id)

    async def add_xp(self, pet_id: int, amount: int) -> tuple:
        pet_data = await self.get_pet(pet_id)
        if not pet_data: return None, False

        pet_object = Pet(pet_data)
        leveled_up = pet_object.add_xp(amount)
        data_to_save = pet_object.to_dict_for_saving()

        await self.update_pet(pet_id, **data_to_save)

        updated_pet = await self.get_pet(pet_id)
        return updated_pet, leveled_up

    # --- Inventory & Item Management ---
    async def add_item_to_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        query = '''INSERT INTO player_items (user_id, item_id, quantity)
                   VALUES ($1, $2, $3) ON CONFLICT(user_id, item_id) DO
                   UPDATE SET quantity = player_items.quantity + $3'''
        await self.pool.execute(query, user_id, item_id, quantity)

    async def remove_item_from_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    'UPDATE player_items SET quantity = quantity - $1 WHERE user_id = $2 AND item_id = $3',
                    quantity, user_id, item_id)
                await conn.execute('DELETE FROM player_items WHERE user_id = $1 AND item_id = $2 AND quantity <= 0',
                                   user_id, item_id)

    async def get_player_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        records = await self.pool.fetch('SELECT item_id, quantity FROM player_items WHERE user_id = $1', user_id)
        return self._records_to_list_of_dicts(records)

    # --- Quest & Crest Management ---
    async def add_quest(self, user_id: int, quest_id: str, progress: Optional[Dict] = None) -> None:
        prog_json = json.dumps(progress or {"status": "in_progress", "count": 0})
        await self.pool.execute(
            'INSERT INTO player_quests (user_id, quest_id, progress) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING',
            user_id, quest_id, prog_json
        )

    async def get_active_quests(self, user_id: int) -> List[Dict[str, Any]]:
        records = await self.pool.fetch('SELECT * FROM player_quests WHERE user_id = $1', user_id)
        quests = self._records_to_list_of_dicts(records)
        for q in quests:
            if isinstance(q['progress'], str):
                q['progress'] = json.loads(q['progress'])
        return quests

    async def update_quest_progress(self, user_id: int, quest_id: str, new_progress: Dict[str, Any]) -> None:
        await self.pool.execute(
            'UPDATE player_quests SET progress = $1 WHERE user_id = $2 AND quest_id = $3',
            json.dumps(new_progress), user_id, quest_id
        )

    async def get_player_crests(self, user_id: int) -> List[str]:
        records = await self.pool.fetch('SELECT crest_name FROM player_crests WHERE user_id = $1', user_id)
        return [row['crest_name'] for row in records]

    async def count_player_crests(self, user_id: int) -> int:
        return await self.pool.fetchval('SELECT COUNT(*) FROM player_crests WHERE user_id = $1', user_id)

    # --- Combined & Game Settings ---
    async def get_player_and_pet_data(self, user_id: int) -> Optional[Dict]:
        player_data = await self.get_player(user_id)
        if not player_data: return None

        main_pet_data = None
        main_pet_id = player_data.get('main_pet_id')
        if main_pet_id:
            main_pet_data = await self.get_pet(main_pet_id)

        return {'player_data': player_data, 'main_pet_data': main_pet_data}

    async def set_game_channel_id(self, channel_id: int) -> None:
        query = '''INSERT INTO settings (key, value) VALUES ($1, $2)
                   ON CONFLICT (key) DO UPDATE SET value = $2'''
        await self.pool.execute(query, "game_channel_id", str(channel_id))


async def setup(bot: commands.Bot):
    db_cog = await Database.create(bot)
    await bot.add_cog(db_cog)