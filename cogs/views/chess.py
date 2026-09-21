# cogs/views/chess.py
#
# Chess vs. AI. The human always plays White, the AI always plays Black
# (see data/chess_ai.py) — PvP is a deliberately separate, later piece,
# and fixing colors avoids needing a color-choice step for v1.
#
# Move input is a modal (standard algebraic notation: "e4", "Nf3",
# "O-O") rather than a button grid — an 8x8 board is 64 squares, well
# past Discord's 25-component-per-message limit, so there's no clean
# button-based square picker here the way Video Poker's 5 card toggles
# work.
#
# Unlike every other casino game, a chess game PERSISTS to the DB
# (chess_games, migrations/025) after every move pair, checkpointed the
# same "DB only at checkpoints" way the rest of the casino settles
# money — just with more checkpoints, since a chess game can run far
# longer than this bot's usual few-minute view lifetime, and this bot
# redeploys often enough that an in-memory-only game would silently
# vanish. on_timeout() deliberately does nothing to the game itself
# (just greys out the buttons) — the DB row is the real source of
# truth, and the player can always resume via /casino later.

import discord
import chess

from data.chess_ai import choose_move
from data.chess_display import render_board, format_captured
from data.casino_badges import format_new_badge_field

MIN_BET = 10
BET_PRESETS = [50, 100, 250, 500, 1000]
BET_VIEW_TIMEOUT_SECONDS = 120
GAME_VIEW_TIMEOUT_SECONDS = 1800  # 30 min of no clicks just greys out the buttons — see module docstring
AI_SEARCH_DEPTH = 3  # tuned single difficulty for v1 — see data/chess_ai.py


def chess_bet_embed(balance: int) -> discord.Embed:
    return discord.Embed(
        title="⚔️ Chess",
        description=(
            f"💰 **Your balance:** {balance:,} chips\n\n"
            f"Pick a bet amount, or set a custom one. You play White; the house's AI plays Black.\n\n"
            f"**Payout:** win pays 2x your bet, a draw refunds it, a loss or resignation forfeits it."
        ),
        color=discord.Color.gold(),
    )


def _format_move_log(move_history: str) -> str:
    tokens = move_history.split()
    if not tokens:
        return "*(no moves yet)*"
    lines = []
    for i in range(0, len(tokens), 2):
        move_number = i // 2 + 1
        white_move = tokens[i]
        black_move = tokens[i + 1] if i + 1 < len(tokens) else ""
        lines.append(f"{move_number}. {white_move} {black_move}".strip())
    return "  ".join(lines)


def _determine_result(board: chess.Board) -> str:
    """'win'/'loss'/'draw' from the human's (White's) perspective. Only
    valid once board.is_game_over() is True."""
    outcome = board.outcome()
    if outcome is None or outcome.winner is None:
        return "draw"
    return "win" if outcome.winner == chess.WHITE else "loss"


def _game_over_text(board: chess.Board, result: str, *, resigned: bool = False) -> str:
    if resigned:
        return "🏳️ You resigned. Better luck next game."
    if board.is_checkmate():
        return "🏆 Checkmate — you win!" if result == "win" else "💀 Checkmate — the house wins."
    if board.is_stalemate():
        return "🤝 Stalemate — it's a draw."
    return "🤝 Draw."


class BetPresetButton(discord.ui.Button):
    def __init__(self, amount: int, *, label: str | None = None, all_in: bool = False):
        super().__init__(
            label=label or f"{amount:,}",
            style=discord.ButtonStyle.success if all_in else discord.ButtonStyle.primary,
            emoji="⚔️",
        )
        self.amount = amount

    async def callback(self, interaction: discord.Interaction):
        view: ChessBetView = self.view
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if wallet["balance"] < self.amount:
            view.busy = False
            await interaction.response.send_message(
                f"You don't have {self.amount:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return
        # Defer here (not inside start_game — see its docstring) since
        # this is the first response-touching call on this interaction.
        await interaction.response.defer()
        await start_game(interaction, db_cog, self.amount, already_public=view.already_public)


class CustomBetModal(discord.ui.Modal, title="Custom Bet"):
    amount = discord.ui.TextInput(label="Bet amount", placeholder="e.g. 150", max_length=10)

    def __init__(self, bet_view: "ChessBetView", *, already_public: bool = False):
        super().__init__()
        self.bet_view = bet_view
        self.already_public = already_public

    async def on_submit(self, interaction: discord.Interaction):
        view = self.bet_view
        if view.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return
        view.busy = True

        db_cog = interaction.client.get_cog('Database')
        try:
            bet = int(self.amount.value)
        except ValueError:
            view.busy = False
            await interaction.response.send_message("Bet amount must be a number.", ephemeral=True)
            return

        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        if bet < MIN_BET:
            view.busy = False
            await interaction.response.send_message(f"Minimum bet is {MIN_BET:,} chips.", ephemeral=True)
            return
        if bet > wallet["balance"]:
            view.busy = False
            await interaction.response.send_message(
                f"You don't have {bet:,} chips — balance is {wallet['balance']:,}.", ephemeral=True
            )
            return

        # Defer here (not inside start_game — see its docstring) since
        # this is the first response-touching call on this interaction.
        await interaction.response.defer()
        await start_game(interaction, db_cog, bet, already_public=self.already_public)


class CustomBetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Custom Bet", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        view: ChessBetView = self.view
        view.busy = False  # a modal takes over from here — it manages this same lock itself
        await interaction.response.send_modal(CustomBetModal(view, already_public=view.already_public))


class BackToCasinoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to Casino", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        from cogs.casino import casino_embed, CasinoView  # local import avoids a circular import
        embed = casino_embed("🎰 Casino", "Pick an option below to get started.")
        view = CasinoView()
        await interaction.response.edit_message(embed=embed, view=view)
        view.message = interaction.message


class ChessBetView(discord.ui.View):
    def __init__(self, balance: int, *, already_public: bool = False):
        super().__init__(timeout=BET_VIEW_TIMEOUT_SECONDS)
        self.already_public = already_public
        self.busy = False
        for amount in BET_PRESETS:
            if amount <= balance:
                self.add_item(BetPresetButton(amount))
        if balance >= MIN_BET:
            self.add_item(BetPresetButton(balance, label=f"All In ({balance:,})", all_in=True))
        self.add_item(CustomBetButton())
        self.add_item(BackToCasinoButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True


async def start_game(interaction: discord.Interaction, db_cog, bet: int, *, already_public: bool = False):
    """Callers must defer (or otherwise respond to) the interaction
    before calling this — same contract as resume_game() below and
    dungeon.py's start_run(). This can chain into two DB round-trips
    (add_chips, then create_chess_game) on top of whatever the caller
    already awaited for its own balance check, which live-confirmed can
    outlast Discord's 3-second interaction window if nothing acked it
    first — but unlike Blackjack's/Video Poker's start_hand, this one
    now also has a caller (cogs/casino.py's chess branch) that's
    already deferred by the time it gets here, so deferring internally
    here too would double-respond and crash."""
    if bet:
        await db_cog.add_chips(interaction.user.id, -bet)
    board = chess.Board()
    await db_cog.create_chess_game(interaction.user.id, board.fen(), bet)
    view = ChessGameView(db_cog, interaction.user.id, board, bet, "")

    if already_public:
        message = await interaction.edit_original_response(embed=view.build_embed(), view=view)
        view.message = message
        return

    await interaction.edit_original_response(
        embed=discord.Embed(
            title="⚔️ Chess",
            description="Bet placed — your game is on the table below for everyone to watch.",
            color=discord.Color.gold(),
        ),
        view=None,
    )
    content = f"⚔️ {interaction.user.mention} is playing Chess!"
    message = await interaction.channel.send(content=content, embed=view.build_embed(), view=view)
    view.message = message


async def resume_game(interaction: discord.Interaction, db_cog, game_row: dict):
    """Reopens an in-progress game from its persisted FEN — used when
    the player already has one (see cogs/casino.py's Chess entry), most
    often because a deploy happened mid-game and the old view is gone
    even though the game itself never stopped existing."""
    board = chess.Board(game_row["fen"])
    view = ChessGameView(db_cog, interaction.user.id, board, game_row["bet"], game_row["move_history"])
    message = await interaction.edit_original_response(embed=view.build_embed(), view=view)
    view.message = message


class MakeMoveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Make a Move", style=discord.ButtonStyle.primary, emoji="✏️", row=0)

    async def callback(self, interaction: discord.Interaction):
        view: ChessGameView = self.view
        view.busy = False  # a modal takes over from here — it manages this same lock itself
        await interaction.response.send_modal(MoveModal(view))


class MoveModal(discord.ui.Modal, title="Make Your Move"):
    move = discord.ui.TextInput(label="Move (standard notation)", placeholder="e.g. e4, Nf3, O-O", max_length=10)

    def __init__(self, game_view: "ChessGameView"):
        super().__init__()
        self.game_view = game_view

    async def on_submit(self, interaction: discord.Interaction):
        view = self.game_view
        if view.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return
        view.busy = True

        # Defer first — this does move validation, a possible
        # multi-second AI search, and a DB write before anything's
        # ready to show, the same "defer before slow work" lesson
        # applied to every other modal this session.
        await interaction.response.defer()

        san_text = self.move.value.strip()
        try:
            player_move = view.board.parse_san(san_text)
        except ValueError:
            view.busy = False
            await interaction.followup.send(
                f"'{san_text}' isn't a legal move right now — try standard notation like e4, Nf3, or O-O.",
                ephemeral=True,
            )
            return

        player_san = view.board.san(player_move)  # canonical text (with +/# suffix) before pushing
        view.board.push(player_move)
        view.move_history = (view.move_history + " " + player_san).strip()

        if view.board.is_game_over():
            await view.finish_game(interaction)
            return

        ai_move = choose_move(view.board, depth=AI_SEARCH_DEPTH)
        ai_san = view.board.san(ai_move)
        view.board.push(ai_move)
        view.move_history = (view.move_history + " " + ai_san).strip()

        if view.board.is_game_over():
            await view.finish_game(interaction)
            return

        await view.db_cog.update_chess_game(view.user_id, view.board.fen(), view.move_history)
        view.rebuild_items()
        await interaction.edit_original_response(embed=view.build_embed(), view=view)


class ResignButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Resign", style=discord.ButtonStyle.danger, emoji="🏳️", row=1)

    async def callback(self, interaction: discord.Interaction):
        view: ChessGameView = self.view
        await interaction.response.defer()
        await view.finish_game(interaction, resigned=True)


class ChessGameView(discord.ui.View):
    def __init__(self, db_cog, user_id: int, board: chess.Board, bet: int, move_history: str):
        super().__init__(timeout=GAME_VIEW_TIMEOUT_SECONDS)
        self.db_cog = db_cog
        self.user_id = user_id
        self.board = board
        self.bet = bet
        self.move_history = move_history
        self.message: discord.Message | None = None
        self.busy = False
        self.rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This isn't your game — feel free to watch, though!", ephemeral=True
            )
            return False
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    def rebuild_items(self):
        self.busy = False
        self.clear_items()
        self.add_item(MakeMoveButton())
        self.add_item(ResignButton())

    def build_embed(self, *, extra_note: str | None = None) -> discord.Embed:
        board_text = render_board(self.board)
        lines = [f"```\n{board_text}\n```", format_captured(self.move_history)]
        if extra_note:
            lines.append(extra_note)
        elif self.board.is_check():
            lines.append("**Your move (White) — you're in check!**")
        else:
            lines.append("**Your move (White)**")
        lines.append(_format_move_log(self.move_history))

        embed = discord.Embed(title="⚔️ Chess vs. the House", description="\n\n".join(lines), color=discord.Color.gold())
        bet_text = f"Bet: {self.bet:,} chips" if self.bet else "Free game — no chips at stake"
        embed.set_footer(text=f"{bet_text} · type moves like e4, Nf3, O-O")
        return embed

    async def finish_game(self, interaction: discord.Interaction, *, resigned: bool = False):
        """Settles chips, records lifetime stats, clears the persisted
        game row, and hands off to ChessResultView. Call only after
        interaction has already been deferred/responded to."""
        result = "loss" if resigned else _determine_result(self.board)
        payout = self.bet * 2 if result == "win" else self.bet if result == "draw" else 0
        if payout > 0:
            await self.db_cog.add_chips(self.user_id, payout)
        await self.db_cog.delete_chess_game(self.user_id)
        new_badges = await self.db_cog.record_game_result(
            self.user_id, "chess", wagered=self.bet, won=payout, is_win=(result == "win")
        )

        embed = self.build_embed(extra_note=_game_over_text(self.board, result, resigned=resigned))
        badge_field = format_new_badge_field(new_badges)
        if badge_field:
            embed.add_field(name=badge_field[0], value=badge_field[1], inline=False)

        result_view = ChessResultView(self.user_id, self.bet)
        message = await interaction.edit_original_response(embed=embed, view=result_view)
        result_view.message = message
        self.stop()

    async def on_timeout(self):
        """Deliberately does NOT touch the game, the wallet, or the DB
        row — a chess game against a thinking opponent can run for a
        while, and the persisted FEN means the player can always resume
        later. Just greys out the dead buttons on this particular
        message so clicking one doesn't silently do nothing."""
        if not self.message:
            return
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass


class PlayAgainButton(discord.ui.Button):
    def __init__(self, bet: int):
        label = "Play Again" if not bet else f"Play Again ({bet:,})"
        super().__init__(label=label, style=discord.ButtonStyle.success, emoji="⚔️")
        self.bet = bet

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        if self.bet:
            wallet = await db_cog.get_or_create_wallet(interaction.user.id)
            if wallet["balance"] < self.bet:
                view: ChessResultView = self.view
                view.busy = False
                await interaction.response.send_message(
                    f"You don't have {self.bet:,} chips for another {self.bet:,}-chip game — "
                    f"balance is {wallet['balance']:,}. Try Change Bet for a smaller amount.",
                    ephemeral=True,
                )
                return
        # Defer here (not inside start_game — see its docstring) since
        # this is the first response-touching call on this interaction.
        await interaction.response.defer()
        await start_game(interaction, db_cog, self.bet, already_public=True)


class ChangeBetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Change Bet", style=discord.ButtonStyle.secondary, emoji="✏️")

    async def callback(self, interaction: discord.Interaction):
        db_cog = interaction.client.get_cog('Database')
        wallet = await db_cog.get_or_create_wallet(interaction.user.id)
        await interaction.response.edit_message(
            embed=chess_bet_embed(wallet["balance"]),
            view=ChessBetView(wallet["balance"], already_public=True),
        )


class ChessResultView(discord.ui.View):
    def __init__(self, user_id: int, bet: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.busy = False
        self.message: discord.Message | None = None
        self.add_item(PlayAgainButton(bet))
        if bet:
            self.add_item(ChangeBetButton())  # nothing to change on a free game
        self.add_item(BackToCasinoButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This isn't your game — feel free to watch, though!", ephemeral=True
            )
            return False
        if self.busy:
            await interaction.response.send_message("Still processing — try again in a second.", ephemeral=True)
            return False
        self.busy = True
        return True

    async def on_timeout(self):
        if not self.message:
            return
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass
