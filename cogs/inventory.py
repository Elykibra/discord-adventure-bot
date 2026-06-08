import discord
from discord import app_commands
from discord.ext import commands
from .views.inventory import BagView

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _open_bag(self, user_id: int, channel):
        """Shared logic for both prefix and slash bag commands."""
        db_cog = self.bot.get_cog("Database")
        player_data = await db_cog.get_player(user_id)
        if not player_data:
            return None, None
        inventory = await db_cog.get_player_inventory(user_id)
        main_pet_data = None
        if player_data.get('main_pet_id'):
            main_pet_data = await db_cog.get_pet(player_data['main_pet_id'])
        view = BagView(bot=self.bot, user_id=user_id, player_data=player_data,
                       main_pet_data=main_pet_data, inventory=inventory, channel=channel)
        await view.initial_setup()
        embed = view.create_embed()
        return view, embed

    # Slash command: /bag
    @app_commands.command(name="bag", description="Open your inventory bag.")
    async def bag_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        view, embed = await self._open_bag(interaction.user.id, interaction.channel)
        if not view:
            return await interaction.followup.send("You don't have a character yet! Use `/start` to begin.", ephemeral=True)
        msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = msg

    # Prefix command: !bag
    @commands.command(name="bag")
    async def bag(self, ctx: commands.Context):
        view, embed = await self._open_bag(ctx.author.id, ctx.channel)
        if not view:
            return await ctx.send("You don't have a character yet! Use `/start` to begin.")
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

async def setup(bot):
    await bot.add_cog(Inventory(bot))