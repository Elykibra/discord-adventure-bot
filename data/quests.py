# data/quests.py
# Quests organized by location.
#
# Quest types:
#   main             ⭐ — Story quest with full objectives, narrative, and rewards
#   side             🔵 — Optional NPC quest, completable anytime
#   repeatable_bounty 🔄 — Repeatable kill/gather task
#   assignment       📋 — Guild directive: lightweight task or travel order, no fanfare on complete
#
# Special fields:
#   grants_assignment — quest_id of an assignment to auto-grant when this quest completes

QUESTS = {
    "oakhavenOutpost": {

        # ------------------------------------------------------------------
        # ASSIGNMENTS — lightweight directives, auto-granted by the system
        # ------------------------------------------------------------------

        "report_to_elara": {
            "title": "Report to Recruitment Officer Elara",
            "description": "You've arrived at Oakhaven Outpost. Head to the Guild Recruitment Hut and introduce yourself.",
            "type": "assignment",
            "objectives": [
                {
                    "text": "Speak with Recruitment Officer Elara at the Guild Recruitment Hut.",
                    "type": "talk_npc", "target": "elara"
                }
            ]
        },

        "head_to_whisperwood": {
            "title": "Head to Whisperwood Grove",
            "description": "Your training at Oakhaven is complete. Travel to Whisperwood Grove and continue your work as a Guildsman.",
            "type": "assignment",
            "objectives": [
                {
                    "text": "Travel to Whisperwood Grove.",
                    "type": "travel", "target": "whisperwoodGrove"
                }
            ]
        },

        # ------------------------------------------------------------------
        # MAIN QUESTS
        # ------------------------------------------------------------------

        "a_guildsmans_first_steps": {
            "title": "A Guildsman's First Steps",
            "description": "Recruitment Officer Elara is teaching you the basics of being a Guild Adventurer.",
            "type": "main",
            "grants_assignment": "head_to_whisperwood",  # auto-granted on completion
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
                    "type": "combat_capture", "target": "any"
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

        # ------------------------------------------------------------------
        # SIDE QUESTS
        # ------------------------------------------------------------------

        "sunk_cost": {
            "title": "Sunk Cost",
            "description": "Grit Galen, a scavenger, has lost his satchel of tools in the Rotting Pits. He's asked for your help to retrieve it before it sinks for good.",
            "type": "side",
            "time_sensitive": True,
            "time_limit_ticks": 2,
            "failure_dialogue": "You took too long... my tools are gone for good now. A shame.",
            "objectives": [
                {
                    "text": "Explore the Rotting Pits to find the `Old Satchel`.",
                    "type": "item_pickup", "target": "old_satchel",
                    "zone": "oakhavenOutpost_rottingPits"
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

    # ------------------------------------------------------------------
    # ASHEN VERGE — Kaelen's repeatable boundary-culling bounty
    # ------------------------------------------------------------------
    "ashenVerge": {
        "kaelens_bounty": {
            "title": "Keeping the Line",
            "description": "Serpentine are working their way toward the ash circle's boundary again. Kaelen wants them cleared before the vines take hold.",
            "type": "repeatable_bounty",
            "objectives": [
                {
                    "text": "Defeat 3 Serpentine near the ash circle's boundary.",
                    "type": "combat_victory",
                    "target": "Serpentine",
                    "required_count": 3
                }
            ],
            "reward_coins": 80,
            "reward_item": "ember_charm",
            "reward_item_quantity": 1
        }
    },
}
