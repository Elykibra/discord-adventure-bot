# --- data/towns.py ---
# This file contains the data structure for all towns in the world of Aethelgard.

TOWNS = {
    "oakhavenOutpost": {
        "id": "oakhavenOutpost",
        "name": "Oakhaven Outpost",
        "image_url": "https://cdn.discordapp.com/attachments/1409446434515714159/1409446496243417168/Oakhaven_Outpost.png?ex=68ad68d6&is=68ac1756&hm=feb079a540226dc368a3be0e1cc04a496bf0fa47a4eaa0c6f4c0b78100249816&",
        "is_hub": True,
        "rank": "Recruit",
        "description_morning": "Dawn light filters through the oak leaves, and the outpost stirs with early activity. The smell of campfire smoke and fresh bread drifts through the cool morning air.",
        "description_noon": "The sun sits high over the outpost, casting short shadows between the log cabins. Guild recruits train in the yard while merchants restock their wares.",
        "description_evening": "The sky turns amber over the outpost as the day winds down. Adventurers return from the wilds, swapping stories near the crackling campfire.",
        "description_night": "The outpost is quiet under the moonlight, with only the crackling of the central campfire providing warmth against the encroaching darkness of the wilds.",
        # Legacy fallback
        "description_day": "The scent of fresh-cut pine fills the air. A single, ancient oak tree stands as a silent sentinel over this humble collection of sturdy log cabins.",

        # --- THIS IS FOR THE "TRAVEL" BUTTON ---
        # outpostWilds accessed via Explore Wilds button, not Travel.
        # Step-by-step travel: Oakhaven → Weeping Chasm → Mirefields → Whisperwood
        "connections": {
            "weeping_chasm": "Weeping Chasm",
        },
        "connection_requirements": {
            "weeping_chasm": "quest_a_guildsmans_first_steps_completed"
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
                "items_for_sale": ["tether_orb", "moss_balm", "sun_kissed_berries", "trail_morsels"],
                "npcs": {
                    "bea": {
                        "name": "Bea",
                        "role": "Supply Merchant",
                        "availability": "day"
                    }
                },
                "services": {
                    "shop": True,
                    "starter_pack": {
                        "max_uses": 3,
                        "flag_prefix": "supply_chest_oakhavenOutpost_use_",
                        "grants": {
                            1: [("tether_orb", 3), ("moss_balm", 2), ("sun_kissed_berries", 3)],
                            2: [("tether_orb", 2), ("trail_morsels", 2), ("moss_balm", 1)],
                            3: [("tether_orb", 1), ("trail_morsels", 2), ("moss_balm", 1)],
                        },
                        "messages": {
                            1: "The chest is freshly stocked. You help yourself to the supplies inside.",
                            2: "Some supplies remain. You take what's left on the upper shelf.",
                            3: "You dig to the bottom of the chest and claim the last of the provisions.",
                        }
                    }
                }
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
    # Outpost Wilds — accessed via Explore Wilds button from Oakhaven Outpost
    "outpostWilds": {
        "id": "outpostWilds",
        "name": "Outpost Wilds",
        "is_wilds": True,
        "description": "The rugged wilderness just outside the safety of the outpost. Tar fumes drift on the wind, and the underbrush stirs with unseen creatures.",
        "connections": {
            "oakhavenOutpost": "Oakhaven Outpost"
        },
        "explore_zone": "outpostWilds"
    },

    # ---------------------------------------------------------------------------
    # TOWN 2 — Whisperwood Grove
    # First real town. Home of the Verdant Crest and Elder Vexia.
    # ---------------------------------------------------------------------------
    "whisperwoodGrove": {
        "id": "whisperwoodGrove",
        "name": "Whisperwood Grove",
        "rank": "Novice",
        "description_morning": "Morning mist drifts between the massive trunks, catching the early light in golden shafts. The grove wakes slowly, birdsong echoing through the ancient canopy.",
        "description_noon": "Filtered sunlight dapples the forest floor as the grove hums with midday activity. Rope bridges sway gently with the comings and goings of treetop residents.",
        "description_evening": "Golden hour turns the canopy into a cathedral of amber and green. Lumina-moths begin their early emergence, flickering to life in the fading light.",
        "description_night": "Under the soft glow of the moon, the forest takes on a mystical quality. Lumina-moths float gently through the air, casting a soft light on the winding paths.",
        # Legacy fallback
        "description_day": "A tranquil and ancient forest where colossal trees reach for the sky. The town is built into the trees themselves, with winding rope bridges connecting cozy, treetop homes.",

        # Travel connections — Whisperwood Wilds accessed via Explore Wilds button, not Travel
        # Step-by-step travel: Whisperwood ← Mirefields ← Weeping Chasm ← Oakhaven
        "connections": {
            "mirefields": "Mirefields",
            "whisperwoodWilds": "Whisperwood Wilds",  # is_wilds=True → renders as Explore Wilds button
        },

        "locations": {
            # ------------------------------------------------------------------
            # 1. The Leaf-Lit Lodge — rest & pet healing, Arboreal the Treant
            # ------------------------------------------------------------------
            "leaf_lit_lodge": {
                "name": "The Leaf-Lit Lodge",
                "emoji": "🌳",
                "menu_description": "A healing lodge tended by an ancient Treant. Restore your companions here.",
                "availability": "all",
                "description_day": "A large, welcoming lodge woven from living branches and glowing moss. Soft light emanates from within, and the gentle chirping of various forest creatures fills the air.",
                "description_night": "Even in the dark, the lodge glows with a warm, bioluminescent light. The old Treant's lanterns never go out.",
                "services": {
                    "rest": {
                        "type": "lodge",
                        "cost": 0,
                        "energy_restore_percent": 0,
                        "health_restore_percent": 100,  # Free full pet HP restore
                    }
                },
                "npcs": {
                    "arboreal": {
                        "name": "Arboreal",
                        "role": "Treant Healer",
                        "availability": "all",
                        "dialogue": {
                            "default": "Welcome, young Adventurer. Let the forest's embrace soothe your companions. Rest here, for the path ahead demands strong bonds.",
                            "after_heal": "May your roots grow deep, and your spirit soar.",
                        }
                    }
                }
            },

            # ------------------------------------------------------------------
            # 2. The Verdant Spire Guild Hall — Elder Vexia + Linden the Scribe
            # ------------------------------------------------------------------
            "verdant_spire": {
                "name": "The Verdant Spire Guild Hall",
                "emoji": "🏛️",
                "menu_description": "The heart of Guild activity in the Grove. Speak with Elder Vexia.",
                "availability": "day",
                "description_day": "A massive, hollowed-out ancient tree spiraling upwards with mossy walls and natural light. The air smells of old parchment and fresh leaves. Adventurers bustle throughout.",
                "description_night": "The Guild Hall is dimly lit at night. Linden keeps a single candle burning at the Quest Board, but Elder Vexia has retired for the evening.",
                "npcs": {
                    "vexia": {
                        "name": "Elder Vexia",
                        "role": "Guild Master",
                        "availability": "day",
                        "dialogue": {
                            "default": "The Grand Master's vision echoes even here, young one. The Verdant Crest is not won, but earned through understanding of nature's delicate balance.",
                            "quest_whisperwoods_plea_active": "The Thicket grows darker by the day. Find the source of the corruption — the Heart of Decay. The forest is counting on you.",
                            "quest_whisperwoods_plea_complete": "You've shown kindness and understanding. Now, let us see the strength of your bond. Face my companion — and prove yourself worthy.",
                            "crest_earned": "The Verdant Crest rests with a worthy guardian, Adventurer. May its light guide you to the next challenge.",
                        }
                    },
                    "linden": {
                        "name": "Linden",
                        "role": "Guild Scribe",
                        "availability": "all",
                        "dialogue": {
                            "default": "Welcome to the Verdant Spire Guild Hall! Please check the Quest Board for available tasks. Remember, proper documentation is key!",
                            "quest_complete": "Another quest completed? Excellent! Make sure you fill out the proper forms, Adventurer.",
                        }
                    }
                }
            },

            # ------------------------------------------------------------------
            # 3. The Root & Branch Emporium — Slithers the Snail-folk shopkeeper
            # ------------------------------------------------------------------
            "root_branch_emporium": {
                "name": "The Root & Branch Emporium",
                "emoji": "🛒",
                "menu_description": "A quirky shop in the roots of the oldest tree. Pick up supplies and Capture Orbs.",
                "availability": "day",
                "description_day": "A quirky, charming shop built into the sprawling root system of the Grove's oldest tree. Shelves are laden with vials of dewdrop potions, bundles of strong vines, and various unusual forest finds.",
                "description_night": "The shutters are closed. Slithers keeps early hours — come back when the sun warms the canopy.",
                "items_for_sale": ["capture_orb", "moss_balm", "simple_sleeping_bag", "potion", "greater_potion"],
                "services": {
                    "shop": True
                },
                "npcs": {
                    "slithers": {
                        "name": "Slithers",
                        "role": "Shopkeeper",
                        "availability": "day",
                        "dialogue": {
                            "default": "Welcome, welcome, Adventurer! Need anything for the road? My wares are as fresh as the morning dew!",
                            "capture_orb_hint": "Ah, a Capture Orb! Essential for befriending new forest friends!",
                        }
                    }
                }
            },

            # ------------------------------------------------------------------
            # 4. The Moonpetal Inn — full rest (costs coins)
            # ------------------------------------------------------------------
            "moonpetal_inn": {
                "name": "The Moonpetal Inn",
                "emoji": "🌙",
                "menu_description": "A cozy inn glowing with moonpetal light. Sleep here to fully restore.",
                "availability": "all",
                "description_day": "A cozy inn constructed from large, glowing moonpetal flowers and sturdy tree trunks. The air inside is filled with soothing, herbal scents.",
                "description_night": "The inn glows warmly against the dark forest. A perfect place to rest weary bones and restore your companions.",
                "services": {
                    "rest": {
                        "type": "inn",
                        "cost": 15,
                        "energy_restore_percent": 100,
                        "health_restore_percent": 100,
                    }
                },
                "npcs": {
                    "mira": {
                        "name": "Mira",
                        "role": "Innkeeper",
                        "availability": "all",
                        "dialogue": {
                            "default": "Welcome to the Moonpetal Inn. Dust off your boots and rest a while — the forest will still be there in the morning.",
                            "night": "You've come at the right hour. The inn is quietest now. The Lumina-moths are out, and the moonpetals are in full bloom. Quite a sight, if you're not too tired to look.",
                            "after_rest": "Sleep well? The grove has a way of making even the most restless adventurers feel at home.",
                        }
                    }
                }
            },

            # ------------------------------------------------------------------
            # 5. The Whispering Thicket — primary explore zone, Fae Whisper NPC
            # ------------------------------------------------------------------
            "whispering_thicket": {
                "name": "The Whispering Thicket",
                "emoji": "🌿",
                "menu_description": "Darker and wilder than the grove. Strange calls echo from within.",
                "availability": "all",
                "description_day": "A deeper, more overgrown section of the Whisperwood. The paths are less clear and the shadows are heavier. Strange calls echo from within.",
                "description_night": "Under the moonlight, the Thicket feels genuinely threatening. The Gloom is stronger here, and the rustle of unseen creatures follows your every step.",
                "services": {
                    "explore_zone": "whisperwoodGrove",
                    "gloom_level": 15,
                },
                "npcs": {
                    "fae_whisper": {
                        "name": "Fae Whisper",
                        "role": "Pixie Sprite",
                        "availability": "all",
                        "dialogue": {
                            "default": "*A tiny sprite flits past, leaving a trail of glittering dust.* Follow the lights, Adventurer... if you dare.",
                        }
                    }
                }
            },
        }
    },

    # Whisperwood Wilds — accessed via Explore Wilds button from Whisperwood Grove
    "whisperwoodWilds": {
        "id": "whisperwoodWilds",
        "name": "Whisperwood Wilds",
        "is_wilds": True,
        "description": "The dense, untamed forest surrounding the Grove. Ancient trees loom overhead, their roots twisting across the path. The deeper you go, the heavier the air becomes.",
        "connections": {
            "whisperwoodGrove": "Whisperwood Grove"
        },
        "explore_zone": "whisperwoodGrove"
    },

    # ---------------------------------------------------------------------------
    # TOWN 3 — Sunstone Oasis (stub, unlocked after Verdant Crest)
    # ---------------------------------------------------------------------------
    "sunstoneOasis": {
        "id": "sunstoneOasis",
        "name": "Sunstone Oasis",
        "rank": "Journeyman",
        "description_morning": "The desert air is crisp and cool before the sun fully rises. Merchants set up their stalls early, and the oasis glimmers with the promise of another day.",
        "description_noon": "The heat is at its peak, driving most locals into the shade of canvas awnings. The oasis water shimmers brilliantly — a welcome refuge from the relentless sun.",
        "description_evening": "As the sun sinks toward the dunes, the temperature drops rapidly and the oasis town truly comes alive. Lanterns are lit, music drifts through warm evening air.",
        "description_night": "Under the cool desert night, the oasis comes alive with the glow of lanterns and the sound of music. The stars above are brilliant and clear.",
        # Legacy fallback
        "description_day": "A bustling town built around a life-giving oasis in the heart of a vast, sun-scorched desert. The heat is intense, but the spirit of the locals is resilient.",
        "connections": {
            "whisperwoodGrove": "Whisperwood Grove",
        },
        "locations": {
            # Content coming in Town 3 update
        }
    },
    # ... (remaining towns to be added)
}