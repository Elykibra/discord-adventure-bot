# cogs/gameplay/minigames.py
# This cog is for all the fun mini-games a player can engage in.

import discord
from discord.ext import commands
import random
import asyncio


class Minigames(commands.Cog):
    """
    A cog for minigames.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fish", help="Go fishing and see what you can catch!")
    async def fish_minigame(self, ctx):
        """
        A simple fishing minigame.
        """
        db_cog = self.bot.get_cog('Database')
        if not db_cog:
            return await ctx.send("Database is not loaded. Please try again later.")

        player_data = await db_cog.get_player(ctx.author.id)
        if not player_data:
            return await ctx.send("You don't have a profile yet!")

        await ctx.send("You cast your line into the murky waters... 🎣")
        await asyncio.sleep(random.uniform(3, 7))  # Wait for a random amount of time

        if random.randint(1, 100) > 70:
            # Player failed to catch anything
            await ctx.send("Nothing bit the bait. Better luck next time!")
        else:
            # Player caught something
            catch = random.choice(["Old Boot", "Shiny Pebble", "Small Fish", "Giant Fish"])
            if catch == "Giant Fish":
                reward_coins = 50
                reward_xp = 20
            else:
                reward_coins = 10
                reward_xp = 5

            await db_cog.add_coins(ctx.author.id, reward_coins)
            # You would also need to add logic to update XP
            await ctx.send(f"You reeled in a **{catch}**! You got **{reward_coins}** coins!")


async def setup(bot):
    await bot.add_cog(Minigames(bot))