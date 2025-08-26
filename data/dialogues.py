# data/dialogues.py
# This file contains all NPC dialogue trees for the game.

DIALOGUES = {
    "elara": {
        "name": "Recruitment Officer Elara", "role": "Guild Officer",
        "dialogue_tree": [
            # This is the dialogue for after the quest is totally finished.
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 6},
             "text": "You've learned the basics of adventuring. You're ready. Your next destination is Whisperwood Grove. Good luck, recruit."},

            # The dialogues for steps 2 through 5 are correct.
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 5},
             "text": "You've spoken to Galen, I see. He's a good reminder that not all adventures end in glory."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 4},
             "text": "Feeling refreshed? Good. There's one last person you should meet... Go have a word with him."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 3},
             "text": "A successful hunt! ... Go rest at the bench by the campfire to recover."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 2},
             "text": "Well done. Managing your items is a key skill. Now, for your first real test..."},

            # This is the dialogue for a player who is currently ON the berry-gathering step.
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 1},
             "text": "I see you're still looking for a Sun-Kissed Berry. You'll need to use the `/adventure` command and explore the wilds outside the outpost to find one."},

            # This is now the ONLY entry for a new player. It will grant the quest.
            {"action": "grant_quest", "quest_id": "a_guildsmans_first_steps",
             "text": "Welcome to the outpost, recruit. I'm Recruitment Officer Elara. Now that you're here, we can begin your training. Your first task is to explore the wilds just outside the outpost and gather a Sun-Kissed Berry. Let me know when you have it."}
        ]
    },
    "grit_galen": {
        "name": "Grit Galen", "role": "Scavenger",
        "dialogue_tree": [
            {"required_quest_status": {"quest_id": "sunk_cost", "status": "completed"}, "text": "Thanks again for finding my tools. That compass will serve you well."},
            {"required_quest_status": {"quest_id": "sunk_cost", "status": "failed"}, "text": "Nothing to say to you, adventurer. You had your chance to help."},
            {"required_item": "old_satchel", "action": "complete_quest", "quest_id": "sunk_cost", "text": "You found it! By the Spirits, I thought it was lost for good. Here, take this. It's a compass of sorts. Doesn't point north, but it has a knack for finding things that don't want to be found."},
            {"required_quest_status": {"quest_id": "sunk_cost", "status": "active"}, "text": "Still looking for my satchel? Be careful down there. The Gloom makes things... twitchy."},
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 5}, "action": "offer_quest", "quest_id": "sunk_cost", "text": "Lost my satchel of tools in there... sinking fast. If you've got the nerve to fetch it, I'll make it worth your while."},
            {"default": "Another fresh face from the Guild. Don't get too close to these pits, adventurer."}
        ]
    }
}