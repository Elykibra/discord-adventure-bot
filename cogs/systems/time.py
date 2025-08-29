# --- cogs/systems/time.py ---
# This cog contains the core logic for advancing time and handling all related consequences.

import discord
from discord.ext import commands
from data.quests import QUESTS
import math

class Time(commands.Cog):
    """A cog for managing the in-game Day/Night cycle and time advancement."""

    def __init__(self, bot):
        self.bot = bot

    async def advance_time(self, user_id: int, restore_details: dict, extra_message: str = ""):
        """
        The central function for advancing the game's time.
        Returns the confirmation embed to be sent by the caller.
        """
        db_cog = self.bot.get_cog('Database')
        if not db_cog: return None

        player_data = await db_cog.get_player(user_id)
        if not player_data: return None

        # --- 1. Flip the Day/Night Cycle ---
        current_time = player_data.get('day_of_cycle', 'day')
        new_time = 'night' if current_time == 'day' else 'day'
        await db_cog.update_player(user_id, day_of_cycle=new_time)

        # --- 2. Process Quest Consequences ---
        active_quests = await db_cog.get_active_quests(user_id)
        failed_quests_messages = []
        for quest in active_quests:
            quest_id = quest['quest_id']
            # Find the quest data across all towns
            quest_data = next((data for town_quests in QUESTS.values() for q_id, data in town_quests.items() if q_id == quest_id), None)

            if quest_data and quest_data.get('time_sensitive'):
                await db_cog.complete_quest(user_id, quest_id)
                failure_message = quest_data.get('failure_dialogue', f"You failed the quest: **{quest_data['title']}**.")
                failed_quests_messages.append(f"⏰ {failure_message}")

        # --- 3. Restore Player and Pet Resources ---
        main_pet_data = None
        if player_data.get('main_pet_id'):
            main_pet_data = await db_cog.get_pet(player_data['main_pet_id'])

        energy_to_restore = math.floor(player_data['max_energy'] * (restore_details.get('energy_restore_percent', 0) / 100))
        new_energy = min(player_data['max_energy'], player_data['current_energy'] + energy_to_restore)
        await db_cog.update_player(user_id, current_energy=new_energy)

        confirmation_desc = f"You feel rested. Your energy is now **{new_energy}/{player_data['max_energy']}**."

        if main_pet_data:
            health_to_restore = math.floor(main_pet_data['max_hp'] * (restore_details.get('health_restore_percent', 0) / 100))
            new_health = min(main_pet_data['max_hp'], main_pet_data['current_hp'] + health_to_restore)
            await db_cog.update_pet(main_pet_data['pet_id'], current_hp=new_health)
            confirmation_desc += f"\nYour pet, {main_pet_data['name']}, has **{new_health}/{main_pet_data['max_hp']}** HP."

        # --- 4. Create and RETURN the Confirmation Embed ---
        confirmation_title = f"The sun sets. It is now **Night**." if new_time == 'night' else f"A new day dawns. It is now **Day**."
        if extra_message:
            confirmation_desc += extra_message

        embed = discord.Embed(
            title=confirmation_title,
            description=confirmation_desc,
            color=discord.Color.blue()
        )
        if failed_quests_messages:
            embed.add_field(name="Quest Updates", value="\n".join(failed_quests_messages), inline=False)

        return embed

async def setup(bot):
    await bot.add_cog(Time(bot))