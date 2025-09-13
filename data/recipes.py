# data/recipes.py

RECIPES = {
    # --- FIELD CRAFTING ---
    "moss_balm": {
        "name": "Moss Balm",
        "type": "Field",
        "discipline": "Alchemy",
        "required_rank": "Novice",
        "ingredients": {
            "whisperbark_shard": 2,
            "spiritspring_moss": 1},
        "dropdown_description": "Heals your pet for 20 HP.",
        "menu_description": "A healing salve made from forest moss. Heals for 20 HP.",
        "process_log": [
            "You grind the whisperbark shards into a fine, aromatic powder...",
            "Carefully mixing in the glowing moss with a bit of clean water...",
            "The mixture thickens into a soothing, herbal balm."
        ]
    },
    "trail_morsels": {
        "name": "Trail Morsels",
        "type": "Field",
        "discipline": "Cooking",
        "required_rank": "Novice",
        "ingredients": {"sun_kissed_berries": 2, "whisperbark_shard": 1},
        "dropdown_description": "A simple meal that restores pet hunger.",
        "menu_description": "A basic but nutritious meal made from common ingredients. Restores 20 Hunger to a pet.",
        "process_log": [
            "You crush the berries and whisperbark shards into a rough paste...",
            "After drying, the paste forms into simple, effective morsels."
        ]
    },

    # --- MASTER CRAFTING (ALCHEMY) ---
    "purity_orb": {
        "name": "Purity Orb",
        "type": "Master",
        "discipline": "Alchemy",
        "required_rank": "Journeyman",
        "ingredients": { "tether_orb": 3, "mystic_essence": 1 },
        "dropdown_description": "A specialized orb for purifying Gloom-Touched pets.",
        "menu_description": "Requires an Alchemist. Fuses 3 Tether Orbs with Mystic Essence to create a Purity Orb.",
        "process_log": [
            "The Alchemist carefully grinds the essence into a fine powder...",
            "They infuse the tether orbs with the purifying dust...",
            "The orbs now glow with a gentle, cleansing light."
        ]

    },
    "energy_biscuit": {
        "name": "Energy Biscuit",
        "type": "Master",
        "discipline": "Alchemy",
        "required_rank": "Veteran",
        "ingredients": {"mystic_essence": 1, "sun_kissed_berries": 10},
        "dropdown_description": "A biscuit that restores hunger and grants a temporary buff.",
        "menu_description": "Requires an Alchemist. An enchanted biscuit that restores 30 Hunger and boosts a pet's Speed for their next battle.",
        "process_log": [
            "The Alchemist infuses the mystic essence into a paste of crushed berries...",
            "The paste is baked into a biscuit that crackles with contained energy...",
            "The finished biscuit seems to vibrate with a low hum."
        ]
    },

    # --- MASTER CRAFTING (FORGECRAFT) ---
    "recruits_medallion_craftable": {
        "name": "Recruit's Medallion",
        "type": "Master",
        "discipline": "Forgecraft",
        "required_rank": "Novice",
        "ingredients": { "mana_stone": 5 },
        "dropdown_description": "Pet Charm: Boosts Attack.",
        "menu_description": "Requires a Blacksmith. Imbues 5 Mana Stones with energy to forge a medallion that passively boosts a pet's Attack by 5%.",
        "process_log_keys": ["CRAFT_GRIND_DRY", "CRAFT_FORM_PASTE"]
    },
    # --- MASTER CRAFTING (COOKING) ---
    "hearty_stew": {
        "name": "Hearty Stew",
        "type": "Master",
        "discipline": "Cooking",
        "required_rank": "Journeyman",
        "ingredients": {"moss_balm": 1, "sun_kissed_berries": 5},
        "dropdown_description": "A rich stew that restores a large amount of hunger.",
        "menu_description": "Requires a Chef. A thick, aromatic stew that restores 50 Hunger and slightly boosts a pet's Defense for their next battle.",
        "process_log_keys": ["CRAFT_SIMMER_INGREDIENTS", "CRAFT_STEW_AROMA"]
    },
}