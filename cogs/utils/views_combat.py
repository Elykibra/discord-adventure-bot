# --- cogs/utils/views_combat.py (Final Version with all mechanics) ---
import discord, random, asyncio, math, traceback
from . import effects
from cogs.utils.constants import XP_REWARD_BY_RARITY, TYPE_EMOJIS
from data.skills import PET_SKILLS
from data.pets import PET_DATABASE
from cogs.utils.effects import apply_effect
from cogs.utils.helpers import get_pet_image_url, get_status_bar, get_ai_move, _create_progress_bar, get_type_multiplier, _pet_tuple_to_dict, check_quest_progress
from .views_towns import WildsView



# --- VIEW FOR PET SWITCHING ---
class SwitchPetView(discord.ui.View):
    def __init__(self, bot, user_id, available_pets, parent_view):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view  # The CombatView that opened this

        options = [
            discord.SelectOption(
                label=f"{pet['name']} (Lvl {pet['level']})",
                description=f"HP: {pet['current_hp']}/{pet['max_hp']}",
                value=str(pet['pet_id'])
            ) for pet in available_pets
        ]

        if not options:
            self.add_item(discord.ui.Button(label="No other pets available to switch!", disabled=True))
        else:
            select = discord.ui.Select(placeholder="Choose a pet to switch to...", options=options)
            select.callback = self.select_callback
            self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_pet_id = int(interaction.data['values'][0])
        db_cog = self.bot.get_cog('Database')

        new_pet = await db_cog.get_pet(selected_pet_id)

        if any(eff.get('status_effect') == 'spirit_blessing_active' for eff in self.parent_view.player_pet_effects):
            heal_amount = new_pet['max_hp']
            new_pet['current_hp'] = heal_amount
            await db_cog.update_pet(new_pet['pet_id'], current_hp=heal_amount)
            for effect in self.parent_view.player_pet_effects[:]:
                if effect.get('status_effect') == 'spirit_blessing_active':
                    self.parent_view.player_pet_effects.remove(effect)

        self.parent_view.player_pet = _pet_tuple_to_dict(new_pet)

        switch_log = f"› You sent out **{new_pet['name']}**!"

        original_interaction = self.parent_view.last_interaction
        if original_interaction:
            await self.parent_view.handle_ai_turn(original_interaction, switch_log)

        await interaction.delete_original_response()
        self.stop()


class CombatView(discord.ui.View):
    def __init__(self, bot, user_id, player_pet, wild_pet, message, parent_interaction, origin_location_id):
        print("--- [CHECK 10] CombatView __init__ initiated. ---")
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.player_pet = _pet_tuple_to_dict(player_pet)
        self.wild_pet = wild_pet
        self.message = message
        self.in_progress = True
        self.player_pet_effects, self.wild_pet_effects = [], []
        self.turn_log = []

        self.gloom_meter = 0
        self.purify_charges = 1

        self.parent_interaction = parent_interaction
        self.origin_location_id = origin_location_id
        self.last_interaction = parent_interaction
        self.rebuild_ui_for_player_turn()

    def rebuild_ui_for_player_turn(self):
        self.clear_items()
        for skill_id in self.player_pet.get("skills", ["scratch"])[:4]:
            skill_info = PET_SKILLS.get(skill_id, {})
            skill_button = discord.ui.Button(label=skill_info.get('name', 'Unknown'), style=discord.ButtonStyle.primary, custom_id=f"skill_{skill_id}")
            skill_button.callback = self.skill_button_callback
            self.add_item(skill_button)
        self.add_item(discord.ui.Button(label="Switch Pet", style=discord.ButtonStyle.secondary, emoji="🔄", row=1))
        self.children[-1].callback = self.switch_pet_callback
        self.add_item(discord.ui.Button(label="Capture", style=discord.ButtonStyle.green, custom_id="capture", row=1, disabled=True)) # Capture disabled for now
        self.add_item(discord.ui.Button(label="Flee", style=discord.ButtonStyle.secondary, custom_id="flee", row=1))
        self.children[-1].callback = self.flee_button_callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.in_progress:
            self.in_progress = False
            for item in self.children: item.disabled = True
            db_cog = self.bot.get_cog('Database')
            if db_cog:
                await db_cog.update_pet(self.player_pet['pet_id'], current_hp=max(0, self.player_pet['current_hp']))
            embed = await self.get_battle_embed("The battle timed out due to inactivity.")
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=self)
                except discord.errors.NotFound:
                    pass

    async def get_battle_embed(self, description):
        """Generates the main battle embed with a color-changing HP bar."""

        turn_log_display = description if description else "\n".join(self.turn_log)

        # --- DYNAMIC COLOR LOGIC ---
        hp_percent = self.player_pet['current_hp'] / self.player_pet['max_hp']
        if hp_percent > 0.6:
            embed_color = discord.Color.green()
        elif hp_percent > 0.25:
            embed_color = discord.Color.gold()
        else:
            embed_color = discord.Color.red()
        # --- END OF DYNAMIC COLOR LOGIC ---

        # The embed is created only ONCE, using the dynamic color.
        embed = discord.Embed(
            title="⚔️ Wild Encounter! ⚔️",
            description=turn_log_display,
            color=embed_color
        )

        # --- TYPE EFFECTIVENESS LOGIC ---
        player_primary_type = self.player_pet['pet_type'] if isinstance(self.player_pet['pet_type'], str) else \
        self.player_pet['pet_type'][0]
        opponent_types = [self.wild_pet['pet_type']] if isinstance(self.wild_pet['pet_type'], str) else self.wild_pet[
            'pet_type']
        multiplier = get_type_multiplier(player_primary_type, opponent_types)

        if multiplier > 1.0:
            advantage_text = "Super Effective!"
        elif multiplier < 1.0 and multiplier > 0:
            advantage_text = "Not Very Effective"
        elif multiplier == 0:
            advantage_text = "No Effect!"
        else:
            advantage_text = "Neutral"
        # --- END OF TYPE EFFECTIVENESS LOGIC ---

        # --- Player Pet Field ---
        player_hp_bar = _create_progress_bar(self.player_pet['current_hp'], self.player_pet['max_hp'])
        player_effects_str = ", ".join([e.get('status_effect', 'effect').title() for e in self.player_pet_effects]) or "None"
        p_passive = self.player_pet.get('passive_ability')
        p_passive_name = p_passive.get('name', 'None') if isinstance(p_passive, dict) else p_passive or "None"

        # NEW: Format pet type with emoji for the stat block
        if isinstance(self.player_pet['pet_type'], list):
            p_types_with_emojis = [f"{t} {TYPE_EMOJIS.get(t, '')}".strip() for t in self.player_pet['pet_type']]
            p_type_str = " / ".join(p_types_with_emojis)
        else:
            p_type = self.player_pet['pet_type']
            p_type_str = f"{p_type} {TYPE_EMOJIS.get(p_type, '')}".strip()

        player_display = (f"```\n"
                        f"❤️ {player_hp_bar} {self.player_pet['current_hp']}/{self.player_pet['max_hp']}\n"
                        f"└─ Type:    {p_type_str}\n"
                        f"└─ Passive: {p_passive_name}\n"
                        f"└─ Status:  {player_effects_str}\n"
                        f"```")
        embed.add_field(name=f"Your {self.player_pet['name']} (Lvl {self.player_pet['level']})", value=player_display, inline=True)

        # --- Wild Pet Field ---
        wild_hp_bar = _create_progress_bar(self.wild_pet['current_hp'], self.wild_pet['max_hp'])
        wild_effects_str = ", ".join([e.get('status_effect', 'effect').title() for e in self.wild_pet_effects]) or "None"
        w_passive = self.wild_pet.get('passive_ability')
        w_passive_name = w_passive.get('name', 'None') if isinstance(w_passive, dict) else w_passive or "None"

        # NEW: Format pet type with emoji for the stat block
        if isinstance(self.wild_pet['pet_type'], list):
            w_types_with_emojis = [f"{t} {TYPE_EMOJIS.get(t, '')}".strip() for t in self.wild_pet['pet_type']]
            w_type_str = " / ".join(w_types_with_emojis)
        else:
            w_type = self.wild_pet['pet_type']
            w_type_str = f"{w_type} {TYPE_EMOJIS.get(w_type, '')}".strip()

        wild_display = (f"```\n"
                      f"❤️ {wild_hp_bar} {self.wild_pet['current_hp']}/{self.wild_pet['max_hp']}\n"
                      f"└─ Type:    {w_type_str}\n"
                      f"└─ Passive: {w_passive_name}\n"
                      f"└─ Status:  {wild_effects_str}\n"
                      f"```")
        embed.add_field(name=f"Wild {self.wild_pet['species']} (Lvl {self.wild_pet['level']})", value=wild_display, inline=True)

        # --- SEPARATE ADVANTAGE FIELD ---
        player_primary_type = self.player_pet['pet_type'] if isinstance(self.player_pet['pet_type'], str) else \
        self.player_pet['pet_type'][0]
        opponent_types = [self.wild_pet['pet_type']] if isinstance(self.wild_pet['pet_type'], str) else self.wild_pet[
            'pet_type']
        multiplier = get_type_multiplier(player_primary_type, opponent_types)

        if multiplier > 1.0:
            advantage_text = "Your attacks are Super Effective!"
        elif multiplier < 1.0 and multiplier > 0:
            advantage_text = "Your attacks are Not Very Effective."
        elif multiplier == 0:
            advantage_text = "Your attacks have No Effect!"
        else:
            advantage_text = "Your attacks are Neutral."

        embed.add_field(name="Type Advantage", value=f"`{advantage_text}`", inline=False)
        # --- END OF ADVANTAGE FIELD ---

        # --- ADDED MAXIMIZED GLOOM METER ---
        gloom_filled = math.floor(self.gloom_meter / 5)
        gloom_empty = 20 - gloom_filled
        gloom_bar = '🟪' * gloom_filled + '⬛' * gloom_empty
        embed.add_field(name="Gloom Meter", value=f"{gloom_bar} `{self.gloom_meter}%`", inline=False)
        # --- END OF GLOOM METER ---

        embed.set_thumbnail(url=get_pet_image_url(self.wild_pet['species']))
        return embed

    async def perform_attack(self, attacker, defender, skill_id, is_player, is_empowered=False):
        skill_info = PET_SKILLS.get(skill_id,
                                    {"name": "Struggle", "power": 35, "type": "Normal", "category": "Physical"})
        attacker_name = f"Your **{attacker['name']}**" if is_player else f"The wild **{attacker['species']}**"
        turn_log_lines = [f"› {attacker_name} used **{skill_info['name']}**!"]

        # --- PRE-ATTACK PHASE ---
        # Get passive ability data
        attacker_passive_data = PET_DATABASE.get(attacker['species'], {}).get('passive_ability')
        defender_passive_data = PET_DATABASE.get(defender.get('species'), {}).get('passive_ability')

        # Check for attacker passives that trigger on attack
        if attacker_passive_data:
            if attacker_passive_data['name'] == "Singeing Fury" and skill_info['type'] == 'Fire':
                # This is where you would add a stacking "Singe" status effect to the attacker
                turn_log_lines.append(f"› {attacker_name}'s Singeing Fury intensifies!")

        final_damage = 0
        # --- DAMAGE CALCULATION PHASE ---
        if skill_info.get("category") != "Status":
            skill_power = skill_info.get("power", 0)
            attack_stat = attacker['attack'] if skill_info["category"] == "Physical" else attacker['special_attack']
            defense_stat = defender['defense'] if skill_info["category"] == "Physical" else defender['special_defense']

            # (Damage formula remains the same)
            defender_types = defender.get('pet_type', []) if isinstance(defender.get('pet_type'), list) else [
                defender.get('pet_type')]
            type_multiplier = get_type_multiplier(skill_info['type'], defender_types)
            base_damage = (skill_power / 10) + (attack_stat / 2 - defense_stat / 4)
            final_damage = max(1, int(base_damage * type_multiplier * random.uniform(0.9, 1.1)))

            # Check for defender passives that affect incoming damage
            if defender_passive_data:
                if defender_passive_data['name'] == "Solid Rock" and defender['current_hp'] == defender['max_hp']:
                    final_damage = min(final_damage, defender['max_hp'] - 1)
                    turn_log_lines.append(f"› {defender['name']}'s Solid Rock allowed it to endure the hit!")

            defender['current_hp'] -= final_damage
            turn_log_lines.append(f"› It dealt **{final_damage}** damage!")
            if type_multiplier > 1.0: turn_log_lines.append("› It's super effective!")
            if type_multiplier < 1.0: turn_log_lines.append("› It's not very effective...")

        # --- POST-ATTACK PHASE ---
        if 'effect' in skill_info:
            effects_list = skill_info['effect'] if isinstance(skill_info['effect'], list) else [skill_info['effect']]
            for effect_data in effects_list:
                # We now let the master apply_effect handler do ALL the work.
                target = attacker if effect_data.get('target') == 'self' else defender
                target_effects_list = self.player_pet_effects if target == self.player_pet else self.wild_pet_effects
                await effects.apply_effect(
                    handler_type=effect_data.get('type'),
                    target=target,
                    target_effects_list=target_effects_list,
                    effect_data=effect_data,
                    turn_log_lines=turn_log_lines,
                    attacker=attacker,
                    damage_dealt=final_damage
                )

        # --- NEW FUTURE-PROOF PASSIVE ABILITY LOGIC ---
        defender_base_data = PET_DATABASE.get(defender.get('species'))
        if defender_base_data:
            passive_name = defender_base_data.get('passive_ability', {}).get('name')
            if passive_name in effects.PASSIVE_HANDLERS_ON_HIT:
                handler = effects.PASSIVE_HANDLERS_ON_HIT[passive_name]
                await handler(
                    attacker=attacker,
                    defender=defender,
                    turn_log_lines=turn_log_lines,
                    skill_info=skill_info,
                    attacker_effects_list=self.player_pet_effects if attacker == self.player_pet else self.wild_pet_effects
                )
        # --- END OF NEW PASSIVE LOGIC ---

        did_faint = defender['current_hp'] <= 0
        # --- CORRECTED RETURN STATEMENT ---
        return did_faint, "\n".join(turn_log_lines) # Note: The return value might need adjustment based on your function signature



    async def skill_button_callback(self, interaction: discord.Interaction):
        await self.handle_turn(interaction, {'type': 'skill', 'skill_id': interaction.data['custom_id'].replace('skill_', '')})

    async def switch_pet_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.last_interaction = interaction
        db_cog = self.bot.get_cog('Database')
        all_pets = await db_cog.get_all_pets(self.user_id)
        available_pets = [_pet_tuple_to_dict(pet) for pet in all_pets if
                          _pet_tuple_to_dict(pet).get('is_in_party') and _pet_tuple_to_dict(pet)['pet_id'] !=
                          self.player_pet['pet_id'] and _pet_tuple_to_dict(pet)['current_hp'] > 0]
        if not available_pets:
            return await interaction.followup.send("You have no other healthy pets in your party to switch to!",
                                                   ephemeral=True)
        for item in self.children: item.disabled = True
        await self.message.edit(view=self)
        switch_view = SwitchPetView(self.bot, self.user_id, available_pets, self)
        await interaction.followup.send("Choose your next pet:", view=switch_view, ephemeral=True)

    async def handle_turn(self, interaction: discord.Interaction, player_action: dict):
        if not self.in_progress: return
        self.last_interaction = interaction
        for item in self.children: item.disabled = True
        await interaction.response.edit_message(view=self)
        await self.process_round(player_action['skill_id'])

    def _get_modified_stat(self, pet: dict, stat: str) -> int:
        base_value = pet.get(stat, 0)
        final_value = float(base_value)
        effects_list = self.player_pet_effects if 'pet_id' in pet else self.wild_pet_effects
        for effect in effects_list:
            if effect.get('type') == 'stat_change' and effect.get('stat') == stat:
                final_value *= effect.get('modifier', 1.0)
        return math.floor(final_value)

    async def process_round(self, player_skill_id: str):
        """Processes a full round of combat, accounting for priority moves and modified stats."""
        player_move = {"skill_id": player_skill_id}
        ai_move = get_ai_move(self.wild_pet, self.player_pet, self.gloom_meter)
        player_skill_data = PET_SKILLS.get(player_move['skill_id'], {})
        ai_skill_data = PET_SKILLS.get(ai_move['skill_id'], {})
        player_goes_first = None
        player_has_priority = player_skill_data.get("special_flag") == "priority_move"
        ai_has_priority = ai_skill_data.get("special_flag") == "priority_move"
        if player_has_priority and not ai_has_priority:
            player_goes_first = True
        elif not player_has_priority and ai_has_priority:
            player_goes_first = False
        if player_goes_first is None:
            player_speed = self._get_modified_stat(self.player_pet, 'speed')
            wild_speed = self._get_modified_stat(self.wild_pet, 'speed')
            player_goes_first = player_speed >= wild_speed
        attacker_order = [(self.player_pet, self.wild_pet, player_move, True),
                          (self.wild_pet, self.player_pet, ai_move, False)]
        if not player_goes_first:
            attacker_order.reverse()
        self.turn_log.clear()
        for attacker, defender, move, is_player in attacker_order:
            attacker_effects = self.player_pet_effects if is_player else self.wild_pet_effects
            attacker_name = f"Your **{attacker['name']}**" if is_player else f"The wild **{attacker['species']}**"
            flinch_effect = next((e for e in attacker_effects if e.get('status_effect') == 'flinch'), None)
            if flinch_effect:
                self.turn_log.append(f"› {attacker_name} flinched and couldn't move!")
                attacker_effects.remove(flinch_effect)
                continue
            fainted, attack_log = await self.perform_attack(attacker, defender, move['skill_id'], is_player)
            self.turn_log.append(attack_log)
            embed = await self.get_battle_embed("\n".join(self.turn_log))
            await self.last_interaction.edit_original_response(embed=embed)
            await asyncio.sleep(2)
            if fainted:
                if is_player:
                    await self._handle_win(self.last_interaction)
                else:
                    await self._handle_loss(self.last_interaction)
                return
        if await self._process_effects(self.wild_pet, self.wild_pet_effects, self.turn_log, False):
            await self._handle_win(self.last_interaction);
            return
        if await self._process_effects(self.player_pet, self.player_pet_effects, self.turn_log, True):
            await self._handle_loss(self.last_interaction);
            return
        self.rebuild_ui_for_player_turn()
        self.turn_log.append("\n**It's your turn!**")
        embed = await self.get_battle_embed("\n".join(self.turn_log))
        await self.last_interaction.edit_original_response(embed=embed, view=self)

    async def flee_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        result_log = "💨 You successfully fled from the battle!"
        await self._return_to_wilds(result_log)

    async def capture_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Capture logic not yet implemented.", ephemeral=True)

    async def channel_gloom_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Channel Gloom logic not yet implemented.", ephemeral=True)

    async def purify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Purify logic not yet implemented.", ephemeral=True)

    async def _process_effects(self, pet, effects_list, turn_log, is_player):
        pet_name = f"Your **{pet['name']}**" if is_player else f"The wild **{pet['species']}**"
        fainted = False

        # Use a copy of the list to iterate over, allowing us to safely remove items
        for effect in effects_list[:]:

            # --- NEW: Check for end-of-turn damage sequences ---
            if effect.get('status_effect') == 'flinch':
                continue

            on_turn_end_data = effect.get('on_turn_end', {})
            if on_turn_end_data.get('type') == 'damage_sequence':
                damage_array = on_turn_end_data.get('damage', [])
                turn_index = effect.get('turn_index', 0)

                if turn_index < len(damage_array):
                    dot_damage = damage_array[turn_index]
                    pet['current_hp'] -= dot_damage
                    turn_log.append(f"› {pet_name} took **{dot_damage}** damage from {effect.get('status_effect')}!")
                    effect['turn_index'] += 1  # Advance the index for the next turn

            # --- EXISTING: Handle standard poison/burn ---
            elif effect.get('status_effect') in ['poison', 'burn']:
                dot_damage = effect.get('damage_per_turn', 5)
                pet['current_hp'] -= dot_damage
                turn_log.append(f"› {pet_name} took **{dot_damage}** damage from its {effect.get('status_effect')}!")

            # Check for fainting after any damage is applied
            if pet['current_hp'] <= 0:
                pet['current_hp'] = 0
                fainted = True
                break  # Stop processing further effects if the pet faints

            # --- EXISTING: Countdown duration ---
            if 'duration' in effect:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    effects_list.remove(effect)
                    status_name = effect.get('status_effect', 'an effect').replace('_', ' ')
                    if effect.get('type') == 'stat_change':
                        turn_log.append(f"› {pet_name}'s {effect.get('stat')} change wore off.")
                    else:
                        turn_log.append(f"› {pet_name} is no longer afflicted with {status_name}.")

        return fainted

    async def _return_to_wilds(self, result_log: str):
        wilds_view = WildsView(self.bot, self.parent_interaction, self.origin_location_id, activity_log=result_log)
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        new_embed = wilds_view.build_embed(result_log)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)
        await self.message.edit(embed=new_embed, view=wilds_view)
        wilds_view.message = self.message

    async def _show_end_of_battle_ui(self, interaction: discord.Interaction, embed: discord.Embed, result_log: str):
        self.in_progress = False
        for item in self.children: item.disabled = True

        return_view = discord.ui.View(timeout=180)
        return_button = discord.ui.Button(label="Return to Wilds", style=discord.ButtonStyle.secondary)

        async def return_callback(cb_interaction: discord.Interaction):
            # This is where we call the new return function
            await self._return_to_wilds(cb_interaction, result_log)

        return_button.callback = return_callback
        return_view.add_item(return_button)
        await interaction.edit_original_response(embed=embed, view=return_view)

        async def return_callback(cb_interaction: discord.Interaction):
            await cb_interaction.response.defer()
            if self.parent_view and self.parent_view.message:
                for item in self.parent_view.children: item.disabled = False
                await self.parent_view.message.edit(view=self.parent_view)
                await cb_interaction.delete_original_response()
            else:
                await cb_interaction.edit_original_response(content="Battle finished.", embed=None, view=None)

        return_button.callback = return_callback
        return_view.add_item(return_button)
        await interaction.edit_original_response(embed=embed, view=return_view)

    async def _handle_win(self, interaction: discord.Interaction):
        self.in_progress = False
        db_cog = self.bot.get_cog('Database')
        if not db_cog: return
        base_xp = XP_REWARD_BY_RARITY.get(self.wild_pet['rarity'], 20)
        xp_gain = max(5, math.floor(base_xp * (self.wild_pet['level'] / self.player_pet['level']) * 1.5))
        coin_gain = random.randint(5, 15) * self.wild_pet['level']
        updated_pet, leveled_up = await db_cog.add_xp(self.player_pet['pet_id'], xp_gain)
        await db_cog.add_coins(self.user_id, coin_gain)
        await check_quest_progress(self.bot, self.user_id, "combat_victory", {"species": self.wild_pet['species']})
        self.player_pet = updated_pet

        quest_updates = await check_quest_progress(self.bot, self.user_id, "combat_victory", {"species": self.wild_pet['species']})

        result_log = f"🏆 You defeated the wild {self.wild_pet['species']}! You earned {coin_gain} coins and {xp_gain} EXP."
        if leveled_up:
            result_log += f"\nYour pet {self.player_pet['name']} grew to Level {self.player_pet['level']}!"
        await self._return_to_wilds(result_log)

        if quest_updates:
            result_log += "\n\n" + "\n".join(quest_updates)

    async def _handle_loss(self, interaction: discord.Interaction):
        self.in_progress = False
        db_cog = self.bot.get_cog('Database')
        if db_cog:
            await db_cog.update_pet(self.player_pet['pet_id'], current_hp=max(0, self.player_pet['current_hp']))
        result_log = f"💔 You were defeated by the wild {self.wild_pet['species']}."
        await self._return_to_wilds(result_log)