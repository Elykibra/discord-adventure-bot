# --- data/towns.py ---
# This file contains the data structure for all towns in the world of Aethelgard.

towns = {
    "oakhavenOutpost": {
        "id": "oakhavenOutpost",
        "name": "Oakhaven Outpost",
        "image_url": "https://cdn.discordapp.com/attachments/1409446434515714159/1409446496243417168/Oakhaven_Outpost.png?ex=68ad68d6&is=68ac1756&hm=feb079a540226dc368a3be0e1cc04a496bf0fa47a4eaa0c6f4c0b78100249816&",
        "is_hub": True,
        "rank": "Recruit",
        "description_day": "The scent of fresh-cut pine fills the air. A single, ancient oak tree stands as a silent sentinel over this humble collection of sturdy log cabins, its leaves whispering a welcome.",
        "description_night": "The outpost is quiet under the moonlight, with the crackling of the central campfire providing a comforting warmth against the encroaching darkness of the wilds.",

        # --- THIS IS FOR THE "TRAVEL" BUTTON ---
        # Defines where you can travel to from this hub.
        "connections": {
            "oakhavenWilds": "Oakhaven Wilds"
            # "theWeepingChasm": "The Weeping Chasm" # We can add this back later
        },

        # --- THIS IS FOR THE DROPDOWN MENU ---
        # Defines the points of interest inside the hub.
        "locations": {
            "recruitment_hut": {
                "name": "The Guild Recruitment Hut",
                "image_url": "https://cdn.discordapp.com/attachments/YOUR_CHANNEL_ID/YOUR_MESSAGE_ID/Recruitment_Hut.png",
                "menu_description": "Speak with Guild officers and get quests.",  # <-- NEW
                "emoji": "🛡️",
                "parent_zone": "oakhavenOutpost",
                "availability": "day",
                "description_day": "The main administrative building of the outpost. A large oak desk sits at the far end, behind which you can see Recruitment Officer Elara organizing various Guild contracts and notice board postings.",
                "description_night": "The hut is dark and quiet, the desk neatly organized for the next day's work. Elara is not present.",
                "npcs": {
                    "elara": {
                        "name": "Recruitment Officer Elara",
                        "role": "Guild Officer",
                        "availability": "day",
                        # --- ENHANCED DIALOGUE ---
                        "dialogue": {
                            "default": "Welcome, Adventurer. The Guild welcomes you. I am here to make sure you're ready for the path ahead.",
                            "quest_the_first_step_step_1": "I see Grit Galen is back from the pits. That old scavenger has seen more of this world than most. You should speak with him."
                        }
                    }
                }
            },
            "supply_chest": {
                "name": "The Outpost's Supply Chest",
                "image_url": "https://cdn.discordapp.com/attachments/YOUR_CHANNEL_ID/YOUR_MESSAGE_ID/Supply_Chest.png",
                "menu_description": "Purchase basic supplies for your journey.",  # <-- NEW
                "emoji": "📦",  # <-- NEW
                "parent_zone": "oakhavenOutpost",
                "availability": "all",
                "description": "A large, reinforced chest stocked with basic supplies...",
                "items_for_sale": ["capture_orb", "moss_balm", "potion"],
                "services": {"shop": True}
            },
            "rest_point": {  # Unchanged
                "name": "The Weary Wanderer's Bench",
                "image_url": "https://cdn.discordapp.com/attachments/YOUR_CHANNEL_ID/YOUR_MESSAGE_ID/Campfire_Bench.png",
                "menu_description": "Rest here to recover energy and pass the time.",  # <-- NEW
                "emoji": "🌙",  # <-- NEW
                "parent_zone": "oakhavenOutpost",
                "availability": "all",
                "description": "A simple wooden bench next to the crackling campfire...",
                "services": {
                    "rest": {"type": "bench", "energy_restore_percent": 50, "health_restore_percent": 25}
                }
            },
            "rotting_pits": {
                "name": "The Rotting Pits",
                "image_url": "https://cdn.discordapp.com/attachments/YOUR_CHANNEL_ID/YOUR_MESSAGE_ID/Rotting_Pits.png",
                "menu_description": "A dangerous area with unique encounters.",  # <-- NEW
                "emoji": "☠️",  # <-- NEW
                "parent_zone": "oakhavenOutpost",
                "availability": "all",
                "description_day": "A series of bubbling tar pits exude a foul, corrupting smell. The air is thick with a palpable sense of Gloom, making the area feel unsettling even in broad daylight. You sense that creatures here are more aggressive.",
                "description_night": "Under the moonlight, the pits seem to glow with a sickly luminescence. The Gloom is stronger now, and the strange sounds bubbling up from the sludge suggest that the creatures within are even more dangerous.",
                "services": {"explore_zone": "oakhavenOutpost_rottingPits",
                             "gloom_level": 20,
                             },
                "npcs": {
                    "grit_galen": {
                        "name": "Grit Galen",
                        "role": "Scavenger",
                        "availability": "day",
                        # --- ENHANCED DIALOGUE ---
                        "dialogue": {
                            "default": "Don't get too close to the pits, adventurer. The Guild taught you nothing of what lives in there. Only what you can fight.",
                            "quest_offer": "A satchel of my tools lies at the bottom of the pits. It's sinking fast. I can't get it myself. Find it for me, and I'll give you something for your troubles.",
                            "quest_active": "Still looking for my satchel? Be careful down there. The Gloom makes things... twitchy.",
                            "quest_complete": "You found it! By the Spirits, I thought it was lost for good. Here, take this. It's a compass of sorts. Doesn't point north, but it has a knack for finding things that don't want to be found. Good luck, adventurer."
                        }
                    }
                }
            }
        }
    },
                # --- MOVED TO HERE ---
                "oakhavenWilds": {
                    "id": "oakhavenWilds",
                    "name": "Oakhaven Wilds",
                    "is_wilds": True,
                    "description": "The rugged wilderness just outside the safety of the outpost.",
                    "connections": {
                        "oakhavenOutpost": "Oakhaven Outpost"
                    },
                    "explore_zone": "oakhavenOutpost_rottingPits"
                },

    "whisperwoodGrove": {
        "id": "whisperwoodGrove",
        "name": "Whisperwood Grove",
        "rank": "Novice",
        "description_day": "A tranquil and ancient forest where colossal trees reach for the sky. The town is built into the trees themselves, with winding rope bridges connecting cozy, treetop homes.",
        "description_night": "Under the soft glow of the moon, the forest takes on a mystical quality. Lumina-moths float gently through the air, casting a soft light on the winding paths.",
        "connections": {
            "whisperwoodWilds": "Whisperwood Wilds",
            "oakhavenOutpost": "Oakhaven Outpost"  # Travel back to the outpost itself
        },
        "prerequisite": None,
        "locations": {
            "guild_hall": {
                "name": "The Verdant Spire Guild Hall",
                "availability": "day",
                "description": "The center of Guild operations in Whisperwood Grove. Elder Vexia can often be found here, her wisdom as ancient as the trees.",
                "npcs": {
                    "vexia": {
                        "name": "Elder Vexia",
                        "role": "Guild Master",
                        "dialogue": {
                            "day": "Welcome, young one. The whispers of the woods precede you. There is a sickness in this forest that needs a steady hand.",
                            "quest_related": "A darkness gnaws at the heart of this grove. I need you to venture into the Whispering Thicket and find the source of the corruption."
                        }
                    }
                }
            },
            "shop": {
                "name": "The Root & Branch Emporium",
                "availability": "day",
                "description": "A cozy shop built into the base of a massive tree, run by a friendly Snail-folk named Slithers.",
                "items_for_sale": ["capture_orb", "moss_balm", "simple_sleeping_bag", "potion", "greater_potion"],
                "services": {
                    "shop": True
                },
                "npcs": {
                    "slithers": {
                        "name": "Slithers",
                        "role": "Shopkeeper",
                        "dialogue": { "day": "Looking for supplies? You've come to the right... shell!" }
                    }
                }
            },
            "inn": {
                "name": "The Moonpetal Inn",
                "availability": "all",
                "description": "A comfortable inn where you can get a full night's rest for a small fee.",
                "services": {
                    "rest": {
                        "type": "inn",
                        "cost": 10,
                        "energy_restore_percent": 100,
                        "health_restore_percent": 100
                    }
                }
            },
                "exploration": {
                    "name": "The Whispering Thicket",
                    "availability": "all",
                    "description": "The deeper, untamed part of the forest. Be wary, as stronger creatures lurk here.",
                    "services": {
                        "explore_zone": "whisperwoodGrove"
                    }
                },
                "whisperwoodWilds": { # --- NEW WILDS ZONE ---
                    "id": "whisperwoodWilds",
                    "name": "Whisperwood Wilds",
                    "is_wilds": True,
                    "description": "The dense, untamed forest surrounding the Grove.",
                    "connections": {
                        "whisperwoodGrove": "Whisperwood Grove"
                    },
                    "explore_zone": "whisperwoodGrove"
                },
            }
        },
            "sunstoneOasis": {
                "id": "sunstoneOasis",
                "name": "Sunstone Oasis",
                "rank": "Journeyman",
                "description_day": "A bustling town built around a life-giving oasis in the heart of a vast, sun-scorched desert. The heat is intense, but the spirit of the locals is resilient.",
                "description_night": "Under the cool desert night, the oasis comes alive with the glow of lanterns and the sound of music. The stars above are brilliant and clear.",
                "connections": ["whisperwoodGrove"], # Connection back to the grove
                "prerequisite": None,
                "locations": {
                    # We can leave this empty for now
                }
            },
    # ... (rest of the town data would go here)
            }