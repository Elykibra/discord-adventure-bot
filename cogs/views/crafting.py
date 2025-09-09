# cogs/views/crafting.py
import discord
import asyncio

from cogs.views.modals import QuantityModal
from data.recipes import RECIPES
from data.items import ITEMS # <-- Add ITEMS import
from utils.helpers import get_status_bar, format_log_block, get_notification


class CraftingView(discord.ui.View):
    def __init__(self, bot, user_id, player_data, main_pet_data):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.player_data = player_data
        self.main_pet_data = main_pet_data
        self.message = None

        # --- State Management ---
        self.show_craftable_only = False
        self.current_discipline = "All"  # 'All', 'Forgecraft', 'Alchemy', 'Cooking'.
        self.selected_recipe_id = None

        self.known_recipes = []
        self.player_inventory = {}
        self.filtered_recipes = []

    async def initial_setup(self):
        """Fetches initial data from the database."""
        db_cog = self.bot.get_cog('Database')

        self.known_recipes = await db_cog.get_player_recipes(self.user_id)

        inventory_list = await db_cog.get_player_inventory(self.user_id)
        self.player_inventory = {item['item_id']: item['quantity'] for item in inventory_list}

        # Give the player a default recipe if they have none
        if not self.known_recipes:
            await db_cog.add_recipe_to_player(self.user_id, "trail_morsels")
            self.known_recipes = await db_cog.get_player_recipes(self.user_id)

        self.rebuild_ui()

    def create_embed(self, log_list: list[str] = None):
        embed = discord.Embed(
            title="🛠️ Recipe Book",
            description="Select a filter and then choose a recipe from the dropdown.",
            color=discord.Color.dark_orange()
        )

        # --- NEW: Smart Checklist Display ---
        if self.selected_recipe_id:
            recipe_data = RECIPES.get(self.selected_recipe_id, {})
            recipe_name = recipe_data.get("name", "Unknown")

            # It will show the image of the item you are crafting.
            crafted_item_data = ITEMS.get(self.selected_recipe_id, {})
            if image_url := crafted_item_data.get("image_url"):
                embed.set_thumbnail(url=image_url)

            # Build the checklist string
            checklist_items = []
            for ingredient_id, required in recipe_data.get("ingredients", {}).items():
                owned = self.player_inventory.get(ingredient_id, 0)
                emoji = "✅" if owned >= required else "❌"
                ingredient_name = ITEMS.get(ingredient_id, {}).get("name", "Unknown Item")
                checklist_items.append(f"{emoji} {ingredient_name}: {owned}/{required}")

            checklist_text = "\n".join(checklist_items)
            embed.add_field(name=f"Recipe: {recipe_name}", value=recipe_data.get("menu_description", ""), inline=False)
            embed.add_field(name="Required Materials", value=checklist_text, inline=False)

        if log_list:
            embed.add_field(name="Activity Log", value=format_log_block(log_list), inline=False)

        status_bar = get_status_bar(self.player_data, self.main_pet_data)
        embed.set_footer(text=status_bar)
        return embed

    def rebuild_ui(self):
        self.clear_items()

        # --- Filter Buttons (Row 0) ---
        can_craft_label = "✅ Can Craft" if self.show_craftable_only else "✅"
        can_craft_style = discord.ButtonStyle.green if self.show_craftable_only else discord.ButtonStyle.secondary
        can_craft_button = discord.ui.Button(label=can_craft_label, style=can_craft_style, custom_id="toggle_craftable",
                                             row=0)
        can_craft_button.callback = self.toggle_craftable_callback
        self.add_item(can_craft_button)

        disciplines = {"All": "All", "Forgecraft": "⚒️", "Alchemy": "🌿", "Cooking": "🍳"}
        for name, emoji in disciplines.items():
            is_active = (self.current_discipline == name)
            label = f"{emoji} {name}" if is_active and name != "All" else emoji
            style = discord.ButtonStyle.blurple if is_active else discord.ButtonStyle.secondary
            disc_button = discord.ui.Button(label=label, style=style, custom_id=f"filter_{name}", row=0)
            disc_button.callback = self.filter_discipline_callback
            self.add_item(disc_button)

        # --- Recipe Dropdown (Row 1) ---
        self.update_filtered_recipes()
        self.add_recipe_dropdown()

        # --- Craft Button (Row 2) ---
        self.add_craft_button()  # <-- NEW DYNAMIC BUTTON

    def update_filtered_recipes(self):
        self.filtered_recipes = []
        for recipe_id in self.known_recipes:
            recipe_data = RECIPES.get(recipe_id, {})
            if self.current_discipline != "All" and recipe_data.get("discipline") != self.current_discipline:
                continue
            if self.show_craftable_only:
                can_craft = True
                for ingredient, required_qty in recipe_data.get("ingredients", {}).items():
                    if self.player_inventory.get(ingredient, 0) < required_qty:
                        can_craft = False
                        break
                if not can_craft:
                    continue
            self.filtered_recipes.append(recipe_id)

    def add_recipe_dropdown(self):
        options = []
        for recipe_id in self.filtered_recipes:
            recipe_data = RECIPES.get(recipe_id, {})
            can_craft_emoji = "✅"
            for ingredient, required_qty in recipe_data.get("ingredients", {}).items():
                if self.player_inventory.get(ingredient, 0) < required_qty:
                    can_craft_emoji = "❌"
                    break
            options.append(discord.SelectOption(
                label=f"{can_craft_emoji} {recipe_data.get('name', 'Unknown Recipe')}",
                value=recipe_id,
                description=recipe_data.get('dropdown_description', ''),
                default=(self.selected_recipe_id == recipe_id)
            ))
        if options:
            dropdown = discord.ui.Select(placeholder="Select a recipe to view...", options=options, row=1)
            dropdown.callback = self.select_recipe_callback  # <-- ADDED CALLBACK
            self.add_item(dropdown)
        else:
            self.add_item(discord.ui.Button(label="No matching recipes found.", disabled=True, row=1))

    def add_craft_button(self):
        if not self.selected_recipe_id:
            self.add_item(discord.ui.Button(label="Craft", disabled=True, row=2))
            return

        recipe_data = RECIPES.get(self.selected_recipe_id, {})
        button_label = "Craft Item"
        button_disabled = False

        # Determine if the player can craft at least one
        can_craft_one = True
        for ingredient, required in recipe_data.get("ingredients", {}).items():
            if self.player_inventory.get(ingredient, 0) < required:
                can_craft_one = False
                break

        if not can_craft_one:
            button_disabled = True

        if recipe_data.get("type") == "Master":
            button_disabled = True
            discipline_emojis = {"Forgecraft": "⚒️", "Alchemy": "🌿", "Cooking": "🍳"}
            emoji = discipline_emojis.get(recipe_data.get("discipline"), "")
            button_label = f"Find a Specialist {emoji}"

        craft_button = discord.ui.Button(label=button_label, style=discord.ButtonStyle.green, disabled=button_disabled,
                                         row=2, custom_id="craft_item")
        craft_button.callback = self.craft_item_callback
        self.add_item(craft_button)

    async def _update_view(self, interaction: discord.Interaction, log_list: list[str] = None):
        """Helper function to defer, rebuild, and edit the message."""
        await interaction.response.defer()

        db_cog = self.bot.get_cog('Database')
        inventory_list = await db_cog.get_player_inventory(self.user_id)
        self.player_inventory = {item['item_id']: item['quantity'] for item in inventory_list}

        self.rebuild_ui()
        # It passes the log_list to the embed creator
        embed = self.create_embed(log_list=log_list)
        await interaction.edit_original_response(embed=embed, view=self)

    async def toggle_craftable_callback(self, interaction: discord.Interaction):
        self.show_craftable_only = not self.show_craftable_only
        self.selected_recipe_id = None  # Reset selection when filter changes
        await self._update_view(interaction)

    async def filter_discipline_callback(self, interaction: discord.Interaction):
        self.current_discipline = interaction.data['custom_id'].split('_')[1]
        self.selected_recipe_id = None  # Reset selection when filter changes
        await self._update_view(interaction)

    async def select_recipe_callback(self, interaction: discord.Interaction):
        self.selected_recipe_id = interaction.data["values"][0]
        await self._update_view(interaction)

    async def craft_item_callback(self, interaction: discord.Interaction):
        recipe_id = self.selected_recipe_id
        recipe_data = RECIPES.get(recipe_id, {})

        # --- Modal and Quantity Logic (Unchanged) ---
        max_craftable = 999
        for ingredient_id, required_qty in recipe_data.get("ingredients", {}).items():
            owned_qty = self.player_inventory.get(ingredient_id, 0)
            if required_qty > 0:
                max_craftable = min(max_craftable, owned_qty // required_qty)

        if max_craftable == 0:
            await interaction.response.send_message("You no longer have the materials to craft this item.",
                                                    ephemeral=True)
            return

        modal = QuantityModal(item_name=recipe_data.get("name", "Item"), max_quantity=max_craftable)
        await interaction.response.send_modal(modal)
        await modal.wait()
        quantity_to_craft = modal.quantity

        # --- NEW: Immersive Crafting Logic ---
        if 0 < quantity_to_craft <= max_craftable:
            db_cog = self.bot.get_cog('Database')

            # 1. Consume ingredients
            for ingredient_id, required_qty in recipe_data.get("ingredients", {}).items():
                await db_cog.remove_item_from_inventory(self.user_id, ingredient_id, required_qty * quantity_to_craft)

            # 2. Add crafted items
            await db_cog.add_item_to_inventory(self.user_id, recipe_id, quantity_to_craft)

            # 3. Animate the process log
            log_list = []
            process_keys = recipe_data.get("process_log_keys", [])

            # Disable buttons during the "animation"
            self.clear_items()
            self.add_item(discord.ui.Button(label="Crafting...", disabled=True, row=2))
            embed = self.create_embed()
            await self.message.edit(embed=embed, view=self)

            for key in process_keys:
                # Get a random notification for each key
                log_list.append(get_notification(key))
                embed = self.create_embed(log_list=log_list)
                await self.message.edit(embed=embed)
                await asyncio.sleep(1.5)

            # 4. Show the final success message and rebuild the UI
            crafted_item_name = recipe_data.get("name", "Item")
            log_list.append(get_notification(
                "CRAFT_SUCCESS",
                quantity=quantity_to_craft,
                item_name=crafted_item_name
            ))
            await self.rebuild_and_edit(log_list=log_list)

        elif quantity_to_craft > 0:
            log_list = [get_notification("ACTION_FAIL_INVALID_QUANTITY", max_quantity=max_craftable)]
            await self.rebuild_and_edit(log_list=log_list)

    async def rebuild_and_edit(self, log_list: list[str] = None):
        """A simple version that uses self.message to edit."""
        if not self.message: return

        db_cog = self.bot.get_cog('Database')
        inventory_list = await db_cog.get_player_inventory(self.user_id)
        self.player_inventory = {item['item_id']: item['quantity'] for item in inventory_list}

        self.rebuild_ui()
        embed = self.create_embed(log_list=log_list)
        await self.message.edit(embed=embed, view=self)