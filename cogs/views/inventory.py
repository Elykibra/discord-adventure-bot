# In views/inventory.py

import discord
from discord.types import embed

from data.items import ITEMS
from .modals import QuantityModal
from utils.helpers import get_notification, format_log_block, apply_effect, get_status_bar

ACTION_ORDER = ["use", "equip", "unequip", "inspect", "drop"]


class BagView(discord.ui.View):
    def __init__(self, bot, user_id, player_data, main_pet_data, inventory):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.player_data = player_data
        self.main_pet_data = main_pet_data
        self.inventory = inventory
        self.message = None
        self.current_filter = "Consumables"
        self.selected_item_id = None
        self.is_selecting_pet = False
        self.pending_action = None

    async def initial_setup(self):
        """This function will be called right after creation."""
        await self.rebuild_ui()

    def add_filter_buttons(self):
        """Rebuilds the filter buttons with the new dynamic emoji style."""
        # --- THIS IS THE FIX ---
        filters = {
            "Consumables": "🍎",
            "Gear": "🛡️",
            "Crafting Materials": "⛏️",
            "Orbs": "🔮",
            "Key Items": "🔑"
        }

        for name, emoji in filters.items():
            is_active = (self.current_filter == name)

            label = f"{emoji} {name}" if is_active else emoji
            style = discord.ButtonStyle.blurple if is_active else discord.ButtonStyle.secondary

            # Use the full name in the custom_id for the callback
            button = discord.ui.Button(label=label, style=style, custom_id=f"filter_{name}", row=0)
            button.callback = self.filter_button_callback
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your bag!", ephemeral=True)
            return False
        return True

    async def rebuild_and_edit(self, log_list: list[str] = None):
        """The single, authoritative function to refresh the view."""
        if not self.message:
            print("[DEBUG] rebuild_and_edit called but self.message is None. Aborting.")
            return

        # --- NEW: Error Handling Block ---
        try:
            db_cog = self.bot.get_cog('Database')
            self.player_data = await db_cog.get_player(self.user_id)
            self.inventory = await db_cog.get_player_inventory(self.user_id)
            if self.selected_item_id and not any(i['item_id'] == self.selected_item_id for i in self.inventory):
                self.selected_item_id = None

            await self.rebuild_ui()
            embed = self.create_embed(log_list=log_list)

            await self.message.edit(embed=embed, view=self)

        except Exception as e:
            # This will catch ANY error that happens inside the block
            # and print it to your console.
            print("--- [INVENTORY VIEW ERROR] ---")
            print(f"An error occurred in rebuild_and_edit: {e}")
            import traceback
            traceback.print_exc()
            print("------------------------------")

    async def rebuild_ui(self):
        self.clear_items()
        self.add_filter_buttons()
        self.add_item_dropdown()
        if self.is_selecting_pet:
            db_cog = self.bot.get_cog('Database')
            party_pets = [p for p in await db_cog.get_all_pets(self.user_id) if p.get('is_in_party', 1) == 1][:6]
            options = [discord.SelectOption(label=f"{p['name']} (Lvl {p['level']})", value=str(p['pet_id'])) for p in
                       party_pets]
            if options:
                placeholder = "Choose a pet to equip this on..." if self.pending_action == "equip_charm" else "Choose a pet to use this on..."
                pet_select = discord.ui.Select(placeholder=placeholder, options=options, row=2)
                pet_select.callback = self.equip_charm_on_pet_callback if self.pending_action == "equip_charm" else self.give_item_to_pet_callback
                self.add_item(pet_select)
            cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.grey, row=3)
            cancel_button.callback = self.cancel_pet_select_callback
            self.add_item(cancel_button)
        else:
            self.add_action_buttons()

    def add_item_dropdown(self):
        """Updates the dropdown logic to handle the new 'Orbs' category."""
        inventory_dict = {item['item_id']: item['quantity'] for item in self.inventory}

        options = []
        for item_id, data in ITEMS.items():
            if item_id in inventory_dict:
                # --- THIS IS THE FIX ---
                # This logic now correctly filters for Orbs and other categories.
                is_in_category = False
                category = data.get('category')

                if self.current_filter == "Orbs":
                    # Special case for Orbs, which are Consumables with orb_data
                    if category == "Consumables" and 'orb_data' in data:
                        is_in_category = True
                elif self.current_filter == "Consumables":
                    # For the main Consumables tab, we now exclude Orbs
                    if category == "Consumables" and 'orb_data' not in data:
                        is_in_category = True
                else:
                    # Standard category check for Gear, Materials, Key Items
                    if isinstance(category, list) and self.current_filter in category:
                        is_in_category = True
                    elif isinstance(category, str) and self.current_filter == category:
                        is_in_category = True

                if is_in_category:
                    options.append(
                        discord.SelectOption(
                            label=f"{data['name']} (x{inventory_dict[item_id]})",
                            value=item_id,
                            description=data.get('dropdown_description'),
                            default=(self.selected_item_id == item_id)
                        )
                    )

        if options:
            select = discord.ui.Select(placeholder="Select an item to see details...", options=options, row=1)
            select.callback = self.item_select_callback
            self.add_item(select)
        else:
            self.add_item(discord.ui.Button(label=f"No {self.current_filter} items", disabled=True, row=1))

    def create_embed(self, log_list: list[str] = None):
        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.dark_gold())
        embed.description = f"💰 **Coins:** {self.player_data.get('coins', 0)}\n"

        #Adventurer's Gear
        equipped_text = (
            f"**Head:** {ITEMS.get(self.player_data.get('equipped_head'), {}).get('name', 'None')}\n"
            f"**Tunic:** {ITEMS.get(self.player_data.get('equipped_tunic'), {}).get('name', 'None')}\n"
            f"**Boots:** {ITEMS.get(self.player_data.get('equipped_boots'), {}).get('name', 'None')}\n"
            f"**Accessory:** {ITEMS.get(self.player_data.get('equipped_accessory'), {}).get('name', 'None')}")
        embed.add_field(name="🛡️ Adventurer's Gear", value=equipped_text, inline=False)

        #Selected Item
        if self.selected_item_id:
            item_data = ITEMS.get(self.selected_item_id, {})
            quantity = next((item['quantity'] for item in self.inventory if item['item_id'] == self.selected_item_id),
                            0)

            if image_url := item_data.get("image_url"):
                embed.set_thumbnail(url=image_url)

            display_description = item_data.get('menu_description', item_data.get('description', 'No description.'))
            selected_item_text = (
                f"**{item_data.get('name', 'Unknown')} (x{quantity})**\n"
                f"_{display_description}_"
            )
            embed.add_field(name="👉 Selected Item", value=selected_item_text, inline=False)

        if log_list:
            embed.add_field(name="Activity Log", value=format_log_block(log_list), inline=False)
        if not self.selected_item_id and not log_list:
            embed.set_footer(text="Select an item from the dropdown to see its details and actions.")

        #status bar
        status_bar = get_status_bar(self.player_data, self.main_pet_data)
        embed.set_footer(text=status_bar)

        return embed

    async def filter_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_filter = interaction.data['custom_id'].split('_')[1]
        self.selected_item_id = None
        await self.rebuild_and_edit()

    async def item_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_item_id = interaction.data['values'][0]
        self.is_selecting_pet = False
        await self.rebuild_and_edit()

    async def handle_action_callback(self, interaction: discord.Interaction):
        action = interaction.data['custom_id'].split('_')[1]
        item_id = self.selected_item_id
        item_data = ITEMS.get(item_id, {})
        db_cog = self.bot.get_cog('Database')

        if (action == "use" and item_data.get('effect', {}).get('type') == 'heal_pet') or \
                (action == "equip" and item_data.get('slot') == "charm"):
            await interaction.response.defer()
            self.is_selecting_pet = True
            self.pending_action = "use_consumable" if action == "use" else "equip_charm"
            await self.rebuild_and_edit()
            return

        elif action in ["use", "drop"]:
            inv_item = next((i for i in self.inventory if i['item_id'] == item_id), None)
            max_qty = inv_item['quantity'] if inv_item else 0
            modal = QuantityModal(item_name=item_data.get('name', 'Item'), max_quantity=max_qty)
            await interaction.response.send_modal(modal)
            await modal.wait()

            quantity_to_use = modal.quantity
            log_list = []
            if quantity_to_use > 0 and quantity_to_use <= max_qty:
                if action == "use":
                    await db_cog.remove_item_from_inventory(self.user_id, item_id, quantity_to_use)
                    log_list.append(
                        get_notification("ITEM_USE_SUCCESS", quantity=quantity_to_use, item_name=item_data['name']))
                elif action == "drop":
                    await db_cog.remove_item_from_inventory(self.user_id, item_id, quantity_to_use)
                    log_list.append(
                        get_notification("ITEM_DROP_SUCCESS", quantity=quantity_to_use, item_name=item_data['name']))
            else:
                log_list.append(get_notification("ACTION_FAIL_INVALID_QUANTITY", max_quantity=max_qty))
            await self.rebuild_and_edit(log_list=log_list)
            return

        elif action in ["equip", "unequip"]:
            await interaction.response.defer()
            log_message = ""
            slot = item_data.get('slot')
            if slot:
                if action == "equip":
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": item_id})
                    log_message = get_notification("ITEM_EQUIP_SUCCESS", item_name=item_data.get('name', 'item'))
                elif action == "unequip":
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": None})
                    log_message = get_notification("ITEM_UNEQUIP_SUCCESS", item_name=item_data.get('name', 'item'))
            await self.rebuild_and_edit(log_list=[log_message])

    def add_action_buttons(self):
        if not self.selected_item_id:
            self.add_item(discord.ui.Button(label="Select an item", disabled=True, row=2))
            return
        item_data = ITEMS.get(self.selected_item_id, {})
        possible_actions = item_data.get("actions", [])
        possible_actions.sort(key=lambda action: ACTION_ORDER.index(action) if action in ACTION_ORDER else 99)
        if not possible_actions:
            self.add_item(discord.ui.Button(label="No actions available", disabled=True, row=2))
            return

        for action in possible_actions:
            button = discord.ui.Button(row=2)
            original_action = action
            if action == "use":
                button.style = discord.ButtonStyle.green
                button.label = "Give" if item_data.get('effect', {}).get('type') == 'heal_pet' else "Use"

                if 'effect' not in item_data:
                    button.disabled = True

            elif action == "drop":
                button.style = discord.ButtonStyle.red
                button.label = "Drop"
            elif action == "equip":
                slot = item_data.get('slot')
                if slot == "charm":
                    button.label = "Equip on Pet"
                    button.style = discord.ButtonStyle.blurple
                else:
                    if self.player_data.get(f"equipped_{slot}") == self.selected_item_id:
                        action = "unequip"
                        button.label = "Unequip"
                        button.style = discord.ButtonStyle.blurple
                    else:
                        button.label = "Equip"
                        button.style = discord.ButtonStyle.green
            else:  # Inspect
                button.label = action.capitalize()
                button.style = discord.ButtonStyle.secondary

            button.custom_id = f"action_{action}"
            button.callback = self.handle_action_callback
            self.add_item(button)

    async def give_item_to_pet_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        target_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')
        target_pet = await db_cog.get_pet(target_pet_id)
        log_list = []
        if target_pet:
            item_data = ITEMS.get(self.selected_item_id, {})
            healed_amount = await apply_effect(db_cog, target_pet, item_data.get('effect', {}))
            if healed_amount > 0:
                await db_cog.remove_item_from_inventory(self.user_id, self.selected_item_id, 1)
                log_list.append(
                    get_notification("ITEM_HEAL_PET_SUCCESS", pet_name=target_pet['name'], heal_amount=healed_amount))
            else:
                log_list.append(get_notification("ACTION_FAIL_PET_MAX_HP", pet_name=target_pet['name']))
        self.is_selecting_pet = False
        self.pending_action = None
        await self.rebuild_and_edit(log_list=log_list)

    async def equip_charm_on_pet_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        target_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')
        target_pet = await db_cog.get_pet(target_pet_id)
        log_list = []
        if target_pet:
            item_data = ITEMS.get(self.selected_item_id, {})
            await db_cog.update_pet(target_pet_id, equipped_charm=self.selected_item_id)
            log_list.append(get_notification(
                "PET_EQUIP_SUCCESS",
                item_name=item_data.get('name', 'charm'),
                pet_name=target_pet.get('name', 'your pet')
            ))
        else:
            log_list.append(get_notification("ACTION_FAIL_GENERIC"))

        self.is_selecting_pet = False
        self.pending_action = None
        await self.rebuild_and_edit(log_list=log_list)

    async def cancel_pet_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.is_selecting_pet = False
        self.pending_action = None
        await self.rebuild_and_edit()