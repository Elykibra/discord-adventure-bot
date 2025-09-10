# core/effect_system.py

# Central "Effect Engine" for handling skill and passive effects.
import random
import math
from typing import List, Dict, Any, Optional

from data.skills import PET_SKILLS

# If these are used elsewhere in this module, keep them; otherwise consider moving imports
# to the modules that actually use them.
# from data.notifications import NOTIFICATIONS
# from data.pets import PET_DATABASE
# from data.skills import PET_SKILLS

# =================================================================================
#  REGISTRIES & CONSTANTS
# =================================================================================

# Single source of truth for effect handlers:
EFFECT_HANDLERS: Dict[str, Any] = {}

# Condition handlers (expand as needed)
CONDITION_HANDLERS: Dict[str, Any] = {}

# Passive handlers keyed by passive name
PASSIVE_HANDLERS_ON_HIT: Dict[str, Any] = {}

# Event constants
EVENT_ON_BEING_HIT = "on_being_hit"
EVENT_ON_TURN_END = "on_turn_end"
EVENT_ON_ATTACK_HIT = "on_attack_hit"
EVENT_ON_NEXT_DAMAGE_RECEIVED = "on_next_damage_received"
EVENT_ON_ACTION_ATTEMPT = "on_action_attempt"
EVENT_ON_Faint = "on_faint"

# =================================================================================
#  REGISTRATION HELPERS
# =================================================================================
def register_effect(effect_type: str):
    """Decorator to register an effect handler. Handlers should accept the canonical signature:
       (target, target_effects_list, effect_data, turn_log_lines, damage_dealt, attacker, **kwargs)
    """
    def _wrap(fn):
        EFFECT_HANDLERS[effect_type] = fn
        return fn
    return _wrap

def register_condition(cond_key: str):
    def _wrap(fn):
        CONDITION_HANDLERS[cond_key] = fn
        return fn
    return _wrap

# =================================================================================
#  HELPERS USED BY BATTLE FLOW
# =================================================================================
def is_player_pet(pet: dict) -> bool:
    """Detect player pet vs wild by presence of pet_id."""
    return bool(pet.get("pet_id"))

def normalize_effects(effects):
    """Ensure skill['effect'] is always a list of effect dicts."""
    if effects is None:
        return []
    if isinstance(effects, list):
        return effects
    return [effects]

def is_debuff(effect: dict) -> bool:
    """Checks if a given effect dictionary is a negative status or stat change."""
    if effect.get("type") == "stat_change" and effect.get("modifier", 1.0) < 1.0:
        return True

    if effect.get("type") == "status":
        negative_statuses = [
            "poison", "burn", "paralyze", "sleep", "frozen", "flinch", "confused",
            "corrupting_blight", "Blighted", "tidal_locked", "scrambled",
            "toxic_poison", "entangled", "weakened", "petrified", "stun",
            "recharging", "infestation", "barbed_spores"
        ]
        if effect.get("status_effect") in negative_statuses:
            return True

    return False

def choose_verb(skill_info: dict, attacker_name: str, defender_name: str, NOTIFICATIONS: Optional[dict] = None) -> str:
    """
    Choose an action verb phrase based on priority.
    Pass NOTIFICATIONS dict if you want notification lookups.
    """
    skill_type = skill_info.get("type")
    skill_cat = skill_info.get("category")
    skill_verb_type = skill_info.get("verb_type")

    # If NOTIFICATIONS isn't provided, fallback to a default phrase
    if NOTIFICATIONS is None:
        return f"attacks {defender_name}"

    verb_options = (
        NOTIFICATIONS.get("COMBAT_ACTION_VERBS", {}).get(skill_type) or
        (skill_verb_type and NOTIFICATIONS["COMBAT_ACTION_VERBS"].get(skill_verb_type)) or
        NOTIFICATIONS["COMBAT_ACTION_VERBS"].get(skill_cat) or
        ["attacks {defender_name}"]
    )

    try:
        verb_phrase = random.choice(verb_options).format(defender_name=defender_name)
    except Exception:
        verb_phrase = f"attacks {defender_name}"

    return verb_phrase

def choose_template(NOTIFICATIONS: Optional[dict] = None):
    templates = (NOTIFICATIONS.get("COMBAT_SENTENCE_TEMPLATES")
                 if NOTIFICATIONS else None)
    if not templates:
        templates = ["› {attacker_name} {verb_phrase} with **{skill_name}**{impact_phrase}"]
    return random.choice(templates)

def compute_base_damage(power: float, attack: float, defense: float) -> int:
    """Centralized damage formula. Ensures at least 1 damage."""
    return max(1, int((power / 10) + (attack / 2 - defense / 4)))

def format_pet_name(pet: dict, is_player: bool = False, is_wild: bool = False) -> str:
    """
    Returns a display-safe pet name for combat logs.
    """
    if is_wild:
        return f"the wild **{pet.get('species', 'Unknown')}**"
    else:
        return f"**{pet.get('name', pet.get('species', 'Unknown'))}**"

def is_status_effect(effect: dict) -> bool:
    return effect.get("type") == "status"

# =================================================================================
#  EFFECT HANDLERS
#  All handlers accept a canonical signature to avoid TypeErrors when called dynamically.
# =================================================================================

@register_effect("status")
async def handle_status(target: dict, target_effects_list: List[dict], effect_data: dict,
                        turn_log_lines: List[str], damage_dealt: int, attacker: dict, battle_state, **kwargs):
    """Unified status handler. Can now apply effects to the field."""

    # --- Field Effect Logic ---
    if effect_data.get("target") == "field":
        # This is a battlefield-wide effect
        user_is_player = is_player_pet(attacker)
        field_side = 'player' if user_is_player else 'opponent'

        # We can add the effect to both sides or just the user's side depending on the skill
        battle_state.field_effects['player'].append(dict(effect_data))
        battle_state.field_effects['opponent'].append(dict(effect_data))

        turn_log_lines.append(f"› A {effect_data.get('status_effect')} was generated on the battlefield!")
        return True

    status_to_apply = effect_data.get("status_effect")
    # --- Immunity Check ---
    # Check if the target has any active effects that grant immunity to this status.
    for active_effect in target_effects_list:
        if "immunities" in active_effect:
            if status_to_apply in active_effect.get("immunities", []):
                turn_log_lines.append(f"› But {format_pet_name(target)} was protected from the effect!")
                return False # The pet is immune, so the effect fails.

    # --- Conditional Check ---
    if "special_condition" in effect_data:
        condition = effect_data["special_condition"]
        # Condition: Check if attacker's stat is higher than target's
        if "if_user_stat_is_higher" in condition:
            stat_check = condition["if_user_stat_is_higher"]
            user_stat_name = stat_check.get("user_stat")
            target_stat_name = stat_check.get("target_stat")

            # Note: This checks BASE stats. For modified stats, we would need the battle_state.
            if attacker.get(user_stat_name, 0) <= target.get(target_stat_name, 0):
                return False  # Condition not met, so the effect fails.

    status = effect_data.get("status_effect")
    duration = effect_data.get("duration", 1)
    chance = effect_data.get("chance", 1.0)

    if random.random() > chance:
        return False

    active = dict(effect_data)
    active.update({
        "duration": duration,
        "source_attacker": attacker.get("name")
    })

    if "on_apply" in effect_data:
        apply_rules = effect_data["on_apply"]
        if "self_damage" in apply_rules:
            damage_info = apply_rules["self_damage"]
            if "percent_of_current_hp" in damage_info:
                percent = damage_info["percent_of_current_hp"]
                damage_amount = math.floor(target.get('current_hp', 1) * percent)
                target['current_hp'] = max(1, target['current_hp'] - damage_amount)

                target_name = format_pet_name(target)
                turn_log_lines.append(f"› {target_name} sacrificed {damage_amount} HP to use the skill!")

    target_effects_list.append(active)

    tgt_name = format_pet_name(target)
    turn_log_lines.append(f"› {tgt_name} is afflicted with {status.replace('_', ' ')}.")
    return True


@register_effect("stat_change")
async def handle_stat_change(target: dict,
                             target_effects_list: List[dict],
                             effect_data: dict,
                             turn_log_lines: List[str],
                             attacker: dict,
                             **kwargs):
    """Apply a stat modifier. Now with conditional logic."""
    stat = effect_data.get("stat")
    modifier = effect_data.get("modifier", 1.0)
    duration = effect_data.get("duration", 1)
    chance = effect_data.get("chance", 1.0)

    # --- NEW: Conditional Logic ---
    if "special_condition" in effect_data:
        condition = effect_data["special_condition"]
        # Condition: Check if target has a specific type
        if "if_target_has_type" in condition:
            required_type = condition["if_target_has_type"]
            target_types = target.get("pet_type", [])
            if required_type in target_types:
                # If condition is met, use the stronger modifier
                modifier = condition.get("then_modifier", modifier)
    # --- END NEW BLOCK ---

    tgt = format_pet_name(target)
    if random.random() <= chance:
        if isinstance(stat, list):
            for s in stat:
                target_effects_list.append(
                    {"type": "stat_change", "stat": s, "modifier": modifier, "duration": duration})
                turn_log_lines.append(f"› {tgt}'s {s} was modified!")
        else:
            target_effects_list.append(
                {"type": "stat_change", "stat": stat, "modifier": modifier, "duration": duration})
            turn_log_lines.append(f"› {tgt}'s {stat} was modified!")
        return True
    return False

@register_effect("heal_on_damage")
async def handle_heal_on_damage(target: dict,
                                target_effects_list: List[dict],
                                effect_data: dict,
                                turn_log_lines: List[str],
                                damage_dealt: int = 0,
                                attacker: dict = None,
                                **kwargs):
    """Heal `target` for a percent of damage_dealt (used immediately after damage)."""
    percent = effect_data.get("percent", 0.0)
    if damage_dealt > 0 and percent > 0:
        heal_amt = math.floor(damage_dealt * percent)
        target['current_hp'] = min(target['max_hp'], target.get('current_hp', 0) + heal_amt)
        tgt_name = f"Your **{target.get('name')}**" if target.get("pet_id") else f"The wild **{target.get('species','Unknown')}**"
        turn_log_lines.append(f"› {tgt_name} healed **{heal_amt}** HP from lifesteal!")
        return True
    return False

@register_effect("remove_buff")
async def handle_remove_buff(target: dict,
                             target_effects_list: List[dict],
                             effect_data: dict,
                             turn_log_lines: List[str],
                             damage_dealt: int = 0,
                             attacker: dict = None,
                             **kwargs):
    """Handle removing a beneficial status effect or stat buff from the target."""
    buffs_found = [
        effect for effect in target_effects_list
        if effect.get('type') == 'stat_change' and effect.get('modifier', 1.0) > 1.0
    ]

    if not buffs_found:
        turn_log_lines.append("› But it failed!")
        return False

    # Optionally remove a specific stat if provided
    stat_to_remove = effect_data.get("stat")
    if stat_to_remove:
        targeted = [b for b in buffs_found if b.get("stat") == stat_to_remove]
        if targeted:
            buff_to_remove = random.choice(targeted)
        else:
            buff_to_remove = random.choice(buffs_found)
    else:
        buff_to_remove = random.choice(buffs_found)

    try:
        target_effects_list.remove(buff_to_remove)
        target_name = target.get('name') or target.get('species', 'The wild pet')
        stat_name = buff_to_remove.get('stat', 'stats')
        turn_log_lines.append(f"› It burned away {target_name}'s {stat_name} boost!")
        return True
    except ValueError:
        turn_log_lines.append("› But it failed to remove the buff!")
        return False

@register_effect("cleanse_status")
async def handle_cleanse_status(target: dict,
                                target_effects_list: List[dict],
                                effect_data: dict,
                                turn_log_lines: List[str],
                                damage_dealt: int = 0,
                                attacker: dict = None,
                                **kwargs):
    """Cleanse up to `count` statuses (heuristic implementation)."""
    count = effect_data.get("count", -1)
    tgt_name = f"Your **{target.get('name')}**" if target.get("pet_id") else f"The wild **{target.get('species','Unknown')}**"
    removed = 0
    for e in target_effects_list[:]:
        if e.get("type") in ("status", "stat_change") and (count < 0 or removed < count):
            target_effects_list.remove(e)
            removed += 1
    turn_log_lines.append(f"› {tgt_name} had {removed} status(es) cleansed.")
    return removed > 0


@register_effect("cleanse_debuffs")
async def handle_cleanse_debuffs(target: dict,
                                 target_effects_list: List[dict],
                                 effect_data: dict,
                                 turn_log_lines: List[str],
                                 **kwargs):
    """
    Removes all negative status effects (debuffs) from the target.
    """
    debuffs_to_remove = [effect for effect in target_effects_list if is_debuff(effect)]

    if not debuffs_to_remove:
        turn_log_lines.append(f"› But there were no debuffs to cleanse!")
        return False

    for debuff in debuffs_to_remove:
        try:
            target_effects_list.remove(debuff)
        except ValueError:
            continue  # Ignore if it was already removed for some reason

    target_name = format_pet_name(target)
    turn_log_lines.append(f"› {target_name} shed all of its negative effects!")
    return True


@register_effect("steal_buff")
async def handle_steal_buff(target: dict,
                            target_effects_list: List[dict],
                            effect_data: dict,
                            turn_log_lines: List[str],
                            attacker: dict,
                            battle_state,
                            **kwargs):
    """
    Finds a random buff on the target, removes it, and applies it to the attacker.
    """
    # The "target" is the pet being stolen from (the opponent in Siphon Sorrow's case)
    # The "attacker" is the one using the skill (the one who will receive the buff)

    # Find all buffs on the target
    buffs_on_target = [
        eff for eff in target_effects_list
        if eff.get("type") == "stat_change" and eff.get("modifier", 1.0) > 1.0
    ]

    if not buffs_on_target:
        turn_log_lines.append(f"› But {format_pet_name(target)} had no buffs to steal!")
        return False

    # Choose a random buff to steal
    buff_to_steal = random.choice(buffs_on_target)

    # Remove the buff from the target
    try:
        target_effects_list.remove(buff_to_steal)
    except ValueError:
        return False  # Buff was already gone, fail silently

    # Add the buff to the attacker
    attacker_is_player = is_player_pet(attacker)
    attacker_effects_list = battle_state.player_pet_effects if attacker_is_player else battle_state.wild_pet_effects
    attacker_effects_list.append(dict(buff_to_steal))  # Add a copy

    stolen_stat = buff_to_steal.get('stat', 'stats')
    turn_log_lines.append(f"› {format_pet_name(attacker)} stole {format_pet_name(target)}'s {stolen_stat} boost!")
    return True


@register_effect("stat_inversion")
async def handle_stat_inversion(target: dict,
                                target_effects_list: List[dict],
                                effect_data: dict,
                                turn_log_lines: List[str],
                                **kwargs):
    """
    Finds all stat changes on a target and inverts their modifiers.
    """
    stat_changes_found = [
        eff for eff in target_effects_list if eff.get("type") == "stat_change"
    ]

    if not stat_changes_found:
        turn_log_lines.append(f"› But there were no stat changes to invert!")
        return False

    inverted_count = 0
    for effect in stat_changes_found:
        current_modifier = effect.get("modifier", 1.0)
        if current_modifier > 0:
            # Invert the modifier (e.g., 1.5 becomes 1/1.5 ≈ 0.67)
            effect["modifier"] = 1.0 / current_modifier
            inverted_count += 1

    if inverted_count > 0:
        turn_log_lines.append(f"› {format_pet_name(target)}'s stat changes were inverted!")
        return True

    return False


@register_effect("team_heal")
async def handle_team_heal(target: dict,
                           effect_data: dict,
                           turn_log_lines: List[str],
                           attacker: dict,
                           battle_state,
                           **kwargs):
    """Heals all pets on the user's team for a percentage of their max HP."""
    user_is_player = is_player_pet(attacker)
    roster_to_heal = battle_state.player_roster if user_is_player else battle_state.opponent_roster

    percent = effect_data.get("amount_percent", 0.0)
    healed_count = 0

    for pet in roster_to_heal:
        if pet.get("current_hp", 0) > 0:  # Don't heal fainted pets
            heal_amount = math.floor(pet.get("max_hp", 1) * percent)
            pet["current_hp"] = min(pet["max_hp"], pet["current_hp"] + heal_amount)
            healed_count += 1

    if healed_count > 0:
        turn_log_lines.append(f"› A divine light healed your team!")
        return True
    return False


@register_effect("team_cleanse")
async def handle_team_cleanse(target: dict,
                              effect_data: dict,
                              turn_log_lines: List[str],
                              attacker: dict,
                              battle_state,
                              **kwargs):
    """Cleanses all statuses from all pets on the user's team."""
    user_is_player = is_player_pet(attacker)

    # This logic assumes benched effects are stored on the battle_state
    # We will clear the active pet's effects directly
    if user_is_player:
        battle_state.player_pet_effects.clear()
    else:
        battle_state.wild_pet_effects.clear()

    # And clear any stored benched effects (conceptual)
    if hasattr(battle_state, 'benched_effects'):
        for pet_id in battle_state.benched_effects:
            # Logic to check if pet_id belongs to the user's team
            # For now, we assume it only affects the player's bench
            if user_is_player:
                battle_state.benched_effects[pet_id].clear()

    turn_log_lines.append(f"› A soothing aura cleansed your team of all ailments!")
    return True
# =================================================================================
#  PASSIVE ABILITY HANDLERS
# =================================================================================

async def handle_flame_body(attacker: dict, defender: dict, turn_log_lines: List[str],
                            attacker_effects_list: List[dict], **kwargs):
    """Handles the Flame Body passive. 30% chance to burn on physical contact."""
    if random.random() < 0.3:  # 30% chance to trigger
        turn_log_lines.append(f"› {defender.get('name', defender.get('species','Defender'))}'s Flame Body burned the attacker!")
        # Delegate to the registered apply_status handler
        await handle_status(
            target=attacker,
            target_effects_list=attacker_effects_list,
            effect_data={"status_effect": "burn", "duration": 3, "damage_per_turn": 4, "type": "status"},
            turn_log_lines=turn_log_lines,
            damage_dealt=0,
            attacker=defender,
        )


async def handle_fortress_form(defender: dict, turn_log_lines: List[str], defender_effects_list: List[dict], **kwargs):
    """Handles the Fortress Form passive. Boosts defense when hit."""
    turn_log_lines.append(f"› {format_pet_name(defender)}'s Fortress Form activates, bolstering its defenses!")

    # Call our existing stat_change handler to apply the buff
    await handle_stat_change(
        target=defender,
        target_effects_list=defender_effects_list,
        effect_data={"stat": "defense", "modifier": 1.3, "duration": 3},  # +30% Def for 3 turns
        turn_log_lines=turn_log_lines,
        attacker=defender  # The pet is buffing itself
    )

async def tick_effects_for_pet(pet: dict, effects_list: List[dict], is_player: bool, turn_log_lines: List[str], source_pet: dict = None, battle_state=None) -> bool:
    """Process lingering effects. Now checks for null_field."""

    # --- Check for Null Field ---
    is_null_field_active = False
    if battle_state:
        is_null_field_active = any(
            eff.get("status_effect") == "null_field" for eff in battle_state.field_effects["player"])

    if is_null_field_active:
        # If field is null, only decrement durations, don't apply effects
        for effect in effects_list[:]:
            if 'duration' in effect and effect.get('duration') != -1:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    try:
                        effects_list.remove(effect)
                    except ValueError:
                        pass
        return False  # No one can faint from effects if the field is null

    pet_name = format_pet_name(pet, is_player=is_player)
    fainted = False

    for effect in effects_list[:]:
        etype = effect.get("type")

        # --- All end-of-turn logic ---
        if etype == "status":
            on_turn_end = effect.get("on_turn_end")
            if on_turn_end:
                et = on_turn_end.get("type")

                # Simple damage over time (replaces the old "dot" kind)
                if et == "dot":
                    damage = on_turn_end.get("damage_per_turn", 5)
                    pet['current_hp'] = max(0, pet['current_hp'] - damage)
                    turn_log_lines.append(f"› {pet_name} took {damage} damage from {effect.get('status_effect')}!")

                # Percentage-based heal
                elif et == "heal":
                    if "amount_percent" in on_turn_end:
                        heal_amount = math.floor(pet.get('max_hp', 1) * on_turn_end["amount_percent"])
                        pet['current_hp'] = min(pet['max_hp'], pet['current_hp'] + heal_amount)
                        turn_log_lines.append(f"› {pet_name} recovered {heal_amount} HP from a lingering effect!")

                # Ramping damage
                elif et == "toxic_dot":
                    turn_index = effect.get("turn_index", 0)
                    base_damage = on_turn_end.get("base_damage", 5)
                    damage_ramp = on_turn_end.get("damage_ramp", 5)
                    dot_damage = base_damage + (turn_index * damage_ramp)
                    pet['current_hp'] = max(0, pet['current_hp'] - dot_damage)
                    turn_log_lines.append(f"› {pet_name} took {dot_damage} damage from {effect.get('status_effect')}!")
                    effect['turn_index'] = turn_index + 1

                # Damage and Leech
                elif et == "damage_and_leech_hp":
                    damage_per_turn = on_turn_end.get("damage_per_turn", 0)
                    pet['current_hp'] = max(0, pet['current_hp'] - damage_per_turn)
                    turn_log_lines.append(f"› {pet_name} took {damage_per_turn} damage from being entangled!")
                    if source_pet:
                        source_pet['current_hp'] = min(source_pet['max_hp'], source_pet['current_hp'] + damage_per_turn)
                        source_name = format_pet_name(source_pet)
                        turn_log_lines.append(f"› {source_name} drained {damage_per_turn} HP!")

                # Sequenced Damage
                elif et == "damage_sequence":
                    damage_array = on_turn_end.get("damage", [])
                    turn_index = effect.get("turn_index", 0)
                    if turn_index < len(damage_array):
                        dot_damage = damage_array[turn_index]
                        pet['current_hp'] = max(0, pet['current_hp'] - dot_damage)
                        turn_log_lines.append(
                            f"› {pet_name} took {dot_damage} damage from {effect.get('status_effect', et)}!")
                        effect['turn_index'] = turn_index + 1

            # --- Faint & Duration Logic ---
            if pet.get('current_hp', 0) <= 0:
                fainted = True
                break

            if 'duration' in effect and effect.get('duration') != -1:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    try:
                        effects_list.remove(effect)
                    except ValueError:
                        pass
                    status_name = effect.get('status_effect', 'effect').replace('_', ' ')
                    turn_log_lines.append(f"› {pet_name} is no longer afflicted with {status_name}.")

        elif etype == "stat_change":
            if 'duration' in effect and effect.get('duration') != -1:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    try:
                        effects_list.remove(effect)
                    except ValueError:
                        pass
                    stat_name = effect.get('stat', 'stats')
                    turn_log_lines.append(f"› {pet_name}'s {stat_name} change wore off.")

    return fainted

# =================================================================================
#  APPLY EFFECT ENTRYPOINT
# =================================================================================

async def apply_effect(handler_type: str, **kwargs):
    """Call a registered effect handler by type with the provided kwargs.
       Returns the handler's return value or False if not found.
    """
    handler = EFFECT_HANDLERS.get(handler_type)
    if handler:
        return await handler(**kwargs)
    return False
