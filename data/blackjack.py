# data/blackjack.py
# Pure blackjack game logic — deck, hand values, dealer rules. No Discord
# dependency, so it's independently testable. The Discord UI layer lives in
# cogs/views/blackjack.py.
#
# Rules implemented (v1 — no Split or Insurance yet):
#   - Real 52-card deck, shuffled fresh per hand.
#   - Correct soft/hard Ace handling.
#   - Natural Blackjack (21 on the first two cards) pays 3:2, unless the
#     dealer also has one (push).
#   - Dealer stands on all 17s (hard or soft) — the standard rule.
#   - Hit / Stand / Double Down for the player.

import random

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']

DEALER_STAND_TOTAL = 17
BLACKJACK_PAYOUT_MULTIPLIER = 1.5  # natural blackjack pays 3:2 on top of the returned bet


def new_shuffled_deck() -> list:
    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    random.shuffle(deck)
    return deck


def card_display(card: tuple) -> str:
    rank, suit = card
    return f"{rank}{suit}"


def format_hand(cards: list) -> str:
    return " ".join(card_display(c) for c in cards)


def hand_value(cards: list) -> tuple:
    """Returns (total, is_soft). is_soft means an Ace is still being counted as 11."""
    total = 0
    aces = 0
    for rank, _ in cards:
        if rank in ('J', 'Q', 'K'):
            total += 10
        elif rank == 'A':
            total += 11
            aces += 1
        else:
            total += int(rank)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total, aces > 0


def is_blackjack(cards: list) -> bool:
    total, _ = hand_value(cards)
    return len(cards) == 2 and total == 21


def is_bust(cards: list) -> bool:
    total, _ = hand_value(cards)
    return total > 21


def dealer_should_hit(cards: list) -> bool:
    total, _ = hand_value(cards)
    return total < DEALER_STAND_TOTAL
