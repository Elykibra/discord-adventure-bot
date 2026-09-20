# data/chess_ai.py
#
# A from-scratch chess AI: minimax search with alpha-beta pruning over
# python-chess's legal move generation, evaluating positions by material
# plus piece-square tables (pieces are worth more on good squares, not
# just present on the board). Built from scratch, using how real engines
# approach the problem as a reference (minimax, alpha-beta, move
# ordering, piece-square tables are all textbook chess-programming
# techniques) — not a wrapper around Stockfish or any other engine.
#
# The AI always plays Black; the human always plays White (see
# cogs/views/chess.py) — a fixed convention for v1 that avoids needing a
# color-choice step. evaluate() follows the standard minimax convention:
# positive is good for White, negative is good for Black.
#
# Depth is a single fixed value for v1 (see choose_move's `depth`
# parameter) — the natural hook for difficulty tiers later; not built
# now to keep this first version scoped.

import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,  # can't be captured — king safety is handled by KING_TABLE, not material
}

# Piece-square tables, indexed 0 (a1) .. 63 (h8) — python-chess's own
# square numbering — from White's perspective. Black's bonus is looked
# up via the vertically-mirrored square (see _square_bonus). Values are
# deliberately modest relative to PIECE_VALUES: a positional nudge on
# top of material counting, not a replacement for it.
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
      0,  0,  5,  5,  5,  5,  0, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

# King safety for the opening/middlegame: reward staying behind cover
# on the back rank, punish wandering into the open center.
KING_TABLE = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
]

PIECE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


def _square_bonus(piece_type: int, square: int, color: bool) -> int:
    table = PIECE_TABLES[piece_type]
    index = square if color == chess.WHITE else chess.square_mirror(square)
    return table[index]


def evaluate(board: chess.Board) -> int:
    """Positive = good for White, negative = good for Black. Checkmate
    and drawn positions are scored as terminal values so the search
    correctly prefers/avoids them; otherwise it's material plus a light
    piece-square positional nudge."""
    if board.is_checkmate():
        return -100_000 if board.turn == chess.WHITE else 100_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type] + _square_bonus(piece.piece_type, square, piece.color)
        score += value if piece.color == chess.WHITE else -value
    return score


def _order_moves(board: chess.Board) -> list:
    """Captures ranked first (higher-value victim, lower-value attacker
    ranks highest — classic MVV-LVA) so alpha-beta pruning cuts more
    branches early. This is what keeps a depth-3+ search fast enough to
    feel responsive inside a Discord interaction."""
    def move_score(move: chess.Move) -> int:
        if not board.is_capture(move):
            return 0
        attacker = board.piece_at(move.from_square)
        captured = board.piece_at(move.to_square)
        # En passant captures a pawn that isn't on the destination square.
        captured_value = PIECE_VALUES[captured.piece_type] if captured else PIECE_VALUES[chess.PAWN]
        attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0
        return captured_value * 10 - attacker_value

    return sorted(board.legal_moves, key=move_score, reverse=True)


def _minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        best = -float("inf")
        for move in _order_moves(board):
            board.push(move)
            best = max(best, _minimax(board, depth - 1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float("inf")
        for move in _order_moves(board):
            board.push(move)
            best = min(best, _minimax(board, depth - 1, alpha, beta, True))
            board.pop()
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def choose_move(board: chess.Board, depth: int = 3) -> chess.Move:
    """Picks the AI's move via minimax + alpha-beta pruning, `depth`
    plies deep, evaluated from board.turn's own side. Raises ValueError
    if there are no legal moves — callers must check
    board.is_game_over() before calling this."""
    legal = list(board.legal_moves)
    if not legal:
        raise ValueError("choose_move called with no legal moves available")

    maximizing = board.turn == chess.WHITE
    best_move = legal[0]
    best_score = -float("inf") if maximizing else float("inf")

    for move in _order_moves(board):
        board.push(move)
        score = _minimax(board, depth - 1, -float("inf"), float("inf"), not maximizing)
        board.pop()
        if maximizing and score > best_score:
            best_score, best_move = score, move
        elif not maximizing and score < best_score:
            best_score, best_move = score, move

    return best_move
