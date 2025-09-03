# cogs/quests.py
import discord
from discord import app_commands
from discord.ext import commands
from data.quests import QUESTS


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quests", description="View your current quest log.")
    async def quests(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        active_quests = await db_cog.get_active_quests(interaction.user.id)

        if not active_quests:
            embed = discord.Embed(
                title="📜 Quest Log",
                description="You have no active quests.\n*Explore the world and talk to people to find new adventures!*",
                color=discord.Color.dark_gold()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="📜 Quest Log",
            description="Here are your current objectives:",
            color=discord.Color.dark_gold()
        )

        for quest in active_quests:
            quest_id = quest['quest_id']
            # Find the quest data from our data file
            quest_data = next(
                (q for town_quests in QUESTS.values() for q_id, q in town_quests.items() if q_id == quest_id), None)

            if quest_data:
                progress = quest['progress']
                current_obj_index = progress.get('count', 0)

                if current_obj_index < len(quest_data['objectives']):
                    objective = quest_data['objectives'][current_obj_index]
                    objective_text = objective['text']

                    if 'required_count' in objective:
                        current_count = progress.get('current_count', 0)
                        objective_text += f" ({current_count}/{objective['required_count']})"

                    embed.add_field(
                        name=f" M {quest_data['title']}",
                        value=f"└─ Objective: {objective_text}",
                        inline=False
                    )

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Quests(bot))