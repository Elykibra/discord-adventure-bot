# cogs/gameplay/character.py
import discord
from discord import app_commands
from discord.ext import commands
from cogs.utils.views_character import CharacterView
from cogs.utils.helpers import get_status_bar


class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='character', description='Opens your main character menu.')
    async def character_menu(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        if not player_and_pet_data:
            return await interaction.followup.send("You have not started your adventure! Use `/start` to begin.",
                                                   ephemeral=True)

        status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
        embed = discord.Embed(
            title="👤 Character Menu",
            description="Select an option to view your profile, manage your pets, or check your bag.",
            color=discord.Color.blue()
        )
        embed.set_footer(text=status_bar)

        view = CharacterView(self.bot, interaction.user.id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Character(bot))