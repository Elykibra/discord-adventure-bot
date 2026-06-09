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
    "Pineling": {
        "species": "Pineling",
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
            "Barkback": {
                "evolves_at": 16,
                "species": "Barkback",
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
            "Sludge Shell": {
                "evolves_at": 15,
                "species": "Sludge Shell", "pet_type": ["Rock", "Poison"], "rarity": "Uncommon",
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
                    "Ossuary Golem": {
                        "evolves_at": 30,
                        "species": "Ossuary Golem", "pet_type": ["Rock", "Poison"], "rarity": "Rare",
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

    "Sunpetal Moth": {
        "species": "Sunpetal Moth",
        "pet_type": ["Bug", "Flying"],
        "rarity": "Common",
        "personality": "Timid",
        "description": "A delicate moth with wings patterned like blooming sunflowers. It drifts lazily through sun-dappled clearings and is drawn to bright light, making it easy to spot — and easy to startle.",
        "base_capture_rate": 50,
        "passive_ability": {
            "name": "Powder Scales",
            "description": "When this pet is hit by a physical attack, there is a 20% chance the attacker is left Confused by the disorienting scales that shake loose."
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
            "Solarmoth": {
                "evolves_at": 15,
                "species": "Solarmoth",
                "pet_type": ["Bug", "Flying"],
                "rarity": "Uncommon",
                "description": "A larger, more resplendent moth whose wings now radiate a warm golden glow. In bright sunlight its wing patterns shimmer with an almost hypnotic beauty that can leave opponents momentarily dazzled.",
                "passive_ability": {
                    "name": "Solar Scales",
                    "description": "In bright conditions, this pet's Special Attack is slightly increased and its Powder Scales effect triggers more reliably."
                },
                "base_stat_ranges": {"hp": [55, 60], "attack": [35, 40], "defense": [38, 43], "special_attack": [65, 70],
                                     "special_defense": [55, 60], "speed": [60, 65]},
                "growth_rates": {"hp": 2.0, "attack": 1.5, "defense": 1.5, "special_attack": 2.4, "special_defense": 2.0,
                                 "speed": 2.3},
                "skill_tree": {
                    "17": ["bug_buzz"],
                    "21": ["barbed_spores"],
                    "26": {"choice": ["accelerated_decay", "cinder_trap"]},
                    "30": ["dazzling_gleam"]
                }
            }
        }
    },

    "Gloom Weaver": {
        "species": "Gloom Weaver",
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
            "Dreadspinner": {
                "evolves_at": 16,
                "species": "Dreadspinner",
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
                }
            }
        }
    },

    "Moonpetal Sprite": {
        "species": "Moonpetal Sprite",
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
        "day": ["Pineling"],
        "night": ["Pineling"]
    },
    "oakhavenOutpost_rottingPits": {
        "day": ["Corroder"],
        "night": ["Corroder"]  # No need to duplicate the whole pet object
    },
    "whisperwoodGrove": {
        "day": ["Mossling", "Sunpetal Moth"],
        "night": ["Mossling", "Gloom Weaver", "Moonpetal Sprite"]
    }
}
