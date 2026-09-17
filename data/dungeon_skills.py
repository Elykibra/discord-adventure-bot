# data/dungeon_skills.py
# In-run level-up skills — the Risk of Rain 2 / Gunfire Reborn / Muck style
# "pick one of a few random upgrades" pool. These are entirely separate
# from permanent progression: everything here resets when a dungeon run
# ends, win or lose. Most stack the more times you pick them; a few are
# one-off ("unique") effects that stop being offered once owned.

import random

UNIQUE_SKILLS = {"second_wind"}  # binary effects — picking twice adds nothing, so don't re-offer

SKILL_POOL = {
    "iron_will": {
        "name": "Iron Will", "emoji": "🛡️", "type": "max_hp", "value": 20,
        "description": "+20 Max HP, and heals you for that much now.",
    },
    "bloodlust": {
        "name": "Bloodlust", "emoji": "🩸", "type": "lifesteal_pct", "value": 0.15,
        "description": "+15% lifesteal on all damage you deal.",
    },
    "adrenaline": {
        "name": "Adrenaline", "emoji": "⚡", "type": "damage_pct", "value": 0.20,
        "description": "+20% damage dealt.",
    },
    "quick_hands": {
        "name": "Quick Hands", "emoji": "🖐️", "type": "extra_hits", "value": 1,
        "description": "+1 hit per combat round.",
    },
    "lucky_charm": {
        "name": "Lucky Charm", "emoji": "🍀", "type": "loot_pct", "value": 0.25,
        "description": "+25% chips from fights and searches.",
    },
    "evasive": {
        "name": "Evasive", "emoji": "💨", "type": "dodge_pct", "value": 0.10,
        "description": "+10% chance to dodge incoming damage entirely.",
    },
    "field_medic": {
        "name": "Field Medic", "emoji": "❤️‍🩹", "type": "regen_per_room", "value": 5,
        "description": "Heal 5 HP after every room.",
    },
    "second_wind": {
        "name": "Second Wind", "emoji": "🌬️", "type": "second_wind", "value": 1,
        "description": "The first time you'd die this run, survive with 1 HP instead.",
    },
}

DODGE_CAP = 0.75  # never let stacked dodge approach guaranteed invincibility


def draw_skill_choices(owned_skills: list, count: int = 3) -> list:
    """Picks up to `count` distinct skill keys, excluding unique skills already owned."""
    owned_unique = {s for s in owned_skills if s in UNIQUE_SKILLS}
    pool = [key for key in SKILL_POOL if key not in owned_unique]
    return random.sample(pool, min(count, len(pool)))
