# data/items.py
# This file contains a dictionary of all items in the game.
# This is now the single source of truth for all item data.

ITEMS = {
    # Consumables
    "potion": {
        "name": "Potion",
        "description": "A standard potion that heals your pet for 50 health.",
        "category": "Consumables",
        "price": 50,
    },
    "greater_potion": {
        "name": "Greater Potion",
        "description": "A powerful potion that heals your pet for 150 health.",
        "category": "Consumables",
        "price": 150,
    },
    "moss_balm": {
        "name": "Moss Balm",
        "description": "A healing salve made from forest moss. Heals for 20 HP.",
        "category": "Consumables",
        "price": 20,
        "effect": {"type": "heal_pet", "value": 20},
        "actions": ["use", "drop", "inspect"]
    },
    "sun_kissed_berries": {
        "name": "Sun-Kissed Berries",
        "description": "Sweet berries that restore 25 player energy.",
        "category": "Consumables",
        "price": 20,
        "effect": {"type": "restore_energy", "value": 25},
        "actions": ["use", "drop", "inspect"]  # <-- New format
    },
    "nightshade_root": {
        "name": "Nightshade Root",
        "description": "A potent root that can heal a pet's health for 40 HP.",
        "category": "Consumables",
        "price": 35,
        "actions": ["use", "drop", "inspect"] # <-- New format
    },


    # Crafting Materials
    "mana_stone": {
        "name": "Mana Stone",
        "description": "A crystal humming with raw magical energy. Used to craft powerful artifacts.",
        "category": "Crafting Materials",
        "price": 100,
        "actions": ["drop"]
    },
    "mystic_essence": {
        "name": "Mystic Essence",
        "description": "A rare and volatile crafting material, condensed from pure magic.",
        "category": "Crafting Materials",
        "price": 300,
        "actions": ["drop"]
    },
    "whisperbark_shard": {
        "name": "Whisperbark Shard",
        "description": "A piece of bark that faintly hums with forest magic.",
        "category": "Crafting Materials",
        "price": 5,
        "actions": ["drop"]
    },
    "verdant_sporebloom": {
        "name": "Verdant Sporebloom",
        "description": "A rare, luminescent flower sought after by alchemists.",
        "category": "Crafting Materials",
        "price": 50,
        "actions": ["drop"]
    },
    "blight_spore": {
        "name": "Blight Spore",
        "description": "A sickly fungus that pulsates with a dark, unsettling energy.",
        "category": "Crafting Materials",
        "price": 10,
        "actions": ["drop"]
    },
    "tainted_sludge": {
        "name": "Tainted Sludge",
        "description": "A thick, foul-smelling substance collected from the Rotting Pits. It pulses with a faint, sickly light.",
        "category": "Crafting Materials",
        "price": 15,
        "actions": ["drop"]
    },

    # Gear
    "wooden_sword": {
        "name": "Wooden Sword",
        "description": "A basic training sword. Provides a small attack boost. (+5 Attack)",
        "category": "Gear",
        "price": 25,
        "actions": ["equip", "drop"]
    },

    # --- NEW TUNIC ITEM ---
    "guild_tunic": {
        "name": "Guild Tunic",
        "description": "The standard issue tunic for a Guild Adventurer. Provides a small bonus to Reputation earned.",
        "category": "Gear",
        "price": 200,
        "slot": "tunic",
        "effect": {"type": "reputation_gain_modifier", "value": 1.05},  # 5% bonus
        "actions": ["equip", "drop", "inspect"] # <-- New format
    },

    # --- NEW BOOTS ITEM ---
    "sturdy_boots": {
        "name": "Sturdy Boots",
        "description": "Well-made leather boots that lessen the burden of long journeys.",
        "category": "Gear",
        "price": 150,
        "slot": "boots",
        "effect": {"type": "energy_cost_modifier", "value": 0.9}, # 10% energy reduction
        "actions": ["equip", "drop", "inspect"]  # <-- New format
    },

    # --- NEW ACCESSORY ITEM ---
    "warding_charm": {
        "name": "Warding Charm",
        "description": "A small charm that pulses with protective energy, warding off the worst of the Gloom.",
        "category": "Gear",
        "price": 300,
        "slot": "accessory",
        "effect": {"type": "gloom_meter_reduction", "value": 5},  # Reduces starting Gloom by 5
        "actions": ["equip", "drop", "inspect"]
    },

    # Key Items (Example)
    "simple_sleeping_bag": {
        "name": "Simple Sleeping Bag",
        "description": "A basic but reliable bag for resting and recovering energy during adventures.",
        "category": "Key Items",
        "price": 150,
        "actions": []
    },
    "scavengers_compass": {
        "name": "The Scavenger's Compass",
        "description": "A rugged compass salvaged from the pits. It doesn't point north, but it seems to react to hidden wonders, subtly enhancing your chances of finding rare treasures.",
        "category": "key items",
        "price": None
    },
    "scavengers_goggles": {
        "name": "Scavenger's Goggles",
        "description": "A pair of sturdy goggles from an old Guild prospector. They have a knack for spotting things others might miss.",
        "category": "Gear",
        "price": 150,  # Sell price
        "slot": "head",  # The equipment slot it uses
        "actions": ["equip", "drop"],
        "effect": {
            "type": "find_extra_materials",
            "chance": 0.1  # 10% chance
        }
    },

    # --- CAPTURE ORBS ---
    "tether_orb": {
        "name": "Tether Orb",
        "description": "A basic orb with a low chance of success. A starter tool for new Recruits.",
        "category": "Consumables",
        "price": 20,
        "orb_data": {
            "base_multiplier": 1.0
        }
    },
    "pact_orb": {
        "name": "Pact Orb",
        "description": "The standard Guild-issue orb with a baseline capture rate.",
        "category": "Consumables",
        "price": 100,
        "orb_data": {
            "base_multiplier": 1.5
        }
    },
    "purity_orb": {
        "name": "Purity Orb",
        "description": "A specialized orb, essential for purifying Gloom-Touched pets.",
        "category": "Consumables",
        "price": 250,
        "orb_data": {
            "base_multiplier": 1.0,
            "gloom_effect": {
                "reduction": 40,  # Reduces Gloom Meter by 40%
                "bonus_multiplier_if_gloom_touched": 2.5  # Extra capture bonus
            }
        }
    },
    "dusk_orb": {
        "name": "Dusk Orb",
        "description": "A situational orb whose effectiveness is doubled when used at night.",
        "category": "Consumables",
        "price": 150,
        "orb_data": {
            "base_multiplier": 1.0,
            "conditional_bonus": {
                "context_key": "time_of_day",
                "expected_value": "night",
                "multiplier": 2.0
            }
        }
    },
    "steadfast_orb": {
        "name": "Steadfast Orb",
        "description": "A strategic orb whose effectiveness increases with each turn that passes in battle.",
        "category": "Consumables",
        "price": 200,
        "orb_data": {
            "base_multiplier": 1.0,
            "scaling_bonus": {
                "context_key": "turn_count",
                "bonus_per_unit": 0.1
            }
        }
    },
}