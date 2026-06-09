# data/remnants.py
# Remnants — Points of Interest found between towns.
#
# Remnants are optional locations discovered while traveling between towns.
# They are not full towns — no inn, no shops — but they can have:
#   - NPCs (quest givers, lore, merchants)
#   - Explore zones (unique encounters)
#   - Quest hooks
#   - Unique items or drops
#
# "between" defines which two towns flank this remnant on the road.
# "availability" can restrict when the remnant is accessible (day/night/all).
# "gloom_level" — if set, all battles here start with this Gloom % preloaded.

REMNANTS = {

    # =========================================================================
    # ROAD: Oakhaven Outpost ↔ Whisperwood Grove
    # =========================================================================

    "weeping_chasm": {
        "id": "weeping_chasm",
        "name": "The Weeping Chasm",
        "emoji": "🕳️",
        "between": ["oakhavenOutpost", "whisperwoodGrove"],
        "connections": {
            "oakhavenOutpost": "Oakhaven Outpost",
            "mirefields": "Mirefields",
        },
        # Per-route energy costs. Falls back to ACTION_COSTS["travel"]["energy"] if not set.
        # Going back to Oakhaven is slightly cheaper (familiar road).
        # Pushing forward into the Mirefields costs more.
        "connection_costs": {
            "oakhavenOutpost": 8,
            "mirefields": 14,
        },
        # Rest at this Remnant: energy restore only, no HP, no time skip.
        "rest_energy": 20,
        "rest_flavor": (
            "You find a stable outcrop of rock away from the Chasm's edge and sit down. "
            "The cold mist is unsettling, but stillness returns to your limbs. "
            "Warden Orin nods from his post without a word."
        ),
        "availability": "all",
        "gloom_level": 25,
        "description_day": (
            "A jagged tear in the earth stretches across the road, as if the land itself "
            "was ripped open long ago. A faint, cold mist rises from below, carrying with it "
            "the distant sound of something — breathing. Guild records mark this as the site "
            "where The Gloom first breached the surface world."
        ),
        "description_night": (
            "At night, the Chasm seems to exhale — a rhythmic pulse of cold air that makes "
            "the trees lean away. The mist thickens into something almost visible, and the "
            "darkness below feels aware of you."
        ),
        "lore": (
            "This is where it began. Centuries ago, a crack formed in the bedrock and the "
            "first tendrils of The Gloom seeped upward. The Guild sealed what they could, "
            "but the scar never healed."
        ),
        "npcs": {
            "chasm_warden": {
                "name": "Warden Orin",
                "role": "Guild Warden",
                "emoji": "🛡️",
                "availability": "day",
                "dialogue": {
                    "default": (
                        "This is as close as most people get. The Chasm draws Gloom-Touched "
                        "creatures — they're drawn to the source. I keep watch so travelers "
                        "can pass safely. Mostly."
                    ),
                    "lore_prompt": (
                        "The records say The Gloom first surfaced here. I believe it. "
                        "Some nights I can feel it thinking."
                    ),
                }
            }
        },
        "services": {
            "explore_zone": "weeping_chasm",
        },
    },

    "mirefields": {
        "id": "mirefields",
        "name": "The Mirefields",
        "emoji": "🌫️",
        "between": ["oakhavenOutpost", "whisperwoodGrove"],
        "connections": {
            "weeping_chasm": "Weeping Chasm",
            "whisperwoodGrove": "Whisperwood Grove",
        },
        # Per-route energy costs.
        # Backtracking to the Chasm is uphill and tiring.
        # Pushing through to Whisperwood requires navigating thick boggy terrain.
        "connection_costs": {
            "weeping_chasm": 12,
            "whisperwoodGrove": 14,
        },
        # Rest at this Remnant: energy restore only, no HP, no time skip.
        "rest_energy": 20,
        "rest_flavor": (
            "Sable tosses you a strip of dried bark to chew on and points to a dry log. "
            "You sit in silence while the fog drifts past. "
            "It's not comfortable, but it's enough to push on."
        ),
        "availability": "all",
        "gloom_level": 8,
        "description_day": (
            "A stretch of dense, boggy terrain where the road becomes little more than a "
            "muddy suggestion. Twisted undergrowth crowds the path and the air smells of "
            "damp earth and rot. The creatures here are territorial and aggressive — not "
            "Gloom-touched, just mean. The ruins of an old crossroads camp can be spotted "
            "through the fog, long since reclaimed by the mire."
        ),
        "description_night": (
            "The fog thickens after dark, swallowing what little visibility remained. "
            "Sounds carry strangely through the mire — snapping branches, low growls, "
            "the occasional splash of something moving through the water. "
            "Not the place to stop and rest."
        ),
        "lore": (
            "Once a busy waystation for traders moving between Oakhaven and the forests "
            "beyond. When the road fell out of use, the mire moved in. "
            "A few stubborn souls still pass through — and a few still live here."
        ),
        "npcs": {
            "sable": {
                "name": "Sable",
                "role": "Bog Trapper",
                "emoji": "🪤",
                "availability": "all",
                "dialogue": {
                    "default": (
                        "You lost? Most people don't come through here by choice. "
                        "I've got supplies if you need them — nothing fancy, but it'll keep you alive."
                    ),
                    "night": (
                        "You're braver than most, traveling through here at night. "
                        "Or dumber. Hard to tell. Watch your step — the mire shifts after dark."
                    ),
                    "sell": "Take what you need and move on. I don't do small talk.",
                }
            }
        },
        "services": {
            "explore_zone": "mirefields",
            "shop": True,
            "shop_items": ["moss_balm", "trail_morsels", "tether_orb"],
        },
    },

    # =========================================================================
    # ROAD: Whisperwood Grove ↔ Sunstone Oasis
    # =========================================================================

    "glade_of_whispers": {
        "id": "glade_of_whispers",
        "name": "The Glade of Whispers",
        "emoji": "✨",
        "between": ["whisperwoodGrove", "sunstoneOasis"],
        "connections": {
            "whisperwoodGrove": "Whisperwood Grove",
            "sunstoneOasis": "Sunstone Oasis",
        },
        "availability": "all",
        "gloom_level": 0,
        "description_day": (
            "A small, perfectly circular glade where sunlight filters through a natural "
            "opening in the canopy. The air hums faintly — not with danger, but with something "
            "older and calmer. Flowers here bloom year-round, and the grass is always soft. "
            "Adventurers often stop to rest."
        ),
        "description_night": (
            "At night the glade is lit by the soft glow of Moonpetal flowers that only "
            "bloom here after dark. The humming grows quieter but doesn't stop. "
            "It feels like the forest is holding its breath — in a good way."
        ),
        "lore": (
            "One of the few places in Aethelgard where the Gloom has never taken hold. "
            "Scholars believe a Great Spirit once rested here, leaving a lasting impression "
            "on the land. Pets recover faster in this glade."
        ),
        "npcs": {},
        "services": {
            "rest": {
                "type": "glade",
                "cost": 0,
                "energy_restore_percent": 25,
                "health_restore_percent": 50,  # Natural healing, free
            }
        },
    },

    # =========================================================================
    # STUBS — Further roads (fill in when those towns are built)
    # =========================================================================

    "obsidian_monoliths": {
        "id": "obsidian_monoliths",
        "name": "The Obsidian Monoliths",
        "emoji": "🗿",
        "between": ["sunstoneOasis", "ironforge"],
        "availability": "all",
        "description_day": "Strange formations of jet-black stone rise from the desert floor, humming with a faint magnetic energy. Compasses are useless here.",
        "npcs": {},
        "services": {},
    },

    "shifting_dunes": {
        "id": "shifting_dunes",
        "name": "The Shifting Dunes",
        "emoji": "🏜️",
        "between": ["sunstoneOasis", "aethelgardsRest"],
        "availability": "all",
        "description_day": "A treacherous desert region where the sands move on their own, erasing paths overnight. More than one caravan has been lost here.",
        "npcs": {},
        "services": {},
    },

    "lost_guild_hall": {
        "id": "lost_guild_hall",
        "name": "The Lost Guild Hall",
        "emoji": "🏚️",
        "between": ["frostfallPeak", "blackwaterMarsh"],
        "availability": "all",
        "description_day": "An ancient, overgrown ruin of what was once a proud Guild Hall. Ivy has reclaimed the walls, and the records inside — if any survived — could be invaluable.",
        "npcs": {},
        "services": {},
    },

    "sunken_ship_graveyard": {
        "id": "sunken_ship_graveyard",
        "name": "The Sunken Ship Graveyard",
        "emoji": "⚓",
        "between": ["aethelgardsRest", "skylightSpire"],
        "availability": "all",
        "description_day": "A treacherous stretch of reef and rusted shipwrecks, half-submerged and groaning in the current. Salvagers come here, but not all of them leave.",
        "npcs": {},
        "services": {},
    },

    "wyrmwood_forest": {
        "id": "wyrmwood_forest",
        "name": "The Wyrmwood Forest",
        "emoji": "🌑",
        "between": ["blackwaterMarsh", "ironforge"],
        "availability": "all",
        "description_day": "A dark, twisted forest where the trees grow in unnatural spirals and the canopy blocks all sunlight. The Gloom runs deep here.",
        "npcs": {},
        "services": {},
    },

    "cloudspire_outpost": {
        "id": "cloudspire_outpost",
        "name": "The Cloudspire Outpost",
        "emoji": "☁️",
        "between": ["skylightSpire", "silvermoonGlade"],
        "availability": "all",
        "description_day": "A small floating platform suspended between two peaks by ancient chain-work. The view is breathtaking. The wind is brutal.",
        "npcs": {},
        "services": {},
    },

    "scholars_retreat": {
        "id": "scholars_retreat",
        "name": "The Scholar's Retreat",
        "emoji": "📚",
        "between": ["silvermoonGlade", "sunkenCity"],
        "availability": "day",
        "description_day": "A secluded library hidden between two cliff faces, accessible only by a narrow rope bridge. The collection inside spans centuries of Aethelgard's history.",
        "npcs": {},
        "services": {},
    },

    "chasm_of_whispers": {
        "id": "chasm_of_whispers",
        "name": "The Chasm of Whispers",
        "emoji": "🌀",
        "between": ["ironforge", "skylightSpire"],
        "availability": "all",
        "description_day": "A deep, winding canyon whose walls amplify sound in strange ways. Voices echo here that have no source. Travelers move through quickly.",
        "npcs": {},
        "services": {},
    },

    "forgotten_grove": {
        "id": "forgotten_grove",
        "name": "The Forgotten Grove",
        "emoji": "🌸",
        "between": ["blackwaterMarsh", "ironforge"],  # hidden within Wyrmwood
        "availability": "all",
        "description_day": "A beautiful grove hidden within the Wyrmwood Forest that has miraculously resisted the Gloom. The contrast with the surrounding darkness is striking.",
        "npcs": {},
        "services": {},
    },

    "serpents_coil": {
        "id": "serpents_coil",
        "name": "The Serpent's Coil",
        "emoji": "🐍",
        "between": ["sunkenCity", "dragonsTooth"],
        "availability": "all",
        "description_day": "A treacherous winding path through ancient ruins that corkscrews down into a valley. The stonework is unlike anything built by current civilization.",
        "npcs": {},
        "services": {},
    },

}
