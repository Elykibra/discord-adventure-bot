# data/dialogues.py
# This file contains all NPC dialogue trees for the game.

DIALOGUES = {
    "elara": {
        "name": "Recruitment Officer Elara", "role": "Guild Officer",
        "dialogue_tree": [
            # Final quest step dialogue
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 8},
             "text": "You've learned the basics of adventuring. You're ready. Your next destination is Whisperwood Grove. Good luck, recruit."},

            # New dialogues for the new steps
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 7},
             "text": "You've spoken to Galen, I see. He's a good reminder that not all adventures end in glory. Return to me when you are ready."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 6},
             "text": "Feeling refreshed? Good. There's one last person you should meet here in the outpost. Go have a word with Grit Galen."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 5},
             "text": "Excellent work, recruit. A successful capture is a sign of a true Guildsman. Now, go rest at the bench by the campfire to recover."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 4},
             "action": "grant_item", "item_id": "tether_orb", "quantity": 1,
             "text": "A fine victory. You've proven you can fight. But a Guildsman's duty is to restore balance, not just defeat. Take this Tether Orb. Show me you can tame a wild spirit."},

            # Existing dialogues (indices are now shifted)
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 3},
             "text": "A successful hunt! Now report back to me at the Recruitment Hut."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 2},
             "text": "Well done. Managing your items is a key skill. Now, for your first real test... head into the wilds and defeat a creature in combat."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 1},
             "text": "I see you're still looking for a Sun-Kissed Berry. You'll find one by exploring the wilds outside the outpost."},

            # Initial quest-granting dialogue
            {"action": "grant_quest", "quest_id": "a_guildsmans_first_steps",
             "text": "Welcome, recruit. To start, explore the wilds just outside the outpost and gather a Sun-Kissed Berry. Let me know when you have it."}
        ]
    },
    "grit_galen": {
        "name": "Grit Galen", "role": "Scavenger",
        "dialogue_tree": [
            {"required_quest_status": {"quest_id": "sunk_cost", "status": "completed"}, "text": "Thanks again for finding my tools. That compass will serve you well."},
            {"required_quest_status": {"quest_id": "sunk_cost", "status": "failed"}, "text": "Nothing to say to you, adventurer. You had your chance to help."},

            {"required_item": "old_satchel",
             "action": "complete_quest",
             "quest_id": "sunk_cost",
             "text": "You found it! By the Spirits... let's see what's left. *Galen rummages through the tar-covered bag, pulling out ruined tools.* Rusted... ruined... a shame. Ah, but these... *He salvages a pair of sturdy goggles.* They survived. From my old days as a Guild prospector. They've got a knack for spotting things others might miss. They're yours. A proper reward for a proper Guildsman."},

            {"required_quest_status": {"quest_id": "sunk_cost", "status": "active"},
             "text": "Still looking for my satchel? Be careful down there. The Gloom makes things... twitchy."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 5}, "action": "offer_quest", "quest_id": "sunk_cost", "text": "Lost my satchel of tools in there... sinking fast. If you've got the nerve to fetch it, I'll make it worth your while."},
            {"default": "Another fresh face from the Guild. Don't get too close to these pits, adventurer. The Gloom here makes everything... twitchy."}
        ]
    }
}