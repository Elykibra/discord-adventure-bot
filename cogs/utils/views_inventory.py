# cogs/utils/views_inventory.py
import discord
from data.items import ITEMS


class BagView(discord.ui.View):
    def __init__(self, bot, user_id, player_data, inventory):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.player_data = player_data
        self.inventory = inventory

        self.current_filter = "All"
        self.selected_item_id = None

        self.rebuild_ui()

    def rebuild_ui(self):
        """Dynamically rebuilds the view based on the current filter and selection."""
        self.clear_items()

        # --- Filter Buttons (Row 0) ---
        filters = ["All", "Consumables", "Gear", "Crafting Materials", "Key Items"]
        for f in filters:
            # Shorten the label for "Crafting Materials" to fit
            label = "Crafting" if f == "Crafting Materials" else f
            button = discord.ui.Button(label=label, style=discord.ButtonStyle.green if self.current_filter == f else discord.ButtonStyle.secondary, custom_id=f"filter_{f}")
            button.callback = self.filter_button_callback
            self.add_item(button)

        # --- Inventory Dropdown (Row 1) ---
        inventory_dict = {item['item_id']: item['quantity'] for item in self.inventory}

        options = []
        for item_id, data in ITEMS.items():
            if item_id in inventory_dict:
                category = data.get('category')
                # The filter now checks for the new categories as well
                if self.current_filter == "All" or self.current_filter == category:
                    options.append(discord.SelectOption(
                        label=f"{data['name']} (x{inventory_dict[item_id]})",
                        value=item_id
                    ))

        if options:
            dropdown = discord.ui.Select(placeholder="Select an item...", options=options, row=1)
            dropdown.callback = self.item_select_callback
            self.add_item(dropdown)
        else:
            self.add_item(discord.ui.Button(label=f"No {self.current_filter} items", disabled=True, row=1))

        # --- Context-Sensitive Action Button (Row 2) ---
        action_button = discord.ui.Button(label="Select an item", disabled=True, row=2)
        if self.selected_item_id:
            item_data = ITEMS.get(self.selected_item_id, {})
            item_category = item_data.get('category')
            slot = item_data.get('slot')

            # Check if the item is already equipped
            is_equipped = self.player_data.get(f"equipped_{slot}") == self.selected_item_id

            if item_category == "Gear":
                is_equipped = self.player_data.get(f"equipped_{item_data.get('slot')}") == self.selected_item_id
                action_button.label = f"Unequip {item_data['name']}" if is_equipped else f"Equip {item_data['name']}"
                action_button.callback = self.unequip_item_callback if is_equipped else self.equip_item_callback
                action_button.disabled = False

            elif item_category == "Consumables":
                action_button.label = f"Use {item_data['name']}"
                action_button.callback = self.use_item_callback
                action_button.disabled = False

            # Add logic for the new categories
            elif item_category in ["Crafting Materials", "Key Items"]:
                action_button.label = "View"
                action_button.disabled = True # No action for these yet

        self.add_item(action_button)

    async def filter_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_filter = interaction.data['custom_id'].replace('filter_', '')
        self.selected_item_id = None

        self.rebuild_ui()
        embed = self.create_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    async def item_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_item_id = interaction.data['values'][0]
        self.rebuild_ui()
        await interaction.edit_original_response(view=self)

    async def equip_item_callback(self, interaction: discord.Interaction):
        """Equips the selected item."""
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        item_data = ITEMS.get(self.selected_item_id, {})
        slot = item_data.get('slot')

        await db_cog.equip_item(self.user_id, self.selected_item_id, slot)

        # Refresh the player data and UI
        self.player_data = await db_cog.get_player(self.user_id)
        self.rebuild_ui()
        embed = self.create_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    async def unequip_item_callback(self, interaction: discord.Interaction):
        """Unequips the selected item."""
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        item_data = ITEMS.get(self.selected_item_id, {})
        slot = item_data.get('slot')

        # To unequip, we set the slot to None
        await db_cog.equip_item(self.user_id, None, slot)

        self.player_data = await db_cog.get_player(self.user_id)
        self.rebuild_ui()
        embed = self.create_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    async def use_item_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Using {self.selected_item_id} is not implemented yet.",
                                                ephemeral=True)

    def create_embed(self):
        """Creates the main embed for the Bag UI."""
        embed = discord.Embed(title="🎒 Bag", color=discord.Color.dark_gold())

        head_item = ITEMS.get(self.player_data.get('equipped_head'), {}).get('name', 'None')
        charm_item = ITEMS.get(self.player_data.get('equipped_charm'), {}).get('name', 'None')

        embed.add_field(
            name="👤 Adventurer Gear",
            value=f"**Head:** {head_item}\n**Charm:** {charm_item}",
            inline=False
        )
        return embed