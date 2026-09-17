# data/poker.py
# Pure Texas Hold'em logic: deck, 7-card hand evaluation, stake tiers.
# No Discord dependency, independently testable — same approach as
# data/blackjack.py. The Discord UI / table orchestration (turn order,
# betting rounds, buy-ins) is a separate, later piece built on top of this.

import random
from itertools import combinations

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
RANK_VALUES = {rank: i + 2 for i, rank in enumerate(RANKS)}  # '2'->2 ... 'A'->14

STAKE_TIERS = {
    "low": {"name": "Low Stakes", "buy_in": 500, "small_blind": 5, "big_blind": 10},
    "mid": {"name": "Mid Stakes", "buy_in": 1000, "small_blind": 50, "big_blind": 100},
    "high": {"name": "High Stakes", "buy_in": 5000, "small_blind": 100, "big_blind": 200},
}

HAND_NAMES = [
    "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
    "Flush", "Full House", "Four of a Kind", "Straight Flush",
]


def new_shuffled_deck() -> list:
    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    random.shuffle(deck)
    return deck


def card_display(card: tuple) -> str:
    return f"{card[0]}{card[1]}"


def format_cards(cards: list) -> str:
    return " ".join(card_display(c) for c in cards)


def _evaluate_5(cards: list) -> tuple:
    """Ranks a single 5-card hand. Returns a tuple compared lexicographically —
    a higher tuple always beats a lower one, category first then tiebreakers."""
    values = sorted((RANK_VALUES[c[0]] for c in cards), reverse=True)
    suits = [c[1] for c in cards]
    is_flush = len(set(suits)) == 1

    unique_values = sorted(set(values), reverse=True)
    is_straight = False
    straight_high = 0
    if len(unique_values) == 5:
        if unique_values[0] - unique_values[4] == 4:
            is_straight = True
            straight_high = unique_values[0]
        elif unique_values == [14, 5, 4, 3, 2]:  # the "wheel" — A-2-3-4-5, plays as 5-high
            is_straight = True
            straight_high = 5

    counts: dict = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    # Sorted by (count desc, value desc) so the most significant group leads —
    # this ordering is what makes every branch below correct without extra sorting.
    by_count = sorted(counts.items(), key=lambda item: (-item[1], -item[0]))
    grouped_values = [v for v, _ in by_count]
    top_count = by_count[0][1]

    if is_straight and is_flush:
        return (8, straight_high)
    if top_count == 4:
        return (7, grouped_values[0], grouped_values[1])
    if top_count == 3 and by_count[1][1] == 2:
        return (6, grouped_values[0], grouped_values[1])
    if is_flush:
        return (5, *values)
    if is_straight:
        return (4, straight_high)
    if top_count == 3:
        return (3, *grouped_values)
    if top_count == 2 and by_count[1][1] == 2:
        return (2, grouped_values[0], grouped_values[1], grouped_values[2])
    if top_count == 2:
        return (1, *grouped_values)
    return (0, *values)


def best_hand_from_7(cards: list) -> tuple:
    """The best possible 5-card ranking out of 7 cards (2 hole + 5 community).
    Same tuple shape as _evaluate_5 — higher tuple wins."""
    return max(_evaluate_5(list(combo)) for combo in combinations(cards, 5))


def hand_name(rank_tuple: tuple) -> str:
    return HAND_NAMES[rank_tuple[0]]
