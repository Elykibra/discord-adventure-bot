# data/pets.py
# This file contains all detailed data for pets in the game,
# including starters, catchable pets, their stats, and skill trees.

# =================================================================================
#  PET DATABASE
# =================================================================================
# This is now the single source of truth for ALL pet data.
# Each pet is defined only once. Evolutions are nested inside their base form.

PET_DATABASE = {
    # --- Starter Pets ---
    "Pyrelisk": {
        "species": "Pyrelisk", "pet_type": "Fire", "rarity": "Starter", "personality": "Aggressive",
        "description": "A small, lizard-like creature with ember-red scales and a tail that flickers with a perpetual flame. Its eyes glow like hot coals, and it leaves tiny scorch marks wherever it steps.",
        "base_capture_rate": 35,
        "passive_ability": {
            "name": "Singeing Fury",
            "description": "Each time this pet uses a damaging Fire-type attack, it gains a 'Singe' stack. Each stack increases the power of all Fire-type moves by 5%."
        },
        "base_stat_ranges": {"hp": [40, 45], "attack": [48, 54], "defense": [30, 35], "special_attack": [42, 48],
                             "special_defense": [30, 35], "speed": [35, 40]},
        "growth_rates": {"hp": 1.8, "attack": 2.2, "defense": 1.1, "special_attack": 1.6, "special_defense": 1.1,
                         "speed": 1.3},
        "skill_tree": {
            "1": ["scratch", "scorch"],
            "7": ["ember"],
            "13": {"choice": ["immolate", "blightborne_fury"]}
        },
        "evolutions": {
            "Blazewyrm": {
                "evolves_at": 16,
                "species": "Blazewyrm", "pet_type": ["Fire", "Dragon"], "rarity": "Starter",
                "description": "A more imposing reptilian form, the Blazewyrm is covered in thick, heat-resistant scales and a ridge of sharp, volcanic rock that runs down its back. Its eyes burn with a low, menacing glow.",
                "base_stat_ranges": {"hp": [60, 65], "attack": [70, 75], "defense": [45, 50], "special_attack": [65, 70],
                                     "special_defense": [45, 50], "speed": [50, 55]},
                "growth_rates": {"hp": 2.2, "attack": 2.5, "defense": 1.5, "special_attack": 2.0, "special_defense": 1.5,
                                 "speed": 1.7},
                "skill_tree": {
                    "17": ["fireball"],
                    "20": ["fire_fang"],
                    "24": ["shattering_blow"],
                    "28": ["dragon_rush"]
                },
                "evolutions": {
                    "Ignisyrn": {
                        "evolves_at": 30,
                        "species": "Ignisyrn", "pet_type": ["Fire", "Dragon"], "rarity": "Starter",
                        "description": "A fearsome draconic creature with scales that glow like magma and massive wings that beat with a volcanic force. It is the undisputed predator of fiery lands.",
                        "base_stat_ranges": {"hp": [80, 85], "attack": [110, 115], "defense": [60, 65], "special_attack": [100, 105],
                                             "special_defense": [60, 65], "speed": [70, 75]},
                        "growth_rates": {"hp": 2.5, "attack": 3.0, "defense": 1.8, "special_attack": 2.8, "special_defense": 1.8,
                                         "speed": 2.0},
                        "skill_tree": {
                            "32": ["scale_slash"],
                            "35": ["wyrms_contempt"],
                            "40": {"choice": ["nexus_conversion", "unyielding_focus"]},
                            "50": ["overwhelm"],
                            "60": ["draconic_ascendance"]
                        }
                    }
                }
            }
        }
    },

    "Dewdrop": {
        "species": "Dewdrop", "pet_type": "Water", "rarity": "Starter", "personality": "Tactical",
        "description": "A small, teardrop-shaped creature with translucent, water-blue skin that shimmers in the light. Tiny ripples flow across its body when it moves, and a soft gurgling sound follows it everywhere.",
        "base_capture_rate": 35,
        "passive_ability": {
            "name": "Temporal Wellspring",
            "description": "All status effects and debuffs applied by this pet last for one extra turn."
        },
        "base_stat_ranges": {"hp": [40, 45], "attack": [30, 35], "defense": [35, 40], "special_attack": [48, 54],
                             "special_defense": [42, 48], "speed": [35, 40]},
        "growth_rates": {"hp": 1.8, "attack": 1.1, "defense": 1.3, "special_attack": 2.2, "special_defense": 1.6,
                         "speed": 1.5},
        "skill_tree": {
            "1": ["pound", "bubble"],
            "7": ["soothing_veil"],
            "13": {"choice": ["water_gun", "blessing_of_aethelgard"]}
        },
        "evolutions": {
            "Aquarius": {
                "evolves_at": 16,
                "species": "Aquarius", "pet_type": ["Water", "Fairy"], "rarity": "Starter",
                "description": "A bipedal, aquatic being with fins that resemble delicate feathers and a body that flows like a river. It moves with a hypnotic, liquid grace.",
                "base_stat_ranges": {"hp": [60, 65], "attack": [45, 50], "defense": [50, 55], "special_attack": [70, 75],
                                     "special_defense": [65, 70], "speed": [55, 60]},
                "growth_rates": {"hp": 2.2, "attack": 1.5, "defense": 1.7, "special_attack": 2.5, "special_defense": 2.0,
                                 "speed": 1.8},
                "skill_tree": {
                    "17": ["water_pulse"],
                    "20": ["tidal_lock"],
                    "25": ["temporal_echo"],
                    "28": ["hydro_pump",]
                },
                "evolutions": {
                    "Aethelgale": {
                        "evolves_at": 30,
                        "species": "Aethelgale", "pet_type": ["Water", "Fairy"], "rarity": "Starter",
                        "description": "A guardian forged from pure, translucent water, its form constantly shifting like a flowing river. It possesses a serene, ancient wisdom in its eyes.",
                        "base_stat_ranges": {"hp": [80, 85], "attack": [60, 65], "defense": [70, 75], "special_attack": [110, 115],
                                             "special_defense": [100, 105], "speed": [75, 80]},
                        "growth_rates": {"hp": 2.5, "attack": 1.8, "defense": 2.0, "special_attack": 3.0, "special_defense": 2.8,
                                         "speed": 2.2},
                        "skill_tree": {
                            "32": ["drizzle"],
                            "35": ["equilibrium_shift"],
                            "40": {"choice": ["spirit_blessing", "karma_weave"]},
                            "50": ["precognition"],
                            "60": ["dazzling_gleam"]
                        }
                    }
                }
            }
        }
    },
    "Terran": {
        "species": "Terran", "pet_type": "Ground", "rarity": "Starter", "personality": "Defensive",
        "description": "A squat, boulder-shaped creature covered in rough, earthy hide the color of dried clay. Despite its slow movements, it carries an unshakeable solidity, as if it were a small fragment of the earth given life.",
        "base_capture_rate": 35,
        "passive_ability": {
            "name": "Fortress Form",
            "description": "When this pet takes a direct hit from an opponent, its Defense and Special Defense stats are temporarily increased by 10% for the remainder of the turn. This bonus cannot stack."
        },
        "base_stat_ranges": {"hp": [45, 50], "attack": [40, 45], "defense": [50, 55], "special_attack": [30, 35],
                             "special_defense": [35, 40], "speed": [25, 30]},
        "growth_rates": {"hp": 2.0, "attack": 1.5, "defense": 2.2, "special_attack": 1.1, "special_defense": 1.3,
                         "speed": 1.0},
        "skill_tree": {
            "1": ["headbutt", "mud_slap"],
            "5": [ "sand_attack"],
            "7": ["rock_throw"],
            "13": {"choice": ["earthen_bulwark", "geode_charge"]}
        },
        "evolutions": {
            "Stonehide": {
                "evolves_at": 16,
                "species": "Stonehide", "pet_type": ["Ground", "Rock"], "rarity": "Starter",
                "description": "A quadrupedal golem whose body is comprised of dense, layered rock. It has a single, large gem in its chest that glows with the light of the earth.",
                "base_stat_ranges": {"hp": [65, 70], "attack": [55, 60], "defense": [75, 80], "special_attack": [40, 45],
                                     "special_defense": [50, 55], "speed": [35, 40]},
                "growth_rates": {"hp": 2.4, "attack": 1.8, "defense": 2.5, "special_attack": 1.3, "special_defense": 1.5,
                                 "speed": 1.2},
                "skill_tree": {
                    "17": ["rock_slide"],
                    "20": ["spiteful_bastion"],
                    "25": ["sorrowful_strike"]
                },
                "evolutions": {
                    "Bouldyrn": {
                        "evolves_at": 30,
                        "species": "Bouldyrn", "pet_type": ["Ground", "Rock"], "rarity": "Starter",
                        "description": "A colossal golem with a fortress-like body of polished obsidian and glowing green crystals embedded within its chest. It moves slowly but with immense, unyielding power.",
                        "base_stat_ranges": {"hp": [90, 95], "attack": [75, 80], "defense": [120, 125], "special_attack": [55, 60],
                                             "special_defense": [70, 75], "speed": [45, 50]},
                        "growth_rates": {"hp": 2.8, "attack": 2.0, "defense": 3.0, "special_attack": 1.5, "special_defense": 1.8,
                                         "speed": 1.4},
                        "skill_tree": {
                            "32": ["harden"],
                            "35": ["balancing_ward"],
                            "40": {"choice": ["seismic_slam", "stone_gaze"]},
                            "50": ["enduring_fortitude"],
                            "60": ["mountain_shatter"]
                        }
                    }
                }
            }
        }
    },

    # --- Oakhaven Outpost Pets ---
    "Bristlecone": {
        "species": "Bristlecone",
        "pet_type": "Normal",
        "rarity": "Common",
        "personality": "Defensive",
        "description": "A small, pine cone-shaped creature with a tough, bark-like exterior and stubby limbs. Its body is studded with short, sharp needles that bristle outward whenever it senses danger.",
        "base_capture_rate": 45,
        "passive_ability": {
            "name": "Bark Skin",
            "description": "This pet's tough natural armor reduces incoming physical damage by 5%."
        },
        "base_stat_ranges": {"hp": [45, 50], "attack": [25, 30], "defense": [40, 45], "special_attack": [20, 25],
                             "special_defense": [30, 35], "speed": [20, 25]},
        "growth_rates": {"hp": 1.9, "attack": 1.2, "defense": 1.8, "special_attack": 1.0, "special_defense": 1.3,
                         "speed": 1.1},
        "skill_tree": {
            "1": ["pound", "harden"],
            "5": ["needle_shot"],
            "10": ["bark_up"],
            "13": {"choice": ["splinter_strike", "ironbark"]}
        },
        "evolutions": {
            "Burlback": {
                "evolves_at": 16,
                "species": "Burlback",
                "pet_type": ["Normal", "Grass"],
                "rarity": "Uncommon",
                "description": "A sturdy, tree-stump-like creature whose bark has hardened into thick natural armor. Gnarled branches sprout from its back, and its slow, deliberate movements carry the weight of something ancient and unyielding.",
                "passive_ability": {
                    "name": "Thorny Hide",
                    "description": "Attackers who make direct physical contact with this pet take a small amount of piercing damage in return."
                },
                "base_stat_ranges": {"hp": [65, 70], "attack": [40, 45], "defense": [65, 70], "special_attack": [30, 35],
                                     "special_defense": [50, 55], "speed": [25, 30]},
                "growth_rates": {"hp": 2.2, "attack": 1.5, "defense": 2.3, "special_attack": 1.2, "special_defense": 1.7,
                                 "speed": 1.2},
                "skill_tree": {
                    "17": ["wood_hammer"],
                    "20": ["leech_seed"],
                    "25": {"choice": ["ironbark", "nature_shield"]},
                    "30": ["branch_whip"]
                }
            }
        }
    },
    "Corroder": {
        "species": "Corroder", "pet_type": ["Rock", "Poison"], "rarity": "Common", "personality": "Defensive",
        "description": "A hunched, crab-like creature whose shell is a patchwork of calcified rock and oozing dark sludge. Its claws drip with a corrosive substance that slowly eats through anything they touch.",
        "is_gloom_touched": True,
        "base_capture_rate": 40,
        "passive_ability": {"name": "Lingering Gloom",
                            "description": "Stat-lowering debuffs applied by this pet last for one extra turn."},
        "skill_tree": {
            "1": ["pound", "poison_sting"],
            "5": ["rotten_grasp"],
            "10": {"choice": ["harden", "corrosive_gaze"]}
        },
        "base_stat_ranges": {"hp": [45, 50], "attack": [35, 40], "defense": [50, 55], "special_attack": [20, 25],
                             "special_defense": [40, 45], "speed": [20, 25]},
        "growth_rates": {"hp": 2.2, "attack": 1.3, "defense": 2.1, "special_attack": 0.8, "special_defense": 1.7,
                         "speed": 0.7},

        # --- EVOLUTIONS ARE NOW NESTED ---
        "evolutions": {
            "Grimplate": {
                "evolves_at": 15,
                "species": "Grimplate", "pet_type": ["Rock", "Poison"], "rarity": "Uncommon",
                "description": "A larger, more heavily armored successor to the Corroder. Its shell has fused into dense, layered rock, and the toxic sludge it secretes has thickened into a viscous, slow-dripping poison.",
                "base_stat_ranges": {"hp": [60, 65], "attack": [45, 50], "defense": [70, 75],
                                     "special_attack": [35, 40],
                                     "special_defense": [55, 60], "speed": [25, 30]},
                "growth_rates": {"hp": 2.5, "attack": 1.6, "defense": 2.5, "special_attack": 1.2,
                                 "special_defense": 2.0,
                                 "speed": 0.9},
                "skill_tree": {
                    "18": ["acid_armor"],
                    "22": {"choice": ["sludge_bomb", "venomous_erosion"]},
                    "25": ["miasmal_aura"]
                },
                "evolutions": {
                    "Blightcrust": {
                        "evolves_at": 30,
                        "species": "Blightcrust", "pet_type": ["Rock", "Poison"], "rarity": "Rare",
                        "description": "A towering construct of fused bones and hardened sludge, shaped by years of Gloom exposure into something ancient and terrifying. It moves slowly but radiates an aura of decay that withers anything that lingers too close.",
                        "base_stat_ranges": {"hp": [80, 85], "attack": [70, 75], "defense": [110, 115],
                                             "special_attack": [50, 55],
                                             "special_defense": [90, 95], "speed": [35, 40]},
                        "growth_rates": {"hp": 2.8, "attack": 2.3, "defense": 3.0, "special_attack": 1.5,
                                         "special_defense": 2.5,
                                         "speed": 1.2},
                        "skill_tree": {
                            "35": {"choice": ["bone_shatter", "sorrowful_strike", "seismic_slam"]},
                            "40": ["ossuary_aegis"],
                            "50": {"choice": ["contagious_blight", "earthbind"]},
                            "60": ["caustic_venom"]
                        }
                    }
                }
            }
        }
    },

    # --- Whisperwood Grove Pets ---
    "Mossling": {
        "species": "Mossling",
        "pet_type": "Grass",
        "rarity": "Common",
        "personality": "Timid",
        "description": "A small, moss-covered creature that blends seamlessly into the forest floor. Its timid nature means it will flee at the first sign of danger, but it becomes surprisingly resilient when cornered.",
        "base_capture_rate": 45,
        "passive_ability": {
            "name": "Camouflage",
            "description": "This pet's natural forest colouring gives it a 10% chance to evade incoming attacks."
        },
        "base_stat_ranges": {"hp": [40, 45], "attack": [20, 25], "defense": [35, 40], "special_attack": [30, 35],
                             "special_defense": [35, 40], "speed": [30, 35]},
        "growth_rates": {"hp": 1.8, "attack": 1.1, "defense": 1.7, "special_attack": 1.4, "special_defense": 1.6,
                         "speed": 1.5},
        "skill_tree": {
            "1": ["pound", "leaf_slap"],
            "6": ["moss_shield"],
            "10": ["barbed_spores"],
            "13": {"choice": ["grasping_briar", "leech_seed"]}
        },
        "evolutions": {
            "Thornmoss": {
                "evolves_at": 14,
                "species": "Thornmoss",
                "pet_type": ["Grass", "Rock"],
                "rarity": "Uncommon",
                "description": "As Mossling matures, its soft coat hardens into a dense layer of moss-covered rock. Sharp thorns protrude from its back, and it carries itself with a quiet, unmovable confidence.",
                "passive_ability": {
                    "name": "Thorn Guard",
                    "description": "Attackers who make direct physical contact take a small amount of Grass-type damage."
                },
                "base_stat_ranges": {"hp": [58, 63], "attack": [32, 37], "defense": [58, 63], "special_attack": [45, 50],
                                     "special_defense": [55, 60], "speed": [35, 40]},
                "growth_rates": {"hp": 2.1, "attack": 1.4, "defense": 2.2, "special_attack": 1.7, "special_defense": 2.0,
                                 "speed": 1.5},
                "skill_tree": {
                    "16": ["ironbark"],
                    "20": ["leech_seed"],
                    "24": ["rock_slide"],
                    "27": {"choice": ["nature_shield", "branch_whip"]}
                },
                "evolutions": {
                    "Ferngale": {
                        "evolves_at": 28,
                        "species": "Ferngale",
                        "pet_type": ["Grass", "Rock"],
                        "rarity": "Rare",
                        "description": "An ancient, towering form wrapped in layers of living stone and cascading fern. Ferngale moves slowly but commands the battlefield with a primal authority — the forest itself seems to bend around it.",
                        "passive_ability": {
                            "name": "Ancient Growth",
                            "description": "At the end of each turn, this pet restores 5% of its max HP as moss and fern slowly regenerate its wounds."
                        },
                        "base_stat_ranges": {"hp": [80, 85], "attack": [50, 55], "defense": [95, 100], "special_attack": [65, 70],
                                             "special_defense": [85, 90], "speed": [40, 45]},
                        "growth_rates": {"hp": 2.5, "attack": 1.7, "defense": 2.8, "special_attack": 2.0, "special_defense": 2.5,
                                         "speed": 1.6},
                        "skill_tree": {
                            "30": ["wood_hammer"],
                            "35": ["barbed_spores"],
                            "40": {"choice": ["grasping_briar", "moss_shield"]},
                            "50": ["branch_whip"],
                            "60": ["ironbark"]
                        }
                    }
                }
            }
        }
    },

    "Glimmerva": {
        "species": "Glimmerva",
        "pet_type": "Bug",
        "rarity": "Common",
        "personality": "Timid",
        "description": "A soft-bodied, wingless larva covered in fine, glowing scales. It clings to sun-warmed leaves and bark, pulsing faintly with light when disturbed. Slow and harmless-looking, but the dust it sheds when threatened can be surprisingly disorienting.",
        "base_capture_rate": 50,
        "passive_ability": {
            "name": "Powder Scales",
            "description": "When this pet is hit by a physical attack, there is a 20% chance the attacker is left Confused by a cloud of urticating light-dust shaken loose from its scales."
        },
        "base_stat_ranges": {"hp": [35, 40], "attack": [25, 30], "defense": [25, 30], "special_attack": [40, 45],
                             "special_defense": [35, 40], "speed": [40, 45]},
        "growth_rates": {"hp": 1.6, "attack": 1.2, "defense": 1.2, "special_attack": 1.9, "special_defense": 1.6,
                         "speed": 2.0},
        "skill_tree": {
            "1": ["pound", "barbed_spores"],
            "5": ["bug_buzz"],
            "9": ["gust"],
            "13": {"choice": ["leaf_slap", "infestation"]}
        },
        "evolutions": {
            "Luminara": {
                "evolves_at": 15,
                "species": "Luminara",
                "pet_type": ["Bug"],
                "rarity": "Uncommon",
                "description": "Freshly emerged from its cocoon, Luminara's wings are still soft and unfolding, glimmering faintly even in shade. It moves in short, fluttering bursts, not yet trusting its new wings, but already drawn toward warmth and light.",
                "passive_ability": {
                    "name": "Gilded Wings",
                    "description": "In daylight, this pet's Special Attack is slightly increased, and its half-formed wings shed drifting light-motes that briefly distract attackers."
                },
                "base_stat_ranges": {"hp": [55, 60], "attack": [35, 40], "defense": [38, 43], "special_attack": [65, 70],
                                     "special_defense": [55, 60], "speed": [60, 65]},
                "growth_rates": {"hp": 2.0, "attack": 1.5, "defense": 1.5, "special_attack": 2.4, "special_defense": 2.0,
                                 "speed": 2.3},
                "skill_tree": {
                    "17": ["bug_buzz"],
                    "21": ["barbed_spores"],
                    "26": {"choice": ["accelerated_decay", "gust"]},
                    "30": ["dazzling_gleam"]
                },
                "evolutions": {
                    "Solarmoth": {
                        "evolves_at": 30,
                        "species": "Solarmoth",
                        "pet_type": ["Bug", "Fire"],
                        "rarity": "Rare",
                        "description": "Its metamorphosis complete, Solarmoth's wings have unfurled into great radiant fans that seem to burn with trapped sunlight. It glides rather than flutters now, leaving faint trails of warmth in the air, and even at night its wings continue to glow like embers.",
                        "passive_ability": {
                            "name": "Radiant Core",
                            "description": "This pet's Special Attack is permanently boosted by 10%. At night, its core burns brighter against the dark, doubling the boost to 20%."
                        },
                        "base_stat_ranges": {"hp": [75, 80], "attack": [55, 60], "defense": [58, 63], "special_attack": [95, 100],
                                             "special_defense": [78, 83], "speed": [85, 90]},
                        "growth_rates": {"hp": 2.6, "attack": 2.0, "defense": 1.9, "special_attack": 3.4,
                                         "special_defense": 2.6, "speed": 2.8},
                        "skill_tree": {
                            "32": ["cinder_trap"],
                            "38": {"choice": ["bug_buzz", "fireball"]},
                            "45": ["dazzling_gleam"]
                        }
                    }
                }
            }
        }
    },

    "Grimweave": {
        "species": "Grimweave",
        "pet_type": ["Ghost", "Poison"],
        "rarity": "Uncommon",
        "personality": "Aggressive",
        "description": "A shadowy, arachnid-like creature that weaves webs of Gloom-infused silk between the trees at night. Its presence makes the air feel cold and heavy, and the faint glow of its eyes is often the only warning before it strikes.",
        "base_capture_rate": 35,
        "is_gloom_touched": True,
        "passive_ability": {
            "name": "Veil of Dread",
            "description": "At the start of battle, this pet's unsettling aura lowers the opponent's Special Defense by 5%."
        },
        "base_stat_ranges": {"hp": [40, 45], "attack": [42, 47], "defense": [30, 35], "special_attack": [48, 53],
                             "special_defense": [35, 40], "speed": [38, 43]},
        "growth_rates": {"hp": 1.8, "attack": 2.0, "defense": 1.3, "special_attack": 2.1, "special_defense": 1.5,
                         "speed": 1.8},
        "skill_tree": {
            "1": ["poison_sting", "rotten_grasp"],
            "6": ["venomous_haze"],
            "10": ["siphon_sorrow"],
            "14": {"choice": ["umbral_shift", "grudge"]}
        },
        "evolutions": {
            "Duskspinner": {
                "evolves_at": 16,
                "species": "Duskspinner",
                "pet_type": ["Ghost", "Poison"],
                "rarity": "Rare",
                "description": "A larger, more terrifying form that wraps itself in a shroud of writhing Gloom-silk. Its eight limbs move with unsettling precision, and the webs it spins can trap both body and spirit.",
                "passive_ability": {
                    "name": "Soul Snare",
                    "description": "This pet's Status-type moves have a 15% higher chance of inflicting their effects."
                },
                "base_stat_ranges": {"hp": [60, 65], "attack": [60, 65], "defense": [45, 50], "special_attack": [72, 77],
                                     "special_defense": [52, 57], "speed": [55, 60]},
                "growth_rates": {"hp": 2.2, "attack": 2.3, "defense": 1.7, "special_attack": 2.6, "special_defense": 1.9,
                                 "speed": 2.1},
                "skill_tree": {
                    "18": ["corrosive_gaze"],
                    "22": ["caustic_venom"],
                    "27": {"choice": ["sludge_bomb", "venomous_erosion"]},
                    "32": ["soulrend"]
                },
                "evolutions": {
                    "Veilmother": {
                        "evolves_at": 30,
                        "species": "Veilmother",
                        "pet_type": ["Ghost", "Poison"],
                        "rarity": "Ancient",
                        "is_gloom_touched": True,
                        "description": (
                            "The final form of the Grimweave line. Lives on the east wall face "
                            "of the Weeping Chasm, passive and vast. Doesn't hunt — waits. "
                            "Everything that falls into the chasm finds its web. The east wall "
                            "webbing is visible from the Chasm's Edge. Capturable only at "
                            "Legend rank, theoretically."
                        ),
                        "base_capture_rate": 2,
                        "passive_ability": {
                            "name": "Endless Web",
                            "description": "At battle start, the opponent's speed is reduced by 20% and cannot be increased.",
                        },
                        "base_stat_ranges": {"hp": [90, 96], "attack": [82, 88], "defense": [65, 71],
                                             "special_attack": [105, 111], "special_defense": [78, 84], "speed": [70, 76]},
                        "growth_rates": {"hp": 2.8, "attack": 2.6, "defense": 2.0, "special_attack": 3.2,
                                         "special_defense": 2.4, "speed": 2.2},
                        "skill_tree": {
                            "32": ["soulrend"],
                            "38": {"choice": ["umbral_shift", "venomous_erosion"]},
                            "45": ["miasmal_aura"],
                        },
                    }
                }
            }
        }
    },

    "Moonwisp": {
        "species": "Moonwisp",
        "pet_type": ["Fairy", "Grass"],
        "rarity": "Uncommon",
        "personality": "Tactical",
        "description": "A tiny, luminescent creature that dances among moonlit flowers in the depths of Whisperwood. Gentle by nature, it uses its fae magic to confound and disorient those who threaten its home rather than fighting directly.",
        "base_capture_rate": 35,
        "passive_ability": {
            "name": "Lunar Bloom",
            "description": "Under moonlight (night encounters), this pet's Fairy-type moves deal 10% more damage."
        },
        "base_stat_ranges": {"hp": [38, 43], "attack": [22, 27], "defense": [32, 37], "special_attack": [50, 55],
                             "special_defense": [48, 53], "speed": [35, 40]},
        "growth_rates": {"hp": 1.7, "attack": 1.1, "defense": 1.5, "special_attack": 2.2, "special_defense": 2.0,
                         "speed": 1.6},
        "skill_tree": {
            "1": ["pound", "moss_shield"],
            "5": ["dazzling_gleam"],
            "9": ["blessing_of_aethelgard"],
            "13": {"choice": ["spirit_blessing", "karma_weave"]}
        },
        "evolutions": {
            "Lunarblossom": {
                "evolves_at": 15,
                "species": "Lunarblossom",
                "pet_type": ["Fairy", "Grass"],
                "rarity": "Rare",
                "description": "A graceful, flower-crowned being that radiates a soft silver light. It moves as if weightless, leaving a faint trail of glowing petals wherever it steps. Its fae magic has deepened into something ancient and difficult to resist.",
                "passive_ability": {
                    "name": "Moonlit Grace",
                    "description": "This pet has a 15% chance to evade incoming attacks, and its evasion increases to 25% during night encounters."
                },
                "base_stat_ranges": {"hp": [58, 63], "attack": [32, 37], "defense": [50, 55], "special_attack": [78, 83],
                                     "special_defense": [72, 77], "speed": [52, 57]},
                "growth_rates": {"hp": 2.1, "attack": 1.4, "defense": 1.8, "special_attack": 2.7, "special_defense": 2.4,
                                 "speed": 2.0},
                "skill_tree": {
                    "17": ["dazzling_gleam"],
                    "21": ["grasping_briar"],
                    "26": {"choice": ["karma_weave", "spirit_blessing"]},
                    "30": ["precognition"]
                }
            }
        }
    },

    "Serpentine": {
        "species": "Serpentine",
        "pet_type": ["Grass", "Dark"],
        "rarity": "Uncommon",
        "personality": "Tactical",
        "description": "A slender, vine-like serpent that moves silently through the underbrush, its scales shifting between deep green and shadow depending on the light. It prefers to watch from cover for long stretches before ever striking.",
        "base_capture_rate": 35,
        "passive_ability": {
            "name": "Shifting Scales",
            "description": "While in shaded or low-light conditions (night encounters), this pet's Defense is slightly increased."
        },
        "base_stat_ranges": {"hp": [42, 47], "attack": [48, 53], "defense": [35, 40], "special_attack": [40, 45],
                             "special_defense": [38, 43], "speed": [55, 60]},
        "growth_rates": {"hp": 1.9, "attack": 2.2, "defense": 1.5, "special_attack": 1.8, "special_defense": 1.7,
                         "speed": 2.3},
        "skill_tree": {
            "1": ["scratch", "leaf_slap"],
            "6": ["leech_seed"],
            "10": ["umbral_shift"],
            "14": {"choice": ["branch_whip", "grudge"]}
        },
        "evolutions": {
            "Serpumbra": {
                "evolves_at": 20,
                "species": "Serpumbra",
                "pet_type": ["Grass", "Dark"],
                "rarity": "Rare",
                "description": "Serpentine's final form — a long, shadow-wreathed serpent whose scales seem to drink in the light around it. In dappled forest shade it can vanish almost entirely, becoming little more than a rustle in the leaves and a pair of watching eyes.",
                "passive_ability": {
                    "name": "Living Camouflage",
                    "description": "At the start of battle, this pet has a 25% chance to avoid the opponent's first attack entirely, vanishing into the surrounding cover."
                },
                "base_stat_ranges": {"hp": [62, 67], "attack": [70, 75], "defense": [52, 57], "special_attack": [60, 65],
                                     "special_defense": [58, 63], "speed": [80, 85]},
                "growth_rates": {"hp": 2.4, "attack": 2.8, "defense": 2.0, "special_attack": 2.3, "special_defense": 2.2,
                                 "speed": 2.9},
                "skill_tree": {
                    "22": ["umbral_shift"],
                    "26": ["branch_whip"],
                    "31": {"choice": ["grudge", "sorrowful_strike"]},
                    "36": ["soulrend"]
                }
            }
        }
    },

    "Glamorose": {
        "species": "Glamorose",
        "pet_type": ["Grass", "Poison"],
        "rarity": "Common",
        "personality": "Tactical",
        "description": "A small, flower-headed creature with petals of an almost unnaturally vivid pink. Its sweet fragrance draws other creatures close — a little too close, and a little too often for it to be entirely accidental.",
        "base_capture_rate": 45,
        "passive_ability": {
            "name": "Toxic Bloom",
            "description": "When this pet is hit by a physical attack, there is a 15% chance the attacker is left Poisoned by pollen released from its petals."
        },
        "base_stat_ranges": {"hp": [38, 43], "attack": [28, 33], "defense": [30, 35], "special_attack": [42, 47],
                             "special_defense": [40, 45], "speed": [32, 37]},
        "growth_rates": {"hp": 1.7, "attack": 1.3, "defense": 1.5, "special_attack": 1.9, "special_defense": 1.8,
                         "speed": 1.4},
        "skill_tree": {
            "1": ["pound", "poison_sting"],
            "5": ["leech_seed"],
            "9": ["acid_armor"],
            "13": {"choice": ["sludge_bomb", "barbed_spores"]}
        },
        "evolutions": {
            "Malicea": {
                "evolves_at": 18,
                "species": "Malicea",
                "pet_type": ["Grass", "Poison"],
                "rarity": "Uncommon",
                "description": "Malicea's petals have unfurled wider and its fragrance grown richer — sweeter, even, the closer one gets to the soft rot at its core. Things that wander too near tend to linger longer than they mean to.",
                "passive_ability": {
                    "name": "Sweet Decay",
                    "description": "At the end of each turn, the opponent loses a small amount of HP, lulled into lingering near this pet's fragrance, while this pet recovers a portion of that HP."
                },
                "base_stat_ranges": {"hp": [58, 63], "attack": [48, 53], "defense": [48, 53], "special_attack": [68, 73],
                                     "special_defense": [62, 67], "speed": [50, 55]},
                "growth_rates": {"hp": 2.1, "attack": 1.7, "defense": 1.9, "special_attack": 2.4, "special_defense": 2.3,
                                 "speed": 1.8},
                "skill_tree": {
                    "20": ["sludge_bomb"],
                    "24": ["corrosive_gaze"],
                    "28": {"choice": ["contagious_blight", "leech_seed"]},
                    "33": ["miasmal_aura"]
                },
                "evolutions": {
                    "Aberraflora": {
                        "evolves_at": 38,
                        "species": "Aberraflora",
                        "pet_type": ["Grass", "Poison"],
                        "rarity": "Ancient",
                        "description": (
                            "The final form of the Glamorose line. A sprawling mass of bloom and "
                            "rot, half-buried in the deep Thicket where the canopy never quite "
                            "lets in the light. Its fragrance carries for a long way, and "
                            "everything that follows it eventually stops moving. Capturable "
                            "only at Legend rank, theoretically."
                        ),
                        "base_capture_rate": 2,
                        "passive_ability": {
                            "name": "Bloom of Ruin",
                            "description": "At the end of each turn, the opponent loses a portion of their max HP to drifting toxic pollen, and this pet recovers a portion of that HP."
                        },
                        "base_stat_ranges": {"hp": [88, 94], "attack": [70, 76], "defense": [75, 81],
                                             "special_attack": [100, 106], "special_defense": [95, 101], "speed": [65, 71]},
                        "growth_rates": {"hp": 2.7, "attack": 2.3, "defense": 2.5, "special_attack": 3.3,
                                         "special_defense": 3.0, "speed": 2.0},
                        "skill_tree": {
                            "40": ["miasmal_aura"],
                            "46": {"choice": ["sludge_bomb", "contagious_blight"]},
                            "52": ["acid_armor"],
                        }
                    }
                }
            }
        }
    },

    "Verdanthorn": {
        "species": "Verdanthorn",
        "pet_type": ["Grass", "Normal"],
        "rarity": "Ancient",
        "personality": "Defensive",
        "description": (
            "An ancient, towering presence at the heart of the Thicket — easy to mistake "
            "for a particularly old tree until it shifts, slowly, and you realize it has "
            "been watching you the entire time. It rarely moves and rarely needs to. "
            "Capturable only at Legend rank, theoretically."
        ),
        "base_capture_rate": 2,
        "passive_ability": {
            "name": "Stillness",
            "description": "While this pet does not act on its turn, it restores a portion of its HP and gains a stacking Defense boost. Acting resets the bonus."
        },
        "base_stat_ranges": {"hp": [100, 108], "attack": [60, 66], "defense": [100, 106], "special_attack": [55, 61],
                             "special_defense": [90, 96], "speed": [20, 26]},
        "growth_rates": {"hp": 3.2, "attack": 1.8, "defense": 3.0, "special_attack": 1.7, "special_defense": 2.8,
                         "speed": 1.0},
        "skill_tree": {
            "1": ["harden", "leech_seed"],
            "30": ["wood_hammer"],
            "40": {"choice": ["nature_shield", "earthen_bulwark"]},
            "50": ["ironbark"]
        }
    },

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # The Ashen Verge (Whisperwood Grove remnant)
    # -------------------------------------------------------------------------

    "Cinderkit": {
        "species": "Cinderkit",
        "pet_type": "Fire",
        "rarity": "Common",
        "personality": "Timid",
        "description": (
            "A small fox-kit-like creature with ash-gray fur and faint ember-orange "
            "streaks running along its spine and tail-tip. Curls up near warm ash to "
            "sleep — looks like a smudge of soot until it moves. Big ears, low body "
            "heat except for the glowing streaks."
        ),
        "base_capture_rate": 45,
        "passive_ability": {
            "name": "Ember Curl",
            "description": "This pet generates its own warmth, granting it small resistance to energy loss from cold-related hazards."
        },
        "base_stat_ranges": {"hp": [38, 43], "attack": [35, 40], "defense": [30, 35], "special_attack": [35, 40],
                             "special_defense": [30, 35], "speed": [42, 47]},
        "growth_rates": {"hp": 1.6, "attack": 1.7, "defense": 1.3, "special_attack": 1.5, "special_defense": 1.3,
                         "speed": 1.8},
        "skill_tree": {
            "1": ["scratch", "ember"],
            "6": ["scorch"],
            "11": {"choice": ["fire_fang", "headbutt"]}
        },
        "evolutions": {
            "Ashveil": {
                "evolves_at": 16,
                "species": "Ashveil",
                "pet_type": "Fire",
                "rarity": "Uncommon",
                "description": (
                    "Bigger and leaner than Cinderkit. The ember streaks have become "
                    "trailing wisps of smoke and ash that drift behind it as it moves, "
                    "partially obscuring its silhouette — genuinely a little hard to "
                    "track. Embers glow through the haze when it's alert."
                ),
                "passive_ability": {
                    "name": "Ash Shroud",
                    "description": "This pet's trailing haze of smoke and ash grants it a small chance to evade incoming attacks."
                },
                "base_stat_ranges": {"hp": [55, 60], "attack": [55, 60], "defense": [45, 50], "special_attack": [52, 57],
                                     "special_defense": [45, 50], "speed": [62, 67]},
                "growth_rates": {"hp": 2.0, "attack": 2.2, "defense": 1.7, "special_attack": 2.0, "special_defense": 1.7,
                                 "speed": 2.4},
                "skill_tree": {
                    "18": ["fireball"],
                    "23": ["fire_fang"],
                    "28": {"choice": ["immolate", "cinder_trap"]}
                }
            }
        }
    },

    "Tindertail": {
        "species": "Tindertail",
        "pet_type": "Fire",
        "rarity": "Uncommon",
        "personality": "Tactical",
        "description": (
            "A small, quick, alert creature — more scout than fighter. Slim, "
            "weasel-like, with a single ember permanently lit at the very tip of its "
            "tail, once used to relight dead fire-rings. Its ears are always twitching, "
            "as if listening for something just out of range."
        ),
        "base_capture_rate": 30,
        "passive_ability": {
            "name": "Boundary Sense",
            "description": "This pet has a small chance to sense danger coming and avoid the outcome of a hazard entirely."
        },
        "base_stat_ranges": {"hp": [42, 47], "attack": [38, 43], "defense": [35, 40], "special_attack": [55, 60],
                             "special_defense": [48, 53], "speed": [68, 73]},
        "growth_rates": {"hp": 1.7, "attack": 1.5, "defense": 1.4, "special_attack": 2.2, "special_defense": 1.9,
                         "speed": 2.6},
        "skill_tree": {
            "1": ["scratch", "ember"],
            "8": ["scorch"],
            "14": {"choice": ["fireball", "fire_fang"]},
            "20": ["cinder_trap"]
        }
    },

    "Smolderoot": {
        "species": "Smolderoot",
        "pet_type": ["Grass", "Fire"],
        "rarity": "Uncommon",
        "personality": "Defensive",
        "description": (
            "Looks like a charred sapling that somehow kept growing — blackened "
            "bark-skin with one thin vein of orange-red glow running through it like "
            "lava in stone. Stiff and slow-moving, with a faint trail of smoke when "
            "it 'breathes.'"
        ),
        "base_capture_rate": 30,
        "passive_ability": {
            "name": "Smolder",
            "description": "This pet is quietly, permanently smoldering. Its physical attacks have a small chance to inflict a minor burn on the opponent."
        },
        "base_stat_ranges": {"hp": [58, 64], "attack": [50, 56], "defense": [55, 61], "special_attack": [48, 54],
                             "special_defense": [50, 56], "speed": [25, 30]},
        "growth_rates": {"hp": 2.2, "attack": 1.9, "defense": 2.1, "special_attack": 1.8, "special_defense": 2.0,
                         "speed": 1.0},
        "skill_tree": {
            "1": ["pound", "ember"],
            "9": ["leaf_slap"],
            "15": {"choice": ["scorch", "branch_whip"]}
        },
        "evolutions": {
            "Pyrethorn": {
                "evolves_at": 30,
                "species": "Pyrethorn",
                "pet_type": ["Grass", "Fire"],
                "rarity": "Rare",
                "description": (
                    "Smolderoot's larger form — gnarled, root-legged, hunched, walking "
                    "on four thorned root-limbs with low flame constantly licking along "
                    "its back like a smoldering log. It leaves smoking footprints behind "
                    "it, like part of the burned forest got up and started walking."
                ),
                "passive_ability": {
                    "name": "Wildfire Roots",
                    "description": "An upgraded form of Smolder — higher chance to inflict burn, with greater burn damage. This pet also recovers a small amount of HP at the end of each turn, sustained by its own slow-burning core."
                },
                "base_stat_ranges": {"hp": [85, 92], "attack": [78, 85], "defense": [80, 87], "special_attack": [68, 75],
                                     "special_defense": [72, 79], "speed": [35, 40]},
                "growth_rates": {"hp": 2.8, "attack": 2.6, "defense": 2.8, "special_attack": 2.4, "special_defense": 2.6,
                                 "speed": 1.4},
                "skill_tree": {
                    "32": ["fireball"],
                    "38": {"choice": ["wood_hammer", "immolate"]},
                    "45": ["cinder_trap"]
                }
            }
        }
    },

    "Cindermaw": {
        "species": "Cindermaw",
        "pet_type": ["Grass", "Fire"],
        "rarity": "Ancient",
        "personality": "Defensive",
        "description": (
            "A massive, mostly inert charred root-mass, half-buried in deep ash at "
            "The First Ring. Looks like a dead, fused tangle of burned roots — until "
            "you notice the single faint ember glow deep within, like a heartbeat "
            "that's almost stopped. It doesn't visibly breathe. "
            "Capturable only at Legend rank, theoretically."
        ),
        "base_capture_rate": 2,
        "passive_ability": {
            "name": "Ash Lock",
            "description": "For the duration of the battle, the opponent's healing effectiveness is reduced. Whatever this corruption touches doesn't recover cleanly."
        },
        "base_stat_ranges": {"hp": [100, 108], "attack": [85, 92], "defense": [95, 102], "special_attack": [80, 87],
                             "special_defense": [88, 95], "speed": [30, 36]},
        "growth_rates": {"hp": 3.2, "attack": 2.8, "defense": 3.0, "special_attack": 2.6, "special_defense": 2.8,
                         "speed": 1.2},
        "skill_tree": {
            "1": ["pound", "ember"],
            "30": ["immolate"],
            "40": {"choice": ["cinder_trap", "wood_hammer"]},
            "50": ["overwhelm"]
        }
    },

    "Pyrehart": {
        "species": "Pyrehart",
        "pet_type": "Fire",
        "rarity": "Ancient",
        "personality": "Aggressive",
        "description": (
            "A large, lion-or-wolf-shaped guardian, its 'fur' made of slow-moving "
            "embers and ash rather than hair — like a campfire holding the shape of "
            "an animal. Visibly scarred and dimmer than it should be, with patches "
            "where the ember-fur has gone cold and gray. Sleeps curled near The First "
            "Ring. Capturable only at Legend rank, theoretically."
        ),
        "base_capture_rate": 2,
        "passive_ability": {
            "name": "Last Light",
            "description": "This pet's Attack and Defense increase as its own HP drops, fighting hardest when it matters most."
        },
        "base_stat_ranges": {"hp": [95, 102], "attack": [100, 108], "defense": [75, 82], "special_attack": [70, 77],
                             "special_defense": [75, 82], "speed": [78, 85]},
        "growth_rates": {"hp": 3.0, "attack": 3.4, "defense": 2.4, "special_attack": 2.2, "special_defense": 2.4,
                         "speed": 2.6},
        "skill_tree": {
            "1": ["scratch", "ember"],
            "30": ["fire_fang"],
            "40": {"choice": ["fireball", "immolate"]},
            "50": ["overwhelm"]
        }
    },

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # The Weeping Root
    # -------------------------------------------------------------------------

    "Stillroot": {
        "species": "Stillroot", "pet_type": ["Rock", "Grass"], "rarity": "Common",
        "personality": "Steadfast",
        "is_gloom_touched": True,
        "description": (
            "A small root-and-moss creature with patches of genuine stone-like "
            "growth spreading across its body — like lichen-covered rock fused "
            "onto living moss. Fully mobile and alert; the calcified patches "
            "haven't progressed in a long time, and likely never will. Touched, "
            "Calcifying — frozen, not failing."
        ),
        "base_capture_rate": 42,
        "passive_ability": {
            "name": "Stonecrust",
            "description": "Bonus passive Defense from calcified plating, with no Speed penalty.",
        },
        "base_stat_ranges": {
            "hp": [42, 48], "attack": [22, 27], "defense": [50, 55],
            "special_attack": [25, 30], "special_defense": [45, 50], "speed": [30, 35],
        },
        "growth_rates": {
            "hp": 1.9, "attack": 1.2, "defense": 2.3, "special_attack": 1.3,
            "special_defense": 2.0, "speed": 1.4,
        },
        "skill_tree": {
            "1": ["pound", "harden"],
            "6": ["rock_throw"],
            "10": ["leech_seed"],
            "14": {"choice": ["iron_defense", "rock_slide"]},
        },
    },

    "Veinglow": {
        "species": "Veinglow", "pet_type": ["Poison", "Grass"], "rarity": "Uncommon",
        "personality": "Cautious",
        "is_gloom_touched": False,
        "description": (
            "A small, eel-like creature that lives directly within the sap-veins, "
            "bioluminescent in the same bruised-purple as its surroundings. Its "
            "glow brightens briefly when it notices something approaching, then "
            "gradually fades as it settles back into stillness. Not "
            "Gloom-touched — its body chemistry has adapted to neutralize the "
            "toxic sap rather than being afflicted by it."
        ),
        "base_capture_rate": 32,
        "passive_ability": {
            "name": "Neutralize",
            "description": "Small chance to resist or shrug off Poison-type status effects inflicted on this pet.",
        },
        "base_stat_ranges": {
            "hp": [38, 44], "attack": [30, 35], "defense": [28, 33],
            "special_attack": [45, 50], "special_defense": [35, 40], "speed": [50, 55],
        },
        "growth_rates": {
            "hp": 1.6, "attack": 1.4, "defense": 1.2, "special_attack": 2.1,
            "special_defense": 1.6, "speed": 2.3,
        },
        "skill_tree": {
            "1": ["pound", "poison_sting"],
            "8": ["leech_seed"],
            "14": {"choice": ["toxic", "venomous_haze"]},
            "20": ["acid_armor"],
        },
    },

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Weeping Chasm
    # -------------------------------------------------------------------------

    "Gauntling": {
        "species": "Gauntling", "pet_type": ["Ghost", "Normal"], "rarity": "Common",
        "personality": "Timid",
        "is_gloom_touched": True,
        "description": (
            "A creature that has lived too close to the Gloom source for generations. "
            "Not violently corrupted — born already fading. Partially translucent, "
            "slow-moving, like something losing its physical definition over time. "
            "It isn't Hollowed yet. It's on the way there and doesn't know it."
        ),
        "base_capture_rate": 38,
        "passive_ability": {
            "name": "Fading Form",
            "description": "Small chance to phase through incoming physical attacks.",
        },
        "base_stat_ranges": {
            "hp": [35, 40], "attack": [25, 30], "defense": [20, 25],
            "special_attack": [38, 43], "special_defense": [30, 35], "speed": [32, 37],
        },
        "growth_rates": {
            "hp": 1.6, "attack": 1.2, "defense": 1.0, "special_attack": 1.8,
            "special_defense": 1.4, "speed": 1.5,
        },
        "skill_tree": {
            "1": ["pound", "confuse_ray"],
            "6": ["mist"],
            "11": {"choice": ["umbral_shift", "siphon_sorrow"]},
        },
        "evolutions": {
            "Waneling": {
                "evolves_at": 15,
                "species": "Waneling", "pet_type": ["Ghost", "Normal"], "rarity": "Uncommon",
                "is_gloom_touched": True,
                "description": (
                    "Further faded. More ghost than creature now. Barely there. "
                    "Still moves. Still hunts. At this stage it barely registers on "
                    "the eye — you sense it more than see it."
                ),
                "base_stat_ranges": {
                    "hp": [50, 56], "attack": [38, 44], "defense": [30, 36],
                    "special_attack": [58, 64], "special_defense": [46, 52], "speed": [50, 56],
                },
                "growth_rates": {
                    "hp": 2.0, "attack": 1.6, "defense": 1.3, "special_attack": 2.2,
                    "special_defense": 1.8, "speed": 1.9,
                },
                "skill_tree": {
                    "16": ["grudge"],
                    "21": ["soulrend"],
                    "26": {"choice": ["umbral_shift", "precognition"]},
                },
            },
        },
    },

    "Rimecrawl": {
        "species": "Rimecrawl", "pet_type": ["Ice", "Poison"], "rarity": "Uncommon",
        "personality": "Defensive",
        "is_gloom_touched": True,
        "description": (
            "Moves along the chasm walls, slow and methodical. Leaves trails of "
            "frost-laced Gloom residue. Where it passes, the stone gets colder. "
            "You notice the trails before you notice the creature. "
            "Patient. Creeping. Wrong in a quiet way."
        ),
        "base_capture_rate": 28,
        "passive_ability": {
            "name": "Cold Trail",
            "description": "Leaves a frost residue on the field — minor damage and speed reduction to opponents who attack.",
        },
        "base_stat_ranges": {
            "hp": [44, 50], "attack": [30, 36], "defense": [48, 54],
            "special_attack": [42, 48], "special_defense": [44, 50], "speed": [18, 24],
        },
        "growth_rates": {
            "hp": 1.9, "attack": 1.3, "defense": 2.1, "special_attack": 1.8,
            "special_defense": 1.9, "speed": 0.9,
        },
        "skill_tree": {
            "1": ["pound", "poison_sting"],
            "7": ["harden"],
            "13": {"choice": ["acid_armor", "venomous_haze"]},
        },
        "evolutions": {
            "Frostbile": {
                "evolves_at": 16,
                "species": "Frostbile", "pet_type": ["Ice", "Poison"], "rarity": "Rare",
                "is_gloom_touched": True,
                "description": (
                    "Larger, slower. The trail it leaves now crystallizes into something "
                    "that damages anything walking through it. Turns the terrain into a weapon."
                ),
                "base_stat_ranges": {
                    "hp": [65, 71], "attack": [46, 52], "defense": [72, 78],
                    "special_attack": [62, 68], "special_defense": [66, 72], "speed": [14, 20],
                },
                "growth_rates": {
                    "hp": 2.3, "attack": 1.7, "defense": 2.5, "special_attack": 2.2,
                    "special_defense": 2.3, "speed": 0.8,
                },
                "skill_tree": {
                    "17": ["miasmal_aura"],
                    "23": ["caustic_venom"],
                    "28": {"choice": ["venomous_erosion", "contagious_blight"]},
                    "35": ["ossuary_aegis"],
                },
            },
        },
    },

    "Threshling": {
        "species": "Threshling", "pet_type": ["Dark", "Ghost"], "rarity": "Rare",
        "personality": "Aggressive",
        "is_gloom_touched": True,
        "description": (
            "Caught at the threshold between existence and full Gloom consumption. "
            "Parts of it solid, parts of it mist. One eye clear, one eye dark. "
            "Not fully Hollowed — locked in between states. "
            "Gretta caught one at this exact moment and has held it there."
        ),
        "base_capture_rate": 12,
        "passive_ability": {
            "name": "Threshold",
            "description": "Drains a small amount of the opponent's Gloom Meter passively each turn.",
        },
        "base_stat_ranges": {
            "hp": [52, 58], "attack": [58, 64], "defense": [38, 44],
            "special_attack": [55, 61], "special_defense": [42, 48], "speed": [44, 50],
        },
        "growth_rates": {
            "hp": 2.1, "attack": 2.4, "defense": 1.6, "special_attack": 2.2,
            "special_defense": 1.7, "speed": 1.8,
        },
        "skill_tree": {
            "1": ["rotten_grasp", "grudge"],
            "8": ["siphon_sorrow"],
            "15": {"choice": ["umbral_shift", "soulrend"]},
        },
        "evolutions": {
            "Threshbound": {
                "evolves_at": 20,
                "species": "Threshbound", "pet_type": ["Dark", "Ghost"], "rarity": "Ancient",
                "is_gloom_touched": True,
                "description": (
                    "Has been held at the threshold so long it IS the threshold. "
                    "Not because it grew larger, but because it became something that "
                    "defies classification. Barely contained. Seeing one should feel "
                    "like a warning. Gretta has one. Nobody else does."
                ),
                "base_capture_rate": 1,
                "passive_ability": {
                    "name": "Threshold Mastery",
                    "description": "Drains the opponent's Gloom Meter each turn and converts it to HP.",
                },
                "base_stat_ranges": {
                    "hp": [80, 86], "attack": [88, 94], "defense": [58, 64],
                    "special_attack": [82, 88], "special_defense": [62, 68], "speed": [62, 68],
                },
                "growth_rates": {
                    "hp": 2.5, "attack": 2.8, "defense": 2.0, "special_attack": 2.6,
                    "special_defense": 2.1, "speed": 2.2,
                },
                "skill_tree": {
                    "21": ["soulrend"],
                    "26": ["umbral_shift"],
                    "32": {"choice": ["grudge", "sorrowful_strike"]},
                    "40": ["overwhelm"],
                },
            },
        },
    },

    # -------------------------------------------------------------------------
    # Mirefields
    # -------------------------------------------------------------------------

    "Murkback": {
        "species": "Murkback", "pet_type": ["Water", "Ground"], "rarity": "Common",
        "personality": "Defensive",
        "description": (
            "A squat, wide-bodied amphibian armored with a crust of dried mud and silt. "
            "Slow on land, fast in shallow water. Territorial — it won't attack unless "
            "you've stepped into its space, and then it won't stop."
        ),
        "base_capture_rate": 40,
        "passive_ability": {
            "name": "Bog Anchor",
            "description": "Resistant to speed debuffs. Reduced knockback from all sources.",
        },
        "base_stat_ranges": {
            "hp": [48, 54], "attack": [35, 40], "defense": [52, 58],
            "special_attack": [22, 27], "special_defense": [45, 50], "speed": [18, 23],
        },
        "growth_rates": {
            "hp": 2.0, "attack": 1.4, "defense": 2.4, "special_attack": 0.9,
            "special_defense": 1.8, "speed": 0.8,
        },
        "skill_tree": {
            "1": ["pound", "mud_slap"],
            "6": ["water_pulse"],
            "12": {"choice": ["iron_defense", "muddy_water"]},
        },
        "evolutions": {
            "Murkwall": {
                "evolves_at": 15,
                "species": "Murkwall", "pet_type": ["Water", "Ground"], "rarity": "Uncommon",
                "description": (
                    "Larger, slower, and nearly immovable. The hide has thickened into "
                    "layered mud-rock plating. Murkback's territorial instinct has become "
                    "something quieter — it doesn't need to threaten. Everything else "
                    "in the mire already knows to give it room."
                ),
                "base_stat_ranges": {
                    "hp": [72, 78], "attack": [52, 58], "defense": [82, 88],
                    "special_attack": [30, 36], "special_defense": [68, 74], "speed": [14, 19],
                },
                "growth_rates": {
                    "hp": 2.4, "attack": 1.8, "defense": 2.8, "special_attack": 1.0,
                    "special_defense": 2.2, "speed": 0.7,
                },
                "skill_tree": {
                    "16": ["rock_wall"],
                    "20": ["body_slam"],
                    "25": {"choice": ["fortress_stance", "tidal_crush"]},
                    "32": ["unyielding_focus"],
                },
            },
        },
    },

    "Pallefin": {
        "species": "Pallefin", "pet_type": "Water", "rarity": "Uncommon",
        "personality": "Timid",
        "description": (
            "A small, almost translucent creature that skims the water surface without "
            "disturbing it. Disappears into mist when startled. Unusually sensitive to "
            "pressure and temperature — it reacts to changes in the environment before "
            "any instrument does."
        ),
        "base_capture_rate": 28,
        "passive_ability": {
            "name": "Mist Veil",
            "description": "Small evasion chance in fog or night conditions.",
        },
        "base_stat_ranges": {
            "hp": [30, 35], "attack": [20, 25], "defense": [22, 27],
            "special_attack": [45, 51], "special_defense": [38, 44], "speed": [50, 56],
        },
        "growth_rates": {
            "hp": 1.4, "attack": 0.9, "defense": 1.0, "special_attack": 2.0,
            "special_defense": 1.6, "speed": 2.2,
        },
        "skill_tree": {
            "1": ["bubble", "swift"],
            "7": ["mist"],
            "13": {"choice": ["aqua_jet", "confuse_ray"]},
        },
        "evolutions": {
            "Shimmerdeep": {
                "evolves_at": 16,
                "species": "Shimmerdeep", "pet_type": "Water", "rarity": "Rare",
                "description": (
                    "No longer skims the surface — descends. The translucency becomes "
                    "a faint bioluminescence, generating soft light in dark water. "
                    "Less ghost-like, more defined. Still environmentally sensitive, "
                    "but now it draws attention to changes rather than fleeing from them."
                ),
                "base_stat_ranges": {
                    "hp": [48, 54], "attack": [32, 38], "defense": [36, 42],
                    "special_attack": [68, 74], "special_defense": [58, 64], "speed": [65, 71],
                },
                "growth_rates": {
                    "hp": 1.8, "attack": 1.2, "defense": 1.4, "special_attack": 2.4,
                    "special_defense": 2.0, "speed": 2.6,
                },
                "skill_tree": {
                    "17": ["water_pulse"],
                    "22": ["aurora_beam"],
                    "27": {"choice": ["deep_current", "flash"]},
                    "34": ["hydro_pump"],
                },
            },
        },
    },

    "Siltborn": {
        "species": "Siltborn", "pet_type": ["Poison", "Grass"], "rarity": "Rare",
        "personality": "Aggressive",
        "is_gloom_touched": False,
        "description": (
            "A roughly creature-shaped mass of compressed reeds, root tangles, and dark "
            "silt. Low to the ground, slow, nearly indistinguishable from the bog floor "
            "until it moves. Not Gloom-touched — the mire's wrongness is ancient and "
            "organic. Ancient-feeling even as a young specimen. Night only."
        ),
        "base_capture_rate": 18,
        "passive_ability": {
            "name": "Reclaim",
            "description": "Recovers a small amount of HP at the end of each turn. The bog sustains it.",
        },
        "base_stat_ranges": {
            "hp": [55, 61], "attack": [48, 54], "defense": [44, 50],
            "special_attack": [36, 42], "special_defense": [40, 46], "speed": [16, 21],
        },
        "growth_rates": {
            "hp": 2.2, "attack": 2.0, "defense": 1.8, "special_attack": 1.4,
            "special_defense": 1.6, "speed": 0.8,
        },
        "skill_tree": {
            "1": ["pound", "poison_sting"],
            "8": ["vine_whip"],
            "14": {"choice": ["toxic", "leech_seed"]},
        },
        "evolutions": {
            "Mirewarden": {
                "evolves_at": 18,
                "species": "Mirewarden", "pet_type": ["Poison", "Grass"], "rarity": "Very Rare",
                "is_gloom_touched": False,
                "description": (
                    "Larger, denser. Reeds and roots have grown through it, not just "
                    "coating it. Moves slower but hits like the terrain itself shifted. "
                    "No longer blends in — looks like a landmark that happens to move. "
                    "The Old Crossroads Mirewarden is implied to be beyond even this stage."
                ),
                "base_stat_ranges": {
                    "hp": [82, 88], "attack": [72, 78], "defense": [66, 72],
                    "special_attack": [50, 56], "special_defense": [60, 66], "speed": [12, 17],
                },
                "growth_rates": {
                    "hp": 2.6, "attack": 2.4, "defense": 2.2, "special_attack": 1.6,
                    "special_defense": 2.0, "speed": 0.7,
                },
                "skill_tree": {
                    "19": ["poison_fang"],
                    "24": ["power_whip"],
                    "29": {"choice": ["toxic_spikes", "sludge_bomb"]},
                    "36": ["overwhelm"],
                },
            },
        },
    },
}

# =================================================================================
#  FLAT SPECIES LOOKUP
# =================================================================================
# Flattened version of PET_DATABASE that includes all evolutions by species name.
# Use get_pet_data(species) anywhere you need to look up a pet including evolved forms.

def _build_flat_lookup(db: dict) -> dict:
    lookup = {}
    def _add(data):
        species = data.get("species")
        if species:
            lookup[species] = data
        for evo in data.get("evolutions", {}).values():
            _add(evo)
    for pet in db.values():
        _add(pet)
    return lookup

PET_LOOKUP = _build_flat_lookup(PET_DATABASE)

def get_pet_data(species: str) -> dict:
    """Returns full pet data for any species, including evolved forms. Returns {} if not found."""
    return PET_LOOKUP.get(species, {})


# =================================================================================
#  ENCOUNTER TABLES
# =================================================================================
# This dictionary defines WHICH pets can be found WHERE and WHEN.
# It simply refers to the pet's name from the PET_DATABASE above.
# This solves the data duplication problem.

ENCOUNTER_TABLES = {

    "outpostWilds": {
        "day": ["Bristlecone", "Bristlecone", "Bristlecone", "Mossling"],   # Mossling ~25% — forest edge glimpse
        "night": ["Bristlecone", "Bristlecone", "Bristlecone", "Mossling"]  # Mossling ~25% — lost
    },
    "oakhavenOutpost_rottingPits": {
        "day": ["Corroder"],
        "night": ["Corroder", "Corroder", "Corroder", "Grimplate"]  # Grimplate ~25% — surfaces after dark
    },
    "whisperwoodGrove": {
        "day": ["Mossling", "Mossling", "Glimmerva", "Glimmerva", "Verdanthorn"],   # Verdanthorn ~20% — ancient, rare sighting
        "night": ["Mossling", "Mossling", "Grimweave", "Moonwisp", "Glamorose", "Glamorose", "Malicea"]  # Malicea ~14% — low-chance evolution
    },
    "whisperwoodWilds": {
        "day": ["Mossling", "Mossling", "Serpentine"],
        "night": ["Mossling", "Serpentine", "Serpentine", "Grimweave", "Serpumbra"]  # Serpumbra ~20% — low-chance evolution
    },
    "ashenVerge": {
        # The Ash Circle — Tindertail intentionally absent (Bram & Pip's shared
        # companion, not a wild population). The First Ring is folded into this
        # table as rare/very-rare sightings rather than its own zone for now.
        "day": ["Mossling", "Mossling", "Cinderkit", "Cinderkit", "Pyrethorn"],  # Pyrethorn ~20% — First Ring, rare daytime sighting
        "night": ["Mossling", "Mossling", "Cinderkit", "Cinderkit", "Cinderkit", "Grimweave", "Smolderoot", "Smolderoot", "Cindermaw", "Pyrehart"]  # Cindermaw/Pyrehart ~10% each — ancient, very rare
    },
    "mirefields": {
        "day": ["Murkback", "Pallefin", "Mossling", "Corroder"],
        "night": ["Murkback", "Grimweave", "Siltborn", "Corroder"],
    },
    "weeping_chasm": {
        "day": ["Gauntling", "Rimecrawl", "Corroder"],
        "night": ["Gauntling", "Rimecrawl", "Grimweave", "Corroder", "Waneling", "Frostbile", "Grimplate", "Threshling"],
    },
    "weepingRoot": {
        # Underground, no real day/night cycle — both keys use the same table.
        # Mossling/Serpentine/Glamorose here are Withering-Marked (flavor-only
        # for now; see EXPLORE_EVENTS["weepingRoot"] and on_enter text).
        "day": ["Mossling", "Mossling", "Mossling", "Serpentine", "Glamorose", "Veinglow", "Veinglow", "Stillroot"],  # Stillroot ~12.5% — rare, Calcifying alongside Withering
        "night": ["Mossling", "Mossling", "Mossling", "Serpentine", "Glamorose", "Veinglow", "Veinglow", "Stillroot"],
    },
}
