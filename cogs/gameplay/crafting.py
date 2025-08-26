# cogs/gameplay/crafting.py
# This cog handles the crafting system, allowing players to create new items.

import discord
from discord.ext import commands
from data.recipes import RECIPES
from data.items import ITEMS


class Crafting(commands.Cog):
    """
    A cog for managing the crafting system.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="craft", help="Craft a new item from your inventory.")
    async def craft_item(self, ctx, item_name: str):
        """
        Allows a player to craft an item if they have the necessary materials.
        """
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await ctx.send("Database is not loaded. Please try again later.")

        player_data = await db_cog.get_player(ctx.author.id)
        if not player_data:
            return await ctx.send("You don't have a profile yet!")

        # Normalize the item name to match recipe keys
        item_key = item_name.lower().replace(" ", "_")

        if item_key not in RECIPES:
            return await ctx.send(f"I don't know the recipe for '{item_name}'.")

        recipe = RECIPES[item_key]
        player_inventory = await db_cog.get_player_inventory(ctx.author.id)

        # Convert list of tuples to a dictionary for easier lookup
        player_inventory_dict = {item: qty for item, qty in player_inventory}

        # Check if the player has all the required ingredients
        can_craft = True
        missing_items = []
        for ingredient, quantity in recipe['ingredients'].items():
            if player_inventory_dict.get(ingredient, 0) < quantity:
                can_craft = False
                missing_items.append(f"{quantity}x {ITEMS[ingredient]['name']}")

        if not can_craft:
            missing_text = "\n".join(missing_items)
            return await ctx.send(
                f"You are missing the following ingredients to craft **{ITEMS[item_key]['name']}**:\n{missing_text}")

        # Consume ingredients and add the crafted item
        for ingredient, quantity in recipe['ingredients'].items():
            await db_cog.remove_item_from_inventory(ctx.author.id, ingredient, quantity)

        await db_cog.add_item_to_inventory(ctx.author.id, item_key, 1)

        await ctx.send(f"You successfully crafted a **{ITEMS[item_key]['name']}**!")


async def setup(bot):
    await bot.add_cog(Crafting(bot))