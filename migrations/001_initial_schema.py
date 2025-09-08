# migrations/001_initial_schema.py
import sqlite3

async def apply(cursor):
    """
    Migration 001: Establishes the complete initial schema for PostgreSQL.
    """
    # --- Schema Version Table (for PostgreSQL) ---
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL
        )
    ''')
    await cursor.execute("INSERT INTO schema_version (id, version) VALUES (1, 0) ON CONFLICT (id) DO NOTHING")

    # --- Players Table ---
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id BIGINT PRIMARY KEY,
            username TEXT NOT NULL,
            gender TEXT,
            coins INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            main_pet_id INTEGER,
            current_location TEXT DEFAULT 'oakhavenOutpost',
            unlocked_towns JSONB DEFAULT '["oakhavenOutpost"]',
            current_energy INTEGER DEFAULT 100,
            max_energy INTEGER DEFAULT 100,
            day_of_cycle TEXT DEFAULT 'day'
        )
    ''')

    # --- Pets Table ---
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            pet_id BIGSERIAL PRIMARY KEY,
            owner_id BIGINT,
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
            skills JSONB DEFAULT '[]',
            is_in_party BOOLEAN DEFAULT TRUE,
            passive_ability TEXT,
            FOREIGN KEY(owner_id) REFERENCES players(user_id) ON DELETE CASCADE
        )
    ''')

    # --- Items and Inventory ---
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            category TEXT,
            price INTEGER
        )
    ''')

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_items (
            user_id BIGINT,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, item_id),
            FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        )
    ''')

    # --- Quests and Crests ---
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_quests (
            user_id BIGINT,
            quest_id TEXT NOT NULL,
            progress JSONB DEFAULT '{"status": "in_progress", "count": 0}',
            PRIMARY KEY (user_id, quest_id),
            FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
        )
    ''')

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_crests (
            user_id BIGINT,
            crest_name TEXT NOT NULL,
            PRIMARY KEY (user_id, crest_name),
            FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
        )
    ''')

    # --- Settings ---
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')