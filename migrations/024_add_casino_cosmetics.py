# migrations/024_add_casino_cosmetics.py

async def apply(cursor):
    """
    Migration 024: Adds the casino cosmetics shop — one generic ownership
    table across every cosmetic category (Card Backs, Titles, Slot
    Themes, Weapon Skins, Table Flair, Taunt Lines), same "no migration
    needed for a new item" shape as casino_game_stats/casino_badges.
    cosmetic_key is globally unique across every category (e.g.
    "cardback_hanafuda", "title_high_roller" — see data/casino_cosmetics.py).

    Equipped state is one nullable column per category on casino_wallets,
    mirroring equipped_weapon from migrations/015_add_casino_armory.py.
    NULL means "using the current default look" — nothing to backfill
    for existing players.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_cosmetics (
            user_id BIGINT NOT NULL,
            cosmetic_key TEXT NOT NULL,
            acquired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (user_id, cosmetic_key)
        )
    """)
    await cursor.execute("""
        ALTER TABLE casino_wallets
        ADD COLUMN IF NOT EXISTS equipped_card_back TEXT,
        ADD COLUMN IF NOT EXISTS equipped_title TEXT,
        ADD COLUMN IF NOT EXISTS equipped_slot_theme TEXT,
        ADD COLUMN IF NOT EXISTS equipped_weapon_skin TEXT,
        ADD COLUMN IF NOT EXISTS equipped_table_flair TEXT,
        ADD COLUMN IF NOT EXISTS equipped_taunt TEXT
    """)
