def create_board():
    return [' '] * 9

def print_board(board):
    print()
    for i in range(0, 9, 3):
        row = '|'.join(board[i:i+3])
        print(row)
        if i < 6:
            print('-+-+-')

def set_board(board, index, value):
    index = int(index)
    if 0 <= index < len(board) and board[index] == ' ':
        board[index] = value
        return True
    return False

def check_win(board, player):
    combos = [
        (0,1,2), (3,4,5), (6,7,8),
        (0,3,6), (1,4,7), (2,5,8),
        (0,4,8), (2,4,6)
    ]
    for a,b,c in combos:
        if board[a] == board[b] == board[c] == player:
            return True
    return False

def board_full(board):
    return all(cell != ' ' for cell in board)
