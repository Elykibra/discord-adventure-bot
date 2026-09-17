# data/permanent_stats.py
# Permanent, between-run dungeon upgrades — bought with chips, never reset.
# Each stat feeds a run-state field that already exists because of the
# in-run skill system (max_hp, dodge_chance, loot_bonus), so permanent
# levels just raise the starting value instead of being a separate system.

MAX_STAT_LEVEL = 10

PERMANENT_STATS = {
    "vitality": {
        "name": "Vitality", "emoji": "❤️",
        "description": "Permanently raises your starting Max HP in the dungeon.",
        "value_per_level": 10,
        "unit": "HP",
    },
    "luck": {
        "name": "Luck", "emoji": "🍀",
        "description": "Permanently raises your dodge chance in the dungeon.",
        "value_per_level": 0.02,
        "unit": "% dodge",
    },
    "greed": {
        "name": "Greed", "emoji": "💰",
        "description": "Permanently raises chips earned from dungeon fights and searches.",
        "value_per_level": 0.05,
        "unit": "% loot",
    },
}

BASE_UPGRADE_COST = 300
COST_GROWTH_PER_LEVEL = 1.4  # each level costs 40% more than the last


def cost_for_next_level(current_level: int) -> int:
    """Cost to go from current_level to current_level + 1."""
    return int(BASE_UPGRADE_COST * (COST_GROWTH_PER_LEVEL ** current_level))


def effect_at_level(stat_key: str, level: int):
    return PERMANENT_STATS[stat_key]["value_per_level"] * level


def format_effect(stat_key: str, level: int) -> str:
    stat = PERMANENT_STATS[stat_key]
    value = effect_at_level(stat_key, level)
    if stat["unit"] == "HP":
        return f"+{int(value)} HP"
    return f"+{value:.0%}" if "%" in stat["unit"] else f"+{value}"
