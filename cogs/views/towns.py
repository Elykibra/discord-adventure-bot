# cogs/views/towns.py

import asyncio
import random
import discord
import traceback
import textwrap

from cogs.resources import ACTION_COSTS
from .shop import ShopView
# --- REFACTORED IMPORTS ---
from data.items import ITEMS
from data.towns import TOWNS
from data.remnants import REMNANTS
from data.dialogues import DIALOGUES
from utils.helpers import (
    get_status_bar, get_town_embed, get_remnant_embed,
    check_quest_progress, get_notification, format_log_block,
    get_location_data, get_connections, is_remnant, get_travel_cost,
)


class WildsView(discord.ui.View):
    def __init__(self, bot, original_interaction, location_id, activity_log: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.original_interaction = original_interaction
        self.user_id = original_interaction.user.id
        self.location_id = location_id
        self.message = None
        self.embed = self.build_embed(activity_log)

        location_data = TOWNS.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        town_name = TOWNS.get(town_connection_id, {}).get('name', 'Town')

        self.add_item(
            discord.ui.Button(label=f"Return to {town_name}", style=discord.ButtonStyle.secondary, emoji="🏘️"))
        self.children[0].callback = self.enter_town_callback
        self.add_item(discord.ui.Button(label="Explore the Wilds", style=discord.ButtonStyle.green, emoji="🌲"))
        self.children[1].callback = self.explore_button_callback

    def build_embed(self, activity_log_list: list[str] = None):
        location_data = TOWNS.get(self.location_id, {})
        embed = discord.Embed(
            title=f"Location: {location_data.get('name')}",
            description=location_data.get('description'),
            color=discord.Color.dark_green()
        )

        # It now expects a list and formats it with our central helper
        if activity_log_list:
            formatted_log = format_log_block(activity_log_list)
            embed.add_field(name="Activity Log", value=formatted_log, inline=False)

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
        location_data = TOWNS.get(self.location_id, {})
        town_connection_id = next(iter(location_data.get('connections', {})), None)
        if not town_connection_id:
            return await interaction.edit_original_response(content="Error: Cannot find path back to town.", view=None, embed=None)

        await db_cog.update_player(self.user_id, current_location=town_connection_id, last_town_id=town_connection_id)
        new_embed = await get_town_embed(self.bot, self.user_id, town_connection_id)
        new_view = TownView(self.bot, self.original_interaction, town_connection_id)
        await new_view.initial_setup()
        await interaction.edit_original_response(embed=new_embed, view=new_view)
        new_view.message = await interaction.original_response()

    async def update_with_activity_log(self, activity_log_list: list[str]):
        db_cog = self.bot.get_cog('Database')
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        new_embed = self.build_embed(activity_log_list)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)
        try:
            await self.message.edit(embed=new_embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            # Original message expired or was deleted — send a fresh ephemeral
            try:
                msg = await self.original_interaction.followup.send(embed=new_embed, view=self, ephemeral=True)
                self.message = msg
            except Exception:
                pass


class TravelView(discord.ui.View):
    def __init__(self, bot, original_interaction, connections, main_message_to_edit,
                 from_location_id: str = None, player_energy: int = 0):
        super().__init__(timeout=60)
        self.bot = bot
        self.original_interaction = original_interaction
        self.connections = connections
        self.main_message_to_edit = main_message_to_edit
        self.from_location_id = from_location_id
        self.message = None  # set by travel_callback after send

        default_cost = ACTION_COSTS.get("travel", {}).get("energy", 10)

        # Store per-route costs so select_callback can deduct the right amount
        self.route_costs = {}
        options = []
        for loc_id, name in connections.items():
            cost = get_travel_cost(from_location_id, loc_id, default=default_cost) if from_location_id else default_cost
            self.route_costs[loc_id] = cost
            can_afford = player_energy >= cost
            loc_data = get_location_data(loc_id)
            gloom = loc_data.get('gloom_level', 0)
            loc_type = "Town" if loc_id in TOWNS else "Remnant"
            desc_parts = [f"⚡ {cost} energy"]
            if gloom > 0:
                desc_parts.append(f"Gloom: {gloom}%")
            desc_parts.append(loc_type)
            options.append(discord.SelectOption(
                label=name if can_afford else f"🔒 {name}",
                value=loc_id,
                description=" · ".join(desc_parts),
                emoji=loc_data.get('emoji'),
            ))
        select = discord.ui.Select(placeholder="Choose a destination...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        destination_id = interaction.data['values'][0]
        db_cog = self.bot.get_cog('Database')
        user_id = self.original_interaction.user.id

        energy_cost = self.route_costs.get(destination_id, ACTION_COSTS.get("travel", {}).get("energy", 10))
        player_data = await db_cog.get_player(user_id)
        current_energy = player_data.get('energy', 0)

        # Block travel if player selected a locked (unaffordable) route
        if current_energy < energy_cost:
            dest_name = self.connections.get(destination_id, destination_id)
            await interaction.followup.send(
                f"🔒 You don't have enough energy to reach **{dest_name}**. "
                f"You need **{energy_cost}** energy but only have **{current_energy}**.",
                ephemeral=True
            )
            return

        new_energy = max(0, current_energy - energy_cost)

        # Track last town so defeat can respawn the player there
        update_kwargs = {"current_location": destination_id, "energy": new_energy}
        if destination_id in TOWNS and not get_location_data(destination_id).get('is_wilds'):
            update_kwargs["last_town_id"] = destination_id

        await db_cog.update_player(user_id, **update_kwargs)
        destination_data = get_location_data(destination_id)

        # Determine what kind of location we're arriving at
        if destination_data.get('is_wilds'):
            new_embed = discord.Embed(
                title=f"Location: {destination_data.get('name')}",
                description=destination_data.get('description'),
                color=discord.Color.dark_green()
            )
            new_view = WildsView(self.bot, self.original_interaction, destination_id)
        elif is_remnant(destination_id):
            new_embed = await get_remnant_embed(self.bot, user_id, destination_id)
            new_view = RemnantView(self.bot, self.original_interaction, destination_id)
            await new_view.initial_setup()
        else:
            new_embed = await get_town_embed(self.bot, user_id, destination_id)
            new_view = TownView(self.bot, self.original_interaction, destination_id)
            await new_view.initial_setup()

        player_and_pet_data = await db_cog.get_player_and_pet_data(user_id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)

        # Try to edit the original message in place.
        # Falls back to a fresh ephemeral if the interaction token has expired (>15 min).
        try:
            await self.main_message_to_edit.edit(embed=new_embed, view=new_view)
            new_view.message = self.main_message_to_edit
        except discord.NotFound:
            msg = await interaction.followup.send(embed=new_embed, view=new_view, ephemeral=True)
            new_view.message = msg
        try:
            await interaction.delete_original_response()
        except (discord.NotFound, discord.HTTPException):
            pass

        # Check if arriving here completes a travel quest objective
        quest_updates = await check_quest_progress(
            self.bot, user_id, "travel", {"location_id": destination_id},
            channel=self.original_interaction.channel
        )
        if quest_updates:
            try:
                await self.original_interaction.followup.send(
                    embed=discord.Embed(
                        description=format_log_block(quest_updates),
                        color=discord.Color.gold()
                    ),
                    ephemeral=True
                )
            except Exception:
                pass

        self.stop()

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except (discord.NotFound, discord.HTTPException):
                pass


class RemnantView(discord.ui.View):
    """
    View for Remnant road stops.
    Mirrors TownView — locations dropdown + Explore Area + Travel.
    Differences: no Explore Wilds, rest lives inside sub-locations.
    """

    _DAY_PHASES   = {'morning', 'noon'}
    _NIGHT_PHASES = {'evening', 'night'}

    def __init__(self, bot, parent_interaction, remnant_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.parent_interaction = parent_interaction
        self.user_id = parent_interaction.user.id
        self.message = None
        self.remnant_id = remnant_id
        self.current_sub_location_id = None

    def _is_location_open(self, location_info: dict, time_of_day: str) -> bool:
        avail = location_info.get('availability', 'all')
        if avail == 'all':
            return True
        if avail == 'day':
            return time_of_day in self._DAY_PHASES
        if avail == 'night':
            return time_of_day in self._NIGHT_PHASES
        return avail == time_of_day

    def _is_location_unlocked(self, location_info: dict, player_flags: set, active_quest_ids: set) -> bool:
        """Returns False if the location is quest-gated and the condition isn't met."""
        req_quest = location_info.get('required_quest')
        if req_quest and req_quest not in active_quest_ids:
            return False
        req_flag = location_info.get('required_flag')
        if req_flag and req_flag not in player_flags:
            return False
        return True

    async def initial_setup(self):
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        time_of_day = player_data.get('day_of_cycle', 'morning') if player_data else 'morning'
        player_flags = player_data.get('flags', set()) if player_data else set()
        active_quests = await db_cog.get_active_quests(self.user_id)
        active_quest_ids = {q['quest_id'] for q in active_quests}
        remnant = REMNANTS.get(self.remnant_id, {})
        self.build_ui(time_of_day, player_flags, active_quest_ids, remnant)

    def build_ui(self, time_of_day='morning', player_flags=None, active_quest_ids=None, remnant=None):
        self.clear_items()
        if player_flags is None:
            player_flags = set()
        if active_quest_ids is None:
            active_quest_ids = set()
        if remnant is None:
            remnant = REMNANTS.get(self.remnant_id, {})

        if self.current_sub_location_id:
            # --- Sub-location view ---
            location_info = remnant.get('locations', {}).get(self.current_sub_location_id, {})
            services = location_info.get('services', {})

            if 'explore_zone' in services:
                btn = discord.ui.Button(label="Explore Area", style=discord.ButtonStyle.green, emoji="🌲")
                btn.callback = self.explore_callback
                self.add_item(btn)

            if 'shop' in services:
                btn = discord.ui.Button(label="Shop", style=discord.ButtonStyle.blurple, emoji="🛒")
                btn.callback = self.shop_callback
                self.add_item(btn)

            if 'rest' in services:
                btn = discord.ui.Button(label="Rest", style=discord.ButtonStyle.secondary, emoji="🔥")
                btn.callback = self.rest_callback
                self.add_item(btn)

            for npc_id, npc_data in location_info.get('npcs', {}).items():
                avail = npc_data.get('availability', 'all')
                if avail == 'all':
                    available = True
                elif avail == 'day':
                    available = time_of_day in self._DAY_PHASES
                elif avail == 'night':
                    available = time_of_day in self._NIGHT_PHASES
                else:
                    available = avail == time_of_day
                btn = discord.ui.Button(
                    label=f"Talk to {npc_data['name']}",
                    style=discord.ButtonStyle.secondary,
                    disabled=not available
                )
                btn.callback = self._make_talk_callback(npc_id, npc_data)
                self.add_item(btn)

            back_btn = discord.ui.Button(label="Back", style=discord.ButtonStyle.grey, emoji="↩️")
            back_btn.callback = self.back_callback
            self.add_item(back_btn)

        else:
            # --- Remnant hub view ---
            locations = remnant.get('locations', {})
            options = []
            for loc_id, loc_data in locations.items():
                is_open = self._is_location_open(loc_data, time_of_day)
                is_unlocked = self._is_location_unlocked(loc_data, player_flags, active_quest_ids)
                if not is_unlocked:
                    label = f"🔒 {loc_data['name']}"
                elif not is_open:
                    label = f"🔒 {loc_data['name']}"
                else:
                    label = loc_data['name']
                options.append(discord.SelectOption(
                    label=label,
                    value=loc_id,
                    description=loc_data.get('menu_description'),
                    emoji=loc_data.get('emoji'),
                ))
            if options:
                select = discord.ui.Select(placeholder="Explore this area...", options=options)
                select.callback = self.select_location_callback
                self.add_item(select)

            # Explore Area button — only if remnant itself has a top-level explore zone
            # (remnants without locations use this; those with locations use sub-location explore)
            top_level_explore = remnant.get('services', {}).get('explore_zone') if not locations else None
            if top_level_explore:
                btn = discord.ui.Button(label="Explore Area", style=discord.ButtonStyle.green, emoji="🌲")
                btn.callback = self.explore_callback
                self.add_item(btn)

            travel_btn = discord.ui.Button(label="Travel", style=discord.ButtonStyle.blurple, emoji="🗺️")
            travel_btn.callback = self.travel_callback
            self.add_item(travel_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return False
        return True

    async def select_location_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = interaction.data['values'][0]
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        time_of_day = player_data.get('day_of_cycle', 'morning') if player_data else 'morning'
        player_flags = player_data.get('flags', set()) if player_data else set()
        active_quests = await db_cog.get_active_quests(self.user_id)
        active_quest_ids = {q['quest_id'] for q in active_quests}
        remnant = REMNANTS.get(self.remnant_id, {})
        location_info = remnant.get('locations', {}).get(self.current_sub_location_id, {})

        # Quest-gated — not yet unlocked
        if not self._is_location_unlocked(location_info, player_flags, active_quest_ids):
            embed = discord.Embed(
                title=f"🔒 {location_info.get('name', 'Location')}",
                description="*There's nothing here for you yet.*",
                color=discord.Color.dark_gray()
            )
            embed.set_footer(text="Complete the required quest to access this area.")
            self.clear_items()
            back_btn = discord.ui.Button(label="Back", style=discord.ButtonStyle.grey, emoji="↩️")
            back_btn.callback = self.back_callback
            self.add_item(back_btn)
            await interaction.edit_original_response(embed=embed, view=self)
            return

        # Time-gated — closed right now
        if not self._is_location_open(location_info, time_of_day):
            closed_desc = (
                location_info.get(f'description_{time_of_day}')
                or location_info.get('description_night')
                or location_info.get('description_day')
                or "This area is inaccessible right now."
            )
            embed = discord.Embed(
                title=f"🔒 {location_info.get('name', 'Location')}",
                description=closed_desc,
                color=discord.Color.dark_gray()
            )
            embed.set_footer(text="Come back at a different time.")
            self.clear_items()
            back_btn = discord.ui.Button(label="Back", style=discord.ButtonStyle.grey, emoji="↩️")
            back_btn.callback = self.back_callback
            self.add_item(back_btn)
            await interaction.edit_original_response(embed=embed, view=self)
            return

        new_embed = await self._build_sublocation_embed(location_info)
        self.build_ui(time_of_day, player_flags, active_quest_ids, remnant)
        await interaction.edit_original_response(embed=new_embed, view=self)

    async def _build_sublocation_embed(self, location_info: dict):
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        time_of_day = player_data.get('day_of_cycle', 'morning') if player_data else 'morning'
        description = (
            location_info.get(f'description_{time_of_day}')
            or location_info.get('description_day')
            or location_info.get('description', 'A quiet spot.')
        )
        embed = discord.Embed(
            title=f"{location_info.get('emoji', '📍')} {location_info['name']}",
            description=description,
            color=discord.Color.dark_teal()
        )
        gloom = location_info.get('services', {}).get('gloom_level', 0)
        if gloom:
            embed.color = discord.Color.dark_purple()
            embed.add_field(
                name="🌑 Zone Hazard: Lingering Gloom",
                value=f"All battles here start with **{gloom}% Gloom**.",
                inline=False
            )
        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            embed.set_footer(text=get_status_bar(
                player_and_pet_data['player_data'], player_and_pet_data['main_pet_data']
            ))
        return embed

    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = None
        new_embed = await get_remnant_embed(self.bot, self.user_id, self.remnant_id)
        player_and_pet_data = await self.bot.get_cog('Database').get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            new_embed.set_footer(text=get_status_bar(
                player_and_pet_data['player_data'], player_and_pet_data['main_pet_data']
            ))
        await self.initial_setup()
        await interaction.edit_original_response(embed=new_embed, view=self)

    def _make_talk_callback(self, npc_id, npc_data):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            db_cog = self.bot.get_cog('Database')
            player_data = await db_cog.get_player(self.user_id)
            time_of_day = player_data.get('day_of_cycle', 'morning') if player_data else 'morning'
            dialogue = npc_data.get('dialogue', {})
            text = dialogue.get(time_of_day) or dialogue.get('default') or "..."
            embed = discord.Embed(
                title=f"{npc_data.get('emoji', '💬')} {npc_data['name']}",
                description=f"*\"{text}\"*",
                color=discord.Color.dark_teal()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        return callback

    async def explore_callback(self, interaction: discord.Interaction):
        remnant = REMNANTS.get(self.remnant_id, {})
        # Use sub-location's explore_zone if inside one, else fall back to remnant id
        if self.current_sub_location_id:
            zone_id = remnant.get('locations', {}).get(
                self.current_sub_location_id, {}
            ).get('services', {}).get('explore_zone', self.remnant_id)
        else:
            zone_id = remnant.get('services', {}).get('explore_zone', self.remnant_id)
        adventure_cog = self.bot.get_cog('Adventure')
        if adventure_cog:
            await adventure_cog.explore(interaction, zone_id, view_context=self)

    async def shop_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        remnant = REMNANTS.get(self.remnant_id, {})
        location_info = remnant.get('locations', {}).get(self.current_sub_location_id, {})
        from .shop import ShopView
        shop_view = ShopView(self.bot, self.user_id, self.parent_interaction, location_info)
        await shop_view.rebuild_ui()
        embed = await shop_view.build_embed()
        msg = await interaction.followup.send(embed=embed, view=shop_view, ephemeral=True)
        shop_view.message = msg

    async def rest_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        remnant = REMNANTS.get(self.remnant_id, {})
        location_info = remnant.get('locations', {}).get(self.current_sub_location_id, {})
        rest_cfg = location_info.get('services', {}).get('rest', {})
        energy_restore = rest_cfg.get('energy_restore', 20)
        flavor = rest_cfg.get('flavor', "You take a moment to catch your breath.")

        player_data = await db_cog.get_player(self.user_id)
        max_energy = player_data.get('max_energy', 100)
        current_energy = player_data.get('energy', 0)
        restored = min(energy_restore, max_energy - current_energy)
        await db_cog.update_player(self.user_id, energy=current_energy + restored)

        new_embed = await self._build_sublocation_embed(location_info)
        new_embed.add_field(
            name="🔥 Rested",
            value=f"*{flavor}*\n\n+**{restored} energy** restored.",
            inline=False
        )
        await interaction.edit_original_response(embed=new_embed, view=self)

    async def travel_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        remnant = REMNANTS.get(self.remnant_id, {})
        connections = remnant.get('connections', {})
        connection_reqs = remnant.get('connection_requirements', {})
        player_flags = player_data.get('flags', set())

        # Filter locked connections
        connections = {
            loc_id: name for loc_id, name in connections.items()
            if loc_id not in connection_reqs or connection_reqs[loc_id] in player_flags
        }
        if not connections:
            return await interaction.followup.send("There's nowhere to go from here.", ephemeral=True)

        default_cost = ACTION_COSTS.get("travel", {}).get("energy", 10)
        min_cost = min(get_travel_cost(self.remnant_id, loc_id, default_cost) for loc_id in connections)
        if player_data.get('energy', 0) < min_cost:
            return await interaction.followup.send(
                f"You're too exhausted to move. You need at least **{min_cost} energy**. Rest first.",
                ephemeral=True
            )

        travel_view = TravelView(self.bot, self.parent_interaction, connections, self.message,
                                 from_location_id=self.remnant_id, player_energy=player_data.get('energy', 0))
        travel_msg = await interaction.followup.send("Where would you like to travel?", view=travel_view, ephemeral=True)
        travel_view.message = travel_msg

    async def update_with_activity_log(self, log_list: list[str]):
        """
        Called after a battle resolves. If the player was defeated and is at a Remnant,
        respawn them at their last town. Otherwise refresh the Remnant embed in place.
        """
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)

        # Defeat respawn — send the player back to their last town
        is_defeat = any("Defeated" in entry for entry in log_list)
        if is_defeat:
            last_town = player_data.get('last_town_id') or 'oakhavenOutpost'
            await db_cog.update_player(self.user_id, current_location=last_town)

            new_embed = await get_town_embed(self.bot, self.user_id, last_town)
            new_view = TownView(self.bot, self.parent_interaction, last_town)
            await new_view.initial_setup()

            # Append retreat note to the log
            from data.towns import TOWNS as _TOWNS
            town_name = _TOWNS.get(last_town, {}).get('name', 'town')
            log_list.append(f"🏠 **Retreated**\n*You were forced back to {town_name}.*")

            player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
            if player_and_pet_data:
                from utils.helpers import get_status_bar as _gsb
                new_embed.set_footer(text=_gsb(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data']))

            # Add battle outcome as a field on the town embed
            from utils.helpers import format_log_block as _flb
            new_embed.add_field(name="Battle Result", value=_flb(log_list), inline=False)

            try:
                await self.message.edit(embed=new_embed, view=new_view)
                new_view.message = self.message
            except (discord.NotFound, discord.HTTPException):
                try:
                    msg = await self.parent_interaction.followup.send(embed=new_embed, view=new_view, ephemeral=True)
                    new_view.message = msg
                except Exception:
                    pass
            return

        # Normal case — battle won, stay at the Remnant
        remnant = REMNANTS.get(self.remnant_id, {})
        new_embed = await get_remnant_embed(self.bot, self.user_id, self.remnant_id)
        from utils.helpers import format_log_block as _flb, get_status_bar as _gsb
        new_embed.add_field(name="Battle Result", value=_flb(log_list), inline=False)

        player_and_pet_data = await db_cog.get_player_and_pet_data(self.user_id)
        if player_and_pet_data:
            new_embed.set_footer(text=_gsb(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data']))

        try:
            await self.message.edit(embed=new_embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            try:
                msg = await self.parent_interaction.followup.send(embed=new_embed, view=self, ephemeral=True)
                self.message = msg
            except Exception:
                pass

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(view=None)
            except (discord.NotFound, discord.HTTPException):
                pass


class TownView(discord.ui.View):
    def __init__(self, bot, parent_interaction, town_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.parent_interaction = parent_interaction
        self.user_id = parent_interaction.user.id
        self.message = None
        self.town_id = town_id
        self.current_sub_location_id = None

    async def initial_setup(self):
        """Asynchronously build the initial UI."""
        self.build_ui()

    # --- NEW HELPER TO BUILD THE SUB-LOCATION EMBED ---
    _DAY_PHASES   = {'morning', 'noon'}
    _NIGHT_PHASES = {'evening', 'night'}

    def _is_location_open(self, location_info: dict, time_of_day: str) -> bool:
        """Returns True if the location is open at the given time of day."""
        avail = location_info.get('availability', 'all')
        if avail == 'all':
            return True
        if avail == 'day':
            return time_of_day in self._DAY_PHASES
        if avail == 'night':
            return time_of_day in self._NIGHT_PHASES
        return avail == time_of_day  # exact phase match (e.g. 'morning' only)

    async def _build_sublocation_embed(self, location_info, log_list: list[str] = None):
        """Builds a standard embed for a sub-location, including hazards and logs."""

        # Resolve description based on current time of day, with fallback chain
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        time_of_day = player_data.get('day_of_cycle', 'morning') if player_data else 'morning'
        description_text = (
            location_info.get(f'description_{time_of_day}')
            or location_info.get('description_morning')
            or location_info.get('description_day')
            or location_info.get('description')
            or "A quiet place."
        )

        embed = discord.Embed(
            title=f"Location: {location_info['name']}",
            description=description_text,
            color=discord.Color.dark_teal()  # Default color
        )

        # --- YOUR GLOOM HAZARD LOGIC (This is the correct place for it) ---
        gloom_level = location_info.get('services', {}).get('gloom_level')
        if gloom_level:
            # Change the embed color and title for hazardous zones
            embed.color = discord.Color.dark_purple()
            embed.title = f"⚠️ {embed.title} ⚠️"

            # Add the specific hazard field
            embed.add_field(
                name="🥀 Zone Hazard: Lingering Gloom",
                value=f"The corruption is strong here. All battles will start with **{gloom_level}% Gloom**.",
                inline=False
            )
        # --- END OF GLOOM LOGIC ---

        # --- OUR NEW ACTIVITY LOG LOGIC ---
        if log_list:
            formatted_log = format_log_block(log_list)
            embed.add_field(
                name="Activity Log",
                value=formatted_log,
                inline=False
            )
        # --- END OF ACTIVITY LOG LOGIC ---

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
        time_of_day = 'morning'  # default — matches _DAY_PHASES
        if self.message and self.message.embeds and self.message.embeds[0].footer and self.message.embeds[0].footer.text:
            footer = self.message.embeds[0].footer.text
            for phase in ('morning', 'noon', 'evening', 'night'):
                if phase.capitalize() in footer:
                    time_of_day = phase
                    break

        if self.current_sub_location_id:
            town_info = TOWNS.get(self.town_id, {})
            location_info = town_info.get('locations', {}).get(self.current_sub_location_id, {})
            services = location_info.get('services', {})

            if "explore_zone" in services:
                self.add_item(discord.ui.Button(label="Explore Area", style=discord.ButtonStyle.green, emoji="🌲"))
                self.children[-1].callback = self.explore_zone_callback
            if "rest" in services:
                self.add_item(discord.ui.Button(label="Rest", style=discord.ButtonStyle.secondary, emoji="🌙"))
                self.children[-1].callback = self.rest_callback
            if "starter_pack" in services:
                pack_cfg = services["starter_pack"]
                uses_done = getattr(self, '_starter_pack_uses', None)
                max_uses = pack_cfg.get("max_uses", 3)
                if uses_done is None or uses_done < max_uses:
                    remaining = "" if uses_done is None else f" ({max_uses - uses_done} left)"
                    btn = discord.ui.Button(label=f"Starter Pack{remaining}", style=discord.ButtonStyle.green, emoji="📦")
                else:
                    btn = discord.ui.Button(label="Starter Pack (Empty)", style=discord.ButtonStyle.grey, emoji="📦", disabled=True)
                btn.callback = self.starter_pack_callback
                self.add_item(btn)
            if "shop" in services:
                self.add_item(discord.ui.Button(label="Shop", style=discord.ButtonStyle.blurple, emoji="🛒"))
                self.children[-1].callback = self.shop_callback

            for npc_id, npc_data in location_info.get('npcs', {}).items():
                avail = npc_data.get('availability', 'all')
                if avail == 'all':
                    is_available = True
                elif avail == 'day':
                    is_available = time_of_day in _DAY_PHASES
                elif avail == 'night':
                    is_available = time_of_day in _NIGHT_PHASES
                else:
                    is_available = avail == time_of_day  # exact phase match
                talk_button = discord.ui.Button(label=f"Talk to {npc_data['name']}",
                                                style=discord.ButtonStyle.secondary, disabled=not is_available)
                # This call is now corrected to pass location_info
                talk_button.callback = self.create_talk_callback(npc_id, location_info)
                self.add_item(talk_button)

            self.add_item(discord.ui.Button(label="Back to Town Hub", style=discord.ButtonStyle.grey, emoji="↩️"))
            self.children[-1].callback = self.back_to_town_callback
        else:
            town_info = TOWNS.get(self.town_id, {})
            locations = town_info.get('locations', {})
            location_options = []
            for loc_id, data in locations.items():
                is_open = self._is_location_open(data, time_of_day)
                label = data['name'] if is_open else f"🔒 {data['name']}"
                location_options.append(
                    discord.SelectOption(label=label, value=loc_id,
                                         description=data.get('menu_description'), emoji=data.get('emoji'))
                )
            if location_options:
                select = discord.ui.Select(placeholder="Explore locations in town...", options=location_options)
                select.callback = self.select_location_callback
                self.add_item(select)
            wilds_id = next(
                (loc_id for loc_id in town_info.get('connections', {}) if TOWNS.get(loc_id, {}).get('is_wilds')), None)
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
        town_info = TOWNS.get(self.town_id, {})
        wilds_id = next((loc_id for loc_id in town_info.get('connections', {}) if TOWNS.get(loc_id, {}).get('is_wilds')), None)
        if not wilds_id: return
        wilds_data = TOWNS.get(wilds_id, {})
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

        location_info = TOWNS.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
        rest_details = location_info.get('services', {}).get('rest', {})

        action_logs = []

        # Handle Inn Costs
        if rest_details.get('type') == 'inn':
            cost = rest_details.get('cost', 10)
            player_data = await db_cog.get_player(self.user_id)
            if player_data['coins'] < cost:
                await self.update_with_activity_log([f"💸 **Not Enough Coins**\n*You need {cost} coins to rest here.*"])
                return
            action_logs.append(f"🛏️ **Checked In**\n*{get_notification('ACTION_SUCCESS_PAY_COINS', cost=cost)}*")

        # 1. Advance time — bundle all restore messages under a single rest header
        time_logs = await time_cog.advance_time(self.user_id, rest_details)
        rest_label = "🛏️ **Rested at Inn**" if rest_details.get('type') == 'inn' else "🌙 **Rested**"
        if time_logs:
            action_logs.append(f"{rest_label}\n" + "\n".join(time_logs))
        else:
            action_logs.append(rest_label)

        # 2. Check for quest progress
        quest_updates = await check_quest_progress(self.bot, self.user_id, "rest",
                                                   {"location_id": self.current_sub_location_id},
                                                   channel=self.parent_interaction.channel)
        if quest_updates:
            action_logs.extend(quest_updates)

        await self.update_with_activity_log(action_logs)

    async def select_location_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_sub_location_id = interaction.data['values'][0]

        location_info = TOWNS.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})

        # Check if location is open — if not, show a closed embed with no action buttons
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        time_of_day = player_data.get('day_of_cycle', 'morning') if player_data else 'morning'

        if not self._is_location_open(location_info, time_of_day):
            # Pick the closed description (night or day fallback)
            closed_desc = (
                location_info.get(f'description_{time_of_day}')
                or location_info.get('description_night')
                or location_info.get('description_day')
                or location_info.get('description')
                or "This location is currently closed."
            )
            closed_embed = discord.Embed(
                title=f"🔒 {location_info.get('name', 'Location')}",
                description=closed_desc,
                color=discord.Color.dark_gray()
            )
            closed_embed.set_footer(text="Come back later.")
            # Only show Back button
            self.clear_items()
            back_btn = discord.ui.Button(label="Back to Town Hub", style=discord.ButtonStyle.grey, emoji="↩️")
            back_btn.callback = self.back_to_town_callback
            self.add_item(back_btn)
            await interaction.edit_original_response(embed=closed_embed, view=self)
            return

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
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)

        town_data = get_location_data(self.town_id)
        all_connections = town_data.get('connections', {})
        connection_reqs = town_data.get('connection_requirements', {})
        player_flags = player_data.get('flags', set())

        # Filter out wilds zones and locked destinations
        connections = {
            loc_id: name for loc_id, name in all_connections.items()
            if not get_location_data(loc_id).get('is_wilds')
            and (loc_id not in connection_reqs or connection_reqs[loc_id] in player_flags)
        }

        if not connections:
            return await interaction.followup.send("There's nowhere to travel to from here.", ephemeral=True)

        # Check player has enough energy for at least one route
        default_cost = ACTION_COSTS.get("travel", {}).get("energy", 10)
        min_cost = min(get_travel_cost(self.town_id, loc_id, default_cost) for loc_id in connections)
        if player_data.get('energy', 0) < min_cost:
            return await interaction.followup.send(
                f"You're too exhausted to travel. You need at least **{min_cost} energy** for the nearest road.",
                ephemeral=True
            )

        travel_view = TravelView(self.bot, self.parent_interaction, connections, self.message,
                                 from_location_id=self.town_id, player_energy=player_data.get('energy', 0))
        travel_msg = await interaction.followup.send("Where would you like to travel?", view=travel_view, ephemeral=True)
        travel_view.message = travel_msg

    async def starter_pack_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        flags = player_data.get('flags', set())

        location_info = TOWNS.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
        pack_cfg = location_info.get('services', {}).get('starter_pack', {})
        max_uses = pack_cfg.get('max_uses', 3)
        flag_prefix = pack_cfg.get('flag_prefix', f'supply_chest_{self.town_id}_use_')

        uses_done = sum(1 for i in range(1, max_uses + 1) if f"{flag_prefix}{i}" in flags)

        if uses_done >= max_uses:
            self._starter_pack_uses = max_uses
            self.build_ui()
            await interaction.edit_original_response(view=self)
            return

        next_use = uses_done + 1
        grants = pack_cfg.get('grants', {}).get(next_use, [])
        message = pack_cfg.get('messages', {}).get(next_use, "You take some supplies from the chest.")

        item_lines = []
        for item_id, qty in grants:
            await db_cog.add_item_to_inventory(self.user_id, item_id, qty)
            item_name = ITEMS.get(item_id, {}).get('name', item_id)
            item_lines.append(f"• {qty}× {item_name}")

        received_str = "\n".join(item_lines) if item_lines else "Nothing left inside."
        log_list = [f"📦 **Supply Chest**\n*{message}*\n{received_str}"]

        await db_cog.set_flag(self.user_id, f"{flag_prefix}{next_use}")
        self._starter_pack_uses = next_use
        await self.update_with_activity_log(log_list)

    async def shop_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        location_info = TOWNS.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
        shop_view = ShopView(self.bot, self.user_id, self.parent_interaction, location_info)
        await shop_view.rebuild_ui()
        embed = await shop_view.build_embed()
        msg = await interaction.followup.send(embed=embed, view=shop_view, ephemeral=True)
        shop_view.message = msg

    async def explore_zone_callback(self, interaction: discord.Interaction):
        adventure_cog = self.bot.get_cog('Adventure')
        if adventure_cog:
            location_info = TOWNS.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
            explore_zone_id = location_info.get('services', {}).get('explore_zone')
            if explore_zone_id:
                # Pass the view instance (self) as the context
                await adventure_cog.explore(interaction, explore_zone_id, self)

    def create_talk_callback(self, npc_id, location_info):
        async def talk_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            db_cog = self.bot.get_cog('Database')
            node, npc_data = await self._get_dialogue_node(npc_id)
            npc_name = npc_data.get('name', npc_id) if npc_data else npc_id
            log_list = []

            if not node:
                log_list.append(f"🗣️ **{npc_name}**\n*They have nothing to say to you right now.*")
            else:
                raw = node.get("text") or node.get("default", "...")
                dialogue_text = random.choice(raw) if isinstance(raw, list) else raw
                log_list.append(f"🗣️ **{npc_name}**\n*\"{dialogue_text}\"*")

                if node.get("action") == "grant_item":
                    item_id = node.get("item_id")
                    quantity = node.get("quantity", 1)
                    if item_id:
                        await db_cog.add_item_to_inventory(self.user_id, item_id, quantity)
                        item_name = ITEMS.get(item_id, {}).get('name', 'an item')
                        log_list.append(f"🎁 **Received**\n*{quantity}× {item_name}*")

                if node.get("action") == "grant_quest":
                    quest_id = node.get("quest_id")
                    from data.quests import QUESTS
                    quest_data = next(
                        (d for town in QUESTS.values() for qid, d in town.items() if qid == quest_id), {}
                    )
                    initial_progress = {"status": "in_progress", "count": 0}
                    if quest_data.get("time_sensitive"):
                        initial_progress["ticks_remaining"] = quest_data.get("time_limit_ticks", 2)
                    await db_cog.add_quest(self.user_id, quest_id, progress=initial_progress)
                    quest_title = quest_data.get('title', quest_id)
                    quest_desc  = quest_data.get('description', '')
                    quest_type  = quest_data.get('type', 'side')
                    grant_emoji = {'main': '⭐', 'assignment': '📋', 'side': '🔵', 'repeatable_bounty': '🔄'}.get(quest_type, '📜')
                    log_list.append(f"{grant_emoji} **New Quest: {quest_title}**\n*{quest_desc}*" if quest_desc
                                    else f"{grant_emoji} **New Quest: {quest_title}**")

                if node.get("action") == "complete_quest":
                    quest_id = node.get("quest_id")
                    from data.quests import QUESTS
                    quest_data = next(
                        (d for town in QUESTS.values() for qid, d in town.items() if qid == quest_id), {}
                    )
                    # Remove the required item from inventory if present
                    required_item = node.get("required_item")
                    if required_item:
                        await db_cog.remove_item_from_inventory(self.user_id, required_item, 1)
                    # Complete the quest (marks as completed in DB)
                    await db_cog.complete_quest(self.user_id, quest_id)
                    # Set completion flag so post-quest dialogue can fire
                    await db_cog.set_flag(self.user_id, f"quest_{quest_id}_completed")
                    # Grant quest rewards
                    reward_item   = quest_data.get("reward_item")
                    reward_qty    = quest_data.get("reward_item_quantity", 1)
                    reward_coins  = quest_data.get("reward_coins", 0)
                    quest_title   = quest_data.get('title', quest_id)
                    if reward_item:
                        await db_cog.add_item_to_inventory(self.user_id, reward_item, reward_qty)
                        item_name = ITEMS.get(reward_item, {}).get('name', reward_item)
                        log_list.append(f"🎉 **Quest Complete: {quest_title}**\n*Reward: {reward_qty}× {item_name}*")
                    elif reward_coins:
                        await db_cog.update_player(self.user_id, coins=reward_coins)
                        log_list.append(f"🎉 **Quest Complete: {quest_title}**\n*Reward: {reward_coins} coins*")
                    else:
                        log_list.append(f"🎉 **Quest Complete: {quest_title}**")

                quest_updates = await check_quest_progress(self.bot, self.user_id, "talk_npc", {"npc_id": npc_id},
                                                           channel=self.parent_interaction.channel)
                if quest_updates:
                    log_list.extend(quest_updates)

            await self.update_with_activity_log(log_list)
        return talk_callback

    async def _get_dialogue_node(self, npc_id):
        npc_data = DIALOGUES.get(npc_id, {})
        dialogue_tree = npc_data.get('dialogue_tree', [])
        db_cog = self.bot.get_cog('Database')
        player_quests = await db_cog.get_active_quests(self.user_id)
        player_data = await db_cog.get_player(self.user_id)
        player_flags = player_data.get('flags', set())
        time_of_day = player_data.get('day_of_cycle', 'morning')

        # Build owned item set for required_item checks
        inventory = await db_cog.get_player_inventory(self.user_id)
        owned_items = {i['item_id'] for i in inventory}

        _req_keys = ("required_flag", "required_item", "required_quest_status",
                     "required_quest_step", "required_time")

        for node in dialogue_tree:
            # --- required_flag ---
            if "required_flag" in node:
                if node["required_flag"] not in player_flags:
                    continue

            # --- required_item ---
            if "required_item" in node:
                if node["required_item"] not in owned_items:
                    continue

            # --- required_quest_status ---
            # status "active"   → quest is in the active_quests list right now
            # status "completed"/"failed" → persistent flag set after the quest ends
            if "required_quest_status" in node:
                req = node["required_quest_status"]
                status = req['status']
                qid   = req['quest_id']
                if status == 'active':
                    if not any(q['quest_id'] == qid for q in player_quests):
                        continue
                else:
                    if f"quest_{qid}_{status}" not in player_flags:
                        continue

            # --- required_quest_step ---
            if "required_quest_step" in node:
                req = node["required_quest_step"]
                quest = next((q for q in player_quests if q['quest_id'] == req['quest_id']), None)
                if not (quest and quest['progress'].get('count', 0) == req['step']):
                    continue

            # --- required_time: list of valid time-of-day phases ---
            if "required_time" in node:
                if time_of_day not in node["required_time"]:
                    continue

            # Node passed all checks — return it if it has any required key
            if any(k in node for k in _req_keys):
                return node, npc_data

        # Fallback 1: unconditional grant_quest nodes (quest not yet active)
        grant_quest_node = next(
            (n for n in dialogue_tree
             if n.get("action") == "grant_quest"
             and not any(k in n for k in _req_keys)
             and not any(q['quest_id'] == n.get("quest_id") for q in player_quests)),
            None,
        )
        if grant_quest_node:
            return grant_quest_node, npc_data

        # Fallback 2: default node
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

    async def update_with_activity_log(self, log_list: list[str]):
        location_info = TOWNS.get(self.town_id, {}).get('locations', {}).get(self.current_sub_location_id, {})
        new_embed = await self._build_sublocation_embed(location_info, log_list=log_list)
        self.build_ui()
        try:
            await self.message.edit(embed=new_embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            # Original message expired or was deleted — send a fresh ephemeral
            try:
                msg = await self.parent_interaction.followup.send(embed=new_embed, view=self, ephemeral=True)
                self.message = msg
            except Exception:
                pass

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(content="🏘️ Town menu closed due to inactivity.", embed=None, view=None)
                await asyncio.sleep(10)
                await self.message.delete()
            except (discord.NotFound, discord.HTTPException):
                pass