#! /usr/bin/env python3

# from command import *
from config import *
# from element import *
# from directions import *
from logger import *
import game_rates as GAME_CONFIG
import copy

from model_defs import *


class Perk:
    toremove =False
    perk_type = None
    perk_live = 0

    X = None
    Y = None

    #not_updated_cnt = 0

    updated = False

    def __init__(self, X, Y, ptype, plive):
        self.X = X
        self.Y = Y
        self.perk_type = ptype
        self.perk_live = plive
        #self.not_updated_cnt = 0
        self.updated=False
    
    def tick(self):
        if self.perk_live!=GAME_CONFIG.Infinite and self.perk_live>0:
            self.perk_live-=1
    
    def is_visible(self):
        return self.perk_live>0

    def is_updated(self):
        #if GAME_CONFIG.FLASHING_PERKS:
        #    return self.not_updated_cnt<2
        return self.updated

    def state(self):
        return "X={} Y={} perk_type={} perk_live={} updated={} toremove={}".format(self.X, self.Y, self.perk_type, self.perk_live, self.updated, self.toremove)


    def track_possible_moves(self):
        return ZOMBIE_POSSIBLE_MOVES

    def track_move_dir2xy(self, dir):
        return MAP_ZOMBIE_MOVES_DXY[dir]

class Perks:
    perks = dict()
    perks_map = None
    _width = None
    _height = None

    def __init__(self):
        self.perks=dict()

    def reset_perks_map(self):
        if self._width==None:
            return #first move, not yet initialized
        self.perks_map = [ [0]*self._width for _ in range(self._height) ]

    def tracking_start(self, width, height):
        self._width=width
        self._height=height
        for p in self.perks.values():
            p.updated=False
        self.reset_perks_map()

    def tracking_finish(self): #remove only perks based on not_updated_cnt
        f=False
        for p in self.perks.values():
            # if not p.updated:
            #     p.not_updated_cnt+=1
            if not p.is_updated():
                p.toremove=True
                f=True
            if p.perk_live==0:
                p.toremove=True
                f=True
        if f:
            self.remove()
        self.make_perks_map()
    
    def make_perks_map(self):
        if self._height==None and self.perks:
            LOG("ERROR")
        self.reset_perks_map()        
        for px, py in self.perks.keys():
            self.perks_map[py][px] = 1

    def get_perk_at(self, x, y):
        return self.perks.get( (x,y), None)

    def is_at(self, x, y):
        #p = self.perks.get( (x,y), None)
        #return p!=None
        return self.perks_map and self.perks_map[y][x]>0

    def size(self):
        return len(self.perks)

    def get(self, i):
        if i>=0 and i<len(self.perks.values()):
            return self.perks.values()[i]
        return None

    def remove(self):
        self.perks = dict(filter(lambda p: p[1].toremove==False, self.perks.items()))


    def tick(self):
        for p in self.perks.values():
            p.tick()
        self.make_perks_map()

    def store_state(self, logger):
        for (px, py), p in self.perks.items():
            logger.log(" {},{} : {}".format(px, py, p.state()))
        logger.log("===")

    def clone(self): #deepcopy not works proper for TPerks !!!
        res = Perks()
        res.perks = copy.deepcopy(self.perks)
        res._width = self._width
        res._height = self._height
        res.make_perks_map()
        return res

    def could_be_masked(self, x, y):
        perk = self.perks.get( (x,y) ) 
        if perk!=None: #found just set updated
            perk.updated = True

    def tracking_add_object(self, x, y, data):
        ptype = getattr(data, "PTYPE", PERKTYPE.UNKNOWN)
        perk = self.perks.get( (x,y) )
        if perk!=None: #found, just set updated
            if ptype!=PERKTYPE.UNKNOWN:
                perk.perk_type=ptype
            perk.updated = True
        else:
            self.perks[(x,y)] = Perk(x,y,ptype, data.TICKS)
            self.perks[(x,y)].updated = True
        self.perks_map[y][x]=1
