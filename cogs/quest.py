# cogs/quest.py
from discord.ext import commands

class Quest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quest")
    async def quest(self, ctx):
        await ctx.send("Quest system coming soon!")

def setup(bot):
    bot.add_cog(Quest(bot))
