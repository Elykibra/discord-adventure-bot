# game.py
# game.py
# Handles the /start command for new players.
# Corrected to fix logical flow in the pet confirmation step.

import discord
from discord import app_commands
from discord.ext import commands
import random
import traceback
from cogs.utils.constants import PET_DESCRIPTIONS
from data.pets import PET_DATABASE
from cogs.utils.helpers import get_pet_image_url, get_status_bar
from data.abilities import STARTER_TALENTS

# A helper list to get only the starter pets from the database
STARTER_PETS_LIST = [pet for pet in PET_DATABASE.values() if pet.get('rarity') == 'Starter']


# A modal to collect the user's desired username.
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
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send(
                "Database not loaded. Please contact an administrator.",
                ephemeral=True
            )
        username = self.username_input.value
        try:
            existing_player = await db_cog.get_player_by_username(username)
            if existing_player:
                return await interaction.followup.send(
                    f"Sorry, the username `{username}` is already taken. Please try again with a different name.",
                    ephemeral=True
                )
        except Exception as e:
            return await interaction.followup.send(
                f"An error occurred while checking the username: `{e}`",
                ephemeral=True
            )
        gender_view = GenderSelectView(self.bot, interaction.user.id, username)
        await interaction.followup.send(
            f"Recruit **{username}**! Recruitment Officer Elara acknowledges your application. Please select your adventurer's gender.",
            view=gender_view,
            ephemeral=True
        )
        gender_view.message = await interaction.original_response()


# A view for gender selection buttons
class GenderSelectView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=60)
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
            for item in self.children:
                item.disabled = True
            await self.message.edit(content="Gender selection timed out.", view=self)

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

# A view for selecting the starter pet.
class StarterPetView(discord.ui.View):
    def __init__(self, bot, user_id, username, gender):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.gender = gender
        self.message = None
        self.selected_pet_data = None

        # --- REFACTOR FIX ---
        # Use the new STARTER_PETS_LIST we created at the top of the file
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
            for item in self.children:
                item.disabled = True
            await self.message.edit(content="Pet selection timed out.", view=self)

    async def pet_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        species_name = interaction.data['values'][0]
        self.selected_pet_data = next((pet for pet in STARTER_PETS_LIST if pet["species"] == species_name), None)
        stat_ranges = self.selected_pet_data["base_stat_ranges"]

        # --- NEW: Dynamic Color Logic ---
        PET_TYPE_COLORS = {
            "Fire": discord.Color.orange(),
            "Water": discord.Color.blue(),
            "Ground": discord.Color.green()
            # You can add more types here later
        }
        pet_color = PET_TYPE_COLORS.get(self.selected_pet_data['pet_type'], discord.Color.default())

        embed = discord.Embed(
            title=f"You've selected the {self.selected_pet_data['species']}!",
            description=PET_DESCRIPTIONS.get(self.selected_pet_data["species"], "No description."),
            color=pet_color  # <-- Use the dynamic color
        )

        embed.set_thumbnail(url=get_pet_image_url(self.selected_pet_data["species"]))
        embed.add_field(name="Type", value=self.selected_pet_data['pet_type'], inline=True)
        embed.add_field(name="Personality", value=self.selected_pet_data['personality'], inline=True)
        stats_display = (f"**HP:** {stat_ranges['hp'][0]}-{stat_ranges['hp'][1]}\n"
                         f"**Attack:** {stat_ranges['attack'][0]}-{stat_ranges['attack'][1]}\n"
                         f"**Defense:** {stat_ranges['defense'][0]}-{stat_ranges['defense'][1]}\n"
                         f"**Sp. Attack:** {stat_ranges['special_attack'][0]}-{stat_ranges['special_attack'][1]}\n"
                         f"**Sp. Defense:** {stat_ranges['special_defense'][0]}-{stat_ranges['special_defense'][1]}\n"
                         f"**Speed:** {stat_ranges['speed'][0]}-{stat_ranges['speed'][1]}")
        embed.add_field(name="Potential Base Stats", value=stats_display, inline=False)
        self.confirm_button.disabled = False
        await interaction.edit_original_response(content=f"You have chosen **{self.selected_pet_data['species']}**! Review its potential and confirm.", embed=embed, view=self)

    async def confirm_callback(self, interaction: discord.Interaction):
        print("\n--- Confirm starter pet button clicked ---")
        try:
            await interaction.response.defer()
            print("[LOG] Interaction deferred.")

            db_cog = self.bot.get_cog('Database')
            if not self.selected_pet_data:
                print("[ERROR] No pet selected.")
                return await interaction.edit_original_response(content="Please select a pet first.", view=self)

            print(f"[LOG] Selected pet: {self.selected_pet_data['species']}")
            stat_ranges = self.selected_pet_data["base_stat_ranges"]
            base_stats = {stat: random.randint(val[0], val[1]) for stat, val in stat_ranges.items()}
            print(f"[LOG] Randomized base stats: {base_stats}")

            starting_skills = self.selected_pet_data.get("skill_tree", {}).get("1", ["scratch"])

            print("[LOG] Calling db_cog.add_pet...")
            pet_id = await db_cog.add_pet(
                owner_id=interaction.user.id, name=self.selected_pet_data["species"],
                species=self.selected_pet_data["species"],
                description=PET_DESCRIPTIONS.get(self.selected_pet_data["species"], ""),
                rarity=self.selected_pet_data["rarity"], pet_type=self.selected_pet_data["pet_type"],
                skills=starting_skills,
                current_hp=base_stats["hp"], max_hp=base_stats["hp"],
                attack=base_stats["attack"], defense=base_stats["defense"],
                special_attack=base_stats["special_attack"], special_defense=base_stats["special_defense"],
                speed=base_stats["speed"], base_hp=base_stats["hp"],
                base_attack=base_stats["attack"], base_defense=base_stats["defense"],
                base_special_attack=base_stats["special_attack"], base_special_defense=base_stats["special_defense"],
                base_speed=base_stats["speed"]
            )
            print(f"[LOG] Pet added. New ID: {pet_id}")

            print("[LOG] Calling db_cog.set_main_pet...")
            await db_cog.set_main_pet(user_id=interaction.user.id, pet_id=pet_id)
            print(f"[LOG] Pet {pet_id} set as main for user {interaction.user.id}.")

            print("[LOG] Calling db_cog.add_quest...")
            await db_cog.add_quest(interaction.user.id, "a_guildsmans_first_steps", {"count": 0})
            print("[LOG] Initial quest added.")

            # --- ALL FINAL MESSAGE LOGIC IS NOW INSIDE THE TRY BLOCK ---
            final_embed = discord.Embed(
                title=f"Welcome to Aethelgard, {self.username}! 🎉",
                description=f"Your adventure begins now! You are registered as a **{self.gender}** adventurer, and the **Aethelband** is attuned to your first companion.",
                color=discord.Color.green()
            )
            final_embed.set_thumbnail(url=get_pet_image_url(self.selected_pet_data["species"]))
            final_embed.add_field(name=f"Your First Companion: {self.selected_pet_data['species']}",
                                  value=PET_DESCRIPTIONS.get(self.selected_pet_data["species"], ""), inline=False)
            stats_text = (f"HP: {base_stats['hp']} | Atk: {base_stats['attack']} | Def: {base_stats['defense']}\n"
                          f"Sp. Atk: {base_stats['special_attack']} | Sp. Def: {base_stats['special_defense']} | Spd: {base_stats['speed']}")
            final_embed.add_field(name="Your Pet's Base Stats", value=stats_text, inline=False)

            player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
            if player_and_pet_data:
                status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
                final_embed.set_footer(text=status_bar)

            print("[LOG] Sending final confirmation message...")
            talent_view = TalentChoiceView(self.bot, self.user_id, pet_id, self.selected_pet_data['species'],
                                           final_embed)
            await interaction.edit_original_response(
                content="An excellent choice. I can sense a particular talent awakening within your new partner. Choose a talent from the dropdown below to shape its future.",
                embed=None,
                view=talent_view
            )
            print("--- Confirm starter pet finished successfully ---\n")
            self.stop()

        except Exception as e:
            print("\n--- [FATAL ERROR] in confirm_callback ---")
            traceback.print_exc()
            await interaction.edit_original_response(content="A critical error occurred. Please check the console.",
                                                     view=None)


class TalentChoiceView(discord.ui.View):
    def __init__(self, bot, user_id, pet_id, pet_species, final_embed):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.pet_id = pet_id
        self.pet_species = pet_species
        self.final_embed = final_embed

        # --- THIS IS THE NEW UI LOGIC ---
        # Get the list of talents for the chosen starter pet
        talents = STARTER_TALENTS.get(self.pet_species, [])

        # Create a list of SelectOptions for the dropdown
        options = [
            discord.SelectOption(
                label=talent['name'],
                # Use the mechanic description to explain what the talent does
                description=talent['mechanic_desc'][:100],  # Descriptions are limited to 100 characters
                value=talent['mechanic_name']  # Store the mechanic name in the value
            ) for talent in talents
        ]

        # Create the dropdown (Select) component
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

    async def talent_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chosen_passive_name = interaction.data['values'][0]

        db_cog = self.bot.get_cog('Database')
        await db_cog.update_pet(self.pet_id, passive_ability=chosen_passive_name)
        chosen_talent = next(
            (t for t in STARTER_TALENTS[self.pet_species] if t['mechanic_name'] == chosen_passive_name), None)

        # --- THIS IS THE CORRECTED QUEST GRANTING LOGIC ---
        quest_id = "a_guildsmans_first_steps"
        await db_cog.add_quest(self.user_id, quest_id)
        # Talking to Elara during /start IS the first objective, so we complete it.
        await db_cog.update_quest_progress(self.user_id, quest_id, {'status': 'in_progress', 'count': 1})

        # Add the talent info to the embed
        self.final_embed.add_field(
            name=f"Innate Talent: {chosen_talent['name']}",
            value=f"_{chosen_talent['mechanic_desc']}_",
            inline=False
        )

        # We also add the mechanic's description to the final embed for clarity
        self.final_embed.add_field(
            name="Talent Effect",
            value=chosen_talent['mechanic_desc'],
            inline=False
        )

        # Add the completed objective and the new, clear objective
        self.final_embed.add_field(
            name="✅ Quest Started",
            value="Recruitment Officer Elara has given you your first task.",
            inline=False
        )
        self.final_embed.add_field(
            name="New Objective",
            value="Use /adventure command and gather a **Sun-Kissed Berry** from the wilds.",
            inline=False
        )
        # --- END OF CORRECTED LOGIC ---

        await interaction.edit_original_response(
            content="Your companion's talent has awakened! Your adventure begins now.",
            embed=self.final_embed,
            view=None
        )
        self.stop()

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
        player_data = await db_cog.get_player(interaction.user.id)
        if player_data and player_data.get('main_pet_id'):
            return await interaction.response.send_message(
                "You have already started your adventure! Use `/adventure` to open your menu.",
                ephemeral=True
            )
        if player_data:
            username = player_data.get('username')
            gender = player_data.get('gender')
            pet_selection_view = StarterPetView(self.bot, interaction.user.id, username, gender)
            await interaction.response.send_message(
                "It seems you have not chosen a starter pet yet. Please select your first companion.",
                view=pet_selection_view,
                ephemeral=True
            )
            pet_selection_view.message = await interaction.original_response()
            return
        modal = StartModal(self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(Game(bot))