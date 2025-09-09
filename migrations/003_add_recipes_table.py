# migrations/003_add_recipes_table.py

async def apply(cursor):
    """
    Migration 003: Adds the player_recipes table to track learned recipes.
    """
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_recipes (
            user_id BIGINT,
            recipe_id TEXT NOT NULL,
            PRIMARY KEY (user_id, recipe_id),
            FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
        )
    ''')