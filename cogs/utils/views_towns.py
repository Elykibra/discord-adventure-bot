# cogs/utils/views_towns.py

import discord
import traceback
from data.towns import towns
from data.items import ITEMS
from data.quests import QUESTS
from data.dialogues import DIALOGUES
from cogs.utils.helpers import get_status_bar, get_town_embed, check_quest_progress


# This is the single, definitive, and correct version of this file.
# It contains all necessary View classes for this part of the game.

class WildsView(discord.ui.View):
    def __init__(self, bot, original_interaction, location_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.original_interaction = original_interaction
        self.user_id = original_interaction.user.id
        self.location_id = location_id
        self.message = None

        location_data = towns.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        town_name = towns.get(town_connection_id, {}).get('name', 'Town')

        enter_town_button = discord.ui.Button(label=f"Return to {town_name}", style=discord.ButtonStyle.secondary,
                                              emoji="🏘️")
        enter_town_button.callback = self.enter_town_callback
        self.add_item(enter_town_button)

        explore_button = discord.ui.Button(label="Explore the Wilds", style=discord.ButtonStyle.green, emoji="🌲")
        explore_button.callback = self.explore_button_callback
        self.add_item(explore_button)

    async def explore_button_callback(self, interaction: discord.Interaction):
        adventure_cog = self.bot.get_cog('Adventure')
        if adventure_cog:
            await adventure_cog.explore(interaction, self.location_id)

    async def enter_town_callback(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('Database')
        location_data = towns.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        if not town_connection_id:
            return await self.message.edit(content="Error: Cannot find path back to town.", view=None)

        await db_cog.update_player(self.user_id, current_location=town_connection_id)

        new_embed = await get_town_embed(self.bot, self.user_id, town_connection_id)
        new_view = TownView(self.bot, self.original_interaction, town_connection_id)

        await interaction.response.edit_message(embed=new_embed, view=new_view)
        new_view.message = interaction.message


class TravelView(discord.ui.View):
    def __init__(self, bot, original_interaction, connections, main_message_to_edit):
        super().__init__(timeout=60)
        self.bot = bot
        self.original_interaction = original_interaction
        self.connections = connections
        self.main_message_to_edit = main_message_to_edit

        options = [discord.SelectOption(label=name, value=loc_id) for loc_id, name in connections.items()]
        select = discord.ui.Select(placeholder="Choose a destination...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        destination_id = interaction.data['values'][0]
        db_cog = self.bot.get_cog('Database')
        await db_cog.update_player(self.original_interaction.user.id, current_location=destination_id)
        destination_data = towns.get(destination_id, {})

        new_view = None
        new_embed = None

        if destination_data.get('is_wilds', False):
            new_embed = discord.Embed(title=f"Location: {destination_data.get('name')}",
                                      description=destination_data.get('description'), color=discord.Color.dark_green())
            new_view = WildsView(self.bot, self.original_interaction, destination_id)
        else:
            new_embed = await get_town_embed(self.bot, self.original_interaction.user.id, destination_id)
            new_view = TownView(self.bot, self.original_interaction, destination_id)

        await self.main_message_to_edit.edit(embed=new_embed, view=new_view)
        new_view.message = self.main_message_to_edit

        await interaction.delete_original_response()
        self.stop()

class TownView(discord.ui.View):
    def __init__(self, bot, parent_interaction, town_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.parent_interaction = parent_interaction
        self.user_id = parent_interaction.user.id
        self.message = None
        self.town_id = town_id
        self.current_sub_location_id = None
        self.build_ui()

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        print(f"--- An error occurred in TownView for item: {item} ---")
        traceback.print_exc()
        if not interaction.response.is_done():
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        else:
            await interaction.followup.send("An unexpected error occurred.", ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return False
        return True

    def build_ui(self):
        self.clear_items()
        time_of_day = 'day'
        if self.message and self.message.embeds:
            footer_text = self.message.embeds[0].footer.text
            if footer_text and 'Night' in footer_text:
                time_of_day = 'night'

        if self.current_sub_location_id:
            town_info = towns.get(self.town_id, {})
            location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
            services = location_info.get('services', {})
            if "explore_zone" in services:
                self.add_item(discord.ui.Button(label="Explore Area", style=discord.ButtonStyle.green, emoji="🌲", custom_id="explore_zone"))
                self.children[-1].callback = self.explore_zone_callback
            if "rest" in services:
                self.add_item(discord.ui.Button(label="Rest", style=discord.ButtonStyle.secondary, emoji="🌙", custom_id="rest"))
                self.children[-1].callback = self.rest_callback
            for npc_id, npc_data in location_info.get('npcs', {}).items():
                is_available = npc_data.get('availability', 'all') in ['all', time_of_day]
                talk_button = discord.ui.Button(label=f"Talk to {npc_data['name']}", style=discord.ButtonStyle.secondary, disabled=not is_available)
                talk_button.callback = self.create_talk_callback(npc_id)
                self.add_item(talk_button)
            back_button = discord.ui.Button(label="Back to Town Hub", style=discord.ButtonStyle.grey, emoji="↩️")
            back_button.callback = self.back_to_town_callback
            self.add_item(back_button)
        else:
            town_info = towns.get(self.town_id, {})
            locations = town_info.get('locations', {})
            location_options = [
                discord.SelectOption(label=data['name'], value=loc_id, description=data.get('menu_description'), emoji=data.get('emoji'))
                for loc_id, data in locations.items()
            ]
            if location_options:
                select = discord.ui.Select(placeholder="Explore locations in town...", options=location_options)
                select.callback = self.select_location_callback
                self.add_item(select)
            wilds_id = next((loc_id for loc_id in town_info.get('connections', {}) if towns.get(loc_id, {}).get('is_wilds')), None)
            if wilds_id:
                explore_wilds_button = discord.ui.Button(label="Explore Wilds", style=discord.ButtonStyle.green, emoji="🌲")
                explore_wilds_button.callback = self.explore_wilds_callback
                self.add_item(explore_wilds_button)
            travel_button = discord.ui.Button(label="Travel", style=discord.ButtonStyle.blurple, emoji="🗺️")
            travel_button.callback = self.travel_callback
            self.add_item(travel_button)

    async def explore_wilds_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        town_info = towns.get(self.town_id, {})
        wilds_id = next((loc_id for loc_id in town_info.get('connections', {}) if towns.get(loc_id, {}).get('is_wilds')), None)
        if not wilds_id: return
        wilds_data = towns.get(wilds_id, {})
        await db_cog.update_player(self.user_id, current_location=wilds_id)
        new_embed = discord.Embed(title=f"Location: {wilds_data.get('name')}", description=wilds_data.get('description'), color=discord.Color.dark_green())
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)
        new_view = WildsView(self.bot, self.parent_interaction, wilds_id)
        await interaction.edit_original_response(embed=new_embed, view=new_view)
        new_view.message = await interaction.original_response()

    async def rest_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        time_cog = self.bot.get_cog('Time')
        db_cog = self.bot.get_cog('Database')
        town_info = towns.get(self.town_id, {})
        location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
        rest_details = location_info.get('services', {}).get('rest', {})
        if rest_details.get('type') == 'inn':
            cost = rest_details.get('cost', 10)
            player_data = await db_cog.get_player(self.user_id)
            if player_data['coins'] < cost:
                return await interaction.followup.send(f"You don't have enough coins. It costs {cost} coins.", ephemeral=True)
            await db_cog.remove_coins(self.user_id, cost)
        if time_cog:
            await time_cog.advance_time(interaction, rest_details)
        await check_quest_progress(self.bot, self.user_id, "rest", {"location_id": self.current_sub_location_id})
        for item in self.children: item.disabled = True
        await self.parent_interaction.edit_original_response(view=self)
        self.stop()

    async def select_location_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = interaction.data['values'][0]
        town_info = towns.get(self.town_id, {})
        location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
        new_embed = discord.Embed(title=f"Location: {location_info['name']}", description=location_info.get('description_day', "No description available."), color=discord.Color.dark_teal())
        if location_image_url := location_info.get("image_url"):
            new_embed.set_image(url=location_image_url)
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)
        self.build_ui()
        await interaction.edit_original_response(embed=new_embed, view=self)

    async def back_to_town_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = None
        new_embed = await get_town_embed(self.bot, self.user_id, self.town_id)
        self.build_ui()
        await interaction.edit_original_response(embed=new_embed, view=self)

    async def travel_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        town_data = towns.get(self.town_id, {})
        connections = town_data.get('connections', {})
        if not connections:
            await interaction.followup.send("There's nowhere to travel to from here.", ephemeral=True)
            return
        travel_view = TravelView(self.bot, self.parent_interaction, connections, self.message)
        await interaction.followup.send("Where would you like to travel?", view=travel_view, ephemeral=True)

    async def explore_zone_callback(self, interaction: discord.Interaction):
        adventure_cog = self.bot.get_cog('Adventure')
        if adventure_cog:
            town_info = towns.get(self.town_id, {})
            location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
            explore_zone_id = location_info.get('services', {}).get('explore_zone')
            if explore_zone_id:
                await adventure_cog.explore(interaction, explore_zone_id)

    def create_talk_callback(self, npc_id):
        async def talk_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            node, npc_data = await self._get_dialogue_node(npc_id)
            await self._handle_dialogue_action(interaction, npc_data, node, npc_id)
        return talk_callback

    async def _get_dialogue_node(self, npc_id):
        npc_data = DIALOGUES.get(npc_id, {})
        dialogue_tree = npc_data.get('dialogue_tree', [])
        db_cog = self.bot.get_cog('Database')
        player_quests = await db_cog.get_active_quests(self.user_id)
        for node in dialogue_tree:
            if "required_quest_step" in node:
                req = node["required_quest_step"]
                quest = next((q for q in player_quests if q['quest_id'] == req['quest_id']), None)
                if quest and quest['progress'].get('count', 0) == req['step']:
                    return node, npc_data
        grant_quest_node = next((n for n in dialogue_tree if n.get("action") == "grant_quest" and not any(q['quest_id'] == n.get("quest_id") for q in player_quests)), None)
        if grant_quest_node:
            return grant_quest_node, npc_data
        default_node = next((n for n in dialogue_tree if "default" in n), None)
        return default_node, npc_data

    async def _handle_dialogue_action(self, interaction, npc_data, node, npc_id):
        if not node:
            await interaction.followup.send("They have nothing to say to you right now.", ephemeral=True)
            return
        db_cog = self.bot.get_cog('Database')
        text_to_show = node.get("text")
        action = node.get("action")
        quest_id = node.get("quest_id")
        message_parts = [f"*{text_to_show}*"]
        embed_title = f"Conversation with {npc_data['name']}"
        if action == "grant_quest":
            await db_cog.add_quest(self.user_id, quest_id)
        quest_updates = await check_quest_progress(self.bot, self.user_id, "talk_npc", {"npc_id": npc_id})
        if quest_updates:
            message_parts.extend(quest_updates)
        full_description = "\n\n".join(message_parts)
        embed = discord.Embed(title=embed_title, description=full_description, color=discord.Color.light_grey())
        await interaction.followup.send(embed=embed, ephemeral=True)