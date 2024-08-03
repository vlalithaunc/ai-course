"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # track the number of moves by player X and O
    countX = 0
    countO = 0

    numRows = len(board)

    for row in range(numRows):
        numCols = len(board[row])
        for col in range(numCols):
            # if the space (row, col) has X, then increment num of moves made by X
            if board[row][col] == X:
                countX += 1
            # if the space (row, col) has O, then increment num of moves made by O
            if board[row][col] == O:
                countO += 1

    # if the num of moves by X is more than moves by O, then its O's turn, otherwise X's turn
    if countX > countO:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # create a set to store the possible moves that can be made
    allPossibleActions = set()

    numRows = len(board)

    for row in range(numRows):
        numCols = len(board[row])
        for col in range(numCols):
            # if the space (row, col) does not contain X or O, then it is added as a possible move to the set
            if board[row][col] == EMPTY:
                allPossibleActions.add((row, col))

    return allPossibleActions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # action contains (row, col)
    (row, col) = action

    # if the action cannot be done within the given row and col info, then an exception in raised
    if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
        raise Exception("not a valid action")

    # if the row, col is already occupied, then an exception is raised
    if board[row][col] is not EMPTY:
        raise Exception("not a valid move")

    # original board should be left unmodified, so created a copy, before making changes
    copyOfboard = [row[:] for row in board]
    # given the action (row, col), mark the board with the player who has to go next, which can be determined by player() func.
    copyOfboard[row][col] = player(board)
    return copyOfboard


def checkRow(board, player):
    # check for winning game by 3 in a row
    numRows = len(board)
    # for each row in the board, if all the cells in a row for all cols contains all X's or O's, then return True
    numCols = len(board[0])
    for row in range(numRows):
        if all(board[row][col] == player for col in range(numCols)):
            return True
    return False


def checkCol(board, player):
    # check for winning game by 3 in a col
    numRows = len(board)
    # for each col in the board, if all the cells in a col for all rows contains all X's or O's, then return True
    numCols = len(board[0])
    for col in range(numCols):
        if all(board[row][col] == player for row in range(numRows)):
            return True
    return False


def diagOne(board, player):
    score = 0
    numRows = len(board)
    numCols = len(board[0])
    for row in range(numRows):
        for col in range(numCols):
            # check the diagonal from left to right
            if row == col and board[row][col] == player:
                score += 1
    # if the entire diagonal contains same value (player), then true
    if score == len(board):
        return True
    else:
        return False


def diagTwo(board, player):
    score = 0
    numRows = len(board)
    for i in range(numRows):
        # the diagonal from right to left, so check the right most cell first
        if board[i][len(board) - 1 - i] == player:
            score += 1
    if score == len(board):
        return True
    else:
        return False


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check whether X is winner or O is winner by calling all the helper functions created
    if checkRow(board, X) or checkCol(board, X) or diagOne(board, X) or diagTwo(board, X):
        return X
    elif checkRow(board, O) or checkCol(board, O) or diagOne(board, O) or diagTwo(board, O):
        return O
    return None


def tie(board):
    # check for a tie in the game
    countEmpty = (len(board) * len(board[0]))
    numRows = len(board)
    numCols = len(board[0])
    for row in range(numRows):
        for col in range(numCols):
            # check whether the cells in the board are empty or not
            if board[row][col] is not EMPTY:
                # if the cell is not empty, decrease the value of countEmpty
                countEmpty -= 1

    # by the end of checking the board, if the spaces are not empty and there is no winner, return True
    return countEmpty == 0


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # terminates the game, if either there is a winner or there has been a tie
    if winner(board) is not None or tie(board):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # if X is the winner, returns 1
    if winner(board) == X:
        return 1
    # if O is winner, return -1
    if winner(board) == O:
        return -1
    # for a tie, return 0
    return 0


def max_value(board):
    # set to negative infinity, bc X wants to find the maximum score or higher score
    v = -math.inf
    if terminal(board):
        return utility(board)
    # you are try to find the maximum value that would result from opposing players play
    for action in actions(board):
        # call 'min_value' on the resulting board, to simulate O's optimal response
        # then try to get the maximum of the responses returned by 'min_value'
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    v = math.inf
    if terminal(board):
        return utility(board)
    # you are try to find the minimum value that would result from opposing players play
    for action in actions(board):
        # call 'max_value' on the resulting board, to simulate X's optimal response
        # then try to get the minimum value of the responses returned by 'max_value'
        v = min(v, max_value(result(board, action)))
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # if the game is over, then return nothing
    if terminal(board):
        return None
    # in the case of when the player is X
    elif player(board) == X:
        options = []
        # check which action will result in the min_value for opposing player, and use the highest of the game value
        for action in actions(board):
            # when 'X' considers a move/action, it must account for O's best possible response,
            # hence, it calls 'min_value' to find out the worst case scenario for that move
            options.append([min_value(result(board, action)), action])
        return sorted(options, key=lambda x: x[0], reverse=True)[0][1]
    elif player(board) == O:
        options = []
        for action in actions(board):
            # tuple with max value and the action that results to its value
            options.append([max_value(result(board, action)), action])
        return sorted(options, key=lambda x: x[0])[0][1]
