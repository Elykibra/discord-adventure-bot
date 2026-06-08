# data/explore_events.py
#
# Flavor events that can fire during /explore, themed per zone.
# Each event is a dict with:
#   "type"        : "flavor" | "choice" | "loot_bonus" | "hazard" | "pet_sighting"
#   "weight"      : int  — relative chance (higher = more common)
#   "text"        : str  — narrative description shown to the player
#   "outcome"     : dict — optional stat/item consequence
#       "energy"  : int  (positive = restore, negative = drain)
#       "hp"      : int  (positive = restore, negative = drain, as % of max_hp)
#       "item"    : {"item_id": str, "qty": int}
#   "choices"     : list of choice dicts (only for "choice" type)
#       Each choice: {"label": str, "emoji": str, "outcome": dict, "text": str}
#
# For "pet_sighting" events, the player sees a wild pet but no battle starts —
# just lore and atmosphere. These are purely flavor.

EXPLORE_EVENTS = {

    # ─────────────────────────────────────────────
    # Oakhaven Outpost — The Rotting Pits
    # ─────────────────────────────────────────────
    "oakhavenOutpost_rottingPits": [

        # --- Flavor Events (no consequence) ---
        {
            "type": "flavor",
            "weight": 10,
            "text": "A thick, sulphurous bubble rises from the nearest pit and pops with a wet *schloop*. Whatever is living down there, it isn't in a hurry.",
        },
        {
            "type": "flavor",
            "weight": 10,
            "text": "You spot a rusted boot half-sunken into the tar at the pit's edge. It has been there a long time. You decide not to think about where the other boot went.",
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": "A faint luminescence pulses beneath the surface of the nearest pit — slow, rhythmic, like a heartbeat. The Gloom is alive here.",
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": "Grit Galen's scratched warning marker — a stick with a strip of red cloth — stands at the pit's edge. Someone keeps moving it further back. The pits are growing.",
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": "The air tastes of iron and rot. Your pet presses close to your leg, eyes fixed on the bubbling centre of the largest pit. Something is watching from below.",
        },

        # --- Pet Sightings (atmosphere, no battle) ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": "A Corroder skitters across the far rim of the pit — all jagged shell and twitching antennae. It stops, fixes you with compound eyes, then sinks silently back into the tar. It already knows where you are.",
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": "Something large and dark shifts beneath the surface of the largest pit. For a moment you see the outline of limbs — too many limbs — before the Gloom closes over it.",
        },

        # --- Loot Bonus Events ---
        {
            "type": "loot_bonus",
            "weight": 7,
            "text": "You notice a weathered pack wedged beneath a cracked tar-stone at the pit's edge. Inside: a few battered supplies, still usable.",
            "outcome": {"item": {"item_id": "moss_balm", "qty": 1}},
        },
        {
            "type": "loot_bonus",
            "weight": 5,
            "text": "A cluster of Spiritshard Moss clings to the underside of a tar-crusted rock — rare here, but the Gloom seems to nourish it.",
            "outcome": {"item": {"item_id": "sun_kissed_berries", "qty": 2}},
        },

        # --- Hazard Events (minor negative) ---
        {
            "type": "hazard",
            "weight": 7,
            "text": "You step too close to a bubbling vent. A geyser of scalding sludge erupts without warning, spattering you and your pet.",
            "outcome": {"hp": -8},
        },
        {
            "type": "hazard",
            "weight": 5,
            "text": "The ground shifts underfoot — a sinkhole, barely a metre across, opens just behind you. Your heart hammers as you scramble clear. That was too close.",
            "outcome": {"energy": -1},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": "A blackened Tether Orb bobs near the surface of the shallower pit — Gloom-stained, but possibly still functional. Do you reach in?",
            "choices": [
                {
                    "label": "Reach in",
                    "emoji": "🤿",
                    "text": "You plunge your arm into the tar and grab the orb. It's intact — and now your sleeve is ruined.",
                    "outcome": {"item": {"item_id": "tether_orb", "qty": 1}, "hp": -5},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": "Not worth a faceful of Gloom-tar. You walk on.",
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 5,
            "text": "A low groan echoes from a collapsed section of pit-wall. Something small is trapped in the rubble — you can't tell what. You could try to free it, or the noise might attract something larger.",
            "choices": [
                {
                    "label": "Investigate",
                    "emoji": "🔍",
                    "text": "You clear the rubble and find a startled Pineling, unhurt. It bolts the moment it is free. Small victories.",
                    "outcome": {"energy": 1},
                },
                {
                    "label": "Back away",
                    "emoji": "🚶",
                    "text": "You slip away quietly. Whatever it was, it can sort itself out.",
                    "outcome": {},
                },
            ],
        },
    ],

    # ─────────────────────────────────────────────
    # Oakhaven Wilds
    # ─────────────────────────────────────────────
    "oakhavenWilds": [

        # --- Flavor ---
        {
            "type": "flavor",
            "weight": 10,
            "text": "A shaft of early light breaks through the canopy, catching motes of dust and spores in a slow golden column. Your pet basks in it for a moment.",
        },
        {
            "type": "flavor",
            "weight": 10,
            "text": "A Pineling watches you from a low branch, perfectly still. The moment you look directly at it, it vanishes into the underbrush without a sound.",
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": "A trail of small, three-toed prints cuts across the muddy path ahead. Fresh — made within the last hour. Something was moving quickly.",
        },
        {
            "type": "flavor",
            "weight": 7,
            "text": "The underbrush rattles violently to your left. Then silence. Then, from your right, the same rattling. Something is circling you, but nothing ever appears.",
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": "You find an old Guild marker — the wood warped and moss-covered, the blazed symbol barely legible. This path was regularly patrolled once. It is not now.",
        },

        # --- Pet Sightings ---
        {
            "type": "pet_sighting",
            "weight": 9,
            "text": "A Dewdrop clings to a broad leaf overhead, its translucent body refracting the light into tiny rainbows on the forest floor. It hasn't noticed you.",
        },
        {
            "type": "pet_sighting",
            "weight": 7,
            "text": "Two Pinelings chase each other through the canopy at reckless speed, crashing through branches and raining bark down around you. Neither one acknowledges your presence.",
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 8,
            "text": "You spot a cluster of ripe Sun-Kissed Berries on a low bush just off the path — more than usual, and perfectly ripe.",
            "outcome": {"item": {"item_id": "sun_kissed_berries", "qty": 2}},
        },
        {
            "type": "loot_bonus",
            "weight": 5,
            "text": "A small hollow in the base of an old oak hides a tattered satchel — forgotten by some past traveller. Inside: trail rations, still sealed.",
            "outcome": {"item": {"item_id": "trail_morsels", "qty": 2}},
        },

        # --- Restorative ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": "A natural spring bubbles up through a mossy outcrop nearby. The water is cold and clear. You and your pet rest here for a few minutes.",
            "outcome": {"energy": 1},
        },

        # --- Hazard ---
        {
            "type": "hazard",
            "weight": 6,
            "text": "You misjudge a jump across a muddy streambed and go in up to the knee. Cold, wet, and annoyed, you haul yourself out. Your pet finds this hilarious.",
            "outcome": {"energy": -1},
        },

        # --- Choice ---
        {
            "type": "choice",
            "weight": 6,
            "text": "You come across a large, unusual mushroom ring — perfect circle, no mushrooms broken. Local lore says eating one gives strength. Local lore also says it causes vivid nightmares.",
            "choices": [
                {
                    "label": "Eat one",
                    "emoji": "🍄",
                    "text": "Earthy, bitter, and oddly warm going down. You feel a strange surge of energy... and resolve to sleep with the lantern on tonight.",
                    "outcome": {"energy": 2, "hp": -5},
                },
                {
                    "label": "Leave it alone",
                    "emoji": "🚶",
                    "text": "Some lore is lore for a reason. You step around the ring and continue on your way.",
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 5,
            "text": "A wounded Mossling sits in the middle of the path, favouring its front leg. It growls weakly as you approach — scared, not aggressive. You have a Moss Balm in your pack.",
            "choices": [
                {
                    "label": "Treat its wound",
                    "emoji": "💚",
                    "text": "You kneel slowly, let it sniff your hand, and apply the balm. After a long moment, it licks your wrist and limps off into the undergrowth. That felt good.",
                    "outcome": {"item": {"item_id": "moss_balm", "qty": -1}},  # costs 1 balm
                },
                {
                    "label": "Walk around it",
                    "emoji": "🚶",
                    "text": "You give it a wide berth. It watches you go, growling softly. Sometimes that is all you can do.",
                    "outcome": {},
                },
            ],
        },
    ],
}


def get_zone_events(zone_id: str) -> list:
    """Returns the event list for a given explore zone, or empty list if none defined."""
    return EXPLORE_EVENTS.get(zone_id, [])


# ─────────────────────────────────────────────
# Zone Loot Tables
# Each entry: (item_id, weight)
# ─────────────────────────────────────────────
ZONE_LOOT_TABLES = {
    "oakhavenOutpost_rottingPits": [
        ("trail_morsels",    3),
        ("moss_balm",        2),
        ("tether_orb",       1),
    ],
    "oakhavenWilds": [
        ("sun_kissed_berries", 4),
        ("trail_morsels",      2),
        ("moss_balm",          1),
    ],
    # Whisperwood and beyond added here when towns are built
}

_DEFAULT_LOOT_TABLE = [("sun_kissed_berries", 1)]


def get_zone_loot(zone_id: str) -> tuple[str, int]:
    """Picks a random item from the zone's loot table. Returns (item_id, qty=1)."""
    import random
    table = ZONE_LOOT_TABLES.get(zone_id, _DEFAULT_LOOT_TABLE)
    items = [entry[0] for entry in table]
    weights = [entry[1] for entry in table]
    return random.choices(items, weights=weights, k=1)[0], 1
