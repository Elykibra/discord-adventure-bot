# cogs/game.py
# Handles the /start command for new players.
# Restored from original (commit 536cf3e) — uses Database cog directly.

import discord, asyncio
from discord import app_commands
from discord.ext import commands
import random
import traceback

from utils.constants import PET_DESCRIPTIONS
from data.pets import PET_DATABASE
from utils.helpers import get_pet_image_url, get_status_bar
from data.abilities import STARTER_TALENTS

# Only starter pets shown during /start
STARTER_PETS_LIST = [pet for pet in PET_DATABASE.values() if pet.get('rarity') == 'Starter']


class StartModal(discord.ui.Modal, title="Guild Registration"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.username_input = discord.ui.TextInput(
            label="Choose an in-game username",
            placeholder="Enter your username (max 20 characters)...",
            max_length=20,
            required=True
        )
        self.add_item(self.username_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await asyncio.sleep(0.1)

        db_cog = self.bot.get_cog('Database')
        username = self.username_input.value

        existing_player = await db_cog.get_player_by_username(username)
        if existing_player:
            return await interaction.followup.send(
                f"Sorry, the username `{username}` is already taken. Please try again with a different name.",
                ephemeral=True
            )

        gender_view = GenderSelectView(self.bot, interaction.user.id, username)
        message = await interaction.followup.send(
            f"Recruit **{username}**! Recruitment Officer Elara acknowledges your application. Please select your adventurer's gender.",
            view=gender_view,
            ephemeral=True
        )
        gender_view.message = message


class GenderSelectView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.gender = None
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your adventure!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(
                    content="⏱️ Gender selection timed out. Please run `/start` again to create your character.",
                    view=None
                )
            except discord.NotFound:
                pass

    async def _create_player(self, interaction: discord.Interaction, gender: str):
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.edit_original_response(
                content="Database not loaded. Please contact an administrator.",
                view=None
            )
        try:
            await db_cog.add_player(
                user_id=self.user_id,
                username=self.username,
                gender=gender
            )
            await db_cog.set_game_channel_id(interaction.channel_id)
            self.gender = gender
        except Exception as e:
            print(f"Error creating player: {e}")
            traceback.print_exc()
            return await interaction.edit_original_response(
                content=f"An error occurred while creating your player: {e}",
                view=None
            )
        for item in self.children:
            item.disabled = True
        pet_selection_view = StarterPetView(self.bot, self.user_id, self.username, self.gender)
        await interaction.edit_original_response(
            content="Recruit, by the authority of the Grand Master, you are now an Adventurer. I bestow upon you this Aethelband. Now, choose your first companion.",
            view=pet_selection_view
        )
        pet_selection_view.message = await interaction.original_response()

    @discord.ui.button(label="Male", style=discord.ButtonStyle.blurple)
    async def male_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self._create_player(interaction, "Male")

    @discord.ui.button(label="Female", style=discord.ButtonStyle.red)
    async def female_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self._create_player(interaction, "Female")

    @discord.ui.button(label="Other", style=discord.ButtonStyle.grey)
    async def other_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self._create_player(interaction, "Other")


class StarterPetView(discord.ui.View):
    def __init__(self, bot, user_id, username, gender):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.gender = gender
        self.message = None
        self.selected_pet_data = None

        options = [discord.SelectOption(label=pet['species'], value=pet['species']) for pet in STARTER_PETS_LIST]
        self.pet_select = discord.ui.Select(placeholder="Choose your starter pet...", options=options)
        self.pet_select.callback = self.pet_select_callback
        self.add_item(self.pet_select)

        self.confirm_button = discord.ui.Button(label="Confirm Choice", style=discord.ButtonStyle.green, disabled=True)
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your adventure!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(content="⏱️ Pet selection timed out. Please run `/start` again.", view=None)
            except discord.NotFound:
                pass

    async def pet_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        species_name = interaction.data['values'][0]
        self.selected_pet_data = next((pet for pet in STARTER_PETS_LIST if pet["species"] == species_name), None)
        stat_ranges = self.selected_pet_data["base_stat_ranges"]

        PET_TYPE_COLORS = {
            "Fire": discord.Color.orange(),
            "Water": discord.Color.blue(),
            "Ground": discord.Color.green(),
            "Earth": discord.Color.green(),
        }
        pet_color = PET_TYPE_COLORS.get(self.selected_pet_data['pet_type'], discord.Color.default())

        embed = discord.Embed(
            title=f"You've selected the {self.selected_pet_data['species']}!",
            description=PET_DESCRIPTIONS.get(self.selected_pet_data["species"], "No description available."),
            color=pet_color
        )
        embed.set_thumbnail(url=get_pet_image_url(self.selected_pet_data["species"]))
        embed.add_field(name="Type",        value=self.selected_pet_data['pet_type'],    inline=True)
        embed.add_field(name="Personality", value=self.selected_pet_data['personality'], inline=True)
        stats_display = (
            f"**HP:** {stat_ranges['hp'][0]}-{stat_ranges['hp'][1]}\n"
            f"**Attack:** {stat_ranges['attack'][0]}-{stat_ranges['attack'][1]}\n"
            f"**Defense:** {stat_ranges['defense'][0]}-{stat_ranges['defense'][1]}\n"
            f"**Sp. Attack:** {stat_ranges['special_attack'][0]}-{stat_ranges['special_attack'][1]}\n"
            f"**Sp. Defense:** {stat_ranges['special_defense'][0]}-{stat_ranges['special_defense'][1]}\n"
            f"**Speed:** {stat_ranges['speed'][0]}-{stat_ranges['speed'][1]}"
        )
        embed.add_field(name="Potential Base Stats", value=stats_display, inline=False)
        self.confirm_button.disabled = False
        await interaction.edit_original_response(
            content=f"You have chosen **{self.selected_pet_data['species']}**! Review its potential and confirm.",
            embed=embed,
            view=self
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')

        if not self.selected_pet_data:
            return await interaction.edit_original_response(content="Please select a pet first.", view=self)

        try:
            stat_ranges  = self.selected_pet_data["base_stat_ranges"]
            base_stats   = {stat: random.randint(val[0], val[1]) for stat, val in stat_ranges.items()}
            starting_skills = self.selected_pet_data.get("skill_tree", {}).get("1", ["scratch"])

            pet_id = await db_cog.add_pet(
                owner_id=self.user_id,
                name=self.selected_pet_data["species"],
                species=self.selected_pet_data["species"],
                description=PET_DESCRIPTIONS.get(self.selected_pet_data["species"], ""),
                rarity=self.selected_pet_data["rarity"],
                pet_type=self.selected_pet_data["pet_type"],
                skills=starting_skills,
                current_hp=base_stats["hp"],          max_hp=base_stats["hp"],
                attack=base_stats["attack"],           defense=base_stats["defense"],
                special_attack=base_stats["special_attack"],
                special_defense=base_stats["special_defense"],
                speed=base_stats["speed"],
                base_hp=base_stats["hp"],
                base_attack=base_stats["attack"],      base_defense=base_stats["defense"],
                base_special_attack=base_stats["special_attack"],
                base_special_defense=base_stats["special_defense"],
                base_speed=base_stats["speed"]
            )

            await db_cog.set_main_pet(user_id=self.user_id, pet_id=pet_id)

            # Grant the first assignment so new players have a quest log entry immediately
            await db_cog.add_quest(self.user_id, "report_to_elara")

            final_embed = discord.Embed(
                title=f"Welcome to Aethelgard, {self.username}! 🎉",
                description=(
                    f"Your adventure begins now! You are registered as a **{self.gender}** adventurer, "
                    f"and the **Aethelband** is attuned to your first companion."
                ),
                color=discord.Color.green()
            )
            final_embed.set_thumbnail(url=get_pet_image_url(self.selected_pet_data["species"]))
            final_embed.add_field(
                name=f"Your First Companion: {self.selected_pet_data['species']}",
                value=PET_DESCRIPTIONS.get(self.selected_pet_data["species"], ""),
                inline=False
            )
            stats_text = (
                f"HP: {base_stats['hp']} | Atk: {base_stats['attack']} | Def: {base_stats['defense']}\n"
                f"Sp. Atk: {base_stats['special_attack']} | Sp. Def: {base_stats['special_defense']} | Spd: {base_stats['speed']}"
            )
            final_embed.add_field(name="Your Pet's Base Stats", value=stats_text, inline=False)

            player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
            if player_and_pet_data:
                status_bar = get_status_bar(
                    player_and_pet_data['player_data'],
                    player_and_pet_data['main_pet_data']
                )
                final_embed.set_footer(text=status_bar)

            talent_view = TalentChoiceView(self.bot, self.user_id, pet_id,
                                           self.selected_pet_data['species'], final_embed)
            await interaction.edit_original_response(
                content="An excellent choice. I can sense a particular talent awakening within your new partner. Choose a talent from the dropdown below to shape its future.",
                embed=None,
                view=talent_view
            )
            self.stop()

        except Exception as e:
            print(f"\n--- [FATAL ERROR] in confirm_callback ---")
            traceback.print_exc()
            await interaction.edit_original_response(
                content=f"A critical error occurred: {e}",
                view=None
            )


class TalentChoiceView(discord.ui.View):
    def __init__(self, bot, user_id, pet_id, pet_species, final_embed):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.pet_id = pet_id
        self.pet_species = pet_species
        self.final_embed = final_embed

        talents = STARTER_TALENTS.get(self.pet_species, [])
        options = [
            discord.SelectOption(
                label=talent['name'],
                description=talent['mechanic_desc'][:100],
                value=talent['mechanic_name']
            ) for talent in talents
        ]
        talent_select = discord.ui.Select(
            placeholder="Choose your pet's Innate Talent...",
            options=options
        )
        talent_select.callback = self.talent_select_callback
        self.add_item(talent_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your adventure!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(content="⏱️ Talent selection timed out. Please run `/start` again.", view=None)
            except discord.NotFound:
                pass

    async def talent_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chosen_passive_name = interaction.data['values'][0]

        db_cog = self.bot.get_cog('Database')
        await db_cog.update_pet(self.pet_id, passive_ability=chosen_passive_name)
        chosen_talent = next(
            (t for t in STARTER_TALENTS[self.pet_species] if t['mechanic_name'] == chosen_passive_name), None
        )

        # Start the tutorial quest and mark step 0 (talk to Elara) as done
        quest_id = "a_guildsmans_first_steps"
        await db_cog.add_quest(self.user_id, quest_id)
        await db_cog.update_quest_progress(self.user_id, quest_id, {'status': 'in_progress', 'count': 1})

        self.final_embed.add_field(
            name=f"Innate Talent: {chosen_talent['name']}",
            value=f"_{chosen_talent['mechanic_desc']}_",
            inline=False
        )
        self.final_embed.add_field(
            name="✅ Quest Started: A Guildsman's First Steps",
            value="Recruitment Officer Elara has given you your first task.",
            inline=False
        )
        self.final_embed.add_field(
            name="📍 New Objective",
            value="Use `/adventure` → **Explore Wilds** and gather a **Sun-Kissed Berry**.",
            inline=False
        )

        await interaction.edit_original_response(
            content="Your companion's talent has awakened! Your adventure begins now.",
            embed=self.final_embed,
            view=None
        )
        self.stop()
        # Auto-dismiss after 30s so it doesn't clutter the screen during play
        await asyncio.sleep(30)
        try:
            await interaction.delete_original_response()
        except discord.NotFound:
            pass


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='start', description='Begin your journey as a Guild Adventurer!')
    async def start_adventure(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.response.send_message(
                "Database is not loaded. Please contact an administrator.",
                ephemeral=True
            )

        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        player_data = player_and_pet_data['player_data'] if player_and_pet_data else None

        # Already fully set up
        if player_data and player_data.get('main_pet_id'):
            return await interaction.response.send_message(
                "You have already started your adventure! Use `/adventure` to open your menu.",
                ephemeral=True
            )

        # Player exists but never picked a pet (e.g. timed out mid-flow)
        if player_data:
            username = player_data.get('username')
            gender   = player_data.get('gender')
            pet_selection_view = StarterPetView(self.bot, interaction.user.id, username, gender)
            await interaction.response.send_message(
                "It seems you haven't chosen a starter pet yet. Please select your first companion.",
                view=pet_selection_view,
                ephemeral=True
            )
            pet_selection_view.message = await interaction.original_response()
            return

        # Brand new player — open the registration modal
        modal = StartModal(self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(Game(bot))
