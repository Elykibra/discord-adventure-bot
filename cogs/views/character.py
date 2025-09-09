# cogs/views/character.py
import asyncio
import math
import inspect
import discord

from data.items import ITEMS
from data.skills import PET_SKILLS

# --- REFACTORED IMPORTS ---
from core.pet_system import Pet
from data.towns import TOWNS
from .crafting import CraftingView
from .inventory import BagView
from .modals import RenamePetModal
from utils.helpers import get_status_bar, get_player_rank_info, _create_progress_bar, get_pet_image_url, _pet_tuple_to_dict
from utils.constants import CREST_DATA, UNEARNED_CREST_EMOJI, RANK_DISPLAY_DATA


# (SetMainPetView and ProfileView are good as they are, so they are omitted for brevity)

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

        # --- Get all the data we need ---
        num_crests = await db_cog.count_player_crests(self.user_id)
        rank_info = get_player_rank_info(num_crests)
        rank_display = RANK_DISPLAY_DATA.get(rank_info["rank"], RANK_DISPLAY_DATA["Novice"])
        main_pet_data = await db_cog.get_pet(player_data['main_pet_id']) if player_data.get('main_pet_id') else None
        all_pets = await db_cog.get_all_pets(self.user_id)
        head_item = ITEMS.get(player_data.get('equipped_head'), {}).get('name', 'None')
        charm_item = ITEMS.get(player_data.get('equipped_charm'), {}).get('name', 'None')

        embed = discord.Embed(
            title=f"{rank_display['title_prefix']}: {player_data['username']}",
            description=rank_display['description'],
            color=rank_display['color']
        )

        # --- PLAYER'S DISCORD AVATAR ---
        # We use .display_avatar.url to ensure it always has a fallback.
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        # --- GUILD CRESTS ---
        earned_crests = await db_cog.get_player_crests(self.user_id)
        crests_display = ""
        for crest_name, emoji in CREST_DATA.items():
            crests_display += f"{emoji} " if crest_name in earned_crests else f"{UNEARNED_CREST_EMOJI} "
        embed.add_field(name="Guild Crests", value=crests_display.strip(), inline=False)

        # --- ADVENTURE STATS ---
        stats_block = (
            f"```\n"
            f"├─ Rank:        {rank_info['rank']}\n"
            f"├─ Coins:       {player_data.get('coins', 0)} 🪙\n"
            f"├─ Reputation:  {player_data.get('reputation', 0)} ✨\n"
            f"└─ Pets Owned:  {len(all_pets)}\n"
            f"```"
        )
        embed.add_field(name="Adventurer Stats", value=stats_block, inline=True)

        # --- EQUIPPED GEAR ---
        gear_info = (
            f"```\n"
            f"├─ Head:  {head_item}\n"
            f"├─ Charm: {charm_item}\n"
            f"└─ Pet Items: None\n"
            f"```"
        )
        embed.add_field(name="Equipped Gear", value=gear_info, inline=True)

        current_location_name = TOWNS.get(player_data['current_location'], {}).get('name', 'Unknown')
        current_location = f"{current_location_name}."
        embed.add_field(name="Current Location", value=f"`{current_location}`", inline=False)

        # --- MAIN PET STATUS ---
        if main_pet_data:
            pet_hp_bar = _create_progress_bar(main_pet_data['current_hp'], main_pet_data['max_hp'])
            pet_info = (
                f"**Lvl {main_pet_data['level']} {main_pet_data['species']}**\n"
                f"❤️ {pet_hp_bar} ({main_pet_data['current_hp']}/{main_pet_data['max_hp']})"
            )
            embed.add_field(name=f"Companion: {main_pet_data['name']}", value=pet_info, inline=False)

        # --- PROGRESS BAR ---
        # Get the raw progress numbers from our updated helper
        progress_current = rank_info.get('progress_current', 0)
        progress_total = rank_info.get('progress_total', 1)  # Default to 1 to avoid division by zero

        progress_percent = progress_current / progress_total if progress_total > 0 else 1

        # We'll use 15 blocks for the bar
        filled_blocks = math.floor(progress_percent * 15)
        empty_blocks = 15 - filled_blocks
        progress_bar_visual = '🟦' * filled_blocks + '⬛' * empty_blocks

        embed.add_field(
            name="Progress to Next Rank",
            value=f"{progress_bar_visual} `{progress_current}/{progress_total}`",
            inline=False
        )

        status_bar = get_status_bar(player_data, main_pet_data)
        embed.set_footer(text=status_bar)

        return embed

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(
                    content="Profile Menu timed out.",
                    view=None
                )
                await asyncio.sleep(15)
                await self.message.delete()
            except discord.NotFound:
                pass


class PetView(discord.ui.View):
    def __init__(self, bot, user_id, player_data, main_pet_data, all_pets_data):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.message = None
        self.main_pet_object = Pet(main_pet_data)
        self.all_pets_data = all_pets_data
        self.player_main_pet_id = player_data.get('main_pet_id')
        self.rebuild_ui()

    def rebuild_ui(self):
        self.clear_items()

        pet_options = [
            discord.SelectOption(label=f"{pet['name']} (Lvl {pet['level']})", value=str(pet['pet_id']),
                                 default=(pet['pet_id'] == self.main_pet_object.pet_id))
            for pet in self.all_pets_data
        ]
        pet_select = discord.ui.Select(placeholder="View a different pet...", options=pet_options, row=0)
        pet_select.callback = self.pet_select_callback
        self.add_item(pet_select)

        rename_btn = discord.ui.Button(label="Rename", style=discord.ButtonStyle.grey, row=1)
        rename_btn.callback = self.rename_button_callback

        self.add_item(rename_btn)

        is_already_main = (self.main_pet_object.pet_id == self.player_main_pet_id)
        set_main_btn = discord.ui.Button(label="Set Main Pet", style=discord.ButtonStyle.secondary, row=1,
                                         disabled=is_already_main)
        set_main_btn.callback = self.set_main_pet_button_callback
        self.add_item(set_main_btn)

    async def set_main_pet_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        db_cog = self.bot.get_cog('Database')
        await db_cog.set_main_pet(self.user_id, self.main_pet_object.pet_id)
        self.player_main_pet_id = self.main_pet_object.pet_id

        self.rebuild_ui()
        new_embed = await self.get_pet_status_embed()
        await interaction.edit_original_response(embed=new_embed, view=self)

    async def pet_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_pet_id = int(interaction.data['values'][0])
        selected_pet_data = next((p for p in self.all_pets_data if p['pet_id'] == selected_pet_id), None)
        if selected_pet_data:
            self.main_pet_object = Pet(selected_pet_data)
            self.rebuild_ui()
            new_embed = await self.get_pet_status_embed()
            await interaction.edit_original_response(embed=new_embed, view=self)

    async def rename_button_callback(self, interaction: discord.Interaction):
        modal = RenamePetModal(
            bot=self.bot,
            pet_id=self.main_pet_object.pet_id,
            old_name=self.main_pet_object.name,
            parent_view=self
        )
        await interaction.response.send_modal(modal)

    async def get_pet_status_embed(self):
        # --- main pet indicator ---
        pet = self.main_pet_object
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)

        rarity_colors = {"Starter": discord.Color.light_grey(), "Common": discord.Color.dark_grey(),
                         "Uncommon": discord.Color.green(), "Rare": discord.Color.blue(),
                         "Legendary": discord.Color.gold()}
        color = rarity_colors.get(pet.rarity, discord.Color.light_grey())

        is_main_pet = player_data.get('main_pet_id') == pet.pet_id
        indicator = "👑 " if is_main_pet else ""

        embed = discord.Embed(
            title=f"{indicator}Companion: {pet.name}",
            description=f"***`Lvl {pet.level} {pet.species}`***",
            color=color
        )
        embed.set_thumbnail(url=get_pet_image_url(pet.species))

        # --- Health and XP Bars (Full-Width) ---
        health_bar = _create_progress_bar(pet.current_hp, pet.max_hp)
        embed.add_field(name="Health", value=f"❤️ {health_bar} ({pet.current_hp}/{pet.max_hp})", inline=False)

        xp_for_next_level = pet.level * 100
        xp_bar = _create_progress_bar(pet.xp, xp_for_next_level)
        embed.add_field(name="Experience", value=f"✨ {xp_bar} ({pet.xp}/{xp_for_next_level})", inline=False)

        # Fetch charm data and include it in the details
        pet_db_data = await db_cog.get_pet(pet.pet_id) # Get fresh data to be sure
        equipped_charm_id = pet_db_data.get('equipped_charm')
        charm_name = ITEMS.get(equipped_charm_id, {}).get('name', 'None')

        # --- Pet Details (Left Column) ---
        pet_type_str = " / ".join(pet.pet_type) if isinstance(pet.pet_type, list) else pet.pet_type
        details_text = (
            f"**Rarity:** {pet.rarity}\n"
            f"**Type:** {pet_type_str}\n"
            f"**Personality:** {pet.personality}\n"
            f"**Talent:** {pet.passive_ability or 'None'}\n"
            f"**Charm:** {charm_name}"
        )
        embed.add_field(name="Details", value=details_text, inline=True)

        # --- Battle Stats (Right Column) ---
        stats_text = (
            f"**Attack:** {pet.attack}\n"
            f"**Defense:** {pet.defense}\n"
            f"**Sp. Atk:** {pet.special_attack}\n"
            f"**Sp. Def:** {pet.special_defense}\n"
            f"**Speed:** {pet.speed}"
        )
        embed.add_field(name="Base Stats", value=stats_text, inline=True)

        # --- Skills (Full-Width) ---
        skills_list = pet.skills or []
        skills_text = " | ".join([PET_SKILLS.get(s, {}).get('name', s.title()) for s in skills_list]) or "None"
        embed.add_field(name="Skills", value=skills_text, inline=False)

        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        embed.set_footer(text=get_status_bar(player_data, pet.__dict__))

        return embed

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(
                    content="Pet Menu timed out. Please run `/character` again to see your Pet.",
                    embed=None,
                    view=None
                )

                await asyncio.sleep(15)
                await self.message.delete()

            except discord.NotFound:
                # If at any point the message is not found (because the user
                # dismissed it), just ignore the error and do nothing.
                # This prevents errors from appearing in your console.
                pass

# This CharacterView now correctly loads data and passes it to the other views
class CharacterView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.message = None

    @discord.ui.button(label="Profile", emoji="👤", style=discord.ButtonStyle.primary)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        # Create an instance of the ProfileView
        profile_view = ProfileView(self.bot, self.user_id)
        # Create the embed using the view's helper method
        embed = await profile_view.get_profile_embed(interaction)

        # Send the new view and embed
        message = await interaction.followup.send(embed=embed, view=profile_view, ephemeral=True)
        profile_view.message = await interaction.original_response()

    @discord.ui.button(label="Pet", emoji="🐾", style=discord.ButtonStyle.primary)
    async def pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_data = await db_cog.get_player(self.user_id)
        if not player_data or not player_data.get('main_pet_id'):
            return await interaction.followup.send("You don't have a main pet set.", ephemeral=True)

        main_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
        all_pets_data = await db_cog.get_all_pets(self.user_id)

        view = PetView(self.bot, self.user_id, player_data, main_pet_data, all_pets_data)
        embed = await view.get_pet_status_embed()

        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = message

    @discord.ui.button(label="Bag", emoji="🎒", style=discord.ButtonStyle.primary)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        inventory_data = await db_cog.get_player_inventory(self.user_id)

        # Create an instance of the BagView
        bag_view = BagView(
            self.bot,
            self.user_id,
            player_and_pet_data['player_data'],
            player_and_pet_data['main_pet_data'], # Pass the pet data
            inventory_data
        )
        await bag_view.rebuild_ui()
        embed = bag_view.create_embed()

        message = await interaction.followup.send(embed=embed, view=bag_view, ephemeral=True)
        bag_view.message = message

    @discord.ui.button(label="Crafting", emoji="🛠️", style=discord.ButtonStyle.primary)
    async def crafting_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)

        crafting_view = CraftingView(
            self.bot,
            self.user_id,
            player_and_pet_data['player_data'],
            player_and_pet_data['main_pet_data']
        )
        await crafting_view.initial_setup()

        embed = crafting_view.create_embed()

        message = await interaction.followup.send(embed=embed, view=crafting_view, ephemeral=True)
        crafting_view.message = message

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(
                    content="Character Menu timed out. Please run `/character` again to see your character.",
                    embed=None,
                    view=None
                )

                await asyncio.sleep(15)
                await self.message.delete()

            except discord.NotFound:
                # If at any point the message is not found (because the user
                # dismissed it), just ignore the error and do nothing.
                # This prevents errors from appearing in your console.
                pass