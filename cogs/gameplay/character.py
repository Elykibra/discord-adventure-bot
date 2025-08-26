# --- cogs/gameplay/character.py (Updated to v4.2.0) ---
import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.helpers import check_quest_progress

# --- REFACTORING FIX ---
# This section now imports from the correct files and no longer causes the error.
from data.items import ITEMS
from cogs.utils.constants import ITEM_CATEGORIES
from cogs.utils.views_character import ProfileView, PetView
from cogs.utils.helpers import get_status_bar


# A new, dynamic view for the player's inventory.
class InventoryView(discord.ui.View):
    """
    A dynamic view for the player's inventory that displays items in
    separate dropdowns based on their category.
    """

    def __init__(self, bot, user_id, inventory, player_data):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.inventory = inventory  # Full inventory list from DB
        self.player_data = player_data
        self.message = None
        self.current_item_id = None  # To track the selected item

        # Organize inventory by category
        self.categorized_items = self._categorize_inventory()
        # Build the initial UI with dropdowns and no buttons
        self._build_ui()

    def _categorize_inventory(self):
        """Sorts the player's inventory into the defined item categories."""
        categorized = {category: [] for category in ITEM_CATEGORIES.keys()}
        # The inventory from the DB is now a list of dicts, e.g., [{'item_id': 'potion', 'quantity': 5}]
        inventory_dict = {item['item_id']: item['quantity'] for item in self.inventory}

        for item_id, item_data in ITEMS.items():
            if item_id in inventory_dict and inventory_dict[item_id] > 0:
                item_category = item_data.get("category")
                if item_category in categorized:
                    categorized[item_category].append({
                        "id": item_id,
                        "name": item_data["name"],
                        "quantity": inventory_dict[item_id]
                    })
        return categorized

    def _build_ui(self):
        """Dynamically creates dropdowns for each category and action buttons."""
        self.clear_items()

        # Create a dropdown for each category that has items
        for category, items in self.categorized_items.items():
            if not items:
                continue  # Skip creating a dropdown for empty categories

            # Set the default selected option if an item from this category is chosen
            options = [
                discord.SelectOption(
                    label=f"{item['name']} (x{item['quantity']})",
                    value=item['id'],
                    default=self.current_item_id == item['id']
                ) for item in items
            ]

            select = discord.ui.Select(
                placeholder=f"Select from {category}...",
                options=options,
                custom_id=f"select_{category.replace(' ', '_')}"
            )
            select.callback = self.on_item_select
            self.add_item(select)

        # Add a contextual button if an item is selected
        if self.current_item_id:
            item_data = ITEMS.get(self.current_item_id)
            category = item_data.get("category")

            action_button = None
            if category == "Consumables":
                action_button = discord.ui.Button(label="Use", style=discord.ButtonStyle.green, custom_id="use_item")
                action_button.callback = self.on_use_item
            elif category == "Gear":
                action_button = discord.ui.Button(label="Equip", style=discord.ButtonStyle.blurple,
                                                  custom_id="equip_item")
                # action_button.callback = self.on_equip_item # Future implementation
                action_button.disabled = True  # Disable until logic is added
            elif category == "Crafting Materials" or category == "Key Items":
                action_button = discord.ui.Button(label="View", style=discord.ButtonStyle.secondary, disabled=True)

            if action_button:
                self.add_item(action_button)

    async def on_item_select(self, interaction: discord.Interaction):
        """Callback for when an item is selected from any dropdown."""
        await interaction.response.defer()

        self.current_item_id = interaction.data["values"][0]

        self._build_ui()

        embed = self._create_item_embed()
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)

    async def on_use_item(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Defer immediately

        if not self.current_item_id:
            return await interaction.followup.send("No item selected!", ephemeral=True)

        item_id = self.current_item_id
        item_name = ITEMS[item_id]['name']
        db_cog = self.bot.get_cog('Database')

        messages_to_send = []
        effect_applied = False

        player_data = await db_cog.get_player(self.user_id)
        if item_id == 'sun_kissed_berries':
            max_energy = player_data['max_energy']
            new_energy = min(max_energy, player_data['current_energy'] + 25)
            await db_cog.update_player(self.user_id, current_energy=new_energy)
            messages_to_send.append(f"You ate the {item_name} and restored 25 energy!")
            effect_applied = True

        # (Add other item effects like potions here in the future)

        if not effect_applied:
            return await interaction.followup.send(f"You can't use the {item_name} right now.", ephemeral=True)

        # --- Consume Item & Check Quests ---
        await db_cog.remove_item_from_inventory(self.user_id, item_id, 1)

        # THE FIX: Call the smarter engine and add its message to our list
        quest_updates = await check_quest_progress(self.bot, self.user_id, "item_use", {"item_id": item_id})
        if quest_updates:
            messages_to_send.extend(quest_updates)

        # --- NEW: Assemble and send a single, clean embed ---
        full_description = "\n\n".join(messages_to_send)
        final_embed = discord.Embed(
            description=full_description,
            color=discord.Color.green()  # You can choose any color
        )
        await interaction.followup.send(embed=final_embed, ephemeral=True)
        # --- END OF NEW LOGIC ---

        # --- Refresh the Inventory View ---
        self.inventory = await db_cog.get_player_inventory(self.user_id)
        self.categorized_items = self._categorize_inventory()

        item_still_exists = any(item['id'] == item_id for cat in self.categorized_items.values() for item in cat)
        if not item_still_exists:
            self.current_item_id = None

        self._build_ui()
        new_embed = self._create_item_embed()
        await interaction.edit_original_response(embed=new_embed, view=self)

    def _create_initial_embed(self):
        """Creates the default embed shown when first opening the inventory."""
        status_bar = get_status_bar(self.player_data, None)
        embed = discord.Embed(
            title="🎒 Inventory",
            description="Select an item from a dropdown to see its details and available actions.",
            color=discord.Color.dark_orange()
        )
        embed.set_footer(text=status_bar)
        return embed

    def _create_item_embed(self):
        """Creates an embed showing the details of the currently selected item."""
        if not self.current_item_id:
            return self._create_initial_embed()

        item_data = ITEMS[self.current_item_id]
        quantity = next((item['quantity'] for cat_items in self.categorized_items.values() for item in cat_items if
                         item['id'] == self.current_item_id), 0)

        embed = discord.Embed(
            title=f"{item_data['name']} (x{quantity})",
            description=item_data['description'],
            color=discord.Color.dark_orange()
        )
        embed.add_field(name="Category", value=item_data['category'], inline=True)
        embed.add_field(name="Sell Price", value=f"{item_data['price']} Gold", inline=True)

        status_bar = get_status_bar(self.player_data, None)
        embed.set_footer(text=status_bar)
        return embed


# A view for all profile-related commands. This is shown after clicking the main 'Character' button.
class CharacterView(discord.ui.View):
    def __init__(self, bot, user_id, player_data, main_pet_data):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.message = None
        self.player_data = player_data
        self.main_pet_data = main_pet_data

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

    @discord.ui.button(label="Profile", style=discord.ButtonStyle.blurple)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            view = ProfileView(self.bot, interaction.user.id)
            profile_embed = await view.get_profile_embed(interaction)
            await interaction.followup.send(embed=profile_embed, view=view, ephemeral=True)
            view.message = await interaction.original_response()
        except Exception as e:
            print(f"ERROR: An error occurred while fetching profile data: {e}")
            await interaction.followup.send(
                "An error occurred while fetching your profile. Please try again later.", ephemeral=True)

    @discord.ui.button(label="Pet", style=discord.ButtonStyle.blurple)
    async def pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            db_cog = self.bot.get_cog('Database')
            if not db_cog:
                return await interaction.followup.send("Database not loaded. Please contact an administrator.")

            main_pet_id = await db_cog.get_main_pet_id(self.user_id)
            user_pets = await db_cog.get_all_pets(self.user_id)

            if not user_pets:
                return await interaction.followup.send(
                    "You have no pets yet! You will get one from your first adventure!",
                    ephemeral=True
                )

            if not main_pet_id:
                first_pet_id = user_pets[0]['pet_id']
                await db_cog.set_main_pet(self.user_id, first_pet_id)
                main_pet_id = first_pet_id

            main_pet = await db_cog.get_pet(main_pet_id) if main_pet_id else None

            if not main_pet:
                return await interaction.followup.send(
                    "Could not find a main pet. Please contact an administrator.",
                    ephemeral=True
                )

            view = PetView(self.bot, self.user_id, main_pet, user_pets)
            embed = await view.get_pet_status_embed(main_pet)

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            view.message = await interaction.original_response()

        except Exception as e:
            print(f"ERROR: An unexpected error occurred in pet_button: {e}")
            await interaction.followup.send(
                "An unexpected error occurred. Please try again or contact an administrator.",
                ephemeral=True
            )

    @discord.ui.button(label="Inventory", style=discord.ButtonStyle.blurple)
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.followup.send("Database not loaded. Please contact an administrator.",
                                                   ephemeral=True)

        player_data = await db_cog.get_player(self.user_id)
        if not player_data:
            return await interaction.followup.send("You haven't started your adventure! Use `/start` to begin.",
                                                   ephemeral=True)

        inventory = await db_cog.get_player_inventory(interaction.user.id)
        if not inventory:
            return await interaction.followup.send("Your inventory is empty. Go on an adventure to find items!",
                                                   ephemeral=True)

        view = InventoryView(self.bot, self.user_id, inventory, player_data)
        embed = view._create_initial_embed()

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

    @discord.ui.button(label="Journal", style=discord.ButtonStyle.green, row=1)
    async def journal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # We will get the Quests cog and call its journal command logic directly
        quests_cog = self.bot.get_cog('Quests')
        if quests_cog:
            # This reuses the logic from your /journal command
            await quests_cog.journal(interaction)
        else:
            await interaction.followup.send("Error: Quests system not available.", ephemeral=True)
    # --- END OF NEW BUTTON ---


class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='character',
                          description='Opens a menu for all character-related commands (profile, pet, inventory).')
    async def character_menu(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await interaction.response.send_message(
                "Database is not loaded. Please contact an administrator.",
                ephemeral=True
            )

        player_and_pet_data = await db_cog.get_player_and_pet_data(interaction.user.id)
        if not player_and_pet_data:
            return await interaction.response.send_message(
                "You have not started your adventure yet! Use `/start` to begin.",
                ephemeral=True
            )

        player_data = player_and_pet_data['player_data']
        main_pet_data = player_and_pet_data['main_pet_data']

        status_bar = get_status_bar(player_data, main_pet_data)

        embed = discord.Embed(
            title="👤 The Character Menu",
            description="Welcome to the Character menu! Please select an option:",
            color=discord.Color.blue()
        )
        embed.set_footer(text=status_bar)

        view = CharacterView(self.bot, interaction.user.id, player_data, main_pet_data)
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )
        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(Character(bot))