# data/chess_display.py
#
# Renders a python-chess Board as a monospace text grid for a Discord
# embed code block — an 8x8 grid of Unicode chess glyphs (the
# "Miscellaneous Symbols" block, Unicode 1.1 — see data/chess_ai.py's
# module docstring for why that block is safe here) with rank and file
# labels. No Discord dependency; pure formatting, independently
# testable, same shape as data/blackjack.py's format_hand().

import chess


def render_board(board: chess.Board) -> str:
    """Rank 8 at the top, rank 1 at the bottom (White's home row), file
    letters along the bottom — the conventional orientation for
    White, which both sides play from in this v1 (the human is always
    White, see cogs/views/chess.py)."""
    lines = []
    for rank_idx in range(7, -1, -1):
        squares = []
        for file_idx in range(8):
            piece = board.piece_at(chess.square(file_idx, rank_idx))
            squares.append(piece.unicode_symbol() if piece else ".")
        lines.append(f"{rank_idx + 1}  " + " ".join(squares))
    lines.append("   a b c d e f g h")
    return "\n".join(lines)
