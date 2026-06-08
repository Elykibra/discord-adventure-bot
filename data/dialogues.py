# data/dialogues.py
# This file contains all NPC dialogue trees for the game.

DIALOGUES = {
    "elara": {
        "name": "Recruitment Officer Elara", "role": "Guild Officer",
        "dialogue_tree": [
            # Final quest step dialogue
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 8},
             "text": "You've learned the basics of adventuring. You've explored, fought, captured, and survived the Rotting Pits. You're no longer a recruit — you're a Guildsman. Your next destination is **Whisperwood Grove**. Use the Travel option from the outpost hub to move on. The Guild expects reports. Don't keep them waiting."},

            # New dialogues for the new steps
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 7},
             "text": "You've spoken to Galen, I see. He's a good reminder that not all adventures end in glory. Return to me when you are ready."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 6},
             "text": "Feeling refreshed? Good. There's one last person you should meet before you head out — Grit Galen, near the Rotting Pits. One warning: that area is saturated with Gloom. Watch the Gloom Meter during battle. If it climbs past 40%, enemy strikes hit harder. Past 80%, you'll take damage just standing in it. Hit 100% and the Gloom will surge — take a heavy hit. Keep it low, and you'll be fine."},
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
    "bea": {
        "name": "Bea", "role": "Supply Merchant",
        "dialogue_tree": [
            {"required_flag": "quest_a_guildsmans_first_steps_completed",
             "text": "Elara send you off already? You made it through faster than most. Come back when you're running low — I'll be here."},
            {"default": "Looking or buying? Either way, touch the chest, not the stock. Everything's priced fair — I've been robbed before and I've got a long memory."}
        ]
    },
    "grit_galen": {
        "name": "Grit Galen", "role": "Scavenger",
        "dialogue_tree": [
            {"required_flag": "quest_sunk_cost_completed", "text": "Thanks again for finding my tools. The goggles will serve you better than they did me — my eyes aren't what they were."},
            {"required_flag": "quest_sunk_cost_failed", "text": "Nothing to say to you, adventurer. You had your chance to help and the pits took the rest."},

            {"required_item": "old_satchel",
             "action": "complete_quest",
             "quest_id": "sunk_cost",
             "text": "You found it! By the Spirits... let's see what's left. *Galen rummages through the tar-covered bag, pulling out ruined tools.* Rusted... ruined... a shame. Ah, but these... *He salvages a pair of sturdy goggles.* They survived. From my old days as a Guild prospector. They've got a knack for spotting things others might miss. They're yours. A proper reward for a proper Guildsman."},

            {"required_quest_status": {"quest_id": "sunk_cost", "status": "active"},
             "text": "Still looking for my satchel? Be careful down there. The Gloom makes things... twitchy."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 5}, "action": "grant_quest", "quest_id": "sunk_cost", "text": "Lost my satchel of tools in the Rotting Pits earlier today. Tar gets deeper every day down there — once something sinks past a certain point, it doesn't come back up. I'd say you've got a day or two at most before it's gone for good. Find it and I'll make it worth your while."},
            {"default": "Another fresh face from the Guild. Don't get too close to these pits, adventurer. The Gloom here makes everything... twitchy."}
        ]
    }
}