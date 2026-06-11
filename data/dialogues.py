# data/dialogues.py
# NPC dialogue trees. Conditions are checked top-to-bottom; first match wins.
#
# Supported condition keys:
#   required_flag        — player must have this flag set
#   required_item        — player must have this item in inventory
#   required_quest_status — {"quest_id": "x", "status": "active"|"completed"|"failed"}
#   required_quest_step  — {"quest_id": "x", "step": N}  (matches when count == N)
#   required_time        — list of valid phases: ["morning","noon","evening","night"]
#   required_rank        — minimum player rank by CREST_RANKS order (e.g. "Veteran")
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

            # --- Quest completed, Veteran rank or above ---
            {"required_flag": "quest_sunk_cost_completed",
             "required_rank": "Veteran",
             "text": "You made it this far. Good. Come back when you've seen the Chasm. Tell me if what's down there looks anything like what's in the Pits."},

            # --- Quest completed ---
            {"required_flag": "quest_sunk_cost_completed",
             "text": [
                 "Those goggles treating you well? Good. Keep them polished — the lenses cloud up in the Gloom.",
                 "You know, I prospected these pits for six years before I quit. Some things down there still follow me in my sleep.",
                 "The Gloom takes things. Tools, time, people. You did good getting that satchel back.",
                 "Not many Guildsmen would bother with a scavenger's lost kit. I won't forget it.",
                 "The far edge moved another foot this week. Don't put that in any report.",
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

            # --- Guild training complete — handoff toward Weeping Chasm ---
            # Flavor-only nudge toward the next leg of the journey (echoes_from_below).
            # Doesn't gate or grant anything — just points the player at Kael.
            {"required_flag": "quest_a_guildsmans_first_steps_completed",
             "text": (
                 "The road to Whisperwood runs through the Weeping Chasm first. Guild keeps "
                 "a scholar out there — Kael. Good man, bit obsessive. He's been cataloguing "
                 "things out there for years. If the Pits and the Chasm really do share a "
                 "source like I think... he's the one who'd want to know what you've seen here."
             )},

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

    # -------------------------------------------------------------------------
    # KAELEN — Hearth-Steward of The Ashen Verge. Soot-stained, terse, dutiful.
    # Tends a containment ring of fire he doesn't fully understand the
    # purpose of, out of inherited obligation. Hands out a repeatable
    # Serpentine-culling bounty to keep the boundary clear.
    # -------------------------------------------------------------------------
    "kaelen": {
        "name": "Kaelen", "role": "Hearth-Steward",
        "dialogue_tree": [

            # --- Bounty completed ---
            {"required_flag": "quest_kaelens_bounty_completed",
             "text": [
                 "Fewer vines on the line today. I noticed. Thank you for that.",
                 "The ash has been quiet since you cleared those Serpentine out. It won't last — it never does — but thank you.",
                 "Soot's been less jumpy lately. He notices when the line's been cleared, same as I do.",
             ]},

            # --- Bounty active ---
            {"required_quest_status": {"quest_id": "kaelens_bounty", "status": "active"},
             "text": "Serpentine's been working its way toward the line again. Vines don't respect boundaries — never have. Clear a few out, would you? Keeps the ash where it belongs."},

            # --- Initial grant ---
            {"action": "grant_quest", "quest_id": "kaelens_bounty",
             "text": "My grandmother's grandmother lit the first ring. Said fire was the only thing the roots couldn't pretend to be. We've kept it lit ever since — but the vines keep testing the line. If you're heading into the Verge, clear a few Serpentine out for me. Keeps the ash where it belongs."},

            # --- Default ---
            {"default": [
                "Out past the deeper ash — the old folk called it the First Ring — something's buried. Two somethings, actually. I don't go that far in. Don't need to.",
                "The circle needs to stay clean. I don't fully understand why it works. Just that it does.",
                "Soot was just a kit when I found him, near frozen at the edge of the ring. Same as the wild ones out there, more or less. He just happens to be mine.",
                "Don't get many visitors out here. Most people see the ash and turn back before they even reach the shack.",
            ]},
        ]
    },

    # -------------------------------------------------------------------------
    # WARDEN ORIN — Guild Warden, Weeping Chasm. Manned during daylight hours.
    # Terse, observational. Reports what he sees without elaborating on it.
    # -------------------------------------------------------------------------
    "warden_orin": {
        "name": "Warden Orin", "role": "Guild Warden",
        "dialogue_tree": [

            # --- echoes_from_below completed ---
            {"required_flag": "quest_echoes_from_below_completed",
             "text": [
                 "Kael still out there scribbling? Of course he is. Man doesn't know when to stop.",
                 "You gave Kael what he needed, I take it. Good. Maybe he'll sleep for once.",
                 "The records say the Gloom first surfaced here. I believe it. Some nights I can feel it thinking.",
             ]},

            # --- echoes_from_below active ---
            {"required_quest_status": {"quest_id": "echoes_from_below", "status": "active"},
             "text": [
                 "This is as close as most people get. The Chasm draws Gloom-Touched creatures — they're drawn to the source. I keep watch so travelers can pass safely. Mostly.",
                 "The east section of the wall is webbed over some mornings. Something large made that overnight. He doesn't elaborate. \"I don't go near it.\"",
                 "Some mornings the mist is different. Heavier. Like something exhaled the whole of it at once. He says it the way you'd report weather.",
                 "See that marker post? Cracked rune, tally marks scratched into the wood. Thirty-seven, last I counted. I didn't start that count. I just keep adding to it.",
             ]},

            # --- Default ---
            {"default": "Road's passable. Mostly. Don't linger at the edge — the creatures here are drawn to the source and they don't watch where they're going."},
        ]
    },

    # -------------------------------------------------------------------------
    # LORE-KEEPER KAEL — Guild Scholar, Weeping Chasm. Obsessive, talks fast,
    # already mid-thought when you arrive. Studies the Chasm as the Gloom's
    # origin point. Quest giver/resolver for echoes_from_below.
    # -------------------------------------------------------------------------
    "lore_keeper_kael": {
        "name": "Lore-Keeper Kael", "role": "Guild Scholar",
        "dialogue_tree": [

            # --- echoes_from_below completed — forward hook + lore in rotation ---
            {"required_flag": "quest_echoes_from_below_completed",
             "text": [
                 "The density readings from your samples were unlike anything recorded further out. When you reach the Sunstone Oasis, find the Obsidian Monoliths. I'll be there. There's something I need to show you.",
                 "Three samples told me more than three years of notes. Thank you for that — truly.",
                 "It isn't shrinking. It's widening. I wish I had better news than that.",
                 "Threnody's been restless since you brought those samples in. I don't think that's a coincidence.",
             ]},

            # --- Samples collected — turn-in ---
            {"required_quest_step": {"quest_id": "echoes_from_below", "step": 1},
             "text": (
                 "These are clean samples — remarkable. The density here is unlike anything "
                 "recorded further out. The Gloom didn't spread from a single point by accident. "
                 "Every record points here — the Chasm — as the breach site. My theory: collective "
                 "grief. A catastrophic loss, enough souls in enough pain at once to tear something "
                 "open. The Guild doesn't like that theory. Too difficult to quantify. "
                 "It isn't shrinking, by the way. It's widening. Thank you for this — truly."
             )},

            # --- Quest active, still collecting samples ---
            {"required_quest_status": {"quest_id": "echoes_from_below", "status": "active"},
             "text": [
                 "You're here — good. I've been waiting for someone Vexia would actually trust with this. The origin point is right here and nobody bothers to study it properly. I need samples — three vials of gloom-mist from the Edge. Can you do that?",
                 "Corrupted creatures can still be reached — the Gloom has touched them but hasn't consumed them. There's still something there to work with. Hollowed is different. When a creature Hollows, there's nothing left that remembers being a creature. That distinction matters. Remember it.",
                 "Threnody — my Duskspinner. Named for a funeral song, after the Gloom's origin in collective sorrow. Yes, I know how that sounds. Ask me again sometime and I'll explain the etymology properly.",
                 "He shows you a single research note: 'Specimen of unusual scale observed on east face. Preliminary classification impossible.' One entry. The next page is blank.",
             ]},

            # --- Default ---
            {"default": "You found me. Good — I wasn't sure Vexia would send anyone capable."},
        ]
    },

    # -------------------------------------------------------------------------
    # "GRIM" GRETTA — Chasm Watcher, Lookout Hollow. Blunt, weathered, doesn't
    # waste words. Keeps a half-bonded Threshling. Subdue-path perspective.
    # -------------------------------------------------------------------------
    "grim_gretta": {
        "name": "\"Grim\" Gretta", "role": "Chasm Watcher",
        "dialogue_tree": [

            # --- echoes_from_below completed, Veteran rank or above ---
            {"required_flag": "quest_echoes_from_below_completed",
             "required_rank": "Veteran",
             "text": "She looks you over once. Looks back at the fire. \"Still here.\" That's all she gives you. From Gretta, it means something."},

            # --- echoes_from_below completed ---
            {"required_flag": "quest_echoes_from_below_completed",
             "text": [
                 "Kael got his samples, then. Good. Maybe he'll stop wandering toward the edge at night.",
                 "\"The breathing. You've heard it.\" Not a question. \"Don't go looking for what makes it.\"",
                 "That creature following you — you trust it? The Gloom finds the ones you're attached to first. Keep it strong. Soft bonds don't survive this road.",
             ]},

            # --- echoes_from_below active ---
            {"required_quest_status": {"quest_id": "echoes_from_below", "status": "active"},
             "text": [
                 "Guild sends another one. They always look the same — hopeful. The Chasm fixes that eventually. What do you want?",
                 "\"Nothing worth finding out there.\"",
                 "You want to know what I know? Fine. The Guild tells you to heal corrupted creatures. I've watched that fail more times than you've been alive. Control is not cruelty. It's honesty. There's another way — if you're willing to hear it.",
             ]},

            # --- Default ---
            {"default": "Guild sends another one. They always look the same."},
        ]
    },
}
