# cogs/voice_earnings.py

import discord
from discord.ext import commands
from datetime import datetime, timezone

VOICE_CHIPS_PER_MINUTE = 2


class VoiceEarnings(commands.Cog):
    """Passively grants casino chips for time spent in a voice channel."""

    def __init__(self, bot):
        self.bot = bot
        self.session_start: dict[int, datetime] = {}  # user_id -> joined_at
        self._seeded = False

    def _credit_amount(self, joined_at: datetime) -> int:
        elapsed_minutes = (datetime.now(timezone.utc) - joined_at).total_seconds() // 60
        return int(elapsed_minutes) * VOICE_CHIPS_PER_MINUTE

    async def _pay_out(self, user_id: int):
        joined_at = self.session_start.pop(user_id, None)
        if not joined_at:
            return
        amount = self._credit_amount(joined_at)
        if amount > 0:
            db_cog = self.bot.get_cog('Database')
            if db_cog:
                await db_cog.add_chips(user_id, amount)

    @commands.Cog.listener()
    async def on_ready(self):
        # Seed anyone already in a voice channel when the bot (re)connects,
        # so an in-progress hangout keeps earning after a restart instead of
        # silently stopping until they rejoin.
        if self._seeded:
            return
        self._seeded = True
        now = datetime.now(timezone.utc)
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if not member.bot:
                        self.session_start[member.id] = now

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                     before: discord.VoiceState, after: discord.VoiceState):
        if member.bot or before.channel == after.channel:
            return  # ignore bots and non-channel changes (mute/deafen toggles, etc.)

        if before.channel is not None:
            await self._pay_out(member.id)

        if after.channel is not None:
            self.session_start[member.id] = datetime.now(timezone.utc)


async def setup(bot):
    await bot.add_cog(VoiceEarnings(bot))
