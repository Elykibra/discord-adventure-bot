import discord
from discord.ext import commands
from .views.inventory import BagView

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix command: !bag
    @commands.command(name="bag")
    async def bag(self, ctx: commands.Context):
        db_cog = self.bot.get_cog("Database")
        if not db_cog:
            return await ctx.send("⚠️ Database not loaded. Please contact an administrator.")

        player_data = await db_cog.get_player(ctx.author.id)
        inventory = await db_cog.get_player_inventory(ctx.author.id)

        view = BagView(bot=self.bot, user_id=ctx.author.id, player_data=player_data, inventory=inventory)
        embed = view.create_embed()
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg  # fallback for modals

async def setup(bot):
    await bot.add_cog(Inventory(bot))