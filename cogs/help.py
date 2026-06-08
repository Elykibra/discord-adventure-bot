# cogs/help.py
# A /help command that lists every command, split by player vs admin.

import discord
from discord import app_commands
from discord.ext import commands


PLAYER_COMMANDS = [
    # (name, description)
    ("/start",      "Create your character and choose your starter pet."),
    ("/adventure",  "Open your current location — explore, fight, rest, travel."),
    ("/character",  "View your profile, pet status, bag, and crafting bench."),
    ("/bag",        "Open your inventory bag directly."),
    ("/quests",     "Check your active quest log and current objectives."),
    ("/pets",       "Manage and browse all your companions."),
    ("/fish",       "Go fishing — a chance at items and rare encounters."),
    ("/event",      "See information about the current global event."),
    ("/general",    "General bot info and utility menu."),
]

ADMIN_COMMANDS = [
    ("/heal",             "Heal your main pet to full HP."),
    ("/energy",           "Restore your energy to full."),
    ("/additem",          "Add an item directly to your inventory."),
    ("/addcoins",         "Add coins to your balance."),
    ("/setlevel",         "Set your main pet to a specific level."),
    ("/learnskill",       "Teach your main pet a skill by ID."),
    ("/learnrecipe",      "Teach your character a crafting recipe."),
    ("/encounter",        "Force-start a battle with a specific pet species."),
    ("/teleport",         "Teleport to any town instantly."),
    ("/quest",            "Manually start, complete, or reset a quest."),
    ("/inspect",          "View a full data summary for any user."),
    ("/listplayers",      "List all registered players."),
    ("/reset",            "Wipe your own character data and start over."),
    ("/deleteplayerdata", "Delete all data for a specific user."),
    ("/exportdata",       "Export a user's data to a JSON file."),
    ("/sync",             "Re-sync the slash command tree."),
    ("/craft",            "Craft an item by ID (testing shortcut)."),
]


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows every command in Aethelgard.")
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # --- Player commands embed ---
        player_embed = discord.Embed(
            title="📖 Aethelgard — Command Reference",
            color=discord.Color.blurple()
        )

        player_lines = "\n".join(
            f"`{name}` — {desc}" for name, desc in PLAYER_COMMANDS
        )
        player_embed.add_field(
            name="🎮 Player Commands",
            value=player_lines,
            inline=False
        )

        # Only show admin section to the bot owner
        app_info = await self.bot.application_info()
        is_owner = interaction.user.id == app_info.owner.id

        if is_owner:
            admin_lines = "\n".join(
                f"`{name}` — {desc}" for name, desc in ADMIN_COMMANDS
            )
            player_embed.add_field(
                name="🔧 Admin / Cheat Commands  *(owner only)*",
                value=admin_lines,
                inline=False
            )
            player_embed.set_footer(text="Admin commands are only visible to you.")
        else:
            player_embed.set_footer(text="Use /start to begin your adventure!")

        await interaction.followup.send(embed=player_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
