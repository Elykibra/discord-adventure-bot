# migrations/025_add_chess_games.py

async def apply(cursor):
    """
    Migration 025: Adds chess_games — one row per player's ACTIVE game
    against the AI (user_id is the primary key, so a player can only
    have one game in progress at a time; no game_id needed).

    Unlike every other casino game, a chess game can run long, and this
    bot redeploys often — an in-memory-only game would silently vanish
    on the next deploy. fen is python-chess's own full board
    serialization, checkpointed here after every move pair, so a game
    survives a restart and resumes exactly where it left off.
    """
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS chess_games (
            user_id BIGINT PRIMARY KEY,
            fen TEXT NOT NULL,
            bet INTEGER NOT NULL,
            move_history TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
