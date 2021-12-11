import os, sys, copy

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QStackedWidget, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt

from element import *
from game_rates import *
from command import *
import config

qt_app = None

QT_TILE_WIDTH  = 26
QT_TILE_HEIGHT = 26


QT_MAP = None


# def x2c(x):
#     return x*QT_TILE_WIDTH

# def y2c(y):
#     return y*QT_TILE_HEIGHT

def xy2screen(x, y, w, h):
    return (x * QT_TILE_WIDTH, y * QT_TILE_HEIGHT)

def xyc2screen(x, y, w, h):
    pos_x1, pos_y1 = xy2screen(x,   y,   w, h)
    pos_x2, pos_y2 = xy2screen(x+1, y+1, w, h) 
    pos_xc = (pos_x1 + pos_x2)//2
    pos_yc = (pos_y1 + pos_y2)//2
    return (pos_xc, pos_yc)

# def xy2screen_r(x, y, w, h):
#     return (x * QT_TILE_WIDTH, (h - y -1) * QT_TILE_HEIGHT)

# def xyc2screen_r(x, y, w, h):
#     pos_x1, pos_y1 = xy2screen_r(x,   y,   w, h)
#     pos_x2, pos_y2 = xy2screen_r(x+1, y-1, w, h) #-1 due to reverse
#     pos_xc = (pos_x1 + pos_x2)//2
#     pos_yc = (pos_y1 + pos_y2)//2
#     return (pos_xc, pos_yc)

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

    def update_from(self, board, gstate):
        self._board=copy.deepcopy(board)
        self._last_command=gstate.last_cmd
        self._width = board.width
        self._height = board.height


    def qmap(self, t):
        s = QT_MAP.get(t, None)
        return s

    def draw_board(self, painter):
        board = self._board.BOARD
        
        painter.setBrush( Qt.GlobalColor.darkGray)
        painter.drawRect( 0, 0, self.width(), self.height() )

        for x in range(self._width):
            for y in range(self._height):
                pos_x, pos_y = xy2screen(x, y, self._width, self._height)

                t = board[y][x]

                if config.QT_BOARD_SIMPLE_GRAPHIC:
                    if t == ESPACE:
                    #     painter.setBrush( Qt.GlobalColor.darkGray)
                    #     painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                        continue
                    if t == EBATTLE_WALL:
                        painter.setBrush( Qt.gray)
                        painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                        continue
                    if t == ERIVER:
                        painter.setBrush( Qt.GlobalColor.darkBlue)
                        painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                        continue
                    if t == ETREE:
                        painter.setBrush( Qt.GlobalColor.darkGreen)
                        painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                        continue
                pic = self.qmap(t)
                painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)
                

        dx = QT_TILE_WIDTH
        dy = QT_TILE_HEIGHT

        #draw me, type Player
        p = self._board.ME
        if p.is_alive():
            t =  DIR2TANK[p.rotation]

            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))
            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            painter.setPen( Qt.white )
            painter.drawText( xc+(dx//3)+4, (yc+7)  , "{}".format(p.ID))
            painter.drawText( xc-5, (yc+7)  , "{}".format(p.shot_counter))

            if p.perk_IMMORTALITY_cnt:
                painter.drawText( xc+dx, yc+7, "{}".format(p.perk_IMMORTALITY_cnt))
            if p.perk_BREAKING_WALLS_cnt:
                painter.drawText( xc+dx, yc+17, "{}".format(p.perk_BREAKING_WALLS_cnt))
            if p.perk_WALKING_ON_WATER_cnt:
                painter.drawText( xc+dx, yc+27, "{}".format(p.perk_WALKING_ON_WATER_cnt))
            if p.perk_VISIBILITY_cnt:
                painter.drawText( xc+dx+10, yc+7, "{}".format(p.perk_VISIBILITY_cnt))
            if p.perk_NO_SLIDING_cnt:                
                painter.drawText( xc+dx+10, yc+17, "{}".format(p.perk_NO_SLIDING_cnt))
           
            if p.sliding_cnt>0:
                painter.setPen( Qt.white )
                painter.drawText( xc-5, (yc+25)  , "{}".format(p.sliding_cnt))
            
    
        #draw players, type TPlayer
        players = self._board.PLAYERS
        for i in range(players.size()):
            p = players.get(i)
            if not p:
                continue
            t = DIR2TANK_OTHER[p.rotation]
            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            #painter.setBrush( Qt.yellow )
            painter.setPen( Qt.red )
            painter.drawText( xc, yc, "{}".format(p.ID))

            painter.setPen( Qt.white )
            painter.drawText( xc-5, (yc+7)  , "{}".format(p.shot_counter))

            if config.QT_BOARD_SHOW_BULLETS_INFO:
                if p.est_lifetime!=None:
                    painter.setPen( Qt.GlobalColor.black )
                    painter.drawText( xc-5, yc+16 , "{}".format(p.est_lifetime))
                    if p.est_killer_id!=None:
                        painter.drawText( xc-5, yc+25, "{}".format( p.est_killer_id))
                    else:
                        painter.drawText( xc-5, yc+23, "*")

            if p.sliding_cnt>0:
                painter.setPen( Qt.white )
                painter.drawText( xc-5, (yc+25)  , "{}".format(p.sliding_cnt))


        for p in self._board.PERKS.perks.values():
            t = p.perk_type
            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            painter.setPen( Qt.white )
            painter.drawText( xc, yc, "{}".format(p.perk_live))

        #draw Zombies, type TPlayer
        zombies = self._board.ZOMBIES
        for i in range(zombies.size()):
            p = zombies.get(i)
            t = DIR2TANK_AI[p.rotation]
            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            painter.setPen( Qt.red )
            painter.drawText( xc, yc, "{}".format(p.ID))

            painter.setPen( Qt.white )
            painter.drawText( xc-5, (yc+7)  , "{}".format(p.shot_counter))

            if p.ai_has_perk:
                painter.setPen( Qt.white )
                painter.drawText( xc+QT_TILE_WIDTH, yc  , "*")

            if config.QT_BOARD_SHOW_BULLETS_INFO:
                if p.est_lifetime!=None:
                    painter.setPen( Qt.GlobalColor.black )
                    painter.drawText( xc-5, yc+16 , "{}".format(p.est_lifetime))
                    if p.est_killer_id!=None:
                        painter.drawText( xc-5, yc+25, "{}".format( p.est_killer_id))
                    else:
                        painter.drawText( xc-5, yc+23, "*")

            if p.sliding_cnt>0:
                painter.setPen( Qt.white )
                painter.drawText( xc-5, (yc+25)  , "{}".format(p.sliding_cnt))



        #draw bullets
        bullets = self._board.BULLETS
        for i in range(bullets.size()):
            b = bullets.get(i)
            t = b.direction
            t = DIR2BULLET[t]
            pos_x, pos_y = xy2screen(b.X, b.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, self.qmap(t))

            if config.QT_BOARD_SHOW_BULLETS_INFO:
                xc, yc = xy2screen(b.X, b.Y, self._width, self._height)

                painter.setPen( Qt.red )
                painter.drawText( xc, yc  , "{}".format(b.ID))

                if b.parent_id!=None:
                    painter.setPen( Qt.darkRed )
                    painter.drawText( xc+QT_TILE_WIDTH-5, yc, "{}".format(b.parent_id))



        #draw dangers map
        dangers     = self._board.DANGERS_MAP
        if dangers:
            for x in range(self._width):
                for y in range(self._height):

                    pos_xc, pos_yc = xyc2screen(x, y, self._width, self._height)

                    d = dangers[y][x]
                    d = min(d, RATE_DEATH)
                    r = (d * dx)//RATE_DEATH
                    r = min(dx, r) 
                    if r:
                        dd = r//2 - 1
                        if d>0 and dd<=0:
                            dd = 1
                        if dd>0:
                            #painter.setPen( Qt.red )
                            painter.setPen( QPen(Qt.red, 2, Qt.SolidLine) )
                            painter.drawLine(pos_xc-dd, pos_yc-dd, pos_xc+dd, pos_yc+dd)
                            painter.drawLine(pos_xc-dd, pos_yc+dd, pos_xc+dd, pos_yc-dd)
                            #painter.drawLine(pos_x1, pos_y1, pos_x2, pos_y2)
        #players moves
        if config.QT_BOARD_SHOW_PLAYERS_MOVES:        
            for i in range(players.size()):
                p = players.get(i)
                if p.PX!=None and p.PY!=None and (p.X!=p.PX or p.Y!=p.PY) :
                    painter.setPen( QPen(Qt.darkMagenta, 2, Qt.SolidLine) )
                    x1, y1 = xyc2screen(p.X,  p.Y,  self._width, self._height)
                    x2, y2 = xyc2screen(p.PX, p.PY, self._width, self._height) #-1 due to reverse
                    painter.drawLine(x1, y1, x2, y2)

        #zombie moves
        if config.QT_BOARD_SHOW_ZOMBIE_MOVES:        
            for i in range(zombies.size()):
                p = zombies.get(i)
                if p.PX!=None and p.PY!=None and (p.X!=p.PX or p.Y!=p.PY) :
                    painter.setPen( QPen(Qt.darkMagenta, 2, Qt.SolidLine) )
                    x1, y1 = xyc2screen(p.X,  p.Y,  self._width, self._height)
                    x2, y2 = xyc2screen(p.PX, p.PY, self._width, self._height) #-1 due to reverse
                    painter.drawLine(x1, y1, x2, y2)


        attack = self._board.ATTACK_MAP_AI
        if config.QT_BOARD_SHOW_ATTACK_MAP_AI and attack:
            for x in range(self._width):
                for y in range(self._height):
                    if attack[y][x]:
                        x1, y1 = xyc2screen(x,  y,  self._width, self._height)
                        painter.setPen( QPen(Qt.green, 4, Qt.SolidLine) )
                        painter.drawPoint(x1, y1)

        attack = self._board.ATTACK_MAP_OTHER
        if config.QT_BOARD_SHOW_ATTACK_MAP_OTHER and attack:
            for x in range(self._width):
                for y in range(self._height):
                    if attack[y][x]:
                        x1, y1 = xyc2screen(x,  y,  self._width, self._height)
                        painter.setPen( QPen(Qt.blue, 4, Qt.SolidLine) )
                        painter.drawPoint(x1, y1)

        if self._board.last_string_same_cnt!=0:
            font=painter.font()
            oldsize = font.pointSize()
            font.setPointSize ( 64 )
            painter.setFont(font)
            painter.setPen( Qt.white )
            if self._board.is_game_start():
                painter.drawText(10, 10, self.width(), self.height(), Qt.AlignCenter | Qt.AlignTop, "Start")
            else:
                painter.drawText(10, 10, self.width(), self.height(), Qt.AlignCenter | Qt.AlignTop, "{}".format(self._board.last_string_same_cnt))
            font.setPointSize ( oldsize )
            painter.setFont(font)

        if self._last_command!=None:
            x, y = self._board.ME.X, self._board.ME.Y
            for cmd in self._last_command:
                dx, dy, fire  = COMMANDS_XYF[cmd]
                if fire:
                    painter.setPen( QPen(Qt.red, 1, Qt.SolidLine) )
                else:
                    painter.setPen( QPen(Qt.blue, 1, Qt.SolidLine) )
                x+=dx
                y+=dy
                x0, y0 = xy2screen(x, y, self._width, self._height)
                painter.setBrush( Qt.NoBrush )
                painter.drawRect( x0, y0, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                


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

    def update_from(self, bigboard, gstate, title="Tanki"):
        #title = "LGUN t={:3} max={:3}".format(bigboard.lgun_counter, (bigboard.lgun_counter_max,-1)[bigboard.lgun_counter_max==None])
        self.setWindowTitle(title)
        if self.bwidth!=bigboard.width or self.bheight!=bigboard.height:
            self.bwidth=bigboard.width
            self.bheight=bigboard.height
            self.play()    
        self.game.update_from(bigboard, gstate)
        self.repaint()
        qt_app.processEvents()



def qt_create_board():
    global qt_app, qt_game, QT_MAP
    qt_app = QApplication(sys.argv)

    QT_MAP = {}
    for v,p in ESPRITES.items():
        QT_MAP[v] = QPixmap(p)

