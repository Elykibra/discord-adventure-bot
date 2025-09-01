# data/quests.py
# This file contains a dictionary of all quests in the game, organized by location.

QUESTS = {
    "oakhavenOutpost": {
        "a_guildsmans_first_steps": {
            "title": "A Guildsman's First Steps",
            "description": "Recruitment Officer Elara is teaching you the basics of being a Guild Adventurer.",
            "type": "main",
            "objectives": [
                {
                    "text": "Speak with Recruitment Officer Elara.",
                    "type": "talk_npc", "target": "elara"
                },
                {
                    "text": "Gather a `Sun-Kissed Berry` from the wild.",
                    "type": "item_pickup", "target": "sun_kissed_berries"
                },
                {
                    "text": "Use the `Sun-Kissed Berry` from your inventory.",
                    "type": "item_use", "target": "sun_kissed_berries"
                },
                {
                    "text": "Defeat one wild pet in combat.",
                    "type": "combat_victory", "target": "any"
                },
                {
                    "text": "Report your victory to Recruitment Officer Elara.",
                    "type": "talk_npc", "target": "elara"
                },
                {
                    "text": "Capture a wild pet using the Tether Orb.",
                    "type": "combat_capture", "target": "any"  # A new type for our engine
                },
                {
                    "text": "Rest at the `Weary Wanderer's Bench` to recover.",
                    "type": "rest", "target": "rest_point"
                },
                {
                    "text": "Speak with Grit Galen near the Rotting Pits.",
                    "type": "talk_npc", "target": "grit_galen"
                },
                {
                    "text": "Return to Recruitment Officer Elara for your final briefing.",
                    "type": "talk_npc", "target": "elara"
                }
            ],
            "reward_coins": 100,
            "reward_reputation": 25,
            "reward_item": "tether_orb",
            "reward_item_quantity": 5
        },

        "sunk_cost": {
            "title": "Sunk Cost",
            "description": "Grit Galen, a scavenger, has lost his satchel of tools in the Rotting Pits. He's asked for your help to retrieve it before it sinks for good.",
            "type": "side",
            "time_sensitive": True,
            "failure_dialogue": "You took too long... my tools are gone for good now. A shame.",
            "objectives": [
                {
                    "text": "Explore the Rotting Pits to find the `Old Satchel`.",
                    "type": "item_pickup", "target": "old_satchel"
                },
                {
                    "text": "Return the `Old Satchel` to Grit Galen.",
                    "type": "talk_npc", "target": "grit_galen"
                }
            ],
            "reward_item": "scavengers_goggles",
            "reward_reputation": 20
        }
    },

    "whisperwoodGrove": {
        "forest_cleanup": {
            "title": "Forest Cleanup",
            "description": "The forest is overrun with hostile creatures. Thin their numbers.",
            "type": "repeatable_bounty",
            "objectives": [
                "Defeat 5 wild pets in Whisperwood Grove."
            ],
            "reward_coins": 250,
            "reward_items": {"mana_stone": 2}
        }
    },
    # Future towns like sunstoneOasis would have their own sections here
}