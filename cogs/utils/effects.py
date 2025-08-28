# cogs/utils/effects.py
# This is the central "Effect Engine" for handling all skill and passive effects.
import random
from data.pets import PET_DATABASE
from data.skills import PET_SKILLS

# =================================================================================
#  EFFECT HANDLERS
# =================================================================================
# Each function handles a specific "type" of effect defined in your skills.py data.

async def handle_apply_status(target, target_effects_list, effect_data, turn_log_lines, attacker=None, **kwargs):
    """Handles applying status effects like poison, burn, flinch, etc."""
    status = effect_data.get('status_effect')
    chance = effect_data.get('chance', 1.0) # Get the chance, default to 100% if not specified

    # --- NEW: Check if the effect successfully triggers based on its chance ---
    if random.random() > chance:
        return False # The effect failed to apply

    # Prevent stacking the same status effect
    if not any(e.get('status_effect') == status for e in target_effects_list):
        new_effect = effect_data.copy()

        if new_effect.get('on_turn_end', {}).get('type') == 'damage_sequence':
            new_effect['turn_index'] = 0

        target_effects_list.append(new_effect)
        target_name = target.get('name', 'The wild pet')
        turn_log_lines.append(f"› {target_name} was afflicted with {status}!")
        return True
    return False

async def handle_stat_change(target, target_effects_list, effect_data, turn_log_lines, attacker=None, **kwargs):
    """Handles applying temporary stat changes."""
    new_effect = effect_data.copy()
    target_effects_list.append(new_effect)
    target_name = target.get('name', 'The wild pet')
    stat = effect_data.get('stat')
    modifier = effect_data.get('modifier', 1.0)
    direction = "rose" if modifier > 1.0 else "fell"
    turn_log_lines.append(f"› {target_name}'s {stat} {direction}!")
    return True


async def handle_heal_on_damage(target, effect_data, damage_dealt, turn_log_lines):
    """Handles effects that heal the user based on damage dealt (e.g., Leech Life)."""
    heal_percent = effect_data.get('percent', 0.5)  # Get the percentage from the skill's data
    heal_amount = int(damage_dealt * heal_percent)

    # Ensure the pet doesn't heal beyond its max HP
    target['current_hp'] = min(target['max_hp'], target['current_hp'] + heal_amount)

    target_name = target.get('name', 'The wild pet')
    turn_log_lines.append(f"› {target_name} restored {heal_amount} HP!")
    return True

# (You would add more handlers here for other effect types like 'delayed_heal', 'stat_inversion', etc.)

async def handle_remove_buff(target, target_effects_list, turn_log_lines):
    """Handles removing a beneficial status effect or stat buff from the target."""
    buffs_found = [
        effect for effect in target_effects_list
        if effect.get('type') == 'stat_change' and effect.get('modifier', 1.0) > 1.0
    ]

    if not buffs_found:
        turn_log_lines.append("› But it failed!")
        return False

    # For simplicity, we'll remove one random buff
    buff_to_remove = random.choice(buffs_found)
    target_effects_list.remove(buff_to_remove)

    target_name = target.get('name', 'The wild pet')
    stat_name = buff_to_remove.get('stat', 'stats')
    turn_log_lines.append(f"› It burned away {target_name}'s {stat_name} boost!")
    return True

# =================================================================================
#  MASTER HANDLER DICTIONARY
# =================================================================================

EFFECT_HANDLERS = {
    "apply_status": handle_apply_status,
    "stat_change": handle_stat_change,
    "heal_on_damage": handle_heal_on_damage,
    "remove_buff": handle_remove_buff,
    # Add other handlers as you create them
}

async def apply_effect(handler_type, **kwargs):
    """A general function to call any effect handler."""
    handler = EFFECT_HANDLERS.get(handler_type)
    if handler:
        # This will now correctly call the right function with the right arguments
        return await handler(**kwargs)
    return False # Return False if no handler was found

# =================================================================================
#  PASSIVE ABILITY HANDLERS
# =================================================================================

async def handle_flame_body(attacker, defender, turn_log_lines, attacker_effects_list, **kwargs):
    """Handles the Flame Body passive. 30% chance to burn on physical contact."""
    if random.random() < 0.3: # 30% chance to trigger
        turn_log_lines.append(f"› {defender['name']}'s Flame Body burned the attacker!")
        await handle_apply_status(
            target=attacker,
            target_effects_list=attacker_effects_list,
            effect_data={"status_effect": "burn", "duration": 3, "damage_per_turn": 4, "type": "status"},
            turn_log_lines=turn_log_lines
        )

async def handle_fortress_form(defender, turn_log_lines, **kwargs):
    """Handles the Fortress Form passive. Boosts defense when hit."""
    turn_log_lines.append(f"› {defender['name']}'s Fortress Form activates, bolstering its defenses!")
    # In the future, you could add a temporary defense buff here.

# The master dictionary that the combat engine will use to find the right function.
PASSIVE_HANDLERS_ON_HIT = {
    "Flame Body": handle_flame_body,
    "Fortress Form": handle_fortress_form,
    # "Rocky Rebuke": handle_rocky_rebuke, # You would add future passives here
}