# cogs/views/inventory.py
import discord
from data.items import ITEMS
from utils.helpers import check_quest_progress


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
        filters = ["All", "Consumables", "Gear", "Crafting Materials", "Key Items"]
        for f in filters:
            label = "Crafting" if f == "Crafting Materials" else f
            button = discord.ui.Button(label=label,
                                       style=discord.ButtonStyle.green if self.current_filter == f else discord.ButtonStyle.secondary,
                                       custom_id=f"filter_{f}")
            button.callback = self.filter_button_callback
            self.add_item(button)

        inventory_dict = {item['item_id']: item['quantity'] for item in self.inventory}
        options = []
        for item_id, data in ITEMS.items():
            if item_id in inventory_dict and (
                    self.current_filter == "All" or self.current_filter == data.get('category')):
                options.append(
                    discord.SelectOption(label=f"{data['name']} (x{inventory_dict[item_id]})", value=item_id))

        if options:
            dropdown = discord.ui.Select(placeholder="Select an item...", options=options, row=1)
            dropdown.callback = self.item_select_callback
            self.add_item(dropdown)
        else:
            self.add_item(discord.ui.Button(label=f"No {self.current_filter} items", disabled=True, row=1))

        action_button = discord.ui.Button(label="Select an item", disabled=True, row=2)
        if self.selected_item_id:
            item_data = ITEMS.get(self.selected_item_id, {})
            if item_data.get('category') == "Gear":
                is_equipped = self.player_data.get(f"equipped_{item_data.get('slot')}") == self.selected_item_id
                action_button.label = f"Unequip {item_data['name']}" if is_equipped else f"Equip {item_data['name']}"
                action_button.callback = self.unequip_item_callback if is_equipped else self.equip_item_callback
                action_button.disabled = False
            elif item_data.get('category') == "Consumables":
                action_button.label = f"Use {item_data['name']}"
                action_button.callback = self.use_item_callback
                action_button.disabled = False
        self.add_item(action_button)

    async def filter_button_callback(self, interaction: discord.Interaction):
        # ... (logic for filtering)
        pass

    async def item_select_callback(self, interaction: discord.Interaction):
        # ... (logic for item selection)
        pass

    async def equip_item_callback(self, interaction: discord.Interaction):
        # ... (logic for equipping)
        pass

    async def unequip_item_callback(self, interaction: discord.Interaction):
        # ... (logic for unequipping)
        pass

    async def use_item_callback(self, interaction: discord.Interaction):
        # ... (logic for using items, including checking quests)
        pass

    def create_embed(self):
        # ... (logic for creating the bag embed)
        pass