# cogs/views/inventory.py
import discord
from data.items import ITEMS
from utils.helpers import check_quest_progress, apply_effect


# --- The Modal for Quantity Input ---
class QuantityModal(discord.ui.Modal):
    def __init__(self, parent_view, item_id, action_type):
        self.parent_view = parent_view
        self.item_id = item_id
        self.action_type = action_type  # "use" or "drop"
        self.item_data = ITEMS.get(item_id, {})
        self.inventory_item = next((i for i in parent_view.inventory if i['item_id'] == item_id), None)
        self.max_quantity = self.inventory_item['quantity'] if self.inventory_item else 0

        super().__init__(title=f"{action_type.capitalize()} {self.item_data.get('name')}")

        self.quantity_input = discord.ui.TextInput(
            label=f"Amount to {self.action_type} (Max: {self.max_quantity})",
            placeholder="Enter a number...",
            required=True
        )
        self.add_item(self.quantity_input)

    async def on_submit(self, interaction: discord.Interaction):
        # First, validate the input
        try:
            quantity = int(self.quantity_input.value)
            if not (1 <= quantity <= self.max_quantity):
                # We use send_message here because the modal is still open
                await interaction.response.send_message(
                    f"Invalid amount. Please enter a number between 1 and {self.max_quantity}.", ephemeral=True,
                    delete_after=5)
                return
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True, delete_after=5)
            return

        # --- THIS IS THE FIX ---
        # Instead of sending a message, just defer silently.
        await interaction.response.defer()
        # --- END OF FIX ---

        db_cog = self.parent_view.bot.get_cog('Database')

        if self.action_type == "use":
            for _ in range(quantity):
                p_data = await db_cog.get_player_and_pet_data(self.parent_view.user_id)
                target = p_data.get('main_pet_data') if self.item_data['effect']['type'] == 'heal_pet' else p_data.get(
                    'player_data')
                await apply_effect(db_cog, target, self.item_data['effect'])

            await db_cog.remove_item_from_inventory(self.parent_view.user_id, self.item_id, quantity)
            await interaction.followup.send(f"Used {quantity}x {self.item_data['name']}.", ephemeral=True)

        elif self.action_type == "drop":
            await db_cog.remove_item_from_inventory(self.parent_view.user_id, self.item_id, quantity)
            await interaction.followup.send(f"You dropped {quantity}x {self.item_data['name']}.", ephemeral=True)

        await self.parent_view.update_message()


class BagView(discord.ui.View):
    def __init__(self, bot, user_id, player_data, inventory):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.player_data = player_data
        self.inventory = inventory
        self.message = None
        self.current_filter = "All"
        self.selected_item_id = None
        self.rebuild_ui()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your bag!", ephemeral=True)
            return False
        return True

    def create_embed(self):
        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.dark_gold())
        embed.description = f"💰 **Coins:** {self.player_data.get('coins', 0)} | ✨ **Reputation:** {self.player_data.get('reputation', 0)}"
        equipped_head_id = self.player_data.get('equipped_head')
        equipped_tunic_id = self.player_data.get('equipped_tunic')
        equipped_boots_id = self.player_data.get('equipped_boots')
        equipped_accessory_id = self.player_data.get('equipped_accessory')
        head_name = ITEMS.get(equipped_head_id, {}).get('name', 'None')
        tunic_name = ITEMS.get(equipped_tunic_id, {}).get('name', 'None')
        boots_name = ITEMS.get(equipped_boots_id, {}).get('name', 'None')
        accessory_name = ITEMS.get(equipped_accessory_id, {}).get('name', 'None')
        equipped_text = (f"**Head:** {head_name}\n"
                         f"**Tunic:** {tunic_name}\n"
                         f"**Boots:** {boots_name}\n"
                         f"**Accessory:** {accessory_name}")
        embed.add_field(name="🛡️ Adventurer's Gear", value=equipped_text, inline=False)
        if self.selected_item_id:
            item_data = ITEMS.get(self.selected_item_id, {})
            item_inv = next((item for item in self.inventory if item['item_id'] == self.selected_item_id), None)
            quantity = item_inv['quantity'] if item_inv else 0
            embed.add_field(name=f"Selected: {item_data.get('name')}",
                            value=f"_{item_data.get('description', 'No description.')}_\n**Quantity:** {quantity}",
                            inline=False)
        else:
            embed.set_footer(text="Select an item from the dropdown to see its details and actions.")
        return embed

    def rebuild_ui(self):
        self.clear_items()
        self.add_filter_buttons()
        self.add_item_dropdown()
        self.add_action_buttons()

    def add_filter_buttons(self):
        filters = ["All", "Consumables", "Gear", "Crafting Materials", "Key Items"]
        for f in filters:
            label = "Crafting" if f == "Crafting Materials" else f
            button = discord.ui.Button(label=label,
                                       style=discord.ButtonStyle.green if self.current_filter == f else discord.ButtonStyle.secondary,
                                       custom_id=f"filter_{f}")
            button.callback = self.filter_button_callback
            self.add_item(button)

    def add_item_dropdown(self):
        inventory_dict = {item['item_id']: item['quantity'] for item in self.inventory}
        options = [discord.SelectOption(label=f"{data['name']} (x{inventory_dict[item_id]})", value=item_id) for
                   item_id, data in ITEMS.items() if item_id in inventory_dict and (
                               self.current_filter == "All" or self.current_filter == data.get('category'))]
        if options:
            dropdown = discord.ui.Select(placeholder="Select an item to see details...", options=options, row=1)
            dropdown.callback = self.item_select_callback
            self.add_item(dropdown)
        else:
            self.add_item(discord.ui.Button(label=f"No {self.current_filter} items", disabled=True, row=1))

    def add_action_buttons(self):
        if not self.selected_item_id:
            self.add_item(discord.ui.Button(label="Select an item", disabled=True, row=2))
            return
        item_data = ITEMS.get(self.selected_item_id, {})
        possible_actions = item_data.get("actions", [])
        if not possible_actions:
            self.add_item(discord.ui.Button(label="No actions available", disabled=True, row=2))
            return
        for action in possible_actions:
            button = discord.ui.Button(style=discord.ButtonStyle.blurple, row=2)
            if action == "equip":
                slot = item_data.get('slot')
                is_equipped = self.player_data.get(f"equipped_{slot}") == self.selected_item_id
                button.label = "Unequip" if is_equipped else "Equip"
                button.custom_id = f"action_{'unequip' if is_equipped else 'equip'}"
            else:
                button.label = action.capitalize()
                button.custom_id = f"action_{action}"
            button.callback = self.handle_action_callback
            self.add_item(button)

    async def refresh_and_edit(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('Database')
        self.player_data = await db_cog.get_player(self.user_id)
        self.inventory = await db_cog.get_player_inventory(self.user_id)
        if self.selected_item_id and not any(i['item_id'] == self.selected_item_id for i in self.inventory):
            self.selected_item_id = None
        self.rebuild_ui()
        embed = self.create_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    async def filter_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_filter = interaction.data['custom_id'].split('_')[1]
        self.selected_item_id = None
        await self.refresh_and_edit(interaction)

    async def item_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_item_id = interaction.data['values'][0]
        await self.refresh_and_edit(interaction)

        # Add this entire function to your BagView class
        async def handle_action_callback(self, interaction: discord.Interaction):
            """Single handler for all action buttons."""
            action = interaction.data['custom_id'].split('_')[1]
            item_id = self.selected_item_id
            item_data = ITEMS.get(item_id, {})

            if action in ["use", "drop"]:
                modal = QuantityModal(parent_view=self, item_id=item_id, action_type=action)
                await interaction.response.send_modal(modal)
                return

            await interaction.response.defer()
            db_cog = self.bot.get_cog('Database')

            if action == "equip":
                slot = item_data.get('slot')
                if slot:
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": item_id})
                    await interaction.followup.send(f"You equipped the **{item_data['name']}**.", ephemeral=True,
                                                    delete_after=3)
            elif action == "unequip":
                slot = item_data.get('slot')
                if slot:
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": None})
                    await interaction.followup.send(f"You unequipped the **{item_data['name']}**.", ephemeral=True,
                                                    delete_after=3)

            await self.update_message()

    # --- THIS IS THE MISSING FUNCTION ---
    async def handle_action_callback(self, interaction: discord.Interaction):
        """Single handler for all action buttons."""
        action = interaction.data['custom_id'].split('_')[1]
        item_id = self.selected_item_id
        item_data = ITEMS.get(item_id, {})

        if action in ["use", "drop"]:
            modal = QuantityModal(parent_view=self, item_id=item_id, action_type=action)
            await interaction.response.send_modal(modal)
            return

        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')

        if action == "equip":
            slot = item_data.get('slot')
            if slot:
                await db_cog.update_player(self.user_id, **{f"equipped_{slot}": item_id})
                await interaction.followup.send(f"You equipped the **{item_data['name']}**.", ephemeral=True,
                                                delete_after=3)  # <-- Add delete_after
        elif action == "unequip":
            slot = item_data.get('slot')
            if slot:
                await db_cog.update_player(self.user_id, **{f"equipped_{slot}": None})
                await interaction.followup.send(f"You unequipped the **{item_data['name']}**.", ephemeral=True,
                                                delete_after=3)  # <-- Add delete_after

        await self.update_message()