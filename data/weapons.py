# data/weapons.py
# Defines every weapon the casino armory sells. Damage is stored as a
# (low, high) tuple so both the armory display and the dungeon's
# round-by-round combat resolution read from the same source of truth.
#
# Weapons are grouped into tiers so future additions have a clear cost/power
# band to slot into instead of picking numbers from scratch each time.
# Higher tier should mean a genuinely stronger pick (validated empirically
# via cogs/views/dungeon.py's combat math, not just eyeballed) — a weapon
# that costs more but performs worse defeats the point of the armory.

STARTER_WEAPON = "pistol"

WEAPON_TIERS = {
    1: {"name": "Starter", "cost_band": "Free"},
    2: {"name": "Standard", "cost_band": "~1,000-1,500 chips"},
    3: {"name": "Advanced", "cost_band": "~1,500-2,000 chips"},
    4: {"name": "Rare", "cost_band": "~2,500-4,000 chips"},
}

WEAPON_CATALOG = {
    "pistol": {
        "name": "Pistol", "emoji": "🔫", "tier": 1, "cost": 0,
        "damage": (10, 16), "hits_per_round": 1, "trait": None,
        "description": "Reliable sidearm. Balanced damage, no frills. Everyone starts with this.",
    },
    "smg": {
        "name": "SMG", "emoji": "🔱", "tier": 2, "cost": 1200,
        "damage": (4, 7), "hits_per_round": 3, "trait": None,
        "description": "Sprays multiple weaker hits — scales well with future fire-rate upgrades.",
    },
    "shotgun": {
        "name": "Shotgun", "emoji": "💥", "tier": 3, "cost": 1500,
        "damage": (20, 30), "hits_per_round": 1, "trait": None,
        "description": "Heavy hitting, but less consistent.",
    },
    "vampiric_blade": {
        "name": "Vampiric Blade", "emoji": "🗡️", "tier": 4, "cost": 3000,
        "damage": (18, 24), "hits_per_round": 1, "trait": "lifesteal",
        "trait_value": 0.40,
        "description": "Melee weapon that heals you for a portion of the damage it deals.",
    },
}


def format_damage_range(weapon: dict) -> str:
    lo, hi = weapon["damage"]
    return f"{lo}-{hi}"


def trait_display(weapon: dict) -> str:
    if weapon["trait"] == "lifesteal":
        pct = int(weapon.get("trait_value", 0) * 100)
        return f"Lifesteal ({pct}%)"
    return "None"


def tier_display(weapon: dict) -> str:
    tier = WEAPON_TIERS[weapon["tier"]]
    return f"Tier {weapon['tier']} — {tier['name']}"
