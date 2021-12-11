import os, sys, copy

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QStackedWidget, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPainter, QPixmap

from element import *

qt_app = None
qt_game = None


QT_BOARD_WIDTH = 23
QT_BOARD_HEIGHT = 23

QT_TILE_WIDTH = 32
QT_TILE_HEIGHT = 32


QT_MAP = None
class Game(QWidget):
    def __init__(self):
        super(Game, self).__init__()
        qt_app.installEventFilter(self)
        self._board=None

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.draw_board(painter)
        painter.end()

    def set_board(self, board):
        if isinstance(board, str):
            board=board.replace('\n', '')
            self._board = list( list(c for c in board[r*QT_BOARD_WIDTH:((r+1)*QT_BOARD_WIDTH)]) for r in range(QT_BOARD_HEIGHT) )
        else:
            self._board=copy.deepcopy(board)

    def draw_board(self, painter):
        """Wyświetlenie planszy na ekranie"""
        width  = QT_TILE_WIDTH
        height = QT_TILE_HEIGHT

        for x in range(QT_BOARD_WIDTH):
            for y in range(QT_BOARD_HEIGHT):
                pos_x = x * width
                pos_y = y * height

                t = self._board[y][x]
                s = QT_MAP.get(t, None)
                if s!=None:
                   painter.drawPixmap(pos_x, pos_y, width, height, s)
                else:
                    assert()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.game = Game()
        self.setWindowTitle('Bomberman')
        self.show()

    def center(self):
        """Wycentrowanie okna gry na ekranie"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def play(self):
        """Rozpoczęcie nowej gry"""

        self.setCentralWidget(self.game)
        self.resize(QT_BOARD_WIDTH * QT_TILE_WIDTH, QT_BOARD_HEIGHT * QT_TILE_HEIGHT)
        self.center()

    def set_board(self, board):
        self.game.set_board(board)
        self.repaint()
        qt_app.processEvents()



def qt_create_board():
    global qt_app, qt_game, QT_MAP
    qt_app = QApplication(sys.argv)

    QT_MAP = {
                EL_BOMBERMAN:                 QPixmap('./sprites/bomberman.png'),
                EL_BOMB_BOMBERMAN:            QPixmap('./sprites/bomb_bomberman.png'),
                EL_DEAD_BOMBERMAN:            QPixmap('./sprites/dead_bomberman.png'),
                EL_OTHER_BOMBERMAN:           QPixmap('./sprites/other_bomberman.png'),
                EL_OTHER_BOMB_BOMBERMAN:      QPixmap('./sprites/other_bomb_bomberman.png'),
                EL_OTHER_DEAD_BOMBERMAN:      QPixmap('./sprites/other_dead_bomberman.png'),
                EL_BOMB_TIMER_5:              QPixmap('./sprites/bomb_timer_5.png'),
                EL_BOMB_TIMER_4:              QPixmap('./sprites/bomb_timer_4.png'),
                EL_BOMB_TIMER_3:              QPixmap('./sprites/bomb_timer_3.png'),
                EL_BOMB_TIMER_2:              QPixmap('./sprites/bomb_timer_2.png'),
                EL_BOMB_TIMER_1:              QPixmap('./sprites/bomb_timer_1.png'),
                EL_BOOM:                      QPixmap('./sprites/boom.png'),
                EL_WALL:                      QPixmap('./sprites/wall.png'),
                EL_DESTROY_WALL:              QPixmap('./sprites/destroyable_wall.png'),
                EL_DESTROYED_WALL:            QPixmap('./sprites/destroyed_wall.png'),
                EL_MEAT_CHOPPER:              QPixmap('./sprites/meat_chopper.png'),
                EL_DEAD_MEAT_CHOPPER:         QPixmap('./sprites/dead_meat_chopper.png'),
                EL_BOMB_BLAST_RADIUS_INCREASE:QPixmap('./sprites/bomb_blast_radius_increase.png'),
                EL_BOMB_COUNT_INCREASE:       QPixmap('./sprites/bomb_count_increase.png'),
                EL_BOMB_IMMUNE:               QPixmap('./sprites/bomb_immune.png'),
                EL_BOMB_REMOTE_CONTROL:       QPixmap('./sprites/bomb_remote_control.png'),
                EL_NONE:                      QPixmap('./sprites/none.png')
        }

    qt_game = Window()
    qt_game.play()
