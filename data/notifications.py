# data/notifications.py
# This file contains all templates for dynamic log messages.

NOTIFICATIONS = {
    # Player Notifications
    "ACTION_FAIL_NO_ENERGY": [
        "⚡ You don't have enough energy to do that. You need at least {cost} energy.",
        "🔋 Your energy is too low. This action requires {cost} energy.",
        "😴 You're too tired to continue. You need {cost} energy to perform this action.",
    ],
    "ACTION_FAIL_PLAYER_MAX_ENERGY": [
        "⚡ [!] You already have full energy!",
        "🔋 [!] Your energy is already at its maximum.",
    ],
    "EXPLORE_FIND_ITEM": [
        "🌲 You searched the area and found {quantity}x {item_name}!",
        "✨ Your keen eyes spotted {quantity}x {item_name} nestled nearby.",
        "😮 What's this? You stumbled upon {quantity}x {item_name}!",
    ],
    "EXPLORE_FIND_NOTHING": [
        "💨 You searched the area but found nothing of interest.",
        "🔎 A thorough search reveals nothing but common rocks and leaves.",
        "🤷‍♂️ No luck this time. The wilds remain quiet.",
    ],
    "ACTION_FAIL_NO_COINS": [
        "💰 You don't have enough coins. This action costs {cost} Coins.",
    ],
    "ACTION_SUCCESS_PAY_COINS": [
        "💰 You paid {cost} Coins.",
        "🪙 {cost} Coins have been deducted from your wallet.",
    ],
    "ACTION_FAIL_INVALID_QUANTITY": [
        "🤔 That's not a valid amount. Please enter a number between 1 and {max_quantity}.",
        "⚠️ You can't use that many. You only have {max_quantity}!",
    ],
    # --- Player Buff Notifications ---
    "PLAYER_BUFF_WELL_RESTED": [
        "✨ Your sharp senses from being well-rested make you feel lucky!",
        "⚡ Feeling energetic, you notice details you might have otherwise missed.",
        "🔋 With energy to spare, your perception is heightened."
    ],

    # Battle Related Notifications
    "FLEE_SUCCESS": [
        "🏃‍♂️ You and your pet made a hasty retreat!",
        "💨 You got away safely!",
        "😮 That was a close one! You successfully escaped.",
    ],
    "FLEE_FAILURE": [
        "❌ You couldn't get away!",
        "🚫 The wild {wild_pet_species} blocked your escape!",
        "⚠️ Your attempt to flee failed!",
    ],
    "BATTLE_DEFEAT": [
        "💔 You were defeated and scurried back to safety.",
        "☠️ Overwhelmed by the wild pet, you made a hasty retreat.",
        "🏳️ You were outmatched and forced to flee the battle."
    ],

    # --- Battle Reward Notifications ---
    "BATTLE_REWARD_BASE": [
        "🏆 You defeated the wild {wild_pet_species}! You earned {coin_gain} coins and {xp_gain} EXP.",
        "🎉 Victory! You received {coin_gain} coins and {xp_gain} EXP for defeating the {wild_pet_species}.",
        "⚔️ The wild {wild_pet_species} was defeated! You gained {coin_gain} coins and {xp_gain} EXP."
    ],
    "BATTLE_REWARD_SATIATED_BONUS": [
        "> Satiated Bonus! Your pet earned an extra **{bonus_xp} EXP** for being well-fed.",
        "> Your well-fed pet feels invigorated, earning a bonus of **{bonus_xp} EXP**!",
        "> Thanks to your excellent care, your pet gets a Satiated Bonus of **{bonus_xp} EXP**."
    ],
    "BATTLE_REWARD_LEVEL_UP": [
        "🌟 Your pet {pet_name} grew to Level {new_level}!",
        "✨ A surge of power! {pet_name} is now Level {new_level}!",
        "🔥 {pet_name} has reached Level {new_level}!"
    ],

    # Quest Updates
    "QUEST_COMPLETE": [
        "🎉 Quest Complete: {quest_title}!",
        "📜 The final objective is complete. You finished {quest_title}!",
    ],
    "QUEST_FAIL_TIME": [
        "⏰ You took too long... {failure_message}",
    ],

    # World Notifications
    "TIME_ADVANCE_NIGHT": [
        "🌙 The sun sets. It is now Night.",
    ],
    "TIME_ADVANCE_DAY": [
        "☀️ A new day dawns. It is now Day.",
    ],
    "PLAYER_RESTORE_ENERGY": [
        "⚡️ You feel rested. Your energy is now {new_energy}/{max_energy}.",
    ],
    "PET_RESTORE_HP": [
        "❤️ Your pet, {pet_name}, has {new_hp}/{max_hp} HP.",
    ],

    # Inventory Related
    "ITEM_EQUIP_SUCCESS": [
        "🛡️ You equipped {item_name}.",
        "✨ {item_name} is now in use!",
    ],
    "ITEM_UNEQUIP_SUCCESS": [
        "❌ You unequipped {item_name}.",
        "🪄 You put away {item_name}.",
    ],
    "ITEM_USE_SUCCESS": [
        "🍎 You used {quantity}x {item_name}.",
        "✨ {item_name} has been used ({quantity}).",
    ],
    "ITEM_DROP_SUCCESS": [
        "🗑️ You dropped {quantity}x {item_name}.",
        "🚮 {quantity}x {item_name} removed from your bag.",
    ],

    # NPC Dialogue
    "NPC_DIALOGUE": [
        "💬 {npc_name}: \"{dialogue}\"",
    ],

    #pet related notifications
    "ITEM_HEAL_PET_SUCCESS": [
        "❤️‍🩹 The item restored {heal_amount} HP to {pet_name}.",
        "✨ {pet_name} looks much better! Healed for {heal_amount} HP.",
        "💖 A soothing energy mends {pet_name}'s wounds. (+{heal_amount} HP)",
    ],
    "ACTION_FAIL_PET_MAX_HP": [
        "❤️ [!] {pet_name} is already at full health!",
        "🩹 [!] No healing needed — {pet_name} has max HP.",
    ],
    "PET_EQUIP_SUCCESS": [
        "🛡️ You equipped the {item_name} on {pet_name}.",
        "✨ {pet_name} is now holding the {item_name}!",
        "✅ The {item_name} has been given to {pet_name} to hold."
    ],
    "ACTION_FAIL_GENERIC": [
        "❌ That action could not be completed.",
        "⚠️ An unexpected error occurred. Please try again.",
        "❗ Something went wrong."
    ],

    # --- Crafting Process Notifications ---

    "CRAFT_SUCCESS": [
        "🎉 You successfully crafted {quantity}x {item_name}!",
        "✅ Success! {quantity}x {item_name} has been added to your inventory.",
        "✨ With a final touch, you complete your work. You've made {quantity}x {item_name}!"
    ],

    #Trail Morsels Recipe
    "CRAFT_GRIND_DRY": [
        "You crush the dry ingredients into a rough paste...",
        "Grinding the components together, you form a thick slurry...",
        "You carefully mill the materials into a fine powder..."
    ],
    "CRAFT_FORM_PASTE": [
        "After drying, the paste forms into simple, effective morsels.",
        "You shape the mixture into small, travel-ready cakes.",
        "The resulting paste is rolled into bite-sized pieces."
    ],

    #Hearty Stew Recipe
    "CRAFT_SIMMER_INGREDIENTS": [
        "The Chef simmers the ingredients in a large cauldron...",
        "The ingredients are added to a bubbling pot...",
        "You watch as the mixture slowly cooks over a low flame..."
    ],
    "CRAFT_STEW_AROMA": [
        "The rich aroma of a well-made stew fills the air.",
        "A delicious and savory smell begins to rise from the pot.",
        "The scent of a hearty meal is unmistakable."
    ],


    # --- Combat Log Notifications ---

    "COMBAT_SENTENCE_TEMPLATES": [
        "› {attacker_name} {verb_phrase} with **{skill_name}**{impact_phrase}",
        "› {attacker_name} uses **{skill_name}** and {verb_phrase}{impact_phrase}",
        "› With **{skill_name}**, {attacker_name} {verb_phrase}{impact_phrase}",
        "› {attacker_name} calls upon **{skill_name}** to {verb_phrase}{impact_phrase}"
    ],
    "COMBAT_STATUS_TEMPLATES": [
        "› {attacker_name} uses **{skill_name}**.",
        "› {attacker_name} calls upon the power of **{skill_name}**!",
        "› Concentrating, {attacker_name} activates **{skill_name}**."
    ],

    "COMBAT_ACTION_VERBS": {
        # Verb-specific groups (new system)
        "impact": [
            "slams into {defender_name}", "crashes against {defender_name}", "rams {defender_name} with force"
        ],
        "slash": [
            "slashes at {defender_name}", "rakes its claws across {defender_name}", "scratches {defender_name}"
        ],
        "bite": [
            "chomps down on {defender_name}", "bites fiercely into {defender_name}",
            "sinks its fangs into {defender_name}"
        ],
        "pierce": [
            "stabs toward {defender_name}", "pierces {defender_name}", "jabs at {defender_name}"
        ],
        "beam": [
            "fires a beam of energy at {defender_name}", "blasts {defender_name} with focused light",
            "emits a piercing ray toward {defender_name}"
        ],
        "blast": [
            "unleashes an explosive force at {defender_name}", "erupts with power toward {defender_name}",
            "detonates energy near {defender_name}"
        ],
        "wave": [
            "releases a wave of force at {defender_name}", "sends a surge crashing toward {defender_name}",
            "unleashes rippling energy at {defender_name}"
        ],

        "strike": [
            "lightly strikes {defender_name}", "whips at {defender_name}",
            "makes contact with {defender_name}"
        ],
        "rush": [
            "rushes toward {defender_name}", "closes the distance and strikes {defender_name}",
            "moves in a blur, attacking {defender_name}"
        ],
        "projectile": [
            "hurls a projectile at {defender_name}", "launches an object toward {defender_name}",
            "sends a volley at {defender_name}"
        ],
        "gaze": [
            "gazes intently at {defender_name}", "fixes its stare on {defender_name}",
            "locks eyes with {defender_name}"
        ],
        "drain": [
            "drains energy from {defender_name}", "siphons vitality from {defender_name}"
        ],
        # for defensive skills like Spiteful Bastion and Balancing Ward.
        "stance": [

        ],
        # for dark/debuff-like moves such as Accelerated Decay.
        "curse": [

        ],
        # for Grasping Briar (grappling/root-style moves).
        "bind": [

        ],
        #for electric/paralysis moves like Short Circuit.
        "shock": [

        ],
        # (for evasive/ghostlike effects like Umbral Shift)
        "phase": [

        ],
        # (for “power-up” transformations like Draconic Ascendance)
        "ascend": [

        ],
        # (for poison/acid-themed moves like Caustic Venom)
        "corrode": [

        ],
        # (for mystical/fate/reflect-style moves like Karma Weave)
        "weave": [

        ],
        # (anti-magic/negation skills like Null Field)
        "nullify": [

        ],
        # (self-costing moves like Sacrificial Pact)
        "sacrifice": [

        ],
        # (holy/healing moves like Divine Benediction)
        "bless": [

        ],
        # (storm/catastrophic moves like Cataclysmic Storm)
        "tempest": [

        ],
        # (soul/ghost dismemberment attacks like Soulrend)
        "rend": [

        ],

        # Self-targeted actions
        "Self": [
            "focuses inward", "gathers strength", "fortifies itself", "restores its energy", "centers its power"
        ],

        # Elemental overrides (stay!)
        "Fire": [
            "engulfs {defender_name} in flames", "hurls a fireball at {defender_name}",
            "scorches {defender_name} with searing heat"
        ],
        "Water": [
            "blasts {defender_name} with a torrent of water", "drenches {defender_name}",
            "soaks {defender_name} with a powerful spray"
        ],
        "Ground": [
            "smashes into {defender_name} with earthy force", "causes the ground to erupt under {defender_name}",
            "hurls rocks toward {defender_name}"
        ],
        "Fairy": [
            "bathes {defender_name} in radiant light", "engulfs {defender_name} with dazzling brilliance",
            "shines a blinding aura at {defender_name}"
        ],
        "Rock": [
            "pelts {defender_name} with stones", "hurls a massive rock at {defender_name}",
            "crashes debris down onto {defender_name}"
        ],
        "Grass": [
            "lashes at {defender_name} with vines", "whips leaves toward {defender_name}",
            "slashes {defender_name} with sharp foliage"
        ],

        # Fallbacks (kept for safety)
        "Physical": [
            "attacks {defender_name}", "lashes out at {defender_name}"
        ],
        "Special": [
            "unleashes a blast of energy at {defender_name}", "focuses its power on {defender_name}"
        ],
        "Miss": [
            "misses its attack on {defender_name}", "fails to connect with {defender_name}",
            "whiffs its strike against {defender_name}"
        ]
    },

    "COMBAT_IMPACT_PHRASES": [
        ", dealing **{damage}** damage!",
        ", hitting for **{damage}** damage!",
        " for a solid **{damage}** damage!"
    ],
    "COMBAT_CRITICAL_HIT": [
        "💥 **A Critical Hit!** {attacker_name}'s {skill_name} strikes a weak point for **{damage}** damage!"
    ],
    "COMBAT_SUPER_EFFECTIVE": [
        " (Super Effective!)",
        " (A direct hit!)",
        " (It struck a weak point!)"
    ],
    "COMBAT_NOT_VERY_EFFECTIVE": [
        " (Not Very Effective...)",
        " (The blow was softened...)",
        " (It was partially blocked...)"
    ],
    "COMBAT_NO_EFFECT": [
        "❌ It has no effect..."
    ],

    # --- NEW: Gloom Notifications ---
    "COMBAT_GLOOM_INCREASE": [
        "> A wave of corruption washes over the battlefield! (Gloom +{amount}%)",
        "> The wild pet exudes a corrupting aura! (Gloom +{amount}%)",
        "> The Gloom on the battlefield intensifies! (Gloom +{amount}%)"
    ],
    "COMBAT_GLOOM_DECREASE": [
        "> Your pet's willpower pushes back the Gloom! (Gloom -{amount}%)",
        "> A surge of determination from your pet weakens the Gloom! (Gloom -{amount}%)",
        "> Your pet's spirit shines, repelling the corruption! (Gloom -{amount}%)"
    ],
}