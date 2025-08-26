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
    "capture_orb": {
        "name": "Capture Orb",
        "description": "A mystical orb used to capture wild pets.",
        "category": "Consumables",
        "price": 50
    },
    "moss_balm": {
        "name": "Moss Balm",
        "description": "A healing salve made from forest moss. Heals for 20 HP.",
        "category": "Consumables",
        "price": 20
    },
    "sun_kissed_berries": {
        "name": "Sun-Kissed Berries",
        "description": "Sweet berries that restore 25 player energy.",
        "category": "Consumables",
        "price": 20
    },
    "nightshade_root": {
        "name": "Nightshade Root",
        "description": "A potent root that can heal a pet's health for 40 HP.",
        "category": "Consumables",
        "price": 35
    },


    # Crafting Materials
    "mana_stone": {
        "name": "Mana Stone",
        "description": "A crystal humming with raw magical energy. Used to craft powerful artifacts.",
        "category": "Crafting Materials",
        "price": 100,
    },
    "mystic_essence": {
        "name": "Mystic Essence",
        "description": "A rare and volatile crafting material, condensed from pure magic.",
        "category": "Crafting Materials",
        "price": 300,
    },
    "whisperbark_shard": {
        "name": "Whisperbark Shard",
        "description": "A piece of bark that faintly hums with forest magic.",
        "category": "Crafting Materials",
        "price": 5
    },
    "verdant_sporebloom": {
        "name": "Verdant Sporebloom",
        "description": "A rare, luminescent flower sought after by alchemists.",
        "category": "Crafting Materials",
        "price": 50
    },
    "blight_spore": {
        "name": "Blight Spore",
        "description": "A sickly fungus that pulsates with a dark, unsettling energy.",
        "category": "Crafting Materials",
        "price": 10
    },
    "tainted_sludge": {
        "name": "Tainted Sludge",
        "description": "A thick, foul-smelling substance collected from the Rotting Pits. It pulses with a faint, sickly light.",
        "category": "Crafting Materials",
        "price": 15,
    },

    # Gear
    "wooden_sword": {
        "name": "Wooden Sword",
        "description": "A basic training sword. Provides a small attack boost. (+5 Attack)",
        "category": "Gear",
        "price": 25,
    },

    # Key Items (Example)
    "simple_sleeping_bag": {
        "name": "Simple Sleeping Bag",
        "description": "A basic but reliable bag for resting and recovering energy during adventures.",
        "category": "Key Items",
        "price": 150
    },
    "scavengers_compass": {
        "name": "The Scavenger's Compass",
        "description": "A rugged compass salvaged from the pits. It doesn't point north, but it seems to react to hidden wonders, subtly enhancing your chances of finding rare treasures.",
        "category": "key items",
        "price": None
    }
}