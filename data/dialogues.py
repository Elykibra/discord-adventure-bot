# data/dialogues.py
# NPC dialogue trees. Conditions are checked top-to-bottom; first match wins.
#
# Supported condition keys:
#   required_flag        — player must have this flag set
#   required_item        — player must have this item in inventory
#   required_quest_status — {"quest_id": "x", "status": "active"|"completed"|"failed"}
#   required_quest_step  — {"quest_id": "x", "step": N}  (matches when count == N)
#   required_time        — list of valid phases: ["morning","noon","evening","night"]
#
# text / default can be a string OR a list — a list picks a random line each visit.

DIALOGUES = {

    # -------------------------------------------------------------------------
    # ELARA — Recruitment Officer. Professional, efficient, quietly proud.
    # She's processed a hundred recruits. Most don't make it past the wilds.
    # -------------------------------------------------------------------------
    "elara": {
        "name": "Recruitment Officer Elara", "role": "Guild Officer",
        "dialogue_tree": [

            # --- Post-graduation, night ---
            {"required_flag": "quest_a_guildsmans_first_steps_completed",
             "required_time": ["night"],
             "text": "Still here? Whisperwood won't wait forever. Rest if you must — but move on soon."},

            # --- Post-graduation ---
            {"required_flag": "quest_a_guildsmans_first_steps_completed",
             "text": [
                 "You've earned your title, Guildsman. Whisperwood awaits — don't keep them waiting.",
                 "Not many recruits make it through that quickly. The Guild is watching. Don't waste the attention.",
                 "I've filed your advancement report. You're a Guildsman now. That means more is expected of you, not less.",
                 "Whisperwood Grove is your next destination. The work there is different — less straightforward. You'll see.",
             ]},

            # --- Tutorial step dialogues (keep in order, highest step first) ---
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 8},
             "text": "You've done it. Explored, fought, captured, survived the Rotting Pits. You're a Guildsman now — not a recruit. Head to Whisperwood Grove when you're ready. The Guild expects results."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 7},
             "text": "Galen's seen more of this world than most. Whatever he told you — take it seriously. Come back to me when you're done."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 6},
             "text": "Feeling rested? Good. One last stop before we're done — Grit Galen, near the Rotting Pits. Fair warning: that area is saturated with Gloom. Watch your Gloom Meter. Past 40%, enemies hit harder. Past 80%, it starts draining you just standing there. Hit 100% and the Gloom surges — heavy damage, instant reset. Keep it low."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 5},
             "text": "A live capture. Not easy. Good work. Now go rest — the bench by the campfire. You've earned it, and your pet needs the recovery time too."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 4},
             "action": "grant_item", "item_id": "tether_orb", "quantity": 1,
             "text": "Victory in the field. You can fight — that's clear. But a Guildsman restores balance, not just defeats it. Take this Tether Orb. Show me you can bring one back alive."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 3},
             "text": "Good — you made it back. A victory is a victory. Now come find me at the Recruitment Hut."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 2},
             "text": "Managing your supplies is half the job. You've got it. Now — your first real test. Head into the wilds and win a fight."},

            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 1},
             "text": "Still hunting for that berry? Check the wilds just outside the outpost. They grow near the treeline."},

            # --- Night (before quest) ---
            {"required_time": ["night"],
             "text": "The office doesn't close, but I'm not taking assignments this late. Come back in the morning."},

            # --- Post-graduation fallback ---
            {"required_flag": "quest_a_guildsmans_first_steps_completed",
             "text": "You've graduated. What are you still doing here? Whisperwood is waiting."},

            # --- Initial grant ---
            {"action": "grant_quest", "quest_id": "a_guildsmans_first_steps",
             "text": "New recruit. Good timing. I'm going to walk you through the basics — not because they're optional, but because Guildsmen who skip them don't last. Start simple: explore the wilds outside the outpost and bring me a Sun-Kissed Berry."},

            # --- Default ---
            {"default": [
                "Welcome to the Guild Recruitment Hut. If you're looking for work, speak with me.",
                "The Guild operates on results. Talk to me when you have some.",
                "Every Guildsman starts somewhere. You're in the right place.",
            ]},
        ]
    },

    # -------------------------------------------------------------------------
    # BEA — Supply Merchant. Practical, sharp-tongued, fair. Been robbed once.
    # Won't let you forget it. Respects people who get things done quietly.
    # -------------------------------------------------------------------------
    "bea": {
        "name": "Bea", "role": "Supply Merchant",
        "dialogue_tree": [

            # --- Night ---
            {"required_time": ["night"],
             "text": [
                 "Chest is locked at night. Come back when the sun's up.",
                 "I don't do business after dark. Too many sticky fingers.",
             ]},

            # --- Post-graduation ---
            {"required_flag": "quest_a_guildsmans_first_steps_completed",
             "text": [
                 "Elara actually graduated you? Faster than most. Come back when your pack runs low — I'll be here.",
                 "A real Guildsman now. Don't let it go to your head. Supplies still cost coins.",
                 "Whisperwood, is it? Pack heavy. The forest doesn't care how tough you think you are.",
                 "You made it through the pits in one piece. That's more than I expected. Take care of yourself out there.",
             ]},

            # --- Morning (setting up) ---
            {"required_time": ["morning"],
             "text": [
                 "Just opening up. Don't crowd the chest — I haven't finished the inventory count.",
                 "Early riser. Good habit. Help yourself, just don't make a mess of the stock.",
             ]},

            # --- Default ---
            {"default": [
                "Looking or buying? Either way, touch the chest, not the stock. Everything's priced fair.",
                "I've been robbed before and I've got a long memory. Don't try anything clever.",
                "The chest is stocked fresh this morning. Take what you need, leave what you don't.",
                "Fair prices, good stock, no nonsense. That's how I run things.",
            ]},
        ]
    },

    # -------------------------------------------------------------------------
    # GRIT GALEN — Veteran scavenger. Knows the pits like the back of his hand.
    # Superstitious about the Gloom. Terse. Respects people who earn it.
    # -------------------------------------------------------------------------
    "grit_galen": {
        "name": "Grit Galen", "role": "Scavenger",
        "dialogue_tree": [

            # --- Quest completed ---
            {"required_flag": "quest_sunk_cost_completed",
             "text": [
                 "Those goggles treating you well? Good. Keep them polished — the lenses cloud up in the Gloom.",
                 "You know, I prospected these pits for six years before I quit. Some things down there still follow me in my sleep.",
                 "The Gloom takes things. Tools, time, people. You did good getting that satchel back.",
                 "Not many Guildsmen would bother with a scavenger's lost kit. I won't forget it.",
             ]},

            # --- Quest failed ---
            {"required_flag": "quest_sunk_cost_failed",
             "text": "Took too long. The tar swallowed it. Can't say I'm surprised — the pits don't wait."},

            # --- Has the satchel ---
            {"required_item": "old_satchel",
             "action": "complete_quest",
             "quest_id": "sunk_cost",
             "text": "By the Spirits... you found it. These goggles survived the tar — from my prospecting days. They've got a knack for spotting things that don't want to be found. They're yours, proper reward for proper work."},

            # --- Quest active, no satchel ---
            {"required_quest_status": {"quest_id": "sunk_cost", "status": "active"},
             "required_time": ["night"],
             "text": "You're still looking? At night? The pits are worse after dark. Be careful — the Gloom gets into your head if you're not paying attention."},

            {"required_quest_status": {"quest_id": "sunk_cost", "status": "active"},
             "text": [
                 "Still looking for my satchel? It's down there somewhere. Keep your eyes low — tar moves slow but it moves.",
                 "Any luck? The pits look calm but they're not. Watch the Gloom Meter if you're heading back in.",
             ]},

            # --- Tutorial step 7: offer the quest ---
            {"required_quest_step": {"quest_id": "a_guildsmans_first_steps", "step": 7},
             "action": "grant_quest", "quest_id": "sunk_cost",
             "text": "Fresh face. You look capable enough. Lost my satchel of tools in the pits earlier today — slipped off the ledge near the second tar pool. It's sinking. Tar gets deeper every season. Give it a day or two and it's gone for good. Find it and I'll make it worth your while."},

            # --- Night, no quest context ---
            {"required_time": ["night"],
             "text": [
                 "Night's the wrong time to be near the pits. The Gloom thickens after dark. Whatever you're looking for — come back tomorrow.",
                 "You can hear the pits shift at night. Most people call it settling. I've been here long enough to know better.",
             ]},

            # --- Default ---
            {"default": [
                "Don't get too close to the pits. The Gloom here makes everything twitchy — you and the creatures both.",
                "Six years I worked these pits. Still don't trust them. Keep your distance unless you know what you're doing.",
                "The tar's been rising. Slowly, but it's rising. Guild doesn't seem to care. I do.",
                "You've got that look — fresh from the outpost, full of confidence. Good. Keep it. Just don't let it make you careless near the pits.",
            ]},
        ]
    },
}
