import os, sys, copy

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QStackedWidget, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt

from element import *
from game_rates import *

qt_app = None

QT_TILE_WIDTH  = 26
QT_TILE_HEIGHT = 26


QT_MAP = None


def xy2screen_r(x, y, w, h):
    return (x * QT_TILE_WIDTH, (h - y -1) * QT_TILE_HEIGHT)

def xyc2screen_r(x, y, w, h):
    pos_x1, pos_y1 = xy2screen_r(x,   y,   w, h)
    pos_x2, pos_y2 = xy2screen_r(x+1, y-1, w, h) #-1 due to reverse
    pos_xc = (pos_x1 + pos_x2)//2
    pos_yc = (pos_y1 + pos_y2)//2
    return (pos_xc, pos_yc)

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

    def update_from(self, board, title="Board"):
        self._board=copy.deepcopy(board)
        self._width = board.width
        self._height = board.height


    def qmap(self, t):
        s = QT_MAP.get(t, None)
        if s==None:
            s = QT_MAP.get(EUNKNOWN, None)
        return s

    def draw_board(self, painter):
        board = self._board.BOARD
        for x in range(self._width):
            for y in range(self._height):
                pos_x, pos_y = xy2screen_r(x, y, self._width, self._height)
                t = board[y][x]
                if t == EFLOOR:
                    continue
                if t == EWALL:
                    painter.setBrush( Qt.gray)
                    painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                    continue
                if t == EBOX:
                    painter.setBrush( Qt.darkYellow)
                    painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                    continue
                painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

        dx = QT_TILE_WIDTH
        dy = QT_TILE_HEIGHT

        #draw me
        p = self._board.ME
        if p.is_alive:
            t =  (EROBO,EROBO_FLYING)[p.is_flying]
            pos_x, pos_y = xy2screen_r(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))
            xc, yc = xy2screen_r(p.X, p.Y, self._width, self._height)
            painter.setPen( Qt.black )
            #painter.drawText( xc+(dx//3)+4, (yc+7)  , "{}".format(p.ID))
            painter.drawText( xc+(dx//3)+4, (yc+7)  , "{}".format(p.shot_counter))
            painter.drawText( xc-5, (yc+7)  , "{}".format(p.gunT))
            painter.drawText( xc-5, yc+15, "{}".format(p.gunCooling))

            painter.drawText( xc+dx, yc+7, "{}".format(p.perk_unstop_cnt))
            painter.drawText( xc+dx, yc+17, "{}".format(p.perk_unlim_cnt))
            painter.drawText( xc+dx, yc+27, "{}".format(p.perk_deathray_cnt))

        #draw players
        players = self._board.PLAYERS
        for i in range(players.size()):
            p = players.get(i)
            if not p:
                continue
            t = EROBO_OTHER
            if p.flying:
                t = EROBO_OTHER_FLYING
            if not p.alive:
                t = EROBO_OTHER_LASER
            pos_x, pos_y = xy2screen_r(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

            xc, yc = xy2screen_r(p.X, p.Y, self._width, self._height)
            #painter.setBrush( Qt.yellow )
            painter.setPen( Qt.black )
            painter.drawText( xc+(dx//3)+4, (yc+7)  , "{}".format(p.ID))

        #draw Zombies
        zombies = self._board.ZOMBIES
        for i in range(zombies.size()):
            p = zombies.get(i)
            t = EMALE_ZOMBIE
            pos_x, pos_y = xy2screen_r(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

            xc, yc = xy2screen_r(p.X, p.Y, self._width, self._height)
            #painter.setBrush( Qt.yellow )
            painter.setPen( Qt.white )
            painter.drawText( xc+(dx//3)+4, (yc+7)  , "{}".format(p.ID))


        #draw lasers
        lasershots = self._board.LASERSHOTS
        for l in lasershots:
            t = l.t
            pos_x, pos_y = xy2screen_r(l.x, l.y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))


        #draw dangers map
        dangers     = self._board.DANGERS_MAP
        if dangers:
            for x in range(self._width):
                for y in range(self._height):
                    pos_x1, pos_y1 = xy2screen_r(x,   y,   self._width, self._height)
                    pos_x2, pos_y2 = xy2screen_r(x+1, y-1, self._width, self._height) #-1 due to reverse

                    pos_xc = (pos_x1 + pos_x2)//2
                    pos_yc = (pos_y1 + pos_y2)//2

                    d = dangers[y][x]
                    d = min(d, RATE_DEATH)
                    r = (d * dx)//RATE_DEATH
                    r = min(dx, r) 
                    if r:
                        dd = r//2 - 1
                        if dd>0:
                            #painter.setPen( Qt.red )
                            painter.setPen( QPen(Qt.red, 2, Qt.SolidLine) )
                            painter.drawLine(pos_xc-dd, pos_yc-dd, pos_xc+dd, pos_yc+dd)
                            painter.drawLine(pos_xc-dd, pos_yc+dd, pos_xc+dd, pos_yc-dd)
                            #painter.drawLine(pos_x1, pos_y1, pos_x2, pos_y2)
        #players moves
        for i in range(players.size()):
            p = players.get(i)
            if p.PX!=None and p.PY!=None and (p.X!=p.PX or p.Y!=p.PY) :
                if p.flying:
                    painter.setPen( QPen(Qt.blue, 4, Qt.SolidLine) )
                else:
                    painter.setPen( QPen(Qt.green, 2, Qt.SolidLine) )
                x1, y1 = xyc2screen_r(p.X,  p.Y,  self._width, self._height)
                x2, y2 = xyc2screen_r(p.PX, p.PY, self._width, self._height) #-1 due to reverse
                painter.drawLine(x1, y1, x2, y2)

        attack     = self._board.ATTACK_MAP
        if attack:
            for x in range(self._width):
                for y in range(self._height):
                    if attack[y][x]:
                        x1, y1 = xyc2screen_r(x,  y,  self._width, self._height)
                        painter.setPen( QPen(Qt.green, 4, Qt.SolidLine) )
                        painter.drawPoint(x1, y1)

class Window(QMainWindow):

    bwidth = 0
    bheight = 0

    def __init__(self):
        super().__init__()

        self.game = Game()
        self.setWindowTitle('Zombie')
        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def play(self):
        self.setCentralWidget(self.game)
        self.resize(self.bwidth * QT_TILE_WIDTH, self.bheight * QT_TILE_HEIGHT)
        self.center()

    def update_from(self, bigboard, title="Zombie"):
        title = "LGUN t={:3} max={:3}".format(bigboard.lgun_counter, (bigboard.lgun_counter_max,-1)[bigboard.lgun_counter_max==None])
        self.setWindowTitle(title)
        if self.bwidth!=bigboard.width or self.bheight!=bigboard.height:
            self.bwidth=bigboard.width
            self.bheight=bigboard.height
            self.play()    
        self.game.update_from(bigboard)
        self.repaint()
        qt_app.processEvents()



def qt_create_board():
    global qt_app, qt_game, QT_MAP
    qt_app = QApplication(sys.argv)

    QT_MAP = {
        EUNKNOWN        : QPixmap('./sprites/unknown.png'),
        EFLOOR          : QPixmap('./sprites/floor.png'),
        EWALL           : QPixmap('./sprites/wall.png'),
        # EWALL_FRONT     : QPixmap('./sprites/wall.png'),
        # EANGLE_IN_RIGHT : QPixmap('./sprites/wall.png'),
        # EWALL_RIGHT     : QPixmap('./sprites/wall.png'),
        # EANGLE_BACK_RIGHT: QPixmap('./sprites/wall.png'),
        # EWALL_BACK      : QPixmap('./sprites/wall.png'),
        # EANGLE_BACK_LEFT: QPixmap('./sprites/wall.png'),
        # EWALL_LEFT      : QPixmap('./sprites/wall.png'),
        # EWALL_BACK_ANGLE_LEFT: QPixmap('./sprites/wall.png'),
        # EWALL_BACK_ANGLE_RIGHT: QPixmap('./sprites/wall.png'),
        # EANGLE_OUT_RIGHT: QPixmap('./sprites/wall.png'),
        # EANGLE_OUT_LEFT: QPixmap('./sprites/wall.png'),
        ESPACE: QPixmap('./sprites/space.png'),
        ELASER_MACHINE_CHARGING_LEFT: QPixmap('./sprites/laser_charging_L.png'),
        ELASER_MACHINE_CHARGING_RIGHT: QPixmap('./sprites/laser_charging_R.png'),
        ELASER_MACHINE_CHARGING_UP: QPixmap('./sprites/laser_charging_D.png'),
        ELASER_MACHINE_CHARGING_DOWN: QPixmap('./sprites/laser_charging_U.png'),
        ELASER_MACHINE_READY_LEFT: QPixmap('./sprites/laser_ready_L.png'),
        ELASER_MACHINE_READY_RIGHT: QPixmap('./sprites/laser_ready_R.png'),
        ELASER_MACHINE_READY_UP: QPixmap('./sprites/laser_ready_D.png'),
        ELASER_MACHINE_READY_DOWN: QPixmap('./sprites/laser_ready_U.png'),
        ESTART: QPixmap('./sprites/start.png'),
        EEXIT: QPixmap('./sprites/exit.png'),
        EHOLE: QPixmap('./sprites/hole.png'),
        EZOMBIE_START: QPixmap('./sprites/zombie_start.png'),
        EGOLD: QPixmap('./sprites/gold.png'),
        EUNSTOPPABLE_LASER_PERK: QPixmap('./sprites/perk_laser_unstoppable.png'),
        EDEATH_RAY_PERK: QPixmap('./sprites/perk_death_ray.png'),
        EUNLIMITED_FIRE_PERK: QPixmap('./sprites/perk_unlim_fire.png'),
        EFOG: QPixmap('./sprites/fog.png'),
        EEMPTY: QPixmap('./sprites/empty.png'),
        EBOX: QPixmap('./sprites/box.png'),
        EROBO: QPixmap('./sprites/robo_2.png'),
        EROBO_FALLING: QPixmap('./sprites/robo_falling.png'),
        EROBO_LASER: QPixmap('./sprites/robo_dead4laser.png'),
        EROBO_OTHER: QPixmap('./sprites/robo_other_2.png'),
        EROBO_OTHER_FALLING: QPixmap('./sprites/robo_other_falling.png'),
        EROBO_OTHER_LASER: QPixmap('./sprites/robo_other_dead4laser.png'),
        ELASER_LEFT: QPixmap('./sprites/laser_L.png'),
        ELASER_RIGHT: QPixmap('./sprites/laser_R.png'), #reverse
        ELASER_UP: QPixmap('./sprites/laser_D.png'),
        ELASER_DOWN: QPixmap('./sprites/laser_U.png'),
        EFEMALE_ZOMBIE: QPixmap('./sprites/zombie_f.png'),
        EMALE_ZOMBIE: QPixmap('./sprites/zombie_m.png'),
        EZOMBIE_DIE: QPixmap('./sprites/zombie_die.png'),
        # system elements, don"t touch it
        # #EBACKGROUND="G"
        EROBO_FLYING: QPixmap('./sprites/robo_flying_2.png'),
        EROBO_OTHER_FLYING: QPixmap('./sprites/robo_other_fly2.png'),
        #EROBO_OTHER_FLYING: QPixmap('./sprites/robo_flying_2.png'),
        # system elements, don"t touch it
        # FOG=("LAYER1", "F"),
        # BACKGROUND=("LAYER2", "G")
        }

