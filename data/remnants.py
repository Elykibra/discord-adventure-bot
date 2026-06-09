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
        "connection_costs": {
            "oakhavenOutpost": 8,
            "mirefields": 14,
        },
        "connection_requirements": {
            "mirefields": "quest_a_guildsmans_first_steps_completed",
        },
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
        # -----------------------------------------------------------------
        # Locations — same pattern as towns.py
        # Availability: 'all' | 'day' | 'night'
        # required_flag: greyed out until player has this flag
        # required_quest: greyed out until this quest is active
        # -----------------------------------------------------------------
        "locations": {
            "chasms_edge": {
                "name": "The Chasm's Edge",
                "emoji": "🕳️",
                "menu_description": "The lip of the Chasm. Cold. The source of the Gloom.",
                "availability": "all",
                "description_day": (
                    "A narrow ledge of cracked stone along the chasm's rim. The Guild has "
                    "bolted warning markers into the rock, but most have tilted with the "
                    "settling ground. The air here smells of cold metal and something older."
                ),
                "description_night": (
                    "The mist curls upward around your ankles. The darkness below is total. "
                    "Nothing attacks. Something is just checking."
                ),
                "services": {
                    "explore_zone": "weeping_chasm",
                    "gloom_level": 25,
                },
                "npcs": {},
            },

            "wardens_post": {
                "name": "The Warden's Post",
                "emoji": "🛡️",
                "menu_description": "Warden Orin's watch station. Manned during daylight hours.",
                "availability": "day",
                "description_day": (
                    "A solid Guild-issue post: a small fire, a folding chair, a logbook "
                    "worn thin from use. Warden Orin keeps his eyes on the Chasm with the "
                    "patience of someone who has been doing this a long time."
                ),
                "description_night": (
                    "A folded note is pinned to the post with a Guild insignia pin.\n\n"
                    "*\"Gone at dark. You should be too. — O.\"*"
                ),
                "services": {},
                "npcs": {
                    "warden_orin": {
                        "name": "Warden Orin",
                        "role": "Guild Warden",
                        "emoji": "🛡️",
                        "availability": "day",
                        "dialogue": {
                            "default": (
                                "This is as close as most people get. The Chasm draws "
                                "Gloom-Touched creatures — they're drawn to the source. "
                                "I keep watch so travelers can pass safely. Mostly."
                            ),
                            "lore_prompt": (
                                "The records say The Gloom first surfaced here. I believe it. "
                                "Some nights I can feel it thinking."
                            ),
                            "returning_recruit": (
                                "Ah — a Guild recruit. Good. The road east gets worse before "
                                "it gets better. Keep your pet fed and your energy up."
                            ),
                        },
                    },
                },
            },

            "scholars_camp": {
                "name": "The Scholar's Camp",
                "emoji": "📜",
                "menu_description": "A field researcher's camp. Appears occupied — sometimes.",
                "availability": "all",
                "required_quest": "echoes_from_below",   # greyed until quest is active
                "description_day": (
                    "A small camp pressed against the rock face away from the wind. "
                    "Notebooks, vials, and equipment cases are stacked with the organised "
                    "chaos of someone who knows exactly where everything is. "
                    "A lamp burns low on a flat stone."
                ),
                "description_night": (
                    "The lamp is still burning. The notebooks are still open. "
                    "Kael doesn't sleep much when he's onto something."
                ),
                "services": {},
                "npcs": {
                    "lore_keeper_kael": {
                        "name": "Lore-Keeper Kael",
                        "role": "Guild Scholar",
                        "emoji": "🔬",
                        "availability": "all",
                        "dialogue": {
                            "default": (
                                "You found me. Good — I wasn't sure Vexia would send anyone "
                                "capable. The origin point is right here and nobody bothers "
                                "to study it properly. I need samples. Three vials of "
                                "gloom-mist from the Edge. Can you do that?"
                            ),
                            "samples_collected": (
                                "These are clean samples — remarkable. The density here is "
                                "unlike anything recorded further out. When you reach the "
                                "Oasis, find the Obsidian Monoliths. I'll be there. "
                                "There's something I need to show you."
                            ),
                        },
                    },
                },
            },

            "lookout_hollow": {
                "name": "The Lookout Hollow",
                "emoji": "🗡️",
                "menu_description": "A weathered hollow. Someone has been here a long time.",
                "availability": "all",
                "description_day": (
                    "A natural depression in the rock, sheltered from the wind and set back "
                    "from the Chasm. It's been lived in — a fire ring, a bedroll, a row of "
                    "marked stones that might be a personal tallying system. "
                    "Gretta is here, as she always is."
                ),
                "description_night": (
                    "The fire is low but steady. Gretta is awake. "
                    "She's always awake at night — she learned not to sleep deeply here "
                    "a long time ago."
                ),
                "services": {
                    "rest": {
                        "type": "rough_camp",
                        "cost": 0,
                        "energy_restore": 20,
                        "health_restore_percent": 0,
                        "flavor": (
                            "Gretta gestures at a flat rock near the fire without looking up. "
                            "*\"Sit. Don't talk.\"* "
                            "You rest in silence. It's enough."
                        ),
                    },
                },
                "npcs": {
                    "grim_gretta": {
                        "name": "\"Grim\" Gretta",
                        "role": "Chasm Watcher",
                        "emoji": "🗡️",
                        "availability": "all",
                        "dialogue": {
                            "default": (
                                "Guild sends another one. They always look the same — "
                                "hopeful. The Chasm fixes that eventually. "
                                "What do you want?"
                            ),
                            "player_has_pet": (
                                "That creature following you — you trust it? "
                                "The Gloom finds the ones you're attached to first. "
                                "Keep it strong. Soft bonds don't survive this road."
                            ),
                            "subdue_path_intro": (
                                "You want to know what I know? Fine. "
                                "The Guild tells you to heal corrupted creatures. "
                                "I've watched that fail more times than you've been alive. "
                                "Control is not cruelty. It's honesty. "
                                "There's another way — if you're willing to hear it."
                            ),
                        },
                    },
                },
            },
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
        "connection_costs": {
            "weeping_chasm": 12,
            "whisperwoodGrove": 14,
        },
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
        "locations": {
            "bogside_trail": {
                "name": "The Bogside Trail",
                "emoji": "🌫️",
                "menu_description": "The main stretch through the mire. Creatures lurk nearby.",
                "availability": "all",
                "description_day": (
                    "The road narrows to a muddy track hemmed in by twisted undergrowth. "
                    "The ground shifts unpredictably underfoot. Territorial creatures "
                    "watch from the fog — not Gloom-touched, just mean and hungry."
                ),
                "description_night": (
                    "The trail is nearly invisible in the dark. Every sound is amplified. "
                    "Moving through here at night requires patience and a steady pet."
                ),
                "services": {
                    "explore_zone": "mirefields",
                    "gloom_level": 8,
                },
                "npcs": {},
            },

            "sables_post": {
                "name": "Sable's Post",
                "emoji": "🪤",
                "menu_description": "A trapper's camp off the main trail. Supplies available.",
                "availability": "all",
                "description_day": (
                    "A compact camp built from salvaged wood and waterproofed canvas. "
                    "Traps and pelts hang from a line. Sable runs a lean operation — "
                    "everything here has a purpose."
                ),
                "description_night": (
                    "The camp lantern is on. Sable keeps late hours. "
                    "Half the road traffic passes through at night, and she knows it."
                ),
                "services": {
                    "shop": True,
                    "shop_items": ["moss_balm", "trail_morsels", "tether_orb"],
                    "rest": {
                        "type": "rough_camp",
                        "cost": 0,
                        "energy_restore": 20,
                        "health_restore_percent": 0,
                        "flavor": (
                            "Sable tosses you a strip of dried bark to chew on and points "
                            "to a dry log. You sit in silence while the fog drifts past. "
                            "*\"Don't get comfortable.\"*"
                        ),
                    },
                },
                "npcs": {
                    "sable": {
                        "name": "Sable",
                        "role": "Bog Trapper",
                        "emoji": "🪤",
                        "availability": "all",
                        "dialogue": {
                            "default": (
                                "You lost? Most people don't come through here by choice. "
                                "I've got supplies if you need them — nothing fancy, "
                                "but it'll keep you alive."
                            ),
                            "night": (
                                "You're braver than most, traveling through here at night. "
                                "Or dumber. Hard to tell. Watch your step — the mire shifts after dark."
                            ),
                            "sell": "Take what you need and move on. I don't do small talk.",
                        },
                    },
                },
            },
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
