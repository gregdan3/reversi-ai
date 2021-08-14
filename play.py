# /usr/bin/env -S python3 -OO
from reversiboard import RBoard
from player import HumanPlayer, RandomPlayer
from aiplayer import AIPlayer
from time import time


print(
    """
Welcome to an interface for playing Reversi!

Select an option
  1) You vs Yourself
  2) You vs AI
  3) Random vs You
  4) Random vs AI
"""
)

choice = int(input("? "))
if 0 < choice < 5:
    ps = [None, None, None]
    if choice < 3:
        ps[1] = HumanPlayer(1)
    else:
        ps[1] = RandomPlayer(1)
    if choice % 2 == 1:
        ps[2] = HumanPlayer(2)
    else:
        ps[2] = AIPlayer(2)
    # Start game loop
    starttime = int(time())
    board = RBoard()
    while not board.terminal():
        act = ps[board.player()].taketurn(board)
        print(
            "Player "
            + str(board.player())
            + " picked "
            + str(act[0])
            + ","
            + str(act[1])
        )
        print("")
        board = board.result(act)
    print("")
    # Print terminal board
    board.print()
    print("")
    if board.utility(1) > board.utility(2):
        print("\n\nPlayer 1 wins!")
    elif board.utility(1) == 0:
        print("\n\nPlayer 1 and 2 tied!")
    else:
        print("\n\nPlayer 2 wins!")
    # If Random vs AI, print timing info
    if choice == 4:
        if starttime + (60 * 5) > int(time()):
            print("Great. Your AI averaged <5sec per move.")
        else:
            print("Uh oh. Your AI averaged >5sec per move!")
    # print(int(time())-starttime)
else:
    print("Sorry...")
    exit(1)
