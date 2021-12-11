import os, sys, copy

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QStackedWidget, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QColor
from PyQt5.QtCore import Qt

from element import *
import dds

qt_app = None


QT_BOARD_WIDTH = 23
QT_BOARD_HEIGHT = 23

QT_TILE_WIDTH  = 40
QT_TILE_HEIGHT = 40


QT_MAP = None


def x2c(x):
    return x*QT_TILE_WIDTH

def y2c(y):
    return y*QT_TILE_HEIGHT

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
        if self._board==None:
            return
        width  = QT_TILE_WIDTH
        height = QT_TILE_HEIGHT
        dx = QT_TILE_WIDTH
        dy = QT_TILE_HEIGHT


        dangers     = dds.GLOBAL_BOARD_DANGERS
        dangers_t   = dds.GLOBAL_BOARD_DANGERS_t


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
                if dangers!=None:
                    d = dangers[y][x]
                    if d in ELS_BLASTS:
                        r = ord(EL_BOMB_BLAST_5) - ord(d) + 1
                        r=r*4
                        dd = (width - r + 1)//2
                        x1, y1 = pos_x + dd, pos_y + dd
                        x2 = x1 + r
                        y2 = y1 + r
                        if dangers_t[y][x]==0:
                            painter.setPen( Qt.green )
                        elif dangers_t[y][x]==1:
                            painter.setPen( Qt.white )
                        elif dangers_t[y][x]==2:
                            painter.setPen( Qt.yellow )
                        else:
                            painter.setPen( Qt.red )

                        painter.drawLine(x1, y1, x2, y2)
                        painter.drawLine(x2, y1, x1, y2)

        # print labels
        brd = dds.GSTATE
        players = brd.players()
        painter.setPen( Qt.white )
        for i, p in players.items():
            xc = x2c(p.x())
            yc = y2c(p.y())

            #painter.setBrush( Qt.green if p._is_alive else Qt.red)
            #painter.drawRect( xc, yc, 4, 4)


            painter.drawText( xc+(dx//3), yc, "{}".format(p.ID))

            painter.setBrush( Qt.green if p.PERK_IMMUNE_TIMER>0 else Qt.red)
            painter.drawRect( xc+25, yc, 4, 4)
            painter.drawText( xc+dx, yc, "{}".format(p.PERK_IMMUNE_TIMER))

            painter.drawText( xc-5, yc+10 ,"{}".format(p.BOMBS_COUNT))
            painter.drawText( xc-5, yc+20, "{}".format(p.BOMB_POWER))
            painter.drawText( xc-5, yc+30, "{}".format(p.PERK_BLAST_TIMER))

            painter.drawText( xc+dx, yc+dy ,"{}".format(p.PERK_RC_TIMES))

            painter.drawText( xc,       yc+dy+8, "{}".format(p.PERK_POISON_THROWER_TIMER))
            painter.drawText( xc+dx//2, yc+dy+8, "{}".format(p.PERK_POTION_EXPLODER_TIMER))

            if p and p.is_dummy_player():
                painter.setBrush( Qt.red )
                painter.drawRect( xc, yc, 4, 4)

        bombs = brd.bombs()
        for i, b in bombs.items():
            xc = x2c(b.X)
            yc = y2c(b.Y)
            id = "{}".format(b.ID)
            if id == None: id = -1
            painter.setPen( Qt.yellow )
            #painter.drawText( xc+(dx//3), yc+dy+10, "{}".format(id))
            painter.drawText( xc+(dx//3), yc, "{}".format(b.owner))

            painter.drawText( xc + dx, yc+10 ,"{}".format(b.timer))
            painter.drawText( xc + dx, yc+20, "{}".format(b.blast))
            painter.drawText( xc + dx, yc+30, "{}".format( ("?","t", "r")[b.bomb_type]))


        choppers = brd.choppers()
        for i, c in choppers.items():
            xc = x2c(c.X)
            yc = y2c(c.Y)
            id = "{}".format(c.ID)
            if id == None: id = -1
            painter.drawText( xc+(dx//3), yc, "{}".format(id))
            painter.drawText( xc+(dx//3), yc+dy+10, "{}".format( c.get_last_move() ))
            painter.drawText( xc-5, yc+10 ,"{}".format(c.type))

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
        self.setWindowTitle("ID={}".format(dds.GSTATE.counter))
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
                EL_POISON_THROWER     :       QPixmap('./sprites/poison_thrower.png'),
                EL_POTION_EXPLODER    :       QPixmap('./sprites/potion_exploder.png'),
                EL_NONE:                      QPixmap('./sprites/none.png'),
        }

