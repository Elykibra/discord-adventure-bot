# data/skills.py
# This file contains all detailed data for pet skills in the game.

PET_SKILLS = {

    # Basic Skills
    "scratch": {
        "name": "Scratch",
        "power": 40,
        "type": "Normal",
        "category": "Physical",
        "verb_type": "slash",
        "description": "A basic scratch attack that has a small chance to lower the target's Defense.",
        "effect": {
            "type": "stat_change",
            "stat": "defense",
            "modifier": 0.9,
            "duration": 2,
            "chance": 0.1,
            "target": "opponent"
        }
    },
    "pound": {
        "name": "Pound",
        "power": 40,
        "type": "Normal",
        "category": "Physical",
        "verb_type": "impact",
        "description": "A physical attack that has a small chance to make the target flinch.",
        "effect": {
            "type": "status",
            "status_effect": "flinch",
            "duration": 1,
            "chance": 0.1,
            "target": "opponent"
        }
    },
    "headbutt": {
        "name": "Headbutt",
        "power": 45,
        "type": "Normal",
        "category": "Physical",
        "verb_type": "impact",
        "description": "A head-first collision that has a chance to leave the target Confused.",
        "effect": {
            "type": "status",
            "status_effect": "confused",
            "duration": 3,
            "chance": 0.2,
            "target": "opponent"
        }
    },
    "water_gun": {
        "name": "Water Gun",
        "power": 40,
        "type": "Water",
        "category": "Special",
        "verb_type": "blast",
        "description": "A jet of water with a small chance to lower the opponent's Speed.",
        "effect": {
            "type": "stat_change",
            "stat": "speed",
            "modifier": 0.9,
            "duration": 2,
            "chance": 0.1,
            "target": "opponent"
        }
    },
    "rock_throw": {
        "name": "Rock Throw",
        "power": 50,
        "type": "Ground",
        "category": "Special",
        "verb_type": "projectile",
        "description": "Hurls a sharp rock. Has a small chance to lower the target's Speed.",
        "effect": {
            "type": "stat_change",
            "stat": "speed",
            "modifier": 0.9,
            "duration": 2,
            "chance": 0.1,
            "target": "opponent"
        }
    },
    "leaf_slap": {
        "name": "Leaf Slap",
        "power": 45,
        "type": "Grass",
        "category": "Physical",
        "verb_type": "strike",
        "description": "A quick slap with a leaf that has a small chance to heal the user for a portion of damage dealt.",
        "effect": {
            "type": "heal_on_damage",
            "percent": 0.15,  # heals 15% of damage dealt
            "chance": 0.2,  # optional: if you want healing to be chance-based
            "target": "self"
        }
    },

    "rock_slide": {
        "name": "Rock Slide",
        "power": 75,
        "type": "Rock",
        "category": "Physical",
        "verb_type": "impact",
        "description": "Slams rocks onto the opponent. Has a chance to flinch the opponent.",
        "effect": {
            "type": "status",
            "status_effect": "flinch",
            "duration": 1,
            "chance": 0.3,
            "target": "opponent"
        }
    },

    "dazzling_gleam": {
        "name": "Dazzling Gleam",
        "power": 55,
        "type": "Fairy",
        "category": "Special",
        "verb_type": "blast",
        "description": "Unleashes a blinding light that has a chance to lower the opponent's accuracy.",
        "effect": {
            "type": "stat_change",
            "stat": "accuracy",
            "modifier": 0.8,  # -20% accuracy
            "duration": 2,
            "chance": 0.2,
            "target": "opponent"
        }
    },

    # --- NEW EFFECT STRUCTURE ---
    "poison_sting": {
        "name": "Poison Sting",
        "power": 15,
        "type": "Poison",
        "category": "Physical",
        "verb_type": "pierce",
        "description": "A weak sting that has a guaranteed chance to poison the opponent.",
        "effect": {
            "type": "status",
            "status_effect": "poison",
            "damage_per_turn": 5,
            "duration": 3,
            "chance": 1.0,
            "target": "opponent"
        }
    },

    "moss_shield": {
        "name": "Moss Shield",
        "power": 0,
        "type": "Grass",
        "category": "Status",
        "verb_type": "Self",
        "description": "Raises the user's Defense sharply by covering them with moss.",
        "effect": {
            "type": "stat_change",
            "stat": "defense",
            "modifier": 1.5,  # +50% Defense
            "duration": 3,
            "chance": 1.0,
            "target": "self"
        }
    },

    "ember": {
        "name": "Ember",
        "power": 40,
        "type": "Fire",
        "category": "Special",
        "verb_type": "projectile",
        "description": "A small burst of fire that has a chance to burn the target.",
        "effect": {
            "type": "status",
            "status_effect": "burn",
            "damage_per_turn": 4,
            "duration": 3,
            "chance": 0.1,
            "target": "opponent",
            "stat_change": {
                "stat": "attack",
                "modifier": 0.75  # Burn also lowers Attack
            }
        }
    },

    "bug_buzz": {
        "name": "Bug Buzz",
        "power": 60,
        "type": "Bug",
        "category": "Special",
        "verb_type": "wave",
        "description": "Generates a loud buzzing sound that has a chance to lower the target's Special Defense.",
        "effect": {
            "type": "stat_change",
            "stat": "special_defense",
            "modifier": 0.8,  # -20% Sp. Def
            "duration": 3,
            "chance": 0.2,
            "target": "opponent"
        }
    },

    "leech_life": {
        "name": "Leech Life",
        "power": 30,
        "type": "Bug",
        "category": "Physical",
        "verb_type": "bite",
        "description": "A draining attack that heals the user for half the damage dealt.",
        "effect": {
            "type": "heal_on_damage",
            "percent": 0.5,
            "chance": 1.0,
            "target": "self"
        }
    },

    #complex skills
    "pyralis_renewal": {
        "name": "Pyralis's Renewal",
        "power": 70,
        "type": "Fire",
        "category": "Special",
        "verb_type": "blast",
        "description": "Deals Fire damage and grants 'Rebirth' status, healing the user after two turns.",
        "effect": {
            "type": "status",
            "status_effect": "rebirth",
            "duration": 2,
            "chance": 1.0,
            "target": "self",
            "on_turn_end": {
                "type": "delayed_heal",
                "percent": 0.25,
                "trigger_on_turn": 2
            },
            "unique_flag": "revive_once"
        }
    },

    "borealis_stasis": {
        "name": "Borealis's Stasis",
        "power": 30,
        "type": "Ice",
        "category": "Special",
        "verb_type": "blast",
        "description": "Deals low Ice damage with a high chance to freeze the target.",
        "effect": {
            "type": "status",
            "status_effect": "frozen",
            "duration": 1,
            "chance": 0.8,
            "target": "opponent",
            "special_condition": {
                "if_target_has_status": "gloom_touched",
                "then_duration": 2
            }
        }
    },

    "sylven_heartwoods_ward": {
        "name": "Sylven Heartwood's Ward",
        "power": 0,
        "type": "Grass",
        "category": "Status",
        "verb_type": "Self",
        "description": "Greatly boosts Defense for one turn. If hit during that turn, cleanses a status condition.",
        "effect": [
            {
                "type": "stat_change",
                "stat": "defense",
                "modifier": 2.0,
                "duration": 1,
                "chance": 1.0,
                "target": "self"
            },
            {
                "type": "status",
                "status_effect": "warded",
                "duration": 1,
                "chance": 1.0,
                "target": "self",
                "on_being_hit": {
                    "type": "cleanse_status",
                    "count": 1
                }
            }
        ]
    },

    "wyrms_contempt": {
        "name": "Wyrm's Contempt",
        "power": 90,
        "type": "Dragon",
        "category": "Special",
        "verb_type": "blast",
        "description": "Deals Dragon damage and inflicts 'Corrupting Blight', which damages the target each turn and reduces healing.",
        "effect": {
            "type": "status",
            "status_effect": "corrupting_blight",
            "status_kind": "dot",  # damage-over-time
            "duration": 3,
            "chance": 1.0,
            "target": "opponent",
            "damage_per_turn": 10,
            "on_heal_received": {  # this will need an effect handler in effects.py
                "modifier": 0.5
            }
        }
    },

    "siphon_sorrow": {
        "name": "Siphon Sorrow",
        "power": 20,
        "type": "Ghost",
        "category": "Special",
        "verb_type": "drain",  # NEW verb_type
        "description": "Deals more damage the higher the target's HP. Steals one of the target's stat buffs.",
        "power_modifier": {
            "type": "scale_with_target_hp_percent",
            "max_power": 110
        },
        "effect": {
            "type": "steal_buff",
            "chance": 1.0,
            "target": "opponent"
        }
    },

    #more complicated skills
    "nexus_conversion": {
        "name": "Nexus Conversion",
        "power": 0,
        "type": "Fighting",
        "category": "Status",
        "verb_type": "stance",
        "description": "A defensive stance. If hit by an elemental attack, damage is reduced and the user's next attack is powered up.",
        "effect": {
            "type": "status",
            "status_effect": "nexus_stance",
            "duration": 1,
            "target": "self",
            "on_being_hit": {
                "if_attack_type": ["Fire", "Water", "Grass", "Electric", "Ice"],
                "then_effect": [
                    {
                        "type": "damage_modifier",
                        "modifier": 0.5  # Reduces incoming damage by 50%
                    },
                    {
                        "type": "status",
                        "status_effect": "power_boost",
                        "duration": 2,
                        "next_attack_modifier": 1.75
                    }
                ]
            }
        }
    },

    "temporal_echo": {
        "name": "Temporal Echo",
        "power": 60,
        "type": "Psychic",
        "category": "Special",
        "verb_type": "beam",
        "description": "Deals Psychic damage and creates a temporal echo that repeats a portion of the next damage the target receives.",
        "effect": {
            "type": "status",
            "status_effect": "echo",
            "duration": 2,
            "target": "opponent",
            "on_next_damage_received": {
                "type": "delayed_damage",
                "percent": 0.30,
                "delay_turns": 1
            }
        }
    },

    "crest_resonance": {
        "name": "Crest Resonance",
        "power": 10,
        "type": "Normal",
        "category": "Special",
        "verb_type": "blast",
        "description": "Deals damage that grows stronger with each Guild Crest you've obtained.",
        "power_modifier": {
            "type": "scale_with_player_crests",
            "power_per_crest": 12
        }
    },

    "blightborne_fury": {
        "name": "Blightborne Fury",
        "power": 0,
        "type": "Fighting",
        "category": "Status",
        "verb_type": "stance",
        "description": "For 3 turns, the user gains Attack but loses Defense. Attacks may also inflict 'Blighted'.",
        "effect": [
            {
                "type": "stat_change",
                "stat": "attack",
                "modifier": 2.0,
                "duration": 3,
                "target": "self"
            },
            {
                "type": "stat_change",
                "stat": "defense",
                "modifier": 0.5,
                "duration": 3,
                "target": "self"
            },
            {
                "type": "status",
                "status_effect": "Rampaging",
                "duration": 3,
                "target": "self",
                "on_attack_hit": {
                    "type": "status",
                    "status_effect": "Blighted",
                    "duration": 2,
                    "chance": 0.3,
                    "target": "opponent"
                }
            }
        ]
    },

    "shattering_blow": {
        "name": "Shattering Blow",
        "power": 140,
        "type": "Rock",
        "category": "Physical",
        "verb_type": "impact",
        "description": "A devastating attack that ignores Defense boosts, but leaves the user recharging.",
        "special_flag": "ignores_defense_buffs",
        "effect": {
            "type": "status",
            "status_effect": "recharging",
            "duration": 1,
            "target": "self"
        }
    },
    "spiteful_bastion": {
        "name": "Spiteful Bastion",
        "power": 0,
        "type": "Steel",
        "category": "Status",
        "verb_type": "stance",
        "description": "A defensive stance. If hit, the attacker's Attack and Speed are lowered.",
        "effect": {
            "type": "status",
            "status_effect": "spiteful_stance",
            "duration": 1,
            "target": "self",
            "on_being_hit": {
                "if_attack_damaging": True,
                "then_effect": [
                    {
                        "type": "stat_change",
                        "stat": "attack",
                        "modifier": 0.75,
                        "duration": 3,
                        "target": "opponent"
                    },
                    {
                        "type": "stat_change",
                        "stat": "speed",
                        "modifier": 0.75,
                        "duration": 3,
                        "target": "opponent"
                    }
                ]
            }
        }
    },

    "balancing_ward": {
        "name": "Balancing Ward",
        "power": 0,
        "type": "Normal",
        "category": "Status",
        "verb_type": "stance",
        "description": "For one turn, any single attack that would deal more than 50% of max HP is capped at 50%.",
        "effect": {
            "type": "status",
            "status_effect": "balancing_ward",
            "duration": 1,
            "target": "self",
            "on_damage_calculation": {
                "damage_cap": {
                    "percent_of_max_hp": 0.5
                }
            }
        }
    },

    "phantom_step": {
        "name": "Phantom Step",
        "power": 40,
        "type": "Flying",
        "category": "Physical",
        "verb_type": "rush",
        "description": "A priority strike that raises the user's Evasion for the turn.",
        "special_flag": "priority_move",
        "effect": {
            "type": "stat_change",
            "stat": "evasion",
            "modifier": 1.5,
            "duration": 1,
            "target": "self"
        }
    },

    "accelerated_decay": {
        "name": "Accelerated Decay",
        "power": 0,
        "type": "Bug",
        "category": "Status",
        "verb_type": "curse",
        "description": "Inflicts a decay that deals small damage after one turn, then heavy damage after the second.",
        "effect": {
            "type": "status",
            "status_effect": "accelerated_decay",
            "duration": 2,
            "target": "opponent",
            "on_turn_end": {
                "type": "damage_sequence",
                "damage": [20, 80]
            }
        }
    },

    "equilibrium_shift": {
        "name": "Equilibrium Shift",
        "power": 0,
        "type": "Psychic",
        "category": "Status",
        "verb_type": "wave",
        "description": "Inverts all of the target's stat changes, turning buffs into debuffs and vice-versa.",
        "effect": {
            "type": "stat_inversion",
            "target": "opponent",
            "fails_if_no_stat_changes": True
        }
    },
    "prophetic_glimpse": {
    "name": "Prophetic Glimpse",
    "power": 0,
    "type": "Psychic",
    "category": "Status",
    "verb_type": "gaze",
    "description": "The user's next attack will be super-effective, regardless of type. High chance to fail if used consecutively.",
    "special_flag": "high_fail_rate_on_consecutive_use",
    "effect": {
        "type": "status",
        "status_effect": "prophetic_glimpse",
        "duration": 2,
        "target": "self",
        "next_attack_modifier": {
            "force_super_effective": True
        }
    }
},

"immolate": {
    "name": "Immolate",
    "power": 65,
    "type": "Fire",
    "category": "Special",
    "verb_type": "blast",
    "description": "Deals Fire damage and burns away one of the target's beneficial effects.",
    "effect": {
        "type": "remove_buff",
        "count": 1,
        "target": "opponent"
    }
},

"tidal_lock": {
    "name": "Tidal Lock",
    "power": 35,
    "type": "Water",
    "category": "Special",
    "verb_type": "wave",
    "description": "Deals Water damage, lowers the target's Speed, and prevents them from fleeing or switching out.",
    "effect": [
        {
            "type": "stat_change",
            "stat": "speed",
            "modifier": 0.75,
            "duration": 3,
            "target": "opponent"
        },
        {
            "type": "status",
            "status_effect": "tidal_locked",
            "duration": 3,
            "target": "opponent"
        }
    ]
},

"grasping_briar": {
    "name": "Grasping Briar",
    "power": 0,
    "type": "Grass",
    "category": "Status",
    "verb_type": "bind",
    "description": "Entangles the target, damaging them and healing the user each turn.",
    "effect": {
        "type": "status",
        "status_effect": "entangled",
        "duration": 3,
        "target": "opponent",
        "on_turn_end": {
            "type": "damage_and_leech_hp",
            "damage_per_turn": 12
        }
    }
},

"short_circuit": {
    "name": "Short Circuit",
    "power": 65,
    "type": "Electric",
    "category": "Special",
    "verb_type": "shock",
    "description": "Deals Electric damage and may scramble the opponent, preventing them from reusing the same move consecutively.",
    "effect": {
        "type": "status",
        "status_effect": "scrambled",
        "duration": 3,
        "chance": 0.3,
        "target": "opponent",
        "on_action_attempt": {
            "prevent_repeat_move": True
        }
    }
},
    "unyielding_focus": {
        "name": "Unyielding Focus",
        "power": 0,
        "type": "Fighting",
        "category": "Status",
        "verb_type": "stance",
        "description": "The user resists flinching and confusion for the next 2 turns.",
        "effect": {
            "type": "status",
            "status_effect": "unyielding_focus",
            "duration": 2,
            "target": "self",
            "immunities": ["flinch", "confusion"]
        }
    },

    "umbral_shift": {
        "name": "Umbral Shift",
        "power": 0,
        "type": "Ghost",
        "category": "Status",
        "verb_type": "phase",
        "description": "The user vanishes into shadows, evading all attacks for a turn.",
        "effect": {
            "type": "status",
            "status_effect": "umbral_shift",
            "duration": 1,
            "target": "self",
            "on_action_attempt": {
                "auto_evade": True
            }
        }
    },

    "draconic_ascendance": {
        "name": "Draconic Ascendance",
        "power": 0,
        "type": "Dragon",
        "category": "Status",
        "verb_type": "ascend",
        "description": "The user taps into its draconic might, sharply raising Attack and Speed.",
        "effect": [
            {
                "type": "stat_change",
                "stat": "attack",
                "modifier": 1.5,
                "duration": 3,
                "target": "self"
            },
            {
                "type": "stat_change",
                "stat": "speed",
                "modifier": 1.5,
                "duration": 3,
                "target": "self"
            }
        ]
    },

    "caustic_venom": {
        "name": "Caustic Venom",
        "power": 55,
        "type": "Poison",
        "category": "Special",
        "verb_type": "corrode",
        "description": "A toxic strike that badly poisons the target, dealing increasing damage over time.",
        "effect": {
            "type": "status",
            "status_effect": "toxic_poison",
            "duration": 3,
            "target": "opponent",
            "on_turn_end": {
                "type": "toxic_dot",
                "base_damage": 5,
                "damage_ramp": 5
            }
        }
    },

    "karma_weave": {
        "name": "Karma Weave",
        "power": 0,
        "type": "Fairy",
        "category": "Status",
        "verb_type": "weave",
        "description": "For the next turn, damage dealt to the user is also reflected back to the attacker.",
        "effect": {
            "type": "status",
            "status_effect": "karma_weave",
            "duration": 1,
            "target": "self",
            "on_next_damage_received": {
                "reflect_percent": 1.0
            }
        }
    },

    # New Skills
    "null_field": {
        "name": "Null Field",
        "power": 0,
        "type": "Psychic",
        "category": "Status",
        "verb_type": "nullify",
        "description": "Generates a field that negates all ongoing effects for 2 turns.",
        "effect": {
            "type": "status",
            "status_effect": "null_field",
            "status_kind": "field",  # battlefield-wide effect
            "duration": 2,
            "target": "field",
            "rules": {
                "suppress_status": True,
                "suppress_stat_changes": True
            }
        }
    },
    "sacrificial_pact": {
        "name": "Sacrificial Pact",
        "power": 0,
        "type": "Dark",
        "category": "Status",
        "verb_type": "sacrifice",
        "description": "The user sacrifices half its HP to fully heal an ally.",
        "effect": [
            {
                "type": "status",
                "status_effect": "hp_drain",
                "status_kind": "self_cost",
                "target": "self",
                "amount_percent": 0.5
            },
            {
                "type": "status",
                "status_effect": "heal",
                "status_kind": "healing",
                "target": "ally",
                "amount_percent": 1.0
            }
        ]
    },

    "divine_benediction": {
        "name": "Divine Benediction",
        "power": 0,
        "type": "Light",  # Assuming "Light" is a defined type
        "category": "Status",
        "verb_type": "bless",
        "description": "The user calls down divine grace, healing allies and curing their ailments.",
        "effect": [
            {
                "type": "team_heal",  # New, specific type
                "target": "ally_team",
                "amount_percent": 0.5
            },
            {
                "type": "team_cleanse",  # New, specific type
                "target": "ally_team",
                "count": -1  # -1 for all
            }
        ]
    },

    "cataclysmic_storm": {
        "name": "Cataclysmic Storm",
        "power": 120,
        "type": "Electric",
        "category": "Special",
        "verb_type": "tempest",
        "description": "A devastating storm that damages all opponents with overwhelming force.",
        "effect": {
            "type": "damage",
            "status_effect": "aoe_damage",
            "status_kind": "aoe",
            "target": "opponent_team"
        }
    },

    "soulrend": {
        "name": "Soulrend",
        "power": 100,
        "type": "Ghost",
        "category": "Special",
        "verb_type": "rend",
        "description": "Rips at the opponent's soul, ignoring defenses and leaving them weakened.",
        "effect": [
            {
                "type": "damage",
                "ignore_defense": True
            },
            {
                "type": "status",
                "status_effect": "weakened",
                "status_kind": "control",  # short-term control/debuff
                "duration": 2,
                "target": "opponent"
            },
            {
                "type": "stat_change",
                "stat": "attack",
                "modifier": 0.75,
                "duration": 2,
                "target": "opponent"
            }
        ]
    },
    "exoskeletal_molt": {
        "name": "Exoskeletal Molt",
        "power": 0,
        "type": "Bug",
        "category": "Status",
        "verb_type": "ascend",
        "description": "Removes all stat debuffs from the user, sharply raises Speed, but lowers Defense for 2 turns.",
        "effect": [
            {
                "type": "cleanse_debuffs",
                "target": "self"
            },
            {
                "type": "stat_change",
                "stat": "speed",
                "modifier": 2.0,
                "duration": 4,
                "target": "self"
            },
            {
                "type": "stat_change",
                "stat": "defense",
                "modifier": 0.75,
                "duration": 2,
                "target": "self"
            }
        ]
    },

    "geode_charge": {
        "name": "Geode Charge",
        "power": 20,
        "type": "Rock",
        "category": "Physical",
        "verb_type": "impact",
        "description": "Deals low Rock damage. Its power increases for the rest of the battle each time the user is damaged.",
        "effect": {
            "type": "status",
            "status_effect": "geode_charge_active",
            "status_kind": "buff",
            "duration": -1,
            "target": "self",
            "on_being_hit": {
                "if_attack_damaging": True,
                "then_effect": {
                    "type": "status",
                    "status_effect": "increase_move_power",
                    "move_id": "geode_charge",
                    "amount": 20,
                    "status_kind": "buff"
                }
            }
        }
    },

    "last_stand": {
        "name": "Last Stand",
        "power": 1,
        "type": "Normal",
        "category": "Physical",
        "verb_type": "rush",
        "description": "A desperate final attack that can only be used at low health. Its power is immense when the user is near fainting.",
        "usage_condition": {
            "max_hp_percent": 0.25
        },
        "power_modifier": {
            "type": "scale_with_missing_hp",
            "max_power": 200
        }
    },

    "earthbind": {
        "name": "Earthbind",
        "power": 60,
        "type": "Ground",
        "category": "Physical",
        "verb_type": "bind",
        "description": "Deals Ground damage and binds the target to the earth, removing Flying-type immunities for 3 turns.",
        "effect": {
            "type": "status",
            "status_effect": "earthbound",
            "status_kind": "control",
            "duration": 3,
            "target": "opponent",
            "special_flag": "removes_ground_immunity"
        }
    },
    "adaptive_spirit": {
        "name": "Adaptive Spirit",
        "power": 0,
        "type": "Normal",
        "category": "Status",
        "verb_type": "weave",
        "description": "The user attunes its essence, changing its type to match the last attack it was hit by.",
        "effect": {
            "type": "status",
            "status_effect": "adaptive_spirit",
            "status_kind": "passive",
            "duration": -1,
            "target": "self",
            "on_being_hit": {
                "if_attack_damaging": True,
                "then_effect": {
                    "type": "status",
                    "status_effect": "change_user_type_to_last_hit",
                    "status_kind": "transform"
                }
            }
        }
    },
    "cinder_trap": {
        "name": "Cinder Trap",
        "power": 0,
        "type": "Fire",
        "category": "Status",
        "verb_type": "bind",
        "description": "Lays a trap of embers. If the opponent makes physical contact, they are burned.",
        "effect": {
            "type": "status",
            "status_effect": "cinder_trap",
            "status_kind": "trap",
            "duration": 3,
            "target": "opponent_field",
            "on_opponent_action": {
                "if_move_is_physical_contact": True,
                "then_effect": {
                    "type": "status",
                    "status_effect": "burn",
                    "status_kind": "dot",
                    "damage_per_turn": 4,
                    "stat": "attack",
                    "modifier": 0.75,
                    "duration": 3
                },
                "self_remove": True
            }
        }
    },
    "soothing_veil": {
        "name": "Soothing Veil",
        "power": 0,
        "type": "Water",
        "category": "Status",
        "verb_type": "bless",
        "description": "Surrounds the user with a healing veil of water. At the end of the next turn, the user is healed.",
        "effect": {
            "type": "status",
            "status_effect": "soothing_veil",
            "status_kind": "heal",
            "duration": 2,
            "target": "self",
            "on_turn_end": {
                "type": "heal",
                "amount_percent": 0.33
            }
        }
    },
    "barbed_spores": {
        "name": "Barbed Spores",
        "power": 10,
        "type": "Grass",
        "category": "Special",
        "verb_type": "corrode",
        "description": "Deals minor damage and covers the target in irritating spores. For 3 turns, the target's status moves have a 50% chance to fail.",
        "effect": {
            "type": "status",
            "status_effect": "barbed_spores",
            "status_kind": "debuff",
            "duration": 3,
            "target": "opponent",
            "on_action_attempt": {
                "if_move_category": "Status",
                "chance_to_fail": 0.5
            }
        }
    },
    "magnetic_flux": {
        "name": "Magnetic Flux",
        "power": 0,
        "type": "Electric",
        "category": "Status",
        "verb_type": "shock",
        "description": "Lowers the target's Speed. The effect is doubled against Steel-type pets.",
        "effect": {
            "type": "stat_change",  # Corrected type
            "status_effect": "magnetic_flux",
            "status_kind": "debuff",
            "stat": "speed",
            "modifier": 0.75,
            "duration": 3,
            "target": "opponent",
            "special_condition": {
                "if_target_has_type": "Steel",
                "then_modifier": 0.50
            }
        }
    },
    "permafrost": {
        "name": "Permafrost",
        "power": 0,
        "type": "Ice",
        "category": "Status",
        "verb_type": "bind",
        "description": "Sharply lowers the target's Speed by freezing the ground. Fails if the ground is already frozen.",
        "effect": {
            "type": "stat_change",  # Corrected type
            "status_effect": "permafrost_debuff",
            "status_kind": "debuff",
            "stat": "speed",
            "modifier": 0.50,
            "duration": 4,
            "target": "opponent",
            "fails_if_target_has_status": "permafrost_debuff"
        }
    },
    "aura_break": {
        "name": "Aura Break",
        "power": 75,
        "type": "Fighting",
        "category": "Special",
        "verb_type": "impact",
        "description": "A focused strike that shatters magical defenses, calculating damage using the target's physical Defense.",
        "special_flag": "calculates_on_physical_defense"
    },
    "venomous_haze": {
        "name": "Venomous Haze",
        "power": 0,
        "type": "Poison",
        "category": "Status",
        "verb_type": "corrode",
        "description": "For 3 turns, any opponent making physical contact has a high chance of being poisoned.",
        "effect": {
            "type": "status",
            "status_effect": "venomous_haze",
            "status_kind": "trap",
            "duration": 3,
            "target": "self",
            "on_being_hit": {
                "if_attack_is_physical_contact": True,
                "then_effect": {
                    "type": "status",
                    "status_effect": "poison",
                    "status_kind": "dot",
                    "damage_per_turn": 5,
                    "duration": 3,
                    "chance": 0.9
                }
            }
        }
    },
    "earthen_bulwark": {
        "name": "Earthen Bulwark",
        "power": 0,
        "type": "Ground",
        "category": "Status",
        "verb_type": "stance",
        "description": "Increases the user's Defense by two stages, but lowers their Speed by one stage.",
        "effect": [
            {
                "type": "stat_change",  # Corrected type
                "status_effect": "defense_boost",
                "status_kind": "buff",
                "stat": "defense",
                "modifier": 2.0,
                "duration": 4,
                "target": "self"
            },
            {
                "type": "stat_change",  # Corrected type
                "status_effect": "speed_drop",
                "status_kind": "debuff",
                "stat": "speed",
                "modifier": 0.75,
                "duration": 4,
                "target": "self"
            }
        ]
    },
    "precognition": {
        "name": "Precognition",
        "power": 0,
        "type": "Psychic",
        "category": "Status",
        "verb_type": "weave",
        "description": "The user perfectly predicts the opponent's next move, guaranteeing an evasion. High chance to fail if used consecutively.",
        "special_flag": "high_fail_rate_on_consecutive_use",
        "effect": {
            "type": "status",
            "status_effect": "precognition",
            "status_kind": "buff",
            "duration": 1,
            "target": "self",
            "on_evade": {
                "guaranteed_dodge": True
            }
        }
    },
    "infestation": {
        "name": "Infestation",
        "power": 0,
        "type": "Bug",
        "category": "Status",
        "verb_type": "bind",
        "description": "For 4 turns, the target's Attack and Special Attack are slightly lowered at the end of each of their turns.",
        "effect": {
            "type": "status",
            "status_effect": "infestation",
            "status_kind": "debuff",
            "duration": 4,
            "target": "opponent",
            "on_turn_end": [
                {
                    "type": "stat_change",
                    "stat": "attack",
                    "modifier": 0.95,
                    "duration": 1,
                    "target": "opponent"
                },
                {
                    "type": "stat_change",
                    "stat": "special_attack",
                    "modifier": 0.95,
                    "duration": 1,
                    "target": "opponent"
                }
            ]
        }
    },
    "grudge": {
        "name": "Grudge",
        "power": 0,
        "type": "Ghost",
        "category": "Status",
        "verb_type": "curse",
        "description": "If the user is knocked out by a damaging move, the move that defeated it is disabled for the rest of the battle.",
        "effect": {
            "type": "status",
            "status_effect": "grudge",
            "status_kind": "trap",
            "duration": -1,  # Until faint/switch
            "target": "self",
            "on_faint": {
                "from_damaging_move": True,
                "then_effect": {
                    "type": "disable_attacker_move"
                }
            }
        }
    },
    "overwhelm": {
        "name": "Overwhelm",
        "power": 80,
        "type": "Dragon",
        "category": "Physical",
        "verb_type": "impact",
        "description": "Deals Dragon damage. If the user's Attack is higher than the target's, the target may flinch.",
        "effect": {
            "type": "status",
            "status_effect": "flinch",
            "status_kind": "control",
            "duration": 1,
            "chance": 0.3,
            "target": "opponent",
            "special_condition": {
                "if_user_stat_is_higher": {
                    "user_stat": "attack",
                    "target_stat": "attack"
                }
            }
        }
    },
    "spirit_blessing": {
        "name": "Spirit Blessing",
        "power": 0,
        "type": "Fairy",
        "category": "Status",
        "verb_type": "bless",
        "description": "Once per battle, the user sacrifices half its current health to fully heal the next pet switched in.",
        "special_flag": "once_per_battle",
        "effect": {
            "type": "status",
            "status_effect": "spirit_blessing",
            "status_kind": "support",
            "duration": -1,
            "target": "self",
            "on_apply": {
                "self_damage": {
                    "percent_of_current_hp": 0.5
                }
            },
            "on_switch_out": {
                "heal_next_pet_percent": 1.0
            }
        }
    },

            #Corroder Added skills
    "rotten_grasp": {
        "name": "Rotten Grasp",
        "power": 30,
        "type": "Poison",
        "category": "Physical",
        "verb_type": "bind",
        "description": "A physical attack that deals minor damage but has a high chance to lower the target's Speed.",
        "effect": {
            "type": "status",
            "status_effect": "speed_drop",
            "status_kind": "debuff",
            "stat": "speed",
            "modifier": 0.75,
            "duration": 3,
            "chance": 0.8,
            "target": "opponent"
        }
    },
    "corrosive_gaze": {
        "name": "Corrosive Gaze",
        "power": 50,
        "type": "Poison",
        "category": "Special",
        "verb_type": "gaze",
        "description": "A special attack that deals damage and has a small chance to corrode the opponent's armor, making them take more physical damage.",
        "effect": {
            "type": "status",
            "status_effect": "defense_shred",
            "status_kind": "debuff",
            "stat": "defense",
            "modifier": 0.8,
            "duration": 3,
            "chance": 0.3,
            "target": "opponent"
        }
    },
    "acid_armor": {
        "name": "Acid Armor",
        "power": 0,
        "type": "Poison",
        "category": "Status",
        "verb_type": "corrode",
        "description": "The user's body liquefies, sharply raising its Defense.",
        "effect": {
            "type": "status",
            "status_effect": "acid_armor",
            "status_kind": "buff",
            "stat": "defense",
            "modifier": 2.0,
            "duration": 3,
            "target": "self"
        }
    },
    "sludge_bomb": {
        "name": "Sludge Bomb",
        "power": 80,
        "type": "Poison",
        "category": "Special",
        "verb_type": "blast",
        "description": "Hurls a blob of toxic sludge at the opponent with a chance to poison.",
        "effect": {
            "type": "status",
            "status_effect": "poison",
            "status_kind": "dot",
            "damage_per_turn": 5,
            "duration": 3,
            "chance": 0.4,
            "target": "opponent"
        }
    },
    "venomous_erosion": {
        "name": "Venomous Erosion",
        "power": 30,
        "type": "Poison",
        "category": "Special",
        "verb_type": "corrode",
        "description": "A special attack that inflicts a poison which grows in power each turn.",
        "effect": {
            "type": "status",
            "status_effect": "venomous_erosion",
            "status_kind": "dot",
            "duration": 3,
            "target": "opponent",
            "on_turn_end": {
                "type": "damage_sequence",
                "damage": [10, 20, 30]
            }
        }
    },
    "miasmal_aura": {
        "name": "Miasmal Aura",
        "power": 0,
        "type": "Poison",
        "category": "Status",
        "verb_type": "corrode",
        "description": "...",
        "effect": {
            "type": "status",
            "status_effect": "miasmal_aura",
            "duration": 3,
            "target": "self",
            "on_being_hit": { # This part needs the engine update to trigger
                "if_attack_category": "Physical",
                "then_effect": {
                    "type": "status",
                    "status_effect": "poison",
                    "status_kind": "dot",
                    "damage_per_turn": 5,
                    "duration": 3,
                    "target": "opponent"
                }
            }
        }
    },

    "bone_shatter": {
        "name": "Bone Shatter",
        "power": 100,
        "type": "Rock",
        "category": "Physical",
        "verb_type": "impact",
        "description": "A powerful attack that uses the golem's bone-like limbs to break down an opponent's defenses.",
        "effect": {
            "type": "stat_change",
            "stat": "defense",
            "modifier": 0.75,
            "duration": 3,
            "chance": 1.0,
            "target": "opponent"
        }
    },
    "sorrowful_strike": {
        "name": "Sorrowful Strike",
        "power": 50,
        "type": "Rock",
        "category": "Physical",
        "verb_type": "strike",
        "description": "An attack that deals more damage the more debuffs the opponent has.",
        "power_modifier": {
            "type": "scale_with_opponent_debuffs",
            "power_per_debuff": 15
        }
    },
    "seismic_slam": {
        "name": "Seismic Slam",
        "power": 80,
        "type": "Ground",
        "category": "Physical",
        "verb_type": "impact",
        "description": "A devastating ground-type attack that lowers the target's speed.",
        "effect": {
            "type": "stat_change",
            "stat": "speed",
            "modifier": 0.75,
            "duration": 3,
            "chance": 1.0,
            "target": "opponent"
        }
    },
"ossuary_aegis": {
    "name": "Ossuary Aegis",
    "power": 0,
    "type": "Rock",
    "category": "Status",
    "verb_type": "stance",
    "description": "...",
    "effect": {
        "type": "status",
        "status_effect": "ossuary_stance",
        "duration": 1,
        "target": "self",
        "on_being_hit": { # This part needs the engine update to trigger
            "if_attack_damaging": True,
            "then_effect": {
                "type": "reflect_debuffs" # This effect type is already supported
            },
            "damage_modifier": 0.0, # This part needs advanced engine logic
            "consume_on_trigger": True # This part needs advanced engine logic
        }
    }
},
    "contagious_blight": {
        "name": "Contagious Blight",
        "power": 0,
        "type": "Poison",
        "category": "Status",
        "verb_type": "curse",
        "description": "Spreads the target's negative status effects to their other available pets.",
        "effect": {
            "type": "spread_debuffs",
            "chance": 1.0,
            "target": "opponent"
        }
    },
        #Pyrelisk Added skills
    "scorch": {
        "name": "Scorch",
        "power": 35,
        "type": "Fire",
        "category": "Special",
        "verb_type": "projectile",  # Added for flavor
        "description": "A minor special fire attack that singes the opponent."
    },
    "fireball": {
        "name": "Fireball",
        "power": 60,
        "type": "Fire",
        "category": "Special",
        "verb_type": "projectile",  # Added for flavor
        "description": "Hurls a ball of fire at the opponent."
    },
    "scale_slash": {
        "name": "Scale Slash",
        "power": 45,
        "type": "Dragon",
        "category": "Physical",
        "verb_type": "slash",  # Added for flavor
        "description": "A physical attack using the pet's scales as a blade."
    },
    "fire_fang": {
        "name": "Fire Fang",
        "power": 65,
        "type": "Fire",
        "category": "Physical",
        "verb_type": "bite",  # Added for flavor
        "description": "A fiery physical attack that has a small chance to burn the opponent.",
        "effect": {
            "type": "status",
            "status_effect": "burn",
            "damage_per_turn": 4,
            "duration": 3,
            "chance": 0.1,
            "target": "opponent"  # Added for clarity
        }
    },
    "dragon_rush": {
        "name": "Dragon Rush",
        "power": 80,
        "type": "Dragon",
        "category": "Physical",
        "verb_type": "rush",  # Added for flavor
        "description": "A fast, high-priority physical dragon attack that has a chance to flinch the opponent.",
        "special_flag": "priority_move",
        "effect": {
            "type": "status",
            "status_effect": "flinch",
            "duration": 1,
            "chance": 0.3,
            "target": "opponent"
        }
    },

        #Dewdrop added skills
    "hydro_pump": {
        "name": "Hydro Pump",
        "power": 110,
        "type": "Water",
        "category": "Special",
        "verb_type": "blast",  # Added for flavor
        "description": "A powerful, high-risk, high-reward special water attack."
    },
    "blessing_of_aethelgard": {
        "name": "Blessing of Aethelgard",
        "power": 0,
        "type": "Fairy",
        "category": "Status",
        "verb_type": "bless",  # Added for flavor
        "description": "A supportive move that cleanses all status effects from a target.",
        "effect": {
            "type": "cleanse_status",
            "target": "ally",
            "count": -1  # -1 signifies cleansing all statuses
        }
    },
    "bubble": {
        "name": "Bubble",
        "power": 30,
        "type": "Water",
        "category": "Special",
        "verb_type": "projectile",  # Added for flavor
        "description": "A minor special water attack that hits with a stream of bubbles."
    },
    "water_pulse": {
        "name": "Water Pulse",
        "power": 60,
        "type": "Water",
        "category": "Special",
        "verb_type": "wave",  # Added for flavor
        "description": "A pulse of water that has a chance to confuse the opponent.",
        "effect": {
            "type": "status",
            "status_effect": "confused",
            "duration": 3,
            "chance": 0.2,
            "target": "opponent"
        }
    },
    "drizzle": {
        "name": "Drizzle",
        "power": 0,
        "type": "Water",
        "category": "Status",
        "verb_type": "Self",  # Added for flavor
        "description": "Summons a gentle drizzle, raising the user's Evasion for 2 turns.",
        "effect": {
            "type": "stat_change",
            "stat": "evasion",
            "modifier": 1.3,
            "duration": 2,
            "chance": 1.0,
            "target": "self"
        }
    },

        #terran added skills
    "stone_gaze": {
        "name": "Stone Gaze",
        "power": 0,
        "type": "Rock",
        "category": "Status",
        "verb_type": "gaze",  # Added for flavor
        "description": "A petrifying gaze that can leave an opponent unable to move for a short time.",
        "effect": {
            "type": "status",
            "status_effect": "petrified",
            "duration": 1,
            "chance": 0.8,
            "target": "opponent"
        }
    },
    "sand_attack": {
        "name": "Sand Attack",
        "power": 0,
        "type": "Ground",
        "category": "Status",
        "verb_type": "projectile",  # Added for flavor
        "description": "Hurls sand at the opponent, lowering their accuracy.",
        "effect": {
            "type": "stat_change",
            "stat": "accuracy",
            "modifier": 0.8,
            "duration": 2,
            "chance": 1.0,
            "target": "opponent"
        }
    },
    "mud_slap": {
        "name": "Mud Slap",
        "power": 20,
        "type": "Ground",
        "category": "Special",
        "verb_type": "strike",  # Added for flavor
        "description": "Slaps the opponent with mud."
    },
    "harden": {
        "name": "Harden",
        "power": 0,
        "type": "Normal",
        "category": "Status",
        "verb_type": "Self",  # Added for flavor
        "description": "Hardens the user's body, raising their Defense.",
        "effect": {
            "type": "stat_change",
            "stat": "defense",
            "modifier": 1.5,
            "duration": 3,
            "chance": 1.0,
            "target": "self"
        }
    },
    "enduring_fortitude": {
        "name": "Enduring Fortitude",
        "power": 0,
        "type": "Rock",
        "category": "Status",
        "verb_type": "stance",  # Added for flavor
        "description": "The user braces for impact, sharply raising its Defense and Special Defense while becoming immune to new debuffs for 2 turns.",
        "effect": [
            {
                # This part is already compatible
                "type": "stat_change",
                "stat": ["defense", "special_defense"],
                "modifier": 1.5,
                "duration": 2,
                "target": "self"
            },
            {
                # This part requires a new immunity system in the engine
                "type": "status",
                "status_effect": "debuff_immunity",
                "duration": 2,
                "target": "self"
            }
        ]
    },
    "mountain_shatter": {
        "name": "Mountain Shatter",
        "power": 120,
        "type": "Ground",
        "category": "Physical",
        "verb_type": "impact",  # Added for flavor
        "description": "A devastating, slow attack that deals immense damage and has a high chance to stun the opponent.",
        "effect": {
            "type": "status",
            "status_effect": "stun",
            "duration": 1,
            "chance": 0.5,
            "target": "opponent"
        },
        "special_flag": "low_priority"  # This flag needs engine support
    },

        #New Skills here

    }
