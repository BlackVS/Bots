#! /usr/bin/env python3

import copy
from bigboard import *
from player import *
from command import *
from collections import *
from element import *
from qstar import *
from config import *
import time

GOAL_GOLD = 1
GOAL_EXIT = 2
GOAL_EXPLORE = 3
GOAL_ATTACK = 4
GOAL_CUSTOM_TARGET = 10

class BoardsCube(QStar):
    cube = None
    dangers = None

    VMAP = None

    GOALS = []

    HISTORY = []
    HISTORY_LONG = []
    _bigboard = None
    _depth  = None

    def __init__(self, bigboard, qtgame, depth=CUBE_DEPTH):
        self.cube = []
        self.dangers = []
        self._bigboard=bigboard
        self._depth=depth

        for i in range(depth):
            if i==0:
                board = bigboard.clone()
                board.tick0() #some estimation staff for t=0
                dangers = board.make_dangers_map()
                #board.print("\n: tick {}".format(i))
            else:
                board=self.cube[-1].clone()
                board.tick()
                dangers = board.make_dangers_map()
                #board.print("\n: tick {}".format(i))
            self.cube.append(board)
            self.dangers.append(dangers)
        self.reset_vmap()

    def reset_vmap(self):
        self.VMAP = []
        for t in range(self._depth):
            m = [ [QNode(x,y,t) for x in range(self._bigboard.width)] for y in range(self._bigboard.height) ]
            self.VMAP.append(m)        

    def is_goal_reached(self, node):
        # if we reach any exit for example
        board = self.get_board(node.t)

        if GOAL_GOLD in self.GOALS:
            if board.BOARD[node.y][node.x]==EGOLD:
                return True

        if GOAL_EXIT in self.GOALS:
            for ex, ey in board.ENDS:
                if ex==node.x and ey==node.y:
                    return True
        
        if GOAL_EXPLORE in self.GOALS:
            if board.BOARD[node.y][node.x]==EUNKNOWN:
                return True
            if node.x == board.width-1 or node.y==board.height-1:
                return True

        if GOAL_ATTACK in self.GOALS and board.ATTACK_MAP and board.ATTACK_MAP[node.y][node.x]:
            return True

        if GOAL_CUSTOM_TARGET in self.GOALS:
            if board.BOARD[node.y][node.x] in self.GOALS:
                return True

        ### Just move somewhere????
        return False

    def get_dist2goal(self, node):
        t = min(node.t, len(self.VMAP)-1)
        board = self.cube[t]
        vmap  = self.VMAP[t]

        res = 1000000 #must be greate of any distance in map! 

        if GOAL_EXIT in self.GOALS:
            for ex, ey in board.ENDS:
                r = abs(ex-node.x) + abs(ey-node.y)
                res = min(r, res)

        if GOAL_GOLD in self.GOALS:
            return 1 #just BFS to reduce time

        if GOAL_EXPLORE in self.GOALS:
            return 1 #just BFS to reduce time

        if GOAL_CUSTOM_TARGET in self.GOALS:
            return 1 #just BFS to reduce time
        
        return res


    def get_board(self, t):
        t = min(t, len(self.cube)-1)
        return self.cube[t]

    def get_vmap(self, t):
        t = min(t, len(self.VMAP)-1)
        return self.VMAP[t]

    def time2layer(self, t):
        t = min(t, len(self.VMAP)-1)
        return t

    def get_possible_moves(self, node):
        t = self.time2layer(node.t)
        flastlayer = t==(len(self.VMAP)-1)

        res = set()
        if flastlayer:
            moves = COMMANDS_NOTSTAY
        else:
            moves = (COMMANDS_ANY_NO_FIRE,COMMANDS_ANY)[t==0]

        oboard = self.get_board(t)
        for cmd in moves:
            dx, dy, dt, _ = COMMANDS_XYTF[cmd]
            #check if wall or die
            nx, ny, nt = node.x+dx, node.y+dy, node.t+dt

            board=self.get_board(nt)
            if not board.is_onboard(nx, ny):
                continue

            bcell = board.BOARD[ny][nx]
            if bcell in ENOMOVES:
                continue

            if bcell==EGOLD and t==0 and cmd==CMD_NULL: #BUG !!!!
                continue

            if board.lasershots_any_active_at(nx,ny): #lasers fire
                continue

            if board.DANGERS_MAP:
                d = board.DANGERS_MAP[ny][nx]
                if d==RATE_DEATH:
                    continue
            
            #special case - laser into face, can't move direct or jump to it
            if dx<0 and dy==0 and oboard.lasershots_active_is_at(nx,ny,ELASER_RIGHT): 
                continue

            if dx>0 and dy==0 and oboard.lasershots_active_is_at(nx,ny,ELASER_LEFT): 
                continue

            if dx==0 and dy<0 and oboard.lasershots_active_is_at(nx,ny,ELASER_DOWN): 
                continue

            if dx==0 and dy>0 and oboard.lasershots_active_is_at(nx,ny,ELASER_UP): 
                continue

            if cmd in COMMANDS_PULL and bcell!=EBOX:
                continue #nothing to push

            if cmd in COMMANDS_FIRE:
                if node.t==0 and board.ME.can_fire():
                    r = board.rate_move_fire(cmd)
                    if GameConfig.get_game_mode() == GAME_MODE_BERSERK:
                        if r>RATE_FIRE_STARTS: #to not shot to empry start
                            res.add(cmd)
                    if GameConfig.get_game_mode() == GAME_MODE_AUTO:
                        if r>=RATE_FIRE_MAKE_SHOT:
                            res.add(cmd)


                continue

            res.add(cmd)
        return res

    def get_neighbor(self, node, cmd):
        dx, dy, dt, _ = COMMANDS_XYTF[cmd]
        nx, ny, nt = node.x+dx, node.y+dy, node.t+dt
        vmap  = self.get_vmap(nt)
        return vmap[ny][nx]


    def rate_move(self, node, cmd):
        # Rate this move
        dx, dy, dt, _ = COMMANDS_XYTF[cmd]
        nx, ny, nt = node.x+dx, node.y+dy, node.t+dt
        board = self.get_board(nt)

        res = RATE_MOVE_STEP[dt] # minimal rate to allow find shortest paths
        b = board.BOARD[ny][nx]

        if b == EGOLD:
            res += RATE_MOVE_GOLD_DEFAULT #try get gold

        if b in EPERKS:
            res += RATE_MOVE_PERK #try get perk

        #check danger map
        if board.DANGERS_MAP:
            d = board.DANGERS_MAP[ny][nx]
            if d:
                res += d

        if cmd in COMMANDS_FIRE:
            profit = board.rate_move_fire(cmd)
            if profit>0: # 0..100 -> 0..-10
                d = (RATE_MOVE_TARGET*profit)//RATE_FIRE_100
                if d:
                    res += d
                    LOG("CAN FIRE to={} at {} {} {}, d={}".format(cmd, nx, ny, nt, d))

        return res




    def get_best_path_berserk(self, srcX, srcY):
        if not self.cube: 
            return None

        print("BERSERK: ", end="")        
        GameConfig.set_game_mode_cur(GAME_MODE_BERSERK)

        board = self.cube[0]
        start = self.VMAP[0][srcY][srcX]

        GOAL_SURVIVE = {GOAL_EXIT, GOAL_GOLD, GOAL_CUSTOM_TARGET, ESTART, EEXIT, EFLOOR} #  risky:EZOMBIE_START

        # if board.ME.can_fire(): #can fire
        #     ##### TEST
        #     return (CMD_FIRE_LEFT, 0)
        # else:
        #     return (CMD_NULL, 0)

        if board.ME.can_fire(): #can fire
            self.GOALS = GOAL_SURVIVE
            self.reset_vmap()
            score, res = self.search(start, False, set(COMMANDS_FIRE))
            LOGF("RES0: score={} res={}".format(score, res))
            if res!=None and score<MOVE_RATE_RISKY:
                return res

        self.GOALS = {GOAL_ATTACK}
        self.reset_vmap()
        score, res = self.search(start)
        LOGF("RES ATTACK: score={} res={}".format(score, res))
        if res!=None and score<MOVE_RATE_RISKY:
            return res

        self.GOALS = {GOAL_EXIT}
        if board.HAS_PLAYERS:
            self.GOALS |= {GOAL_EXIT, GOAL_EXPLORE}
        if self.GOALS:
            self.reset_vmap()
            score, res = self.search(start)
            LOGF("RES1: score={} res={}".format(score, res))
            if res!=None and score<MOVE_RATE_RISKY:
                return res

        #just survive
        self.GOALS = GOAL_SURVIVE
        self.reset_vmap()
        score, res = self.search(start) #start, True ?
        LOGF("RES5: score={} res={}".format(score, res))
        if res!=None:
            return res

        return res



    def get_best_path(self, srcX, srcY):
        if not self.cube: 
            return None

        board = self.cube[0]
        start = self.VMAP[0][srcY][srcX]

        #return self.get_best_path_berserk(srcX, srcY)
        
        if GameConfig.get_game_mode_default() == GAME_MODE_BERSERK and board.HAS_PLAYERS:
            return self.get_best_path_berserk(srcX, srcY)


        print("AUTO    : ", end="")        
        GameConfig.set_game_mode_cur(GAME_MODE_AUTO)

        #first try gather gold
        GOAL_PROFIT  = {GOAL_EXIT, GOAL_GOLD, GOAL_EXPLORE}
        GOAL_SURVIVE = GOAL_PROFIT | {GOAL_CUSTOM_TARGET, ESTART, EEXIT, EFLOOR} #  risky:EZOMBIE_START

        #check for fire - we can fire if can survive after
        if board.ME.can_fire(): #can fire
            self.GOALS = GOAL_SURVIVE
            self.reset_vmap()
            score, res = self.search(start, False, set(COMMANDS_FIRE))
            LOGF("RES0: score={} res={}".format(score, res))
            if res!=None and score<MOVE_RATE_RISKY:
                return res

        self.GOALS = {GOAL_EXIT}
        if board.HAS_PLAYERS:
            self.GOALS |= {GOAL_EXIT, GOAL_EXPLORE}
        if self.GOALS:
            self.reset_vmap()
            score, res = self.search(start)
            LOGF("RES1: score={} res={}".format(score, res))
            if res!=None and score<MOVE_RATE_RISKY:
                return res

        #try any good
        if self.GOALS!=GOAL_PROFIT:
            self.GOALS = GOAL_PROFIT
            self.reset_vmap()
            score, res = self.search(start)
            LOGF("RES3: score={} res={}".format(score, res))
            if res!=None and self.has_stuck():
                LOGF("STUCK: try to risk")
                return res
            if res!=None and score<MOVE_RATE_RISKY:
                return res

        self.GOALS = {GOAL_ATTACK}
        self.reset_vmap()
        score, res = self.search(start)
        LOGF("RES ATTACK: score={} res={}".format(score, res))
        if res!=None and score<MOVE_RATE_RISKY:
            return res

        #just survive
        self.GOALS = GOAL_SURVIVE
        self.reset_vmap()
        score, res = self.search(start) #start, True ?
        LOGF("RES5: score={} res={}".format(score, res))
        if res!=None:
            return res

        return res


    def get_best_move(self, srcX, srcY):
        res = self.get_best_path(srcX, srcY)

        if len(self.HISTORY)<CUBE_HISTORY_LEN:
            self.HISTORY.append(res)
        else:
            self.HISTORY=self.HISTORY[1:] + [res]

        if len(self.HISTORY_LONG)<CUBE_LONG_HISTORY_LEN:
            self.HISTORY_LONG.append(res)
        else:
            self.HISTORY_LONG=self.HISTORY_LONG[1:] + [res]

        return res
        
    def has_stuck(self):
        if len(self.HISTORY)<CUBE_HISTORY_LEN:
            return False
        return all(c==self.HISTORY[0] for c in self.HISTORY[1:])

    def has_stuck_to_long(self):
        if len(self.HISTORY_LONG)<CUBE_LONG_HISTORY_LEN:
            return False
        return all(c==self.HISTORY_LONG[0] for c in self.HISTORY_LONG[1:])