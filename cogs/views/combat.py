# cogs/views/combat.py
import asyncio
import traceback
import discord
import math

# --- REFACTORED IMPORTS ---
from core.battle_engine import BattleState
from utils.helpers import get_pet_image_url, get_status_bar, _create_progress_bar, check_quest_progress, \
    get_type_multiplier, _pet_tuple_to_dict, format_log_block, get_notification
from .battle_actions import ForcedSwitchView, EvolvingView, LearnSkillView
from .towns import WildsView, TownView # Assuming views_towns.py is renamed to towns.py in this folder
from data.items import ITEMS
from data.skills import PET_SKILLS
from utils.constants import TYPE_EMOJIS

class CombatView(discord.ui.View):
    def __init__(self, bot, user_id, player_roster, wild_pet, spectator_message, parent_interaction, origin_location_id,
                 view_context=None, initial_log_message=None):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.message = None
        self.spectator_message = spectator_message
        self.parent_interaction = parent_interaction
        self.origin_location_id = origin_location_id
        self.battle = BattleState(bot, user_id, player_roster, [wild_pet])
        self.view_context = view_context


        # --- STATE MANAGEMENT ---
        self.current_menu = "fight"
        self.selected_item_id = None
        self.selected_pet_to_switch = None
        self.selected_skill_id = None
        self.battle_log = initial_log_message or "> What will you do next?"
        self.is_processing = False

        self.view_context = view_context

    async def initial_setup(self):
        """Builds the initial UI and sends the first embed."""
        await self._update_display()

    async def rebuild_ui(self):
        """Dynamically rebuilds the entire view based on the current state."""
        self.clear_items()

        if self.current_menu == "fight":
            skill_options = []
            for skill_id in self.battle.player_pet.get("skills", [])[:4]:
                skill_info = PET_SKILLS.get(skill_id, {})

                power = skill_info.get('power', 0)
                category = skill_info.get('category', 'N/A')
                skill_type = skill_info.get('type', 'N/A')

                desc_parts = []
                if category == "Status":
                    desc_parts.append("Status")
                else:
                    desc_parts.append(f"Power: {power}")
                desc_parts.append(f"Type: {skill_type}")

                description = " | ".join(desc_parts)

                skill_options.append(
                    discord.SelectOption(
                        label=skill_info.get('name', 'Unknown Skill'),
                        value=skill_id,
                        description=description
                    )
                )

            skill_select = discord.ui.Select(placeholder="Choose a skill to use...", options=skill_options)
            skill_select.callback = self.skill_select_callback
            self.add_item(skill_select)

            use_skill_button = discord.ui.Button(
                label="Use Selected Skill",
                style=discord.ButtonStyle.green,
                disabled=(not self.selected_skill_id),
                row=1
            )
            use_skill_button.callback = self.skill_button_callback
            self.add_item(use_skill_button)

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

    async def _update_display(self, interaction: discord.Interaction = None, log: str = None,
                              log_list: list[str] = None):
        """
        A single, reliable function to update both the public embed and private view.
        Now handles setting the private message content with skill details and effectiveness.
        """
        if interaction and not interaction.response.is_done():
            await interaction.response.defer()

        if log_list:
            self.battle_log = format_log_block(log_list)
        elif log:
            self.battle_log = format_log_block(log.split('\n'))

        await self.rebuild_ui()  # Correctly awaited
        embed = await self.get_battle_embed()

        private_message_content = "⚔️ **It's your turn!**"
        if self.selected_skill_id:
            skill_data = PET_SKILLS.get(self.selected_skill_id, {})
            skill_name = skill_data.get('name', 'Unknown Skill')
            skill_desc = skill_data.get('description', 'No description available.')

            # Calculate type effectiveness
            attack_type = skill_data.get('type')
            defender_types = self.battle.wild_pet.get('pet_type', [])
            if not isinstance(defender_types, list):
                defender_types = [defender_types]

            multiplier = get_type_multiplier(attack_type, defender_types, self.battle.wild_pet_effects)

            # (Optional) Uncomment this line in your code to debug type matchups
            # print(f"DEBUG: Attacking with '{attack_type}' against '{defender_types}'. Multiplier: {multiplier}")

            effectiveness_text = ""
            if multiplier > 1.0:
                effectiveness_text = "ᐃ It's **Super Effective!**"
            elif multiplier < 1.0 and multiplier > 0:
                effectiveness_text = "ᐁ It's **Not Very Effective...**"
            elif multiplier == 0:
                effectiveness_text = "⨷ It will have **No Effect!**"
            else:  # --- FIX: This new 'else' block handles the neutral case ---
                effectiveness_text = "→ It's normally **Effective**."

            private_message_content = f"**Selected: {skill_name}**\n_{skill_desc}_\n\n{effectiveness_text}"

        await self.spectator_message.edit(embed=embed)
        if self.message:
            await self.message.edit(content=private_message_content, view=self)

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
        if self.is_processing:
            await interaction.response.send_message("Processing... Please wait.", ephemeral=True, delete_after=3)
            return

        try:
            self.is_processing = True
            for item in self.children:
                item.disabled = True
            await interaction.response.defer()
            await self.message.edit(view=self)

            # --- FIX: We check the item_id BEFORE parsing it ---
            if 'orb' in self.selected_item_id:
                await self.attempt_capture(self.selected_item_id)
            else:
                # Regular items don't need parsing here
                results = await self.battle.process_player_item_use(self.selected_item_id)
                await self._update_view(interaction, results)

        except Exception as e:
            traceback.print_exc()
            self.stop()
        finally:
            self.is_processing = False

    async def _update_view(self, interaction: discord.Interaction, results: dict):
        """
        This function handles updates AFTER a turn is processed.
        It now correctly handles the log as a list.
        """
        log_list = results.get('log', [])
        # Ensure the log is always a list for consistent handling
        if not isinstance(log_list, list):
            log_list = [log_list]

        if not results.get("is_over"):
            log_list.append("\n> **It's your turn!**")
            # This now passes the complete log list to the display updater
            await self._update_display(interaction, log_list=log_list)
        else:
            if results.get("win"):
                await self._handle_win(results)
            else:
                await self._handle_loss(results)

    async def skill_select_callback(self, interaction: discord.Interaction):
        """Called when a skill is selected from the dropdown."""
        self.selected_skill_id = interaction.data['values'][0]
        # Simply update the display to show the skill's info and effectiveness
        await self._update_display(interaction)

    async def skill_button_callback(self, interaction: discord.Interaction):
        """Called when the "Use Selected Skill" button is pressed."""
        if not self.selected_skill_id:
            # Failsafe in case the button is enabled incorrectly
            return

        if self.is_processing:
            await interaction.response.send_message("Processing... Please wait.", ephemeral=True, delete_after=3)
            return

        try:
            # 1. Lock the view for the duration of the turn
            self.is_processing = True
            for item in self.children:
                item.disabled = True
            await interaction.response.defer()
            await self.message.edit(view=self)

            # 2. Process the combat round
            results = await self.battle.process_round(self.selected_skill_id)
            self.selected_skill_id = None

            # Immediately update the internal log with what just happened
            self.battle_log = results['log']
            self.battle.turn_log = results['log'].split('\n')  # Also update the engine's turn log

            # 3. Check for a definitive end to the battle
            if results.get("is_over"):
                if results.get("win"):
                    await self._handle_win(results)
                else:
                    await self._handle_loss(results)
                return  # The battle is over, stop here.

            # 4. Check if the player's pet fainted and a switch is required
            if results.get("switch_required") and results.get("fainted_side") == "player":
                switch_view = ForcedSwitchView(self.battle.player_roster)
                switch_message = await interaction.followup.send(
                    "Your pet has fainted! Choose your next companion.", view=switch_view, ephemeral=True)
                await switch_view.wait()

                if switch_view.chosen_pet_id:
                    switch_log = await self.battle.set_active_player_pet(switch_view.chosen_pet_id)
                    self.battle.turn_log.append(switch_log)
                    ai_results = await self.battle.process_ai_turn()
                    self.battle.turn_log.append(ai_results['log'])
                else:  # Timeout on switch is a forfeit
                    await self._handle_loss({"log": "Forfeited by not choosing a pet."})
                    return
                await switch_message.delete()

            # 5. After the turn is resolved, handle any pending evolutions or skill learns
            await self._handle_pending_actions(interaction)

            # 6. Perform a single, final update to the display
            await self._update_display(log="\n".join(self.battle.turn_log))

        except Exception as e:
            print(f"An error occurred in skill_button_callback: {e}")
            traceback.print_exc()
            self.stop()
        finally:
            # 7. ALWAYS unlock the view for the next turn
            self.is_processing = False

    async def attempt_capture(self, unique_orb_id: str):
        """
        Handles the logic for attempting to capture a wild pet.
        'unique_orb_id' is in the format 'index:item_id'
        """
        try:
            inventory_index, orb_id = unique_orb_id.split(':')
        except ValueError:
            # Failsafe for admin-spawned orbs, etc.
            orb_id = unique_orb_id

        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        results = await self.battle.attempt_capture(orb_id)
        await self._update_view(self.parent_interaction, results)

    async def confirm_switch_callback(self, interaction: discord.Interaction):
        """Callback for the 'Confirm Switch' button."""
        if self.is_processing:
            await interaction.response.send_message("Processing... Please wait.", ephemeral=True, delete_after=3)
            return

        try:
            self.is_processing = True
            for item in self.children: item.disabled = True
            await interaction.response.defer()
            await self.message.edit(view=self)

            if not self.selected_pet_to_switch:
                # Handle case where nothing is selected, then unlock and return
                self.is_processing = False
                await self._update_display(interaction)
                return

            # This is the corrected logic: call the main engine function
            results = await self.battle.process_player_switch(self.selected_pet_to_switch)

            # Update the view with the results from the engine
            await self._update_view(interaction, results)

        except Exception as e:
            traceback.print_exc()
            # Ensure view stops on error to prevent being stuck
            self.stop()
        finally:
            # This now correctly unlocks the view for the next turn
            self.is_processing = False

    async def flee_button_callback(self, interaction: discord.Interaction):
        if self.is_processing:
            await interaction.response.send_message("Processing... Please wait.", ephemeral=True, delete_after=3)
            return

        try:
            self.is_processing = True
            for item in self.children: item.disabled = True
            await interaction.response.defer()
            await self.message.edit(view=self)

            # Call the new flee logic from your battle engine
            flee_result = await self.battle.attempt_flee()

            if flee_result['success']:
                # On success, return to the wilds with the dynamic success message
                await self._return_to_wilds(flee_result['log'])
                # No need to unlock here, the view is being replaced
                return
            else:
                # On failure, update the combat UI with the failure log and the enemy's attack
                # This logic now correctly passes the results to _update_view
                await self._update_view(interaction, flee_result)

        except Exception as e:
            traceback.print_exc()
            self.stop()
        finally:
            self.is_processing = False

    async def get_battle_embed(self, turn_summary: list[str] = None, preview_orb_id: str = None):

        if self.battle_log:
            turn_log_display = self.battle_log
        elif turn_summary:
            turn_log_display = format_log_block(turn_summary)
        elif preview_orb_id:
            # If an orb is being previewed, show its capture info.
            capture_info = await self.battle.get_capture_info(preview_orb_id)
            orb_name = ITEMS.get(preview_orb_id, {}).get('name', 'Orb')
            turn_log_display = f"**{orb_name} Preview:**\n> {capture_info['text']}\n> *Estimated Capture Rate: **{capture_info['rate']}%***"
        else:
            # If nothing else, show a default message.
            turn_log_display = self.battle_log

        hp_percent = self.battle.player_pet['current_hp'] / self.battle.player_pet['max_hp'] if self.battle.player_pet[
                                                                                                        'max_hp'] > 0 else 0
        color = discord.Color.green() if hp_percent > 0.6 else (
            discord.Color.gold() if hp_percent > 0.25 else discord.Color.red())
        embed = discord.Embed(title="⚔️ Wild Encounter! ⚔️", description=turn_log_display, color=color)

        if image_url := get_pet_image_url(self.battle.wild_pet['species']):
            embed.set_thumbnail(url=image_url)

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
                            value=player_display, inline=False)

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
                            value=wild_display, inline=False)

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

        print("DEBUG orb_to_display:", orb_to_display)
        if orb_to_display:
            info = await self.battle.get_capture_info(orb_to_display)
            if not info or not isinstance(info, dict):
                rate = 0
                lore = "No orb preview available."
            else:
                rate = info.get('rate', 0)
                lore = info.get('text', "")

            filled_blocks = math.floor(rate / 5)
            empty_blocks = 20 - filled_blocks
            bar = '🟨' * filled_blocks + '⬛' * empty_blocks
            embed.add_field(name="Capture Meter", value=f"{bar} `{rate}%`\n> *{info['text']}*", inline=False)

        return embed

    async def _handle_win(self, results: dict):
        await self.battle.db_cog.update_pet(
            self.battle.player_pet['pet_id'],
            current_hp=self.battle.player_pet['current_hp']
        )
        final_log_list = []
        if results.get("captured"):
            final_log_list.append(results['log'])
            quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_capture",
                                                       {"species": self.battle.wild_pet['species']})
        else:
            final_log_list = await self.battle.grant_battle_rewards()
            quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_victory",
                                                       {"species": self.battle.wild_pet['species']})
        if quest_updates:
            final_log_list.extend(quest_updates)
        await self._return_to_wilds(final_log_list)

    async def _handle_loss(self, results: dict):
        await self.battle.db_cog.update_pet(self.battle.player_pet['pet_id'], current_hp=0)
        log_message = results.get('log')
        if not log_message:
            log_message = get_notification("BATTLE_DEFEAT")
        await self._return_to_wilds([log_message])

    async def _return_to_wilds(self, result_log_list: list[str]):
        """
        Cleans up all battle messages and returns control to the previous view.
        """
        # --- START OF CORRECTED LOGIC ---
        # Safely delete both the private and public messages
        try:
            await self.message.delete()
        except (discord.NotFound, AttributeError):
            pass  # Ignore if it's already gone

        try:
            await self.spectator_message.delete()
        except (discord.NotFound, AttributeError):
            pass  # Ignore if it's already gone

        # Update the original view (WildsView/TownView) with the battle results
        if hasattr(self.view_context, 'update_with_activity_log'):
            await self.view_context.update_with_activity_log(result_log_list)

        self.stop()

    async def _handle_pending_actions(self, interaction: discord.Interaction):
        """A loop that handles all pending actions (evo, skills) until none are left."""
        while True:
            pending_action = self.battle.check_for_pending_actions()
            if not pending_action:
                break

            for item in self.children: item.disabled = True
            await self.message.edit(view=self)

            if pending_action['type'] == 'evolution':
                evolving_view = EvolvingView(self.bot, self.battle, pending_action['pet_id'])
                evo_message = await interaction.followup.send("Your pet is evolving!", view=evolving_view,
                                                              ephemeral=True)
                evolving_view.message = evo_message
                await evolving_view.wait()

                await self.battle.finalize_evolution(pending_action['pet_id'])
                await evo_message.delete()

            elif pending_action['type'] == 'learn_skill':
                learn_view = LearnSkillView(self.battle.player_pet, pending_action['skill_id'])
                skill_message = await interaction.followup.send(
                    f"Your {self.battle.player_pet['name']} wants to learn a new skill! Choose one to forget.",
                    view=learn_view,
                    ephemeral=True
                )
                await learn_view.wait()

                if learn_view.chosen_skill_to_forget:
                    await self.battle.finalize_skill_learn(
                        pet_id=pending_action['pet_id'],
                        new_skill=pending_action['skill_id'],
                        skill_to_forget=learn_view.chosen_skill_to_forget
                    )
                else:
                    self.battle.clear_pending_skill_learn(pending_action['pet_id'])
                    self.battle.turn_log.append(f"› {self.battle.player_pet['name']} did not learn the new skill.")

                await skill_message.delete()

    async def on_timeout(self):
        # This function runs automatically when the view expires
        if self.message:
            try:
                await self.spectator_message.delete()
                await self.message.edit(
                    content="⚔️ The battle has timed out due to inactivity.",
                    embed=None,
                    view=None
                )
                await asyncio.sleep(15)
                await self.message.delete()
            except discord.NotFound:
                pass
        self.stop()