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
from data.dialogues import DIALOGUES
from utils.helpers import get_status_bar, get_town_embed, check_quest_progress, get_notification, format_log_block


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

        await db_cog.update_player(self.user_id, current_location=town_connection_id)
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
    def __init__(self, bot, original_interaction, connections, main_message_to_edit):
        super().__init__(timeout=60)
        self.bot = bot
        self.original_interaction = original_interaction
        self.connections = connections
        self.main_message_to_edit = main_message_to_edit
        self.message = None  # set by travel_callback after send
        options = [discord.SelectOption(label=name, value=loc_id) for loc_id, name in connections.items()]
        select = discord.ui.Select(placeholder="Choose a destination...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        destination_id = interaction.data['values'][0]
        db_cog = self.bot.get_cog('Database')
        await db_cog.update_player(self.original_interaction.user.id, current_location=destination_id)
        destination_data = TOWNS.get(destination_id, {})

        new_view = None
        if destination_data.get('is_wilds', False):
            new_embed = discord.Embed(title=f"Location: {destination_data.get('name')}",
                                      description=destination_data.get('description'), color=discord.Color.dark_green())
            new_view = WildsView(self.bot, self.original_interaction, destination_id)
        else:
            new_embed = await get_town_embed(self.bot, self.original_interaction.user.id, destination_id)
            new_view = TownView(self.bot, self.original_interaction, destination_id)
            await new_view.initial_setup()

        player_and_pet_data = await db_cog.get_player_and_pet_data(self.original_interaction.user.id)
        if player_and_pet_data:
            status_bar = get_status_bar(player_and_pet_data['player_data'], player_and_pet_data['main_pet_data'])
            new_embed.set_footer(text=status_bar)

        await self.main_message_to_edit.edit(embed=new_embed, view=new_view)
        new_view.message = self.main_message_to_edit
        await interaction.delete_original_response()
        self.stop()

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
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

            # Map 4 phases to broad day/night groups for availability checks
            _DAY_PHASES   = {'morning', 'noon'}
            _NIGHT_PHASES = {'evening', 'night'}

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

        travel_cost = ACTION_COSTS.get("travel", {}).get("energy", 0)
        if player_data['energy'] < travel_cost:
            return await interaction.followup.send(
                f"You don't have enough energy to travel. You need at least {travel_cost} energy.",
                ephemeral=True
            )

        town_data = TOWNS.get(self.town_id, {})
        connections = town_data.get('connections', {})
        if not connections:
            return await interaction.followup.send("There's nowhere to travel to from here.", ephemeral=True)

        # We now pass the resource cog and user_id to the TravelView
        travel_view = TravelView(self.bot, self.parent_interaction, connections, self.message)
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
                    log_list.append(f"📋 **New Quest: {quest_title}**\n*{quest_desc}*" if quest_desc
                                    else f"📋 **New Quest: {quest_title}**")

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
                    # Complete the quest (deletes the row)
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