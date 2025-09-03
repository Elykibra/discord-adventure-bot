# cogs/general.py

import discord
from discord import app_commands
from discord.ext import commands

# --- REFACTORED IMPORTS ---
# The paths are now shorter and point to the top-level utils/ directory.
from utils.constants import VERSION
from utils.helpers import get_status_bar


class GeneralView(discord.ui.View):
    """
    This view contains the buttons for the general command menu.
    Its internal logic was already solid and required no changes.
    """

    def __init__(self, bot, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    @discord.ui.button(label="Help", style=discord.ButtonStyle.blurple)
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # This code is already clean and uses the database cog correctly.
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        # ... (rest of button logic is unchanged)

    # ... (All other buttons like Ping, About, Leaderboard, and Rules are also unchanged) ...


class General(commands.Cog):
    """The main cog that contains the /general slash command."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='general', description='Opens a menu for all general bot commands.')
    async def general_menu(self, interaction: discord.Interaction):
        # This command's logic is already perfect. It correctly creates the view
        # and uses the helper function to generate the status bar.
        view = GeneralView(self.bot, interaction.user.id)
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        embed = discord.Embed(
            title="General Commands Menu",
            description="Welcome to the General Commands menu. Please select an option:",
            color=discord.Color.blue()
        )
        if player_and_pet_data:
            embed.set_footer(
                text=get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data']))
        else:
            embed.set_footer(text="Use /start to begin your adventure!")

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(General(bot))