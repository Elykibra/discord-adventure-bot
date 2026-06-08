# data/section_0/story.py

STORY = {
    "id": "section_0",
    "title": "Prologue: Oakhaven",
    "steps": [

        # ── INTRO ──────────────────────────────────────────────────────────
        {
            "id": "intro_1",
            "type": "narration",
            "text": (
                "The smell of pine and damp earth fills your lungs as you stir awake.\n\n"
                "You're lying on a straw cot inside **Oakhaven Outpost** — "
                "a modest cluster of log cabins huddled beneath an ancient oak at the edge of "
                "the known world. Rain drums steadily on the roof. Through a cracked shutter, "
                "you catch a distant rumble of thunder rolling across the wilds.\n\n"
                "On the floor beside you: a worn satchel, a Guild recruitment notice, "
                "and a creature curled asleep against your boot — your companion, who followed "
                "you here from the last town you barely escaped.\n\n"
                "*The notice reads:*\n"
                "```\n"
                "By order of the Adventurers' Guild — Oakhaven Branch\n"
                "All new recruits are to report to Officer Elara\n"
                "upon arrival. Do not wander the wilds unregistered.\n"
                "The Gloom does not discriminate.\n"
                "```"
            ),
            "next": "intro_2"
        },

        {
            "id": "intro_2",
            "type": "narration",
            "text": (
                "You sit up, rubbing sleep from your eyes.\n\n"
                "You came here because the Guild promised work, coin, and purpose. "
                "Because the cities back home grew too loud, too hungry, or too dangerous. "
                "Because something out in the wilds keeps calling — "
                "a pull you can't explain and can't ignore.\n\n"
                "Your companion stirs, blinking up at you with quiet trust.\n\n"
                "Whatever waits beyond that door — you won't face it alone.\n\n"
                "*First things first: what do they call you?*"
            ),
            "next": "name_prompt"
        },

        # ── NAME INPUT ─────────────────────────────────────────────────────
        {
            "id": "name_prompt",
            "type": "modal",
            "modal_title": "What is your name, recruit?",
            "modal_label": "Your name",
            "modal_min": 2,
            "modal_max": 16,
            "effects": [{"op": "set_name_from_modal"}],
            "next": "name_ack"
        },

        {
            "id": "name_ack",
            "type": "narration",
            "text": (
                "**{player_name}.**\n\n"
                "The name settles in the air like it belongs here.\n\n"
                "You pull on your boots, grab your satchel, and push open the cabin door. "
                "Cold morning air rushes in. The outpost is already stirring — "
                "a blacksmith hammering, a merchant arguing over crate weights, "
                "and somewhere nearby, the low growl of a wild creature testing its cage.\n\n"
                "Officer Elara's recruitment hut sits just across the mud path. "
                "A hand-painted sign above the door reads: *\"All new arrivals — knock first.\"*\n\n"
                "But before you register... your companion nudges your hand. "
                "You've been travelling together, but you've never formally bonded. "
                "Not the way Guild adventurers do.\n\n"
                "*It's time to choose your path.*"
            ),
            "next": "choose_starter"
        },

        # ── STARTER CHOICE ─────────────────────────────────────────────────
        {
            "id": "choose_starter",
            "type": "choice",
            "prompt": (
                "Three spirits linger near the outpost's ancient oak — drawn to new arrivals, "
                "the old-timers say. Each one waits to see if *you* are the one they've chosen.\n\n"
                "🔥 **Pyrelisk** — *Fire-type.* Aggressive and fierce. It burns hot and fast, "
                "loyal to those who match its intensity.\n\n"
                "💧 **Dewdrop** — *Water-type.* Calm and resilient. It endures, adapts, "
                "and outlasts anything thrown at it.\n\n"
                "🪨 **Terran** — *Earth-type.* Stubborn and steadfast. Slow to trust, "
                "but immovable once it does.\n\n"
                "*Which spirit feels like yours?*"
            ),
            "options": [
                {
                    "id": "pet_pyrelisk",
                    "label": "🔥 Pyrelisk",
                    "effects": [
                        {"op": "grant_pet",              "pet_id": "Pyrelisk"},
                        {"op": "set_main_pet_by_species","pet_id": "Pyrelisk"},
                        {"op": "set_flag",               "flag":   "starter_pet:Pyrelisk"}
                    ],
                    "next": "starter_ack_pyrelisk"
                },
                {
                    "id": "pet_dewdrop",
                    "label": "💧 Dewdrop",
                    "effects": [
                        {"op": "grant_pet",              "pet_id": "Dewdrop"},
                        {"op": "set_main_pet_by_species","pet_id": "Dewdrop"},
                        {"op": "set_flag",               "flag":   "starter_pet:Dewdrop"}
                    ],
                    "next": "starter_ack_dewdrop"
                },
                {
                    "id": "pet_terran",
                    "label": "🪨 Terran",
                    "effects": [
                        {"op": "grant_pet",              "pet_id": "Terran"},
                        {"op": "set_main_pet_by_species","pet_id": "Terran"},
                        {"op": "set_flag",               "flag":   "starter_pet:Terran"}
                    ],
                    "next": "starter_ack_terran"
                }
            ]
        },

        # ── STARTER ACKNOWLEDGEMENTS ───────────────────────────────────────
        {
            "id": "starter_ack_pyrelisk",
            "type": "narration",
            "text": (
                "The Pyrelisk holds your gaze for a long moment — then steps forward.\n\n"
                "A warmth radiates from it, not just heat but something older. "
                "The air around you smells faintly of smoke and iron. "
                "It presses its snout against your palm.\n\n"
                "*Bond forged.*\n\n"
                "The other two spirits drift back into the wilds without a sound."
            ),
            "next": "choose_talent"
        },
        {
            "id": "starter_ack_dewdrop",
            "type": "narration",
            "text": (
                "The Dewdrop glides toward you, water trailing behind it like a slow tide.\n\n"
                "It doesn't rush. It simply arrives — certain, unhurried. "
                "A coolness settles over you, calm and absolute. "
                "It wraps a tendril of water gently around your wrist.\n\n"
                "*Bond forged.*\n\n"
                "The other two spirits drift back into the wilds without a sound."
            ),
            "next": "choose_talent"
        },
        {
            "id": "starter_ack_terran",
            "type": "narration",
            "text": (
                "The Terran doesn't move at first. It watches you — testing.\n\n"
                "Then, slowly, it crosses the distance. The ground hums faintly under each step. "
                "It lowers its heavy head and presses it against your chest. "
                "You feel the weight of it. The solidity.\n\n"
                "*Bond forged.*\n\n"
                "The other two spirits drift back into the wilds without a sound."
            ),
            "next": "choose_talent"
        },

        # ── TALENT CHOICE ──────────────────────────────────────────────────
        {
            "id": "choose_talent",
            "type": "dyn_choice",
            "prompt": (
                "Your companion tilts its head, sensing something shift between you.\n\n"
                "Every bond has a nature. The way two people fight together, "
                "endure together, survive together — it takes a shape.\n\n"
                "*What defines how you and your companion face the world?*"
            ),
            "dynamic_source": "starter_talents",
            "pet_flag_key": "starter_pet",
            "next": "talent_ack"
        },

        {
            "id": "talent_ack",
            "type": "narration",
            "text": (
                "Something settles — a quiet click, like a lock finding its key.\n\n"
                "Your companion exhales slowly. You feel it too."
            ),
            "next": "intro_to_hub"
        },

        # ── TRANSITION TO TOWN ────────────────────────────────────────────
        {
            "id": "intro_to_hub",
            "type": "narration",
            "text": (
                "The outpost stretches before you, modest but alive.\n\n"
                "Elara's recruitment hut. The supply chest by the east wall. "
                "The scent of something cooking from the bunkhouse. "
                "And beyond the treeline — the wilds, dark and restless.\n\n"
                "You are **{player_name}**, recruit of the Adventurers' Guild, "
                "Oakhaven Branch. You have a companion, a name, and nowhere else to be.\n\n"
                "*The rest is yours to write.*"
            ),
            "next": "hub_1"
        },

        # ── TOWN HUB LOOP ─────────────────────────────────────────────────
        {
            "id": "hub_1",
            "type": "choice",
            "prompt": (
                "**Oakhaven Outpost** — *Morning*\n\n"
                "The ancient oak stands at the centre of everything here, "
                "its bark carved with the marks of every adventurer who ever sheltered beneath it. "
                "Rain has eased to a drizzle.\n\n"
                "What do you do?"
            ),
            "options": [
                {"id": "hub_elara",    "label": "🛡️ Report to Officer Elara",         "next": "hub_elara_say"},
                {"id": "hub_market",   "label": "📦 Check the supply chest",           "next": "hub_market_say"},
                {"id": "hub_training", "label": "⚔️ Warm up in the training yard",     "next": "hub_training_say"},
                {"id": "hub_rest",     "label": "🌙 Rest at the bunks",                "next": "hub_rest_say"},
                {"id": "hub_end",      "label": "🚪 Head out (end prologue)",
                 "effects": [
                     {"op": "set_flag", "flag": "finished_tutorial"}
                 ],
                 "next": "hub_end_say"}
            ]
        },

        {
            "id": "hub_elara_say",
            "type": "narration",
            "text": (
                "Elara barely looks up from her ledger as you knock.\n\n"
                "*\"Name, companion species, and previous Guild affiliation — if any.\"*\n\n"
                "She writes quickly, stamps a form, and slides it across the desk without ceremony.\n\n"
                "*\"You're registered. Don't die. That's all.\"*\n\n"
                "She's already onto the next form. You get the sense she's said this a hundred times."
            ),
            "next": "hub_1"
        },
        {
            "id": "hub_market_say",
            "type": "narration",
            "text": (
                "The supply chest sits beside the east wall, lid propped open. "
                "A hand-written price list is nailed to the wall above it.\n\n"
                "Potions, rope, ration packs, a few items you don't recognise. "
                "The merchant — a compact woman named Bea — "
                "watches you with the eyes of someone who has been robbed before.\n\n"
                "*\"Looking or buying?\"*\n\n"
                "You're looking. For now."
            ),
            "next": "hub_1"
        },
        {
            "id": "hub_training_say",
            "type": "narration",
            "text": (
                "The training yard is a muddy patch of ground behind the main hall, "
                "equipped with a battered scarecrow, some rope targets, and a sign "
                "that reads *\"HIT IT UNTIL IT FEELS REAL.\"*\n\n"
                "You run through some basic forms with your companion. "
                "It mirrors your movements, testing its range, learning your timing.\n\n"
                "By the end, you're both breathing hard — and a little more ready."
            ),
            "effects": [{"op": "spend_energy", "amount": 1}],
            "next": "hub_1"
        },
        {
            "id": "hub_rest_say",
            "type": "narration",
            "effects": [{"op": "restore_energy_full"}],
            "text": (
                "The bunkhouse is quiet this time of morning. "
                "You take the cot nearest the wall, your companion curling up at your feet.\n\n"
                "Sleep comes fast. Deep. The kind you've been needing.\n\n"
                "*You wake restored, the drizzle finally gone.*"
            ),
            "next": "hub_1"
        },
        {
            "id": "hub_end_say",
            "type": "narration",
            "text": (
                "You tighten the straps on your satchel and step outside.\n\n"
                "The ancient oak watches you go, silent and knowing. "
                "Ahead, the wilds stretch on — dark beneath the canopy, "
                "humming with something you can't name.\n\n"
                "Your companion falls into step beside you.\n\n"
                "**The prologue is complete.**\n"
                "*Use* `/adventure` *to explore Oakhaven, enter the wilds, and begin your story.*"
            )
            # no next — ends the prologue cleanly
        }
    ]
}
