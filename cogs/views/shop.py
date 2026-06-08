# cogs/views/shop.py

import discord
from data.items import ITEMS
from .modals import QuantityModal


class ShopView(discord.ui.View):
    def __init__(self, bot, user_id, parent_interaction, location_info):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.parent_interaction = parent_interaction
        self.location_info = location_info
        self.items_for_sale = location_info.get('items_for_sale', [])
        self.current_mode = 'buy'
        self.selected_item_id = None
        self.message = None

    async def build_embed(self):
        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        coins = player_data.get('coins', 0)

        if self.current_mode == 'buy':
            lines = []
            for item_id in self.items_for_sale:
                item = ITEMS.get(item_id, {})
                if not item:
                    continue
                price = item.get('price', 0)
                desc = item.get('menu_description') or item.get('description', '')
                lines.append(f"**{item['name']}** — {price} 🪙\n> {desc}")

            embed = discord.Embed(
                title=f"🛒 {self.location_info['name']}",
                description="\n\n".join(lines) if lines else "Nothing for sale.",
                color=discord.Color.gold()
            )

        else:  # sell mode
            inventory = await db_cog.get_player_inventory(self.user_id)
            lines = []
            for inv_item in inventory:
                item = ITEMS.get(inv_item['item_id'], {})
                price = item.get('price')
                if not price or price <= 0:
                    continue
                sell_price = max(1, price // 2)
                lines.append(
                    f"**{item['name']}** (x{inv_item['quantity']}) — {sell_price} 🪙 each"
                )

            embed = discord.Embed(
                title="💰 Sell Items",
                description="\n".join(lines) if lines else "You have nothing to sell.",
                color=discord.Color.green()
            )

        embed.set_footer(text=f"💰 Your coins: {coins}")
        return embed

    async def rebuild_ui(self):
        self.clear_items()
        db_cog = self.bot.get_cog('Database')

        if self.current_mode == 'buy':
            options = []
            for item_id in self.items_for_sale:
                item = ITEMS.get(item_id, {})
                if not item:
                    continue
                price = item.get('price', 0)
                options.append(discord.SelectOption(
                    label=item['name'],
                    value=item_id,
                    description=f"{price} 🪙  •  {(item.get('description', ''))[:80]}",
                    default=(item_id == self.selected_item_id)
                ))

            if options:
                select = discord.ui.Select(
                    placeholder="Choose an item to buy...",
                    options=options,
                    row=0
                )
                select.callback = self.item_select_callback
                self.add_item(select)

            buy_btn = discord.ui.Button(
                label=f"Buy{' ' + ITEMS[self.selected_item_id]['name'] if self.selected_item_id else ''}",
                style=discord.ButtonStyle.green,
                disabled=not self.selected_item_id,
                row=1
            )
            buy_btn.callback = self.buy_callback
            self.add_item(buy_btn)

        else:  # sell mode
            inventory = await db_cog.get_player_inventory(self.user_id)
            sellable = [
                (i, ITEMS[i['item_id']])
                for i in inventory
                if ITEMS.get(i['item_id'], {}).get('price', 0) > 0
            ]

            if sellable:
                options = []
                for inv_item, item_data in sellable:
                    sell_price = max(1, item_data['price'] // 2)
                    options.append(discord.SelectOption(
                        label=f"{item_data['name']} (x{inv_item['quantity']})",
                        value=inv_item['item_id'],
                        description=f"Sell for {sell_price} 🪙 each",
                        default=(inv_item['item_id'] == self.selected_item_id)
                    ))
                select = discord.ui.Select(
                    placeholder="Choose an item to sell...",
                    options=options,
                    row=0
                )
                select.callback = self.item_select_callback
                self.add_item(select)
            else:
                self.add_item(discord.ui.Button(
                    label="Nothing to sell", disabled=True, row=0
                ))

            sell_btn = discord.ui.Button(
                label=f"Sell{' ' + ITEMS[self.selected_item_id]['name'] if self.selected_item_id and self.selected_item_id in ITEMS else ''}",
                style=discord.ButtonStyle.red,
                disabled=not self.selected_item_id,
                row=1
            )
            sell_btn.callback = self.sell_callback
            self.add_item(sell_btn)

        # Tab toggle + close
        buy_tab = discord.ui.Button(
            label="🛒 Buy",
            style=discord.ButtonStyle.blurple if self.current_mode == 'buy' else discord.ButtonStyle.grey,
            row=2
        )
        buy_tab.callback = self.buy_tab_callback
        self.add_item(buy_tab)

        sell_tab = discord.ui.Button(
            label="💰 Sell",
            style=discord.ButtonStyle.blurple if self.current_mode == 'sell' else discord.ButtonStyle.grey,
            row=2
        )
        sell_tab.callback = self.sell_tab_callback
        self.add_item(sell_tab)

        close_btn = discord.ui.Button(label="Close", style=discord.ButtonStyle.grey, emoji="↩️", row=2)
        close_btn.callback = self.close_callback
        self.add_item(close_btn)

    async def refresh(self, interaction: discord.Interaction = None):
        await self.rebuild_ui()
        embed = await self.build_embed()
        if self.message:
            await self.message.edit(embed=embed, view=self)
        if interaction and not interaction.response.is_done():
            await interaction.response.defer()

    async def item_select_callback(self, interaction: discord.Interaction):
        self.selected_item_id = interaction.data['values'][0]
        await self.refresh(interaction)

    async def buy_tab_callback(self, interaction: discord.Interaction):
        self.current_mode = 'buy'
        self.selected_item_id = None
        await self.refresh(interaction)

    async def sell_tab_callback(self, interaction: discord.Interaction):
        self.current_mode = 'sell'
        self.selected_item_id = None
        await self.refresh(interaction)

    async def buy_callback(self, interaction: discord.Interaction):
        if not self.selected_item_id:
            return
        item = ITEMS.get(self.selected_item_id, {})
        price = item.get('price', 0)
        max_qty = 99

        modal = QuantityModal(item_name=item['name'], max_quantity=max_qty)
        modal.title = f"Buy {item['name']}"
        modal.quantity_input.label = f"How many? ({price} 🪙 each)"
        modal.quantity_input.placeholder = "Enter a number..."
        await interaction.response.send_modal(modal)
        await modal.wait()

        quantity = modal.quantity
        if quantity <= 0:
            return

        db_cog = self.bot.get_cog('Database')
        player_data = await db_cog.get_player(self.user_id)
        total_cost = price * quantity

        if player_data['coins'] < total_cost:
            await self.message.edit(
                content=f"❌ Not enough coins. You need **{total_cost} 🪙** but only have **{player_data['coins']} 🪙**.",
                embed=await self.build_embed(), view=self
            )
            return

        await db_cog.add_coins(self.user_id, -total_cost)
        await db_cog.add_item_to_inventory(self.user_id, self.selected_item_id, quantity)
        await self.message.edit(
            content=f"✅ Bought **{quantity}x {item['name']}** for **{total_cost} 🪙**.",
            embed=await self.build_embed(), view=self
        )

    async def sell_callback(self, interaction: discord.Interaction):
        if not self.selected_item_id:
            return
        db_cog = self.bot.get_cog('Database')
        item = ITEMS.get(self.selected_item_id, {})
        sell_price = max(1, item.get('price', 0) // 2)

        inventory = await db_cog.get_player_inventory(self.user_id)
        inv_item = next((i for i in inventory if i['item_id'] == self.selected_item_id), None)
        if not inv_item:
            return

        modal = QuantityModal(item_name=item['name'], max_quantity=inv_item['quantity'])
        modal.title = f"Sell {item['name']}"
        modal.quantity_input.label = f"How many? ({sell_price} 🪙 each)"
        await interaction.response.send_modal(modal)
        await modal.wait()

        quantity = modal.quantity
        if quantity <= 0:
            return

        await db_cog.remove_item_from_inventory(self.user_id, self.selected_item_id, quantity, inv_item.get('item_data'))
        total_earned = sell_price * quantity
        await db_cog.add_coins(self.user_id, total_earned)
        self.selected_item_id = None
        await self.message.edit(
            content=f"✅ Sold **{quantity}x {item['name']}** for **{total_earned} 🪙**.",
            embed=await self.build_embed(), view=self
        )

    async def close_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            await self.message.delete()
        except (discord.NotFound, discord.HTTPException):
            pass
        self.stop()

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except (discord.NotFound, discord.HTTPException):
                pass
