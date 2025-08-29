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

class SelectOrbView(discord.ui.View):
    def __init__(self, bot, user_id, available_orbs, parent_view):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        options = [discord.SelectOption(label=f"{orb['name']} (x{orb['quantity']})", value=orb['id']) for orb in available_orbs]
        select = discord.ui.Select(placeholder="Choose an orb to use...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')
        new_pet = await db_cog.get_pet(selected_pet_id)

        if any(eff.get('status_effect') == 'spirit_blessing_active' for eff in
               self.parent_view.battle.player_pet_effects):
            new_pet['current_hp'] = new_pet['max_hp']
            await db_cog.update_pet(new_pet['pet_id'], current_hp=new_pet['max_hp'])
            for effect in self.parent_view.battle.player_pet_effects[:]:
                if effect.get('status_effect') == 'spirit_blessing_active':
                    self.parent_view.battle.player_pet_effects.remove(effect)

        self.parent_view.battle.player_pet = _pet_tuple_to_dict(new_pet)
        self.parent_view.battle.turn_log = [f"› You sent out **{new_pet['name']}**!"]

        results = await self.parent_view.battle.process_ai_turn()
        await self.parent_view._update_view(interaction, results)
        await interaction.delete_original_response()
        self.stop()


# --- VIEW FOR PET SWITCHING ---
class SwitchPetView(discord.ui.View):
    def __init__(self, bot, user_id, available_pets, parent_view):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        options = [discord.SelectOption(label=f"{pet['name']} (Lvl {pet['level']})", description=f"HP: {pet['current_hp']}/{pet['max_hp']}", value=str(pet['pet_id'])) for pet in available_pets]
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

class CombatView(discord.ui.View):
    def __init__(self, bot, user_id, player_pet, wild_pet, message, parent_interaction, origin_location_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.message = message
        self.parent_interaction = parent_interaction
        self.origin_location_id = origin_location_id
        self.battle = BattleState(bot, user_id, _pet_tuple_to_dict(player_pet), wild_pet)
        self.rebuild_ui_for_player_turn()

    def rebuild_ui_for_player_turn(self):
        self.clear_items()

        # --- Skill Buttons ---
        for skill_id in self.battle.player_pet.get("skills", ["scratch"])[:4]:
            skill_info = PET_SKILLS.get(skill_id, {})
            skill_button = discord.ui.Button(
                label=skill_info.get('name', 'Unknown'),
                style=discord.ButtonStyle.primary,
                custom_id=f"skill_{skill_id}"
            )
            skill_button.callback = self.skill_button_callback
            self.add_item(skill_button)

        # --- Switch Pet Button ---
        switch_button = discord.ui.Button(
            label="Switch Pet",
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
            row=1
        )
        switch_button.callback = self.switch_pet_callback
        self.add_item(switch_button)

        # --- Capture Button ---
        capture_button = discord.ui.Button(
            label="Capture",
            style=discord.ButtonStyle.green,
            custom_id="capture",
            row=1
        )
        capture_button.callback = self.capture_button_callback
        self.add_item(capture_button)

        # --- Flee Button ---
        flee_button = discord.ui.Button(
            label="Flee",
            style=discord.ButtonStyle.secondary,
            custom_id="flee",
            row=1
        )
        flee_button.callback = self.flee_button_callback
        self.add_item(flee_button)

    async def _update_view(self, interaction: discord.Interaction, results: dict):
        print("[DEBUG] _update_view: Updating view with results:", results)
        if not results.get("is_over"):
            self.rebuild_ui_for_player_turn()
            embed = await self.get_battle_embed(results['log'] + "\n\n**It's your turn!**")
            await self.message.edit(embed=embed, view=self)
        else:
            if results.get("win"):
                await self._handle_win(results)
            else:
                await self._handle_loss(results)

    async def skill_button_callback(self, interaction: discord.Interaction):
        # --- THIS IS THE NEW ERROR CHECKER ---
        await interaction.response.defer()
        skill_id = interaction.data['custom_id'].replace('skill_', '')
        print(f"\n--- [DEBUG] Skill button '{skill_id}' pressed ---")

        try:
            # Disable buttons immediately
            for item in self.children: item.disabled = True
            await self.message.edit(view=self)
            print("[DEBUG] Buttons disabled. Calling engine...")

            # Call the engine
            results = await self.battle.process_round(skill_id)
            print(f"[DEBUG] Engine returned: {results}")

            # Update the view with results
            await self._update_view(interaction, results)
            print("[DEBUG] View update complete.")

        except Exception as e:
            # If any error occurs, this block will catch it
            print("\n--- [FATAL ERROR in skill_button_callback] ---")
            traceback.print_exc()  # This prints the full error to your console

            # Send an error message to Discord
            error_embed = discord.Embed(
                title="⚔️ An Error Occurred ⚔️",
                description=f"A critical error happened during combat. The battle cannot continue.\n\n`{type(e).__name__}: {e}`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

            # End the battle view safely
            for item in self.children: item.disabled = True
            await self.message.edit(content="This battle has ended due to an error.", embed=None, view=self)
            self.stop()

    # --- NEW: CAPTURE BUTTON LOGIC ---
    async def capture_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        inventory = await self.battle.db_cog.get_player_inventory(self.user_id)
        available_orbs = [
            {'id': i['item_id'], 'name': ITEMS.get(i['item_id'], {}).get('name', 'Orb'), 'quantity': i['quantity']} for
            i in inventory if 'orb' in i['item_id']]

        if not available_orbs:
            return await interaction.followup.send("You don't have any Capture Orbs!", ephemeral=True)

        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        await interaction.followup.send("Which orb will you use?",
                                        view=SelectOrbView(self.bot, self.user_id, available_orbs, self),
                                        ephemeral=True)

    async def attempt_capture(self, interaction: discord.Interaction, orb_id: str):
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

        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        await interaction.followup.send("Choose your next pet:",
                                        view=SwitchPetView(self.bot, self.user_id, available, self), ephemeral=True)

    async def flee_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self._return_to_wilds("💨 You successfully fled from the battle!")

    async def get_battle_embed(self, description):
        turn_log_display = description
        # Determine embed color based on player pet's HP
        hp_percent = self.battle.player_pet['current_hp'] / self.battle.player_pet['max_hp'] if self.battle.player_pet[
                                                                                                    'max_hp'] > 0 else 0
        embed_color = discord.Color.green() if hp_percent > 0.6 else (
            discord.Color.gold() if hp_percent > 0.25 else discord.Color.red())

        embed = discord.Embed(title="⚔️ Wild Encounter! ⚔️", description=turn_log_display, color=embed_color)

        # --- Player Pet Field ---
        p_hp_bar = _create_progress_bar(self.battle.player_pet['current_hp'], self.battle.player_pet['max_hp'])
        p_fx = ", ".join([e.get('status_effect', 'e').title() for e in self.battle.player_pet_effects]) or "None"

        # Format pet type with emoji
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

        # --- Wild Pet Field ---
        w_hp_bar = _create_progress_bar(self.battle.wild_pet['current_hp'], self.battle.wild_pet['max_hp'])
        w_fx = ", ".join([e.get('status_effect', 'e').title() for e in self.battle.wild_pet_effects]) or "None"

        # Format pet type with emoji
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

        # --- Type Advantage Field ---
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

        # --- Gloom Meter Field ---
        gloom_filled = math.floor(self.battle.gloom_meter / 5)
        gloom_empty = 20 - gloom_filled
        gloom_bar = '🟪' * gloom_filled + '⬛' * gloom_empty
        embed.add_field(name="Gloom Meter", value=f"{gloom_bar} `{self.battle.gloom_meter}%`", inline=False)

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

        await check_quest_progress(self.bot, self.user_id, "combat_victory",
                                   {"species": self.battle.wild_pet['species']})
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