# migrations/005_add_skill_library.py

async def apply(cursor):
    """
    Migration 005: Adds the pet_skill_library table to store all learned skills.
    """
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS pet_skill_library (
            pet_id BIGINT,
            skill_id TEXT NOT NULL,
            PRIMARY KEY (pet_id, skill_id),
            FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE
        )
    ''')