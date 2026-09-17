# migrations/018_add_poker_snapshots.py

async def apply(cursor):
    """
    Migration 018: Adds poker_session_snapshots — a lightweight safety net
    against a bot restart mid-poker-session. Poker's in-progress state
    (cards, pot, whose turn it is) stays in memory only, same as Blackjack
    and the Dungeon. But unlike those, a poker table can hold several
    players' buy-ins at once for a long time, so a crash mid-session risks
    losing real chips, not just an interrupted session.

    This table isn't a full state snapshot — it only tracks each seated
    player's current stack, refreshed at the same checkpoints that already
    touch the database (buy-in, hand resolution, someone leaving). On
    startup, any leftover row means the bot went down without a clean
    close, and every stack in it gets refunded back to its owner's wallet.
    The in-progress hand itself is NOT recoverable — players just get their
    chips back and have to open a new table.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS poker_session_snapshots (
            table_key TEXT PRIMARY KEY,
            stacks JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
