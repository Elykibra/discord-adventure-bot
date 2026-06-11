# data/items.py
# This file contains a dictionary of all items in the game.
# This is now the single source of truth for all item data.

ITEMS = {
    "skill_tome": {
        "name": "Skill Tome",  # Generic Name
        "description": "A book containing the knowledge of a single skill.",
        "category": "Consumables",
        "price": 250,  # A base price
        "actions": ["use", "drop", "inspect"],
        "effect": {"type": "teach_skill"}  # Generic effect
    },
    # Consumables
    "moss_balm": {
        "name": "Moss Balm",
        "description": "A healing salve made from forest moss. Heals for 20 HP.",
        "dropdown_description": "Heals your pet.",
        "menu_description": "Heals your pet for 20 HP when used.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "price": 20,
        "effect": {"type": "heal_pet", "value": 20},
        "actions": ["use", "drop", "inspect"]
    },
    "mire_balm": {
        "name": "Mire Balm",
        "description": "A compress made from bog herbs. Slightly less potent than Moss Balm, but Sable always has it in stock. Heals for 15 HP.",
        "dropdown_description": "Heals your pet.",
        "menu_description": "Heals your pet for 15 HP. A Mirefields staple.",
        "category": "Consumables",
        "price": 15,
        "effect": {"type": "heal_pet", "value": 15},
        "actions": ["use", "drop", "inspect"]
    },
    "ember_charm": {
        "name": "Ember Charm",
        "description": "A small charm that always feels faintly warm to the touch, no matter the weather. Carrying one wards off the worst of the cold.",
        "dropdown_description": "Restores player energy.",
        "menu_description": "Restores 15 energy to the player when consumed.",
        "category": "Consumables",
        "price": 25,
        "effect": {"type": "restore_energy", "value": 15},
        "actions": ["use", "drop", "inspect"]
    },
    "sun_kissed_berries": {
        "name": "Sun-Kissed Berries",
        "description": "Sweet berries that restore 25 player energy.",
        "dropdown_description": "Restores player energy.",
        "menu_description": "Restores 25 energy to the player when consumed.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "price": 20,
        "effect": {"type": "restore_energy", "value": 25},
        "actions": ["use", "drop", "inspect"]
    },
    "nightshade_root": {
        "name": "Nightshade Root",
        "description": "A potent root that can heal a pet's health for 40 HP.",
        "dropdown_description": "Heals your pet.",
        "menu_description": "Restores 40 HP to your pet when consumed.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "price": 35,
        "actions": ["use", "drop", "inspect"]
    },

    # Crafting Materials
    "bog_reed_bundle": {
        "name": "Bog Reed Bundle",
        "description": "Dense dried reeds from the Mirefields, bound tight. No use yet — but something this sturdy probably has one.",
        "dropdown_description": "Crafting material.",
        "menu_description": "Dense Mirefields reeds. Future crafting use.",
        "category": "Crafting Materials",
        "price": 8,
        "actions": ["drop", "inspect"],
    },
    "murk_fragment": {
        "name": "Murk Fragment",
        "description": "A shard of mud-rock plating that flakes off a Murkback or Murkwall naturally. Dense and oddly smooth on one side.",
        "dropdown_description": "Crafting material from Murkback.",
        "menu_description": "Shed plating from a Murkback or Murkwall. Future crafting use.",
        "category": "Crafting Materials",
        "price": 12,
        "actions": ["drop", "inspect"],
    },
    "pallefin_scale": {
        "name": "Pallefin Scale",
        "description": "A translucent, faintly luminescent scale shed by a Pallefin or Shimmerdeep. Rare. Catches light in a way that doesn't quite make sense.",
        "dropdown_description": "Rare crafting material from Pallefin.",
        "menu_description": "A rare luminescent scale. Future crafting use.",
        "category": "Crafting Materials",
        "price": 35,
        "actions": ["drop", "inspect"],
    },
    "ash_ember": {
        "name": "Ash Ember",
        "description": "A small ember pried from cold-looking ash. It's still warm. It doesn't cool down.",
        "dropdown_description": "Crafting material from the Ashen Verge.",
        "menu_description": "Still-warm ember shed by Ashen Verge wildlife. Future crafting use.",
        "category": "Crafting Materials",
        "price": 12,
        "actions": ["drop", "inspect"],
    },
    "mana_stone": {
        "name": "Mana Stone",
        "description": "A crystal humming with raw magical energy. Used to craft powerful artifacts.",
        "dropdown_description": "Crafting Material: Magical crystal.",
        "menu_description": "A crystal filled with raw magical energy, used in crafting powerful artifacts.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Crafting Materials",
        "price": 100,
        "actions": ["use", "drop", "inspect"]
    },
    "mystic_essence": {
        "name": "Mystic Essence",
        "description": "A rare and volatile crafting material, condensed from pure magic.",
        "dropdown_description": "Crafting Material: Rare essence.",
        "menu_description": "A condensed form of pure magic, highly sought after for advanced crafting.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Crafting Materials",
        "price": 300,
        "actions": ["use", "drop", "inspect"]
    },
    "whisperbark_shard": {
        "name": "Whisperbark Shard",
        "description": "A piece of bark that faintly hums with forest magic.",
        "dropdown_description": "Crafting Material: Forest shard.",
        "menu_description": "A shard of enchanted bark, used in basic alchemy and crafting.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Crafting Materials",
        "price": 5,
        "actions": ["use", "drop", "inspect"]
    },
    "verdant_sporebloom": {
        "name": "Verdant Sporebloom",
        "description": "A rare, luminescent flower sought after by alchemists.",
        "dropdown_description": "Crafting Material: Rare flower.",
        "menu_description": "A glowing flower prized by alchemists for its alchemical potency.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Crafting Materials",
        "price": 50,
        "actions": ["use", "drop", "inspect"]
    },
    "blight_spore": {
        "name": "Blight Spore",
        "description": "A sickly fungus that pulsates with a dark, unsettling energy.",
        "dropdown_description": "Crafting Material: Dark fungus.",
        "menu_description": "A fungus that carries dark energy, sometimes used in sinister concoctions.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Crafting Materials",
        "price": 10,
        "actions": ["use", "drop", "inspect"]
    },
    "tainted_sludge": {
        "name": "Tainted Sludge",
        "description": "A thick, foul-smelling substance collected from the Rotting Pits. It pulses with a faint, sickly light.",
        "dropdown_description": "Crafting Material: Corrupted sludge.",
        "menu_description": "A foul-smelling sludge, occasionally useful in crafting dark alchemical items.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Crafting Materials",
        "price": 15,
        "actions": ["use", "drop", "inspect"]
    },

    # Gear
    "guild_tunic": {
        "name": "Guild Tunic",
        "description": "The standard issue tunic for a Guild Adventurer. Provides a small bonus to Reputation earned.",
        "dropdown_description": "Gear: Boosts Reputation gain.",
        "menu_description": "Standard Guild attire that grants a 5% bonus to Reputation earned.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 200,
        "slot": "tunic",
        "effect": {"type": "reputation_gain_modifier", "value": 1.05},
        "actions": ["equip", "drop", "inspect"]
    },
    "sturdy_boots": {
        "name": "Sturdy Boots",
        "description": "Well-made leather boots that lessen the burden of long journeys.",
        "dropdown_description": "Gear: Reduces energy cost.",
        "menu_description": "Durable boots that reduce the energy cost of traveling by 10%.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 150,
        "slot": "boots",
        "effect": {"type": "energy_cost_modifier", "value": 0.9},
        "actions": ["equip", "drop", "inspect"]
    },
    "warding_charm": {
        "name": "Warding Charm",
        "description": "A small charm that pulses with protective energy, warding off the worst of the Gloom.",
        "dropdown_description": "Accessory: Reduces Gloom.",
        "menu_description": "An enchanted charm that reduces your starting Gloom by 5.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 300,
        "slot": "accessory",
        "effect": {"type": "gloom_meter_reduction", "value": 5},
        "actions": ["equip", "drop", "inspect"]
    },

    # Key Items
    "simple_sleeping_bag": {
        "name": "Simple Sleeping Bag",
        "description": "A basic but reliable bag for resting and recovering energy during adventures.",
        "dropdown_description": "Resting item: Restore energy.",
        "menu_description": "Allows you to rest and recover energy during adventures.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Key Items",
        "price": 150,
        "actions": ["use", "drop", "inspect"],
    },
    "old_satchel": {
        "name": "Galen's Old Satchel",
        "description": "A tar-stained leather satchel dredged from the Rotting Pits. Smells terrible. Belongs to Grit Galen — return it to him.",
        "dropdown_description": "Quest Item: Return to Grit Galen.",
        "menu_description": "A tar-covered satchel. Grit Galen is waiting for this.",
        "category": "Key Items",
        "price": None,
        "quest_item": True,
        "actions": ["inspect"]
    },
    "scavengers_compass": {
        "name": "The Scavenger's Compass",
        "description": "A rugged compass salvaged from the pits. It doesn't point north, but it seems to react to hidden wonders, subtly enhancing your chances of finding rare treasures.",
        "dropdown_description": "Key Item: Increases treasure chance.",
        "menu_description": "A salvaged compass that improves your chances of finding rare treasures.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Key Items",
        "actions": ["equip", "drop", "inspect"],
        "price": None
    },
    "scavengers_goggles": {
        "name": "Scavenger's Goggles",
        "description": "A pair of sturdy goggles from an old Guild prospector. They have a knack for spotting things others might miss.",
        "dropdown_description": "Gear: Find extra materials.",
        "menu_description": "Prospector’s goggles with a 10% chance to find extra crafting materials.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": ["Gear", "Key Items"],
        "price": None,
        "slot": "head",
        "actions": ["equip", "drop", "inspect"],
        "effect": {"type": "find_extra_materials", "chance": 0.1}
    },

    # Pet Charms
    "recruits_medallion": {
        "name": "Recruit's Medallion",
        "description": "A standard-issue bronze medallion given to new Guild recruits to inspire courage and strength in a pet's first battles.",
        "dropdown_description": "Pet Charm: Boosts Attack.",
        "menu_description": "Grants a passive +5% Attack boost to the equipped pet.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 50,
        "slot": "charm",
        "actions": ["equip", "drop", "inspect"],
        "effect": {"type": "stat_modifier_percent", "stat": "attack", "value": 1.05}
    },
    "oaken_ward": {
        "name": "Oaken Ward",
        "description": "A small, smooth piece of petrified wood from the ancient oak at Oakhaven Outpost, imbued with its resilience and protective nature.",
        "dropdown_description": "Pet Charm: Boosts Defense.",
        "menu_description": "Grants a passive +5% Defense boost to the equipped pet.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 75,
        "slot": "charm",
        "actions": ["equip", "drop", "inspect"],
        "effect": {"type": "stat_modifier_percent", "stat": "defense", "value": 1.05}
    },
    "skylight_plume": {
        "name": "Skylight Plume",
        "description": "A single, impossibly light feather said to have drifted down from Skylight Spire 💨. It seems to grant its holder a touch of the Spire's swiftness.",
        "dropdown_description": "Pet Charm: Boosts Speed.",
        "menu_description": "Grants a passive +5% Speed boost to the equipped pet.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 100,
        "slot": "charm",
        "actions": ["equip", "drop", "inspect"],
        "effect": {"type": "stat_modifier_percent", "stat": "speed", "value": 1.05}
    },
    "soothing_stone": {
        "name": "Soothing Stone",
        "description": "A smooth river stone steeped in healing waters. It constantly radiates a faint, calming energy that helps soothe wounds over time.",
        "dropdown_description": "Pet Charm: Passive HP regen.",
        "menu_description": "Passively restores 3% of your pet’s max HP each turn.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Gear",
        "price": 150,
        "slot": "charm",
        "actions": ["equip", "drop", "inspect"],
        "effect": {"type": "passive_regen_percent", "value": 0.03}
    },

    # Capture Orbs
    "tether_orb": {
        "name": "Tether Orb",
        "description": "A basic orb with a low chance of success. A starter tool for new Recruits.",
        "dropdown_description": "Capture Orb: Low success rate.",
        "menu_description": "A basic Guild orb with the lowest chance of capturing a wild pet. Suited for beginners.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "actions": ["use", "drop", "inspect"],
        "price": 20,
        "orb_data": {"base_multiplier": 1.0}
    },
    "pact_orb": {
        "name": "Pact Orb",
        "description": "The standard Guild-issue orb with a baseline capture rate.",
        "dropdown_description": "Capture Orb: Standard rate.",
        "menu_description": "The Guild’s standard orb, with a reliable baseline chance to capture pets.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "actions": ["use", "drop", "inspect"],
        "price": 100,
        "orb_data": {"base_multiplier": 1.5}
    },
    "purity_orb": {
        "name": "Purity Orb",
        "description": "A specialized orb, essential for purifying Gloom-Touched pets.",
        "dropdown_description": "Capture Orb: Purifies Gloom pets.",
        "menu_description": "Purifies Gloom-Touched pets by reducing their Gloom Meter by 40%, with a strong capture bonus.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "actions": ["use", "drop", "inspect"],
        "price": 250,
        "orb_data": {
            "base_multiplier": 1.0,
            "gloom_effect": {
                "reduction": 40,
                "bonus_multiplier_if_gloom_touched": 2.5
            }
        }
    },
    "dusk_orb": {
        "name": "Dusk Orb",
        "description": "A situational orb whose effectiveness is doubled when used at night.",
        "dropdown_description": "Capture Orb: Strong at night.",
        "menu_description": "Doubles its effectiveness when used at night.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "actions": ["use", "drop", "inspect"],
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
        "dropdown_description": "Capture Orb: Stronger each turn.",
        "menu_description": "Gains strength with each turn that passes in battle, improving capture rates.",
        "image_url": "https://placehold.co/100x100/CD7F32/FFFFFF?text=Medallion",
        "category": "Consumables",
        "actions": ["use", "drop", "inspect"],
        "price": 200,
        "orb_data": {
            "base_multiplier": 1.0,
            "scaling_bonus": {
                "context_key": "turn_count",
                "bonus_per_unit": 0.1
            }
        }
    },

    # --- NEW: Pet Food Items ---
    "trail_morsels": {
        "name": "Trail Morsels",
        "description": "A basic but nutritious meal made from common ingredients. Restores 20 Hunger to a pet.",
        "dropdown_description": "Restores pet hunger.",
        "menu_description": "Restores 20 Hunger to a pet.",
        "category": "Consumables",
        "price": 15,
        "actions": ["use", "drop", "inspect"],
        "effect": {
            "type": "restore_hunger",
            "value": 20
        }
    },
    "hearty_stew": {
        "name": "Hearty Stew",
        "description": "A thick, aromatic stew that restores 50 Hunger and slightly boosts a pet's Defense for their next battle.",
        "dropdown_description": "Restores a large amount of hunger.",
        "menu_description": "Restores 50 Hunger and grants a temporary Defense boost.",
        "category": "Consumables",
        "price": 50,
        "actions": ["use", "drop", "inspect"],
        "effect": {
            "type": "restore_hunger",
            "value": 50
        }
    },
    "energy_biscuit": {
        "name": "Energy Biscuit",
        "description": "An enchanted biscuit that restores 30 Hunger and boosts a pet's Speed for their next battle.",
        "dropdown_description": "Restores hunger and grants a temporary buff.",
        "menu_description": "Restores 30 Hunger and grants a temporary Speed boost.",
        "category": "Consumables",
        "price": 75,
        "actions": ["use", "drop", "inspect"],
        "effect": {
            "type": "restore_hunger",
            "value": 30
        }
    },

    # Lore Items
    "lore_fragment": {
        "name": "Guild Record Fragment",
        "description": (
            "A page torn from a sealed Guild journal found near the Tainted Ledge. "
            "The handwriting is steady until the last few lines, where it isn't."
        ),
        "dropdown_description": "Lore item from the Weeping Chasm.",
        "menu_description": "A fragment from a sealed Guild journal. Read to learn what it contained.",
        "category": "Lore Items",
        "price": 0,
        "actions": ["inspect", "drop"],
        "lore_text": (
            "**Guild Field Record — Warden Post Attachment**\n\n"
            "The handwriting is precise for the first half — dates, creature sightings, "
            "patrol notes. Standard warden documentation.\n\n"
            "Near the bottom the writing changes. Faster. Less careful.\n\n"
            "*'The mist tonight came up from the chasm in a single column. Not diffuse — "
            "directed. It moved toward the post. Stopped at the ward line. "
            "I watched it for approximately four minutes.*\n\n"
            "*It went back down.*\n\n"
            "*I don't know what to put in the official report.'*"
        ),
    },
    "gloom_mist_sample": {
        "name": "Gloom-mist Sample",
        "description": "A sealed vial of dense Gloom-mist collected from a hollow in the rock at the Chasm's Edge. The glass is cold to the touch.",
        "dropdown_description": "Quest item — Kael's research.",
        "menu_description": "A vial of Gloom-mist for Lore-Keeper Kael. Part of the echoes_from_below quest.",
        "category": "Quest Items",
        "price": 0,
        "actions": ["inspect"],
    },
    "waystation_ledger": {
        "name": "Waystation Ledger",
        "description": (
            "Trader records from the Mirefields crossroads, back when it was still active. "
            "Cargo manifests, names, dates — a place that mattered to people. "
            "The last entry cuts off mid-sentence. The ink is still dry."
        ),
        "dropdown_description": "Lore item from the Old Crossroads.",
        "menu_description": "Records from the Mirefields waystation. Read to learn its history.",
        "category": "Lore Items",
        "price": 0,
        "actions": ["inspect", "drop"],
        "lore_text": (
            "**Waystation Ledger — Final Entries**\n\n"
            "The records are methodical until the last few pages. Cargo in, cargo out. "
            "Names of traders, quantities, dates. A place that worked.\n\n"
            "The second-to-last entry notes a \"territorial disturbance near the south "
            "foundation\" and a recommendation to reroute the eastern path.\n\n"
            "The last entry is dated two weeks later. It reads: *\"Something has moved into "
            "the ruins. Orin says leave it. Vessan says we can drive it out if we —\"*\n\n"
            "It stops there."
        ),
    },
}