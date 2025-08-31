# gameplay/battle_engine.py
# This file contains the core logic engine for combat.

import random,math,asyncio, discord
from data.pets import PET_DATABASE
from data.items import ITEMS
from data.skills import PET_SKILLS
from cogs.utils import effects
from cogs.utils.helpers import get_ai_move, get_type_multiplier, check_quest_progress
from cogs.utils.constants import XP_REWARD_BY_RARITY, PET_DESCRIPTIONS


class BattleState:
    """Manages the state and logic of a single combat encounter."""

    def __init__(self, bot, user_id, player_pet, wild_pet):
        self.bot = bot
        self.db_cog = bot.get_cog('Database')
        self.user_id = user_id
        self.player_pet = player_pet
        self.wild_pet = wild_pet
        self.player_pet_effects = []
        self.wild_pet_effects = []
        self.turn_count = 1
        self.turn_log = []
        self.gloom_meter = 0
        self.purify_charges = 1

    def _get_modified_stat(self, pet: dict, stat: str) -> int:
        base_value = pet.get(stat, 0)
        final_value = float(base_value)
        effects_list = self.player_pet_effects if 'pet_id' in pet else self.wild_pet_effects
        for effect in effects_list:
            if effect.get('type') == 'stat_change' and effect.get('stat') == stat:
                final_value *= effect.get('modifier', 1.0)
        return math.floor(final_value)

    async def get_capture_info(self, orb_id: str) -> dict:

        player_data = await self.db_cog.get_player(self.user_id)

        context = {
            "time_of_day": player_data.get('day_of_cycle', 'day'),
            "turn_count": self.turn_count,
            "is_gloom_touched": False
        }

        RARITY_MODIFIERS = {"Common": 1.1, "Uncommon": 1.0, "Rare": 0.9, "Legendary": 0.7, "Starter": 1.0}
        PERSONALITY_MODIFIERS = {"Aggressive": 0.9, "Defensive": 0.95, "Tactical": 0.95, "Timid": 1.1}
        STATUS_MODIFIERS = {"sleep": 2.0, "paralyze": 1.5, "frozen": 2.0, "confused": 1.2}

        pet_data = PET_DATABASE.get(self.wild_pet['species'], {})
        base_rate = pet_data.get('base_capture_rate', 30)
        orb_data = ITEMS.get(orb_id, {}).get('orb_data', {"base_multiplier": 1.0})

        max_hp, current_hp = self.wild_pet['max_hp'], self.wild_pet['current_hp']
        hp_factor = ((3 * max_hp) - (2 * current_hp)) / (3 * max_hp) if max_hp > 0 else 0

        rarity_mult = RARITY_MODIFIERS.get(self.wild_pet['rarity'], 1.0)
        pers_mult = PERSONALITY_MODIFIERS.get(self.wild_pet.get('personality'), 1.0)

        status_mult = 1.0
        active_statuses = [e.get('status_effect') for e in self.wild_pet_effects]
        for status, mod in STATUS_MODIFIERS.items():
            if status in active_statuses:
                status_mult = max(status_mult, mod)

        orb_mult = orb_data.get('base_multiplier', 1.0)

        # Check for conditional bonuses
        if 'conditional_bonus' in orb_data:
            bonus_info = orb_data['conditional_bonus']
            if context.get(bonus_info['context_key']) == bonus_info['expected_value']:
                orb_mult *= bonus_info['multiplier']

        # Check for scaling bonuses
        if 'scaling_bonus' in orb_data:
            bonus_info = orb_data['scaling_bonus']
            scaling_value = context.get(bonus_info['context_key'], 0)
            orb_mult += (scaling_value * bonus_info['bonus_per_unit'])
        # --- END OF NEW ORB LOGIC ---

        final_rate = max(1, min(100, int((hp_factor * base_rate) * rarity_mult * pers_mult * status_mult * orb_mult)))

        if final_rate > 75:
            lore_text = "The pet's spirit is calm. A pact is nearly formed!"
        elif final_rate > 50:
            lore_text = "The pet is weary from battle. Its wild spirit is beginning to calm."
        elif final_rate > 25:
            lore_text = "The creature is still wary, but an opportunity may present itself."
        else:
            lore_text = "The creature is alert and defensive. It would be difficult to form a pact now."

        return {"rate": final_rate, "text": lore_text}

    async def perform_attack(self, attacker, defender, skill_id, is_player):
        skill_info = PET_SKILLS.get(skill_id,
                                    {"name": "Struggle", "power": 35, "type": "Normal", "category": "Physical"})
        attacker_name = f"Your **{attacker['name']}**" if is_player else f"The wild **{attacker['species']}**"
        log = [f"› {attacker_name} used **{skill_info['name']}**!"]

        attacker_passive_data = attacker.get('passive_ability')
        if isinstance(attacker_passive_data, dict) and attacker_passive_data.get('name') == "Singeing Fury" and \
                skill_info['type'] == 'Fire':
            log.append(f"› {attacker_name}'s Singeing Fury intensifies!")

        damage = 0
        if skill_info.get("category") != "Status":
            power = skill_info.get("power", 0)
            attack = self._get_modified_stat(attacker,
                                             'attack' if skill_info["category"] == "Physical" else 'special_attack')
            defense = self._get_modified_stat(defender,
                                              'defense' if skill_info["category"] == "Physical" else 'special_defense')
            types = defender.get('pet_type', []) if isinstance(defender.get('pet_type'), list) else [
                defender.get('pet_type')]
            multiplier = get_type_multiplier(skill_info['type'], types)
            base_dmg = (power / 10) + (attack / 2 - defense / 4)
            damage = max(1, int(base_dmg * multiplier * random.uniform(0.9, 1.1)))

            defender_passive_data = defender.get('passive_ability')
            if isinstance(defender_passive_data, dict) and defender_passive_data.get('name') == "Solid Rock" and \
                    defender['current_hp'] == defender['max_hp']:
                damage = min(damage, defender['max_hp'] - 1)
                log.append(
                    f"› {defender.get('name', defender.get('species'))}'s Solid Rock allowed it to endure the hit!")

            defender['current_hp'] -= damage
            log.append(f"› It dealt **{damage}** damage!")
            if multiplier > 1.0:
                log.append("› It's super effective!")
            elif multiplier < 1.0 and multiplier > 0:
                log.append("› It's not very effective...")

        if 'effect' in skill_info:
            target = attacker if skill_info['effect'].get('target') == 'self' else defender
            target_fx = self.player_pet_effects if target == self.player_pet else self.wild_pet_effects
            await effects.apply_effect(handler_type=skill_info['effect'].get('type'), target=target,
                                       target_effects_list=target_fx, effect_data=skill_info['effect'],
                                       turn_log_lines=log, damage_dealt=damage)

        defender_passive_data = defender.get('passive_ability')
        passive_name = None
        if isinstance(defender_passive_data, dict):
            passive_name = defender_passive_data.get('name')
        elif isinstance(defender_passive_data, str):
            passive_name = defender_passive_data

        if passive_name and passive_name in effects.PASSIVE_HANDLERS_ON_HIT:
            handler = effects.PASSIVE_HANDLERS_ON_HIT[passive_name]
            attacker_fx = self.player_pet_effects if is_player else self.wild_pet_effects
            await handler(attacker=attacker, defender=defender, turn_log_lines=log, skill_info=skill_info,
                          attacker_effects_list=attacker_fx)

        return defender['current_hp'] <= 0, "\n".join(log)

    async def _process_effects(self, pet, effects_list, is_player):
        pet_name = f"Your **{pet['name']}**" if is_player else f"The wild **{pet['species']}**"
        fainted = False
        for effect in effects_list[:]:
            if effect.get('status_effect') == 'flinch': continue

            on_turn_end_data = effect.get('on_turn_end', {})
            if on_turn_end_data.get('type') == 'damage_sequence':
                damage_array = on_turn_end_data.get('damage', [])
                turn_index = effect.get('turn_index', 0)
                if turn_index < len(damage_array):
                    dot_damage = damage_array[turn_index]
                    pet['current_hp'] -= dot_damage
                    self.turn_log.append(
                        f"› {pet_name} took **{dot_damage}** damage from {effect.get('status_effect')}!")
                    effect['turn_index'] = turn_index + 1
            elif effect.get('status_effect') in ['poison', 'burn']:
                damage = effect.get('damage_per_turn', 5)
                pet['current_hp'] -= damage
                self.turn_log.append(f"› {pet_name} took **{damage}** damage from its {effect.get('status_effect')}!")

            if pet['current_hp'] <= 0:
                fainted = True
                break

            if 'duration' in effect:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    effects_list.remove(effect)

                    if effect.get('type') == 'stat_change':
                        stat_name = effect.get('stat', 'stats')
                        self.turn_log.append(f"› {pet_name}'s {stat_name} change wore off.")
                    else:
                        status_name = effect.get('status_effect', 'effect').replace('_', ' ')
                        self.turn_log.append(f"› {pet_name} is no longer afflicted with {status_name}.")

        return fainted

    async def process_round(self, player_skill_id: str):
        player_move = {"skill_id": player_skill_id}
        ai_move = get_ai_move(self.wild_pet, self.player_pet, self.gloom_meter)

        # Determine turn order, including priority moves
        player_skill_data = PET_SKILLS.get(player_move['skill_id'], {})
        ai_skill_data = PET_SKILLS.get(ai_move['skill_id'], {})
        player_has_priority = player_skill_data.get("special_flag") == "priority_move"
        ai_has_priority = ai_skill_data.get("special_flag") == "priority_move"

        if player_has_priority and not ai_has_priority:
            player_goes_first = True
        elif not player_has_priority and ai_has_priority:
            player_goes_first = False
        else:
            player_goes_first = self._get_modified_stat(self.player_pet, 'speed') >= self._get_modified_stat(
                self.wild_pet, 'speed')

        order = [(self.player_pet, self.wild_pet, player_move, True), (self.wild_pet, self.player_pet, ai_move, False)]
        if not player_goes_first:
            order.reverse()

        self.turn_log.clear()
        for attacker, defender, move, is_player in order:
            # Check for flinch status
            attacker_effects = self.player_pet_effects if is_player else self.wild_pet_effects
            attacker_name = f"Your **{attacker['name']}**" if is_player else f"The wild **{attacker['species']}**"
            flinch_effect = next((e for e in attacker_effects if e.get('status_effect') == 'flinch'), None)
            if flinch_effect:
                self.turn_log.append(f"› {attacker_name} flinched and couldn't move!")
                attacker_effects.remove(flinch_effect)
                continue

            # Perform the attack and check for fainting
            fainted, attack_log = await self.perform_attack(attacker, defender, move['skill_id'], is_player)
            self.turn_log.append(attack_log)
            if fainted:
                # If a pet faints, the round is over. Return the result immediately.
                return {"log": "\n".join(self.turn_log), "is_over": True, "win": is_player}

        # Process end-of-turn effects if no one fainted from attacks
        if await self._process_effects(self.wild_pet, self.wild_pet_effects, False):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": True}
        if await self._process_effects(self.player_pet, self.player_pet_effects, True):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": False}

        # If the battle is not over, increment the turn and return the final state
        self.turn_count += 1
        return {"log": "\n".join(self.turn_log), "is_over": False}

    async def attempt_capture(self, orb_id: str):
        await self.db_cog.remove_item_from_inventory(self.user_id, orb_id, 1)
        capture_info = await self.get_capture_info(orb_id)
        rate = capture_info['rate']
        orb_name = ITEMS.get(orb_id, {}).get('name', 'Orb')
        self.turn_log = [f"› You used a **{orb_name}**!"]

        if random.randint(1, 100) <= rate:
            # SUCCESS
            self.turn_log.append(f"› Gotcha! **{self.wild_pet['species']}** was caught!")

            # Call the database with the correct, explicit parameters
            pet_to_add = self.wild_pet
            await self.db_cog.add_pet(
                owner_id=self.user_id,
                name=pet_to_add["species"],
                species=pet_to_add["species"],
                description=PET_DESCRIPTIONS.get(pet_to_add["species"], ""),
                rarity=pet_to_add["rarity"],
                pet_type=pet_to_add["pet_type"],
                skills=pet_to_add["skills"],
                current_hp=pet_to_add["max_hp"],  # Healed on capture
                max_hp=pet_to_add["max_hp"],
                attack=pet_to_add["attack"],
                defense=pet_to_add["defense"],
                special_attack=pet_to_add["special_attack"],
                special_defense=pet_to_add["special_defense"],
                speed=pet_to_add["speed"],
                # For wild pets, base stats can mirror final stats for now
                base_hp=pet_to_add["max_hp"],
                base_attack=pet_to_add["attack"],
                base_defense=pet_to_add["defense"],
                base_special_attack=pet_to_add["special_attack"],
                base_special_defense=pet_to_add["special_defense"],
                base_speed=pet_to_add["speed"],
                passive_ability=pet_to_add.get('passive_ability', {}).get('name')
            )

            # We also need to check for quest progress on capture
            quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_capture",
                                                       {"species": self.wild_pet['species']})
            if quest_updates:
                self.turn_log.extend(quest_updates)

            return {"log": "\n".join(self.turn_log), "is_over": True, "win": True, "captured": True}
        else:
            # FAILURE
            self.turn_log.append(f"› Oh no! The wild **{self.wild_pet['species']}** broke free!")
            return await self.process_ai_turn()

    async def process_ai_turn(self):
        ai_move = get_ai_move(self.wild_pet, self.player_pet, self.gloom_meter)
        fainted, attack_log = await self.perform_attack(self.wild_pet, self.player_pet, ai_move['skill_id'], is_player=False)
        self.turn_log.append(attack_log)

        if fainted: return {"log": "\n".join(self.turn_log), "is_over": True, "win": False}

        if await self._process_effects(self.player_pet, self.player_pet_effects, True):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": False}
        if await self._process_effects(self.wild_pet, self.wild_pet_effects, False):
            return {"log": "\n".join(self.turn_log), "is_over": True, "win": True}

        self.turn_count += 1
        return {"log": "\n".join(self.turn_log), "is_over": False}

    async def grant_battle_rewards(self):
        base_xp = XP_REWARD_BY_RARITY.get(self.wild_pet['rarity'], 20)
        xp_gain = max(5, math.floor(base_xp * (self.wild_pet['level'] / self.player_pet['level']) * 1.5))
        coin_gain = random.randint(5, 15) * self.wild_pet['level']

        updated_pet, leveled_up = await self.db_cog.add_xp(self.player_pet['pet_id'], xp_gain)
        await self.db_cog.add_coins(self.user_id, coin_gain)
        self.player_pet = updated_pet

        result_log = f"🏆 You defeated the wild {self.wild_pet['species']}! You earned {coin_gain} coins and {xp_gain} EXP."
        if leveled_up:
            result_log += f"\n🌟 Your pet {self.player_pet['name']} grew to Level {self.player_pet['level']}!"
        return result_log