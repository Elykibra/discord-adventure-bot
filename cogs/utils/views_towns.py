# cogs/utils/views_towns.py

import discord
import traceback
from data.towns import towns
from data.items import ITEMS
from data.quests import QUESTS
from data.dialogues import DIALOGUES
from cogs.utils.helpers import get_status_bar, get_town_embed, check_quest_progress


class WildsView(discord.ui.View):
    def __init__(self, bot, original_interaction, location_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.original_interaction = original_interaction
        self.user_id = original_interaction.user.id
        self.location_id = location_id
        self.message = None
        self.is_exploring = False

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
        if self.is_exploring:
            return await interaction.response.defer()

        self.is_exploring = True
        try:
            adventure_cog = self.bot.get_cog('Adventure')
            if adventure_cog:
                await adventure_cog.explore(interaction, self.location_id, self.message)
        finally:
            # This GUARANTEES the lock is released after the action
            self.is_exploring = False

    async def enter_town_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        location_data = towns.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        if not town_connection_id:
            return await interaction.edit_original_response(content="Error: Cannot find path back to town.", view=None,
                                                            embed=None)

        await db_cog.update_player(self.user_id, current_location=town_connection_id)
        new_embed = await get_town_embed(self.bot, self.user_id, town_connection_id)
        new_view = TownView(self.bot, self.original_interaction, town_connection_id)
        await interaction.edit_original_response(embed=new_embed, view=new_view)
        new_view.message = await interaction.original_response()


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
        if self.message and self.message.embeds and self.message.embeds[0].footer:
            if 'Night' in str(self.message.embeds[0].footer.text):
                time_of_day = 'night'

        if self.current_sub_location_id:
            town_info = towns.get(self.town_id, {})
            location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
            back_button = discord.ui.Button(label="Back to Town Hub", style=discord.ButtonStyle.grey, emoji="↩️")
            back_button.callback = self.back_to_town_callback
            self.add_item(back_button)
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
        wilds_id = next(
            (loc_id for loc_id in town_info.get('connections', {}) if towns.get(loc_id, {}).get('is_wilds')), None)
        if not wilds_id: return
        wilds_data = towns.get(wilds_id, {})
        await db_cog.update_player(self.user_id, current_location=wilds_id)
        new_embed = discord.Embed(title=f"Location: {wilds_data.get('name')}",
                                  description=wilds_data.get('description'), color=discord.Color.dark_green())
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)
        new_view = WildsView(self.bot, self.parent_interaction, wilds_id)
        await interaction.edit_original_response(embed=new_embed, view=new_view)
        new_view.message = await interaction.original_response()

    async def select_location_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = interaction.data['values'][0]
        # Rest of the logic for selecting a location...
        self.build_ui()
        # You would edit the message here with the new embed for the location
        # await interaction.edit_original_response(...)

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