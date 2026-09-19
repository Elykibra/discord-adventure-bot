# migrations/022_add_casino_game_stats.py

async def apply(cursor):
    """
    Migration 022: Adds casino_game_stats — one shared, per-game lifetime
    stats table for the whole casino (Blackjack, Slots, Solo Poker,
    Baccarat, Poker, Dungeon, and any future game), replacing the
    Poker-only poker_stats table.

    Keyed by (user_id, game_key) rather than one table per game, so a
    future game just starts writing rows under a new game_key — no
    migration needed to "add" it. `extra` is a schemaless JSONB bucket for
    anything game-specific (e.g. Poker's biggest_pot_won, preserved below)
    that doesn't warrant its own column — same reasoning, no migration
    needed to add a new counter later either.

    Backfills from poker_stats: hands_played, hands_won, and net_chips
    migrate over exactly (that data exists as stored). total_wagered and
    total_won can't be reconstructed — poker_stats only ever stored a
    running net (won minus contributed, already combined per hand), with
    no way to split that back into historical gross wagered/won — so
    those start at 0 and only reflect Poker activity from this migration
    forward. poker_stats and poker_hand_history are left in place,
    unused but harmless; nothing here drops them.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_game_stats (
            user_id BIGINT NOT NULL,
            game_key TEXT NOT NULL,
            plays INTEGER NOT NULL DEFAULT 0,
            wins INTEGER NOT NULL DEFAULT 0,
            total_wagered BIGINT NOT NULL DEFAULT 0,
            total_won BIGINT NOT NULL DEFAULT 0,
            net_chips BIGINT NOT NULL DEFAULT 0,
            biggest_win BIGINT NOT NULL DEFAULT 0,
            last_played_at TIMESTAMPTZ,
            extra JSONB NOT NULL DEFAULT '{}',
            PRIMARY KEY (user_id, game_key)
        )
    """)

    await cursor.execute("""
        INSERT INTO casino_game_stats (user_id, game_key, plays, wins, net_chips, extra)
        SELECT user_id, 'poker', hands_played, hands_won, net_chips,
               jsonb_build_object('biggest_pot_won', biggest_pot_won)
        FROM poker_stats
        ON CONFLICT (user_id, game_key) DO NOTHING
    """)
