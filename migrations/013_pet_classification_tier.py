# migrations/013_pet_classification_tier.py

async def apply(cursor):
    """
    Migration 013: Replaces the legacy per-pet `rarity` column with
    `classification_tier`.

    The old `rarity` values (Starter/Common/Uncommon/Rare/Ancient/"Very Rare")
    are being retired in favor of the Classification Tier system
    (Ordinary/Prime/Apex/Elder/Ancient/Primordial/Eternal) — see
    docs/design/world/pets_rarity_cleanup.md.

    This renames the column and backfills every existing row from
    PET_DATABASE's classification_tier for that species, falling back to
    'Ordinary' for any species no longer present in the database.
    """
    await cursor.execute("""
        ALTER TABLE pets RENAME COLUMN rarity TO classification_tier
    """)

    # Backfill from PET_DATABASE so existing pets get their proper tier
    # instead of the stale rarity string that used to live in this column.
    from data.pets import PET_DATABASE

    rows = await cursor.fetch("SELECT DISTINCT species FROM pets")
    for row in rows:
        species = row["species"]
        tier = PET_DATABASE.get(species, {}).get("classification_tier", "Ordinary")
        await cursor.execute(
            "UPDATE pets SET classification_tier = $1 WHERE species = $2",
            tier, species,
        )
