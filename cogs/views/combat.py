# cogs/views/combat.py
import asyncio
import traceback
import discord
import math

# --- REFACTORED IMPORTS ---
from core.battle_engine import BattleState
from utils.helpers import get_pet_image_url, get_status_bar, _create_progress_bar, check_quest_progress, \
    get_type_multiplier, _pet_tuple_to_dict, format_log_block
from .towns import WildsView, TownView # Assuming views_towns.py is renamed to towns.py in this folder
from data.items import ITEMS
from data.skills import PET_SKILLS
from utils.constants import TYPE_EMOJIS

class CombatView(discord.ui.View):
    def __init__(self, bot, user_id, player_pet, wild_pet, message, parent_interaction, origin_location_id, view_context=None):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.message = message
        self.parent_interaction = parent_interaction
        self.origin_location_id = origin_location_id
        # This correctly creates an instance of our core battle engine
        self.battle = BattleState(bot, user_id, player_pet, wild_pet)
        self.view_context = view_context

        # --- STATE MANAGEMENT ---
        self.current_menu = "fight"
        self.selected_item_id = None
        self.selected_pet_to_switch = None
        self.battle_log = ""
        self.is_processing = False

        self.bot.loop.create_task(self.initial_setup())
        self.view_context = view_context

    async def initial_setup(self):
        """Builds the initial UI and sends the first embed."""
        self.battle_log = f"A wild Level {self.battle.wild_pet['level']} **{self.battle.wild_pet['species']}** appeared!"
        await self._update_display()

        # --- UI BUILDING LOGIC ---
    async def rebuild_ui(self):
        """Dynamically rebuilds the entire view based on the current state."""
        self.clear_items()

        # --- TOP ROW: Dynamic Components ---
        if self.current_menu == "fight":
            for skill_id in self.battle.player_pet.get("skills", ["scratch"])[:4]:
                skill_info = PET_SKILLS.get(skill_id, {})
                skill_button = discord.ui.Button(label=skill_info.get('name', 'Unknown'), style=discord.ButtonStyle.secondary, custom_id=f"skill_{skill_id}")
                skill_button.callback = self.skill_button_callback
                self.add_item(skill_button)

        elif self.current_menu == "bag":
            inventory = await self.battle.db_cog.get_player_inventory(self.user_id)
            usable_items = [{'id': i['item_id'], 'name': ITEMS[i['item_id']]['name'], 'quantity': i['quantity']} for
                                i in inventory if ITEMS.get(i['item_id'], {}).get('category') == 'Consumables']
            if usable_items:
                options = [
                    discord.SelectOption(
                            label=f"{item['name']} (x{item['quantity']})",
                            value=item['id'],
                            description=ITEMS[item['id']].get('description', '')[:100]  # Add item description
                    ) for item in usable_items
                ]
                item_dropdown = discord.ui.Select(placeholder="Select an item to use...", options=options)
                item_dropdown.callback = self.item_select_callback
                self.add_item(item_dropdown)
            else:
                self.add_item(discord.ui.Button(label="Your bag is empty!", disabled=True))

        elif self.current_menu == "switch":
            all_pets = await self.battle.db_cog.get_all_pets(self.user_id)
            available_pets = [_pet_tuple_to_dict(p) for p in all_pets if _pet_tuple_to_dict(p)['pet_id'] != self.battle.player_pet['pet_id'] and _pet_tuple_to_dict(p)['current_hp'] > 0]
            if available_pets:
                # --- THIS IS THE FIX for PETS ---
                options = [
                    discord.SelectOption(
                        label=f"{pet['name']} (Lvl {pet['level']})",
                        value=str(pet['pet_id']),
                        description=f"HP: {pet['current_hp']}/{pet['max_hp']} | Status: None" # Add HP/Status
                    ) for pet in available_pets
                ]
                # --- END OF FIX ---
                pet_dropdown = discord.ui.Select(placeholder="Select a pet to switch to...", options=options)
                pet_dropdown.callback = self.pet_select_callback
                self.add_item(pet_dropdown)
            else:
                self.add_item(discord.ui.Button(label="No other pets to switch to!", disabled=True))

        # --- CONFIRMATION BUTTONS ---
        if self.current_menu == "bag" and self.selected_item_id:
            use_item_button = discord.ui.Button(label=f"Use {ITEMS[self.selected_item_id]['name']}", style=discord.ButtonStyle.blurple, row=1)
            use_item_button.callback = self.use_item_callback
            self.add_item(use_item_button)

        if self.current_menu == "switch" and self.selected_pet_to_switch:
            confirm_switch_button = discord.ui.Button(label="Confirm Switch", style=discord.ButtonStyle.blurple, row=1)
            confirm_switch_button.callback = self.confirm_switch_callback
            self.add_item(confirm_switch_button)

        # --- BOTTOM ROW: Main Action Buttons ---
        fight_button = discord.ui.Button(label="Fight", emoji="⚔️", style=discord.ButtonStyle.green if self.current_menu == 'fight' else discord.ButtonStyle.grey, row=4, custom_id="main_fight")
        fight_button.callback = self.main_button_callback
        self.add_item(fight_button)

        bag_button = discord.ui.Button(label="Bag", emoji="🎒", style=discord.ButtonStyle.green if self.current_menu == 'bag' else discord.ButtonStyle.grey, row=4, custom_id="main_bag")
        bag_button.callback = self.main_button_callback
        self.add_item(bag_button)

        switch_button = discord.ui.Button(label="Switch Pet", emoji="🐾", style=discord.ButtonStyle.green if self.current_menu == 'switch' else discord.ButtonStyle.grey, row=4, custom_id="main_switch")
        switch_button.callback = self.main_button_callback
        self.add_item(switch_button)

        flee_button = discord.ui.Button(label="Flee", emoji="🏃", style=discord.ButtonStyle.grey, row=4, custom_id="flee")
        flee_button.callback = self.flee_button_callback
        self.add_item(flee_button)

    async def _update_display(self, interaction: discord.Interaction = None, log: str = None):
        """A single, reliable function to update the entire view and embed."""
        if interaction and not interaction.response.is_done():
            await interaction.response.defer()

        if log:
            self.battle_log = log

        await self.rebuild_ui()
        embed = await self.get_battle_embed(preview_orb_id=self.selected_item_id)
        await self.message.edit(embed=embed, view=self)

    async def main_button_callback(self, interaction: discord.Interaction):
        action = interaction.data['custom_id']
        if action == 'main_fight': self.current_menu = 'fight'
        elif action == 'main_bag': self.current_menu = 'bag'
        elif action == 'main_switch': self.current_menu = 'switch'
        self.selected_item_id, self.selected_pet_to_switch = None, None
        await self._update_display(interaction)

    async def item_select_callback(self, interaction: discord.Interaction):
        """Callback for when an item is chosen from the bag dropdown."""
        self.selected_item_id = interaction.data['values'][0]
        await self._update_display(interaction)

    async def pet_select_callback(self, interaction: discord.Interaction):
        """Callback for when a pet is chosen from the switch dropdown."""
        self.selected_pet_to_switch = int(interaction.data['values'][0])
        await self._update_display(interaction)

    async def use_item_callback(self, interaction: discord.Interaction):
        """Handles using an item (including orbs)."""

        item_data = ITEMS.get(self.selected_item_id, {})
        gloom_effect_data = item_data.get('orb_data', {}).get('gloom_effect')

        if gloom_effect_data and self.battle.wild_pet.get('is_gloom_touched'):
            reduction = gloom_effect_data.get('reduction', 0)
            await self.battle.reduce_gloom(reduction)
            self.battle_log += f"\n> The **{item_data.get('name')}** unleashes a purifying light! (Gloom -{reduction}%)"

        if 'orb' in self.selected_item_id:
            await self.attempt_capture(interaction, self.selected_item_id)
        else:
            await interaction.response.send_message(f"Using {self.selected_item_id} is not implemented yet.",
                                                    ephemeral=True)

    async def _update_view(self, interaction: discord.Interaction, results: dict):
        """This function handles updates AFTER a turn is processed."""
        if not results.get("is_over"):
            new_log = results['log'] + "\n\n> **It's your turn!**"

            # --- THIS IS THE FIX ---
            # We must pass the interaction object to the helper.
            await self._update_display(interaction, log=new_log)
            # --- END OF FIX ---
        else:
            if results.get("win"):
                await self._handle_win(results)
            else:
                await self._handle_loss(results)

    async def skill_button_callback(self, interaction: discord.Interaction):
        # 1. Check if an action is already being processed.
        if self.is_processing:
            await interaction.response.send_message("Processing... Please wait.", ephemeral=True, delete_after=3)
            return

        # Use a try...finally block to GUARANTEE the view is unlocked at the end.
        try:
            # 2. Lock the view and disable buttons visually.
            self.is_processing = True
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)

            # 3. Process the game logic.
            results = await self.battle.process_round(interaction.data['custom_id'].replace('skill_', ''))

            # 4. Update the view with the results.
            # The _update_display() or _handle_win() will re-enable buttons or change the view.
            self.battle_log = results['log']
            if not results.get("is_over"):
                self.battle_log += "\n\n> **It's your turn!**"
                await self._update_display()
            else:
                if results.get("win"):
                    await self._handle_win(results)
                else:
                    await self._handle_loss(results)

        except Exception as e:
            # If any error occurs, print it and stop the view.
            print(f"An error occurred in skill_button_callback: {e}")
            traceback.print_exc()
            self.stop()
        finally:
            # 5. ALWAYS unlock the view when the action is done.
            # This is the most important part to prevent stuck buttons.
            self.is_processing = False

    async def attempt_capture(self, interaction: discord.Interaction, orb_id: str):
        await interaction.response.defer()
        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        results = await self.battle.attempt_capture(orb_id)
        await self._update_view(interaction, results)

    async def confirm_switch_callback(self, interaction: discord.Interaction):
        """Callback for the 'Confirm Switch' button."""
        try:
            if not self.selected_pet_to_switch:
                return

            await interaction.response.defer()
            for item in self.children: item.disabled = True
            await self.message.edit(view=self)

            db_cog = self.bot.get_cog('Database')
            new_pet = await db_cog.get_pet(self.selected_pet_to_switch)
            self.battle.player_pet = _pet_tuple_to_dict(new_pet)
            self.battle.turn_log = [f"> You sent out **{new_pet['name']}**!"]

            results = await self.battle.process_ai_turn()

            await self._update_view(interaction, results)

        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"An error occurred while switching pets: `{e}`", ephemeral=True)
            self.stop()

    async def flee_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Call the new flee logic from your battle engine
        flee_result = await self.battle.attempt_flee()

        if flee_result['success']:
            # On success, return to the wilds with the dynamic success message
            await self._return_to_wilds(flee_result['log'])
        else:
            # On failure, update the combat UI with the failure log and the enemy's attack
            embed = await self.get_battle_embed(turn_summary=flee_result['log'])

            # Disable buttons if the player's pet fainted from the counter-attack
            view = self
            if flee_result.get('is_over'):
                view = self.disable_all_buttons()  # You would need a helper to disable all buttons

            await interaction.edit_original_response(embed=embed, view=view)

    async def get_battle_embed(self, turn_summary: list[str] = None, preview_orb_id: str = None):

        if turn_summary:
            # If a turn summary is provided (like from a failed flee), display it.
            turn_log_display = format_log_block(turn_summary)
        elif preview_orb_id:
            # If an orb is being previewed, show its capture info.
            capture_info = await self.battle.get_capture_info(preview_orb_id)
            orb_name = ITEMS.get(preview_orb_id, {}).get('name', 'Orb')
            turn_log_display = f"**{orb_name} Preview:**\n> {capture_info['text']}\n> *Estimated Capture Rate: **{capture_info['rate']}%***"
        else:
            # If nothing else, show a default message.
            turn_log_display = "> What will you do next?"

        hp_percent = self.battle.player_pet['current_hp'] / self.battle.player_pet['max_hp'] if self.battle.player_pet[
                                                                                                        'max_hp'] > 0 else 0
        color = discord.Color.green() if hp_percent > 0.6 else (
            discord.Color.gold() if hp_percent > 0.25 else discord.Color.red())
        embed = discord.Embed(title="⚔️ Wild Encounter! ⚔️", description=turn_log_display, color=color)

        # --- Player & Wild Pet Fields (No change) ---
        p_hp_bar = _create_progress_bar(self.battle.player_pet['current_hp'], self.battle.player_pet['max_hp'])
        p_fx = ", ".join([e.get('status_effect', 'e').title() for e in self.battle.player_pet_effects]) or "None"
        p_pet_type = self.battle.player_pet['pet_type']
        p_type_str = " / ".join([f"{t} {TYPE_EMOJIS.get(t, '')}".strip() for t in p_pet_type]) if isinstance(p_pet_type,
                                                                                                                 list) else f"{p_pet_type} {TYPE_EMOJIS.get(p_pet_type, '')}".strip()
        p_passive = self.battle.player_pet.get('passive_ability', 'None')
        p_personality = self.battle.wild_pet.get('personality', 'N/A')
        player_display = (f"```\n"
                              f"❤️ {p_hp_bar} {self.battle.player_pet['current_hp']}/{self.battle.player_pet['max_hp']}\n"
                              f"└─ Type:      {p_type_str}\n"
                              f"└─ Personality: {p_personality}\n"
                              f"└─ Passive:   {p_passive}\n"
                              f"└─ Status:    {p_fx}\n"
                              f"```")
        embed.add_field(name=f"Your {self.battle.player_pet['name']} (Lvl {self.battle.player_pet['level']})",
                            value=player_display, inline=True)

        w_hp_bar = _create_progress_bar(self.battle.wild_pet['current_hp'], self.battle.wild_pet['max_hp'])
        w_fx = ", ".join([e.get('status_effect', 'e').title() for e in self.battle.wild_pet_effects]) or "None"
        w_pet_type = self.battle.wild_pet['pet_type']
        w_type_str = " / ".join([f"{t} {TYPE_EMOJIS.get(t, '')}".strip() for t in w_pet_type]) if isinstance(w_pet_type,
                                                                                                                 list) else f"{w_pet_type} {TYPE_EMOJIS.get(w_pet_type, '')}".strip()
        w_passive_data = self.battle.wild_pet.get('passive_ability')
        w_passive = w_passive_data.get('name', 'None') if isinstance(w_passive_data, dict) else (
                        w_passive_data or 'None')
        w_personality = self.battle.wild_pet.get('personality', 'N/A')
        wild_display = (f"```\n"
                            f"❤️ {w_hp_bar} {self.battle.wild_pet['current_hp']}/{self.battle.wild_pet['max_hp']}\n"
                            f"└─ Type:        {w_type_str}\n"
                            f"└─ Personality: {w_personality}\n"
                            f"└─ Passive:     {w_passive}\n"
                            f"└─ Status:      {w_fx}\n"
                            f"```")
        embed.add_field(name=f"Wild {self.battle.wild_pet['species']} (Lvl {self.battle.wild_pet['level']})",
                            value=wild_display, inline=True)

        player_primary_type = self.battle.player_pet['pet_type'][0] if isinstance(self.battle.player_pet['pet_type'],
                                                                                      list) else self.battle.player_pet[
                'pet_type']
        defender_types = self.battle.wild_pet['pet_type'] if isinstance(self.battle.wild_pet['pet_type'], list) else [
            self.battle.wild_pet['pet_type']]
        multiplier = get_type_multiplier(player_primary_type, defender_types)
        if multiplier > 1.0:
            advantage_text = "Your attacks are Super Effective!"
        elif multiplier < 1.0 and multiplier > 0:
            advantage_text = "Your attacks are Not Very Effective."
        elif multiplier == 0:
            advantage_text = "Your attacks have No Effect!"
        else:
            advantage_text = "Your attacks are Neutral."
        embed.add_field(name="Type Advantage", value=f"`{advantage_text}`", inline=False)

        # --- GLOOM METER ---
        gloom_filled = math.floor(self.battle.gloom_meter / 5)
        gloom_empty = 20 - gloom_filled
        gloom_bar = '🟪' * gloom_filled + '⬛' * gloom_empty
        embed.add_field(name="Gloom Meter", value=f"{gloom_bar} `{self.battle.gloom_meter}%`", inline=False)

        inventory = await self.battle.db_cog.get_player_inventory(self.user_id)
        orbs = [i['item_id'] for i in inventory if 'orb' in i['item_id']]
        baseline_orb = "tether_orb" if "tether_orb" in orbs else (orbs[0] if orbs else None)

        orb_to_display = baseline_orb

        if preview_orb_id and 'orb' in preview_orb_id:
            orb_to_display = preview_orb_id

        if orb_to_display:
            info = await self.battle.get_capture_info(orb_to_display)
            rate = info['rate']
            filled_blocks = math.floor(rate / 5)
            empty_blocks = 20 - filled_blocks
            bar = '🟨' * filled_blocks + '⬛' * empty_blocks
            embed.add_field(name="Capture Meter", value=f"{bar} `{rate}%`\n> *{info['text']}*", inline=False)

        embed.set_thumbnail(url=get_pet_image_url(self.battle.wild_pet['species']))
        return embed

    async def _handle_win(self, results: dict):
        await self.battle.db_cog.update_pet(
            self.battle.player_pet['pet_id'],
            current_hp=self.battle.player_pet['current_hp']
        )
        result_log = ""
        quest_updates = []  # Initialize the list here

        if results.get("captured"):
            result_log = results['log']
            # If the pet was captured, check for "combat_capture" quests.
            quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_capture",
                                                       {"species": self.battle.wild_pet['species']})
        else:
            result_log = await self.battle.grant_battle_rewards()
            # If the pet was defeated, check for "combat_victory" quests.
            quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_victory",
                                                       {"species": self.battle.wild_pet['species']})

        if quest_updates:
            result_log += "\n\n" + "\n".join(quest_updates)

        await self._return_to_wilds(result_log)

    async def _handle_loss(self, results: dict):
        await self.battle.db_cog.update_pet(self.battle.player_pet['pet_id'], current_hp=0)
        result_log = "💔 You were defeated and scurried back to safety."
        await self._return_to_wilds(result_log)

    async def _return_to_wilds(self, result_log: str):
        # --- THIS IS THE FIX ---
        # If the battle started from a TownView (a sub-location), return to it.
        if isinstance(self.view_context, (TownView, WildsView)):
            # Tell the original view to update itself with the battle results.
            await self.view_context.update_with_activity_log(result_log)
            # Delete the now-unused combat message.
            await self.message.delete()
        else:
            # Fallback for older or different systems.
            view = WildsView(self.bot, self.parent_interaction, self.origin_location_id, activity_log=result_log)
            data = await self.battle.db_cog.get_player_and_pet_data(self.user_id)
            embed = view.build_embed(result_log)
            if data:
                embed.set_footer(text=get_status_bar(data['player_data'], data['main_pet_data']))
            await self.message.edit(embed=embed, view=view)
        # --- END OF FIX ---

    async def on_timeout(self):
        # This function runs automatically when the view expires (after 300 seconds)
        if self.message:
            try:
                # We edit the message to show a clear timeout status
                # and remove all buttons/embeds for a clean look.
                await self.message.edit(
                    content="⚔️ The battle has timed out due to inactivity.",
                    embed=None,  # Clears the embed
                    view=None    # Removes all buttons
                )
                await asyncio.sleep(15)
                await self.message.delete()

            except discord.NotFound:
                # If the message was already deleted, we don't want an error.
                # This makes the bot resilient.
                pass
        self.stop() # Stops the view from listening for more interactions