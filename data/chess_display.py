# data/chess_display.py
#
# Renders a python-chess Board as a monospace text grid for a Discord
# embed code block — an 8x8 grid with rank and file labels. No Discord
# dependency; pure formatting, independently testable, same shape as
# data/blackjack.py's format_hand().

import chess

_PIECE_VALUE = {chess.QUEEN: 9, chess.ROOK: 5, chess.BISHOP: 3, chess.KNIGHT: 3, chess.PAWN: 1}
_PIECE_LETTER = {chess.QUEEN: "Q", chess.ROOK: "R", chess.BISHOP: "B", chess.KNIGHT: "N", chess.PAWN: "P"}


def render_board(board: chess.Board) -> str:
    """Rank 8 at the top, rank 1 at the bottom (White's home row), file
    letters along the bottom — the conventional orientation for
    White, which both sides play from in this v1 (the human is always
    White, see cogs/views/chess.py).

    Pieces are plain ASCII letters (Piece.symbol() — uppercase White,
    lowercase Black), not the Unicode chess glyphs (♔♞ etc.) used
    earlier. Those glyphs render a full character wider than plain text
    in Discord's monospace font, so any rank mixing pieces and empty
    squares drifted out of column alignment with the file-letter row
    below it. ASCII letters are guaranteed single-width everywhere."""
    lines = []
    for rank_idx in range(7, -1, -1):
        squares = []
        for file_idx in range(8):
            piece = board.piece_at(chess.square(file_idx, rank_idx))
            squares.append(piece.symbol() if piece else ".")
        lines.append(f"{rank_idx + 1}  " + " ".join(squares))
    lines.append("   a b c d e f g h")
    return "\n".join(lines)


def _replay_captures(move_history: str) -> tuple:
    """Replays move_history (the space-separated SAN log already kept
    for the move-log display) from the starting position, returning
    (pieces_white_captured, pieces_black_captured) sorted high-to-low
    value.

    This replays moves rather than diffing the final board's piece
    counts against the starting counts on purpose: diffing can't tell
    a captured original piece from a captured *promoted* one (a queen
    captured after a pawn promotion would misreport as a "missing
    pawn" — wrong symbol, and understates the capturing side's material
    lead by 8 points), since a pawn promoting and that pawn's promoted
    piece later being captured is indistinguishable from that pawn
    simply having been captured outright once you only look at final
    counts. Replaying sees the actual piece captured on each move."""
    board = chess.Board()
    white_captured, black_captured = [], []
    for san in move_history.split():
        move = board.parse_san(san)
        if board.is_capture(move):
            captured_type = chess.PAWN if board.is_en_passant(move) else board.piece_at(move.to_square).piece_type
            (white_captured if board.turn == chess.WHITE else black_captured).append(captured_type)
        board.push(move)
    white_captured.sort(key=lambda pt: -_PIECE_VALUE[pt])
    black_captured.sort(key=lambda pt: -_PIECE_VALUE[pt])
    return white_captured, black_captured


def format_captured(move_history: str) -> str:
    """A two-line captured-material summary, from White's perspective
    (the human always plays White, see cogs/views/chess.py). The side
    currently ahead on material gets a '(+N)' next to its line, same
    convention as chess.com/lichess's captured trays."""
    white_captured, black_captured = _replay_captures(move_history)
    material_lead = sum(_PIECE_VALUE[pt] for pt in white_captured) - sum(_PIECE_VALUE[pt] for pt in black_captured)

    white_text = " ".join(_PIECE_LETTER[pt] for pt in white_captured) if white_captured else "*(none)*"
    black_text = " ".join(_PIECE_LETTER[pt] for pt in black_captured) if black_captured else "*(none)*"
    if material_lead > 0:
        white_text += f"  (+{material_lead})"
    elif material_lead < 0:
        black_text += f"  (+{-material_lead})"

    return f"You've captured: {white_text}\nThe house has captured: {black_text}"
