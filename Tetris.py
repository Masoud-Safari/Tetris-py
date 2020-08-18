import tkinter as tk
import numpy as np
import time


class Tetris:
    def __init__(self):
        self.block_size = 30
        self.pad = 15

        self.win_color = '#4773b5'
        self.border_color = '#0e1724'
        self.background = '#0f1c4d'
        self.te_color = ['#f0d930', '#2d4aed', '#e8382e', '#54eb49', '#bf53ed', '#53e1e6', '#f5971d', '#ffffff']

        self.te = [0] * 7  # 7 tetromino
        self.create_te(self.te)
        self.ground = np.ones([21, 16], dtype=int)
        self.ground[0:18, 3:13] = 0
        self.color = np.zeros([21, 16], dtype=int)

        self.refresh_rate = 0.04  # seconds
        self.game_speed = 25  # number of frames per each descend
        self.status = 'game_over'
        self.last_status = 'game_over'
        self.counter = 0
        self.current_piece = None
        self.n = 7
        self.next_n = np.random.randint(7)
        self.next_piece = np.copy(np.rot90(self.te[self.next_n], np.random.randint(4)))
        self.row = 0
        self.full_line = np.array([0], dtype=int)

        self.px = 0  # te position (x)
        self.py = 0  # te position (y)

        self.can_h = self.block_size * 18
        self.can_w = self.block_size * 10

        self.win = tk.Tk()
        self.win.configure(bg=self.win_color)
        self.win.geometry(str(self.can_w + self.pad * 4 + self.block_size * 8) + 'x' +
                          str(self.can_h + self.pad * 2 + 8))
        self.win.bind('<Key>', self.key_action)
        self.win.resizable(False, False)

        self.can = tk.Canvas(self.win, bg=self.background, width=self.can_w, height=self.can_h, bd=0,
                             highlightthickness=4, relief='flat', highlightbackground=self.border_color)
        self.can.place(x=self.pad, y=self.pad)

        self.start_label = tk.Label(self.win, text='Press Enter to start\na new game', font='Verdana 15')
        self.start_label.place(x=65, y=200)

        self.go_label = tk.Label(self.win, text='Game Over', fg='red', font='Verdana 15')

        self.pause_label = tk.Label(self.win, text='Game Paused\nPress Enter to continue', font='Verdana 15')

        x_temp = 400
        y_temp = 20
        self.score = tk.IntVar()
        self.score.set(0)
        self.score_label_text = tk.Label(self.win, text='Score:', font='Verdana 15', bg='#4773b5', width=10)
        self.score_label_text.place(x=x_temp, y=2.5 * y_temp)
        self.score_label = tk.Label(self.win, textvariable=self.score, font='Verdana 15',
                                    borderwidth=2, relief='solid', width=10)
        self.score_label.place(x=x_temp, y=4 * y_temp)

        self.level = tk.IntVar()
        self.level.set(1)
        self.level_label_text = tk.Label(self.win, text='Level:', font='Verdana 15', bg='#4773b5', width=10)
        self.level_label_text.place(x=x_temp, y=6.5 * y_temp)
        self.level_label = tk.Label(self.win, textvariable=self.level, font='Verdana 15',
                                    borderwidth=2, relief='solid', width=10)
        self.level_label.place(x=x_temp, y=8 * y_temp)

        self.line = tk.IntVar()
        self.line.set(0)
        self.line_label_text = tk.Label(self.win, text='lines:', font='Verdana 15', bg='#4773b5', width=10)
        self.line_label_text.place(x=x_temp, y=10.5 * y_temp)
        self.line_label = tk.Label(self.win, textvariable=self.line, font='Verdana 15',
                                   borderwidth=2, relief='solid', width=10)
        self.line_label.place(x=x_temp, y=12 * y_temp)

        self.next_label_text = tk.Label(self.win, text='Next piece:', font='Verdana 15', bg='#4773b5', width=10)
        self.next_label_text.place(x=x_temp, y=14.5 * y_temp)
        self.next_can = tk.Canvas(self.win, bg=self.background, width=self.block_size * 6, height=self.block_size * 6,
                                  bd=0, highlightthickness=4, relief='flat', highlightbackground=self.border_color)
        self.next_can.place(x=370, y=330)

        try:
            while True:
                self.game_logic()

                self.win.update()
                time.sleep(self.refresh_rate)

        except tk.TclError:
            pass

    def game_logic(self):
        if self.status != 'game_over':
            if self.status == 'descend':
                if self.tick():
                    self.descend()

            elif self.status == 'new_piece':
                self.new_piece()

            elif self.status == 'mark_line':
                if self.tick():
                    self.del_line()

    def tick(self):
        self.counter = self.counter + 1
        if self.counter >= self.game_speed:
            self.counter = 0
            return True
        else:
            return False

    def new_game(self):
        self.ground[0:18, 3:13] = 0
        self.color = self.color * 0

        self.refresh_rate = 0.04  # seconds
        self.game_speed = 25  # number of frames per each descend
        self.counter = 0
        self.current_piece = None
        self.n = 7
        self.next_n = np.random.randint(7)
        self.next_piece = np.copy(np.rot90(self.te[self.next_n], np.random.randint(4)))
        self.row = 0

        self.score.set(0)
        self.level.set(1)
        self.line.set(0)

        self.px = 0  # te position (x)
        self.py = 0  # te position (y)

        self.draw()

    def check_line(self):
        self.row = np.sum(self.ground[0:18, 3:13], 1)
        self.full_line = np.where(self.row == 10)
        if len(self.full_line[0]) != 0:
            for i in range(len(self.full_line[0])):
                self.color[self.full_line[0][i], 3:13] = 7

            self.draw()
            self.status = 'mark_line'
        else:
            self.status = 'new_piece'

    def del_line(self):
        n_line = len(self.full_line[0])
        for i in range(n_line):
            self.ground[1:self.full_line[0][i] + 1, 3:13] = self.ground[0:self.full_line[0][i], 3:13]
            self.color[1:self.full_line[0][i] + 1, 3:13] = self.color[0:self.full_line[0][i], 3:13]

        if n_line == 1:
            self.update_score('1_line')
        elif n_line == 2:
            self.update_score('2_line')
        elif n_line == 3:
            self.update_score('3_line')
        elif n_line == 4:
            self.update_score('4_line')

        self.status = 'new_piece'

    def descend(self):
        if not self.collision(1, 0, 0):
            self.px = self.px + 1  # descend
            self.draw()
            self.status = 'descend'
        else:
            self.put_piece()
            self.update_score('one')
            self.check_line()

    def instant_descent(self):
        dx = 0
        while not self.collision(dx, 0, 0):
            dx = dx + 1

        if dx >= 1:
            self.px = self.px + dx - 1

        self.counter = 0
        self.put_piece()
        self.update_score('one')
        self.draw()
        self.check_line()

    def key_action(self, event):
        k = event.keysym

        if self.status == 'game_over':
            if k == 'Return':
                self.go_label.place_forget()
                self.start_label.place_forget()
                self.new_game()
                self.new_piece()
                self.status = 'descend'

        elif self.status == 'pause':
            if k == 'Return':
                self.status = self.last_status
                self.pause_label.place_forget()
                self.draw()

        else:
            if k == 'Left':
                if not self.collision(0, -1, 0):
                    self.py = self.py - 1
                    self.draw()

            elif k == 'Right':
                if not self.collision(0, 1, 0):
                    self.py = self.py + 1
                    self.draw()

            elif k == 'Up':
                if not self.collision(0, 0, 1):
                    self.current_piece = np.rot90(self.current_piece, 1)
                    self.draw()

            elif k == 'Down':
                if not self.collision(0, 0, 3):
                    self.current_piece = np.rot90(self.current_piece, 3)
                    self.draw()

            elif k == 'space':
                self.instant_descent()
                self.draw()

            elif k == 'Return':
                self.last_status = self.status
                self.status = 'pause'
                self.can.delete('all')
                self.next_can.delete('all')
                self.pause_label.place(x=45, y=(self.pad + 5 * self.block_size))

    def collision(self, dx, dy, rot):
        x, y = self.current_piece.shape

        return np.max(self.ground[self.px + dx:self.px + x + dx, self.py + dy:self.py + y + dy] +
                      np.rot90(self.current_piece, rot)) == 2

    def new_piece(self):
        self.current_piece = self.next_piece
        self.n = self.next_n
        self.next_n = np.random.randint(7)
        rot = np.random.randint(4)
        self.next_piece = np.copy(np.rot90(self.te[self.next_n], rot))
        self.px = 0
        self.py = int(8 - np.around(self.next_piece.shape[1] / 2))
        if self.collision(0, 0, 0):
            self.put_piece()
            self.status = 'game_over'
            self.go_label.place(x=110, y=150)
            self.start_label.place(x=65, y=200)
        else:
            self.status = 'descend'

    def put_piece(self):
        x, y = self.current_piece.shape
        px = self.px
        py = self.py

        self.ground[px:px + x, py:py + y][self.current_piece == 1] = self.current_piece[self.current_piece == 1]
        self.color[px:px + x, py:py + y][self.current_piece == 1] = self.n * self.current_piece[self.current_piece == 1]

        self.n = 7

    def draw(self):
        bd = 3
        self.can.delete('all')
        self.next_can.delete('all')
        d = self.block_size
        for i in range(18):
            for j in range(3, 13):
                if self.ground[i, j] == 1:
                    self.can.create_rectangle((j - 3) * d + bd, i * d + bd, (j - 2) * d + bd, (i + 1) * d + bd,
                                              fill=self.te_color[self.color[i, j]], width=2, outline=self.border_color)

        if self.n != 7:
            x, y = self.current_piece.shape
            px = self.px
            py = self.py
            for i in range(x):
                for j in range(y):
                    if self.current_piece[i, j] == 1:
                        self.can.create_rectangle((py + j - 3) * d + bd, (px + i) * d + bd,
                                                  (py + j - 2) * d + bd, (px + i + 1) * d + bd,
                                                  fill=self.te_color[self.n],
                                                  width=2, outline=self.border_color)

        x, y = self.next_piece.shape
        px = (6 - x) // 2
        py = (6 - y) // 2
        for i in range(x):
            for j in range(y):
                if self.next_piece[i, j] == 1:
                    self.next_can.create_rectangle((j + px) * d, (i + py) * d, (j + px + 1) * d, (i + py + 1) * d,
                                                   fill=self.te_color[self.next_n], width=2, outline=self.border_color)

    def update_score(self, e):
        if e == 'one':
            self.score.set(self.score.get() + 25)
            pass
        elif e == '1_line':
            self.score.set(self.score.get() + 100)
            self.line.set(self.line.get() + 1)
            pass
        elif e == '2_line':
            self.score.set(self.score.get() + 200)
            self.line.set(self.line.get() + 2)
            pass
        elif e == '3_line':
            self.score.set(self.score.get() + 400)
            self.line.set(self.line.get() + 3)
            pass
        elif e == '4_line':
            self.score.set(self.score.get() + 800)
            self.line.set(self.line.get() + 4)

        self.level.set(self.line.get() // 10 + 1)
        self.game_speed = max(27 - 2 * self.level.get(), 1)

    @staticmethod
    def create_te(t):
        t[0] = np.zeros([4, 4])
        t[0][:, 1] = 1

        t[1] = np.zeros([3, 3])
        t[1][1, :] = 1
        t[1][0, 2] = 1

        t[2] = np.fliplr(np.copy(t[1]))

        t[3] = np.zeros([3, 3])
        t[3][1, 0:2] = 1
        t[3][0, 1:3] = 1

        t[4] = np.fliplr(np.copy(t[3]))

        t[5] = np.zeros([3, 3])
        t[5][1, :] = 1
        t[5][0, 1] = 1

        t[6] = np.ones([2, 2])


game = Tetris()
