import chess
import math

# Material values
P_MAP = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}

# Piece-square tables
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

def evaluate(board: chess.Board) -> float:
    material_white = 0
    material_black = 0
    pos_white = 0
    pos_black = 0

    for sq, piece in board.piece_map().items():
        symbol = piece.symbol()  # 'P','n', etc.
        piece_type = symbol.lower()
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        if piece.color == chess.WHITE:
            material_white += P_MAP[piece_type]
            row_idx = 7 - rank
            if piece_type in PST:
                pos_white += PST[piece_type][row_idx][file]
        else:
            material_black += P_MAP[piece_type]
            row_idx = rank
            if piece_type in PST:
                pos_black += PST[piece_type][row_idx][file]

    material_diff = material_white - material_black
    pos_diff = (pos_white - pos_black) / 10.0
    eval_score = 0.5 * material_diff + 0.5 * pos_diff
    return eval_score

def terminal_value(board: chess.Board) -> float:
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -9999.0
        else:
            return 9999.0
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0.0
    return None

def minimax(board: chess.Board, depth: int, alpha: float = -math.inf, beta: float = math.inf, maximizing: bool = True):

    # Terminal or depth 0
    term = terminal_value(board)
    if term is not None:
        return term, None

    if depth == 0:
        return evaluate(board), None

    best_move = None

    if maximizing:
        max_eval = -math.inf
        for move in board.legal_moves:
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
        for move in board.legal_moves:
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
                # Ask again
                continue

            # After human move, toggle turn
            human_to_move = False

        else:
            # Engine move
            score, san_move = find_best_move_san(board.fen(), 5)  # depth 5 (or choose depth)
            if san_move is None:
                print("No legal AI move (terminal position).")
                break

            try:
                board.push_san(san_move)
            except ValueError:
                try:
                    # Convert SAN to a Move by searching legal moves whose SAN matches
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
                        # try interpreting it as uci string
                        board.push(chess.Move.from_uci(san_move))
                except Exception as e:
                    print("Failed to push AI move:", san_move, "error:", e)
                    break

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
