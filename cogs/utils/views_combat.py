# --- cogs/utils/views_combat.py (Final Version with all mechanics) ---
import traceback

import discord
import asyncio
import math
from cogs.gameplay.battle_engine import BattleState
from cogs.utils.helpers import get_pet_image_url, get_status_bar, _create_progress_bar, _pet_tuple_to_dict, check_quest_progress, get_type_multiplier
from .views_towns import WildsView
from data.items import ITEMS
from data.skills import PET_SKILLS
from cogs.utils.constants import TYPE_EMOJIS

# --- A DEDICATED DROPDOWN COMPONENT FOR THE MAIN COMBAT VIEW ---
class OrbSelectDropdown(discord.ui.Select):
    def __init__(self, available_orbs, parent_view):
        self.parent_view = parent_view
        options = [discord.SelectOption(label=f"{orb['name']} (x{orb['quantity']})", value=orb['id']) for orb in
                   available_orbs]
        super().__init__(placeholder="Select an orb to preview...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_orb_id = self.values[0]

        # Tell the parent view to update the embed and enable the confirm button
        await self.parent_view.preview_orb(selected_orb_id)

        # Edit the original message to apply the changes
        await self.parent_view.message.edit(view=self.parent_view)

    # --- VIEW FOR PET SWITCHING ---
class SwitchPetView(discord.ui.View):
    def __init__(self, bot, user_id, available_pets, parent_view):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        options = [discord.SelectOption(label=f"{pet['name']} (Lvl {pet['level']})",
                                            description=f"HP: {pet['current_hp']}/{pet['max_hp']}",
                                            value=str(pet['pet_id'])) for pet in available_pets]
        select = discord.ui.Select(placeholder="Choose a pet to switch to...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')
        new_pet = await db_cog.get_pet(selected_pet_id)

        self.parent_view.battle.player_pet = _pet_tuple_to_dict(new_pet)
        self.parent_view.battle.turn_log = [f"› You sent out **{new_pet['name']}**!"]

        results = await self.parent_view.battle.process_ai_turn()
        await self.parent_view._update_view(interaction, results)

        await interaction.delete_original_response()
        self.stop()

# --- THE MAIN COMBAT VIEW ---
class CombatView(discord.ui.View):
    def __init__(self, bot, user_id, player_pet, wild_pet, message, parent_interaction, origin_location_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.message = message
        self.parent_interaction = parent_interaction
        self.origin_location_id = origin_location_id
        self.battle = BattleState(bot, user_id, _pet_tuple_to_dict(player_pet), wild_pet)
        self.selected_orb_id = None
        self.bot.loop.create_task(self.async_init())

    async def async_init(self):
        await self.rebuild_ui_for_player_turn()
        # Initial embed creation
        embed = await self.get_battle_embed(f"A wild Level {self.battle.wild_pet['level']} **{self.battle.wild_pet['species']}** appeared!")
        await self.message.edit(embed=embed, view=self)

    async def rebuild_ui_for_player_turn(self):
        self.clear_items()

        for skill_id in self.battle.player_pet.get("skills", ["scratch"])[:4]:
            skill_info = PET_SKILLS.get(skill_id, {})
            skill_button = discord.ui.Button(label=skill_info.get('name', 'Unknown'), style=discord.ButtonStyle.primary,
                                             custom_id=f"skill_{skill_id}")
            skill_button.callback = self.skill_button_callback
            self.add_item(skill_button)

        inventory = await self.battle.db_cog.get_player_inventory(self.user_id)
        available_orbs = [
            {'id': i['item_id'], 'name': ITEMS.get(i['item_id'], {}).get('name', 'Orb'), 'quantity': i['quantity']} for
            i in inventory if 'orb' in i['item_id']]
        if available_orbs:
            self.add_item(OrbSelectDropdown(available_orbs, self))

        switch_button = discord.ui.Button(label="Switch Pet", style=discord.ButtonStyle.secondary, emoji="🔄", row=2)
        switch_button.callback = self.switch_pet_callback
        self.add_item(switch_button)

        capture_button = discord.ui.Button(label="Use Orb", style=discord.ButtonStyle.green,
                                           disabled=self.selected_orb_id is None, custom_id="confirm_capture", row=2)
        capture_button.callback = self.confirm_capture_callback
        self.add_item(capture_button)

        flee_button = discord.ui.Button(label="Flee", style=discord.ButtonStyle.secondary, row=2, custom_id="flee")
        flee_button.callback = self.flee_button_callback
        self.add_item(flee_button)

    async def preview_orb(self, orb_id: str):
        self.selected_orb_id = orb_id
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id == "confirm_capture":
                item.disabled = False

        embed = await self.get_battle_embed(self.message.embeds[0].description, preview_orb_id=orb_id)
        await self.message.edit(embed=embed, view=self)  # Edit the view as well to show the enabled button

    async def confirm_capture_callback(self, interaction: discord.Interaction):
        if not self.selected_orb_id:
            return await interaction.response.send_message("Please select an orb from the dropdown first.", ephemeral=True)
        await self.attempt_capture(interaction, self.selected_orb_id)

    async def _update_view(self, interaction: discord.Interaction, results: dict):
        if not results.get("is_over"):
            await self.rebuild_ui_for_player_turn()
            embed = await self.get_battle_embed(results['log'] + "\n\n**It's your turn!**")
            await self.message.edit(embed=embed, view=self)
        else:
            if results.get("win"):
                await self._handle_win(results)
            else:
                await self._handle_loss(results)

    async def skill_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        results = await self.battle.process_round(interaction.data['custom_id'].replace('skill_', ''))
        await self._update_view(interaction, results)

    async def attempt_capture(self, interaction: discord.Interaction, orb_id: str):
        await interaction.response.defer()
        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        results = await self.battle.attempt_capture(orb_id)
        await self._update_view(interaction, results)

    async def switch_pet_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        all_pets = await self.battle.db_cog.get_all_pets(self.user_id)
        available = [_pet_tuple_to_dict(p) for p in all_pets if
                     _pet_tuple_to_dict(p)['pet_id'] != self.battle.player_pet['pet_id'] and _pet_tuple_to_dict(p)[
                         'current_hp'] > 0]
        if not available:
            return await interaction.followup.send("You have no other healthy pets to switch to!", ephemeral=True)

        await interaction.followup.send("Choose your next pet:",
                                        view=SwitchPetView(self.bot, self.user_id, available, self), ephemeral=True)

    async def flee_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self._return_to_wilds("💨 You successfully fled from the battle!")

    async def get_battle_embed(self, description, preview_orb_id: str = None):
        turn_log_display = description
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

        # --- Type Advantage Field (No change) ---
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

        # --- Gloom Meter ---
        gloom_filled = math.floor(self.battle.gloom_meter / 5)
        gloom_empty = 20 - gloom_filled
        gloom_bar = '🟪' * gloom_filled + '⬛' * gloom_empty
        embed.add_field(name="Gloom Meter", value=f"{gloom_bar} `{self.battle.gloom_meter}%`", inline=False)

        # --- THIS IS THE SINGLE, CORRECTED CAPTURE CHANCE BLOCK ---
        orb_to_check = preview_orb_id
        if not orb_to_check:
            inventory = await self.battle.db_cog.get_player_inventory(self.user_id)
            orbs = [i['item_id'] for i in inventory if 'orb' in i['item_id']]
            orb_to_check = "tether_orb" if "tether_orb" in orbs else (orbs[0] if orbs else None)

        if orb_to_check:
            info = await self.battle.get_capture_info(orb_to_check)
            bar = _create_progress_bar(info['rate'], 100)
            embed.add_field(name="Capture Chance", value=f"{bar} `{info['rate']}%`\n> *{info['text']}*", inline=False)

        embed.set_thumbnail(url=get_pet_image_url(self.battle.wild_pet['species']))
        return embed

    async def _handle_win(self, results: dict):
        await self.battle.db_cog.update_pet(
            self.battle.player_pet['pet_id'],
            current_hp=self.battle.player_pet['current_hp']
        )

        result_log = ""
        if results.get("captured"):
            result_log = results['log']
        else:
            result_log = await self.battle.grant_battle_rewards()

        quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_victory", {"species": self.battle.wild_pet['species']})
        if quest_updates:
            result_log += "\n\n" + "\n".join(quest_updates)
        await self._return_to_wilds(result_log)

    async def _handle_loss(self, results: dict):
        await self.battle.db_cog.update_pet(self.battle.player_pet['pet_id'], current_hp=0)
        result_log = "💔 You were defeated and scurried back to safety."
        await self._return_to_wilds(result_log)

    async def _return_to_wilds(self, result_log: str):
        view = WildsView(self.bot, self.parent_interaction, self.origin_location_id, activity_log=result_log)
        data = await self.battle.db_cog.get_player_and_pet_data(self.user_id)
        embed = view.build_embed(result_log)
        if data:
            embed.set_footer(text=get_status_bar(data['player_data'], data['main_pet_data']))
        await self.message.edit(embed=embed, view=view)
        view.message = self.message