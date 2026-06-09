# data/wandering_npcs.py
# Wandering NPCs that can appear on roads between towns.
#
# Structure:
#   WANDERING_NPCS  — base pool, any NPC here can appear on any road
#   PATH_ENCOUNTERS — per-road overrides: which NPCs appear and at what weight
#
# To add a road-exclusive NPC, define it in WANDERING_NPCS and only reference
# it in the specific PATH_ENCOUNTERS entry you want it to appear in.

WANDERING_NPCS = {

    # -------------------------------------------------------------------------
    # NON-COMBAT
    # -------------------------------------------------------------------------

    "traveling_merchant": {
        "name": "Rowan",
        "title": "Traveling Merchant",
        "emoji": "🧳",
        "type": "merchant",
        "dialogue": {
            "greeting": "Ah, a fellow traveler! I've got wares from all across Aethelgard. Take a look — you won't find these prices in any town.",
            "farewell": "Safe roads, Adventurer. Watch your step out there.",
        },
        "shop_pool": ["moss_balm", "tether_orb", "trail_morsels", "simple_sleeping_bag"],
        # Rotates a random subset of shop_pool each encounter
        "shop_size": 3,
    },

    "guild_courier": {
        "name": "Guild Courier",
        "title": "Guild Courier",
        "emoji": "📜",
        "type": "quest_hint",
        "dialogue": {
            "greeting": "Courier business — no time to chat. But I did hear something at the last outpost you might want to know.",
            "hint": "Word from the Guild: keep your eyes open on these roads. Things have been... unsettled lately.",
            "farewell": "I've got a dozen more deliveries. Good luck out there.",
        },
    },

    "field_medic": {
        "name": "Field Medic",
        "title": "Wandering Healer",
        "emoji": "💊",
        "type": "service",
        "dialogue": {
            "greeting": "You look like you've had a rough go of it. I can patch up your companion for a few coins — proper supplies cost money, after all.",
            "after_heal": "There we go. Good as new. Try not to get them banged up too quickly.",
            "farewell": "Take care of that companion. They're counting on you.",
        },
        "service": {
            "type": "heal_pet",
            "cost": 20,
            "heal_percent": 50,
        },
    },

    "lost_adventurer": {
        "name": "Lost Adventurer",
        "title": "Wayward Adventurer",
        "emoji": "🗺️",
        "type": "mini_quest",
        "dialogue": {
            "greeting": "Oh thank the Spirits — another person! I've been wandering these roads for hours. I think I took a wrong turn somewhere near the last landmark...",
            "quest_offer": "If you could just point me toward the nearest town, I'd make it worth your while. I've got some supplies I can spare.",
            "quest_complete": "You're a lifesaver. Literally. Here — take this. I was saving it, but I owe you.",
            "farewell": "I'll be more careful next time. Probably.",
        },
        "reward_coins": 30,
        "reward_items": ["moss_balm", "trail_morsels"],  # picks one randomly
    },

    "gloom_scout": {
        "name": "Gloom Scout",
        "title": "Guild Scout",
        "emoji": "👁️",
        "type": "intel",
        "dialogue": {
            "greeting": "Halt — Guild Scout. I've been tracking Gloom activity along this road. You'll want to hear this before you head further.",
            "warning_low": "Gloom levels are low ahead. You're fine for now, but don't linger.",
            "warning_high": "I'd be careful. The Gloom is thick further down this road. Make sure your companion is in good shape.",
            "farewell": "Stay sharp. The Gloom doesn't announce itself.",
        },
    },

    "drifter": {
        "name": "The Drifter",
        "title": "Mysterious Drifter",
        "emoji": "🎲",
        "type": "gamble",
        "dialogue": {
            "greeting": "You look like someone who appreciates a good gamble. I've got something in this pack — could be junk, could be treasure. Fifty coins says it's worth your while.",
            "win": "Ha! Lady luck smiles on you today, Adventurer.",
            "lose": "Better luck next time. That's the way of things.",
            "farewell": "The road gives and the road takes. See you around.",
        },
        "gamble": {
            "cost": 50,
            "win_chance": 0.45,
            "win_reward_coins": 120,
            "win_reward_items": ["moss_balm", "tether_orb", "trail_morsels"],
            "lose_reward_items": [],
        },
    },

    # -------------------------------------------------------------------------
    # COMBAT — COMPETITIVE
    # -------------------------------------------------------------------------

    "rival_adventurer": {
        "name": "Rival Adventurer",
        "title": "Guild Rival",
        "emoji": "⚔️",
        "type": "battle_competitive",
        "dialogue": {
            "greeting": "Well, well. Another Guild Adventurer. I've heard good things — let's see if the reputation holds. One battle, no hard feelings.",
            "win": "Good fight. You've earned that. I'll remember this.",
            "lose": "Don't take it personally. Get stronger and find me again — I'd like a rematch.",
            "farewell": "Till next time, Adventurer.",
        },
        "battle": {
            "difficulty": "medium",
            "win_coins": 80,
            "win_reputation": 5,
            "lose_coins": 0,        # no penalty from rival
        },
    },

    # -------------------------------------------------------------------------
    # COMBAT — NEUTRAL
    # -------------------------------------------------------------------------

    "wandering_duelist": {
        "name": "Wandering Duelist",
        "title": "Road Duelist",
        "emoji": "🥊",
        "type": "battle_neutral",
        "dialogue": {
            "greeting": "I travel these roads for one reason — to find strong companions and test myself against them. Yours looks capable. Shall we?",
            "win": "Impressive. You've given me something to think about on the road ahead.",
            "lose": "Train harder. The road ahead won't be so forgiving.",
            "farewell": "Good roads, Adventurer.",
        },
        "battle": {
            "difficulty": "medium",
            "win_coins": 60,
            "win_reputation": 3,
            "lose_coins": 15,       # small penalty — they take a small toll
        },
    },

}

# -----------------------------------------------------------------------------
# PATH ENCOUNTERS
# Per-road configuration. "pool" controls which NPCs can appear.
# "weights" controls relative frequency (higher = more common).
# Omitting a path uses the full WANDERING_NPCS pool at equal weight.
# -----------------------------------------------------------------------------

PATH_ENCOUNTERS = {

    # Oakhaven Outpost __ Whisperwood Grove
    "oakhavenOutpost__whisperwoodGrove": {
        "pool": [
            "traveling_merchant",
            "guild_courier",
            "field_medic",
            "lost_adventurer",
            "gloom_scout",
            "rival_adventurer",
            "wandering_duelist",
        ],
        "weights": [20, 15, 15, 20, 10, 10, 10],
    },

    # Whisperwood Grove __ Sunstone Oasis (stub — fill in when Town 3 is built)
    "whisperwoodGrove__sunstoneOasis": {
        "pool": [
            "traveling_merchant",
            "guild_courier",
            "field_medic",
            "gloom_scout",
            "rival_adventurer",
            "wandering_duelist",
            "drifter",
        ],
        "weights": [20, 10, 15, 15, 15, 15, 10],
    },

}
