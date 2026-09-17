# cogs/game_invite.py

import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

DEFAULT_CLOSE_MINUTES = 5  # invites auto-close 5 minutes after posting unless the host cancels first

# Each entry describes how that game's lobby is actually joined, so the
# modal asks for the right thing instead of a one-size-fits-all "code".
# extra_label/placeholder describe the one flexible follow-up field;
# leave extra_label as "" for games with no useful third field at all.
GAME_CONFIG = {
    "valorant": {
        "display": "Valorant", "emoji": "🔫",
        "extra_label": "Lobby Code", "extra_placeholder": "e.g. AB12CD",
    },
    "mobile legends": {
        "display": "Mobile Legends", "emoji": "⚔️",
        "extra_label": "In-Game ID / Add Me", "extra_placeholder": "e.g. 123456789 (1234)",
    },
    "league of legends": {
        "display": "League of Legends", "emoji": "🐉",
        "extra_label": "Summoner Name / Add Me", "extra_placeholder": "e.g. Faker#KR1",
    },
    "dota 2": {
        "display": "Dota 2", "emoji": "🪓",
        "extra_label": "Friend Code / Steam", "extra_placeholder": "e.g. steamcommunity.com/id/...",
    },
    "minecraft": {
        "display": "Minecraft", "emoji": "⛏️",
        "extra_label": "Server IP", "extra_placeholder": "e.g. play.myserver.net",
    },
    "counter-strike 2": {
        "display": "Counter-Strike 2", "emoji": "💣",
        "extra_label": "Lobby Code", "extra_placeholder": "e.g. CS2-ABCDE-FGHIJ",
    },
    "overwatch 2": {
        "display": "Overwatch 2", "emoji": "🛡️",
        "extra_label": "Battletag", "extra_placeholder": "e.g. Name#1234",
    },
    "genshin impact": {
        "display": "Genshin Impact", "emoji": "⚔️",
        "extra_label": "UID / World Link", "extra_placeholder": "e.g. 800xxxxxxx",
    },
}

OTHER_KEY = "other"
OTHER_CONFIG = {
    "display": None,  # filled in from the modal's free-text Game field
    "emoji": "🎮",
    "extra_label": "Code / Link", "extra_placeholder": "optional",
}


class GameInviteView(discord.ui.View):
    """Live-updating Join/Leave panel attached to a posted game invite."""

    def __init__(self, host: discord.Member, game: str, emoji: str, players_needed: int,
                 extra_label: str, extra_value: str, notes: str, close_minutes: int):
        super().__init__(timeout=close_minutes * 60)
        self.host = host
        self.game = game
        self.emoji = emoji
        self.players_needed = players_needed
        self.extra_label = extra_label
        self.extra_value = extra_value
        self.notes = notes
        self.expires_at = discord.utils.utcnow() + timedelta(minutes=close_minutes)
        self.participants: list[discord.Member] = [host]
        self.message: discord.Message | None = None

    def build_embed(self, *, closed: bool = False, closed_reason: str | None = None) -> discord.Embed:
        full = len(self.participants) >= self.players_needed
        if closed:
            color = discord.Color.dark_grey()
        elif full:
            color = discord.Color.gold()
        else:
            color = discord.Color.green()

        embed = discord.Embed(
            title=f"{self.emoji} {self.game} — Game Invite",
            color=color,
        )
        embed.add_field(name="Host", value=self.host.mention, inline=True)
        embed.add_field(
            name="Players",
            value=f"{len(self.participants)}/{self.players_needed}",
            inline=True,
        )
        if self.extra_value:
            embed.add_field(name=self.extra_label, value=self.extra_value, inline=False)
        if self.notes:
            embed.add_field(name="Notes", value=self.notes, inline=False)

        joined = "\n".join(p.mention for p in self.participants) or "Nobody yet"
        embed.add_field(name="Joined", value=joined, inline=False)

        if closed:
            embed.set_footer(text=closed_reason or "This invite is closed.")
        elif full:
            embed.set_footer(text="Lobby is full! Host can still Cancel, or someone can Leave to free a slot.")
        else:
            expires_ts = int(self.expires_at.timestamp())
            embed.set_footer(text="Click Join to hop in!")
            embed.description = f"Closes <t:{expires_ts}:R> unless the host cancels first."

        return embed

    def _is_full(self) -> bool:
        return len(self.participants) >= self.players_needed

    async def _refresh(self, interaction: discord.Interaction):
        self.join_button.disabled = self._is_full()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="✅")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("You're already in this lobby!", ephemeral=True)
        if self._is_full():
            return await interaction.response.send_message("This lobby is already full.", ephemeral=True)

        self.participants.append(interaction.user)
        await self._refresh(interaction)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.secondary, emoji="🚪")
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.host:
            return await interaction.response.send_message(
                "You're hosting this invite — use Cancel to close it instead.", ephemeral=True
            )
        if interaction.user not in self.participants:
            return await interaction.response.send_message("You're not in this lobby.", ephemeral=True)

        self.participants.remove(interaction.user)
        await self._refresh(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="🛑")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            return await interaction.response.send_message(
                "Only the host can cancel this invite.", ephemeral=True
            )

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            embed=self.build_embed(closed=True, closed_reason=f"Cancelled by {self.host.display_name}."),
            view=self,
        )
        self.stop()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(embed=self.build_embed(closed=True, closed_reason="Invite expired."), view=self)
            except discord.HTTPException:
                pass


async def _post_invite(interaction: discord.Interaction, *, game: str, emoji: str,
                        players_needed: int, extra_label: str, extra_value: str, notes: str,
                        close_minutes: int):
    view = GameInviteView(
        host=interaction.user,
        game=game,
        emoji=emoji,
        players_needed=players_needed,
        extra_label=extra_label,
        extra_value=extra_value,
        notes=notes,
        close_minutes=close_minutes,
    )
    await interaction.response.send_message(
        content="@everyone",
        embed=view.build_embed(),
        view=view,
        allowed_mentions=discord.AllowedMentions(everyone=True),
    )
    view.message = await interaction.original_response()


class KnownGameModal(discord.ui.Modal):
    """Modal for a game we have a tailored config for (no free-text Game field needed)."""

    players_needed = discord.ui.TextInput(label="Players Needed (total, including you)",
                                           placeholder="e.g. 5", max_length=2)
    notes = discord.ui.TextInput(label="Notes (optional)", style=discord.TextStyle.paragraph,
                                  required=False, max_length=300)

    def __init__(self, game_key: str, close_minutes: int):
        config = GAME_CONFIG[game_key]
        super().__init__(title=f"Invite — {config['display']}")
        self.config = config
        self.close_minutes = close_minutes

        if config["extra_label"]:
            self.extra_field = discord.ui.TextInput(
                label=config["extra_label"],
                placeholder=config["extra_placeholder"] or None,
                required=False,
                max_length=100,
            )
            self.add_item(self.extra_field)
        else:
            self.extra_field = None

    async def on_submit(self, interaction: discord.Interaction):
        try:
            needed = int(self.players_needed.value)
        except ValueError:
            return await interaction.response.send_message("Players Needed must be a number.", ephemeral=True)
        if not 2 <= needed <= 25:
            return await interaction.response.send_message("Players Needed must be between 2 and 25.", ephemeral=True)

        await _post_invite(
            interaction,
            game=self.config["display"],
            emoji=self.config["emoji"],
            players_needed=needed,
            extra_label=self.config["extra_label"],
            extra_value=str(self.extra_field.value) if self.extra_field and self.extra_field.value else "",
            notes=str(self.notes.value) if self.notes.value else "",
            close_minutes=self.close_minutes,
        )


class OtherGameModal(discord.ui.Modal):
    game = discord.ui.TextInput(label="Game", placeholder="e.g. Split Fiction", max_length=50)
    players_needed = discord.ui.TextInput(label="Players Needed (total, including you)",
                                           placeholder="e.g. 4", max_length=2)
    extra_field = discord.ui.TextInput(label="Code / Link (optional)", required=False, max_length=100)
    notes = discord.ui.TextInput(label="Notes (optional)", style=discord.TextStyle.paragraph,
                                  required=False, max_length=300)

    def __init__(self, close_minutes: int):
        super().__init__(title="Create a Game Invite")
        self.close_minutes = close_minutes

    async def on_submit(self, interaction: discord.Interaction):
        try:
            needed = int(self.players_needed.value)
        except ValueError:
            return await interaction.response.send_message("Players Needed must be a number.", ephemeral=True)
        if not 2 <= needed <= 25:
            return await interaction.response.send_message("Players Needed must be between 2 and 25.", ephemeral=True)

        await _post_invite(
            interaction,
            game=str(self.game.value),
            emoji=OTHER_CONFIG["emoji"],
            players_needed=needed,
            extra_label=OTHER_CONFIG["extra_label"],
            extra_value=str(self.extra_field.value) if self.extra_field.value else "",
            notes=str(self.notes.value) if self.notes.value else "",
            close_minutes=self.close_minutes,
        )


class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=cfg["display"], value=key, emoji=cfg["emoji"])
            for key, cfg in GAME_CONFIG.items()
        ]
        options.append(discord.SelectOption(label="Other (type it in)", value=OTHER_KEY, emoji="🎮"))
        super().__init__(placeholder="Which game are you forming a lobby for?", options=options)

    async def callback(self, interaction: discord.Interaction):
        game_key = self.values[0]
        if game_key == OTHER_KEY:
            await interaction.response.send_modal(OtherGameModal(DEFAULT_CLOSE_MINUTES))
        else:
            await interaction.response.send_modal(KnownGameModal(game_key, DEFAULT_CLOSE_MINUTES))


class GameSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(GameSelect())


class GameInvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gameinvite", description="Post an invite for others to join your game lobby.")
    async def gameinvite(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Which game are you forming a lobby for?", view=GameSelectView(), ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(GameInvite(bot))
