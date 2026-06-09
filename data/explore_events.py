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
    # Outpost Wilds
    # ─────────────────────────────────────────────
    "outpostWilds": [

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

    # ─────────────────────────────────────────────
    # Weeping Chasm — The Chasm's Edge
    # ─────────────────────────────────────────────
    "weeping_chasm": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The chasm exhales cold air in a slow, rhythmic pulse. "
                "Your pet refuses to approach the edge. "
                "It doesn't move until the pulse stops."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "A Guild marker post — cracked, the rune barely holding. "
                "Someone scratched a tally into the wood. Thirty-seven marks. "
                "You don't know what they were counting."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "A sound rises from below. Not a creature — more like a voice, "
                "too deep and too slow to understand. "
                "It stops the moment you move."
            ),
        },
        {
            "type": "flavor",
            "weight": 7,
            "text": (
                "Near the Whispering Stones — a cluster of rounded rocks at the "
                "sealed section — the air hums faintly. Guild records say this is "
                "where the first ward was placed. Whatever it was holding, it's still holding."
            ),
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": (
                "The mist curls upward around your ankles. "
                "Nothing attacks. Something is just checking.",
            ),
            "time": "night",
        },
        {
            "type": "flavor",
            "weight": 5,
            "text": (
                "The breathing from below changes rhythm. Slower. Deeper. "
                "Your pet goes completely still and won't move until it resumes."
            ),
            "time": "night",
        },

        # --- Pet Sightings ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "A Corroder sits at the chasm's lip, staring down into the dark "
                "instead of at you. It doesn't react to your presence. "
                "It seems drawn to the source."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": (
                "Something pale drifts upward from the chasm on the cold thermal — "
                "translucent, barely there, gone before you can focus on it."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "The east wall of the Chasm is covered in thick, dark silk from rim "
                "to rock face. Something enormous spun this overnight. "
                "The webbing is still faintly warm."
            ),
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "A cold updraft hits without warning — disorienting, wrong. "
                "Not wind. An exhale from below. Your pet stumbles. You catch it."
            ),
            "outcome": {"hp": -8},
        },
        {
            "type": "hazard",
            "weight": 6,
            "text": (
                "The ground near the Tainted Ledge shifts. A crack opens, "
                "runs three feet, stops. You step back slowly. "
                "The crack doesn't close."
            ),
            "outcome": {"energy": -1},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 5,
            "text": (
                "A Guild emergency cache bolted to a post near the sealed section. "
                "Still stocked. Someone kept resupplying this long after the post was abandoned."
            ),
            "outcome": {"item": {"item_id": "zone_loot", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": (
                "A sealed Guild journal is wedged in a crack near the Tainted Ledge. "
                "It's been here a while — the wax seal is intact but the cover is "
                "warped from cold. You could pry it open."
            ),
            "choices": [
                {
                    "label": "Pry it open",
                    "emoji": "📖",
                    "text": (
                        "The seal breaks. Inside: field notes, precise until the last few pages "
                        "where the handwriting changes. You take the fragment. "
                        "The Gloom around you feels slightly heavier."
                    ),
                    "outcome": {"item": {"item_id": "lore_fragment", "qty": 1}, "gloom_tick": 5},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": "Some things stay sealed for a reason. You walk away.",
                    "outcome": {},
                },
            ],
        },

        # --- Apex Lore Events (Chasmbane + Veilmother) ---
        # These are atmosphere/scare events — no battle, no capture.
        # Full rank-gated encounter logic tagged for later.
        {
            "type": "hazard",
            "weight": 3,
            "text": (
                "The mist stops. All of it — in an instant. The chasm goes completely "
                "silent. Something at the rim of your vision, near the base of the wall, "
                "is large enough that your mind refuses to measure it. "
                "It isn't looking at you. Then it is. "
                "The Gloom floods your senses before you consciously decide to back away."
            ),
            "outcome": {"gloom_tick": 15},
        },
        {
            "type": "pet_sighting",
            "weight": 2,
            "time": "night",
            "text": (
                "The east wall moves. Not shifts — moves, deliberately, slowly. "
                "A section of what you thought was webbing detaches from the rock face "
                "and redistributes itself further up. The scale of it doesn't make sense "
                "until you find a marker post for reference. "
                "You stop using the marker post for reference."
            ),
        },
    ],

    # ─────────────────────────────────────────────
    # Mirefields — The Mire Path
    # ─────────────────────────────────────────────
    "mirefields": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The path disappears under two inches of brown water. You can't tell if it "
                "continues forward or if you've already stepped off it."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "A territorial bog creature bursts from the reeds, takes one look at you "
                "and your pet, and retreats. You're bigger than its usual targets. Barely."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "The ruins of a signpost poke out of the muck — three arrows pointing "
                "different directions. None of the place names are legible. Someone has "
                "tried to scratch new ones in. You can't read those either."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "Sable's trail markers — knotted reed bundles tied to stakes — are the "
                "only reliable guide here. You spot one and orient yourself. Without "
                "these, you'd be walking in circles."
            ),
        },
        {
            "type": "flavor",
            "weight": 5,
            "text": (
                "The fog sits low and still. Sound travels oddly — a splash from somewhere "
                "to your left sounds close, then far, then close again. Nothing surfaces."
            ),
            "time": "night",
        },

        # --- Pet Sightings ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "A Murkback watches you from a half-submerged log, perfectly still. "
                "It's not interested in fighting. It's waiting for you to leave its territory."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": (
                "Something moves under the surface in the deeper section of the mire. "
                "Not small. It tracks alongside you for about a minute, then veers off "
                "without surfacing."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "A Pallefin skims the surface of a still pool just off the path — barely "
                "disturbing the water. It's gone before you can focus on it."
            ),
            "time": "day",
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "Something low and slow moves through the reeds. You can't see it clearly. "
                "Just the reeds parting and settling. It doesn't come closer."
            ),
            "time": "night",
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "You sink into a soft patch up to your knee. Extracting yourself takes "
                "time and costs you. Your pet watches from dry ground with no sympathy."
            ),
            "outcome": {"energy": -1},
        },
        {
            "type": "hazard",
            "weight": 6,
            "text": (
                "A bog creature you didn't see charges from the shallow water — a glancing "
                "hit. It was more startled than aggressive, but that doesn't help your ribs much."
            ),
            "outcome": {"hp": -10},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": (
                "You spot a waterlogged pack half-buried in the reed bed — old, probably "
                "from the waystation days. Still has something inside worth keeping."
            ),
            "outcome": {"item": {"item_id": "zone_loot", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 7,
            "text": (
                "A section of the old crossroads road is visible just beneath the water — "
                "stone paving, still intact. You could follow it deeper into the mire, "
                "or stick to Sable's markers."
            ),
            "choices": [
                {
                    "label": "Follow the old road",
                    "emoji": "🗺️",
                    "text": (
                        "The paving holds for a while. Then it doesn't. You backtrack "
                        "before it gets worse — but not before finding something."
                    ),
                    "outcome": {"item": {"item_id": "zone_loot", "qty": 1}, "energy": -1},
                },
                {
                    "label": "Stick to the markers",
                    "emoji": "🌿",
                    "text": "Smart. You follow Sable's reeds and stay dry. Nothing happens.",
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
    "outpostWilds": [
        ("sun_kissed_berries", 4),
        ("trail_morsels",      2),
        ("moss_balm",          1),
    ],
    "weeping_chasm": [
        ("moss_balm",     3),
        ("tether_orb",    3),
        ("trail_morsels", 2),
    ],
    "mirefields": [
        ("trail_morsels",    4),
        ("mire_balm",        3),
        ("bog_reed_bundle",  3),
        ("tether_orb",       1),
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
