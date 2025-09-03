# utils/helpers.py
# This file contains all shared helper functions.

import discord
import random
from typing import Any, Dict, List

# We import from our new data and utils layers
from data import towns, skills, quests, items
from data.skills import PET_SKILLS
from .constants import PET_IMAGE_URLS, CREST_RANKS, DEFENSIVE_TYPE_CHART

async def get_town_embed(bot, user_id, town_id):
    """Creates a dynamic embed for a town, showing the correct description for day or night."""
    db_cog = bot.get_cog('Database')
    player_data = await db_cog.get_player(user_id)
    time_of_day = player_data.get('day_of_cycle', 'day')
    town_info = towns.get(town_id)
    if not town_info:
        return None
    description_key = f"description_{time_of_day}"
    description = town_info.get(description_key, town_info.get('description_day'))
    embed = discord.Embed(
        title=f"Welcome to {town_info['name']}!",
        description=description,
        color=discord.Color.blue()
    )
    # --- NEW: This block adds the banner image ---
    if town_image_url := town_info.get("image_url"):
        embed.set_image(url=town_image_url)
    # --- END OF NEW BLOCK ---

    player_and_pet_data = await db_cog.get_player_and_pet_data(user_id)
    if player_and_pet_data:
        status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
        embed.set_footer(text=status_bar)
    return embed

def get_player_rank_info(num_crests):
    """Determines the player's rank and provides progress info."""
    current_rank_info = CREST_RANKS[0]
    for rank_data in CREST_RANKS:
        if num_crests >= rank_data["crest_count"]:
            current_rank_info = rank_data
    rank, description, next_threshold = current_rank_info["rank"], current_rank_info["description"], current_rank_info["next_crest_count"]
    if next_threshold is not None:
        current_threshold = current_rank_info["crest_count"]
        progress_total = next_threshold - current_threshold
        progress_current = num_crests - current_threshold
        filled_blocks = int((progress_current / progress_total) * 10) if progress_total > 0 else 10
        empty_blocks = 10 - filled_blocks
        progress_bar = f"{'🟩' * filled_blocks}{'⬜' * empty_blocks} {progress_current}/{progress_total}"
    else:
        progress_bar = "Max Rank Reached! ✨"
    return {"rank": rank, "description": description, "progress_bar": progress_bar, "next_rank_threshold": next_threshold}

def get_pet_image_url(pet_species):
    """Returns the image URL for a given pet species."""
    return PET_IMAGE_URLS.get(pet_species, "https://placehold.co/100x100")


def _pet_tuple_to_dict(pet_data: tuple) -> Dict[str, Any]:
    """
    Converts a pet data tuple from the database into a dictionary.
    UPDATED to match the new 26-column database schema.
    """
    if not pet_data: return {}
    if isinstance(pet_data, dict): return pet_data

    # This is the corrected list of keys in the exact order of your new database table
    keys = ['pet_id', 'owner_id', 'name', 'species', 'description', 'rarity', 'pet_type', 'level', 'xp', 'current_hp', 'max_hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed', 'base_hp', 'base_attack', 'base_defense', 'base_special_attack', 'base_special_defense', 'base_speed', 'hunger', 'skills', 'is_in_party', 'passive_ability']

    # Ensure the data from the database has the same number of items as our keys
    if len(keys) != len(pet_data):
        print(f"!!! KEY-VALUE MISMATCH ERROR in _pet_tuple_to_dict !!! Expected {len(keys)}, got {len(pet_data)}.")
        return dict(zip(keys[:len(pet_data)], pet_data))
    return dict(zip(keys, pet_data))


def _create_progress_bar(current: int, max_val: int) -> str:
    """Creates a simple, color-changing emoji-based progress bar."""
    if max_val == 0:
        return " " * 8 # Return empty space if no max value

    percent = current / max_val

    if percent > 0.6:
        filled_emoji = '🟩'
    elif percent > 0.25:
        filled_emoji = '🟨'
    else:
        filled_emoji = '🟥'

    filled_blocks = int(percent * 7)
    empty_blocks = 7 - filled_blocks

    return f"{filled_emoji * filled_blocks}{'⬜' * empty_blocks}"

def get_status_bar(player_data: dict, main_pet_data: dict) -> str:
    """Generates a concise, one-line status bar for a player and their main pet."""
    time_of_day = player_data.get('day_of_cycle', 'day')
    time_emoji = '☀️' if time_of_day == 'day' else '🌙'
    current_energy, max_energy = player_data.get('current_energy', 0), player_data.get('max_energy', 100)
    pet_current_hp = main_pet_data.get('current_hp', 0) if main_pet_data else 0
    pet_max_hp = main_pet_data.get('max_hp', 0) if main_pet_data else 0
    pet_hunger = main_pet_data.get('hunger', 0) if main_pet_data else 0
    return (f"{time_emoji} {time_of_day.capitalize()} | ⚡️ Energy: {current_energy}/{max_energy} | "
            f"❤️ Pet HP: {pet_current_hp}/{pet_max_hp} | 🍔 Pet Hunger: {pet_hunger}/100")


def get_ai_move(ai_pet, player_pet, gloom_meter):
    """
    Determines the AI's move based on its personality and the state of the battle.
    Now with unique logic for each archetype.
    """
    personality = ai_pet.get("personality", "Aggressive")
    available_skills = ai_pet.get("skills", ["scratch"])

    def get_strongest_move():
        strongest_move_id, max_power = (available_skills[0] if available_skills else "scratch"), 0
        for skill_id in available_skills:
            # --- FIX: Use "power" instead of "damage" ---
            power = PET_SKILLS.get(skill_id, {}).get("power", 0)
            if power > max_power:
                max_power, strongest_move_id = power, skill_id
        return strongest_move_id

    # --- NEW: Expanded AI Logic ---
    if personality == "Defensive":
        # If health is low, it tries to use a defensive move. Otherwise, it attacks.
        if (ai_pet["current_hp"] / ai_pet["max_hp"]) < 0.4:
            for skill_id in available_skills:
                if PET_SKILLS.get(skill_id, {}).get("effect") == "defense_up":
                    return {"action": "skill", "skill_id": skill_id}
        return {"action": "skill", "skill_id": get_strongest_move()}

    elif personality == "Tactical":
        # If health is low, it has a 50% chance to try and heal or use a status move.
        if (ai_pet["current_hp"] / ai_pet["max_hp"]) < 0.5 and random.random() < 0.5:
            for skill_id in available_skills:
                skill_category = PET_SKILLS.get(skill_id, {}).get("category")
                if skill_category == "Status":
                    return {"action": "skill", "skill_id": skill_id}
        # Otherwise, it attacks.
        return {"action": "skill", "skill_id": get_strongest_move()}

    # "Swift" would have its own logic here in the future.
    # elif personality == "Swift":
    #     ...

    else:  # Default behavior for "Aggressive" and any other types
        return {"action": "skill", "skill_id": get_strongest_move()}

async def apply_effect(db_cog, target, effect_data):
    """Applies a given effect to a target player or pet."""
    effect_type = effect_data.get("type")
    if effect_type == "heal_pet":
        # --- CORRECTED HEALING LOGIC ---
        new_health = min(target['max_hp'], target['current_hp'] + effect_data['value'])
        await db_cog.update_pet(target['pet_id'], current_hp=new_health) # Corrected function call
        return f"Healed {target['name']} for {effect_data['value']} HP!"
    elif effect_type == "restore_energy":
        new_energy = min(target['max_energy'], target['current_energy'] + effect_data['value'])
        await db_cog.update_player(target['user_id'], current_energy=new_energy)
        return f"Restored {effect_data['value']} energy!"

    # ... add more elifs for "apply_status", etc.


def get_type_multiplier(attack_type: str, defender_types: list) -> float:
    """
    Calculates the damage multiplier based on the attack type and the defender's type(s).
    Returns the final multiplier (e.g., 2.0 for super effective, 0.5 for not very effective, 0.0 for immune).
    """
    total_multiplier = 1.0

    # Ensure defender_types is a list
    if not isinstance(defender_types, list):
        defender_types = [defender_types]

    for defender_type in defender_types:
        chart_entry = DEFENSIVE_TYPE_CHART.get(defender_type, {})

        if attack_type in chart_entry.get("weak_to", []):
            total_multiplier *= 2.0
        elif attack_type in chart_entry.get("resists", []):
            total_multiplier *= 0.5
        elif attack_type in chart_entry.get("immune_to", []):
            return 0.0  # Immunity overrides everything

    return total_multiplier

async def check_quest_progress(bot, user_id, action_type, context=None):
    """
    The definitive, scalable Quest Progression Engine.
    This version RETURNS a list of messages instead of sending them.
    """
    context = context or {}
    messages_to_return = []  # Initialize the list at the top
    db_cog = bot.get_cog('Database')
    active_quests = await db_cog.get_active_quests(user_id)

    if not active_quests:
        return messages_to_return  # Return the empty list

    for quest in active_quests:
        quest_id = quest['quest_id']
        # --- FIX: Look up quest data from the master QUESTS dictionary ---
        # This searches through all towns to find the quest_id
        quest_data = next(
            (data for town_quests in QUESTS.values() for q_id, data in town_quests.items() if q_id == quest_id),
            None
        )
        if not quest_data: continue

        # Player's current progress from the database
        player_progress = quest['progress']
        current_step_index = player_progress.get('count', 0)

        objectives = quest_data.get('objectives', [])
        if current_step_index >= len(objectives): continue # Quest is likely finished but not yet removed

        current_objective = objectives[current_step_index]
        if action_type != current_objective.get("type"):
            continue

        target_matches = False
        objective_target = current_objective.get("target")

        # Check if the action's target matches the objective's target
        if action_type == "talk_npc" and context.get("npc_id") == objective_target:
            target_matches = True
        elif action_type in ["item_pickup", "item_use"] and context.get("item_id") == objective_target:
            target_matches = True
        elif action_type == "combat_victory" and (objective_target == "any" or context.get("species") == objective_target):
            target_matches = True
        elif action_type == "rest" and context.get("location_id") == objective_target:
            target_matches = True
        elif action_type == "combat_capture" and (objective_target == "any" or context.get("species") == objective_target):
            target_matches = True

        if target_matches:
            # --- NEW LOGIC FOR HANDLING COUNTS ---
            required_count = current_objective.get('required_count', 1)
            current_count = player_progress.get('current_count', 0) + 1

            if current_count < required_count:
                # Update the current count but don't advance to the next objective yet
                player_progress['current_count'] = current_count
                await db_cog.update_quest_progress(user_id, quest_id, player_progress)
                messages_to_return.append(
                    f"**Quest Progress:** {current_objective['text']} ({current_count}/{required_count})")
            else:
                completed_objective_text = current_objective['text']
                messages_to_return.append(f"✅ **Quest Objective Complete:** {completed_objective_text}")

                new_progress_step = current_step_index + 1
                new_progress_data = {'status': 'in_progress', 'count': new_progress_step, 'current_count': 0}

                if new_progress_step < len(objectives):
                    # Move to the next objective
                    await db_cog.update_quest_progress(user_id, quest_id, new_progress_data)
                    next_objective_text = objectives[new_progress_step]['text']
                    messages_to_return.append(f"**New Objective:** {next_objective_text}")

                else:
                    # --- THIS IS THE NEW REWARD LOGIC ---
                    # All objectives are done, complete the quest and give rewards.
                    reward_messages = []

                    # Coins
                    coins = quest_data.get('reward_coins', 0)
                    if coins > 0:
                        await db_cog.add_coins(user_id, coins)
                        reward_messages.append(f"💰 {coins} Coins")

                    # Reputation
                    rep = quest_data.get('reward_reputation', 0)
                    if rep > 0:
                        player_data = await db_cog.get_player(user_id)
                        await db_cog.update_player(user_id, reputation=player_data['reputation'] + rep)
                        reward_messages.append(f"✨ {rep} Reputation")

                    # Item(s)
                    item_id = quest_data.get('reward_item')
                    if item_id:
                        quantity = quest_data.get('reward_item_quantity', 1)
                        await db_cog.add_item_to_inventory(user_id, item_id, quantity)
                        item_name = ITEMS.get(item_id, {}).get('name', 'an item')
                        reward_messages.append(f"🎁 {quantity}x {item_name}")

                    # Send completion message
                    rewards_text = "\n".join(reward_messages)
                    embed = discord.Embed(
                        title=f"🎉 Quest Complete: {quest_data['title']}",
                        description=f"**Rewards:**\n{rewards_text}",
                        color=discord.Color.gold()
                    )
                    messages_to_return.append(f"🎉 **Quest Complete:** {quest_data['title']}")
                    await db_cog.complete_quest(user_id, quest_id)

                return messages_to_return  # Return the list, which might be empty or full of messages