from player import Player


CORNERS = {(0, 0), (0, 7), (7, 0), (7, 7)}

RISK_ADJACENT_CORNER = {
    (0, 1),  # top left
    (1, 0),
    (1, 7),  # bot left
    (0, 6),
    (7, 1),  # top right
    (6, 0),
    (7, 6),  # bot right
    (6, 7),
}
RISK_INNER_CORNERS = {(1, 1), (1, 6), (6, 1), (6, 6)}

RISK_CORNERS = RISK_INNER_CORNERS | RISK_ADJACENT_CORNER


WORSE_EDGES = (
    {(0, y) for y in (3, 4)}
    | {(7, y) for y in (3, 4)}
    | {(x, 0) for x in (3, 4)}
    | {(x, 7) for x in (3, 4)}
)

BETTER_EDGES = (
    {(0, y) for y in (2, 5)}
    | {(7, y) for y in (2, 5)}
    | {(x, 0) for x in (2, 5)}
    | {(x, 7) for x in (2, 5)}
)

EDGES = WORSE_EDGES | BETTER_EDGES

RISK_EDGES = (
    {(1, y) for y in (2, 3, 4, 5)}
    | {(6, y) for y in (2, 3, 4, 5)}
    | {(x, 1) for x in (2, 3, 4, 5)}
    | {(x, 6) for x in (2, 3, 4, 5)}
)
CENTER_BOONS = {(2, 2), (2, 5), (5, 2), (5, 5)}


class AIPlayer(Player):
    def __init__(self, p):
        self.playerN = p

    def minimax(self, board, depth=1000):
        actions = board.actions()
        if len(actions) == 0 or depth == 0:
            # find other reasons to return utility?
            return (
                None,
                more_pieces_utility(board, board.player())
                + board.utility(board.player()),
            )

        if board.player() == 2:  # optimize for us
            bestact = None
            bestutil = float("-inf")
            for action in actions:
                _, utility = self.minimax(board.result(action), depth - 1)
                utility += composite_utility(board, action, 2)
                if utility > bestutil:
                    bestact = action
                    bestutil = utility
            return bestact, bestutil

        # optimize for opponent
        worstact = None
        worstutil = float("inf")
        for action in actions:
            _, utility = self.minimax(board.result(action), depth - 1)
            utility += composite_utility(board, action, 1)
            if utility < worstutil:
                worstact = action
                worstutil = utility
        return worstact, worstutil

    def taketurn(self, board):
        board.print()
        return self.minimax(board, 4)[0]

    def player(self):
        return self.playerN


def more_pieces_utility(board, player):
    """ Count pieces owned by `player`,
        subtract pieces owned by opponent,
        return result. Negative for 1. """
    if player == 2:  # optimizing player, for us
        return board.countpieces(2) - board.countpieces(1)
        # this util cares about having more pieces than opponent
    return -1 * (board.countpieces(1) - board.countpieces(2))
    # same, but negative, because opponent player


def owned_pieces_utility(board, player):
    """ Count pieces owned by `player`, return result.
        Negative for 1. """
    if player == 2:  # optimizing player, for us
        return board.countpieces(2)
    return -1 * board.countpieces(1)


def move_utility(move, player):
    """ http://mnemstudio.org/game-reversi-example-2.htm
        position scoring based on risk factors presented here
        any position that opens an Edge or Corner is bad
        placing a piece in those positions is good """
    if move in CORNERS:
        score = 25
    elif move in BETTER_EDGES:
        score = 7
    elif move in WORSE_EDGES:
        score = 5
    elif move in CENTER_BOONS:
        score = 8
    elif move in RISK_ADJACENT_CORNER:
        score = -10
    elif move in RISK_INNER_CORNERS:
        score = -15
    elif move in RISK_EDGES:
        score = -5
    else:
        score = 0

    if player == 2:
        return score
    return score * -1


def composite_utility(board, move, player):
    return move_utility(move, player) + more_pieces_utility(board, player)


def dynamic_utility(board, move, player):
    pieces = board.countpieces(2) + board.countpieces(1)

    if pieces < 16:  # early game, 15 moves
        # we only care about move utility
        # piece count is irrelevant, only power matters
        return move_utility(move, player) - (more_pieces_utility(board, player) // 2)
        # early game strat is to minimize losable pieces, letting us take more later

    if 44 > pieces >= 16:  # mid game, 28 moves
        return move_utility(move, player) + (more_pieces_utility(board, player) // 2)
        # setting up is still important, but having a lot of pieces now matters too

    return move_utility(move, player) // 1.5 + more_pieces_utility(board, player)
    # end game, 21 moves
    # more pieces matters in full, but we still weight moves strongly
    # cause any good moves remaining are still good,
    # and bad moves remaining are still bad
