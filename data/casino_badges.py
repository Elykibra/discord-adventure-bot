# data/casino_badges.py
#
# One catalog entry per casino badge, keyed the same way casino_badges.
# badge_key is stored. Mirrors data/casino_games.py's "one dict, iterate
# everywhere" pattern — adding a 9th badge later is just a new entry
# here, no migration needed (casino_badges has no badge-specific
# columns, see migrations/023).
#
# Each condition is evaluated against the exact shapes ProfileView.create()
# already builds: `wallet` (a casino_wallets row dict) and `all_stats`
# (game_key -> casino_game_stats row dict, one entry per CASINO_GAMES key,
# zeroed for games never played). No badge here needs data beyond what's
# already fetched for the Profile.
#
# `all_stats` may be either the raw get_all_game_stats() result (only rows
# that exist, i.e. games with at least one play) or ProfileView's fully
# zero-defaulted version (one entry per CASINO_GAMES key) — every
# condition below is written to give the same answer either way.

from data.casino_games import CASINO_GAMES


def _lifetime_total(all_stats, field):
    return sum(stats[field] for stats in all_stats.values())


def _games_played(all_stats):
    return sum(1 for stats in all_stats.values() if stats["plays"] > 0)


def _best_win_rate(all_stats, min_plays):
    best = 0.0
    for stats in all_stats.values():
        if stats["plays"] < min_plays:
            continue
        best = max(best, stats["wins"] / stats["plays"])
    return best


CASINO_BADGES = {
    "high_roller": {
        "name": "High Roller", "emoji": "🎰",
        "description": "Wager 50,000 chips lifetime, across every game.",
        "condition": lambda wallet, all_stats: _lifetime_total(all_stats, "total_wagered") >= 50_000,
    },
    "chip_baron": {
        "name": "Chip Baron", "emoji": "💰",
        "description": "Wager 250,000 chips lifetime, across every game.",
        "condition": lambda wallet, all_stats: _lifetime_total(all_stats, "total_wagered") >= 250_000,
    },
    "century_club": {
        "name": "Century Club", "emoji": "💯",
        "description": "Play 100 games lifetime, any game, combined.",
        "condition": lambda wallet, all_stats: _lifetime_total(all_stats, "plays") >= 100,
    },
    "jack_of_all_trades": {
        "name": "Jack of All Trades", "emoji": "🃏",
        "description": "Play all six casino games at least once.",
        "condition": lambda wallet, all_stats: _games_played(all_stats) >= len(CASINO_GAMES),
    },
    "on_a_heater": {
        "name": "On a Heater", "emoji": "🔥",
        "description": "Reach +10,000 net chips lifetime, across every game.",
        "condition": lambda wallet, all_stats: _lifetime_total(all_stats, "net_chips") >= 10_000,
    },
    "daily_grinder": {
        "name": "Daily Grinder", "emoji": "🌅",
        "description": "Reach a 7-day daily streak.",
        "condition": lambda wallet, all_stats: wallet["daily_streak"] >= 7,
    },
    "casino_royalty": {
        "name": "Casino Royalty", "emoji": "👑",
        "description": "Reach a 30-day daily streak.",
        "condition": lambda wallet, all_stats: wallet["daily_streak"] >= 30,
    },
    "sharpshooter": {
        "name": "Sharpshooter", "emoji": "🎯",
        "description": "Hit a 60%+ win rate in a single game with at least 20 plays in it.",
        "condition": lambda wallet, all_stats: _best_win_rate(all_stats, min_plays=20) >= 0.6,
    },
}


def format_new_badge_field(new_badge_keys):
    """Formats a Discord embed field (name, value) announcing newly-earned
    badges, or None if the list is empty. Callers that already build a
    result embed just do:
        field = format_new_badge_field(new_badges)
        if field:
            embed.add_field(name=field[0], value=field[1], inline=False)
    """
    if not new_badge_keys:
        return None
    lines = []
    for key in new_badge_keys:
        badge = CASINO_BADGES[key]
        lines.append(f"{badge['emoji']} **{badge['name']}** — {badge['description']}")
    title = "🎖️ New Badge Unlocked!" if len(new_badge_keys) == 1 else "🎖️ New Badges Unlocked!"
    return title, "\n".join(lines)
