# data/casino_games.py
#
# One catalog entry per casino game, keyed the same way as
# casino_game_stats.game_key — the Casino Profile iterates this dict
# to build its Lifetime Performance list rather than hardcoding one
# branch per game. Adding a future game just means adding one entry
# here; the Profile picks it up automatically, no other code changes.
# Mirrors casino_game_stats' own "no migration needed for a new game"
# design at the display layer.

CASINO_GAMES = {
    "blackjack": {"label": "Blackjack", "emoji": "🃏"},
    "slots": {"label": "Slots", "emoji": "🎰"},
    "video_poker": {"label": "Solo Poker", "emoji": "♦️"},
    "baccarat": {"label": "Baccarat", "emoji": "🎴"},
    "poker": {"label": "Poker", "emoji": "♠️"},
    "dungeon": {"label": "Dungeon", "emoji": "🗝️"},
    "chess": {"label": "Chess", "emoji": "⚔️"},
}
