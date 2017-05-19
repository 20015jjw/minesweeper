from random import shuffle
from time import time

class Mine:
    def __init__(self, X=10, Y=10, mine_count=10, no_print=False):
        assert 1 < X <= 100 and 1 < Y <= 100
        assert 0 < mine_count < X*Y
        self.X = X
        self.Y = Y
        self.mine_count = mine_count
        self.has_start = False
        self.board = [0] * self.X * self.Y
        self.revealed = [0] * self.X * self.Y
        self.flagged = [0] * self.X * self.Y
        self.start_time = 0
        self.end_time = 0
        self.lose = False
        self.no_print = no_print

    def _init_board(self, avoid_idx):
        """
        initialize the board while making sure `avoid_idx` doesn't have a mine.
        This is to enhance the game experience so the player don't click
        on the mine as the first move and lose right way.
        """
        self.has_start = True
        self.revealed = [0] * self.X * self.Y
        ids = range(self.X * self.Y)
        shuffle(ids)
        # keep shuffling until the avoid_idx is not one of the mines
        while avoid_idx in ids[:self.mine_count]:
            shuffle(ids)
        mines = ids[:self.mine_count]
        for pos in mines:
            self.board[pos] = -1

        for i in range(len(self.board)):
            if self.board[i] != -1:
                self.board[i] = self._count_surrending(*self._i2c(i))

        self.start_time = time()
        self._check_win()

    def _count_surrending(self, x, y, flag=False):
        """
        return the surrending mine count for a given coords set
        """
        coords = ((x-1, y-1), (x, y-1), (x+1, y-1), \
                  (x-1, y),             (x+1, y),   \
                  (x-1, y+1), (x, y+1), (x+1, y+1))
        total = 0
        for new_x, new_y in coords:
            i = self._c2i(new_x, new_y)
            if 0 <= new_x < self.X and 0 <= new_y < self.Y and \
                    (self.flagged[i] if flag else (self.board[i] == -1)):
                total += 1
        return total

    def print_mines(self):
        """
        print the board
        """
        if not self.has_start:
            print "No board available."
            return
        for line_start in range(0, self.X * self.Y, self.Y):
            print self.board[line_start:line_start + self.Y]

    def reveal(self, x, y, printing=True):
        """
        reveals a spot at given coord
        priting controls if the fucntion prints itself
        uses recursion to reveal the surrending if the player reveals a 0
        """
        i = self._c2i(x, y)
        if not self.has_start:
            self._init_board(i)
        if self.revealed[i] or self.flagged[i]:
            if printing and not self.no_print:
                print self
            return
        m = self.board[i]
        if m == -1:
            self._ends(lose=True)
        if (m == -1 and not printing) or m != -1:
            self.revealed[i] = 1
        if m == 0:
            coords = ((x-1, y-1), (x, y-1), (x+1, y-1), \
                      (x-1, y),             (x+1, y),   \
                      (x-1, y+1), (x, y+1), (x+1, y+1))
            for new_x, new_y in coords:
                if 0 <= new_x < self.X and 0 <= new_y < self.Y:
                    self.reveal(new_x, new_y, printing=False)
        if printing and not self.no_print:
            print self

    def group_reveal(self, x, y):
        i = self._c2i(x, y)
        if self.revealed[i] and \
                self._count_surrending(x, y, flag=True) == self.board[i]:
            coords = ((x-1, y-1), (x, y-1), (x+1, y-1), \
                      (x-1, y),             (x+1, y),   \
                      (x-1, y+1), (x, y+1), (x+1, y+1))
            for new_x, new_y in coords:
                if 0 <= new_x < self.X and 0 <= new_y < self.Y:
                    self.reveal(new_x, new_y, printing=False)
        if not self.no_print:
            print self

    def flag(self, x, y):
        """
        flag a spot at given coord.
        also checks for winning
        """
        i = self._c2i(x, y)
        if self.revealed[i]:
            return
        self.flagged[i] ^= 1
        self._check_win()
        if not self.no_print:
            print self

    def _check_win(self):
        """
        check if the player has won the game
        """
        if sum(self.flagged) == self.mine_count:
            flag = True
            for i in range(self.X * self.Y):
                if self.flagged[i] and not self.board[i] == -1:
                    flag = False
                    return
            self._ends(lose=False)

    def _ends(self, lose=True):
        self.end_time = time()
        if not self.no_print:
            print round(self.end_time - self.start_time, 3)
            if lose:
                print 'b00m'
            else:
                print 'c0ng'
        for i in range(len(self.board)):
            # self.reveal(*self._i2c(i), printing=False)
            self.revealed[i] = 1
        self.lose = lose

    def __str__(self):
        """
        magic function to turn the board into a pretty string
        """
        if not self.has_start:
            return "No board available."
        res = '  ' + ' '.join(map(str, range(self.X))) + '\n'
        for line_start in range(0, self.X * self.Y, self.X):
            cur_row = self.board[line_start:line_start + self.X]
            cur_revealed = self.revealed[line_start:line_start + self.X]
            cur_flagged = self.flagged[line_start:line_start + self.X]
            cur_res = []
            for i in range(self.X):
                if cur_flagged[i]:
                    cur_res.append('?')
                    continue
                cur_res.append(str(cur_row[i]) if cur_revealed[i] else '_')
                cur_res[-1] = ' ' if cur_res[-1] == '0' else cur_res[-1]
                cur_res[-1] = '*' if cur_res[-1] == '-1' else cur_res[-1]
            res += str(line_start // self.X) + ' ' + ' '.join(cur_res) + '\n'
        return res[:-1]

    def _c2i(self, x, y):
        """
        2D coords -> index
        """
        return self.X * y + x

    def _i2c(self, i):
        """
        index -> 2D coords (x, y)
        >>> m = Mine()
        >>> all([m._c2i(*m._i2c(i)) == i for i in range(100)])
        True
        """
        return (i % self.X, i // self.X)
