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
        "base_capture_rate": 45,
        "base_stat_ranges": {"hp": [45, 50], "attack": [25, 30], "defense": [40, 45], "special_attack": [20, 25],
                             "special_defense": [30, 35], "speed": [20, 25]},
        "growth_rates": {"hp": 1.9, "attack": 1.2, "defense": 1.8, "special_attack": 1.0, "special_defense": 1.3,
                         "speed": 1.1},
        "skill_tree": {
            "1": ["pound", "harden"]
        },
        "evolutions": {
            "Barkback": {
                "evolves_at": 16
                # Full data for Barkback to be added later
            }
        }
    },
    "Corroder": {
        "species": "Corroder", "pet_type": ["Rock", "Poison"], "rarity": "Common", "personality": "Defensive",
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
        "personality": "Timid", # Example of a future personality
        "base_capture_rate": 45,
        # ... Mossling's data would go here, with its evolutions nested inside
    }
}

# =================================================================================
#  ENCOUNTER TABLES
# =================================================================================
# This dictionary defines WHICH pets can be found WHERE and WHEN.
# It simply refers to the pet's name from the PET_DATABASE above.
# This solves the data duplication problem.

ENCOUNTER_TABLES = {

    "oakhavenWilds": {
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
