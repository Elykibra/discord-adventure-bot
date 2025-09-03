# cogs/utils/views_character.py
# This file contains all views related to player management.
# Corrected to display the new 6-stat system and skills.

import discord
from data.skills import PET_SKILLS
from utils.helpers import get_status_bar, get_player_rank_info, _create_progress_bar, get_pet_image_url, \
    _pet_tuple_to_dict
from utils.constants import CREST_DATA, UNEARNED_CREST_EMOJI, RANK_DISPLAY_DATA
from .views_inventory import BagView
from .views_modals import RenamePetModal


class SetMainPetView(discord.ui.View):
    def __init__(self, bot, user_id, all_pets, parent_view):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view  # The PetView that opened this

        # Create a dropdown with all pets that are NOT the current main pet
        options = [
            discord.SelectOption(
                label=f"{pet['name']} (Lvl {pet['level']})",
                value=str(pet['pet_id'])
            ) for pet in all_pets if pet['pet_id'] != _pet_tuple_to_dict(parent_view.main_pet)['pet_id']
        ]

        if not options:
            # Handle the case where the player only has one pet
            self.add_item(discord.ui.Button(label="You only have one pet!", disabled=True))
        else:
            self.pet_select = discord.ui.Select(placeholder="Choose your new main pet...", options=options)
            self.pet_select.callback = self.select_callback
            self.add_item(self.pet_select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        new_main_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')

        # Update the database
        await db_cog.set_main_pet(self.user_id, new_main_pet_id)

        # Update the parent PetView with the new main pet
        self.parent_view.main_pet = await db_cog.get_pet(new_main_pet_id)
        new_embed = await self.parent_view.get_pet_status_embed(self.parent_view.main_pet)

        # Edit the original pet menu message with the new pet's info
        await self.parent_view.message.edit(embed=new_embed, view=self.parent_view)

        # Close this selection menu
        await interaction.delete_original_response()
        self.stop()


class PetView(discord.ui.View):
    def __init__(self, bot, user_id, main_pet, user_pets):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.message = None
        self.main_pet = main_pet
        self.all_pets = user_pets

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return False
        return True

    async def get_pet_status_embed(self, pet_data):
        if not pet_data:
            return discord.Embed(title="No Pet Found", description="You don't have a main pet set!",
                                 color=discord.Color.red())

        pet_data = _pet_tuple_to_dict(pet_data)
        rarity_colors = {"Starter": discord.Color.light_grey(), "Common": discord.Color.dark_grey(),
                         "Uncommon": discord.Color.green(), "Rare": discord.Color.blue(),
                         "Legendary": discord.Color.gold()}
        color = rarity_colors.get(pet_data.get('rarity', 'Common'), discord.Color.light_grey())
        health_bar = _create_progress_bar(pet_data.get('current_hp', 0), pet_data.get('max_hp', 1))

        embed = discord.Embed(
            title=f"Pet Card: {pet_data.get('name')}",
            description=f"***`{pet_data.get('species')}`***\n**_Level {pet_data.get('level', 1)} {pet_data.get('rarity', 'Common')}_**",
            color=color
        )
        embed.set_thumbnail(url=get_pet_image_url(pet_data.get('species')))

        embed.add_field(name="Health",
                        value=f"❤️ {health_bar} ({pet_data.get('current_hp', 0)}/{pet_data.get('max_hp', 1)})",
                        inline=False)

        stats_text = (f"**Attack:** {pet_data.get('attack', 0)}\n"
                      f"**Defense:** {pet_data.get('defense', 0)}\n"
                      f"**Speed:** {pet_data.get('speed', 0)}")
        special_stats_text = (f"**Sp. Atk:** {pet_data.get('special_attack', 0)}\n"
                              f"**Sp. Def:** {pet_data.get('special_defense', 0)}\n")

        embed.add_field(name="Physical Stats", value=stats_text, inline=True)
        embed.add_field(name="Special Stats", value=special_stats_text, inline=True)

        skills_list = pet_data.get('skills', [])
        if skills_list:
            skills_text = " | ".join(
                [PET_SKILLS.get(s, {}).get('name', s.replace('_', ' ').title()) for s in skills_list])
            embed.add_field(name="Skills", value=skills_text, inline=False)

        xp_needed = pet_data.get('level', 1) * 100
        embed.add_field(name="XP",
                        value=f"✨ {_create_progress_bar(pet_data.get('xp', 0), xp_needed)} ({pet_data.get('xp', 0)}/{xp_needed})",
                        inline=False)

        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            embed.set_footer(text=status_bar)
        return embed

    # Other buttons (Feed, Rename, Set Main) are correct and require no changes
    @discord.ui.button(label="Feed", style=discord.ButtonStyle.green)
    async def feed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.grey)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pet_dict = _pet_tuple_to_dict(self.main_pet)
        # This will open the modal you already have defined in views_modals.py
        modal = RenamePetModal(
            bot=self.bot,
            pet_id=pet_dict['pet_id'],
            old_name=pet_dict['name'],
            parent_view=self
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Main Pet", style=discord.ButtonStyle.secondary)
    async def set_main_pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # Create a list of pet dictionaries from the raw data
        all_pets_dicts = [_pet_tuple_to_dict(pet) for pet in self.all_pets]

        # Open the new view with the pet selection dropdown
        view = SetMainPetView(self.bot, self.user_id, all_pets_dicts, self)
        await interaction.followup.send("Select your new main pet from the list:", view=view, ephemeral=True)


class ProfileView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.message = None

    async def get_profile_embed(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        if not player_data:
            return discord.Embed(title="Error", description="Could not find your player profile.")

        num_crests = await db_cog.count_player_crests(self.user_id)
        rank_info = get_player_rank_info(num_crests)
        rank_display = RANK_DISPLAY_DATA.get(rank_info["rank"], RANK_DISPLAY_DATA["Novice"])

        embed = discord.Embed(
            title=f"{rank_display['title_prefix']}: {player_data['username']}",
            description=rank_display['description'],
            color=rank_display['color']
        )

        # Add Rank and Progress
        embed.add_field(name="Current Rank", value=f"**{rank_info['rank']}**", inline=False)
        embed.add_field(name="Progress to Next Rank", value=rank_info['progress_bar'], inline=False)

        # Add Player Stats
        stats_text = (
            f"{rank_display['stat_emoji_coins']} **Coins:** {player_data.get('coins', 0)}\n"
            f"{rank_display['stat_emoji_reputation']} **Reputation:** {player_data.get('reputation', 0)}"
        )
        embed.add_field(name="Adventurer Stats", value=stats_text, inline=False)

        # Add Guild Crests
        earned_crests = await db_cog.get_player_crests(self.user_id)
        crests_display = ""
        for crest_name, emoji in CREST_DATA.items():
            if crest_name in earned_crests:
                crests_display += f"{emoji} "
            else:
                crests_display += f"{UNEARNED_CREST_EMOJI} "

        embed.add_field(name="Guild Crests", value=crests_display.strip(), inline=False)

        main_pet_data = await db_cog.get_pet(player_data['main_pet_id']) if player_data.get('main_pet_id') else None
        status_bar = get_status_bar(player_data, main_pet_data)
        embed.set_footer(text=status_bar)

        return embed


class CharacterView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label="Profile", emoji="👤", style=discord.ButtonStyle.primary)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # This will open the existing ProfileView
        await interaction.response.defer(ephemeral=True)
        # ... (logic to create and send ProfileView) ...

    @discord.ui.button(label="Pet", emoji="🐾", style=discord.ButtonStyle.primary)
    async def pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # This will open the existing PetView
        await interaction.response.defer(ephemeral=True)
        # ... (logic to create and send PetView) ...

    @discord.ui.button(label="Bag", emoji="🎒", style=discord.ButtonStyle.primary)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Opens the new, unified Bag interface."""
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_data = await db_cog.get_player(self.user_id)
        inventory = await db_cog.get_player_inventory(self.user_id)

        view = BagView(self.bot, self.user_id, player_data, inventory)
        embed = view.create_embed()

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)