# data/skills.py
# This file contains all detailed data for pet skills in the game.

PET_SKILLS = {

    # Basic Skills
    "scratch": {
        "name": "Scratch", "power": 40, "type": "Normal", "category": "Physical",
        "description": "A basic scratch attack that has a small chance to lower the target's defense.",
        "effect": {
            "type": "stat_change", "stat": "defense", "modifier": 0.9, "duration": 2, "chance": 0.1, "target": "opponent"
        }
    },
    "pound": {
        "name": "Pound", "power": 40, "type": "Normal", "category": "Physical",
        "description": "A physical attack that has a small chance to make the target flinch.",
        "effect": {
            "type": "apply_status", "status_effect": "flinch", "duration": 1, "chance": 0.1, "target": "opponent"
        }
    },
    "headbutt": {
        "name": "Headbutt", "power": 45, "type": "Normal", "category": "Physical",
        "description": "A head-first collision that has a chance to leave the target confused.",
        "effect": {
            "type": "apply_status", "status_effect": "confused", "duration": 3, "chance": 0.2, "target": "opponent"
        }
    },
    "water_gun": {
        "name": "Water Gun", "power": 40, "type": "Water", "category": "Special",
        "description": "A jet of water with a small chance to lower the opponent's speed.",
        "effect": {
            "type": "stat_change", "stat": "speed", "modifier": 0.9, "duration": 2, "chance": 0.1, "target": "opponent"
        }
    },
    "rock_throw": {
        "name": "Rock Throw", "power": 50, "type": "Ground", "category": "Special",
        "description": "Hurls a sharp rock. Has a small chance to lower the target's speed.",
        "effect": {
            "type": "stat_change", "stat": "speed", "modifier": 0.9, "duration": 2, "chance": 0.1, "target": "opponent"
        }
    },
    "leaf_slap": {
        "name": "Leaf Slap", "power": 45, "type": "Grass", "category": "Physical",
        "description": "A quick slap with a leaf that has a small chance to heal the user for a portion of damage dealt.",
        "effect": {
            "type": "heal_on_damage", "percent": 0.15
        }
    },
    "rock_slide": {
        "name": "Rock Slide", "power": 75, "type": "Rock", "category": "Physical",
        "description": "Slams rocks onto the opponent. Has a chance to flinch the opponent.",
        "effect": {
            "type": "apply_status", "status_effect": "flinch", "duration": 1, "chance": 0.3, "target": "opponent"
        }
    },
    "dazzling_gleam": {
        "name": "Dazzling Gleam", "power": 55, "type": "Fairy", "category": "Special",
        "description": "Unleashes a blinding light that has a chance to lower the opponent's accuracy.",
        "effect": {
            "type": "stat_change", "stat": "accuracy", "modifier": 0.8, "duration": 2, "chance": 0.2, "target": "opponent"
        }
    },

    # --- NEW EFFECT STRUCTURE ---
    "poison_sting": {
        "name": "Poison Sting", "power": 15, "type": "Poison", "category": "Physical",
        "effect": {
            "type": "status",
            "status_effect": "poison",
            "damage_per_turn": 5,
            "duration": 3,
            "chance": 1.0
        }
    },
    "moss_shield": {
        "name": "Moss Shield", "power": 0, "type": "Grass", "category": "Status",
        "effect": {
            "type": "stat_change",
            "stat": "defense",
            "modifier": 1.5,
            "duration": 3,
            "target": "self"
        }
    },
    "ember": {
        "name": "Ember", "power": 40, "type": "Fire", "category": "Special",
        "effect": {
            "type": "status",
            "status_effect": "burn",
            "damage_per_turn": 4,
            "stat_change": {
                "stat": "attack",
                "modifier": 0.75
            },
            "duration": 3,
            "chance": 0.1
        }
    },
    "bug_buzz": {
        "name": "Bug Buzz", "power": 60, "type": "Bug", "category": "Special",
        "effect": {
            "type": "stat_change",
            "stat": "special_defense",
            "modifier": 0.8,  # Lowers target's Sp. Def by 20%
            "duration": 3,
            "chance": 0.2,  # 20% chance
            "target": "opponent"
        }
    },
    "leech_life": {
        "name": "Leech Life", "power": 30, "type": "Bug", "category": "Physical",
        "effect": {
            "type": "heal_on_damage",
            "percent": 0.5  # Heals for 50% of damage dealt
        }
    },
    "pyralis_renewal": {
        "name": "Pyralis's Renewal",
        "power": 70,
        "type": "Fire",
        "category": "Special",
        "description": "Deals Fire damage and grants 'Rebirth' status, healing the user after two turns.",
        "effect": {
            "type": "apply_status",
            "status_effect": "Rebirth",
            "duration": 2,
            "chance": 1.0,
            "target": "self",
            "on_turn_end": {  # A new trigger for our engine
                "type": "delayed_heal",
                "percent": 0.25,
                "trigger_on_turn": 2
            },
            "unique_flag": "revive_once"  # Another new flag
        }
    },
    "borealis_stasis": {
        "name": "Borealis's Stasis",
        "power": 30,
        "type": "Ice",
        "category": "Special",
        "description": "Deals low Ice damage with a high chance to freeze the target.",
        "effect": {
            "type": "apply_status",
            "status_effect": "frozen",
            "duration": 1,
            "chance": 0.8,  # 80% high chance
            "target": "opponent",
            "special_condition": {  # A new key to handle the conditional logic
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
        "description": "Greatly boosts Defense for one turn. If hit during that turn, cleanses a status condition.",
        "effect": [
            {
                "type": "stat_change",
                "stat": "defense",
                "modifier": 2.0,  # "Greatly increases" = 100% boost
                "duration": 1,
                "chance": 1.0,
                "target": "self"
            },
            {
                "type": "apply_status",
                "status_effect": "warded",
                "duration": 1,
                "chance": 1.0,
                "target": "self",
                "on_being_hit": {  # A new trigger for our engine
                    "type": "cleanse_status",
                    "count": 1  # Cleanses one negative status
                }
            }
        ]
    },
    "wyrms_contempt": {
        "name": "Wyrm's Contempt",
        "power": 90,
        "type": "Dragon",
        "category": "Special",  # Assuming it's a special, poison-like breath attack
        "description": "Deals Dragon damage and inflicts 'Corrupting Blight', which damages the target each turn and reduces healing.",
        "effect": {
            "type": "apply_status",
            "status_effect": "corrupting_blight",
            "duration": 3,
            "chance": 1.0,
            "target": "opponent",
            "damage_per_turn": 10,  # A strong damage-over-time effect
            "on_heal_received": {  # A new trigger for our engine
                "modifier": 0.5  # Reduces incoming healing by 50%
            }
        }
    },
    "siphon_sorrow": {
        "name": "Siphon Sorrow",
        "power": 20,  # A base power for when the target has low HP
        "type": "Ghost",
        "category": "Special",
        "description": "Deals more damage the higher the target's HP. Steals one of the target's stat buffs.",
        "power_modifier": {  # A new key to instruct the damage formula
            "type": "scale_with_target_hp_percent",
            "max_power": 110  # The skill's power at 100% target HP
        },
        "effect": [
            {
                "type": "steal_buff",
                "chance": 1.0,
                "target": "opponent"
            }
        ]
    },
    "nexus_conversion": {
        "name": "Nexus Conversion",
        "power": 0,
        "type": "Fighting",
        "category": "Status",
        "description": "A defensive stance. If hit by an elemental attack, damage is reduced and the user's next attack is powered up.",
        "effect": {
            "type": "apply_status",
            "status_effect": "nexus_stance",
            "duration": 1,
            "chance": 1.0,
            "target": "self",
            "on_being_hit": {
                "if_attack_type": ["Fire", "Water", "Grass", "Electric", "Ice"],
                "then_effect": {
                    "damage_modifier": 0.5,  # Reduces incoming damage by 50%
                    "counter_effect": {  # Applies a new status to the user
                        "type": "apply_status",
                        "status_effect": "power_boost",
                        "duration": 2,  # Lasts long enough for the next turn
                        "next_attack_modifier": 1.75  # Boosts next attack's damage by 75%
                    }
                }
            }
        }
    },
    "temporal_echo": {
        "name": "Temporal Echo",
        "power": 60,
        "type": "Psychic",
        "category": "Special",
        "description": "Deals Psychic damage and creates a temporal echo. The next time the target is hit, the echo repeats a portion of that damage on the following turn.",
        "effect": {
            "type": "apply_status",
            "status_effect": "echo",
            "duration": 2,  # Lasts long enough to trigger and then fade
            "chance": 1.0,
            "target": "opponent",
            "on_next_damage_received": {  # A new trigger for our engine
                "type": "delayed_damage",
                "percent": 0.30,  # Repeats 30% of the triggering damage
                "delay_turns": 1  # Damage occurs 1 turn after the trigger
            }
        }
    },
    "crest_resonance": {
        "name": "Crest Resonance",
        "power": 10,  # A very low base power
        "type": "Normal",
        "category": "Special",  # A mystical, energy-based attack
        "description": "Deals damage that grows stronger with each Guild Crest you've obtained.",
        "power_modifier": {
            "type": "scale_with_player_crests",
            "power_per_crest": 12  # The skill gains +12 power for every crest
        }
    },
    "blightborne_fury": {
        "name": "Blightborne Fury",
        "power": 0,
        "type": "Fighting",
        "category": "Status",
        "description": "For 3 turns, the user is overcome with a corrupting fury, greatly raising Attack but also greatly lowering Defense. Attacks gain a chance to inflict 'Blighted' status.",
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
                "type": "apply_status",
                "status_effect": "Rampaging",
                "duration": 3,
                "target": "self",
                "on_attack_hit": {
                    "type": "apply_status",
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
        "power": 140,  # Very high power
        "type": "Rock",
        "category": "Physical",
        "description": "A devastating attack that ignores the target's Defense increases, but leaves the user unable to move on the next turn.",
        "special_flag": "ignores_defense_buffs",  # A new flag for the damage formula
        "effect": {
            "type": "apply_status",
            "status_effect": "recharging",  # A status that prevents action
            "duration": 1,  # Lasts for the next turn
            "chance": 1.0,
            "target": "self"
        }
    },
    "spiteful_bastion": {
        "name": "Spiteful Bastion",
        "power": 0,
        "type": "Steel",  # Assuming Steel type for a bastion
        "category": "Status",
        "description": "A defensive stance. If hit by an attack, the attacker's Attack and Speed are lowered.",
        "effect": {
            "type": "apply_status",
            "status_effect": "spiteful_stance",
            "duration": 1,
            "chance": 1.0,
            "target": "self",
            "on_being_hit": {
                "if_attack_damaging": True,  # A new flag to ensure it only triggers on damaging moves
                "then_effect": {
                    "counter_effect": [  # A list to apply multiple debuffs
                        {
                            "type": "stat_change",
                            "stat": "attack",
                            "modifier": 0.75,  # Lowers Attack by 25%
                            "duration": 3,
                            "target": "opponent"
                        },
                        {
                            "type": "stat_change",
                            "stat": "speed",
                            "modifier": 0.75,  # Lowers Speed by 25%
                            "duration": 3,
                            "target": "opponent"
                        }
                    ]
                }
            }
        }
    },
    "balancing_ward": {
        "name": "Balancing Ward",
        "power": 0,
        "type": "Normal",
        "category": "Status",
        "description": "For one turn, any single attack that would deal more than 50% of the user's max HP is reduced to deal exactly 50%.",
        "effect": {
            "type": "apply_status",
            "status_effect": "balancing_ward",
            "duration": 1,
            "chance": 1.0,
            "target": "self",
            "on_damage_calculation": {  # A new trigger for our engine
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
        "description": "A priority move that strikes first and raises the user's Evasion for the turn.",
        "special_flag": "priority_move",  # A new flag for the turn handler
        "effect": {
            "type": "stat_change",
            "stat": "evasion",  # We will need to add an Evasion stat to pets
            "modifier": 1.5,  # Increases Evasion by 50%
            "duration": 1,
            "chance": 1.0,
            "target": "self"
        }
    },
    "accelerated_decay": {
        "name": "Accelerated Decay",
        "power": 0,
        "type": "Bug",
        "category": "Status",
        "description": "Inflicts a decay that deals small damage after one turn, then large damage after the second.",
        "effect": {
            "type": "apply_status",
            "status_effect": "accelerated_decay",
            "duration": 2,
            "chance": 1.0,
            "target": "opponent",
            "on_turn_end": {
                "type": "damage_sequence",
                "damage": [20, 80]  # Deals 20 damage on the first trigger, 80 on the second
            }
        }
    },
    "equilibrium_shift": {
        "name": "Equilibrium Shift",
        "power": 0,
        "type": "Psychic",
        "category": "Status",
        "description": "Inverts all of the target's stat changes, turning buffs into debuffs and vice-versa.",
        "effect": {
            "type": "stat_inversion",  # A new, unique type for our engine
            "chance": 1.0,
            "target": "opponent",
            "fails_if_no_stat_changes": True  # A flag for the logic handler
        }
    },
    "prophetic_glimpse": {
        "name": "Prophetic Glimpse",
        "power": 0,
        "type": "Psychic",
        "category": "Status",
        "description": "The user's next attack will be super-effective, regardless of type. High chance to fail if used consecutively.",
        "special_flag": "high_fail_rate_on_consecutive_use",  # A flag for the logic handler
        "effect": {
            "type": "apply_status",
            "status_effect": "prophetic_glimpse",
            "duration": 2,  # Lasts long enough for the next turn
            "chance": 1.0,
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
        "description": "Deals Fire damage and burns away one of the target's beneficial status effects or stat buffs.",
        "effect": [
            {
                "type": "remove_buff",  # A new, unique type for our engine
                "count": 1,
                "chance": 1.0,
                "target": "opponent"
            }
        ]
    },
    "tidal_lock": {
        "name": "Tidal Lock",
        "power": 35,
        "type": "Water",
        "category": "Special",
        "description": "Deals Water damage, lowers the target's Speed, and prevents them from fleeing or switching out.",
        "effect": [
            {
                "type": "stat_change",
                "stat": "speed",
                "modifier": 0.75,  # Lowers Speed by 25%
                "duration": 3,
                "chance": 1.0,
                "target": "opponent"
            },
            {
                "type": "apply_status",
                "status_effect": "Tidal Locked",  # A new, unique status
                "duration": 3,
                "chance": 1.0,
                "target": "opponent"
            }
        ]
    },
    "grasping_briar": {
        "name": "Grasping Briar",
        "power": 0,
        "type": "Grass",
        "category": "Status",
        "description": "Inflicts 'Entangled' status, damaging the target and healing the user for the same amount each turn.",
        "effect": {
            "type": "apply_status",
            "status_effect": "Entangled",
            "duration": 3,
            "chance": 1.0,
            "target": "opponent",
            "on_turn_end": {
                "type": "damage_and_leech_hp",  # A new, combined effect type
                "damage_per_turn": 12
            }
        }
    },
    "short_circuit": {
        "name": "Short Circuit",
        "power": 65,
        "type": "Electric",
        "category": "Special",
        "description": "Deals Electric damage and has a chance to scramble the target's focus, preventing them from using the same move consecutively.",
        "effect": {
            "type": "apply_status",
            "status_effect": "Scrambled",
            "duration": 3,
            "chance": 0.3,  # 30% chance to apply
            "target": "opponent",
            "on_action_attempt": {  # A new trigger for our engine
                "prevent_repeat_move": True
            }
        }
    },
    "unyielding_focus": {
        "name": "Unyielding Focus",
        "power": 0,
        "type": "Fighting",
        "category": "Status",
        "description": "A counter-stance. If hit by a physical attack, the user takes reduced damage and strikes back for 1.5x the damage received.",
        "effect": {
            "type": "apply_status",
            "status_effect": "unyielding_focus",
            "duration": 1,
            "chance": 1.0,
            "target": "self",
            "on_being_hit": {
                "if_attack_category": "Physical",  # A new condition for our engine
                "then_effect": {
                    "damage_modifier": 0.75,  # Reduces incoming physical damage by 25%
                    "counter_attack": {  # A new effect type
                        "damage_multiplier_of_received": 1.5
                    }
                }
            }
        }
    },
    "umbral_shift": {
        "name": "Umbral Shift",
        "power": 0,
        "type": "Ghost",
        "category": "Status",
        "description": "User shifts into shadow, gaining a high chance to evade the next attack, but takes recoil damage at the end of the turn.",
        "effect": {
            "type": "apply_status",
            "status_effect": "fading",
            "duration": 1,
            "chance": 1.0,
            "target": "self",
            "on_evade": {
                "chance": 0.90
            },
            "on_turn_end": {
                "type": "recoil_damage",
                "percent_of_max_hp": 0.10
            }
        }
    },
    "draconic_ascendance": {
        "name": "Draconic Ascendance",
        "power": 0,  # The initial use has no power
        "type": "Dragon",
        "category": "Status",
        "description": "A two-turn move. User boosts its stats on turn 1, then unleashes a devastating attack on turn 2.",
        "effect": {
            "type": "two_turn_move",
            "turn_1": {
                "message": "{user_name} is gathering immense draconic energy!",
                "apply_effects": [
                    {
                        "type": "stat_change",
                        "stat": "attack",
                        "modifier": 1.5,
                        "duration": 1,  # Only for the big attack
                        "target": "self"
                    },
                    {
                        "type": "stat_change",
                        "stat": "defense",
                        "modifier": 1.5,
                        "duration": 1,
                        "target": "self"
                    }
                ]
            },
            "turn_2": {
                "message": "{user_name} unleashes its full power!",
                "attack": {
                    "name": "Draconic Burst",  # A name for the attack itself
                    "power": 150,
                    "type": "Dragon",
                    "category": "Physical"
                }
            }
        }
    },
    "caustic_venom": {
        "name": "Caustic Venom",
        "power": 40,
        "type": "Poison",
        "category": "Special",
        "description": "Deals Poison damage and inflicts 'Caustic' status. Healing received is 50% effective, with the other 50% dealt as damage.",
        "effect": {
            "type": "apply_status",
            "status_effect": "caustic_venom",
            "duration": 3,
            "chance": 1.0,
            "target": "opponent",
            "on_heal_received": {
                "healing_modifier": 0.5,  # Reduces incoming healing by 50%
                "deal_damage_from_heal_percent": 0.5  # Deals 50% of the original heal as damage
            }
        }
    },
    "karma_weave": {
        "name": "Karma Weave",
        "power": 0,
        "type": "Fairy",
        "category": "Status",
        "description": "For 2 turns, any stat-lowering debuffs inflicted on the user are also applied to the attacker.",
        "effect": {
            "type": "apply_status",
            "status_effect": "karma_weave",
            "duration": 2,
            "chance": 1.0,
            "target": "self",
            "on_debuff_received": {  # A new trigger for our engine
                "reflect_debuff": True
            }
        }
    },
    "exoskeletal_molt": {
        "name": "Exoskeletal Molt",
        "power": 0,
        "type": "Bug",
        "category": "Status",
        "description": "Removes all stat debuffs from the user, sharply raises Speed, but lowers Defense for 2 turns.",
        "effect": [
            {
                "type": "cleanse_debuffs",  # A new, unique type for our engine
                "target": "self"
            },
            {
                "type": "stat_change",
                "stat": "speed",
                "modifier": 2.0,  # "Sharply raises" = 100% boost
                "duration": 4,
                "target": "self"
            },
            {
                "type": "stat_change",
                "stat": "defense",
                "modifier": 0.75,  # Lowers Defense by 25%
                "duration": 2,
                "target": "self"
            }
        ]
    },
    "geode_charge": {
        "name": "Geode Charge",
        "power": 20,  # Starts very weak
        "type": "Rock",
        "category": "Physical",
        "description": "Deals low Rock damage. Its power increases for the rest of the battle each time the user is damaged.",
        "effect": {
            "type": "apply_status",
            "status_effect": "geode_charge_active",
            "duration": -1,  # -1 can signify the effect lasts for the entire battle
            "chance": 1.0,
            "target": "self",
            "on_being_hit": {
                "if_attack_damaging": True,
                "then_effect": {
                    "type": "increase_move_power",
                    "move_id": "geode_charge",
                    "amount": 20  # Increases its own power by 20
                }
            }
        }
    },
    "last_stand": {
        "name": "Last Stand",
        "power": 1,
        "type": "Normal",
        "category": "Physical",
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
            "description": "Deals Ground damage and binds the target to the earth, removing Flying-type immunities for 3 turns.",
            "effect": {
                "type": "apply_status",
                "status_effect": "Earthbound",
                "duration": 3,
                "chance": 1.0,
                "target": "opponent",
                "special_flag": "removes_ground_immunity" # A new flag for the type calculator
            }
        },
        "adaptive_spirit": {
            "name": "Adaptive Spirit",
            "power": 0,
            "type": "Normal",
            "category": "Status",
            "description": "The user attunes its essence, changing its type to match the last attack it was hit by.",
            "effect": {
                "type": "apply_status",
                "status_effect": "adaptive_spirit",
                "duration": -1, # Lasts for the whole battle or until used again
                "chance": 1.0,
                "target": "self",
                "on_being_hit": {
                    "if_attack_damaging": True,
                    "then_effect": {
                        "type": "change_user_type_to_last_hit" # A new, unique effect type
                    }
                }
            }
        },
        "cinder_trap": {
            "name": "Cinder Trap",
            "power": 0,
            "type": "Fire",
            "category": "Status",
            "description": "Lays a trap of embers. If the opponent makes physical contact, they are burned.",
            "effect": {
                "type": "apply_status",
                "status_effect": "cinder_trap_active",
                "duration": 3,
                "chance": 1.0,
                "target": "opponent_field", # A new target type for field effects
                "on_opponent_action": { # A new trigger for our engine
                    "if_move_is_physical_contact": True,
                    "then_effect": {
                        "counter_effect": {
                            "type": "apply_status",
                            "status_effect": "burn",
                            # We can pull the burn details from another skill or define them here
                            "damage_per_turn": 4,
                            "stat_change": {"stat": "attack", "modifier": 0.75},
                            "duration": 3
                        },
                        "self_remove": True # The trap is consumed after triggering
                    }
                }
            }
        },
        "soothing_veil": {
            "name": "Soothing Veil",
            "power": 0,
            "type": "Water",
            "category": "Status",
            "description": "Surrounds the user with a healing veil of water. At the end of the next turn, the user is healed.",
            "effect": {
                "type": "apply_status",
                "status_effect": "soothing_veil",
                "duration": 2, # Lasts long enough to trigger on the next turn
                "chance": 1.0,
                "target": "self",
                "on_turn_end": {
                    "type": "delayed_heal",
                    "percent": 0.33, # Heals for 33% of max HP
                    "trigger_on_turn": 1 # Triggers at the end of the user's next turn (1 turn remaining)
                }
            }
        },
        "barbed_spores": {
            "name": "Barbed Spores",
            "power": 10, # Very low damage
            "type": "Grass",
            "category": "Special",
            "description": "Deals minor damage and covers the target in irritating spores. For 3 turns, the target's status moves have a 50% chance to fail.",
            "effect": {
                "type": "apply_status",
                "status_effect": "barbed_spores",
                "duration": 3,
                "chance": 1.0,
                "target": "opponent",
                "on_action_attempt": {
                    "if_move_category": "Status", # A new condition for our engine
                    "chance_to_fail": 0.5 # 50% chance
                }
            }
        },
        "magnetic_flux": {
            "name": "Magnetic Flux",
            "power": 0,
            "type": "Electric",
            "category": "Status",
            "description": "Lowers the target's Speed. The effect is doubled against Steel-type pets.",
            "effect": {
                "type": "stat_change",
                "stat": "speed",
                "modifier": 0.75, # Lowers speed by 25% (one stage)
                "duration": 3,
                "chance": 1.0,
                "target": "opponent",
                "special_condition": {
                    "if_target_has_type": "Steel",
                    "then_modifier": 0.50 # Lowers speed by 50% (two stages)
                }
            }
        },
        "permafrost": {
            "name": "Permafrost",
            "power": 0,
            "type": "Ice",
            "category": "Status",
            "description": "Sharply lowers the target's Speed by freezing the ground. Fails if the ground is already frozen.",
            "effect": {
                "type": "stat_change",
                "stat": "speed",
                "modifier": 0.50, # "Sharply lowers" = 50% reduction (two stages)
                "duration": 4,
                "chance": 1.0,
                "target": "opponent",
                "fails_if_target_has_status": "permafrost_debuff" # A new condition for our engine
            },
            "applies_status_on_use": "permafrost_debuff" # A new key to track the debuff for the failure condition
        },
        "aura_break": {
            "name": "Aura Break",
            "power": 75,
            "type": "Fighting",
            "category": "Special", # It's a special move that targets physical defense
            "description": "A focused strike that shatters magical defenses, calculating damage using the target's physical Defense.",
            "special_flag": "calculates_on_physical_defense" # A new flag for the damage formula
        },
        "venomous_haze": {
            "name": "Venomous Haze",
            "power": 0,
            "type": "Poison",
            "category": "Status",
            "description": "For 3 turns, any opponent making physical contact has a high chance of being poisoned.",
            "effect": {
                "type": "apply_status",
                "status_effect": "venomous_haze",
                "duration": 3,
                "chance": 1.0,
                "target": "self",
                "on_being_hit": {
                    "if_attack_is_physical_contact": True,
                    "then_effect": {
                        "counter_effect": {
                            "type": "apply_status",
                            "status_effect": "poison",
                            "damage_per_turn": 5,
                            "duration": 3,
                            "chance": 0.9 # 90% high chance
                        }
                    }
                }
            }
        },
        "earthen_bulwark": {
            "name": "Earthen Bulwark",
            "power": 0,
            "type": "Ground",
            "category": "Status",
            "description": "Increases the user's Defense by two stages, but lowers their Speed by one stage.",
            "effect": [
                {
                    "type": "stat_change",
                    "stat": "defense",
                    "modifier": 2.0, # Increases Defense by 100% (two stages)
                    "duration": 4,
                    "chance": 1.0,
                    "target": "self"
                },
                {
                    "type": "stat_change",
                    "stat": "speed",
                    "modifier": 0.75, # Lowers Speed by 25% (one stage)
                    "duration": 4,
                    "chance": 1.0,
                    "target": "self"
                }
            ]
        },
        "precognition": {
            "name": "Precognition",
            "power": 0,
            "type": "Psychic",
            "category": "Status",
            "description": "The user perfectly predicts the opponent's next move, guaranteeing an evasion. High chance to fail if used consecutively.",
            "special_flag": "high_fail_rate_on_consecutive_use",
            "effect": {
                "type": "apply_status",
                "status_effect": "precognition_active",
                "duration": 1,
                "chance": 1.0,
                "target": "self",
                "on_evade": {
                    "guaranteed_dodge": True # A new flag for our engine
                }
            }
        },
        "infestation": {
            "name": "Infestation",
            "power": 0,
            "type": "Bug",
            "category": "Status",
            "description": "For 4 turns, the target's Attack and Special Attack are slightly lowered at the end of each of their turns.",
            "effect": {
                "type": "apply_status",
                "status_effect": "infestation",
                "duration": 4,
                "chance": 1.0,
                "target": "opponent",
                "on_turn_end": {
                    "type": "recurring_stat_change", # A new, unique type for our engine
                    "changes": [
                        {
                            "stat": "attack",
                            "modifier": 0.95 # Lowers Attack by 5% each turn
                        },
                        {
                            "stat": "special_attack",
                            "modifier": 0.95 # Lowers Sp. Atk by 5% each turn
                        }
                    ]
                }
            }
        },
        "grudge": {
            "name": "Grudge",
            "power": 0,
            "type": "Ghost",
            "category": "Status",
            "description": "If the user is knocked out by a damaging move, the move that defeated it is disabled for the rest of the battle.",
            "effect": {
                "type": "apply_status",
                "status_effect": "grudge",
                "duration": -1, # Lasts until the pet faints or switches out
                "chance": 1.0,
                "target": "self",
                "on_faint": { # A new trigger for our engine
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
            "description": "Deals Dragon damage. If the user's Attack is higher than the target's, the target may flinch.",
            "effect": {
                "type": "apply_status",
                "status_effect": "flinch",
                "duration": 1,
                "chance": 0.3, # 30% chance to flinch
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
            "description": "Once per battle, the user sacrifices half its current health to fully heal the next pet switched in.",
            "special_flag": "once_per_battle", # A new flag for the logic handler
            "effect": {
                "type": "apply_status",
                "status_effect": "spirit_blessing_active",
                "duration": -1, # Lasts until the pet switches out
                "chance": 1.0,
                "target": "self",
                "self_damage": { # A new key to handle the health sacrifice
                    "percent_of_current_hp": 0.5
                },
                "on_switch_out": { # A new trigger for our engine
                    "heal_next_pet_percent": 1.0 # Heals 100% of the next pet's max HP
                }
            }
        },

            #Corroder Added skills
            "rotten_grasp": {
            "name": "Rotten Grasp",
            "power": 30, "type": "Poison", "category": "Physical",
            "description": "A physical attack that deals minor damage but has a high chance to lower the target's speed.",
            "effect": {
                "type": "stat_change", "stat": "speed", "modifier": 0.75, "duration": 3,
                "chance": 0.8, "target": "opponent"
            }
        },
        "corrosive_gaze": {
            "name": "Corrosive Gaze",
            "power": 50, "type": "Poison", "category": "Special",
            "description": "A special attack that deals damage and has a small chance to 'corrode' the opponent's armor, making them take more physical damage.",
            "effect": {
                "type": "stat_change", "stat": "defense", "modifier": 0.8, "duration": 3,
                "chance": 0.3, "target": "opponent"
            }
        },
        "acid_armor": {
            "name": "Acid Armor",
            "power": 0, "type": "Poison", "category": "Status",
            "description": "The user's body liquefies, sharply raising its defense.",
            "effect": {
                "type": "stat_change", "stat": "defense", "modifier": 2.0, "duration": 3,
                "chance": 1.0, "target": "self"
            }
        },
        "sludge_bomb": {
            "name": "Sludge Bomb",
            "power": 80, "type": "Poison", "category": "Special",
            "description": "Hurls a blob of toxic sludge at the opponent with a chance to poison.",
            "effect": {
                "type": "status", "status_effect": "poison", "damage_per_turn": 5, "duration": 3,
                "chance": 0.4
            }
        },
        "venomous_erosion": {
            "name": "Venomous Erosion",
            "power": 30, "type": "Poison", "category": "Special",
            "description": "A special attack that inflicts a poison which grows in power each turn.",
            "effect": {
                "type": "apply_status", "status_effect": "venomous_erosion", "duration": 3,
                "chance": 1.0, "target": "opponent",
                "on_turn_end": {"type": "damage_sequence", "damage": [10, 20, 30]}
            }
        },
        "miasmal_aura": {
            "name": "Miasmal Aura",
            "power": 0, "type": "Poison", "category": "Status",
            "description": "The user is surrounded by a cloud of poison for three turns, poisoning any pet that makes physical contact.",
            "effect": {
                "type": "apply_status", "status_effect": "miasmal_aura", "duration": 3,
                "chance": 1.0, "target": "self",
                "on_being_hit": {
                    "if_attack_category": "Physical",
                    "then_effect": {
                        "counter_effect": {
                            "type": "apply_status", "status_effect": "poison", "damage_per_turn": 5,
                            "duration": 3
                        }
                    }
                }
            }
        },
        "bone_shatter": {
            "name": "Bone Shatter",
            "power": 100, "type": "Rock", "category": "Physical",
            "description": "A powerful attack that uses the golem's bone-like limbs to break down an opponent's defenses.",
            "effect": {
                "type": "stat_change", "stat": "defense", "modifier": 0.75, "duration": 3,
                "chance": 1.0, "target": "opponent"
            }
        },
        "sorrowful_strike": {
            "name": "Sorrowful Strike",
            "power": 50, "type": "Rock", "category": "Physical",
            "description": "An attack that deals more damage the more debuffs the opponent has.",
            "power_modifier": {
                "type": "scale_with_opponent_debuffs", "power_per_debuff": 15
            }
        },
        "seismic_slam": {
            "name": "Seismic Slam",
            "power": 80, "type": "Ground", "category": "Physical",
            "description": "A devastating ground-type attack that lowers the target's speed.",
            "effect": {
                "type": "stat_change", "stat": "speed", "modifier": 0.75, "duration": 3,
                "chance": 1.0, "target": "opponent"
            }
        },
        "ossuary_aegis": {
            "name": "Ossuary Aegis",
            "power": 0, "type": "Rock", "category": "Status",
            "description": "A defensive stance that takes no damage from the next attack and reflects status debuffs back to the attacker.",
            "effect": {
                "type": "apply_status", "status_effect": "ossuary_stance", "duration": 1,
                "chance": 1.0, "target": "self",
                "on_being_hit": {
                    "if_attack_damaging": True,
                    "then_effect": {
                        "damage_modifier": 0.0,
                        "counter_effect": {"type": "reflect_debuffs"}
                    }
                }
            }
        },
        "contagious_blight": {
            "name": "Contagious Blight",
            "power": 0, "type": "Poison", "category": "Status",
            "description": "Spreads an opponent's negative status effects to their allies.",
            "effect": {
                "type": "spread_debuffs", "chance": 1.0, "target": "opponent",
                "targets_allies": True
            }
        },

        #Pyrelisk Added skills
        "scorch": {
            "name": "Scorch", "power": 35, "type": "Fire", "category": "Special",
            "description": "A minor special fire attack that singes the opponent."
        },
        "fireball": {
            "name": "Fireball", "power": 60, "type": "Fire", "category": "Special",
            "description": "Hurls a ball of fire at the opponent."
        },
        "scale_slash": {
            "name": "Scale Slash", "power": 45, "type": "Dragon", "category": "Physical",
            "description": "A physical attack using the pet's scales as a blade."
        },
        "fire_fang": {
            "name": "Fire Fang", "power": 65, "type": "Fire", "category": "Physical",
            "description": "A fiery physical attack that has a small chance to burn the opponent.",
            "effect": {
                "type": "status", "status_effect": "burn", "damage_per_turn": 4, "duration": 3, "chance": 0.1
            }
        },
        "dragon_rush": {
            "name": "Dragon Rush", "power": 80, "type": "Dragon", "category": "Physical",
            "description": "A fast, high-priority physical dragon attack that has a chance to flinch the opponent.",
            "special_flag": "priority_move",
            "effect": {
                "type": "apply_status", "status_effect": "flinch", "duration": 1, "chance": 0.3, "target": "opponent"
            }
        },

        #Dewdrop added skills
        "hydro_pump": {
            "name": "Hydro Pump", "power": 110, "type": "Water", "category": "Special",
            "description": "A powerful, high-risk, high-reward special water attack."
        },
        "blessing_of_aethelgard": {
            "name": "Blessing of Aethelgard", "power": 0, "type": "Fairy", "category": "Status",
            "description": "A supportive move that cleanses all status effects from a target.",
            "effect": {
                "type": "cleanse_status", "target": "ally", "count": -1
            }
        },
        "bubble": {
            "name": "Bubble", "power": 30, "type": "Water", "category": "Special",
            "description": "A minor special water attack that hits with a stream of bubbles."
        },
        "water_pulse": {
            "name": "Water Pulse", "power": 60, "type": "Water", "category": "Special",
            "description": "A pulse of water that has a chance to confuse the opponent.",
            "effect": {
                "type": "apply_status", "status_effect": "confused", "duration": 3, "chance": 0.2, "target": "opponent"
            }
        },
        "drizzle": {
            "name": "Drizzle", "power": 0, "type": "Water", "category": "Status",
            "description": "Summons a gentle drizzle, raising the user's Evasion for 2 turns.",
            "effect": {
                "type": "stat_change", "stat": "evasion", "modifier": 1.3, "duration": 2, "chance": 1.0, "target": "self"
            }
        },

        #terran added skills
        "stone_gaze": {
            "name": "Stone Gaze", "power": 0, "type": "Rock", "category": "Status",
            "description": "A petrifying gaze that can leave an opponent unable to move for a short time.",
            "effect": {
                "type": "apply_status", "status_effect": "petrified", "duration": 1, "chance": 0.8, "target": "opponent"
            }
        },
        "sand_attack": {
            "name": "Sand Attack", "power": 0, "type": "Ground", "category": "Status",
            "description": "Hurls sand at the opponent, lowering their accuracy.",
            "effect": {
                "type": "stat_change", "stat": "accuracy", "modifier": 0.8, "duration": 2, "chance": 1.0,
                "target": "opponent"
            }
        },
        "mud_slap": {
            "name": "Mud Slap", "power": 20, "type": "Ground", "category": "Special",
            "description": "Slaps the opponent with mud."
        },
        "harden": {
            "name": "Harden", "power": 0, "type": "Normal", "category": "Status",
            "description": "Hardens the user's body, raising their Defense.",
            "effect": {
                "type": "stat_change", "stat": "defense", "modifier": 1.5, "duration": 3, "chance": 1.0, "target": "self"
            }
        },
        "enduring_fortitude": {
            "name": "Enduring Fortitude", "power": 0, "type": "Rock", "category": "Status",
            "description": "The user braces for impact, sharply raising its Defense and Special Defense while becoming immune to new debuffs for 2 turns.",
            "effect": {
                "type": "stat_change", "stat": ["defense", "special_defense"], "modifier": 1.5, "duration": 2, "chance": 1.0, "target": "self",
                "additional_effect": {"type": "immunity", "effect_type": "debuff", "duration": 2}
            }
        },
        "mountain_shatter": {
            "name": "Mountain Shatter", "power": 120, "type": "Ground", "category": "Physical",
            "description": "A devastating, slow attack that deals immense damage and has a high chance to stun the opponent.",
            "effect": {
                "type": "apply_status", "status_effect": "stun", "duration": 1, "chance": 0.5, "target": "opponent"
            },
            "special_flag": "low_priority"
        },

        #New Skills here

    }







