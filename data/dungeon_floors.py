# data/dungeon_floors.py
# Defines the casino dungeon's floor themes and mob rosters.
#
# The dungeon is designed to eventually run up to floor 99, organized into
# themed bands — adding a new theme later is just appending an entry here,
# no other code changes needed. Each theme is a template with four parts:
#   - mobs: the regular roster, each a named variant with its own floor
#     sub-range (so within a theme, the roster visibly escalates) and a
#     `trait`, a real mechanical hook implemented in the combat loop —
#     not just bigger numbers.
#   - mini_boss: a rare (see MINI_BOSS_CHANCE), tougher substitute for a
#     regular Fight encounter, anywhere in the theme's floor range.
#   - boss: a mandatory encounter that gates the LAST floor of the theme —
#     you must clear it to descend into the next theme.
# Repeating this same four-part shape for a new mob family (goblins, slime,
# trolls, ...) is the whole job of adding a new theme.
#
# Floors past the last defined theme's range reuse it (scaled further)
# until the next theme is added — currently that's floor 41+.

import random

FLOOR_THEMES = [
    {
        "name": "The Flooded Underlevel",
        "floor_range": (1, 15),
        "mobs": [
            {
                "name": "Skeleton", "emoji": "💀", "floor_range": (1, 6),
                "base_hp": 18, "base_damage": (3, 6), "trait": None,
            },
            {
                "name": "Skeleton Archer", "emoji": "🏹", "floor_range": (3, 9),
                "base_hp": 20, "base_damage": (4, 7), "trait": "pierce_dodge",
                # Ranged — ignores the player's dodge chance entirely.
            },
            {
                "name": "Skeletal Mage", "emoji": "🔮", "floor_range": (4, 10),
                "base_hp": 25, "base_damage": (3, 5), "trait": "cursed",
                # Also lands a small guaranteed curse tick each round, dodge or not.
            },
            {
                "name": "Armored Skeleton", "emoji": "🛡️", "floor_range": (5, 11),
                "base_hp": 40, "base_damage": (3, 5), "trait": "armored",
                # Takes 25% less damage from the player.
            },
            {
                "name": "Giant Skeleton", "emoji": "🦴", "floor_range": (8, 13),
                "base_hp": 55, "base_damage": (10, 15), "trait": "slow",
                # Only attacks every other round — hits hard, but rarely.
            },
            {
                "name": "Dullahan", "emoji": "🎃", "floor_range": (11, 15),
                "base_hp": 115, "base_damage": (7, 12), "trait": "execute",
                # Deals 75% bonus damage if the player is already below 30% HP.
            },
        ],
        "mini_boss": {
            "name": "Bone Collector", "emoji": "☠️", "hp": 90, "damage": (8, 13), "trait": None,
            "loot_multiplier": 2.5,
            "description": "A hulking mass of fused skeletal remains, dragging a cart of bones.",
        },
        "boss": {
            "name": "The Drowned King", "emoji": "👑", "hp": 220, "damage": (12, 20), "trait": "execute",
            "loot_multiplier": 5,
            "description": "Ruler of the flooded crypts, risen once more to guard the way down.",
        },
    },
    {
        "name": "The Goblin Warren",
        "floor_range": (16, 40),
        "mobs": [
            {
                "name": "Goblin", "emoji": "👺", "floor_range": (16, 23),
                "base_hp": 45, "base_damage": (6, 10), "trait": None,
            },
            {
                "name": "Goblin Slinger", "emoji": "🪨", "floor_range": (19, 28),
                "base_hp": 50, "base_damage": (7, 11), "trait": "pierce_dodge",
            },
            {
                "name": "Goblin Brute", "emoji": "🪓", "floor_range": (24, 33),
                "base_hp": 95, "base_damage": (8, 13), "trait": "armored",
            },
            {
                "name": "Hobgoblin Berserker", "emoji": "😡", "floor_range": (29, 40),
                "base_hp": 150, "base_damage": (18, 26), "trait": "slow",
            },
        ],
        "mini_boss": {
            "name": "Goblin Shaman", "emoji": "🧙", "hp": 120, "damage": (9, 15), "trait": "pierce_dodge",
            "loot_multiplier": 2.5,
            "description": "Hexes fly from its staff, impossible to simply step around.",
        },
        "boss": {
            "name": "The Goblin Warlord", "emoji": "🏆", "hp": 260, "damage": (16, 24), "trait": "execute",
            "loot_multiplier": 5,
            "description": "He didn't lead this warren by mercy — he finishes off the weak.",
        },
    },
    # Ideas noted for the next themes (floors 41-70, 71-99): slime family
    # (a "split" trait — dividing into weaker copies on hit?) and a troll
    # family (heavy "slow" hitters with a "regenerate" trait). Same
    # four-part template as above once we get there.
]

MOB_SCALING_PER_FLOOR = 0.05  # mild extra scaling across a mob's OWN floor range, on top of its base stats
MINI_BOSS_CHANCE = 0.12       # chance a Fight roll substitutes the theme's mini_boss instead

# How many rooms must be cleared to descend a floor. This is a separate
# band structure from FLOOR_THEMES on purpose — pacing (how grindy a floor
# is) doesn't have to line up with where the flavor/mob content changes.
# Covers the full 99-floor arc even though FLOOR_THEMES only has content
# defined up to floor 40 so far.
ROOM_COUNT_BANDS = [
    {"floor_range": (1, 15), "rooms_per_floor": 3},
    {"floor_range": (16, 40), "rooms_per_floor": 5},
    {"floor_range": (41, 70), "rooms_per_floor": 7},
    {"floor_range": (71, 99), "rooms_per_floor": 10},
]

ROOM_EVENTS = [
    {"text": "💰 You stumble across a stash left by a previous adventurer.", "type": "loot", "value": (15, 40)},
    {"text": "🕯️ A flickering shrine restores some of your strength.", "type": "heal", "value": 10},
    {"text": "🌀 The air here feels wrong, but nothing happens... this time.", "type": "flavor", "value": 0},
    {"text": "📦 A sealed chest springs open on its own, spilling chips.", "type": "loot", "value": (25, 55)},
]
EVENT_CHANCE = 0.18


def get_theme_for_floor(floor: int) -> dict:
    for theme in FLOOR_THEMES:
        lo, hi = theme["floor_range"]
        if lo <= floor <= hi:
            return theme
    return FLOOR_THEMES[-1]


def get_rooms_per_floor(floor: int) -> int:
    for band in ROOM_COUNT_BANDS:
        lo, hi = band["floor_range"]
        if lo <= floor <= hi:
            return band["rooms_per_floor"]
    return ROOM_COUNT_BANDS[-1]["rooms_per_floor"]


def is_boss_floor(floor: int) -> bool:
    theme = get_theme_for_floor(floor)
    return floor == theme["floor_range"][1]


def get_boss_for_floor(floor: int) -> dict:
    return get_theme_for_floor(floor)["boss"]


def roll_mob_for_floor(floor: int) -> dict:
    """Picks a random mob eligible for this floor (its own floor_range must include it),
    lightly scaled by how deep into ITS OWN range the floor is."""
    theme = get_theme_for_floor(floor)

    eligible = [m for m in theme["mobs"] if m["floor_range"][0] <= floor <= m["floor_range"][1]]
    if not eligible:
        # Floor past every mob's defined range (deep-reuse of the last theme) —
        # fall back to the toughest mob in the roster.
        eligible = [max(theme["mobs"], key=lambda m: m["base_hp"])]

    base_mob = random.choice(eligible)
    mob_lo, mob_hi = base_mob["floor_range"]
    span = max(1, mob_hi - mob_lo)
    progress = max(0, min(1, (floor - mob_lo) / span))
    scale = 1 + (progress * MOB_SCALING_PER_FLOOR)

    dmg_lo, dmg_hi = base_mob["base_damage"]
    return {
        "name": base_mob["name"],
        "emoji": base_mob["emoji"],
        "hp": int(base_mob["base_hp"] * scale),
        "damage": (max(1, int(dmg_lo * scale)), max(1, int(dmg_hi * scale))),
        "trait": base_mob["trait"],
        "loot_multiplier": 1.0,
        "theme": theme["name"],
    }


def maybe_roll_mini_boss(floor: int) -> dict | None:
    """With MINI_BOSS_CHANCE odds, returns this floor's theme mini_boss instead of a regular mob."""
    theme = get_theme_for_floor(floor)
    if "mini_boss" not in theme or random.random() >= MINI_BOSS_CHANCE:
        return None
    return dict(theme["mini_boss"], theme=theme["name"])


def maybe_roll_event() -> dict | None:
    if random.random() < EVENT_CHANCE:
        return random.choice(ROOM_EVENTS)
    return None
