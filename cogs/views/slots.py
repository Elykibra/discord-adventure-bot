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


def _spin_embed(reels: list, note: str, balance: int) -> discord.Embed:
    reel_text = "  ".join(f"[ {s} ]" for s in reels)
    embed = discord.Embed(title="🎰 Slots", description=f"{reel_text}\n\n*{note}*", color=discord.Color.gold())
    embed.set_footer(text=f"💰 Balance: {balance:,} chips")
    return embed


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

    # Balance already settled above before any animation plays, so every
    # frame up to the last shows the post-bet balance; only the final
    # frame reflects a win's credit, since that's when it actually lands.
    frames = [
        _spin_embed(random_reels(), "Spinning...", balance_after_bet),
        _spin_embed(random_reels(), "Spinning...", balance_after_bet),
    ]
    frames.append(_spin_embed(
        [final_reels[0], *random_reels()[1:]], f"Reel 1 locks: {final_reels[0]}", balance_after_bet
    ))
    frames.append(_spin_embed(
        [final_reels[0], final_reels[1], random_reels()[2]], f"Reel 2 locks: {final_reels[1]}", balance_after_bet
    ))

    net = credit - bet
    if multiplier > 0:
        result_note = f"🏆 {multiplier}x — you win {credit:,} chips! (net +{net:,})"
    else:
        result_note = f"No match — you lost {bet:,} chips. Try again!"
    frames.append(_spin_embed(final_reels, result_note, final_balance))

    await interaction.edit_original_response(embed=frames[0], view=None)
    for embed in frames[1:-1]:
        await asyncio.sleep(REVEAL_DELAY_SECONDS)
        await interaction.edit_original_response(embed=embed, view=None)

    # The last frame gets a fresh result view attached — lets the player
    # spin again (same bet) or change their bet without re-running the
    # command. A brand-new SlotsResultView instance each time means there's
    # nothing to "release" between spins: the old one (and whatever busy
    # state it ended in) is simply discarded once replaced.
    await asyncio.sleep(REVEAL_DELAY_SECONDS)
    result_view = SlotsResultView(bet)
    message = await interaction.edit_original_response(embed=frames[-1], view=result_view)
    result_view.message = message


class SpinAgainButton(discord.ui.Button):
    def __init__(self, bet: int):
        super().__init__(label=f"Spin Again ({bet:,})", style=discord.ButtonStyle.success, emoji="🎰")
        self.bet = bet

    async def callback(self, interaction: discord.Interaction):
        view: SlotsResultView = self.view
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.bet:
            view.busy = False
            await interaction.response.send_message(
                f"You don't have {self.bet:,} chips for another {self.bet:,}-chip spin — "
                f"balance is {wallet['balance']:,}. Try Change Bet for a smaller amount.",
                ephemeral=True,
            )
            return
        await start_spin(interaction, db_cog, self.bet)


class ChangeBetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Change Bet", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        await interaction.response.edit_message(embed=slots_bet_embed(wallet["balance"]), view=SlotsBetView(wallet["balance"]))


class SlotsResultView(discord.ui.View):
    """Shown after a spin resolves — lets the player spin again (same bet)
    or change their bet, without needing to re-run /casino. A fresh
    instance is created for every spin (see start_spin()), so the
    busy-guard below only ever needs to protect ONE spin's duration, not
    a whole reused session — same reasoning as Poker/Baccarat's
    busy-guard, just scoped to a single-use view instead of a long-lived
    one."""

    def __init__(self, bet: int):
        super().__init__(timeout=180)
        self.busy = False
        self.message: discord.Message | None = None
        self.add_item(SpinAgainButton(bet))
        self.add_item(ChangeBetButton())
        self.add_item(BackToCasinoButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    async def on_timeout(self):
        """Grey out Spin Again / Change Bet / Back to Casino once nobody's
        left to click them — otherwise the buttons stay up looking live,
        and clicking a dead one just gets Discord's "didn't respond in
        time" error instead of anything happening."""
        if not self.message:
            return
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass


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
        # `spun` is this view's one-shot lock, same role as `busy` elsewhere
        # in the casino — claim it synchronously, right after the check,
        # before any DB round-trip. Setting it only after the wallet
        # lookup left a window where two near-simultaneous clicks could
        # both pass the balance check before either spin actually starts.
        if view.spun:
            await interaction.response.send_message("This bet's already spinning — open Slots again for another pull.", ephemeral=True)
            return
        view.spun = True

        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.amount:
            view.spun = False
            await interaction.response.send_message(
                f"You don't have {self.amount:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return

        await start_spin(interaction, db_cog, self.amount)


class CustomBetModal(discord.ui.Modal, title="Pull the Lever"):
    amount = discord.ui.TextInput(label="Bet amount", placeholder="e.g. 100", max_length=10)

    def __init__(self, bet_view: "SlotsBetView"):
        super().__init__()
        self.bet_view = bet_view

    async def on_submit(self, interaction: discord.Interaction):
        view = self.bet_view
        # Same synchronous claim-before-any-await reasoning as
        # BetPresetButton above — a modal bypasses the view's own
        # interaction_check entirely, so this is the only thing closing
        # the race for a custom bet.
        if view.spun:
            await interaction.response.send_message("This bet's already spinning — open Slots again for another pull.", ephemeral=True)
            return
        view.spun = True

        db_cog = interaction.client.get_cog('Database')
        try:
            bet = int(self.amount.value)
        except ValueError:
            view.spun = False
            await interaction.response.send_message("Bet amount must be a number.", ephemeral=True)
            return

        if bet < MIN_BET:
            view.spun = False
            await interaction.response.send_message(f"Minimum bet is {MIN_BET:,} chips.", ephemeral=True)
            return

        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if bet > wallet["balance"]:
            view.spun = False
            await interaction.response.send_message(
                f"You don't have {bet:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return

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
        view = CasinoView()
        await interaction.response.edit_message(embed=embed, view=view)
        view.message = interaction.message


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
