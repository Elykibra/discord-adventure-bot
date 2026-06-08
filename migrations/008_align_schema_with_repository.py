# migrations/008_align_schema_with_repository.py

async def apply(conn):
    """
    Migration 008: Align the players table and related tables with the SqlRepository code.
    """

    async def column_exists(table: str, column: str) -> bool:
        q = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = $1 AND column_name = $2
        );
        """
        return await conn.fetchval(q, table, column)

    async def table_exists(table: str) -> bool:
        q = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = $1
        );
        """
        return await conn.fetchval(q, table)

    # --- players: add energy (code uses 'energy', schema had 'current_energy') ---
    if not await column_exists('players', 'energy'):
        if await column_exists('players', 'current_energy'):
            await conn.execute("ALTER TABLE players RENAME COLUMN current_energy TO energy")
        else:
            await conn.execute("ALTER TABLE players ADD COLUMN energy INTEGER DEFAULT 100")

    # --- players: add main_pet_species ---
    if not await column_exists('players', 'main_pet_species'):
        await conn.execute("ALTER TABLE players ADD COLUMN main_pet_species TEXT")

    # --- player_flags table ---
    if not await table_exists('player_flags'):
        await conn.execute("""
            CREATE TABLE player_flags (
                player_id BIGINT,
                flag TEXT NOT NULL,
                PRIMARY KEY (player_id, flag),
                FOREIGN KEY (player_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        """)

    # --- inventory table (code uses inventory, schema had player_items) ---
    if not await table_exists('inventory'):
        if await table_exists('player_items'):
            await conn.execute("ALTER TABLE player_items RENAME TO inventory")
            # fix column names if needed
            if await column_exists('inventory', 'user_id'):
                await conn.execute("ALTER TABLE inventory RENAME COLUMN user_id TO player_id")
            if await column_exists('inventory', 'item_id') and not await column_exists('inventory', 'qty'):
                await conn.execute("ALTER TABLE inventory RENAME COLUMN quantity TO qty")
        else:
            await conn.execute("""
                CREATE TABLE inventory (
                    player_id BIGINT,
                    item_id TEXT NOT NULL,
                    qty INTEGER DEFAULT 1,
                    PRIMARY KEY (player_id, item_id),
                    FOREIGN KEY (player_id) REFERENCES players(user_id) ON DELETE CASCADE
                )
            """)

    # --- pets: add player_id column (code uses player_id, schema had owner_id) ---
    if not await column_exists('pets', 'player_id'):
        if await column_exists('pets', 'owner_id'):
            await conn.execute("ALTER TABLE pets RENAME COLUMN owner_id TO player_id")
        else:
            await conn.execute("ALTER TABLE pets ADD COLUMN player_id BIGINT REFERENCES players(user_id) ON DELETE CASCADE")
