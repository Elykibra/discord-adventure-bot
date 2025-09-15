# data/section_0/story.py

STORY = {
    "id": "section_0",
    "title": "Prologue: Oakhaven",
    "steps": [
        {
            "id": "intro_1",
            "type": "narration",
            "text": "You wake in Oakhaven’s guild hall to the distant roll of thunder...",
            "next": "name_prompt"
        },

        {
            "id": "name_prompt",
            "type": "modal",                       # <-- will open a modal
            "modal_title": "Choose your guild name",
            "modal_label": "Name",
            "modal_min": 2,
            "modal_max": 16,
            "effects": [{"op": "set_name_from_modal"}],   # engine will read modal value
            "next": "name_ack"
        },

        {
            "id": "name_ack",
            "type": "narration",
            "text": "Welcome, {player_name}.",
            "next": "choose_starter"
        },

        {
            "id": "choose_starter",
            "type": "choice",
            "prompt": "A companion approaches. Who will you bond with?",
            "options": [
                {"id": "pet_pyrelisk", "label": "Pyrelisk",
                 "effects": [
                     {"op": "grant_pet", "pet_id": "Pyrelisk"},
                     {"op": "set_main_pet_by_species", "pet_id": "Pyrelisk"},
                     {"op": "set_flag", "flag": "starter_pet:Pyrelisk"}
                 ],
                 "next": "choose_talent"},

                {"id": "pet_dewdrop", "label": "Dewdrop",
                 "effects": [
                     {"op": "grant_pet", "pet_id": "Dewdrop"},
                     {"op": "set_main_pet_by_species", "pet_id": "Dewdrop"},
                     {"op": "set_flag", "flag": "starter_pet:Dewdrop"}
                 ],
                 "next": "choose_talent"},

                {"id": "pet_terran", "label": "Terran",
                 "effects": [
                     {"op": "grant_pet", "pet_id": "Terran"},
                     {"op": "set_main_pet_by_species", "pet_id": "Terran"},
                     {"op": "set_flag", "flag": "starter_pet:Terran"}
                 ],
                 "next": "choose_talent"}
            ]
        },

        {
            "id": "choose_talent",
            "type": "dyn_choice",                  # <-- dynamic options (from data)
            "prompt": "Select a talent for your starter.",
            "dynamic_source": "starter_talents",   # we'll resolve from data
            "pet_flag_key": "starter_pet",
            "next": "intro_3"
        },

        {
            "id": "intro_3",
            "type": "narration",
            "text": "With your companion by your side, the guildmaster nods approvingly.\nYour journey begins.",
            "next": "hub_1"
        },

        # --- simple "town hub" loop for testing ---
        {
            "id": "hub_1",
            "type": "choice",
            "prompt": "You're in Oakhaven's guild hall. What do you do?",
            "options": [
                {"id": "hub_gm", "label": "Talk to the guildmaster", "next": "hub_gm_say"},
                {"id": "hub_market", "label": "Visit the market", "next": "hub_market_say"},
                {"id": "hub_training", "label": "Training yard", "next": "hub_training_say"},
                {"id": "hub_rest", "label": "Rest at the bunks (restore energy)", "next": "hub_rest_say"},

                # Put effects here (on the option), not on the next narration.
                {"id": "hub_end", "label": "Call it a day (end demo)",
                 "effects": [
                     {"op": "set_flag", "flag": "finished_tutorial"},
                     {"op": "goto", "section": "section_1", "step": "intro_1"}
                 ],
                 "next": "hub_end_say"}
            ]
        },
        {
            "id": "hub_gm_say",
            "type": "narration",
            "text": "The guildmaster reviews a stack of requests. \"Come back tomorrow—more work will be posted.\"",
            "next": "hub_1"
        },
        {
            "id": "hub_market_say",
            "type": "narration",
            "text": "Vendors haggle, blades glitter, and a baker hands you a sample roll. Tastes like hope.",
            "next": "hub_1"
        },
        {
            "id": "hub_training_say",
            "type": "narration",
            "text": "You stretch and run drills with your companion. Spirits high; muscles burning—good burn.",
            "effects": [{"op": "spend_energy", "amount": 1}],
            "next": "hub_1"
        },
        {
            "id": "hub_rest_say",
            "type": "narration",
            "effects": [ { "op": "restore_energy_full" } ],
            "text": "You take a proper rest. Your energy is fully restored.",
            "next": "hub_1"
        },
        {
            "id": "hub_end_say",
            "type": "narration",
            "text": "You call it a day. Thanks for testing this early build!"
            # no next — ends demo cleanly
        }
    ]
}
