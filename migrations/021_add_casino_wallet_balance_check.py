# migrations/021_add_casino_wallet_balance_check.py

async def apply(cursor):
    """
    Migration 021: Adds a database-level floor on casino_wallets.balance.

    Defense in depth — nothing in the application should ever let a
    wallet go negative (several double-spend races were closed this
    session), but a DB constraint protects against any future bug too,
    known or not. Clamps any existing negative balance to 0 first so
    the constraint can never fail to apply regardless of current data.
    """
    await cursor.execute("UPDATE casino_wallets SET balance = 0 WHERE balance < 0")
    await cursor.execute("""
        ALTER TABLE casino_wallets
        ADD CONSTRAINT casino_wallets_balance_non_negative CHECK (balance >= 0)
    """)
