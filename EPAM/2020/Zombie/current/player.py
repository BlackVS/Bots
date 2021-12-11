#!/usr/bin/env python3

from command import *
from config import *
from element import *


GUNT_DT_HEAT = CONFIG['lasergun_dt_heat']
GUNT_DT_COOL = CONFIG['lasergun_dt_cool']
GUNT_RELOAD_TIME = CONFIG["lasergun_reload_time"]
GUNT_COOLING_TIME = CONFIG["lasergun_ticks2cold"]
GUNT_TMAX = GUNT_DT_COOL * CONFIG['lasergun_ticks2cold']

class Player:
    ID = 0
    X  = 0
    Y  = 0
    PX = 0
    PY = 0
  
    is_alive  = False
    is_flying = False

    #_processed = False
    shot_counter = 0
    prev_cmd = CMD_NULL

    gunT       = 0
    gunCooling = 0

    perk_unlim_cnt  = 0
    perk_unstop_cnt = 0
    perk_deathray_cnt = 0


    def __init__(self, id, x=None, y=None, alive=False, flying = False):
        self.ID=id
        self.PX = None
        self.PY = None
        self.X = x
        self.Y = y
        self.is_alive = alive
        self.is_flying = flying
        self.prev_cmd = CMD_NULL
        self.reset_player()

    def reset_player(self):
        self.shot_counter = 0
        self.gunT       = 0
        self.gunCooling = 0
        self.perk_unlim_cnt  = 0
        self.perk_unstop_cnt = 0
        self.perk_deathray_cnt = 0

    def moved(self, x, y, flying):
        if self.X!=x or self.Y!=y or self.is_flying!=flying:
            self.PX = self.X
            self.PY = self.Y
            self.X = x
            self.Y = y
            self.is_flying=flying
        if self.PX and self.PY:
            dx = abs(self.PX-self.X)
            dy = abs(self.PY-self.Y)
            if dx>2 or dy>2:
                self.reset_player() #seems to be jumped between exits (died?)
            
    def set_alive(self, alive):
        if alive!=self.is_alive:
            self.is_alive=alive
            if alive:
                print("Player {} respawn".format(self.ID))
            else:
                print("Player {} died".format(self.ID))
                self.reset_player()

    def do_cmd(self, cmd):

        self.prev_cmd = cmd
        if cmd in COMMANDS_FIRE:
            if self.gunCooling>0:
                LOG("False fire detect, overheated!!!!")
            if self.shot_counter!=0:
                LOG("False fire detect!!!!")
            self.gunT += GUNT_DT_HEAT
            if self.gunT>GUNT_TMAX: 
                #overheating
                self.gunCooling = GUNT_COOLING_TIME
                self.gunT = 0

            if self.perk_unlim_cnt==0:
                self.shot_counter = GUNT_RELOAD_TIME
            else:
                self.gunCooling=0
                self.shot_counter=0
                self.gunT=0
        else:
            if self.gunT>0:
                self.gunT-=GUNT_DT_COOL
            if self.gunCooling:
                self.gunCooling-=1
            if self.shot_counter>0:
                self.shot_counter -= 1

        if self.perk_unlim_cnt:
            self.perk_unlim_cnt-=1

        if self.perk_unstop_cnt:
            self.perk_unstop_cnt-=1

        if self.perk_deathray_cnt:
            self.perk_deathray_cnt-=1
        return True
    
    def can_fire(self):
        return self.shot_counter == 0 and self.gunCooling==0

    def got_perk(self, perk):
        if perk==EDEATH_RAY_PERK:
            self.perk_deathray_cnt = CONFIG['perks_action_dur']
        if perk==EUNLIMITED_FIRE_PERK:
            self.perk_unlim_cnt = CONFIG['perks_action_dur']
            self.gunCooling = 0
            self.shot_counter = 0
            self.gunT = 0
        if perk==EUNSTOPPABLE_LASER_PERK:
            self.perk_unstop_cnt = CONFIG['perks_action_dur']

class LaserShot:
    t  = None
    x  = 0
    y  = 0
    dx = 0
    dy = 0

    updated = False
    active  = False
    nottrack = False

    def __init__(self, t, x, y, dx, dy, updated, active):
        self.t = t
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.updated = updated
        self.active = active

    def tick(self):
        if self.active and self.nottrack:
            return
        self.x += self.dx
        self.y += self.dy
        self.active = True #activate if not yet, 1 tick delay is for players autofire
        


class Zombie:
    ID = 0
    X  = 0
    Y  = 0
    PX = 0
    PY = 0
  
    is_alive  = False
    updated = False

    ###
    NEAR_MOVES    = []
    PREV_NEAR_MOVES    = []    

    def __init__(self, id, x=None, y=None, alive=False, updated=False):
        self.ID=id
        self.PX = None
        self.PY = None
        self.X = x
        self.Y = y
        self.is_alive = alive
        self.updated = updated


    def moved(self, x, y):
        if self.X!=x or self.Y!=y:
            self.PX = self.X
            self.PY = self.Y
            self.X = x
            self.Y = y

    def is_alive(self):
        return  self.is_alive

    def set_alive(self, alive):
        if alive!=self.is_alive:
            self.is_alive=alive
            if alive:
                print("Zombie {} respawn".format(self.ID))
            else:
                print("Zombie {} died".format(self.ID))

    def tick(self):
        pass #move to nearest player or me

    def env_reset_stats(self):
        self.PREV_NEAR_MOVES    = self.NEAR_MOVES
        self.NEAR_MOVES    = []

    def env_found_move(self, dir):
        self.NEAR_MOVES.append( dir )
