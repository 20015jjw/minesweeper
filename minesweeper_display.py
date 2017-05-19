#!/usr/bin/python
# coding=utf-8

# curses: user interface lib
# sys, argparse: parse the user input
import curses, sys, argparse
from minesweeper_game import *

# set locale to support unicode emoji
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

X, Y, M = 10, 10, 10
NO_EMOJI = False
HELP_TEXT = """
HJKL/Arrows   left, down, up, right
Space         reveal the tile
U/Z           flag the tile
I/X           reveal surrounding tiles
              (only works when all surrounding mines are flagged)
R             restart the game
Q             quit the game
g,G,0/^,$     top, buttom, leftmost, rightmost
"""

def main(screen):
    """
    main loop function
    """
    # init setup
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    screen.timeout(50)

    # game setup
    game = Mine(X, Y, M, no_print=True)
    cur_y, cur_x = 0, 0

    # help setup
    y, x = game.Y * 2 + 3, game.X * 4 + 5
    # help setup
    h_y = game.Y * 2 + 3
    for ht in HELP_TEXT.split('\n'):
        screen.addstr(h_y, 2, ht)
        h_y += 1
    screen.refresh()

    # game window setup
    win = curses.newwin(y, x, 0, 0)
    win.border(0, 0, 0, 0, 0, 0, 0, 0)
    draw_board(win, game)
    set_cursor(win, cur_y, cur_x, clear=False)

    # status window setup
    swin = curses.newwin(9, 20, y - 9, x)
    swin.border(0, 0, 0, 0, 0, 0, 0, 0)
    swin.addstr(2, 4, "Time:          ")
    swin.addstr(4, 4, "Mines:         ")
    swin.refresh()

    while True:
        if game.end_time:
            swin.addstr(2, 10, str(round(game.end_time - game.start_time, 1)))
            swin.addstr(6, 4, "You Lost" if game.lose else "You Won!")
        elif game.has_start:
            swin.addstr(2, 10, str(round(time() - game.start_time, 3)))
        key = screen.getch()
        if key == ord('q'):
            break
        if key == ord('r'):
            set_cursor(win, cur_y, cur_x, clear=True)
            game = Mine(X, Y, M, no_print=True)
            cur_x, cur_y = 0, 0
            draw_board(win, game)
            set_cursor(win, cur_y, cur_x, clear=False)

            swin.addstr(2, 4, "Time:          ")
            swin.addstr(4, 4, "Mines:         ")
            swin.addstr(6, 4, "               ")
        if key in [curses.KEY_UP, ord('k'),
                   curses.KEY_DOWN, ord('j'),
                   curses.KEY_LEFT, ord('h'),
                   curses.KEY_RIGHT, ord('l'),
                   ord('g'), ord('G'), ord('0'),
                   ord('^'), ord('$')]:
            set_cursor(win, cur_y, cur_x, clear=True)
            if key in [ord('k'), curses.KEY_UP]:
                cur_y -= 1
            if key in [ord('j'), curses.KEY_DOWN]:
                cur_y += 1
            if key in [ord('h'), curses.KEY_LEFT]:
                cur_x -= 1
            if key in [ord('l'), curses.KEY_RIGHT]:
                cur_x += 1
            if key in [ord('^'), ord('0')]:
                cur_x = 0
            if key == ord('g'):
                cur_y = 0
            if key == ord('G'):
                cur_y = -1
            if key == ord('$'):
                cur_x = -1
            cur_y %= game.Y
            cur_x %= game.X
            set_cursor(win, cur_y, cur_x, clear=False)

        if key == ord(' '):
            game.reveal(cur_x, cur_y, printing=True)
            draw_board(win, game)

        if key in [ord('u'), ord('z')]:
            game.flag(cur_x, cur_y)
            draw_board(win, game)

        if key in [ord('i'), ord('x')]:
            game.group_reveal(cur_x, cur_y)
            draw_board(win, game)

        mines = str(game.mine_count - sum(game.flagged))
        swin.addstr(4, 11, mines.ljust(len(str(game.mine_count))))
        swin.refresh()

def draw_board(win, game):
    """
    draw the board tile by tile
    """
    start_idx = 0
    for y in range(2, game.Y * 2+1, 2):
        for idx in range(start_idx, start_idx+game.X):
            b = game.board[idx]
            r = game.revealed[idx]
            f = game.flagged[idx]
            if f:
                c = ('?', curses.A_STANDOUT) if NO_EMOJI else ("🚩", curses.A_NORMAL)
            elif r:
                c = BOARD_CHR_MAP[b] if b <= 0 else (str(b), curses.color_pair(b + 2))
            else:
                c = "#", curses.color_pair(0) | curses.A_DIM
            win.addstr(y, (idx % game.X) * 4 + 4, *c)
        start_idx += game.X
    win.refresh()

def set_cursor(win, cur_y, cur_x, clear=False):
    """
    set the cursor at given coords
    with emoji:
        ->🚩
    without emoji:
        -3-
    """
    m = curses.A_NORMAL if clear else curses.A_BOLD
    y = 2 + 2 * cur_y
    x = 3 + 4 * cur_x
    if NO_EMOJI:
        c = ' ' if clear else '-'
        win.addstr(y, x, c, m)
        win.addstr(y, x+2, c, m)
    else:
        c = '  ' if clear else '->'
        win.addstr(y, x-1, c, m)

    win.refresh()

if __name__ == "__main__":
    description = "Text Minesweeper"
    epilog = "Example: ./minecraft_display.py 5 5 5 -D"
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('x', help='Board width', type=int)
    parser.add_argument('y', help='Board height', type=int)
    parser.add_argument('m', help='Mine count', type=int)
    emoji_help = 'Use this flag to launch the ' + \
                 'game if your terminal does not support emoji'

    parser.add_argument('-D', '--disable_emoji', help=emoji_help, action='store_true')
    args = parser.parse_args()

    X, Y, M = args.x, args.y, args.m
    NO_EMOJI = args.disable_emoji
    BOARD_CHR_MAP = [(' ', curses.A_NORMAL), \
                     ('*', curses.A_BOLD) if NO_EMOJI else ('💣', curses.A_NORMAL)]

    if not 4 <= X <= 100:
        print "Error: The number of rows must be between 4 and 100"
        exit(1)
    if not 4 <= Y <= 100:
        print "Error: The number of columns must be between 4 and 100"
        exit(1)
    if not M < X * Y:
        print "Error: The number of mines must be less than the numbers of tiles"
        exit(1)

    try:
        curses.wrapper(main)
    except curses.error:
        print "Please make your terminal larger or the board smaller " + \
              "and restart the game"
        exit(1)

    exit(0)
