# core/battle_engine.py
import random
import math
import asyncio
from typing import List, Dict, Any, Optional

# External project imports (keep these as in your project)
from data.notifications import NOTIFICATIONS
from data.pets import PET_DATABASE
from data.items import ITEMS
from data.skills import PET_SKILLS
from utils.constants import XP_REWARD_BY_RARITY
from utils.helpers import get_notification, get_type_multiplier
from core.effect_system import (
    PASSIVE_HANDLERS_ON_HIT,
    is_player_pet,
    normalize_effects,
    EVENT_ON_TURN_END,
    apply_effect,
    tick_effects_for_pet,
    EFFECT_HANDLERS, format_pet_name,
)


class BattleState:
    def __init__(self, bot, user_id, player_roster: List[dict], opponent_roster: List[dict]):
        self.bot = bot
        self.db_cog = bot.get_cog('Database')
        self.user_id = user_id

        # Store the full rosters
        self.player_roster = player_roster
        self.opponent_roster = opponent_roster

        # The active pets are the first in each roster
        self.player_pet = self.player_roster[0]
        self.wild_pet = self.opponent_roster[0]  # Renaming to opponent_pet might be clearer later

        self.player_pet_effects: List[dict] = []
        self.wild_pet_effects: List[dict] = []
        self.field_effects: Dict[str, List[dict]] = {"player": [], "opponent": []}
        self.turn_count = 1
        self.turn_log: List[str] = []
        self.gloom_meter = 0
        self.purify_charges = 1
        self.pending_player_heal = 0.0
        self.disabled_moves: List[str] = []

        # -------------------------
    # Stats with modifiers
    # -------------------------
    def _get_modified_stat(self, pet: dict, stat: str, is_player: bool) -> int:
        """Return modified stat after checking for null_field."""
        base_value = pet.get(stat, 0)

        # --- Check for Null Field ---
        is_null_field_active = any(eff.get("status_effect") == "null_field" for eff in self.field_effects["player"])
        if is_null_field_active:
            return math.floor(base_value)  # Return base stat if field is null

        final_value = float(base_value)
        effects_list = self.player_pet_effects if is_player else self.wild_pet_effects
        for effect in effects_list:
            if effect.get("type") == "stat_change" and effect.get("stat") == stat:
                final_value *= effect.get("modifier", 1.0)
        return math.floor(final_value)

    # -------------------------
    # Event trigger dispatcher (scans active statuses and field effects)
    # -------------------------
    async def trigger_event(self, event_name: str, subject_pet: dict, source_pet: dict = None,
                            context: Optional[dict] = None) -> any:
        """
        Handles all event triggers. Returns a specific value depending on the event_name.
        - for "on_action_attempt": returns (bool, str) for prevention status.
        - for "on_being_hit": returns int for modified damage.
        - for others: returns None.
        """
        if context is None:
            context = {}

        # Set up default return values
        action_prevented = False
        prevention_log = ""
        modified_damage = context.get("damage", 0)

        is_player_subject = is_player_pet(subject_pet)
        effects_list = self.player_pet_effects if is_player_subject else self.wild_pet_effects

        for active_effect in effects_list[:]:
            trigger_data = active_effect.get(event_name)
            if not trigger_data:
                continue

            # --- Conditional Checks ---
            conditions_met = True
            skill_info = context.get("skill_info", {})

            if "if_move_category" in trigger_data and skill_info.get("category") != trigger_data["if_move_category"]:
                conditions_met = False
            if "if_attack_category" in trigger_data and skill_info.get("category") != trigger_data[
                "if_attack_category"]:
                conditions_met = False
            if "if_attack_type" in trigger_data:
                required_types = trigger_data["if_attack_type"]
                if not isinstance(required_types, list): required_types = [required_types]
                if skill_info.get("type") not in required_types: conditions_met = False
            if trigger_data.get("if_attack_damaging") and context.get("damage", 0) <= 0:
                conditions_met = False
            # --- End Conditional Checks ---

            if conditions_met:
                # --- Event-Specific Logic ---
                if event_name == "on_action_attempt" and "chance_to_fail" in trigger_data:
                    if random.random() < trigger_data["chance_to_fail"]:
                        subject_name = f"**{subject_pet.get('name', subject_pet.get('species'))}**"
                        prevention_log = f"› {subject_name}'s action was thwarted by {active_effect.get('status_effect')}!"
                        action_prevented = True
                        break

                if event_name == "on_being_hit" and "damage_modifier" in trigger_data:
                    modifier = trigger_data["damage_modifier"]
                    modified_damage = math.floor(modified_damage * modifier)
                    self.turn_log.append(
                        f"› {subject_pet.get('name')}'s {active_effect.get('status_effect')} softened the blow!")

                if event_name == "on_switch_out" and "heal_next_pet_percent" in trigger_data:
                    self.pending_player_heal = trigger_data["heal_next_pet_percent"]

                if event_name == "on_faint" and trigger_data.get("from_damaging_move"):
                    then_effect = trigger_data.get("then_effect", {})
                    if then_effect.get("type") == "disable_attacker_move":
                        last_move_id = context.get("last_move_id")
                        if last_move_id:
                            self.disabled_moves.append(last_move_id)
                            skill_name = PET_SKILLS.get(last_move_id, {}).get("name", "the last move")
                            self.turn_log.append(
                                f"› {format_pet_name(subject_pet)}'s Grudge disabled {format_pet_name(source_pet)}'s {skill_name}!")

                # --- Generic "then_effect" Application ---
                then_effect_data = trigger_data.get("then_effect")
                if then_effect_data:
                    for effect_data in normalize_effects(then_effect_data):
                        if effect_data.get("type") in ["reflect_debuffs"]:
                            skill_name = skill_info.get("name", "unknown_skill")
                            effect_data["source_skill_id"] = skill_name.lower().replace(" ", "_")

                        target_pet = subject_pet if effect_data.get("target") == "self" else source_pet
                        if target_pet is None: continue

                        target_is_player = is_player_pet(target_pet)
                        target_effects_list = self.player_pet_effects if target_is_player else self.wild_pet_effects

                        await apply_effect(
                            effect_data.get("type"), target=target_pet, target_effects_list=target_effects_list,
                            effect_data=effect_data, turn_log_lines=self.turn_log,
                            damage_dealt=context.get("damage", 0),
                            attacker=subject_pet, battle_state=self,
                        )

                # --- Effect Consumption ---
                if trigger_data.get("consume_on_trigger"):
                    try:
                        effects_list.remove(active_effect)
                        self.turn_log.append(
                            f"› {subject_pet.get('name')}'s {active_effect.get('status_effect')} was consumed.")
                    except ValueError:
                        pass

        # --- Final Return Logic ---
        if event_name == "on_action_attempt":
            return action_prevented, prevention_log
        elif event_name == "on_being_hit":
            return modified_damage
        else:
            return None

    # -------------------------
    # Core attack routine (uses helpers)
    # -------------------------
    async def perform_attack(self, attacker: dict, defender: dict, skill_id: str, is_player: bool):
        skill_info = PET_SKILLS.get(skill_id,
                                    {"name": "Struggle", "power": 35, "type": "Normal", "category": "Physical"})

        log_list = []
        attacker_name = f"**{attacker['name']}**" if is_player else f"The wild **{attacker['species']}**"
        defender_name = f"the wild **{defender['species']}**" if is_player else f"**{defender['name']}**"

        skill_name = skill_info.get("name", "an unknown attack")
        skill_type = skill_info.get("type")
        skill_category = skill_info.get("category")
        skill_verb_type = skill_info.get("verb_type")

        # --- Gloom and Passive Logic (Goes first) ---
        if self.wild_pet.get('is_gloom_touched', False):
            if not is_player:
                gloom_increase = 15
                self.gloom_meter = min(100, self.gloom_meter + gloom_increase)
                log_list.append(get_notification("COMBAT_GLOOM_INCREASE", amount=gloom_increase))
            else:
                gloom_reduction = 10
                self.gloom_meter = max(0, self.gloom_meter - gloom_reduction)
                log_list.append(get_notification("COMBAT_GLOOM_DECREASE", amount=gloom_reduction))

        attacker_passive = attacker.get('passive_ability')
        if isinstance(attacker_passive, dict) and attacker_passive.get(
                'name') == "Singeing Fury" and skill_type == 'Fire':
            log_list.append(f"› {attacker_name}'s Singeing Fury intensifies!")

        # --- Main Logic Branch: Status vs. Damaging ---
        damage = 0
        if skill_category == "Status":
            effects = normalize_effects(skill_info.get('effect'))
            is_self_target = effects and effects[0].get('target') == 'self'

            if is_self_target:
                verb_phrase = random.choice(NOTIFICATIONS["COMBAT_ACTION_VERBS"].get("Self", ["prepares itself"]))
                log_list.append(f"› {attacker_name} uses **{skill_name}** and {verb_phrase}!")
            else:
                log_list.append(
                    get_notification("COMBAT_STATUS_TEMPLATES", attacker_name=attacker_name, skill_name=skill_name))

        else:  # Damaging Moves (Physical & Special)
            power = skill_info.get("power", 0)

            # --- Power Modifier System ---
            if 'power_modifier' in skill_info:
                modifier_data = skill_info['power_modifier']
                modifier_type = modifier_data.get("type")

                if modifier_type == "scale_with_opponent_debuffs":
                    # Get the list of effects on the defender
                    defender_effects = self.wild_pet_effects if is_player else self.player_pet_effects

                    # Define what a "debuff" is (e.g., a stat change with modifier < 1.0)
                    debuff_count = sum(1 for eff in defender_effects if
                                       eff.get("type") == "stat_change" and eff.get("modifier", 1.0) < 1.0)

                    power_per_debuff = modifier_data.get("power_per_debuff", 0)  # Get the value from the skill's data
                    bonus_power = debuff_count * power_per_debuff
                    power += bonus_power
                    log_list.append(f"› {skill_name}'s power grew from the opponent's weakened state!")

                # Add placeholders for other types we'll need later
                elif modifier_type == "scale_with_missing_hp":
                    # Logic for 'Last Stand' will go here
                    pass

                elif modifier_type == "scale_with_player_crests":
                    # Logic for 'Crest Resonance' will go here
                    pass

            # --- Evasion / Accuracy Check ---
            # NOTE: For this to work, pets will need base "accuracy" and "evasion" stats.
            # A good default is 1.0 for both.
            base_skill_accuracy = skill_info.get("accuracy", 1.0)  # Assume 100% accuracy unless specified on the skill

            attacker_accuracy_mod = self._get_modified_stat(attacker, 'accuracy', is_player) or 1
            defender_evasion_mod = self._get_modified_stat(defender, 'evasion', not is_player) or 1

            # Calculate final hit chance, ensuring it's not zero if evasion is high
            hit_chance = base_skill_accuracy * (attacker_accuracy_mod / defender_evasion_mod)
            hit_chance = max(0.1, min(1.0, hit_chance))  # Clamp the chance between 10% and 100%

            if random.random() > hit_chance:
                # The attack missed!
                miss_verb = random.choice(NOTIFICATIONS["COMBAT_ACTION_VERBS"]["Miss"]).format(
                    defender_name=defender_name)
                log_list.append(f"› {attacker_name}'s **{skill_name}** {miss_verb}!")

                # Return early, skipping all damage calculation and effects
                # The 'fainted' return value is False, and the log is the miss message.
                return False, "\n".join(log_list)

            attack = self._get_modified_stat(attacker, 'attack' if skill_category == "Physical" else 'special_attack',
                                             is_player)

            # --- Special Flag: Ignore Defense Buffs Check ---
            defense_stat_name = 'defense' if skill_category == "Physical" else 'special_defense'
            defense = 0  # Initialize defense

            if skill_info.get("special_flag") == "ignores_defense_buffs":
                # This attack ignores buffs. Get the defender's BASE defense stat directly.
                defense = defender.get(defense_stat_name, 0)
                log_list.append(f"› {attacker_name}'s attack shatters through the defender's fortifications!")

            # Flag
            elif skill_info.get("special_flag") == "calculates_on_physical_defense":
                # This special attack targets physical defense.
                # We ignore the 'defense_stat_name' we calculated earlier and specifically use 'defense'.
                defense = self._get_modified_stat(defender, 'defense', not is_player)
                log_list.append(f"› {attacker_name}'s attack bypasses magical wards!")

            else:
                # This is a normal attack. Calculate defense with active effects.
                defense = self._get_modified_stat(defender, defense_stat_name, not is_player)
            # --- End

            types = defender.get('pet_type', []) if isinstance(defender.get('pet_type'), list) else [
                defender.get('pet_type')]

            # --- Type Matchup Calculation ---
            defender_effects = self.wild_pet_effects if is_player else self.player_pet_effects
            multiplier = get_type_multiplier(skill_type, types,
                                             active_effects=defender_effects)  # Pass the defender's effects

            if multiplier == 0:
                log_list.append(get_notification("COMBAT_NO_EFFECT"))
            else:
                base_dmg = (power / 10) + (attack / 2 - defense / 4)

                is_crit = False
                crit_chance = skill_info.get('crit_chance', 0.05)

                if random.random() <= crit_chance:
                    is_crit = True
                    damage = max(1, int(base_dmg * 1.5 * multiplier))  # Crit damage is also affected by type

                    log_list.append(get_notification(
                        "COMBAT_CRITICAL_HIT",
                        attacker_name=attacker_name,
                        skill_name=skill_name,
                        damage=damage
                    ))
                else:
                    # This is the normal attack logic
                    damage = max(1, int(base_dmg * multiplier * random.uniform(0.9, 1.1)))

                    verb_options = (
                            NOTIFICATIONS["COMBAT_ACTION_VERBS"].get(skill_type) or
                            (skill_verb_type and NOTIFICATIONS["COMBAT_ACTION_VERBS"].get(skill_verb_type)) or
                            NOTIFICATIONS["COMBAT_ACTION_VERBS"].get(skill_category) or
                            ["attacks {defender_name}"]
                    )
                    verb_phrase = random.choice(verb_options).format(defender_name=defender_name)
                    impact_phrase = random.choice(NOTIFICATIONS["COMBAT_IMPACT_PHRASES"]).format(damage=damage)

                    template = random.choice(NOTIFICATIONS["COMBAT_SENTENCE_TEMPLATES"])
                    log_list.append(template.format(
                        attacker_name=attacker_name, verb_phrase=verb_phrase, skill_name=skill_name,
                        impact_phrase=impact_phrase
                    ))

                    if multiplier > 1.0:
                        log_list.append(get_notification("COMBAT_SUPER_EFFECTIVE", damage=damage))
                    elif multiplier < 1.0:
                        log_list.append(get_notification("COMBAT_NOT_VERY_EFFECTIVE", damage=damage))

                # --- Mid-Calculation Hooks (e.g., Damage Caps) ---
                defender_effects = self.wild_pet_effects if is_player else self.player_pet_effects
                for effect in defender_effects:
                    # Check for the on_damage_calculation trigger
                    if "on_damage_calculation" in effect:
                        calc_rules = effect["on_damage_calculation"]

                        # Handle Damage Caps
                        if "damage_cap" in calc_rules:
                            cap_info = calc_rules["damage_cap"]
                            if "percent_of_max_hp" in cap_info:
                                cap_percent = cap_info["percent_of_max_hp"]
                                max_damage = math.floor(defender.get('max_hp', 1) * cap_percent)
                                if damage > max_damage:
                                    log_list.append(f"› {defender_name}'s ward absorbed the blow, capping the damage!")
                                    damage = max_damage  # Enforce the damage cap

                # --- on_being_hit ---
                # This trigger now runs before damage is applied, and can modify the final damage.
                damage = await self.trigger_event(
                    "on_being_hit",
                    subject_pet=defender,
                    source_pet=attacker,
                    context={"damage": damage, "skill_info": skill_info}
                )
                # ---
                defender_passive = defender.get('passive_ability')
                if isinstance(defender_passive, dict) and defender_passive.get('name') == "Solid Rock" and defender[
                    'current_hp'] == defender['max_hp']:
                    damage = min(damage, defender['max_hp'] - 1)
                    log_list.append(
                        f"› {defender.get('name', 'The defender')}'s Solid Rock allowed it to endure the hit!")

                defender['current_hp'] -= damage

                # trigger for the attacker
                await self.trigger_event(
                    "on_attack_hit",
                    subject_pet=attacker,
                    source_pet=defender,
                    context={"damage": damage, "skill_info": skill_info}
                )

        # --- Effect Application (Runs for all move types) ---
        if 'effect' in skill_info:
            effects = normalize_effects(skill_info['effect'])
            for effect_data in effects:
                # determine target & which active-effects list to pass
                target_pet = attacker if effect_data.get('target') == 'self' else defender
                target_is_player = is_player_pet(target_pet)
                target_effects_list = self.player_pet_effects if target_is_player else self.wild_pet_effects

                # Centralized call to effect system (it will find the correct handler via registry)
                await apply_effect(
                    effect_data.get('type'),
                    target=target_pet,
                    target_effects_list=target_effects_list,
                    effect_data=effect_data,
                    turn_log_lines=log_list,
                    damage_dealt=damage,
                    attacker=attacker,
                    battle_state=self,  # pass battle_state if some handlers need broader access
                )

        # --- Defender's Passive on_hit (Runs for all move types) ---

        defender_passive = defender.get('passive_ability')
        passive_name = defender_passive.get('name') if isinstance(defender_passive, dict) else defender_passive
        if passive_name and passive_name in PASSIVE_HANDLERS_ON_HIT:
            handler = PASSIVE_HANDLERS_ON_HIT[passive_name]

            attacker_fx = self.player_pet_effects if is_player else self.wild_pet_effects
            defender_fx = self.wild_pet_effects if is_player else self.player_pet_effects

            await handler(attacker=attacker, defender=defender, turn_log_lines=log_list, skill_info=skill_info,
                          attacker_effects_list=attacker_fx, defender_effects_list=defender_fx)

        return defender['current_hp'] <= 0, "\n".join(log_list)

    # -------------------------
    # Round processing (keeps public flow similar to your prior code)
    # -------------------------
    async def process_round(self, player_skill_id: str):

        player_move = {"skill_id": player_skill_id}
        try:
            from utils.helpers import get_ai_move
            ai_move = get_ai_move(self.wild_pet, self.player_pet, self.gloom_meter)
        except Exception:
            ai_move = {"skill_id": random.choice(list(PET_SKILLS.keys()))}

        # Priority & order logic
        player_skill_data = PET_SKILLS.get(player_move['skill_id'], {})
        ai_skill_data = PET_SKILLS.get(ai_move['skill_id'], {})
        player_has_priority = player_skill_data.get("special_flag") == "priority_move"
        ai_has_priority = ai_skill_data.get("special_flag") == "priority_move"

        if player_has_priority and not ai_has_priority:
            player_goes_first = True
        elif not player_has_priority and ai_has_priority:
            player_goes_first = False
        else:
            player_goes_first = (
                self._get_modified_stat(self.player_pet, 'speed', True) >=
                self._get_modified_stat(self.wild_pet, 'speed', False)
            )

        order = [(self.player_pet, self.wild_pet, player_move, True),
                 (self.wild_pet, self.player_pet, ai_move, False)]
        if not player_goes_first:
            order.reverse()

        self.turn_log.clear()
        for attacker, defender, move, is_player in order:

            # --- Check if move is disabled ---
            if move['skill_id'] in self.disabled_moves:
                attacker_name = format_pet_name(attacker, is_player=is_player)
                skill_name = PET_SKILLS.get(move['skill_id'], {}).get("name")
                self.turn_log.append(f"› {attacker_name}'s {skill_name} is disabled and cannot be used!")
                continue  # Skip turn

            # --- Move Usage Condition Check ---
            skill_info = PET_SKILLS.get(move['skill_id'], {})

            if "usage_condition" in skill_info:
                condition = skill_info["usage_condition"]

                # Condition: Pet must be below a certain HP percentage
                if "max_hp_percent" in condition:
                    required_percent = condition["max_hp_percent"]
                    current_percent = attacker['current_hp'] / attacker['max_hp']

                    if current_percent > required_percent:
                        attacker_name = format_pet_name(attacker, is_player=is_player)
                        self.turn_log.append(
                            f"› {attacker_name} couldn't muster the strength to use {skill_info.get('name')}!")
                        continue  # The move fails, skip the turn

            # --- "on_action_attempt" Trigger ---
            # This event can potentially cause the turn to be skipped.
            action_prevented, prevention_log = await self.trigger_event(
                "on_action_attempt",
                subject_pet=attacker,
                source_pet=defender,
                context={"skill_info": PET_SKILLS.get(move['skill_id'], {})}
            )
            if action_prevented:
                self.turn_log.append(prevention_log)
                continue  # Skip the rest of this pet's turn
            # --- End

            attacker_effects = self.player_pet_effects if is_player else self.wild_pet_effects
            attacker_name = f"Your **{attacker['name']}**" if is_player else f"The wild **{attacker['species']}**"

            # -------------------------
            # CONTROL STATUS HANDLING
            # -------------------------
            skip_turn = False

            # 1. Flinch (one-turn skip, always consumed)
            flinch_effect = next((e for e in attacker_effects if e.get('status_effect') == 'flinch'), None)
            if flinch_effect:
                self.turn_log.append(f"› {attacker_name} flinched and couldn't move!")
                attacker_effects.remove(flinch_effect)
                continue  # move is skipped

            # --- Handle Stun, Petrified, Recharging ---
            # These are multi-turn skips that are NOT consumed until their duration expires.
            stun_effect = next((e for e in attacker_effects if e.get('status_effect') == 'stun'), None)
            if stun_effect:
                self.turn_log.append(f"› {attacker_name} is stunned and can't act!")
                skip_turn = True

            petrified_effect = next((e for e in attacker_effects if e.get('status_effect') == 'petrified'), None)
            if petrified_effect:
                self.turn_log.append(f"› {attacker_name} is petrified and cannot move!")
                skip_turn = True

            recharging_effect = next((e for e in attacker_effects if e.get('status_effect') == 'recharging'), None)
            if recharging_effect:
                self.turn_log.append(f"› {attacker_name} is recharging and must wait!")
                skip_turn = True

            # 2. Sleep (skip until duration expires)
            sleep_effect = next((e for e in attacker_effects if e.get('status_effect') == 'sleep'), None)
            if not skip_turn and sleep_effect:  # MODIFIED
                self.turn_log.append(f"› {attacker_name} is fast asleep and can't move!")
                skip_turn = True

            # 3. Frozen (same as sleep but could later add chance to thaw)
            frozen_effect = next((e for e in attacker_effects if e.get('status_effect') == 'frozen'), None)
            if not skip_turn and frozen_effect:  # MODIFIED
                self.turn_log.append(f"› {attacker_name} is frozen solid and can't move!")
                skip_turn = True

            # 4. Paralysis (chance to fail)
            paralyze_effect = next((e for e in attacker_effects if e.get('status_effect') == 'paralyze'), None)
            if not skip_turn and paralyze_effect and random.random() < 0.25:  # MODIFIED
                self.turn_log.append(f"› {attacker_name} is paralyzed! It couldn't move!")
                skip_turn = True

            # 5. Confusion (chance to self-hit)
            confuse_effect = next((e for e in attacker_effects if e.get('status_effect') == 'confuse'), None)
            if not skip_turn and confuse_effect:  # MODIFIED
                if random.random() < 0.33:  # 33% chance to self-hit
                    damage = max(1, int(attacker['max_hp'] * 0.05))  # 5% max HP self-damage
                    attacker['current_hp'] -= damage
                    self.turn_log.append(f"› {attacker_name} is confused and hurt itself in its confusion! (-{damage} HP)")
                    if attacker['current_hp'] <= 0:
                        return {"log": "\n".join(self.turn_log), "is_over": True, "win": not is_player}
                    skip_turn = True
                else:
                    self.turn_log.append(f"› {attacker_name} is confused... but it fights through the haze!")

            # 6. --- Future Control Placeholders ---

            # Silence: blocks using skills with category "Special" or "Status"
            # silence_effect = next((e for e in attacker_effects if e.get('status_effect') == 'silence'), None)
            # if silence_effect and move['skill_id'] in SPECIAL_OR_STATUS_SKILLS:
            #     self.turn_log.append(f"› {attacker_name} is silenced and can't use that move!")
            #     skip_turn = True

            if skip_turn:
                continue  # attacker loses its action this turn

            # -------------------------
            # Perform attack
            # -------------------------
            fainted, attack_log = await self.perform_attack(attacker, defender, move['skill_id'], is_player)
            self.turn_log.append(attack_log)
            if fainted:
                # --- Revive Logic Check ---
                revived = False
                # Check the fainted pet's (the defender's) effects for a revive flag
                defender_effects = self.wild_pet_effects if is_player else self.player_pet_effects
                for effect in defender_effects[:]:
                    if effect.get("unique_flag") == "revive_once":
                        # Revive the pet!
                        revive_hp = math.floor(defender.get('max_hp', 1) * 0.5)  # Revive with 50% HP
                        defender['current_hp'] = revive_hp

                        self.turn_log.append(
                            f"› {format_pet_name(defender)} endured the hit and was revived by a special power!")

                        # Remove the effect so it can't be used again
                        defender_effects.remove(effect)
                        revived = True
                        break  # Stop checking for other revive effects

                if revived:
                    fainted = False  # The pet is no longer fainted
                else:
                    # If not revived, then proceed with the normal faint logic
                    await self.trigger_event("on_faint", subject_pet=defender, source_pet=attacker,
                                             context={"last_move_id": move['skill_id']})
                    return {"log": "\n".join(self.turn_log), "is_over": True, "win": is_player}

        # -------------------------
        # End-of-turn effects
        # -------------------------
        if await tick_effects_for_pet(self.wild_pet, self.wild_pet_effects, False, self.turn_log,
                                      source_pet=self.player_pet, battle_state=self):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": True}
        if await tick_effects_for_pet(self.player_pet, self.player_pet_effects, True, self.turn_log,
                                      source_pet=self.wild_pet, battle_state=self):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": False}

        self.turn_count += 1
        return {"log": "\n".join(self.turn_log), "is_over": False}

    # -------------------------
    # Other convenience methods (capture / flee / rewards)
    # Keep your existing implementations; simplified here for clarity.
    # -------------------------
    async def attempt_capture(self, orb_id: str):
        # Use your existing logic; simplified for skeleton
        await self.db_cog.remove_item_from_inventory(self.user_id, orb_id, 1)
        capture_info = await self.get_capture_info(orb_id)
        rate = capture_info['rate']
        orb_name = ITEMS.get(orb_id, {}).get('name', 'Orb')
        self.turn_log = [f"› You used a **{orb_name}**!"]
        if random.randint(1, 100) <= rate:
            self.turn_log.append(f"› Gotcha! **{self.wild_pet['species']}** was caught!")
            # add pet to DB (keep your original call)
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": True, "captured": True}
        else:
            self.turn_log.append(f"› Oh no! The wild **{self.wild_pet['species']}** broke free!")
            # Let AI take a turn for penalty (optional)
            return await self.process_ai_turn()

    async def get_capture_info(self, orb_id: str) -> dict:
        """
        Returns a dict with capture 'rate' (1-100) and a short 'text' lore string.
        Always returns a dict (never None) so callers can safely index 'rate'.
        """
        # defensive: if DB cog missing or orb invalid, return safe defaults
        try:
            player_data = await self.db_cog.get_player(self.user_id)
        except Exception:
            player_data = {"day_of_cycle": "day"}

        context = {
            "time_of_day": player_data.get('day_of_cycle', 'day'),
            "turn_count": self.turn_count,
            "is_gloom_touched": self.wild_pet.get('is_gloom_touched', False)
        }

        RARITY_MODIFIERS = {"Common": 1.1, "Uncommon": 1.0, "Rare": 0.9, "Legendary": 0.7, "Starter": 1.0}
        PERSONALITY_MODIFIERS = {"Aggressive": 0.9, "Defensive": 0.95, "Tactical": 0.95, "Timid": 1.1}
        STATUS_MODIFIERS = {"sleep": 2.0, "paralyze": 1.5, "frozen": 2.0, "confused": 1.2}

        # If orb_id is falsy or not present, return safe default
        orb_entry = ITEMS.get(orb_id) if orb_id else None
        if not orb_entry:
            return {"rate": 0, "text": "No orb selected or orb data unavailable."}

        orb_data = orb_entry.get("orb_data")
        if not orb_data:
            return {"rate": 0, "text": f"{orb_entry.get('name', 'This orb')} has no capture data."}

        # 1. Check if the pet is Gloom-Touched and if the meter is too high.
        if context["is_gloom_touched"] and self.gloom_meter >= 50:
            return {"rate": 0, "text": "The Gloom's hold is too strong. A pact is impossible."}

        species = self.wild_pet.get("species") if self.wild_pet else None
        pet_data = PET_DATABASE.get(species, {}) if species else {}
        base_rate = pet_data.get("base_capture_rate", 30)

        max_hp = self.wild_pet.get('max_hp', 1)
        current_hp = self.wild_pet.get('current_hp', 1)
        hp_factor = ((3 * max_hp) - (2 * current_hp)) / (3 * max_hp) if max_hp > 0 else 0

        rarity_mult = RARITY_MODIFIERS.get(self.wild_pet.get('rarity'), 1.0)
        pers_mult = PERSONALITY_MODIFIERS.get(self.wild_pet.get('personality'), 1.0)

        status_mult = 1.0
        active_statuses = [e.get('status_effect') for e in self.wild_pet_effects]
        for status, mod in STATUS_MODIFIERS.items():
            if status in active_statuses:
                status_mult = max(status_mult, mod)

        orb_mult = orb_data.get('base_multiplier', 1.0)

        # Apply the Purity Orb's special bonus multiplier if the pet is Gloom-Touched
        gloom_effect_data = orb_data.get('gloom_effect', {})
        if gloom_effect_data and context["is_gloom_touched"]:
            orb_mult *= gloom_effect_data.get('bonus_multiplier_if_gloom_touched', 1.0)

        # Conditional bonuses
        if 'conditional_bonus' in orb_data:
            bonus_info = orb_data['conditional_bonus']
            if context.get(bonus_info['context_key']) == bonus_info['expected_value']:
                orb_mult *= bonus_info['multiplier']

        # Scaling bonuses
        if 'scaling_bonus' in orb_data:
            bonus_info = orb_data['scaling_bonus']
            scaling_value = context.get(bonus_info['context_key'], 0)
            orb_mult += (scaling_value * bonus_info['bonus_per_unit'])

        # Clamp final rate between 1 and 100
        final_rate = max(1, min(100, int((hp_factor * base_rate) * rarity_mult * pers_mult * status_mult * orb_mult)))

        if context["is_gloom_touched"]:
            lore_text = "The Gloom's grip is weakening! The creature's spirit is fighting back."
        elif final_rate > 75:
            lore_text = "The pet's spirit is calm. A pact is nearly formed!"
        elif final_rate > 50:
            lore_text = "The pet is weary from battle. Its wild spirit is beginning to calm."
        elif final_rate > 25:
            lore_text = "The creature is still wary, but an opportunity may present itself."
        else:
            lore_text = "The creature is alert and defensive. It would be difficult to form a pact now."

        return {"rate": final_rate, "text": lore_text}

    async def process_ai_turn(self):
        try:
            from utils.helpers import get_ai_move
            ai_move = get_ai_move(self.wild_pet, self.player_pet, self.gloom_meter)
        except Exception:
            ai_move = {"skill_id": random.choice(list(PET_SKILLS.keys()))}
        fainted, attack_log = await self.perform_attack(self.wild_pet, self.player_pet, ai_move['skill_id'], is_player=False)
        self.turn_log.append(attack_log)
        if fainted:
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": False}
        if await tick_effects_for_pet(self.player_pet, self.player_pet_effects, True, self.turn_log):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": False}
        if await tick_effects_for_pet(self.wild_pet, self.wild_pet_effects, False, self.turn_log):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": True}
        self.turn_count += 1
        return {"log": "\n".join(self.turn_log), "is_over": False}

    async def attempt_flee(self):
        # Check if the player's pet has a status that prevents fleeing.
        is_trapped = any(eff.get("status_effect") == "tidal_locked" for eff in self.player_pet_effects)

        if is_trapped:
            log = [f"› You can't escape! Your pet is affected by Tidal Lock!"]
            # If escape fails, the AI gets to take a turn.
            self.turn_log.clear()
            ai_turn_result = await self.process_ai_turn()
            log.extend(ai_turn_result['log'] if isinstance(ai_turn_result['log'], list) else [ai_turn_result['log']])
            return {"success": False, "log": log, "is_over": ai_turn_result.get('is_over', False)}

        player_speed = self._get_modified_stat(self.player_pet, 'speed', True)
        wild_speed = self._get_modified_stat(self.wild_pet, 'speed', False)
        flee_chance = 50 + (player_speed - wild_speed)
        flee_chance = max(10, min(95, flee_chance))

        if random.randint(1, 100) <= flee_chance:
            return {"success": True, "log": [get_notification("FLEE_SUCCESS")]}
        else:
            log = [get_notification("FLEE_FAILURE", wild_pet_species=self.wild_pet['species'])]
            self.turn_log.clear()
            ai_turn_result = await self.process_ai_turn()
            log.extend(ai_turn_result['log'] if isinstance(ai_turn_result['log'], list) else [ai_turn_result['log']])
            return {"success": False, "log": log, "is_over": ai_turn_result.get('is_over', False)}

    async def grant_battle_rewards(self):
        base_xp = XP_REWARD_BY_RARITY.get(self.wild_pet['rarity'], 20)

        hunger_percentage = (self.player_pet.get('hunger', 0) / 100)
        is_satiated = hunger_percentage >= 0.9  # 90-100% hunger

        # Calculate EXP with the potential bonus
        xp_gain = max(5, math.floor(base_xp * (self.wild_pet['level'] / self.player_pet['level']) * 1.5))
        satiated_bonus_xp = 0
        if is_satiated:
            satiated_bonus_xp = math.ceil(xp_gain * 0.05)
            xp_gain += satiated_bonus_xp

        coin_gain = random.randint(5, 15) * self.wild_pet['level']

        updated_pet, leveled_up = await self.db_cog.add_xp(self.player_pet['pet_id'], xp_gain)
        await self.db_cog.add_coins(self.user_id, coin_gain)
        self.player_pet = updated_pet

        log_list = [get_notification(
            "BATTLE_REWARD_BASE",
            wild_pet_species=self.wild_pet['species'],
            coin_gain=coin_gain,
            xp_gain=xp_gain
        )]

        if is_satiated:
            log_list.append(get_notification(
                "BATTLE_REWARD_SATIATED_BONUS",
                bonus_xp=satiated_bonus_xp
            ))

        if leveled_up:
            log_list.append(get_notification(
                "BATTLE_REWARD_LEVEL_UP",
                pet_name=self.player_pet['name'],
                new_level=self.player_pet['level']
            ))

        return log_list

    async def process_player_switch(self, new_pet_id: str):
        """
        Handles the logic for a player switching their active pet.
        Now includes on_switch_out and on_switch_in logic.
        """
        # Check if the CURRENT pet is trapped
        is_trapped = any(eff.get("status_effect") == "tidal_locked" for eff in self.player_pet_effects)
        if is_trapped:
            return {"success": False,
                    "log": f"› **{self.player_pet['name']}** is trapped by Tidal Lock and cannot switch out!"}

        # Find the chosen pet in the player's roster
        new_pet = next((p for p in self.player_roster if p.get('pet_id') == new_pet_id), None)

        # Validation Checks
        if not new_pet:
            return {"success": False, "log": "Error: Pet not found in your roster."}
        if new_pet['pet_id'] == self.player_pet['pet_id']:
            return {"success": False, "log": "That pet is already in battle!"}
        if new_pet.get('current_hp', 0) <= 0:
            return {"success": False, "log": f"{new_pet['name']} is unable to battle!"}

        old_pet = self.player_pet
        self.turn_log.clear()

        # Trigger "on_switch_out" for the old pet
        await self.trigger_event("on_switch_out", subject_pet=old_pet)

        # Swap the active pet
        self.player_pet = new_pet
        self.player_pet_effects.clear()  # Clear the old pet's temporary effects

        self.turn_log.append(f"› You withdrew **{old_pet['name']}** and sent out **{self.player_pet['name']}**!")

        # Handle "on_switch_in" logic
        if self.pending_player_heal > 0:
            heal_amount = math.floor(self.player_pet['max_hp'] * self.pending_player_heal)
            self.player_pet['current_hp'] = min(self.player_pet['max_hp'], self.player_pet['current_hp'] + heal_amount)
            self.turn_log.append(f"› **{self.player_pet['name']}** was blessed and healed for {heal_amount} HP!")
            self.pending_player_heal = 0.0  # Reset the flag

        # The opponent gets a free turn after a switch
        ai_turn_result = await self.process_ai_turn()
        self.turn_log.append(ai_turn_result['log'])

        return {
            "success": True,
            "log": "\n".join(self.turn_log),
            "is_over": ai_turn_result.get('is_over', False)
        }