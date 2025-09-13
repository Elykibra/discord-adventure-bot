# In views/inventory.py

import discord
import json
from discord.types import embed

from data.items import ITEMS
from data.skills import PET_SKILLS
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
        await self.rebuild_ui()

    def add_filter_buttons(self):
        # This function is correct.
        filters = {"Consumables": "🍎", "Gear": "🛡️", "Crafting Materials": "⛏️", "Orbs": "🔮", "Key Items": "🔑"}
        for name, emoji in filters.items():
            is_active = (self.current_filter == name)
            label = f"{emoji} {name}" if is_active else emoji
            style = discord.ButtonStyle.blurple if is_active else discord.ButtonStyle.secondary
            button = discord.ui.Button(label=label, style=style, custom_id=f"filter_{name}", row=0)
            button.callback = self.filter_button_callback
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your bag!", ephemeral=True)
            return False
        return True

    async def rebuild_and_edit(self, log_list: list[str] = None):
        if not self.message: return
        try:
            db_cog = self.bot.get_cog('Database')
            self.player_data = await db_cog.get_player(self.user_id)
            self.inventory = await db_cog.get_player_inventory(self.user_id)

            # --- FIX: Properly check if the selected item still exists ---
            if self.selected_item_id:
                try:
                    inventory_index = int(self.selected_item_id.split(':')[0])
                    if inventory_index >= len(self.inventory):
                        self.selected_item_id = None
                except (ValueError, IndexError):
                    self.selected_item_id = None

            await self.rebuild_ui()
            embed = self.create_embed(log_list=log_list)
            await self.message.edit(embed=embed, view=self)
        except Exception as e:
            print(f"--- [INVENTORY VIEW ERROR] --- \nAn error occurred in rebuild_and_edit: {e}")
            import traceback
            traceback.print_exc()

    async def rebuild_ui(self):
        # This function is correct.
        self.clear_items()
        self.add_filter_buttons()
        self.add_item_dropdown()
        if self.is_selecting_pet:
            db_cog = self.bot.get_cog('Database')
            party_pets = [p for p in await db_cog.get_all_pets(self.user_id) if p.get('is_in_party', True)][:6]
            options = [discord.SelectOption(label=f"{p['name']} (Lvl {p['level']})", value=str(p['pet_id'])) for p in
                       party_pets]
            if options:
                if self.pending_action == "equip_charm":
                    placeholder = "Choose a pet to equip this on..."
                    callback = self.equip_charm_on_pet_callback
                elif self.pending_action == "teach_skill":
                    placeholder = "Choose a pet to teach this skill to..."
                    callback = self.teach_skill_to_pet_callback
                else:
                    placeholder = "Choose a pet to use this on..."
                    callback = self.give_item_to_pet_callback
                pet_select = discord.ui.Select(placeholder=placeholder, options=options, row=2)
                pet_select.callback = callback
                self.add_item(pet_select)
            cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.grey, row=3)
            cancel_button.callback = self.cancel_pet_select_callback
            self.add_item(cancel_button)
        else:
            self.add_action_buttons()

    def add_item_dropdown(self):
        # This function is correct.
        options = []
        for i, item_instance in enumerate(self.inventory):
            item_id = item_instance['item_id']
            quantity = item_instance['quantity']
            item_data_from_db = item_instance.get('item_data')
            base_item_data = ITEMS.get(item_id, {})
            category = base_item_data.get('category')
            display_name = base_item_data.get('name', 'Unknown')
            display_desc = base_item_data.get('dropdown_description', '')
            if item_id == 'skill_tome' and item_data_from_db:
                skill_id = item_data_from_db.get('skill')
                if skill_id:
                    skill_name = PET_SKILLS.get(skill_id, {}).get('name', 'Unknown Skill')
                    display_name = f"Tome of {skill_name}"
                    display_desc = f"Teaches the skill '{skill_name}'."
            is_in_category = False
            if self.current_filter == "Orbs":
                if category == "Consumables" and 'orb_data' in base_item_data: is_in_category = True
            elif self.current_filter == "Consumables":
                if category == "Consumables" and 'orb_data' not in base_item_data: is_in_category = True
            else:
                if isinstance(category, list) and self.current_filter in category:
                    is_in_category = True
                elif isinstance(category, str) and self.current_filter == category:
                    is_in_category = True
            if is_in_category:
                unique_value = f"{i}:{item_id}"
                options.append(
                    discord.SelectOption(label=f"{display_name} (x{quantity})", value=unique_value,
                                         description=display_desc, default=(self.selected_item_id == unique_value)))
        if options:
            select = discord.ui.Select(placeholder="Select an item to see details...", options=options, row=1)
            select.callback = self.item_select_callback
            self.add_item(select)
        else:
            self.add_item(discord.ui.Button(label=f"No {self.current_filter} items", disabled=True, row=1))

    def create_embed(self, log_list: list[str] = None):
        # This function is correct.
        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.dark_gold())
        embed.description = f"💰 **Coins:** {self.player_data.get('coins', 0)}\n"
        equipped_text = (f"**Head:** {ITEMS.get(self.player_data.get('equipped_head'), {}).get('name', 'None')}\n"
                         f"**Tunic:** {ITEMS.get(self.player_data.get('equipped_tunic'), {}).get('name', 'None')}\n"
                         f"**Boots:** {ITEMS.get(self.player_data.get('equipped_boots'), {}).get('name', 'None')}\n"
                         f"**Accessory:** {ITEMS.get(self.player_data.get('equipped_accessory'), {}).get('name', 'None')}")
        embed.add_field(name="🛡️ Adventurer's Gear", value=equipped_text, inline=False)
        if self.selected_item_id:
            try:
                inventory_index, item_id = self.selected_item_id.split(':')
                item_instance = self.inventory[int(inventory_index)]
                base_item_data = ITEMS.get(item_id, {})
                quantity = item_instance['quantity']
                display_name = base_item_data.get('name', 'Unknown')
                if item_id == 'skill_tome' and item_instance.get('item_data'):
                    skill_id = item_instance.get('item_data', {}).get('skill')
                    if skill_id:
                        skill_name = PET_SKILLS.get(skill_id, {}).get('name', 'Unknown Skill')
                        display_name = f"Tome of {skill_name}"
                if image_url := base_item_data.get("image_url"):
                    embed.set_thumbnail(url=image_url)
                display_description = base_item_data.get('menu_description',
                                                         base_item_data.get('description', 'No description.'))
                selected_item_text = f"**{display_name} (x{quantity})**\n_{display_description}_"
                embed.add_field(name="👉 Selected Item", value=selected_item_text, inline=False)
            except (ValueError, IndexError):
                self.selected_item_id = None
        if log_list:
            embed.add_field(name="Activity Log", value=format_log_block(log_list), inline=False)
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
        # This function is correct.
        action = interaction.data['custom_id'].split('_')[1]
        db_cog = self.bot.get_cog('Database')
        if not self.selected_item_id: return
        try:
            inventory_index, item_id = self.selected_item_id.split(':')
            item_instance = self.inventory[int(inventory_index)]
            base_item_data = ITEMS.get(item_id, {})
        except (ValueError, IndexError):
            return
        effect_type = base_item_data.get('effect', {}).get('type')
        if (action == "use" and effect_type in ['heal_pet', 'teach_skill', 'restore_hunger']) or \
                (action == "equip" and base_item_data.get('slot') == "charm"):
            await interaction.response.defer()
            self.is_selecting_pet = True
            if action == "equip":
                self.pending_action = "equip_charm"
            elif effect_type == 'heal_pet' or effect_type == 'restore_hunger':
                self.pending_action = "use_consumable"
            elif effect_type == 'teach_skill':
                self.pending_action = "teach_skill"
            await self.rebuild_and_edit()
            return
        elif action in ["use", "drop"]:
            max_qty = item_instance['quantity']
            modal = QuantityModal(item_name=base_item_data.get('name', 'Item'), max_quantity=max_qty)
            await interaction.response.send_modal(modal)
            await modal.wait()
            quantity_to_use = modal.quantity
            log_list = []
            if 0 < quantity_to_use <= max_qty:
                if action == "use":
                    await db_cog.remove_item_from_inventory(self.user_id, item_id, quantity_to_use,
                                                            item_instance.get('item_data'))
                    log_list.append(get_notification("ITEM_USE_SUCCESS", quantity=quantity_to_use,
                                                     item_name=base_item_data['name']))
                elif action == "drop":
                    await db_cog.remove_item_from_inventory(self.user_id, item_id, quantity_to_use,
                                                            item_instance.get('item_data'))
                    log_list.append(get_notification("ITEM_DROP_SUCCESS", quantity=quantity_to_use,
                                                     item_name=base_item_data['name']))
            else:
                log_list.append(get_notification("ACTION_FAIL_INVALID_QUANTITY", max_quantity=max_qty))
            await self.rebuild_and_edit(log_list=log_list)
            return
        elif action in ["equip", "unequip"]:
            await interaction.response.defer()
            log_message = ""
            slot = base_item_data.get('slot')
            if slot:
                if action == "equip":
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": item_id})
                    log_message = get_notification("ITEM_EQUIP_SUCCESS", item_name=base_item_data.get('name', 'item'))
                elif action == "unequip":
                    await db_cog.update_player(self.user_id, **{f"equipped_{slot}": None})
                    log_message = get_notification("ITEM_UNEQUIP_SUCCESS", item_name=base_item_data.get('name', 'item'))
            await self.rebuild_and_edit(log_list=[log_message])

    def add_action_buttons(self):
        if not self.selected_item_id:
            self.add_item(discord.ui.Button(label="Select an item", disabled=True, row=2))
            return

        # --- FIX: Parse unique ID to get correct data for buttons ---
        try:
            inventory_index, item_id = self.selected_item_id.split(':')
            base_item_data = ITEMS.get(item_id, {})
        except (ValueError, IndexError):
            self.add_item(discord.ui.Button(label="Error reading item", disabled=True, row=2))
            return

        possible_actions = base_item_data.get("actions", [])
        possible_actions.sort(key=lambda action: ACTION_ORDER.index(action) if action in ACTION_ORDER else 99)
        if not possible_actions:
            self.add_item(discord.ui.Button(label="No actions available", disabled=True, row=2))
            return
        for action in possible_actions:
            button = discord.ui.Button(row=2)
            if action == "use":
                button.style = discord.ButtonStyle.green
                button.label = "Give" if base_item_data.get('effect', {}).get('type') == 'heal_pet' else "Use"
                if 'effect' not in base_item_data:
                    button.disabled = True
            elif action == "drop":
                button.style = discord.ButtonStyle.red
                button.label = "Drop"
            elif action == "equip":
                slot = base_item_data.get('slot')
                if slot == "charm":
                    button.label = "Equip on Pet"
                    button.style = discord.ButtonStyle.blurple
                else:
                    if self.player_data.get(f"equipped_{slot}") == item_id:
                        action = "unequip"
                        button.label = "Unequip"
                        button.style = discord.ButtonStyle.blurple
                    else:
                        button.label = "Equip"
                        button.style = discord.ButtonStyle.green
            else:
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

        if target_pet and self.selected_item_id:
            # --- FIX: Parse unique ID ---
            inventory_index, item_id = self.selected_item_id.split(':')
            item_instance = self.inventory[int(inventory_index)]
            base_item_data = ITEMS.get(item_id, {})

            healed_amount = await apply_effect(db_cog, target_pet, base_item_data.get('effect', {}))
            if healed_amount > 0:
                await db_cog.remove_item_from_inventory(self.user_id, item_id, 1, item_instance.get('item_data'))
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

        if target_pet and self.selected_item_id:
            # --- FIX: Parse unique ID ---
            inventory_index, item_id = self.selected_item_id.split(':')
            base_item_data = ITEMS.get(item_id, {})

            await db_cog.update_pet(target_pet_id, equipped_charm=item_id)
            log_list.append(get_notification("PET_EQUIP_SUCCESS", item_name=base_item_data.get('name', 'charm'),
                                             pet_name=target_pet.get('name', 'your pet')))
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

    async def teach_skill_to_pet_callback(self, interaction: discord.Interaction):
        # This function is correct.
        await interaction.response.defer()
        target_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')
        target_pet = await db_cog.get_pet(target_pet_id)
        log_list = []
        if target_pet and self.selected_item_id:
            inventory_index, item_id = self.selected_item_id.split(':')
            tome_instance = self.inventory[int(inventory_index)]
            skill_id_to_learn = tome_instance.get('item_data', {}).get('skill')
            if skill_id_to_learn:
                await db_cog.add_skill_to_library(target_pet_id, skill_id_to_learn)
                await db_cog.remove_item_from_inventory(self.user_id, item_id, 1, tome_instance.get('item_data'))
                skill_name = PET_SKILLS.get(skill_id_to_learn, {}).get('name', 'a new skill')
                log_list.append(f"Success! **{target_pet['name']}** has learned **{skill_name}**.")
            else:
                log_list.append("Error: This tome seems to be blank.")
        else:
            log_list.append(get_notification("ACTION_FAIL_GENERIC"))
        self.is_selecting_pet = False
        self.pending_action = None
        await self.rebuild_and_edit(log_list=log_list)