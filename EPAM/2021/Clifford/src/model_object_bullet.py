#! /usr/bin/env python3

from model_directions import DIR_UNKNOWN
from trackobjects import *
from model_defs import *

# from command import *
from config import CONFIG_CUSTOM
# from element import *
# from directions import *
# from logger import *
import game_rates as GAME_CONFIG


BULLET_SPEED = 2 # base dir twice 

MAP_BULLET_MOVES_DXY_TOTAL = {
    DIR_STOP   : ( 0, 0),
    DIR_LEFT   : (-2, 0),
    DIR_RIGHT  : ( 2, 0),
    DIR_UP     : ( 0, -2),
    DIR_DOWN   : ( 0, 2),
}

MAP_BULLET_MOVES_DXY_STEP = {
    DIR_STOP   : ( 0, 0),
    DIR_LEFT   : (-1, 0),
    DIR_RIGHT  : ( 1, 0),
    DIR_UP     : ( 0, -1),
    DIR_DOWN   : ( 0, 1),
}

MAP_BULLET_POSSIBLE_MOVES_DIR = {
    DIR_UNKNOWN: [ DIR_LEFT, DIR_RIGHT ],
    DIR_LEFT   : [ DIR_LEFT ],
    DIR_RIGHT  : [ DIR_RIGHT ] ,
    DIR_UP     : [ DIR_UP ],
    DIR_DOWN   : [ DIR_DOWN ] ,
}

BULLET_MOVES_DXY_TRACK = [ (-2, 0), (2,0) ]
    
BULLET_DIRS  = [ DIR_UNKNOWN, DIR_LEFT, DIR_RIGHT ]


class TBullet(TObject):
    parent_id = None
    DIR = DIR_UNKNOWN
    toremove = False

    delayed = False
    delayed_appear_cnt = 0
    ricochet_cnt   = 0

    def __init__(self, direction=DIR_UNKNOWN):
        if direction not in BULLET_DIRS:
            print("error")
        self.ricochet_cnt   = CONFIG_CUSTOM.ricochets_max
        self.DIR = direction
        self.delayed = False
        super().__init__()

    def custom_update_from(self, object):
        self.DIR   = object.DIR

    def estimate_next_pos(self): ## ??? почему для пули не реализовал?
        return (None, None, None) # (estimated, x, y)

    def tick1(self):
        dx, dy = MAP_BULLET_MOVES_DXY_STEP[self.DIR]
        self.PX = self.X
        self.PY = self.Y
        self.X += dx
        self.Y += dy

    #track - to not join with simualte!
    def tick(self):
        if self.DIR==DIR_UNKNOWN:
            self.tick_moved = False
            return
        if self.delayed_appear_cnt>0:
            self.delayed_appear_cnt-=1
            self.delayed = True #to not remove after tracking
        else:
            dx, dy = MAP_BULLET_MOVES_DXY_TOTAL[self.DIR]
            self.PX = self.X
            self.PY = self.Y
            self.X += dx
            self.Y += dy
            self.tick_moved = True
            self.delayed =False

    def simulate(self, board):
        if self.DIR==DIR_UNKNOWN:
            self.tick_moved = False
            return
        if self.delayed_appear_cnt>0:
            self.delayed_appear_cnt-=1
            self.delayed = True #to not remove after tracking due to masked by the wall/player for example
        else:
            for j in range(BULLET_SPEED):
                self.tick1()
                if not board.is_onboard(self.X, self.Y):
                    self.toremove = True
                    continue
                c = board.BOARD[self.Y][self.X]
                # MODEL: can riochect from walls
                if self.ricochet_cnt>0 and c in MMOVES.BULLET_RICOCHET_FROM:
                    self.ricochet_cnt-=1
                    self.DIR = DIR_REVERSE[self.DIR]
                    # if recochet - leave in wall
                elif c in MMOVES.BULLET_BARRIER:
                    self.toremove=True
            self.tick_moved = True
            self.delayed = False

    def track_is_hidden(self):
        return self.delayed

    def is_active(self):
        return not self.delayed


    def hit_chance(self, x, y):
        dd = (0,1,2)
        if GAME_CONFIG.CHECK_BULLET_NEW:
            dd = (1,2)
        if self.DIR!=DIR_UNKNOWN:
            dx, dy = DIR2XY[self.DIR]
            nx, ny = self.X, self.Y
            for i in dd: #0, 1, 2 0 - bullet will hit at old position too
                if nx==x and ny==y:
                    return 100
                nx+=dx
                ny+=dy
            return 0
        #uni dir - chance 25?
        for dx, dy in DIR2XY[1:]:
            nx, ny = self.X, self.Y
            for i in dd: #0, 1, 2
                if nx==x and ny==y:
                    return 25
                nx+=dx
                ny+=dy
            return 0
        return 0

    def update_params(self, params):
        dir = getattr(params, "DIR", DIR_UNKNOWN)
        if dir!=DIR_UNKNOWN:
            self.DIR = dir

    def track_possible_moves(self):
        return MAP_BULLET_POSSIBLE_MOVES_DIR[self.DIR]

    def track_move_dir2xy(self, dir):
        return MAP_BULLET_MOVES_DXY_TOTAL[dir]

class TBullets(TObjects):

    def __init__(self):
        #super().__init__() - static object, not called
        self.cleanup()

    #CUSTOM METHODS
    def object_new(self):
        return TBullet()

    def create_object(self, x, y):
        obj = self.object_new()
        obj.X = x
        obj.Y = y
        return obj

    def tracking_add_object(self, x, y, data):
        obj = self.create_object(x, y)
        self.tobjects_new.append( obj )
        return obj

    def tracking_remove_not_updated(self):
        res = [l for l in self.tobjects if l.updated]
        self.tobjects=res

    def tracking_init(self, width, height):
        super().tracking_init(width, height)
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            if p.delayed:
                p.updated=True

    def tracking_finish(self):
        super().tracking_finish()
        #update directions
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            if p.PX!=None and p.PY!=None:
                p.DIR = dxy2dir(p.X-p.PX, p.Y-p.PY)
                if p.DIR not in BULLET_DIRS:
                    print("error")

    def add_custom_bullet(self, x, y, dir, delay):
        if dir not in BULLET_DIRS:
            print("error")
        if dir==DIR_UNKNOWN:
            return
        obj = self.create_object(x, y)
        obj.delayed_appear_cnt = delay
        obj.DIR = dir
        obj.ID = self.get_new_id()
        self.tobjects.append(obj)
        return obj
        
    def store_state(self, logger):
        logger.log_object(self)
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            logger.log_types(p)
            logger.log("{}: ".format(i), endl='')
            logger.log_object(p, False)
        logger.log("===")
        
    def hit_chance(self, x, y):
        chance = 0
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            chance = max(chance, p.hit_chance(x,y))
        return chance


    def could_be_masked(self, x, y):
        bullets = self.get_all_at( x,y ) 
        found = False
        if bullets: 
            for b in bullets: #found just set updated
                b.updated = True
                found = True
        return found

    def tick(self): #just move, we nothing know about baord here
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            p.tick()

    #simulate tick using real board
    def simulate(self, board):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            p.simulate(board)
