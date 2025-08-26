# --- general.py (Refactored) ---
# This file now only contains the general, out-of-game commands.
# Updated to remove outdated command descriptions, correct version, and use the new status bar.
# Version updated to 4.1.8.

import discord
from discord import app_commands
from discord.ext import commands

## --- REFACTORING CHANGES ---
# We now import all necessary data and helper functions from the consolidated files.
from cogs.utils.constants import VERSION
from cogs.utils.helpers import get_status_bar


# A view for the general commands, allowing users to interact via buttons.
class GeneralView(discord.ui.View):
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
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send("Database is not ready. Please try again later.", ephemeral=True)
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None
        main_pet_data = player_and_pet_data['main_pet_data'] if player_and_pet_data else None
        help_embed = discord.Embed(
            title="Bot Commands",
            description="Here's a list of all the commands you can use in your adventure:",
            color=discord.Color.gold()
        )
        help_embed.add_field(name="`/adventure`", value="Opens the in-game menu.", inline=False)
        help_embed.add_field(name="`/start`", value="Begins your adventure.", inline=False)
        help_embed.add_field(name="`/character`", value="Opens your character menu (profile, pets, inventory).", inline=False)
        help_embed.add_field(name="`/general`", value="Opens this general command menu.", inline=False)
        if player_data and main_pet_data:
            help_embed.set_footer(text=get_status_bar(player_data, main_pet_data))
        else:
            help_embed.set_footer(text="Use /start to begin your adventure!")
        await interaction.followup.send(embed=help_embed, ephemeral=True)

    @discord.ui.button(label="Ping", style=discord.ButtonStyle.blurple)
    async def ping_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send("Database is not ready. Please try again later.", ephemeral=True)
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None
        main_pet_data = player_and_pet_data['main_pet_data'] if player_and_pet_data else None
        latency = round(self.bot.latency * 1000)
        ping_embed = discord.Embed(
            title="Latency",
            description=f"Pong! My latency is **{latency}ms**.",
            color=discord.Color.blue()
        )
        if player_data and main_pet_data:
            ping_embed.set_footer(text=get_status_bar(player_data, main_pet_data))
        else:
            ping_embed.set_footer(text="Use /start to begin your adventure!")
        await interaction.followup.send(embed=ping_embed, ephemeral=True)

    @discord.ui.button(label="About", style=discord.ButtonStyle.blurple)
    async def about_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send("Database is not ready. Please try again later.", ephemeral=True)
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None
        main_pet_data = player_and_pet_data['main_pet_data'] if player_and_pet_data else None
        about_embed = discord.Embed(
            title="Aethelgard: The Guild's Path",
            description="""
            Welcome, adventurer, to the world of Aethelgard!

            Embark on a grand adventure across the lands, collecting powerful companions and completing quests given to you by the Guild. Your journey will take you through ten diverse towns, from the scorching Sunstone Oasis to the freezing Frostfall Peak, each with its own Guild Master.

            Earn every Guild Crest by defeating the Guild Masters to prove your worth, secure your place as a Legend, and cement your legacy in the Guild's history!
            """,
            color=discord.Color.blue()
        )
        about_embed.add_field(name="Created By", value="Kyle", inline=True)
        about_embed.add_field(name="Version", value=VERSION, inline=True)
        if player_data and main_pet_data:
            about_embed.set_footer(text=get_status_bar(player_data, main_pet_data))
        else:
            about_embed.set_footer(text="Use /start to begin your adventure!")
        await interaction.followup.send(embed=about_embed, ephemeral=True)

    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.blurple)
    async def leaderboard_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send("Database is not ready. Please try again later.", ephemeral=True)
        try:
            top_players = await db_cog.get_top_players(limit=10)
        except Exception as e:
            print(f"An error occurred while fetching leaderboard data: {e}")
            return await interaction.followup.send(
                "An error occurred while fetching the leaderboard. Please try again later.", ephemeral=True)
        if not top_players:
            return await interaction.followup.send(
                "No players found yet. Be the first to join the adventure with `/start`!", ephemeral=True)
        leaderboard_text = ""
        for i, player in enumerate(top_players, 1):
            username, coins = player
            leaderboard_text += f"**{i}.** {username} - `{coins}` coins\n"
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None
        main_pet_data = player_and_pet_data['main_pet_data'] if player_and_pet_data else None
        leaderboard_embed = discord.Embed(
            title="💰 Top Adventurers Leaderboard",
            description=leaderboard_text,
            color=discord.Color.gold()
        )
        leaderboard_embed.set_thumbnail(url="https://www.pngall.com/wp-content/uploads/2016/06/Coin-Transparent.png")
        if player_data and main_pet_data:
            leaderboard_embed.set_footer(text=get_status_bar(player_data, main_pet_data))
        else:
            leaderboard_embed.set_footer(text="Use /start to begin your adventure!")
        await interaction.followup.send(embed=leaderboard_embed, ephemeral=True)

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.blurple)
    async def rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send("Database is not ready. Please try again later.", ephemeral=True)
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None
        main_pet_data = player_and_pet_data['main_pet_data'] if player_and_pet_data else None
        rules_embed = discord.Embed(
            title="Pet Adventure Rules",
            description="""
            1. No cheating or exploiting bugs.
            2. Be respectful to other players.
            3. Use the commands in the designated channels.
            4. Have fun!
            """,
            color=discord.Color.red()
        )
        if player_data and main_pet_data:
            rules_embed.set_footer(text=get_status_bar(player_data, main_pet_data))
        else:
            rules_embed.set_footer(text="Use /start to begin your adventure!")
        await interaction.followup.send(embed=rules_embed, ephemeral=True)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='general', description='Opens a menu for all general bot commands.')
    async def general_menu(self, interaction: discord.Interaction):
        view = GeneralView(self.bot, interaction.user.id)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.response.send_message("Database is not ready. Please try again later.",
                                                           ephemeral=True)
        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None
        main_pet_data = player_and_pet_data['main_pet_data'] if player_and_pet_data else None
        embed = discord.Embed(
            title="General Commands Menu",
            description="Welcome to the General Commands menu. Please select an option:",
            color=discord.Color.blue()
        )
        if player_data and main_pet_data:
            embed.set_footer(text=get_status_bar(player_data, main_pet_data))
        else:
            embed.set_footer(text="Use /start to begin your adventure!")
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(General(bot))
