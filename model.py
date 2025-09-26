import chess
import math

# Material values
P_MAP = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}

# Piece-square tables (same as you provided)
PST = {
    'p': [
        [0,0,0,0,0,0,0,0],
        [50,50,50,50,50,50,50,50],
        [10,10,20,30,30,20,10,10],
        [5,5,10,25,25,10,5,5],
        [0,0,0,20,20,0,0,0],
        [5,-5,-10,0,0,-10,-5,5],
        [5,10,10,-20,-20,10,10,5],
        [0,0,0,0,0,0,0,0]
    ],
    'n': [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,0,0,0,0,-20,-40],
        [-30,0,10,15,15,10,0,-30],
        [-30,5,15,20,20,15,5,-30],
        [-30,0,15,20,20,15,0,-30],
        [-30,5,10,15,15,10,5,-30],
        [-40,-20,0,5,5,0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ],
    'b': [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,0,0,0,0,0,0,-10],
        [-10,0,5,10,10,5,0,-10],
        [-10,5,5,10,10,5,5,-10],
        [-10,0,10,10,10,10,0,-10],
        [-10,10,10,10,10,10,10,-10],
        [-10,5,0,0,0,0,5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ],
    'r': [
        [0,0,0,0,0,0,0,0],
        [5,10,10,10,10,10,10,5],
        [-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5],
        [0,0,0,5,5,0,0,0]
    ],
    'q': [
        [-20,-10,-10,-5,-5,-10,-10,-20],
        [-10,0,0,0,0,0,0,-10],
        [-10,0,5,5,5,5,0,-10],
        [-5,0,5,5,5,5,0,-5],
        [0,0,5,5,5,5,0,-5],
        [-10,5,5,5,5,5,0,-10],
        [-10,0,5,0,0,0,0,-10],
        [-20,-10,-10,-5,-5,-10,-10,-20]
    ],
    'k': [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20,20,0,0,0,0,20,20],
        [20,30,10,0,0,10,30,20]
    ]
}

def pst_lookup(piece_char: str, square: int, color: bool) -> int:
    if piece_char not in PST:
        return 0
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    row_idx = 7 - rank if color == chess.WHITE else rank
    return PST[piece_char][row_idx][file]
def _pst_value_for_piece_on_square(piece: chess.Piece, square: int) -> int:
    if piece is None:
        return 0
    piece_char = piece.symbol().lower()
    return pst_lookup(piece_char, square, piece.color)
def score_move(board: chess.Board, move: chess.Move) -> float:
    moving_piece = board.piece_at(move.from_square)
    if moving_piece is None:
        return -9999.0
    if move.promotion:
        promoted_piece = chess.Piece(move.promotion, moving_piece.color)
        moved_char = promoted_piece.symbol().lower()
        pst_from = _pst_value_for_piece_on_square(moving_piece, move.from_square)
        pst_to = pst_lookup(promoted_piece.symbol().lower(), move.to_square, promoted_piece.color)
    else:
        moved_char = moving_piece.symbol().lower()
        pst_from = _pst_value_for_piece_on_square(moving_piece, move.from_square)
        pst_to = _pst_value_for_piece_on_square(moving_piece, move.to_square)
    captured_piece = None
    captured_sq = None
    if board.is_capture(move):
        if board.is_en_passant(move):
            cap_rank = chess.square_rank(move.from_square)
            cap_file = chess.square_file(move.to_square)
            captured_sq = chess.square(cap_file, cap_rank)
            captured_piece = board.piece_at(captured_sq)
        else:
            captured_sq = move.to_square
            captured_piece = board.piece_at(captured_sq)
    if captured_piece is None:
        captured_value = 0
        pst_captured = 0
    else:
        captured_value = P_MAP.get(captured_piece.symbol().lower(), 0)
        pst_captured = _pst_value_for_piece_on_square(captured_piece, captured_sq)
    pst_increase = (pst_to - pst_from)
    score = 0.6 * captured_value + 0.4 * (pst_increase / 10.0) + (0.2 * pst_captured if captured_piece else 0)
    return score

def moves_priority_queue(board: chess.Board):
    scored = []
    for move in board.legal_moves:
        s = score_move(board, move)
        scored.append((s, move))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for (_, m) in scored]

# EVALUATION FUNCTIONS
def evaluate(board: chess.Board) -> float:
    material_white = 0
    material_black = 0
    pos_white = 0
    pos_black = 0
    for sq, piece in board.piece_map().items():
        piece_type = piece.symbol().lower()
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        if piece.color == chess.WHITE:
            material_white += P_MAP.get(piece_type, 0)
            row_idx = 7 - rank
            if piece_type in PST:
                pos_white += PST[piece_type][row_idx][file]
        else:
            material_black += P_MAP.get(piece_type, 0)
            row_idx = rank
            if piece_type in PST:
                pos_black += PST[piece_type][row_idx][file]
    material_diff = material_white - material_black
    pos_diff = (pos_white - pos_black) / 10.0
    eval_score = 0.5 * material_diff + 0.5 * pos_diff
    return eval_score
def terminal_value(board: chess.Board) -> float:
    if board.is_checkmate():
        return -9999.0 if board.turn == chess.WHITE else 9999.0
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0.0
    return None
def minimax(board: chess.Board, depth: int, alpha: float = -math.inf, beta: float = math.inf, maximizing: bool = True):
    term = terminal_value(board)
    if term is not None:
        return term, None
    if depth == 0:
        return evaluate(board), None
    best_move = None
    if maximizing:
        max_eval = -math.inf
        for move in moves_priority_queue(board):
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in moves_priority_queue(board):
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def find_best_move_san(fen: str, depth: int):
    board = chess.Board(fen)
    score, best_move = minimax(board, depth, -math.inf, math.inf, board.turn == chess.WHITE)
    if best_move is None:
        return score, None
    try:
        san = board.san(best_move)
    except Exception:
        san = best_move.uci()
    return score, san

def play(fen: str, player_starts: bool):
    depth = 4
    board = chess.Board(fen)
    human_to_move = player_starts
    while True:
        print("\nCurrent board:")
        print(board)  # ASCII board
        print("FEN:", board.fen())
        if board.is_game_over():
            print("Game over:", board.result(), "-", board.outcome())
            break
        if human_to_move:
            user_raw = input("Your move (SAN or UCI). Type 'quit' to exit: ").strip()
            if user_raw.lower() in ("quit", "exit"):
                print("Exiting.")
                break
            moved = False
            try:
                board.push_san(user_raw)
                moved = True
            except ValueError:
                # Try UCI
                try:
                    move = chess.Move.from_uci(user_raw)
                    if move in board.legal_moves:
                        board.push(move)
                        moved = True
                    else:
                        print("That UCI move is not legal in this position.")
                except Exception:
                    print("Couldn't parse move as SAN or UCI.")

            if not moved:
                continue
            human_to_move = False

        else:
            score, san_move = find_best_move_san(board.fen(), depth)  # depth 4 by default for speed
            if san_move is None:
                print("No legal AI move (terminal position).")
                break

            try:
                board.push_san(san_move)
            except ValueError:
                # fallback: try to find the matching move object among legal moves
                pushed = False
                for m in board.legal_moves:
                    try:
                        if board.san(m) == san_move:
                            board.push(m)
                            pushed = True
                            break
                    except Exception:
                        continue
                if not pushed:
                    # final fallback: try UCI
                    board.push(chess.Move.from_uci(san_move))

            print(f"AI plays: {san_move}   (Eval: {score})")
            human_to_move = True

    # final position
    print("\nFinal board:")
    print(board)
    print("Result:", board.result())
    if board.is_checkmate():
        print("Checkmate. Winner:", "Black" if board.turn == chess.WHITE else "White")

# Example
if __name__ == "__main__":
    start_fen = chess.STARTING_FEN
    play(start_fen, player_starts=True)
