# migrations/015_add_casino_armory.py

async def apply(cursor):
    """
    Migration 015: Adds the casino armory — permanent weapons players can
    buy with chips and equip for future dungeon runs.

    The starter "pistol" is free and always owned, so it never gets a row
    here; owned_weapons only tracks paid purchases.
    """
    await cursor.execute("""
        ALTER TABLE casino_wallets
        ADD COLUMN IF NOT EXISTS equipped_weapon TEXT NOT NULL DEFAULT 'pistol'
    """)
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS owned_weapons (
            user_id BIGINT NOT NULL,
            weapon_key TEXT NOT NULL,
            acquired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (user_id, weapon_key)
        )
    """)
