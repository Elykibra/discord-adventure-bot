# cogs/game.py
# Handles the /start command for new players.

import discord, asyncio
from discord import app_commands
from discord.ext import commands
import random
import traceback

# --- REFACTORED IMPORTS ---
from utils.constants import PET_DESCRIPTIONS
from data.pets import PET_DATABASE
from utils.helpers import get_pet_image_url, get_status_bar
from data.abilities import STARTER_TALENTS



# A helper list to get only the starter pets from the database
STARTER_PETS_LIST = [pet for pet in PET_DATABASE.values() if pet.get('rarity') == 'Starter']


class NameModal(discord.ui.Modal):
    def __init__(self, title: str, label: str, min_len: int, max_len: int, on_submit):
        super().__init__(title=title, timeout=120)
        self.on_submit_callback = on_submit
        self.input = discord.ui.TextInput(
            label=label, placeholder="Enter your name",
            min_length=min_len, max_length=max_len, required=True
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.on_submit_callback(interaction, self.input.value)

class Game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- Session message helpers (one message UI) ----------

    async def _ensure_session_message(self, interaction: discord.Interaction) -> int:
        """Return the session message id, creating it if needed."""
        user_id = interaction.user.id
        repo = self.bot.repo
        msg_id = await repo.get_session_message_id(user_id)
        if msg_id:
            return msg_id

        # We already deferred in /start; create the initial ephemeral message now.
        await interaction.edit_original_response(content="…")
        msg = await interaction.original_response()
        await repo.set_session_message_id(user_id, msg.id)
        return msg.id

    async def _edit_session(self, interaction: discord.Interaction, *, content: str, view: discord.ui.View | None):
        """Edit the persistent session message regardless of interaction type."""
        msg_id = await self._ensure_session_message(interaction)
        await interaction.followup.edit_message(msg_id, content=content, view=view)

    # ---------- Story rendering ----------

    async def _render_story(self, interaction: discord.Interaction, *, force_step_id: str | None = None):
        user_id = interaction.user.id
        repo = self.bot.repo
        narrative = self.bot.narratives["section_0"]

        # Ensure player exists
        player = await repo.get_player(user_id)
        if not player:
            first_step = narrative.first_step_id()
            await repo.create_player(user_id, {
                "name": interaction.user.display_name,
                "section_id": "section_0",
                "story_step_id": first_step,
                "energy": 10,
                "max_energy": 10,
            })
            player = await repo.get_player(user_id)

        state = await repo.get_story_state(user_id)
        step_id = force_step_id or state["story_step_id"]
        step = narrative.get_step(step_id)

        def render_text(t: str) -> str:
            if not t:
                return ""
            return t.replace("{player_name}", player.get("name") or interaction.user.display_name)

        # --- NARRATION ---
        if step.get("type") == "narration":
            text = render_text(step.get("text", ""))
            next_id = step.get("next")

            if not next_id:
                await self._edit_session(interaction, content=text, view=None)
                return

            view = discord.ui.View(timeout=120)
            btn = discord.ui.Button(label="Continue", style=discord.ButtonStyle.primary)

            async def on_click(inter: discord.Interaction, to_next=next_id, current_step=step):
                # Look ahead: if next is a modal, DO NOT defer; show modal directly.
                nxt_step = narrative.get_step(to_next)
                if nxt_step.get("type") == "modal":
                    await narrative.apply_effects(user_id, current_step.get("effects"))
                    await repo.set_story_state(user_id, "section_0", to_next)
                    await self._render_story(inter, force_step_id=to_next)
                    return

                # Non-modal: safe to defer, then render next step
                await inter.response.defer(ephemeral=True)
                await narrative.apply_effects(user_id, current_step.get("effects"))
                await repo.set_story_state(user_id, "section_0", to_next)
                await self._render_story(inter, force_step_id=to_next)

            btn.callback = on_click
            view.add_item(btn)
            await self._edit_session(interaction, content=text, view=view)
            return

        # --- MODAL (e.g., name input) ---
        if step.get("type") == "modal":
            title = step.get("modal_title", "Enter Name")
            label = step.get("modal_label", "Name")
            min_len = int(step.get("modal_min", 2))
            max_len = int(step.get("modal_max", 16))
            next_id = step.get("next")

            # IMPORTANT: do NOT defer before sending a modal
            self_outer = self
            narrative_outer = narrative
            repo_outer = repo

            class NameModal(discord.ui.Modal):
                def __init__(self, _title, _label, _min, _max):
                    super().__init__(title=_title, timeout=120)
                    self.input = discord.ui.TextInput(
                        label=_label, placeholder="Enter your name",
                        min_length=_min, max_length=_max, required=True
                    )
                    self.add_item(self.input)

                async def on_submit(self, inter: discord.Interaction):
                    # We are now in the modal submit interaction → defer then follow-up edit
                    await inter.response.defer(ephemeral=True)
                    await narrative_outer.apply_effects(user_id, step.get("effects"), modal_value=self.input.value)
                    if next_id:
                        await repo_outer.set_story_state(user_id, "section_0", next_id)
                        await self_outer._render_story(inter, force_step_id=next_id)
                    else:
                        await self_outer._edit_session(inter, content="Name saved.", view=None)

            await interaction.response.send_modal(NameModal(title, label, min_len, max_len))
            return

        # --- CHOICE (e.g., starter selection) ---
        if step.get("type") == "choice":
            prompt = render_text(step.get("prompt", "Choose:"))
            view = discord.ui.View(timeout=120)

            for opt in step.get("options", []):
                label = opt["label"]
                eff = opt.get("effects")
                to_next = opt.get("next") or step.get("next") or step_id

                button = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)

                async def handler(inter: discord.Interaction, eff_=eff, next_id_=to_next):
                    nxt_step = narrative.get_step(next_id_)
                    if nxt_step.get("type") == "modal":
                        await narrative.apply_effects(user_id, eff_)
                        await repo.set_story_state(user_id, "section_0", next_id_)
                        await self._render_story(inter, force_step_id=next_id_)
                        return

                    await inter.response.defer(ephemeral=True)
                    await narrative.apply_effects(user_id, eff_)
                    await repo.set_story_state(user_id, "section_0", next_id_)
                    await self._render_story(inter, force_step_id=next_id_)

                button.callback = handler
                view.add_item(button)

            await self._edit_session(interaction, content=prompt, view=view)
            return

        # --- DYNAMIC CHOICE (e.g., starter talents) ---
        if step.get("type") == "dyn_choice":
            prompt = render_text(step.get("prompt", "Choose:"))
            view = discord.ui.View(timeout=120)

            # Read selected starter from flags (starter_pet:<Name>)
            player = await repo.get_player(user_id)
            flags = player.get("flags", set())
            if not isinstance(flags, set):
                flags = set(flags or [])
            starter = next((f.split(":", 1)[1] for f in flags
                            if isinstance(f, str) and f.startswith("starter_pet:")), None)

            talents = STARTER_TALENTS.get(starter, [])
            if not talents:
                await self._edit_session(interaction, content="No talents available for your starter.", view=None)
                return

            for t in talents:
                label = t["name"]
                mech = t.get("mechanic_name", label)

                button = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)

                async def handler(inter: discord.Interaction, mech_=mech):
                    await inter.response.defer(ephemeral=True)
                    await narrative.apply_effects(
                        user_id, [{"op": "set_flag", "flag": f"starter_talent:{mech_}"}]
                    )
                    next_id = step.get("next") or step_id
                    await repo.set_story_state(user_id, "section_0", next_id)
                    await self._render_story(inter, force_step_id=next_id)

                button.callback = handler
                view.add_item(button)

            await self._edit_session(interaction, content=prompt, view=view)
            return

        # --- Fallback ---
        await self._edit_session(interaction, content="⚠️ This part of the story is under construction.", view=None)

    # ---------- Slash command ----------

    @app_commands.command(name="start", description="Begin your adventure.")
    async def start(self, interaction: discord.Interaction):
        # Create the ephemeral session message; subsequent steps edit it
        await interaction.response.defer(ephemeral=True)
        await self._render_story(interaction)


async def setup(bot):
    await bot.add_cog(Game(bot))