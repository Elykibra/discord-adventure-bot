# cogs/views/video_poker.py
#
# Video Poker ("Jacks or Better") — solo, like Blackjack and Slots, not
# a shared table. Unlike Slots though, there's a real decision here:
# which of the 5 dealt cards to hold before the single replacement
# draw. That choice genuinely changes the odds — see data/video_poker.py
# for the math (a heuristic-strategy simulation landed at ~93% return,
# meaningfully below the ~99.5% true-optimal-play ceiling but nowhere
# near broken), which is the whole point: unlike Slots, skill matters.
#
# Same conventions established across today's other casino views:
#   - Bet picker shaped like Blackjack/Slots (presets + custom modal).
#   - Interactions defer before any DB work, learned live from a real
#     production bug in Baccarat's bet modal (a chain of sequential DB
#     calls before ever acknowledging the interaction outlasted
#     Discord's 3-second ack window and killed it outright).
#   - Balance shown in a footer throughout, not just at the end.
#   - Play Again / Change Bet on the result, same as Blackjack/Slots.
#   - Busy-guard + ownership check on the hand view, same as
#     Blackjack's "watchable but not controllable by others."
#
# Toggling which cards to hold is pure in-memory state — no DB call,
# so no defer needed there; only the final Draw (which credits any
# winnings) needs it.

import discord

from data.poker import new_shuffled_deck, card_display
from data.video_poker import evaluate_hand, payout_multiplier, PAYOUTS, HAND_LABELS

MIN_BET = 10
BET_PRESETS = [50, 100, 250, 500, 1000]
BET_VIEW_TIMEOUT_SECONDS = 120
HAND_VIEW_TIMEOUT_SECONDS = 180


def _payout_table_text() -> str:
    lines = [f"{HAND_LABELS[key]} — {mult}x" for key, mult in PAYOUTS.items()]
    return "\n".join(lines)


def video_poker_bet_embed(balance: int) -> discord.Embed:
    return discord.Embed(
        title="🎴 Solo Poker",
        description=(
            f"💰 **Your balance:** {balance:,} chips\n\n"
            f"Pick a bet amount, or set a custom one.\n\n"
            f"**Payouts (Jacks or Better):**\n{_payout_table_text()}"
        ),
        color=discord.Color.gold(),
    )


class BetPresetButton(discord.ui.Button):
    def __init__(self, amount: int, *, label: str | None = None, all_in: bool = False):
        super().__init__(
            label=label or f"{amount:,}",
            style=discord.ButtonStyle.success if all_in else discord.ButtonStyle.primary,
            emoji="🎴",
        )
        self.amount = amount

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.amount:
            await interaction.response.send_message(
                f"You don't have {self.amount:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return
        await start_hand(interaction, db_cog, self.amount)


class CustomBetModal(discord.ui.Modal, title="Custom Bet"):
    amount = discord.ui.TextInput(label="Bet amount", placeholder="e.g. 150", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        try:
            bet = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message("Bet amount must be a number.", ephemeral=True)
            return

        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if bet < MIN_BET:
            await interaction.response.send_message(f"Minimum bet is {MIN_BET:,} chips.", ephemeral=True)
            return
        if bet > wallet["balance"]:
            await interaction.response.send_message(
                f"You don't have {bet:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return

        await start_hand(interaction, db_cog, bet)


class CustomBetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Custom Bet", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CustomBetModal())


class BackToCasinoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to Casino", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        from cogs.casino import casino_embed, CasinoView  # local import avoids a circular import
        embed = casino_embed("🎰 Casino", "Pick an option below to get started.")
        await interaction.response.edit_message(embed=embed, view=CasinoView())


class VideoPokerBetView(discord.ui.View):
    def __init__(self, balance: int):
        super().__init__(timeout=BET_VIEW_TIMEOUT_SECONDS)
        for amount in BET_PRESETS:
            if amount <= balance:
                self.add_item(BetPresetButton(amount))
        if balance >= MIN_BET:
            self.add_item(BetPresetButton(balance, label=f"All In ({balance:,})", all_in=True))
        self.add_item(CustomBetButton())
        self.add_item(BackToCasinoButton())


async def start_hand(interaction: discord.Interaction, db_cog, bet: int):
    balance = await db_cog.add_chips(interaction.user.id, -bet)
    deck = new_shuffled_deck()
    hand = [deck.pop() for _ in range(5)]

    view = VideoPokerHandView(db_cog, interaction.user.id, deck, hand, bet, balance)

    await interaction.response.edit_message(
        embed=discord.Embed(
            title="🎴 Solo Poker",
            description="Bet placed — your hand is on the table below for everyone to watch.",
            color=discord.Color.gold(),
        ),
        view=None,
    )

    message = await interaction.channel.send(
        content=f"🎴 {interaction.user.mention} is playing Solo Poker!",
        embed=view.build_embed(),
        view=view,
    )
    view.message = message


class VideoPokerHandView(discord.ui.View):
    def __init__(self, db_cog, user_id: int, deck: list, hand: list, bet: int, balance: int):
        super().__init__(timeout=HAND_VIEW_TIMEOUT_SECONDS)
        self.db_cog = db_cog
        self.user_id = user_id
        self.deck = deck
        self.hand = hand
        self.held: set = set()  # indices into self.hand currently marked to keep
        self.bet = bet
        self.current_balance = balance
        self.message: discord.Message | None = None
        self.busy = False
        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This isn't your hand — feel free to watch, though!", ephemeral=True
            )
            return False
        if self.busy:
            await interaction.response.send_message(
                "Still resolving your last move — hang on a second.", ephemeral=True
            )
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        for i in range(5):
            self.add_item(CardToggleButton(i, self.hand[i], held=i in self.held))
        self.add_item(DrawButton())

    def build_embed(self, *, result: dict | None = None) -> discord.Embed:
        embed = discord.Embed(title="🎴 Solo Poker", color=discord.Color.dark_gold())

        if result:
            outcome_label = HAND_LABELS[result["category"]]
            if result["multiplier"] > 0:
                embed.description = (
                    f"🏆 **{outcome_label}!** {result['multiplier']}x — you win {result['payout']:,} chips."
                )
                embed.color = discord.Color.green()
            else:
                embed.description = f"❌ {outcome_label}. You lose {self.bet:,} chips."
                embed.color = discord.Color.dark_grey()

            # Spell out exactly what happened — which cards were kept from
            # the deal vs. freshly drawn — so the final hand and category
            # aren't left for the player to puzzle out on their own.
            final_hand = "  ".join(f"`{card_display(c)}`" for c in self.hand)
            kept = [card_display(self.hand[i]) for i in sorted(self.held)]
            drawn = [card_display(self.hand[i]) for i in range(5) if i not in self.held]
            embed.add_field(name="Final Hand", value=final_hand, inline=False)
            embed.add_field(name="Kept", value="  ".join(f"`{c}`" for c in kept) if kept else "_nothing_", inline=True)
            embed.add_field(name="Drew", value="  ".join(f"`{c}`" for c in drawn) if drawn else "_nothing_", inline=True)
        else:
            embed.description = "Pick which cards to **hold**, then hit **Draw**."
            card_lines = [
                f"`{card_display(card)}{' 🔒' if i in self.held else ''}`"
                for i, card in enumerate(self.hand)
            ]
            embed.add_field(name="Your Hand", value="  ".join(card_lines), inline=False)

        embed.add_field(name="Bet", value=f"{self.bet:,} chips", inline=True)
        embed.set_footer(text=f"💰 Balance: {self.current_balance:,} chips")
        return embed

    async def on_timeout(self):
        """Auto-draws with whatever was held so far (nothing, if the
        player never touched a card) rather than leaving the bet
        deducted with no resolution — same reasoning as Blackjack's
        auto-stand on inactivity."""
        if not self.message:
            return
        for i in range(5):
            if i not in self.held:
                self.hand[i] = self.deck.pop()

        category = evaluate_hand(self.hand)
        multiplier = payout_multiplier(self.hand)
        payout = self.bet * multiplier
        if payout > 0:
            self.current_balance = await self.db_cog.add_chips(self.user_id, payout)

        result = {"category": category, "multiplier": multiplier, "payout": payout}
        embed = self.build_embed(result=result)
        embed.description = "⏱️ Auto-drew after inactivity. " + embed.description
        result_view = VideoPokerResultView(self.user_id, self.bet)
        try:
            await self.message.edit(embed=embed, view=result_view)
            result_view.message = self.message
        except discord.HTTPException:
            pass


class CardToggleButton(discord.ui.Button):
    def __init__(self, index: int, card: tuple, *, held: bool):
        super().__init__(
            label=card_display(card),
            style=discord.ButtonStyle.success if held else discord.ButtonStyle.secondary,
            emoji="🔒" if held else None,
            row=0,
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: VideoPokerHandView = self.view
        if self.index in view.held:
            view.held.discard(self.index)
        else:
            view.held.add(self.index)
        view.rebuild_items()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class DrawButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Draw", style=discord.ButtonStyle.primary, emoji="🎴", row=1)

    async def callback(self, interaction: discord.Interaction):
        view: VideoPokerHandView = self.view
        # Defer now, before any DB work — see module docstring.
        await interaction.response.defer()

        for i in range(5):
            if i not in view.held:
                view.hand[i] = view.deck.pop()

        category = evaluate_hand(view.hand)
        multiplier = payout_multiplier(view.hand)
        payout = view.bet * multiplier
        if payout > 0:
            view.current_balance = await view.db_cog.add_chips(view.user_id, payout)

        view.clear_items()  # hand is resolved — no more buttons on this view
        result = {"category": category, "multiplier": multiplier, "payout": payout}
        result_view = VideoPokerResultView(view.user_id, view.bet)
        message = await interaction.edit_original_response(
            embed=view.build_embed(result=result),
            view=result_view,
        )
        result_view.message = message


class PlayAgainButton(discord.ui.Button):
    def __init__(self, bet: int):
        super().__init__(label=f"Play Again ({bet:,})", style=discord.ButtonStyle.success, emoji="🎴")
        self.bet = bet

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.bet:
            await interaction.response.send_message(
                f"You don't have {self.bet:,} chips for another {self.bet:,}-chip hand — "
                f"balance is {wallet['balance']:,}. Try Change Bet for a smaller amount.",
                ephemeral=True,
            )
            return
        await start_hand(interaction, db_cog, self.bet)


class ChangeBetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Change Bet", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        await interaction.response.edit_message(
            embed=video_poker_bet_embed(wallet["balance"]), view=VideoPokerBetView(wallet["balance"])
        )


class VideoPokerResultView(discord.ui.View):
    """Shown once a hand resolves — lets the player play another hand at
    the same bet, or change it, without re-running /casino. A fresh
    instance every time a hand ends, so there's nothing to release
    between hands, same reasoning as Slots' SlotsResultView and
    Blackjack's BlackjackResultView."""

    def __init__(self, user_id: int, bet: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.busy = False
        self.message: discord.Message | None = None
        self.add_item(PlayAgainButton(bet))
        self.add_item(ChangeBetButton())
        self.add_item(BackToCasinoButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This isn't your hand — feel free to watch, though!", ephemeral=True
            )
            return False
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    async def on_timeout(self):
        """Grey out Play Again / Change Bet / Back to Casino once nobody's
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
