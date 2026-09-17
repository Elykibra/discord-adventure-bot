# data/baccarat.py
# Pure Baccarat logic: hand values, the fixed Banker/Player draw rules,
# and payouts. No Discord dependency, independently testable — same
# approach as data/poker.py and data/blackjack.py.
#
# Deck/card display aren't redefined here — callers use
# data.poker.new_shuffled_deck() / card_display() / format_cards()
# directly, same 52-card deck, same (rank, suit) tuple shape.
#
# Unlike Blackjack or Poker, there's no player decision tree here at
# all: once a bet is placed, both hands are dealt and the draw rules
# below are purely mechanical. That's what makes Baccarat fast to
# build and fast to play.

CARD_VALUES = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 0, 'J': 0, 'Q': 0, 'K': 0,
}

# Bet-side payout multipliers, applied on top of returning the original bet.
# Banker pays less than even money because Banker wins more often — without
# the commission, betting Banker would always be strictly better than
# betting Player, which flattens the game.
PAYOUTS = {
    "player": 1.0,   # 1:1
    "banker": 0.95,  # 1:1 minus 5% commission
    "tie": 8.0,      # 8:1 — high risk, high reward, rare
}


def hand_value(cards: list) -> int:
    """Sum of card values, mod 10 — e.g. 7+8=15 plays as 5."""
    return sum(CARD_VALUES[rank] for rank, _ in cards) % 10


def banker_should_draw(banker_total: int, player_third_value: int | None) -> bool:
    """The real fixed Banker draw table. player_third_value is None if the
    Player stood (didn't draw a third card) — Banker then follows the same
    0-5 rule Player would have. Otherwise Banker's decision also depends on
    what that specific card was."""
    if player_third_value is None:
        return banker_total <= 5
    if banker_total <= 2:
        return True
    if banker_total == 3:
        return player_third_value != 8
    if banker_total == 4:
        return player_third_value in (2, 3, 4, 5, 6, 7)
    if banker_total == 5:
        return player_third_value in (4, 5, 6, 7)
    if banker_total == 6:
        return player_third_value in (6, 7)
    return False  # banker_total == 7 always stands


def play_round(deck: list) -> dict:
    """Deals both hands from the given deck (mutates it via pop()) and
    plays out the fixed draw rules to a final result. Returns everything
    a caller needs to display the round and resolve bets against it."""
    player = [deck.pop(), deck.pop()]
    banker = [deck.pop(), deck.pop()]
    p_total = hand_value(player)
    b_total = hand_value(banker)
    natural = p_total >= 8 or b_total >= 8

    if not natural:
        player_third_value = None
        if p_total <= 5:
            card = deck.pop()
            player.append(card)
            player_third_value = CARD_VALUES[card[0]]
            p_total = hand_value(player)

        if banker_should_draw(b_total, player_third_value):
            banker.append(deck.pop())
            b_total = hand_value(banker)

    if p_total > b_total:
        outcome = "player"
    elif b_total > p_total:
        outcome = "banker"
    else:
        outcome = "tie"

    return {
        "player": player,
        "banker": banker,
        "player_total": p_total,
        "banker_total": b_total,
        "natural": natural,
        "outcome": outcome,
    }


def resolve_bet_amount(side: str, amount: int, outcome: str) -> int:
    """How much to credit back for a bet, given the round's outcome —
    0 means a clean loss. Player/Banker bets push (stake returned, no
    win or loss) on a Tie outcome, standard baccarat convention; a Tie
    bet only wins if the outcome is actually a tie."""
    if side == outcome:
        return amount + int(amount * PAYOUTS[side])
    if outcome == "tie" and side in ("player", "banker"):
        return amount
    return 0
