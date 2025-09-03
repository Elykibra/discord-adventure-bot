# cogs/views/character.py

import discord
from data.skills import PET_SKILLS

# --- REFACTORED IMPORTS ---
from core.pet_system import Pet  # <-- Import our Pet class!
from core.inventory import Bag  # <-- Import our Bag class!
from utils.helpers import get_status_bar, get_player_rank_info, _create_progress_bar, get_pet_image_url
from .inventory import BagView  # The view for the bag
from .modals import RenamePetModal


# (SetMainPetView and ProfileView are good as they are, so they are omitted for brevity)

class PetView(discord.ui.View):
    def __init__(self, bot, user_id, main_pet_data, all_pets_data):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.message = None

        # --- REFACTOR IN ACTION ---
        # 1. Create a Pet object from the raw database dictionary.
        self.main_pet = Pet(main_pet_data)

        # 2. Store the raw data for other pets for the dropdown
        self.all_pets_data = all_pets_data

    # ... (interaction_check is unchanged) ...

    async def get_pet_status_embed(self):
        pet = self.main_pet  # Use the Pet object

        rarity_colors = {"Starter": discord.Color.light_grey(), "Common": discord.Color.dark_grey(),
                         "Uncommon": discord.Color.green(), "Rare": discord.Color.blue(),
                         "Legendary": discord.Color.gold()}
        color = rarity_colors.get(pet.rarity, discord.Color.light_grey())

        health_bar = _create_progress_bar(pet.current_hp, pet.max_hp)

        embed = discord.Embed(
            # 3. Use object attributes (pet.name) instead of dictionary lookups (pet['name'])
            title=f"Pet Card: {pet.name}",
            description=f"***`{pet.species}`***\n**_Level {pet.level} {pet.rarity}_**",
            color=color
        )
        embed.set_thumbnail(url=get_pet_image_url(pet.species))

        embed.add_field(name="Health", value=f"❤️ {health_bar} ({pet.current_hp}/{pet.max_hp})", inline=False)

        stats_text = (f"**Attack:** {pet.attack}\n"
                      f"**Defense:** {pet.defense}\n"
                      f"**Speed:** {pet.speed}")
        special_stats_text = (f"**Sp. Atk:** {pet.special_attack}\n"
                              f"**Sp. Def:** {pet.special_defense}\n")

        embed.add_field(name="Physical Stats", value=stats_text, inline=True)
        embed.add_field(name="Special Stats", value=special_stats_text, inline=True)

        # ... (rest of the embed creation is the same, using pet.attribute) ...

        return embed

    # ... (The button callbacks would also be updated to create Pet and Bag objects) ...


# This CharacterView now correctly loads data and passes it to the other views
class CharacterView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label="Profile", emoji="👤", style=discord.ButtonStyle.primary)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ... (logic to create and send ProfileView) ...
        pass

    @discord.ui.button(label="Pet", emoji="🐾", style=discord.ButtonStyle.primary)
    async def pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)

        main_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
        all_pets_data = await db_cog.get_all_pets(self.user_id)

        # Pass the raw data to the view, which will create the Pet object
        view = PetView(self.bot, self.user_id, main_pet_data, all_pets_data)
        embed = await view.get_pet_status_embed()

        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = message

    @discord.ui.button(label="Bag", emoji="🎒", style=discord.ButtonStyle.primary)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ... (This would now create a Bag object) ...
        pass