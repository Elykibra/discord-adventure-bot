# cogs/views/blackjack.py
#
# Blackjack v1: real 52-card deck, correct soft/hard Ace handling, natural
# blackjack 3:2 payout, dealer stands on all 17s, Hit/Stand/Double Down.
# Split and Insurance are a planned follow-up once this core is proven —
# same incremental approach as the dungeon.
#
# Betting: preset buttons for common amounts (filtered to what the player
# can actually afford) plus a "Custom Bet" modal, with the current balance
# shown up front so sizing a bet doesn't require checking /casino first.

import asyncio
import discord

from data.blackjack import (
    new_shuffled_deck, format_hand, hand_value, is_blackjack, is_bust,
    dealer_should_hit, BLACKJACK_PAYOUT_MULTIPLIER,
)

MIN_BET = 10
BET_PRESETS = [50, 100, 250, 500, 1000]
DEALER_DRAW_DELAY = 1.0
HAND_TIMEOUT_SECONDS = 180
BET_VIEW_TIMEOUT_SECONDS = 120


def blackjack_bet_embed(balance: int) -> discord.Embed:
    return discord.Embed(
        title="🃏 Blackjack",
        description=f"💰 **Your balance:** {balance:,} chips\n\nPick a bet amount, or set a custom one.",
        color=discord.Color.gold(),
    )


class BetPresetButton(discord.ui.Button):
    def __init__(self, amount: int, *, label: str | None = None, all_in: bool = False):
        super().__init__(
            label=label or f"{amount:,}",
            style=discord.ButtonStyle.success if all_in else discord.ButtonStyle.primary,
            emoji="🎲",
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


class BlackjackBetView(discord.ui.View):
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
    await db_cog.add_chips(interaction.user.id, -bet)
    deck = new_shuffled_deck()
    player_cards = [deck.pop(), deck.pop()]
    dealer_cards = [deck.pop(), deck.pop()]

    view = BlackjackHandView(db_cog, interaction.user.id, deck, player_cards, dealer_cards, bet)

    # Close out the private bet-picker (keeps balance/bet-sizing private)...
    await interaction.response.edit_message(
        embed=discord.Embed(
            title="🃏 Blackjack",
            description="Bet placed — your hand is on the table below for everyone to watch.",
            color=discord.Color.gold(),
        ),
        view=None,
    )

    # ...then deal the actual hand as a public message: anyone can watch it
    # play out, but only the player who bet can touch the buttons — see
    # BlackjackHandView.interaction_check.
    content = f"🃏 {interaction.user.mention} is playing Blackjack!"
    if is_blackjack(player_cards) or is_blackjack(dealer_cards):
        message = await interaction.channel.send(content=content, embed=view.build_embed())
        await view.resolve_naturals(message)
        return

    message = await interaction.channel.send(content=content, embed=view.build_embed(), view=view)
    view.message = message


class BlackjackHandView(discord.ui.View):
    def __init__(self, db_cog, user_id: int, deck: list, player_cards: list, dealer_cards: list, bet: int):
        super().__init__(timeout=HAND_TIMEOUT_SECONDS)
        self.db_cog = db_cog
        self.user_id = user_id
        self.deck = deck
        self.player_cards = player_cards
        self.dealer_cards = dealer_cards
        self.bet = bet
        self.total_wagered = bet
        self.finished = False
        self.reveal_dealer = False
        self.outcome = "pending"
        self.result_text = "Your move."
        self.message: discord.Message | None = None
        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This isn't your hand — feel free to watch, though!", ephemeral=True
            )
            return False
        return True

    def rebuild_items(self):
        self.clear_items()
        if self.finished:
            return
        self.add_item(HitButton())
        self.add_item(StandButton())
        if len(self.player_cards) == 2:
            self.add_item(DoubleDownButton())

    def build_embed(self) -> discord.Embed:
        player_total, player_soft = hand_value(self.player_cards)
        player_label = f"{player_total}" + (" (soft)" if player_soft else "")

        if self.reveal_dealer:
            dealer_total, dealer_soft = hand_value(self.dealer_cards)
            dealer_hand_text = format_hand(self.dealer_cards)
            dealer_label = f"{dealer_total}" + (" (soft)" if dealer_soft else "")
        else:
            dealer_hand_text = f"{format_hand([self.dealer_cards[0]])} 🎴"
            dealer_label = "?"

        color = {
            "pending": discord.Color.dark_gold(),
            "win": discord.Color.green(),
            "lose": discord.Color.dark_grey(),
            "push": discord.Color.blurple(),
        }[self.outcome]

        embed = discord.Embed(title="🃏 Blackjack", description=self.result_text, color=color)
        embed.add_field(name=f"Your Hand ({player_label})", value=format_hand(self.player_cards), inline=False)
        embed.add_field(name=f"Dealer's Hand ({dealer_label})", value=dealer_hand_text, inline=False)
        embed.add_field(name="Bet", value=f"{self.total_wagered:,} chips", inline=True)
        return embed

    async def push_update(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.build_embed(), view=self)

    def _compute_outcome(self) -> tuple:
        """Returns (outcome, payout, result_text) from the current hands. Doesn't touch the DB."""
        player_total, _ = hand_value(self.player_cards)
        dealer_total, _ = hand_value(self.dealer_cards)
        dealer_bust = dealer_total > 21

        if dealer_bust or player_total > dealer_total:
            payout = self.total_wagered * 2
            reason = "Dealer busts!" if dealer_bust else "You win!"
            return "win", payout, f"🎉 {reason} You win {payout:,} chips."
        if player_total == dealer_total:
            return "push", self.total_wagered, f"🤝 Push. Your {self.total_wagered:,} chips are returned."
        return "lose", 0, f"❌ Dealer wins with {dealer_total}. You lose {self.total_wagered:,} chips."

    async def resolve(self, interaction: discord.Interaction, *, busted: bool):
        self.finished = True
        self.reveal_dealer = True

        if busted:
            player_total, _ = hand_value(self.player_cards)
            self.outcome = "lose"
            self.result_text = f"💥 Bust with {player_total}! You lose {self.total_wagered:,} chips."
            self.rebuild_items()
            await self.push_update(interaction)
            self.stop()
            return

        self.rebuild_items()
        await self.push_update(interaction)
        while dealer_should_hit(self.dealer_cards):
            await asyncio.sleep(DEALER_DRAW_DELAY)
            self.dealer_cards.append(self.deck.pop())
            await self.push_update(interaction)

        await self.finalize_payout(interaction)

    async def finalize_payout(self, interaction: discord.Interaction):
        self.outcome, payout, self.result_text = self._compute_outcome()
        if payout > 0:
            await self.db_cog.add_chips(self.user_id, payout)
        self.rebuild_items()
        await self.push_update(interaction)
        self.stop()

    async def resolve_naturals(self, message: discord.Message):
        """Called right after posting the public hand message — there's no
        button-click interaction to respond to yet, so this edits the
        message directly (same as on_timeout does)."""
        self.message = message
        self.finished = True
        self.reveal_dealer = True
        player_bj = is_blackjack(self.player_cards)
        dealer_bj = is_blackjack(self.dealer_cards)

        if player_bj and dealer_bj:
            await self.db_cog.add_chips(self.user_id, self.bet)
            self.outcome = "push"
            self.result_text = "🤝 Both have Blackjack! Push — your bet is returned."
        elif player_bj:
            payout = int(self.bet * (1 + BLACKJACK_PAYOUT_MULTIPLIER))
            await self.db_cog.add_chips(self.user_id, payout)
            self.outcome = "win"
            self.result_text = f"🃏 **BLACKJACK!** You win {payout:,} chips (3:2 payout)."
        else:
            self.outcome = "lose"
            self.result_text = "❌ Dealer has Blackjack. You lose your bet."

        self.rebuild_items()
        await message.edit(embed=self.build_embed(), view=self)
        self.stop()

    async def on_timeout(self):
        if self.finished or not self.message:
            return
        self.finished = True
        self.reveal_dealer = True
        while dealer_should_hit(self.dealer_cards):
            self.dealer_cards.append(self.deck.pop())

        self.outcome, payout, result = self._compute_outcome()
        self.result_text = "⏱️ Auto-stood after inactivity. " + result
        if payout > 0:
            await self.db_cog.add_chips(self.user_id, payout)

        self.rebuild_items()
        try:
            await self.message.edit(embed=self.build_embed(), view=self)
        except discord.HTTPException:
            pass


class HitButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Hit", style=discord.ButtonStyle.primary, emoji="➕")

    async def callback(self, interaction: discord.Interaction):
        view: BlackjackHandView = self.view
        await interaction.response.defer()

        view.player_cards.append(view.deck.pop())
        if is_bust(view.player_cards):
            await view.resolve(interaction, busted=True)
        else:
            view.rebuild_items()
            await view.push_update(interaction)


class StandButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stand", style=discord.ButtonStyle.secondary, emoji="✋")

    async def callback(self, interaction: discord.Interaction):
        view: BlackjackHandView = self.view
        await interaction.response.defer()
        await view.resolve(interaction, busted=False)


class DoubleDownButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Double Down", style=discord.ButtonStyle.success, emoji="⏫")

    async def callback(self, interaction: discord.Interaction):
        view: BlackjackHandView = self.view
        await interaction.response.defer()

        wallet = await view.db_cog.get_or_create_wallet(view.user_id)
        if wallet["balance"] < view.bet:
            await interaction.followup.send(
                f"You need {view.bet:,} more chips to double down — you have {wallet['balance']:,}.",
                ephemeral=True,
            )
            return

        await view.db_cog.add_chips(view.user_id, -view.bet)
        view.total_wagered += view.bet
        view.player_cards.append(view.deck.pop())
        await view.resolve(interaction, busted=is_bust(view.player_cards))
