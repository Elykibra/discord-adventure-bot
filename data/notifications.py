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

    # Battle Related Notifications
    "BATTLE_REWARD_COINS": [
        "💰 You earned {amount} Coins.",
        "🪙 A prize of {amount} Coins for your victory!",
    ],
    "BATTLE_PET_LEVEL_UP": [
        "🌟 Your {pet_name} grew to Level {new_level}!",
        "🎉 A surge of power! {pet_name} is now Level {new_level}!",
    ],
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
}