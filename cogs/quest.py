# cogs/quest.py
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from data.quests import QUESTS

TYPE_EMOJI = {
    'main':              '⭐',
    'side':              '🔵',
    'repeatable_bounty': '🔄',
}
PAGE_SIZE = 5  # quests per page


def _build_active_embed(active_quests: list, page: int, total_pages: int) -> discord.Embed:
    embed = discord.Embed(title="📜 Quest Log — Active", color=discord.Color.dark_gold())
    if not active_quests:
        embed.description = "*All caught up — no active quests right now.*"
        return embed

    embed.description = "Here are your current objectives:"
    start = page * PAGE_SIZE
    for quest in active_quests[start: start + PAGE_SIZE]:
        quest_id = quest['quest_id']
        quest_data = next(
            (q for town_quests in QUESTS.values() for q_id, q in town_quests.items() if q_id == quest_id), None)
        if not quest_data:
            continue

        progress = quest['progress']
        current_obj_index = progress.get('count', 0)
        objectives = quest_data.get('objectives', [])

        if current_obj_index < len(objectives):
            objective = objectives[current_obj_index]
            objective_text = objective['text']
            if 'required_count' in objective:
                current_count = progress.get('current_count', 0)
                objective_text += f" ({current_count}/{objective['required_count']})"

            emoji = TYPE_EMOJI.get(quest_data.get('type', 'main'), '📜')
            embed.add_field(
                name=f"{emoji} {quest_data['title']}",
                value=f"└─ Objective: {objective_text}",
                inline=False
            )

    if total_pages > 1:
        embed.set_footer(text=f"Page {page + 1} of {total_pages}")
    return embed


def _build_completed_embed(completed_quests: list, page: int, total_pages: int) -> discord.Embed:
    embed = discord.Embed(title="📜 Quest Log — Completed", color=discord.Color.dark_gold())
    if not completed_quests:
        embed.description = "*No completed quests yet. Get out there!*"
        return embed

    embed.description = f"You've finished **{len(completed_quests)}** quest(s)."
    start = page * PAGE_SIZE
    for quest in completed_quests[start: start + PAGE_SIZE]:
        quest_id = quest['quest_id']
        quest_data = next(
            (q for town_quests in QUESTS.values() for q_id, q in town_quests.items() if q_id == quest_id), None)
        if not quest_data:
            continue

        emoji = TYPE_EMOJI.get(quest_data.get('type', 'main'), '📜')
        embed.add_field(
            name=f"✅ {quest_data['title']}",
            value=f"└─ *{quest_data.get('description', 'Completed.')}*",
            inline=False
        )

    if total_pages > 1:
        embed.set_footer(text=f"Page {page + 1} of {total_pages}")
    return embed


def _page_count(quest_list: list) -> int:
    return max(1, -(-len(quest_list) // PAGE_SIZE))  # ceiling division


class QuestLogView(discord.ui.View):
    """Two-tab quest log with per-tab pagination."""

    def __init__(self, active_quests: list, completed_quests: list):
        super().__init__(timeout=120)
        self.active_quests    = active_quests
        self.completed_quests = completed_quests
        self._tab  = "active"
        self._page = 0
        self._rebuild()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _current_list(self) -> list:
        return self.active_quests if self._tab == "active" else self.completed_quests

    def _total_pages(self) -> int:
        return _page_count(self._current_list())

    def _rebuild(self):
        """Clear and re-add all buttons with correct disabled states."""
        self.clear_items()

        # Tab buttons (row 0)
        active_btn = discord.ui.Button(
            label="Active",
            style=discord.ButtonStyle.primary if self._tab == "active" else discord.ButtonStyle.secondary,
            disabled=(self._tab == "active"),
            row=0,
        )
        active_btn.callback = self._on_active
        self.add_item(active_btn)

        # Only show Completed tab if there's something there
        if self.completed_quests:
            completed_btn = discord.ui.Button(
                label=f"Completed ({len(self.completed_quests)})",
                style=discord.ButtonStyle.primary if self._tab == "completed" else discord.ButtonStyle.secondary,
                disabled=(self._tab == "completed"),
                row=0,
            )
            completed_btn.callback = self._on_completed
            self.add_item(completed_btn)

        # Pagination buttons (row 1) — only shown when there's more than one page
        total = self._total_pages()
        if total > 1:
            prev_btn = discord.ui.Button(
                label="◀ Prev",
                style=discord.ButtonStyle.secondary,
                disabled=(self._page == 0),
                row=1,
            )
            prev_btn.callback = self._on_prev

            page_btn = discord.ui.Button(
                label=f"{self._page + 1} / {total}",
                style=discord.ButtonStyle.secondary,
                disabled=True,  # just a label
                row=1,
            )

            next_btn = discord.ui.Button(
                label="Next ▶",
                style=discord.ButtonStyle.secondary,
                disabled=(self._page >= total - 1),
                row=1,
            )
            next_btn.callback = self._on_next

            self.add_item(prev_btn)
            self.add_item(page_btn)
            self.add_item(next_btn)

    def _current_embed(self) -> discord.Embed:
        total = self._total_pages()
        if self._tab == "active":
            return _build_active_embed(self.active_quests, self._page, total)
        return _build_completed_embed(self.completed_quests, self._page, total)

    # ------------------------------------------------------------------ #
    # Button callbacks
    # ------------------------------------------------------------------ #

    async def _on_active(self, interaction: discord.Interaction):
        self._tab  = "active"
        self._page = 0
        self._rebuild()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    async def _on_completed(self, interaction: discord.Interaction):
        self._tab  = "completed"
        self._page = 0
        self._rebuild()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    async def _on_prev(self, interaction: discord.Interaction):
        self._page = max(0, self._page - 1)
        self._rebuild()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    async def _on_next(self, interaction: discord.Interaction):
        self._page = min(self._total_pages() - 1, self._page + 1)
        self._rebuild()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quests", description="View your current quest log.")
    async def quests(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog('Database')

        all_quests = await db_cog.get_active_quests(interaction.user.id)

        active_quests    = [q for q in all_quests if q['progress'].get('status') != 'completed']
        completed_quests = [q for q in all_quests if q['progress'].get('status') == 'completed']

        if not all_quests:
            embed = discord.Embed(
                title="📜 Quest Log",
                description="You have no quests yet.\n*Explore the world and talk to people to find new adventures!*",
                color=discord.Color.dark_gold()
            )
            msg = await interaction.followup.send(embed=embed, ephemeral=True)
            async def _dismiss():
                await asyncio.sleep(60)
                try: await msg.delete()
                except discord.NotFound: pass
            asyncio.create_task(_dismiss())
            return

        view  = QuestLogView(active_quests, completed_quests)
        embed = _build_active_embed(active_quests, 0, _page_count(active_quests))
        msg   = await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        async def _dismiss():
            await asyncio.sleep(120)
            try: await msg.delete()
            except discord.NotFound: pass
        asyncio.create_task(_dismiss())


async def setup(bot):
    await bot.add_cog(Quests(bot))
