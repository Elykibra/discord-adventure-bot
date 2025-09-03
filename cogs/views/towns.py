# cogs/views/towns.py

import discord
import traceback
import textwrap

# --- REFACTORED IMPORTS ---
from data.items import ITEMS
from data.towns import towns
from data.dialogues import DIALOGUES
from utils.helpers import get_status_bar, get_town_embed, check_quest_progress


class WildsView(discord.ui.View):
    def __init__(self, bot, original_interaction, location_id, activity_log: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.original_interaction = original_interaction
        self.user_id = original_interaction.user.id
        self.location_id = location_id
        self.message = None
        self.embed = self.build_embed(activity_log)

        location_data = towns.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        town_name = towns.get(town_connection_id, {}).get('name', 'Town')

        self.add_item(
            discord.ui.Button(label=f"Return to {town_name}", style=discord.ButtonStyle.secondary, emoji="🏘️"))
        self.children[0].callback = self.enter_town_callback
        self.add_item(discord.ui.Button(label="Explore the Wilds", style=discord.ButtonStyle.green, emoji="🌲"))
        self.children[1].callback = self.explore_button_callback

    def build_embed(self, activity_log: str = None):
        location_data = towns.get(self.location_id, {})
        embed = discord.Embed(
            title=f"Location: {location_data.get('name')}",
            description=location_data.get('description'),
            color=discord.Color.dark_green()
        )
        if activity_log:
            embed.add_field(name="Activity Log", value=f"> *{activity_log}*", inline=False)
        return embed

    async def explore_button_callback(self, interaction: discord.Interaction):
        print("\n--- [CHECK 1] WildsView: explore_button_callback initiated. ---")
        try:
            adventure_cog = self.bot.get_cog('Adventure')
            if adventure_cog:
                print("--- [CHECK 2] Adventure cog found, calling explore... ---")

                # --- THIS IS THE FIX ---
                # Pass the main message (self.message) to the explore function.
                await adventure_cog.explore(interaction, self.location_id, self)
                # --- END OF FIX ---

            else:
                print("--- [ERROR] Adventure cog NOT found. ---")
        except Exception as e:
            print(f"--- [FATAL ERROR] An exception occurred in explore_button_callback: {e} ---")
            traceback.print_exc()

    async def enter_town_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        location_data = towns.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        if not town_connection_id:
            return await interaction.edit_original_response(content="Error: Cannot find path back to town.", view=None, embed=None)

        await db_cog.update_player(self.user_id, current_location=town_connection_id)
        new_embed = await get_town_embed(self.bot, self.user_id, town_connection_id)
        new_view = TownView(self.bot, self.original_interaction, town_connection_id)
        await interaction.edit_original_response(embed=new_embed, view=new_view)
        new_view.message = await interaction.original_response()

    async def update_with_activity_log(self, activity_log: str):
        """Helper to refresh the WildsView with an activity log."""
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)

        new_embed = self.build_embed(activity_log)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)

        await self.message.edit(embed=new_embed, view=self)


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
        if destination_data.get('is_wilds', False):
            new_embed = discord.Embed(title=f"Location: {destination_data.get('name')}",
                                      description=destination_data.get('description'), color=discord.Color.dark_green())
            new_view = WildsView(self.bot, self.original_interaction, destination_id)
        else:
            new_embed = await get_town_embed(self.bot, self.original_interaction.user.id, destination_id)
            new_view = TownView(self.bot, self.original_interaction, destination_id)

        player_and_pet_data = await db_cog.get_player_and_pet_data(self.original_interaction.user.id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)

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

    # --- NEW HELPER TO BUILD THE SUB-LOCATION EMBED ---
    async def _build_sublocation_embed(self, location_info, dialogue_log: str = None):
        """Builds a standard embed with a non-wrapping monospaced description."""

        description_text = location_info.get('description_day', "No description available.")
        location_name = location_info['name']
        embed_color = discord.Color.dark_teal() # Default color

        # --- THIS IS THE NEW LOGIC ---
        # Check for a gloom_level to determine if the zone is hazardous
        gloom_level = location_info.get('services', {}).get('gloom_level')
        if gloom_level:
            embed_color = discord.Color.dark_purple() # Change color for hazardous zones
            location_name = f"⚠️ {location_name} ⚠️" # Add warning emojis to the title
        # --- END OF NEW LOGIC ---

        embed = discord.Embed(
            title=f"Location: {location_info['name']}",
            description=f"```{description_text}```",
            color=discord.Color.dark_teal()
        )

        # --- ADD A HAZARD FIELD IF APPLICABLE ---
        if gloom_level:
            embed.add_field(
                name="🥀 Zone Hazard: Lingering Gloom",
                value=f"The corruption is strong here. All battles will start with **{gloom_level}% Gloom**.",
                inline=False
            )
        # --- END OF HAZARD FIELD ---

        # Add the dialogue log as a separate field if it exists
        if dialogue_log:
            embed.add_field(
                name="Dialogue Log",
                value=f"> *{dialogue_log}*",
                inline=False
            )

        # Add the footer with the status bar
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            embed.set_footer(text=status_bar)

        return embed

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        print(f"--- An error occurred in TownView for item: {item} ---")
        traceback.print_exc()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return False
        return True

    def build_ui(self):
        self.clear_items()
        time_of_day = 'day'
        if self.message and self.message.embeds and self.message.embeds[0].footer and self.message.embeds[
            0].footer.text:
            if 'Night' in self.message.embeds[0].footer.text:
                time_of_day = 'night'

        if self.current_sub_location_id:
            town_info = towns.get(self.town_id, {})
            location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
            services = location_info.get('services', {})

            if "explore_zone" in services:
                self.add_item(discord.ui.Button(label="Explore Area", style=discord.ButtonStyle.green, emoji="🌲"))
                self.children[-1].callback = self.explore_zone_callback
            if "rest" in services:
                self.add_item(discord.ui.Button(label="Rest", style=discord.ButtonStyle.secondary, emoji="🌙"))
                self.children[-1].callback = self.rest_callback

            for npc_id, npc_data in location_info.get('npcs', {}).items():
                is_available = npc_data.get('availability', 'all') in ['all', time_of_day]
                talk_button = discord.ui.Button(label=f"Talk to {npc_data['name']}",
                                                style=discord.ButtonStyle.secondary, disabled=not is_available)
                # This call is now corrected to pass location_info
                talk_button.callback = self.create_talk_callback(npc_id, location_info)
                self.add_item(talk_button)

            self.add_item(discord.ui.Button(label="Back to Town Hub", style=discord.ButtonStyle.grey, emoji="↩️"))
            self.children[-1].callback = self.back_to_town_callback
        else:
            town_info = towns.get(self.town_id, {})
            locations = town_info.get('locations', {})
            location_options = [
                discord.SelectOption(label=data['name'], value=loc_id, description=data.get('menu_description'),
                                     emoji=data.get('emoji'))
                for loc_id, data in locations.items()
            ]
            if location_options:
                select = discord.ui.Select(placeholder="Explore locations in town...", options=location_options)
                select.callback = self.select_location_callback
                self.add_item(select)
            wilds_id = next(
                (loc_id for loc_id in town_info.get('connections', {}) if towns.get(loc_id, {}).get('is_wilds')), None)
            if wilds_id:
                explore_wilds_button = discord.ui.Button(label="Explore Wilds", style=discord.ButtonStyle.green,
                                                         emoji="🌲")
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
        await interaction.response.defer()
        time_cog = self.bot.get_cog('Time')
        db_cog = self.bot.get_cog('Database')

        location_info = towns.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
        rest_details = location_info.get('services', {}).get('rest', {})

        if rest_details.get('type') == 'inn':
            cost = rest_details.get('cost', 10)
            player_data = await db_cog.get_player(self.user_id)
            if player_data['coins'] < cost:
                return await interaction.followup.send(f"You don't have enough coins. It costs {cost} coins.",
                                                       ephemeral=True)
            await db_cog.remove_coins(self.user_id, cost)

        confirmation_embed = await time_cog.advance_time(self.user_id, rest_details)
        if confirmation_embed:
            await interaction.followup.send(embed=confirmation_embed, ephemeral=True)

        await check_quest_progress(self.bot, self.user_id, "rest", {"location_id": self.current_sub_location_id})

        # Create a new, fresh Town Hub view to reflect the time change
        self.current_sub_location_id = None
        new_hub_embed = await get_town_embed(self.bot, self.user_id, self.town_id)
        new_hub_view = TownView(self.bot, self.parent_interaction, self.town_id)

        for item in self.children:
            item.disabled = True

        # We edit the original message from the parent interaction to show the disabled view
        await self.parent_interaction.edit_original_response(embed=new_hub_embed, view=new_hub_view)
        new_hub_view.message = await self.parent_interaction.original_response()
        self.stop()
        pass

    async def select_location_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = interaction.data['values'][0]

        location_info = towns.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})

        # Use the new helper to build the initial embed
        new_embed = await self._build_sublocation_embed(location_info)

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
            return await interaction.followup.send("There's nowhere to travel to from here.", ephemeral=True)
        travel_view = TravelView(self.bot, self.parent_interaction, connections, self.message)
        await interaction.followup.send("Where would you like to travel?", view=travel_view, ephemeral=True)

    async def explore_zone_callback(self, interaction: discord.Interaction):
        adventure_cog = self.bot.get_cog('Adventure')
        if adventure_cog:
            location_info = towns.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
            explore_zone_id = location_info.get('services', {}).get('explore_zone')
            if explore_zone_id:
                # Pass the view instance (self) as the context
                await adventure_cog.explore(interaction, explore_zone_id, self)

    def create_talk_callback(self, npc_id, location_info):
        async def talk_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            db_cog = self.bot.get_cog('Database')
            node, npc_data = await self._get_dialogue_node(npc_id)
            if not node:
                dialogue_text = "They have nothing to say to you right now."
            else:
                dialogue_text = node.get("text", "...")

                if node.get("action") == "grant_item":
                    item_id = node.get("item_id")
                    quantity = node.get("quantity", 1)
                    if item_id:
                        await db_cog.add_item_to_inventory(self.user_id, item_id, quantity)
                        item_name = ITEMS.get(item_id, {}).get('name', 'an item')
                        dialogue_text += f"\n\n*You received: {quantity}x {item_name}*"

                if node.get("action") == "grant_quest":
                    await db_cog.add_quest(self.user_id, node.get("quest_id"))
                await check_quest_progress(self.bot, self.user_id, "talk_npc", {"npc_id": npc_id})

            new_embed = await self._build_sublocation_embed(location_info, dialogue_log=dialogue_text)
            await interaction.edit_original_response(embed=new_embed, view=self)

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
            return await interaction.followup.send("They have nothing to say to you right now.", ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        text_to_show = node.get("text", node.get("default", "...") )
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

    async def _update_sublocation_view(self, activity_log: str):
        """A dedicated helper to refresh a sub-location view with an activity log."""
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)

        # Get the current embed and add the activity log
        embed = self.message.embeds[0]
        embed.add_field(name="Activity Log", value=f"> *{activity_log}*", inline=False)

        # Update the status bar
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            embed.set_footer(text=status_bar)

        # Rebuild the buttons for the current sub-location to ensure they are fresh
        self.build_ui()

        # Edit the message with the updated embed and view
        await self.message.edit(embed=embed, view=self)

    async def update_with_activity_log(self, activity_log: str):
        """Helper to refresh the TownView (sub-location) with an activity log."""
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)

        location_info = towns.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})

        # Use the existing _build_sublocation_embed and pass the log to it.
        # This assumes the log should be displayed in the 'dialogue_log' parameter.
        new_embed = await self._build_sublocation_embed(location_info, dialogue_log=activity_log)

        await self.message.edit(embed=new_embed, view=self)