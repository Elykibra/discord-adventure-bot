# cogs/crafting.py

import discord
from discord import app_commands
from discord.ext import commands

# --- REFACTORED IMPORTS ---
# These paths are already correct for our new structure.
from data.recipes import RECIPES
from data.items import ITEMS


class Crafting(commands.Cog):
    """A cog for managing the game's crafting system."""

    def __init__(self, bot):
        self.bot = bot

    # --- NEW: Autocomplete Function ---
    # This function will suggest craftable items to the user as they type.
    async def item_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[
        app_commands.Choice[str]]:
        choices = []
        # We iterate through our RECIPES data
        for item_id, recipe_data in RECIPES.items():
            item_name = ITEMS.get(item_id, {}).get('name', item_id)
            # If the user's input matches the start of a craftable item's name...
            if current.lower() in item_name.lower():
                # ...we add it as a choice.
                choices.append(app_commands.Choice(name=item_name, value=item_id))

        # Return the first 25 matches
        return choices[:25]

    # --- REFACTOR: Converted to Slash Command ---
    @app_commands.command(name="craft", description="Craft a new item from raw materials.")
    @app_commands.autocomplete(item_name=item_name_autocomplete)  # Link the autocomplete function
    async def craft(self, interaction: discord.Interaction, item_name: str):
        """Allows a player to craft an item if they have the necessary materials."""
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        player_data = await db_cog.get_player(interaction.user.id)
        if not player_data:
            await interaction.followup.send("You don't have a profile yet! Use `/start` to begin.", ephemeral=True)
            return

        # The item_name we receive from the autocomplete is the item_id (e.g., "greater_potion")
        recipe = RECIPES.get(item_name)
        if not recipe:
            await interaction.followup.send(f"I don't know the recipe for that item. Please select one from the list.",
                                            ephemeral=True)
            return

        player_inventory = await db_cog.get_player_inventory(interaction.user.id)
        player_inventory_dict = {item['item_id']: item['quantity'] for item in player_inventory}

        # The core logic for checking ingredients remains the same, as it was well-written.
        missing_items = []
        for ingredient_id, required_qty in recipe['ingredients'].items():
            if player_inventory_dict.get(ingredient_id, 0) < required_qty:
                missing_items.append(f"{required_qty}x {ITEMS[ingredient_id]['name']}")

        if missing_items:
            missing_text = "\n".join(missing_items)
            await interaction.followup.send(
                f"You are missing the following ingredients to craft **{ITEMS[item_name]['name']}**:\n{missing_text}",
                ephemeral=True
            )
            return

        # Consume ingredients and add the crafted item
        for ingredient_id, required_qty in recipe['ingredients'].items():
            await db_cog.remove_item_from_inventory(interaction.user.id, ingredient_id, required_qty)

        await db_cog.add_item_to_inventory(interaction.user.id, item_name, 1)

        await interaction.followup.send(f"You successfully crafted **1x {ITEMS[item_name]['name']}**!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Crafting(bot))