from discord.ext import commands
from core.inventory import Bag

# Temporary player bags (later swap to DB)
player_bags = {}

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bag(self, ctx):
        user_id = str(ctx.author.id)
        bag = player_bags.get(user_id, Bag())
        await ctx.send(f"Bag: {len(bag.items)}/{bag.slots} items")

    @commands.command()
    async def additem(self, ctx, *, item_name):
        user_id = str(ctx.author.id)
        bag = player_bags.get(user_id, Bag())
        success = bag.add_item(item_name)
        player_bags[user_id] = bag
        if success:
            await ctx.send(f"Added {item_name} to your bag.")
        else:
            await ctx.send("Your bag is full!")

async def setup(bot):
    await bot.add_cog(Inventory(bot))
