import discord
from data.items import ITEMS
from .modals import QuantityModal
from utils.helpers import get_notification, format_log_block, apply_effect

ACTION_ORDER = ["use", "equip", "unequip", "inspect", "drop"]

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
        self.is_selecting_pet = False
        # The UI is now built by the command before being sent.

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your bag!", ephemeral=True)
            return False
        return True

    async def rebuild_and_edit(self, interaction: discord.Interaction, log_list: list[str] = None):
        """The single, authoritative function to refresh the view."""
        # Get fresh data
        db_cog = self.bot.get_cog('Database')
        self.player_data = await db_cog.get_player(self.user_id)
        self.inventory = await db_cog.get_player_inventory(self.user_id)
        if self.selected_item_id and not any(i['item_id'] == self.selected_item_id for i in self.inventory):
            self.selected_item_id = None

        # Rebuild the UI components based on the current state
        await self.rebuild_ui()

        # Create the embed with the new data and optional log
        embed = self.create_embed(log_list=log_list)

        # Edit the message
        await interaction.edit_original_response(embed=embed, view=self)

    # --- UI Building ---
    async def rebuild_ui(self):
        """Clears and rebuilds all components, now async to handle pet fetching."""
        self.clear_items()

        # --- Row 0 & 1: Filters and Item Dropdown (No change in their logic) ---
        self.add_filter_buttons()
        self.add_item_dropdown()

        # --- Row 2 & 3: Dynamic Action Area ---
        if self.is_selecting_pet:
            # If we are in "pet selection mode", show the pet dropdown
            db_cog = self.bot.get_cog('Database')
            all_pets = await db_cog.get_all_pets(self.user_id)

            # Filter for the 6 pets in the vanguard/party
            party_pets = [p for p in all_pets if p.get('is_in_party', 1) == 1][:6]

            options = [
                discord.SelectOption(label=f"{pet['name']} ({pet['current_hp']}/{pet['max_hp']} HP)",
                                     value=str(pet['pet_id']))
                for pet in party_pets
            ]

            if options:
                pet_select = discord.ui.Select(placeholder="Choose a pet to use this on...", options=options, row=2)
                pet_select.callback = self.give_item_to_pet_callback  # New callback
                self.add_item(pet_select)

            cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.grey, row=3)
            cancel_button.callback = self.cancel_pet_select_callback  # New callback
            self.add_item(cancel_button)
        else:
            # Otherwise, show the normal action buttons
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

    # ADD this new helper function
    def add_item_dropdown(self):
        inventory_dict = {item['item_id']: item['quantity'] for item in self.inventory}
        options = [
            discord.SelectOption(
                label=f"{data['name']} (x{inventory_dict[item_id]})",
                value=item_id,
                default=(self.selected_item_id == item_id)
            )
            for item_id, data in ITEMS.items()
            if item_id in inventory_dict and (
                            self.current_filter == "All" or self.current_filter == data.get('category'))
        ]
        if options:
            dropdown = discord.ui.Select(placeholder="Select an item to see details...", options=options, row=1)
            dropdown.callback = self.item_select_callback
            self.add_item(dropdown)
        else:
            self.add_item(discord.ui.Button(label=f"No {self.current_filter} items", disabled=True, row=1))

    # --- Embed Building ---
    def create_embed(self, log_list: list[str] = None):
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
        equipped_text = (
            f"**Head:** {head_name}\n**Tunic:** {tunic_name}\n**Boots:** {boots_name}\n**Accessory:** {accessory_name}")
        embed.add_field(name="🛡️ Adventurer's Gear", value=equipped_text, inline=False)
        if self.selected_item_id:
            item_data = ITEMS.get(self.selected_item_id, {})
            item_inv = next((item for item in self.inventory if item['item_id'] == self.selected_item_id), None)
            quantity = item_inv['quantity'] if item_inv else 0
            embed.add_field(name=f"Selected: {item_data.get('name')}",
                            value=f"_{item_data.get('description', 'No description.')}_\n**Quantity:** {quantity}",
                            inline=False)
        if log_list:
            formatted_log = format_log_block(log_list)
            embed.add_field(name="Activity Log", value=formatted_log, inline=False)
        if not self.selected_item_id and not log_list:
            embed.set_footer(text="Select an item from the dropdown to see its details and actions.")
        return embed

    # --- Callbacks ---
    async def filter_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_filter = interaction.data['custom_id'].split('_')[1]
        self.selected_item_id = None
        await self.rebuild_and_edit(interaction)

    async def item_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_item_id = interaction.data['values'][0]
        self.is_selecting_pet = False
        await self.rebuild_and_edit(interaction)

    async def handle_action_callback(self, interaction: discord.Interaction):
        action = interaction.data['custom_id'].split('_')[1]
        item_id = self.selected_item_id
        item_data = ITEMS.get(item_id, {})
        db_cog = self.bot.get_cog('Database')

        # --- Path 1: Using a healing item that requires pet selection ---
        if action == "use" and item_data.get('effect', {}).get('type') == 'heal_pet':
            self.is_selecting_pet = True  # Enter pet selection mode
            await self.rebuild_ui()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
            return

        # --- Path 2: Using a non-healing item or dropping (opens modal) ---
        elif action in ["use", "drop"]:
            inv_item = next((i for i in self.inventory if i['item_id'] == item_id), None)
            max_qty = inv_item['quantity'] if inv_item else 0
            modal = QuantityModal(item_name=item_data.get('name', 'Item'), max_quantity=max_qty)

            await interaction.response.send_modal(modal)
            await modal.wait()

            quantity_to_use = modal.quantity
            if quantity_to_use <= 0 or quantity_to_use > max_qty:
                log_message = get_notification("ACTION_FAIL_INVALID_QUANTITY")
                await self.rebuild_ui()
                embed = self.create_embed(log_list=[log_message])
                await interaction.edit_original_response(embed=embed, view=self)
                return

            log_message = ""
            if action == "use":  # This now only handles non-healing items
                for _ in range(quantity_to_use):
                    p_data = await db_cog.get_player_and_pet_data(self.user_id)
                    target = p_data.get('player_data')  # Assuming it's for the player
                    if target:
                        await apply_effect(db_cog, target, item_data['effect'])
                await db_cog.remove_item_from_inventory(self.user_id, item_id, quantity_to_use)
                log_message = get_notification("ITEM_USE_SUCCESS", quantity=quantity_to_use,
                                               item_name=item_data['name'])

            elif action == "drop":
                await db_cog.remove_item_from_inventory(self.user_id, item_id, quantity_to_use)
                log_message = get_notification("ITEM_DROP_SUCCESS", quantity=quantity_to_use,
                                               item_name=item_data['name'])

            self.player_data = await db_cog.get_player(self.user_id)
            self.inventory = await db_cog.get_player_inventory(self.user_id)
            await self.rebuild_ui()
            embed = self.create_embed(log_list=[log_message])
            await interaction.edit_original_response(embed=embed, view=self)
            return

        # --- Path 3: Equipping or Unequipping ---
        elif action in ["equip", "unequip"]:
            await interaction.response.defer()
            log_message = ""
            if action == "equip":
                slot = item_data.get('slot')
                if slot:
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": item_id})
                    log_message = get_notification("ITEM_EQUIP_SUCCESS", item_name=item_data.get('name', 'item'))

            elif action == "unequip":
                slot = item_data.get('slot')
                if slot:
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": None})
                    log_message = get_notification("ITEM_UNEQUIP_SUCCESS", item_name=item_data.get('name', 'item'))

            self.player_data = await db_cog.get_player(self.user_id)
            await self.rebuild_ui()
            embed = self.create_embed(log_list=[log_message])
            await interaction.edit_original_response(embed=embed, view=self)

    def add_action_buttons(self):
        if not self.selected_item_id:
            self.add_item(discord.ui.Button(label="Select an item", disabled=True, row=2))
            return

        item_data = ITEMS.get(self.selected_item_id, {})
        possible_actions = item_data.get("actions", [])

        # Sort the actions so they always appear in the same order
        possible_actions.sort(key=lambda action: ACTION_ORDER.index(action) if action in ACTION_ORDER else 99)

        if not possible_actions:
            self.add_item(discord.ui.Button(label="No actions available", disabled=True, row=2))
            return

        for action in possible_actions:
            button = discord.ui.Button(style=discord.ButtonStyle.secondary, row=2)

            # --- Dynamic "Use" / "Give" Button ---
            if action == "use":
                button.style = discord.ButtonStyle.green  # Make it the primary color
                effect_type = item_data.get('effect', {}).get('type')
                if effect_type == 'heal_pet':
                    button.label = "Give"
                else:
                    button.label = "Use"

            # --- Dynamic "Drop" Button ---
            elif action == "drop":
                button.style = discord.ButtonStyle.red
                button.label = "Drop"
                # Disable the drop button for Key Items
                if item_data.get("category") == "Key Items":
                    button.disabled = True

            # --- Standard Buttons ---
            else:  # For "equip", "inspect", etc.
                if action == "equip":
                    slot = item_data.get('slot')
                    is_equipped = self.player_data.get(f"equipped_{slot}") == self.selected_item_id
                    if is_equipped:
                        action = "unequip"  # Change the action itself
                        button.style = discord.ButtonStyle.blurple
                    else:
                        button.style = discord.ButtonStyle.green
                button.label = action.capitalize()

            button.custom_id = f"action_{action}"
            button.callback = self.handle_action_callback
            self.add_item(button)

    async def handle_secondary_action_callback(self, interaction: discord.Interaction):
        # This callback handles actions from the "More Actions..." dropdown
        action = interaction.data['values'][0]
        item_id = self.selected_item_id
        item_data = ITEMS.get(item_id, {})

        if action == "drop":
            inv_item = next((i for i in self.inventory if i['item_id'] == item_id), None)
            max_qty = inv_item['quantity'] if inv_item else 0

            modal = QuantityModal(
                parent_view=self,
                item_id=item_id,
                action_type=action,
                origin_message=interaction.message
            )
            await interaction.response.send_modal(modal)
            return

        elif action == "inspect":
            await interaction.response.send_message(f"You take a closer look at the {item_data.get('name', 'item')}.",
                                                    ephemeral=True)

    async def give_item_to_pet_callback(self, interaction: discord.Interaction):
        """Called when a pet is selected. Instantly uses ONE item."""
        await interaction.response.defer()

        target_pet_id = int(interaction.data['values'][0])
        item_id = self.selected_item_id
        item_data = ITEMS.get(item_id, {})
        db_cog = self.bot.get_cog('Database')

        target_pet = await db_cog.get_pet(target_pet_id)
        log_message = ""
        if target_pet:
            # 1. Try to heal the pet and get the amount healed back
            healed_amount = await apply_effect(db_cog, target_pet, item_data['effect'])

            # 2. Check if any health was actually restored
            if healed_amount > 0:
                # If successful, remove the item and create the success message
                await db_cog.remove_item_from_inventory(self.user_id, item_id, 1)
                log_message = get_notification(
                    "ITEM_HEAL_PET_SUCCESS",
                    pet_name=target_pet['name'],
                    heal_amount=healed_amount
                )
            else:
                # If no healing occurred, the pet was at max HP. Do not remove the item.
                log_message = get_notification("ACTION_FAIL_PET_MAX_HP", pet_name=target_pet['name'])

        # Return to the standard item view
        self.is_selecting_pet = False
        await self.rebuild_and_edit(interaction, log_list=[log_message])

    async def cancel_pet_select_callback(self, interaction: discord.Interaction):
        """Cancels pet selection and returns to the standard action buttons."""
        await interaction.response.defer()
        self.is_selecting_pet = False
        await self.rebuild_and_edit(interaction)