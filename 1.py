import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def f2(i, j, n):
    arr = np.add.outer(range(n), range(n)) % 2

    for col in range(1, n + 1):
        if col != j:
            arr[-i][col - 1] = 2
    for row in range(1, n + 1):
        if row != i:
            arr[-row][j - 1] = 2

    draw_board(arr, n)


def f1(i, j, n):
    arr = np.add.outer(range(n), range(n)) % 2

    for row in range(i - 1, i + 1 + 1):
        for col in range(j - 1, j + 1 + 1):
            if 1 <= row <= n and 1 <= col <= n and (row, col) != (i, j):
                arr[-row][col - 1] = 2

    draw_board(arr, n)


def draw_board(board, n):

    dx, dy = 0.015, 0.05
    P = np.arange(0, n, dx)
    Q = np.arange(0, n, dy)
    P, Q = np.meshgrid(P, Q)

    min_max = np.min(P), np.max(P), np.min(Q), np.max(Q)

    cmap = ListedColormap(['white', 'black', 'lightgreen'])
    plt.imshow(board, cmap=cmap, extent=min_max)
    plt.grid(True, color='black', linewidth=1.5)
    plt.xticks(list(range(0, n + 1)))
    plt.yticks(list(range(0, n + 1)))
    plt.title("Chessboard")
    #plt.show()
    plt.savefig('res1')


def main():
    board_size = 8
    #coord_y = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    try:
        var = int(input('Input 1 for a king or 2 for a rook: '))
        assert var in (1, 2)
        x, y = input(f'Input coordinates of the chosen figure, format - "1 {board_size}"'
                     f' (2 integer numbers from 1 to {board_size}: ').split()

        x, y = int(x), int(y)        
        assert 1 <= x <= board_size and 1 <= y <= board_size
        #y = coord_y[y]
    except (ValueError, AssertionError):
        print('Incorrect input!')
    else:
        if var == 1:
            f1(x, y, board_size)
        else:
            f2(x, y, board_size)


if __name__ == '__main__':
    main()

