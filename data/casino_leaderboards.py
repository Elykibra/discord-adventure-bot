# data/casino_leaderboards.py
#
# One catalog entry per leaderboard category — same "one dict, iterate
# everywhere" pattern as CASINO_GAMES/CASINO_BADGES/COSMETIC_CATEGORIES.
# Pure display metadata, no SQL here: `list_method`/`rank_method` name
# the cogs/database.py methods LeaderboardView calls via getattr(), so
# adding a 7th leaderboard later is a new method pair here plus one
# entry — no new view code.
#
# `unit` is how build_embed() formats a row's value: "chips" gets
# thousands separators and a +/- sign where the category can go
# negative, "count" is a plain integer noun ("7 badges"), "days" is a
# plain integer noun ("14 days").

LEADERBOARD_CATEGORIES = {
    "richest": {
        "label": "Richest", "emoji": "💰", "unit": "chips", "noun": "chips", "signed": False,
        "list_method": "get_richest_players", "rank_method": "get_richest_players_rank",
    },
    "wagered": {
        "label": "Biggest Lifetime Wagered", "emoji": "📈", "unit": "chips", "noun": "chips", "signed": False,
        "list_method": "get_most_wagered_players", "rank_method": "get_most_wagered_players_rank",
    },
    "biggest_win": {
        "label": "Biggest Single Win", "emoji": "🏆", "unit": "chips_with_game", "noun": "chips", "signed": False,
        "list_method": "get_biggest_win_players", "rank_method": "get_biggest_win_players_rank",
    },
    "badges": {
        "label": "Most Badges", "emoji": "🎖️", "unit": "count", "noun": "badge", "signed": False,
        "list_method": "get_most_badges_players", "rank_method": "get_most_badges_players_rank",
    },
    "net_profit": {
        "label": "Best Net Profit", "emoji": "🔥", "unit": "chips", "noun": "chips", "signed": True,
        "list_method": "get_best_net_profit_players", "rank_method": "get_best_net_profit_players_rank",
    },
    "streak": {
        "label": "Longest Daily Streak", "emoji": "🌅", "unit": "count", "noun": "day", "signed": False,
        "list_method": "get_longest_streak_players", "rank_method": "get_longest_streak_players_rank",
    },
}
