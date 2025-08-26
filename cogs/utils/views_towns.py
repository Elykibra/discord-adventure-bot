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
    # This is the final, fully corrected version of TownView
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

        time_of_day = 'day'  # Default to day
        if self.message and self.message.embeds:
            footer_text = self.message.embeds[0].footer.text
            if footer_text and 'Night' in footer_text:
                time_of_day = 'night'

        if self.current_sub_location_id:
            town_info = towns.get(self.town_id, {})
            location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
            services = location_info.get('services', {})

            if "explore_zone" in services:
                explore_button = discord.ui.Button(label="Explore Area", style=discord.ButtonStyle.green, emoji="🌲")
                explore_button.callback = self.explore_zone_callback
                self.add_item(explore_button)

            if "rest" in services:
                rest_button = discord.ui.Button(label="Rest", style=discord.ButtonStyle.secondary, emoji="🌙")
                rest_button.callback = self.rest_callback
                self.add_item(rest_button)

            for npc_id, npc_data in location_info.get('npcs', {}).items():
                npc_availability = npc_data.get('availability', 'all')
                is_available = (npc_availability == 'all' or npc_availability == time_of_day)

                talk_button = discord.ui.Button(
                    label=f"Talk to {npc_data['name']}",
                    style=discord.ButtonStyle.secondary,
                    disabled=not is_available  # Button is disabled if NPC is NOT available
                )
                talk_button.callback = self.create_talk_callback(npc_id)
                self.add_item(talk_button)

                back_button = discord.ui.Button(label="Back to Town Hub", style=discord.ButtonStyle.grey, emoji="↩️")
                back_button.callback = self.back_to_town_callback
                self.add_item(back_button)
        else:
            town_info = towns.get(self.town_id, {})
            locations = town_info.get('locations', {})
            location_options = [
                discord.SelectOption(
                    label=data['name'],
                    value=loc_id,
                    description=data.get('menu_description'),  # <-- USES NEW DESCRIPTION
                    emoji=data.get('emoji')  # <-- USES NEW EMOJI
                ) for loc_id, data in locations.items()
            ]

            if location_options:
                select = discord.ui.Select(placeholder="Explore locations in town...", options=location_options)
                select.callback = self.select_location_callback
                self.add_item(select)
            travel_button = discord.ui.Button(label="Travel", style=discord.ButtonStyle.green, emoji="🗺️")
            travel_button.callback = self.travel_callback
            self.add_item(travel_button)

    async def rest_callback(self, interaction: discord.Interaction):
        # --- THE FIX ---
        # Defer the interaction immediately to prevent it from timing out.
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
                return await interaction.followup.send(f"You don't have enough coins. It costs {cost} coins.",
                                                       ephemeral=True)
            await db_cog.remove_coins(self.user_id, cost)

        if time_cog:
            # The time_cog will now use followup.send, which is correct after a defer.
            await time_cog.advance_time(interaction, rest_details)

        await check_quest_progress(self.bot, interaction, "rest", {"location_id": self.current_sub_location_id})

        for item in self.children:
            item.disabled = True

        # We edit the original message from the parent interaction to show the disabled view
        await self.parent_interaction.edit_original_response(view=self)
        self.stop()

    async def select_location_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = interaction.data['values'][0]
        town_info = towns.get(self.town_id, {})
        location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})

        new_embed = discord.Embed(
            title=f"Location: {location_info['name']}",
            description=location_info.get('description_day', "No description available."),
            color=discord.Color.dark_teal()
        )
        if location_image_url := location_info.get("image_url"):
            new_embed.set_image(url=location_image_url)

        # Add the missing status bar
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)
        # --- END OF UPGRADE ---

        self.build_ui()
        await self.message.edit(embed=new_embed, view=self)

    async def back_to_town_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = None
        new_embed = await get_town_embed(self.bot, self.user_id, self.town_id)
        self.build_ui()
        await self.message.edit(embed=new_embed, view=self)

    async def travel_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
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

    # In the TownView class

    def create_talk_callback(self, npc_id):
        async def talk_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            node, npc_data = await self._get_dialogue_node(npc_id)
            # This callback's ONLY job is to find the right dialogue and pass it to the handler.
            await self._handle_dialogue_action(interaction, npc_data, node, npc_id)

        return talk_callback

    async def _get_dialogue_node(self, npc_id):
        # This is the final, correct version from our previous discussion
        npc_data = DIALOGUES.get(npc_id, {})
        dialogue_tree = npc_data.get('dialogue_tree', [])
        db_cog = self.bot.get_cog('Database')
        player_quests = await db_cog.get_active_quests(self.user_id)

        # Find the highest-priority node that matches a player's current quest step
        for node in dialogue_tree:
            if "required_quest_step" in node:
                req = node["required_quest_step"]
                quest = next((q for q in player_quests if q['quest_id'] == req['quest_id']), None)
                if quest and quest['progress'].get('count', 0) == req['step']:
                    return node, npc_data

        # If not, check if this NPC can grant a quest the player doesn't have
        grant_quest_node = next((n for n in dialogue_tree if n.get("action") == "grant_quest" and not any(
            q['quest_id'] == n.get("quest_id") for q in player_quests)), None)
        if grant_quest_node:
            return grant_quest_node, npc_data

        # If all else fails, find the default dialogue
        default_node = next((n for n in dialogue_tree if "default" in n), None)
        return default_node, npc_data

    async def _handle_dialogue_action(self, interaction, npc_data, node, npc_id):
        # This function is now the single source of truth for handling dialogue actions.
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

        # We now run the quest check AFTER handling the initial action.
        quest_updates = await check_quest_progress(self.bot, self.user_id, "talk_npc", {"npc_id": npc_id})
        if quest_updates:
            message_parts.extend(quest_updates)

        full_description = "\n\n".join(message_parts)
        embed = discord.Embed(
            title=embed_title,
            description=full_description,
            color=discord.Color.light_grey()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)