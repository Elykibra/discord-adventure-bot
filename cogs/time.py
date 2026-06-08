# cogs/time.py
# This cog contains the core logic for advancing time and handling all related consequences.

import discord
from discord.ext import commands
import math

# --- REFACTORED IMPORTS ---
from data.quests import QUESTS
from utils.helpers import get_notification


class Time(commands.Cog):
    """A cog for managing the in-game Day/Night cycle and time advancement."""

    def __init__(self, bot):
        self.bot = bot

    async def advance_time(self, user_id: int, restore_details: dict) -> list[str]:
        """
        Advances the game's time and returns a list of log strings
        detailing the consequences.
        """
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(user_id)
        if not player_data:
            return ["Error: Player data not found."]

        log_messages = []

        # 1. Advance the 4-Phase Time Cycle and log it
        TIME_CYCLE = ['morning', 'noon', 'evening', 'night']
        TIME_KEYS = {
            'morning': 'TIME_ADVANCE_MORNING',
            'noon':    'TIME_ADVANCE_NOON',
            'evening': 'TIME_ADVANCE_EVENING',
            'night':   'TIME_ADVANCE_NIGHT',
        }
        current_time = player_data.get('day_of_cycle', 'morning')
        # Advance to the next phase; wrap around after night → morning
        current_index = TIME_CYCLE.index(current_time) if current_time in TIME_CYCLE else 0
        new_time = TIME_CYCLE[(current_index + 1) % len(TIME_CYCLE)]
        await db_cog.update_player(user_id, day_of_cycle=new_time)

        time_key = TIME_KEYS.get(new_time, 'TIME_ADVANCE_MORNING')
        log_messages.append(get_notification(time_key))

        # 2. Process Quest Consequences (e.g., for time-sensitive quests)
        active_quests = await db_cog.get_active_quests(user_id)
        failed_quests_messages = []
        for quest in active_quests:
            quest_id = quest['quest_id']
            quest_data = next((data for town_quests in QUESTS.values() for q_id, data in town_quests.items() if q_id == quest_id), None)

            if quest_data and quest_data.get('time_sensitive'):
                progress = quest.get('progress', {})
                ticks_remaining = progress.get('ticks_remaining', 1)
                ticks_remaining -= 1

                if ticks_remaining <= 0:
                    # Time's up — fail the quest
                    await db_cog.complete_quest(user_id, quest_id)
                    await db_cog.set_flag(user_id, f"quest_{quest_id}_failed")
                    failure_message = quest_data.get('failure_dialogue', f"You failed the quest: **{quest_data['title']}**.")
                    failed_quests_messages.append(f"⏰ {failure_message}")
                else:
                    # Still has time — decrement and warn if last tick
                    progress['ticks_remaining'] = ticks_remaining
                    await db_cog.update_quest_progress(user_id, quest_id, progress)
                    if ticks_remaining == 1:
                        failed_quests_messages.append(f"⚠️ **{quest_data['title']}** is running out of time — one more rest and it will be gone!")

        # 3. Restore Player and Pet Resources
        energy_to_restore = math.floor(
            player_data['max_energy'] * (restore_details.get('energy_restore_percent', 0) / 100))
        new_energy = min(player_data['max_energy'], player_data['energy'] + energy_to_restore)
        await db_cog.update_player(user_id, energy=new_energy)
        log_messages.append(get_notification(
            "PLAYER_RESTORE_ENERGY",
            new_energy=new_energy,
            max_energy=player_data['max_energy']
        ))

        if player_data.get('main_pet_id'):
            main_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
            if main_pet_data:
                health_to_restore = math.floor(
                    main_pet_data['max_hp'] * (restore_details.get('health_restore_percent', 0) / 100))
                new_health = min(main_pet_data['max_hp'], main_pet_data['current_hp'] + health_to_restore)
                await db_cog.update_pet(main_pet_data['pet_id'], current_hp=new_health)
                log_messages.append(get_notification(
                    "PET_RESTORE_HP",
                    pet_name=main_pet_data['name'],
                    new_hp=new_health,
                    max_hp=main_pet_data['max_hp']
                ))

        # 4. Return the list of log messages
        return log_messages

async def setup(bot):
    await bot.add_cog(Time(bot))