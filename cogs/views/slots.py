# cogs/views/slots.py
#
# Slot machine — solo only, no shared table (each pull is entirely
# personal, nothing to bet alongside anyone else on). Shaped like
# Blackjack's bet-picker: preset amounts + a Custom Bet modal, deduct
# and resolve at bet time, no lingering game state afterward.
#
# The "spin" is a sequence of message edits showing progressively more
# locked reels, not real animation — Discord can't tween between
# states, every step is a hard cut. Same technique as Baccarat's
# card-by-card reveal, just paced faster since there's no comparable
# drama to a single reel landing.
#
# The interaction is deferred immediately, before any DB work — lesson
# learned live from Baccarat's bet modal, where a chain of sequential
# DB calls before ever acknowledging the interaction could (and did)
# outlast Discord's 3-second ack window and kill the interaction
# outright. Also guards against clicking a second preset bet button
# before the first spin's reveal finishes — not a money-safety issue
# (each spin still settles correctly), but two spins' reveal frames
# editing the same message at once would look broken.

import asyncio
import random

import discord

from data.slots import spin_reels, payout_multiplier, TRIPLE_PAYOUT, SYMBOL_WEIGHTS

MIN_BET = 10
BET_PRESETS = [50, 100, 250, 500, 1000]
REVEAL_DELAY_SECONDS = 0.6
BET_VIEW_TIMEOUT_SECONDS = 120

_DECORATIVE_SYMBOLS = list(SYMBOL_WEIGHTS.keys())  # unweighted — these frames are cosmetic, the real outcome is already decided


def slots_bet_embed(balance: int) -> discord.Embed:
    payout_lines = "\n".join(
        f"{symbol}{symbol}{symbol} — {mult}x" for symbol, mult in sorted(TRIPLE_PAYOUT.items(), key=lambda kv: kv[1])
    )
    return discord.Embed(
        title="🎰 Slots",
        description=(
            f"💰 **Your balance:** {balance:,} chips\n\n"
            f"Pick a bet amount, or set a custom one.\n\n"
            f"**Payouts (triple only):**\n{payout_lines}"
        ),
        color=discord.Color.gold(),
    )


def _spin_embed(reels: list, note: str, balance_line: str | None = None) -> discord.Embed:
    reel_text = "  ".join(f"[ {s} ]" for s in reels)
    description = f"{reel_text}\n\n*{note}*"
    if balance_line:
        description += f"\n\n{balance_line}"
    return discord.Embed(title="🎰 Slots", description=description, color=discord.Color.gold())


async def start_spin(interaction: discord.Interaction, db_cog, bet: int):
    # Defer now, before any DB work — see module docstring.
    await interaction.response.defer()

    balance_after_bet = await db_cog.add_chips(interaction.user.id, -bet)

    final_reels = spin_reels()
    multiplier = payout_multiplier(final_reels)
    credit = bet * multiplier
    final_balance = balance_after_bet
    if credit > 0:
        final_balance = await db_cog.add_chips(interaction.user.id, credit)

    def random_reels():
        return [random.choice(_DECORATIVE_SYMBOLS) for _ in range(3)]

    frames = [
        _spin_embed(random_reels(), "Spinning..."),
        _spin_embed(random_reels(), "Spinning..."),
    ]
    frames.append(_spin_embed(
        [final_reels[0], *random_reels()[1:]], f"Reel 1 locks: {final_reels[0]}"
    ))
    frames.append(_spin_embed(
        [final_reels[0], final_reels[1], random_reels()[2]], f"Reel 2 locks: {final_reels[1]}"
    ))

    net = credit - bet
    if multiplier > 0:
        result_note = f"🏆 {multiplier}x — you win {credit:,} chips! (net +{net:,})"
    else:
        result_note = f"No match — you lost {bet:,} chips. Try again!"
    frames.append(_spin_embed(final_reels, result_note, f"💰 Balance: {final_balance:,} chips"))

    await interaction.edit_original_response(embed=frames[0], view=None)
    for embed in frames[1:]:
        await asyncio.sleep(REVEAL_DELAY_SECONDS)
        await interaction.edit_original_response(embed=embed, view=None)


class BetPresetButton(discord.ui.Button):
    def __init__(self, amount: int, *, label: str | None = None, all_in: bool = False):
        super().__init__(
            label=label or f"{amount:,}",
            style=discord.ButtonStyle.success if all_in else discord.ButtonStyle.primary,
            emoji="🎰",
        )
        self.amount = amount

    async def callback(self, interaction: discord.Interaction):
        view: SlotsBetView = self.view
        if view.spun:
            await interaction.response.send_message("This bet's already spinning — open Slots again for another pull.", ephemeral=True)
            return

        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.amount:
            await interaction.response.send_message(
                f"You don't have {self.amount:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return

        view.spun = True
        await start_spin(interaction, db_cog, self.amount)


class CustomBetModal(discord.ui.Modal, title="Pull the Lever"):
    amount = discord.ui.TextInput(label="Bet amount", placeholder="e.g. 100", max_length=10)

    def __init__(self, bet_view: "SlotsBetView"):
        super().__init__()
        self.bet_view = bet_view

    async def on_submit(self, interaction: discord.Interaction):
        view = self.bet_view
        if view.spun:
            await interaction.response.send_message("This bet's already spinning — open Slots again for another pull.", ephemeral=True)
            return

        db_cog = interaction.client.get_cog('Database')
        try:
            bet = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message("Bet amount must be a number.", ephemeral=True)
            return

        if bet < MIN_BET:
            await interaction.response.send_message(f"Minimum bet is {MIN_BET:,} chips.", ephemeral=True)
            return

        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if bet > wallet["balance"]:
            await interaction.response.send_message(
                f"You don't have {bet:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return

        view.spun = True
        await start_spin(interaction, db_cog, bet)


class CustomBetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Custom Bet", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        view: SlotsBetView = self.view
        if view.spun:
            await interaction.response.send_message("This bet's already spinning — open Slots again for another pull.", ephemeral=True)
            return
        await interaction.response.send_modal(CustomBetModal(view))


class BackToCasinoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to Casino", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        from cogs.casino import casino_embed, CasinoView  # local import avoids a circular import
        embed = casino_embed("🎰 Casino", "Pick an option below to get started.")
        await interaction.response.edit_message(embed=embed, view=CasinoView())


class SlotsBetView(discord.ui.View):
    def __init__(self, balance: int):
        super().__init__(timeout=BET_VIEW_TIMEOUT_SECONDS)
        self.spun = False
        for amount in BET_PRESETS:
            if amount <= balance:
                self.add_item(BetPresetButton(amount))
        if balance >= MIN_BET:
            self.add_item(BetPresetButton(balance, label=f"All In ({balance:,})", all_in=True))
        self.add_item(CustomBetButton())
        self.add_item(BackToCasinoButton())
