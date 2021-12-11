import os, sys, copy

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QStackedWidget, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt

# from element import *
from game_rates import *
# from command import *
import config

from model import *

qt_app = None

QT_TILE_WIDTH  = 26
QT_TILE_HEIGHT = 26


QT_SPRITES_INPUT = None
QT_SPRITES_BOARD = None
QT_SPRITES_HERO  = None
QT_SPRITES_PLAYER= None
QT_SPRITES_ZOMBIE= None
QT_SPRITES_PERKS = None
QT_SPRITES_BULLET = None


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
        self._board_big=None
        self._board_input=None

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.draw_board(painter)
        painter.end()

    def update_board_big(self, board_big, gstate):
        self._board_big=copy.deepcopy(board_big)
        self._last_command=gstate.last_cmd
        self._width = board_big.width
        self._height = board_big.height

    def update_board_input(self, board_orig, width, height):
        self._board_input=copy.deepcopy(board_orig)
        self._width = width
        self._height = height

    def get_sprite_input(self, t):
        s = QT_SPRITES_INPUT.get(t, None)
        return s

    def get_sprite_board(self, t):
        s = QT_SPRITES_BOARD.get(t, None)
        return s

    def get_sprite_hero(self, dir, alive, mask=False):
        return QT_SPRITES_HERO.get(dir, None)

    def get_sprite_player(self, dir, alive, mask=False):
        return QT_SPRITES_PLAYER.get(dir, None)

    def get_sprite_zombie(self, dir, alive, mask=False):
        return QT_SPRITES_ZOMBIE.get(dir, None)

    def draw_board_input(self, painter):
        board = self._board_input
        
        painter.setBrush( Qt.GlobalColor.darkGray)
        painter.drawRect( 0, 0, self.width(), self.height() )

        for x in range(self._width):
            for y in range(self._height):
                pos_x, pos_y = xy2screen(x, y, self._width, self._height)
                t = board[y*self._width+x]
                clr = ELI.SPRITES_COLORS.get(t, None)
                if clr!=None:
                    c = QColor(*clr)
                    painter.setBrush( c)
                    painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                    continue
                pic = self.get_sprite_input(t)
                painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)
                

    def draw_board(self, painter):
        if self._board_input!=None:
            return self.draw_board_input(painter)

        board = self._board_big.BOARD
        
        painter.setBrush( Qt.GlobalColor.darkGray)
        painter.drawRect( 0, 0, self.width(), self.height() )

        for x in range(self._width):
            for y in range(self._height):
                pos_x, pos_y = xy2screen(x, y, self._width, self._height)
                t = board[y][x]

                clr = ELB.SPRITES_COLORS.get(t, None)
                if clr!=None:
                    c = QColor(*clr)
                    painter.setBrush( c)
                    painter.drawRect( pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT )
                    continue
                pic = self.get_sprite_board(t)
                painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)
                

        dx = QT_TILE_WIDTH
        dy = QT_TILE_HEIGHT

        #draw me, type Player
        p = self._board_big.ME
        # if p.is_alive():
        pic =  self.get_sprite_hero(p.DIR, p.is_alive())
        if pic!=None:
            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)
        
            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            if p.is_alive():
                painter.setPen( Qt.GlobalColor.white )
            else:
                painter.setPen( Qt.GlobalColor.red)
            painter.drawText( xc+(dx//2)-4, yc, "{}".format(p.get_ID()))
            # painter.drawText( xc-5, (yc+7)  , "{}".format(p.shot_counter))

            painter.drawText( xc+dx+1, yc+7 , "{}".format(p.perk_RING_cnt))
            painter.drawText( xc+dx+1, yc+17, "{}".format(p.perk_KNIFE_cnt))
            painter.drawText( xc+dx+1, yc+27, "{}".format(p.perk_GLOVE_cnt))

            if p.perk_IMMORTALITY_cnt:
                painter.drawText( xc+dx+10, yc+7, "{}".format(p.perk_IMMORTALITY_cnt))
           
    
        # #draw players, type TPlayer
        players = self._board_big.PLAYERS
        for i in range(players.size()):
            p = players.get(i)
            if not p:
                continue
            pic =  self.get_sprite_player(p.DIR, p.is_alive())
            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)

            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            #painter.setBrush( Qt.yellow )
            if p.is_alive():
                painter.setPen( Qt.GlobalColor.white )
            else:
                painter.setPen( Qt.GlobalColor.red)
            painter.drawText( xc+(dx//2)-4, yc, "{}".format(p.get_ID()))

            painter.drawText( xc+dx+1, yc+7 , "{}".format(p.perk_RING_cnt))
            painter.drawText( xc+dx+1, yc+17, "{}".format(p.perk_KNIFE_cnt))
            painter.drawText( xc+dx+1, yc+27, "{}".format(p.perk_GLOVE_cnt))

            if p.perk_IMMORTALITY_cnt:
                painter.drawText( xc+dx+10, yc+7, "{}".format(p.perk_IMMORTALITY_cnt))

            # painter.drawText( xc, yc+7, "{}".format(p.cnt_same_position))

            if p and p.is_dummy():
                painter.setBrush( Qt.red )
                painter.drawRect( xc, yc, 4, 4)

        #     painter.setPen( Qt.white )
        #     #painter.drawText( xc-5, (yc+7)  , "{}".format(p.shot_counter))

        #     # if config.QT_BOARD_SHOW_BULLETS_INFO:
        #     #     if p.est_lifetime!=None:
        #     #         painter.setPen( Qt.GlobalColor.black )
        #     #         painter.drawText( xc-5, yc+16 , "{}".format(p.est_lifetime))
        #     #         # if p.est_killer_id!=None:
        #     #         #     painter.drawText( xc-5, yc+25, "{}".format( p.est_killer_id))
        #     #         # else:
        #     #         #     painter.drawText( xc-5, yc+23, "*")


        for p in self._board_big.PERKS.perks.values():
            pic  = QT_SPRITES_PERKS.get(p.perk_type, None)
            pos_x, pos_y = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)

            xc, yc = xy2screen(p.X, p.Y, self._width, self._height)
            if p.perk_live!=Infinite:
                painter.setPen( Qt.white )
                painter.drawText( xc, yc, "{}".format(p.perk_live))

        #draw Zombies, type TPlayer
        zombies = self._board_big.ZOMBIES
        for i in range(zombies.size()):
            p = zombies.get(i)
            pic =  self.get_sprite_zombie(p.DIR, p.is_alive())
            px, py = xy2screen(p.X, p.Y, self._width, self._height)
            painter.drawPixmap(px, py, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)

            if p.is_alive():
                painter.setPen( Qt.GlobalColor.white )
            else:
                painter.setPen( Qt.GlobalColor.red)
            painter.drawText( px+(dx//2)-4, py, "{}".format(p.get_ID()))

        #     painter.setPen( Qt.white )
        #     #painter.drawText( xc-5, (yc+7)  , "{}".format(p.shot_counter))

        #     if config.QT_BOARD_SHOW_BULLETS_INFO:
        #         if p.est_lifetime!=None:
        #             painter.setPen( Qt.GlobalColor.black )
        #             painter.drawText( xc-5, yc+16 , "{}".format(p.est_lifetime))
        #             if p.est_killer_id!=None:
        #                 painter.drawText( xc-5, yc+25, "{}".format( p.est_killer_id))
        #             else:
        #                 painter.drawText( xc-5, yc+23, "*")


        #draw bullets
        bullets = self._board_big.BULLETS
        for i in range(bullets.size()):
            b = bullets.get(i)
            pic = QT_SPRITES_BULLET.get(b.DIR, None)
            pos_x, pos_y = xy2screen(b.X, b.Y, self._width, self._height)
            painter.drawPixmap(pos_x, pos_y, QT_TILE_WIDTH, QT_TILE_HEIGHT, pic)

            if config.QT_BOARD_SHOW_BULLETS_INFO:
                xc, yc = xy2screen(b.X, b.Y, self._width, self._height)

                painter.setPen( Qt.red )
                painter.drawText( xc, yc  , "{}".format(b.ID))

                if b.parent_id!=None:
                    painter.setPen( Qt.darkRed )
                    painter.drawText( xc+QT_TILE_WIDTH-5, yc, "{}".format(b.parent_id))



        #draw dangers map
        if config.QT_BOARD_SHOW_DANGERS_MAP:
            dangers     = self._board_big.DANGERS_MAP
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
        # #players moves
        # if config.QT_BOARD_SHOW_PLAYERS_MOVES:        
        #     for i in range(players.size()):
        #         p = players.get(i)
        #         if p.PX!=None and p.PY!=None and (p.X!=p.PX or p.Y!=p.PY) :
        #             painter.setPen( QPen(Qt.darkMagenta, 2, Qt.SolidLine) )
        #             x1, y1 = xyc2screen(p.X,  p.Y,  self._width, self._height)
        #             x2, y2 = xyc2screen(p.PX, p.PY, self._width, self._height) #-1 due to reverse
        #             painter.drawLine(x1, y1, x2, y2)

        # #zombie moves
        # if config.QT_BOARD_SHOW_ZOMBIE_MOVES:        
        #     for i in range(zombies.size()):
        #         p = zombies.get(i)
        #         if p.PX!=None and p.PY!=None and (p.X!=p.PX or p.Y!=p.PY) :
        #             painter.setPen( QPen(Qt.darkMagenta, 2, Qt.SolidLine) )
        #             x1, y1 = xyc2screen(p.X,  p.Y,  self._width, self._height)
        #             x2, y2 = xyc2screen(p.PX, p.PY, self._width, self._height) #-1 due to reverse
        #             painter.drawLine(x1, y1, x2, y2)


        # attack = self._board.ATTACK_MAP_AI
        # if config.QT_BOARD_SHOW_ATTACK_MAP_AI and attack:
        #     for x in range(self._width):
        #         for y in range(self._height):
        #             if attack[y][x]:
        #                 x1, y1 = xyc2screen(x,  y,  self._width, self._height)
        #                 painter.setPen( QPen(Qt.green, 4, Qt.SolidLine) )
        #                 painter.drawPoint(x1, y1)

        # attack = self._board.ATTACK_MAP_OTHER
        # if config.QT_BOARD_SHOW_ATTACK_MAP_OTHER and attack:
        #     for x in range(self._width):
        #         for y in range(self._height):
        #             if attack[y][x]:
        #                 x1, y1 = xyc2screen(x,  y,  self._width, self._height)
        #                 painter.setPen( QPen(Qt.blue, 4, Qt.SolidLine) )
        #                 painter.drawPoint(x1, y1)

        # if self._board.last_string_same_cnt!=0:
        #     font=painter.font()
        #     oldsize = font.pointSize()
        #     font.setPointSize ( 64 )
        #     painter.setFont(font)
        #     painter.setPen( Qt.white )
        #     if self._board.is_game_start():
        #         painter.drawText(10, 10, self.width(), self.height(), Qt.AlignCenter | Qt.AlignTop, "Start")
        #     else:
        #         painter.drawText(10, 10, self.width(), self.height(), Qt.AlignCenter | Qt.AlignTop, "{}".format(self._board.last_string_same_cnt))
        #     font.setPointSize ( oldsize )
        #     painter.setFont(font)

        mmap = self._board_big.PLAYER_POSSIBLE_DIRS
        dd = 10
        if config.QT_BOARD_SHOW_MOVES_MAP and mmap:
            painter.setPen( QPen(Qt.green, 1, Qt.SolidLine) )
            for x in range(self._width):
                for y in range(self._height):
                    xc, yc = xyc2screen(x, y, self._width, self._height)
                    moves = mmap[y][x]
                    if moves:
                        for m in moves:
                            mdx, mdy = DIR2XY[m]
                            painter.drawLine(xc, yc, xc+mdx*dd, yc+mdy*dd)
                
        cmap = self._board_big.PLAYER_POSSIBLE_MOVES
        colors = [QPen(Qt.yellow, 1, Qt.SolidLine), QPen(Qt.green, 1, Qt.SolidLine), QPen(Qt.red, 1, Qt.SolidLine)]
        if config.QT_BOARD_SHOW_CMDS_MAP and cmap:
            #painter.setPen(  )
            for x in range(self._width):
                for y in range(self._height):
                    xc, yc = xyc2screen(x, y, self._width, self._height)
                    moves = cmap[y][x]
                    if moves:
                        for m in moves:
                            dx1, dy1, dx2, dy2, idc = CMDS.QT_COMMANDS_VIEW[m]
                            if idc==None:
                                continue
                            painter.setPen( colors[idc] )
                            painter.drawLine(xc+dx1, yc+dy1, xc+dx2, yc+dy2)
            

        if self._last_command!=None:
            x, y = self._board_big.ME.X, self._board_big.ME.Y
            for cmd in self._last_command:
                dx, dy, _ = CMDS.QSTAR_COMMAND_DXYW_TOTAL(cmd)
                if CMDS.COMMAND_HAS_FIRE(cmd):
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

    def draw_board_big(self, bigboard, gstate, title="Game board"):
        #title = "LGUN t={:3} max={:3}".format(bigboard.lgun_counter, (bigboard.lgun_counter_max,-1)[bigboard.lgun_counter_max==None])
        self.setWindowTitle(title)
        if self.bwidth!=bigboard.width or self.bheight!=bigboard.height:
            self.bwidth=bigboard.width
            self.bheight=bigboard.height
            self.play()    
        self.game.update_board_big(bigboard, gstate)
        self.repaint()
        qt_app.processEvents()

    def draw_board_input(self, board, w, h, title="Game board"):
        self.setWindowTitle(title)
        if self.bwidth!=w or self.bheight!=h:
            self.bwidth =w
            self.bheight=h
            self.play()    
        self.game.update_board_input(board, w, h)
        self.repaint()
        qt_app.processEvents()


def qt_create_board():
    global qt_app, qt_game, QT_MAP_BIGBOARD, QT_SPRITES_INPUT, QT_SPRITES_BOARD, QT_SPRITES_HERO, QT_SPRITES_PLAYER, QT_SPRITES_ZOMBIE, QT_SPRITES_PERKS, QT_SPRITES_BULLET
    qt_app = QApplication(sys.argv)

    QT_SPRITES_INPUT = {}
    for v,p in ELI.SPRITES.items():
        QT_SPRITES_INPUT[v] = QPixmap(p)

    QT_SPRITES_BOARD = {}
    for v,p in ELB.SPRITES.items():
        QT_SPRITES_BOARD[v] = QPixmap(p)

    QT_SPRITES_HERO = {}
    for v,p in ELB.SPRITES_HERO_DIR.items():
        QT_SPRITES_HERO[v] = QPixmap(p)

    QT_SPRITES_PLAYER = {}
    for v,p in ELB.SPRITES_PLAYER_DIR.items():
        QT_SPRITES_PLAYER[v] = QPixmap(p)

    QT_SPRITES_ZOMBIE = {}
    for v,p in ELB.SPRITES_ZOMBIE_DIR.items():
        QT_SPRITES_ZOMBIE[v] = QPixmap(p)

    QT_SPRITES_PERKS = {}
    for v,p in ELB.SPRITES_PERKS.items():
        QT_SPRITES_PERKS[v] = QPixmap(p)

    QT_SPRITES_BULLET = {}
    for v,p in ELB.SPRITES_BULLET_DIR.items():
        QT_SPRITES_BULLET[v] = QPixmap(p)
        
