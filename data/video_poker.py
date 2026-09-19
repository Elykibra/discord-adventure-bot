# data/video_poker.py
# Pure Video Poker ("Jacks or Better") logic: hand evaluation, the
# standard payout table, deck utilities reused directly from
# data.poker. No Discord dependency, independently testable — same
# approach as data/poker.py, data/blackjack.py, data/baccarat.py.
#
# Unlike Texas Hold'em Poker (multiplayer, betting rounds, community
# cards), Video Poker is solo and structurally closer to Blackjack: a
# single hand of exactly 5 cards, one real decision (which cards to
# hold before the single replacement draw), then resolved against a
# fixed payout table — same shape as Slots' payout table, except here
# the player's choice genuinely changes the odds instead of the
# outcome being fully decided the instant the deal happens.
#
# This is the classic "9/6 Jacks or Better" table (named for its Full
# House / Flush payouts) — the most common, most studied video poker
# variant. It's famous in gambling math for returning ~99.5% under
# PERFECT play, one of the lowest edges of any casino game — which is
# exactly why it rewards skill: bad hold/discard choices measurably
# cost expected value, unlike Slots where nothing the player does
# matters.

from data.poker import RANK_VALUES  # reuse the same rank-value mapping (Jack=11 ... Ace=14)

# Payout multiplier on the bet, total return (includes the original
# stake) — e.g. a 10-chip bet on a Full House (9x) returns 90 total.
PAYOUTS = {
    "royal_flush": 800,
    "straight_flush": 50,
    "four_of_a_kind": 25,
    "full_house": 9,
    "flush": 6,
    "straight": 4,
    "three_of_a_kind": 3,
    "two_pair": 2,
    "jacks_or_better": 1,
}

HAND_LABELS = {
    "royal_flush": "Royal Flush",
    "straight_flush": "Straight Flush",
    "four_of_a_kind": "Four of a Kind",
    "full_house": "Full House",
    "flush": "Flush",
    "straight": "Straight",
    "three_of_a_kind": "Three of a Kind",
    "two_pair": "Two Pair",
    "jacks_or_better": "Jacks or Better",
    "nothing": "No Win",
}

JACKS_OR_BETTER_MIN_RANK = RANK_VALUES['J']  # 11 — a pair below this (2s through 10s) doesn't pay


def evaluate_hand(cards: list) -> str:
    """Classifies a 5-card hand into one of PAYOUTS' keys, or 'nothing'
    if it doesn't pay. Unlike data.poker's hand evaluator (which only
    needs to rank/compare hands against each other), this has to
    distinguish two things Texas Hold'em never needs to: a Royal Flush
    from an ordinary Straight Flush (800x vs 50x — a huge difference),
    and a Jacks-or-better pair from a lower one (1x vs nothing)."""
    values = sorted((RANK_VALUES[c[0]] for c in cards), reverse=True)
    suits = [c[1] for c in cards]
    is_flush = len(set(suits)) == 1

    unique_values = sorted(set(values), reverse=True)
    is_straight = False
    if len(unique_values) == 5:
        if unique_values[0] - unique_values[4] == 4:
            is_straight = True
        elif unique_values == [14, 5, 4, 3, 2]:  # the wheel (A-2-3-4-5) — a straight, but never a royal
            is_straight = True

    is_royal = is_straight and is_flush and unique_values[0] == 14 and unique_values[4] == 10

    counts: dict = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    by_count = sorted(counts.items(), key=lambda item: (-item[1], -item[0]))
    top_count = by_count[0][1]

    if is_royal:
        return "royal_flush"
    if is_straight and is_flush:
        return "straight_flush"
    if top_count == 4:
        return "four_of_a_kind"
    if top_count == 3 and by_count[1][1] == 2:
        return "full_house"
    if is_flush:
        return "flush"
    if is_straight:
        return "straight"
    if top_count == 3:
        return "three_of_a_kind"
    if top_count == 2 and by_count[1][1] == 2:
        return "two_pair"
    if top_count == 2 and by_count[0][0] >= JACKS_OR_BETTER_MIN_RANK:
        return "jacks_or_better"
    return "nothing"


def payout_multiplier(cards: list) -> int:
    """0 means a clean loss."""
    return PAYOUTS.get(evaluate_hand(cards), 0)
