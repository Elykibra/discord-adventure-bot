# cogs/resources.py
import discord
from discord.ext import commands

# This dictionary defines the costs for each action.
ACTION_COSTS = {
    "explore": {"energy": 2, "hunger": 1},
    "travel": {"energy": 3, "hunger": 2},
    "battle": {"energy": 5, "hunger": 3}
}

class Resources(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def spend_resources(self, user_id: int, action_type: str):
        """
        The central function for spending player energy and pet hunger.
        """
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return

        costs = ACTION_COSTS.get(action_type)
        if not costs:
            return

        # Update Player Energy
        player_data = await db_cog.get_player(user_id)
        new_energy = max(0, player_data.get('current_energy', 0) - costs.get('energy', 0))
        await db_cog.update_player(user_id, current_energy=new_energy)

        # Update Pet Hunger
        main_pet_id = player_data.get('main_pet_id')
        if main_pet_id:
            pet_data = await db_cog.get_pet(main_pet_id)
            if pet_data:
                new_hunger = max(0, pet_data.get('hunger', 0) - costs.get('hunger', 0))
                await db_cog.update_pet(main_pet_id, hunger=new_hunger)

    async def can_pet_passively_heal(self, pet_data: dict) -> bool:
        """
        Checks if a pet can receive passive health regeneration.
        Returns True if the pet is eligible, False otherwise.
        """
        if not pet_data:
            return False

        # Get the pet's hunger percentage
        hunger_percentage = pet_data.get('hunger', 100) / 100.0

        # According to the plan, pets who are "Hungry" (20-39%) or worse cannot heal.
        if hunger_percentage < 0.40:
            return False

        return True

async def setup(bot):
    await bot.add_cog(Resources(bot))