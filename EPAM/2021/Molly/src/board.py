#! /usr/bin/env python3
import shutil, os
from math import sqrt
from point import Point
from element import *
from direction import *
from config import *
from collections import *
import boardQt
from copy import copy, deepcopy
from logger import *

ACTIONS =       [ 'LEFT'    , 'RIGHT'   , 'UP'      , 'DOWN'    , 'STOP']
MOVES   =       [(-1, 0)    , (1,0)     , (0,-1)    , (0,1)     , (0,0) ]
ACTIONS_MAP =   { 'LEFT':0  , 'RIGHT':1 , 'UP':2    , 'DOWN':3  , 'STOP':4 }
MOVES_MAP   =   { (-1, 0):0 , (1,0):1   ,  (0,-1):2 , (0,1):3   , (0,0):4 }

GAMERES_OK          = 0
GAMERES_WRONG_INPUT = 1
GAMERES_OVER        = 2
GAMERES_INACTIVE    = 3

GAMERES2STR = [ "OK", "WRONG INPUT", "GAME OVER", "GAME INACTIVE"] 

DANGERS_TYPE_NONE         = 0
DANGERS_TYPE_BLAST        = 1
DANGERS_TYPE_CHOPPER      = 2
DANGERS_TYPE_DEAD_CHOPPER = 3


def dx2dir(ox, oy, nx, ny):
    dx = nx - ox
    dy = ny - oy
    return MOVES_MAP.get( (dx,dy), None )    

class Player:
    ID = 0
    _X = 0
    _Y = 0
    _PX = 0
    _PY = 0
    _SAME_POS_CNT = 0
    _is_alive = False
    _processed = False

    _my_bombs_ids  = None
    _my_rc_bomb_id = None
    
    _est_next_move = None
    _est_act_pre   = None
    _est_act_post  = None

    BOMB_POWER  = None  #current our game power
    BOMBS_COUNT = None

    #perks
    PERK_BLAST_TIMER = 0
    PERK_BOMB_COUNTS_TIMER = 0
    PERK_IMMUNE_TIMER = 0
    PERK_RC_TIMES = 0
    PERK_POISON_THROWER_TIMER = 0
    PERK_POTION_EXPLODER_TIMER = 0


    NEAR_PERKS    = []
    NEAR_PLAYERS  = []
    NEAR_CHOPPERS = []
    NEAR_BOMBS    = []
    NEAR_MOVES    = []

    PREV_NEAR_PERKS    = []
    PREV_NEAR_PLAYERS  = []
    PREV_NEAR_CHOPPERS = []
    PREV_NEAR_BOMBS    = []
    PREV_NEAR_MOVES    = []

    def __init__(self, id):
        self.ID=id
        self.init_from_config()
        # if DEBUG:
        #     if id==0:
        #         self.PERK_IMMUNE_TIMER=10

    def dump(self):
        LOGD("===== PLAYER {} =========".format(self.ID))
        LOGD(" X,Y = {}, {}".format(self._X, self._Y))
        LOGD(" BOMB_POWER = {}".format(self.BOMB_POWER))
        LOGD(" BOMBS_COUNT = {}".format(self.BOMBS_COUNT))
        LOGD(" PERK_BLAST_TIMER = {}".format(self.PERK_BLAST_TIMER))
        LOGD(" PERK_BOMB_COUNTS_TIMER = {}".format(self.PERK_BOMB_COUNTS_TIMER))
        LOGD(" PERK_IMMUNE_TIMER = {}".format(self.PERK_IMMUNE_TIMER))
        LOGD(" PERK_RC_TIMES = {}".format(self.PERK_RC_TIMES))
        LOGD(" PERK_POISON_THROWER = {}".format(self.PERK_POISON_THROWER_TIMER))
        LOGD(" PERK_POTION_EXPLODER = {}".format(self.PERK_POTION_EXPLODER_TIMER))
        LOGD("=========================\n")

    def dump_as_code(self):
        LOGD("  ({}, {}) : ({}, {}, {}, {}, {}, {}, {}),".format(self._X, self._Y, \
            self.ID, self.BOMB_POWER, self.BOMBS_COUNT, 
            self.PERK_BLAST_TIMER, self.PERK_BOMB_COUNTS_TIMER, self.PERK_IMMUNE_TIMER, self.PERK_RC_TIMES) )

    def init_from_config(self):
        config_init() #due static initialization need sure that config read
        if self.BOMB_POWER==None:
            self.BOMB_POWER = CONFIG["bombPower"]
        if self.BOMBS_COUNT==None:
            self.BOMBS_COUNT = CONFIG["bombsCount"]

    def bomb_power(self):
        return self.BOMB_POWER

    def lifes(self):
        return self.PERK_IMMUNE_TIMER

    def set_alive(self, state):
        if self._is_alive!=state:
            LOGD("PLAYER {} ".format(self.ID) + ("DIED","RESPAWNED")[state])
            self._is_alive=state

    def event_moved(self, x, y): #pos updated - i.e. next round - update pwned perks!
        self._PX = self._X
        self._PY = self._Y
        self._X = x
        self._Y = y
        if x!=self._PX or y!=self._PY:
            LOGD("PLAYER {} MOVED to: {},{}".format(self.ID,x,y))
            self._SAME_POS_CNT=0
        else:
            self._SAME_POS_CNT+=1

    def is_dummy_player(self):
        return self._SAME_POS_CNT>5
        
    def reset_processed(self):
        self._processed=False

    def set_processed(self):
        self._processed=True

    def env_reset_stats(self):
        self.PREV_NEAR_PERKS    = self.NEAR_PERKS
        self.PREV_NEAR_PLAYERS  = self.NEAR_PLAYERS
        self.PREV_NEAR_CHOPPERS = self.NEAR_CHOPPERS
        self.PREV_NEAR_BOMBS    = self.NEAR_BOMBS
        self.PREV_NEAR_MOVES    = self.NEAR_MOVES

        self.NEAR_PERKS    = []
        self.NEAR_PLAYERS  = []
        self.NEAR_CHOPPERS = []
        self.NEAR_BOMBS    = []
        self.NEAR_MOVES    = []

    def env_found_perk(self, x, y, t):
        self.NEAR_PERKS.append( (x,y,t) )

    def env_found_player(self, x, y, t):
        self.NEAR_PLAYERS.append( (x,y,t) )

    def env_found_chopper(self, x, y, t):
        self.NEAR_CHOPPERS.append( (x,y,t) )

    def env_found_bomb(self, x, y, t):
        self.NEAR_BOMBS.append( (x,y,t) )

    def env_found_move(self, dir, t):
        self.NEAR_MOVES.append( (dir,t) )

    def event_perk_blast(self):
        self.BOMB_POWER += CONFIG["perkBombBlastRadiusInc"]
        self.PERK_BLAST_TIMER += CONFIG["timeoutBombBlastRadiusInc"]

    def event_perk_bomb_counts(self):
        self.BOMBS_COUNT = CONFIG["bombsCount"] + CONFIG["perkBombCountInc"]
        self.PERK_BOMB_COUNTS_TIMER = CONFIG["timeoutBombCountInc"]

    def event_perk_immune(self):
        self.PERK_IMMUNE_TIMER = CONFIG["timeoutBombImmune"]

    def event_perk_rc(self):
        self.PERK_RC_TIMES = CONFIG["remoteControlCount"]

    def event_perk_throw(self):
        self.PERK_POISON_THROWER_TIMER = CONFIG["perkPoisonThrower"]

    def event_perk_explode(self):
        self.PERK_POTION_EXPLODER_TIMER = CONFIG["perkPoisonExploder"]

    def tick(self):
        if self.PERK_BLAST_TIMER>0:
            self.PERK_BLAST_TIMER-=1
            if self.PERK_BLAST_TIMER==0:
               self.BOMB_POWER = CONFIG["bombPower"]

        if self.PERK_BOMB_COUNTS_TIMER>0:
            self.PERK_BOMB_COUNTS_TIMER-=1
            if self.PERK_BOMB_COUNTS_TIMER==0:
                self.BOMBS_COUNT = CONFIG["bombsCount"]

        if self.PERK_IMMUNE_TIMER>0:
            self.PERK_IMMUNE_TIMER-=1
            if self.PERK_IMMUNE_TIMER==0:
                pass

        if self.PERK_POISON_THROWER_TIMER>0:
            self.PERK_POISON_THROWER_TIMER-=1
            if self.PERK_POISON_THROWER_TIMER==0:
                pass

        if self.PERK_POTION_EXPLODER_TIMER>0:
            self.PERK_POTION_EXPLODER_TIMER-=1
            if self.PERK_POTION_EXPLODER_TIMER==0:
                pass

    def get_current_blast_size(self):
        return self.BOMB_POWER

    def has_remote_perk(self):
        if self.PERK_RC_TIMES>0:
            LOGD("PLAYER {} has RC PERK".format(self.ID))
        return self.PERK_RC_TIMES>0

    def has_explode_perk(self):
        if self.PERK_POTION_EXPLODER_TIMER>0:
            LOGD("PLAYER {} has EXPLODE PERK".format(self.ID))
        return self.PERK_POTION_EXPLODER_TIMER>0

    def has_throw_perk(self):
        if self.PERK_POISON_THROWER_TIMER>0:
            LOGD("PLAYER {} has THROW PERK".format(self.ID))
        return self.PERK_POISON_THROWER_TIMER>0

    def event_new_bomb(self, bomb):
        if bomb.bomb_type == BOMBTYPE_REMOTE:
            if self.PERK_RC_TIMES>0:
                self.PERK_RC_TIMES-=1
            else:
                BREAK

    def event_new_rc_bomb(self, bomb):
        assert(bomb.bomb_type == BOMBTYPE_REMOTE)
        if self.PERK_RC_TIMES>0:
            self.PERK_RC_TIMES-=1
        else:
            LOGD("BOMB switched TO REMOTE") 
            #due to we not sure - how much rc times left - just ignore. Usually if join in the middle of game
            pass


    def x(self):
        return self._X

    def y(self):
        return self._Y
    
    def update_my_bombs(self, mybombs):
        self._my_bombs_ids = [b.ID for b in mybombs]
        #count my bombs
        self._my_rc_bomb_id = None
        for b in mybombs:
            if b.bomb_type==BOMBTYPE_REMOTE:
                self._my_rc_bomb_id=b.ID

    def has_free_bombs(self):
        max_bombs = self.BOMBS_COUNT
        my_bombs_cnt = len(self._my_bombs_ids)
        return my_bombs_cnt<max_bombs

    def est_try_drop_bomb(self,x,y, state):
        if self._my_rc_bomb_id!=None:
            LOGD("EST: activate remote bomb {}".format(self._my_rc_bomb_id))
            rc_bomb=state.BOMBS.get(self._my_rc_bomb_id, None)
            if rc_bomb!=None:
                rc_bomb.timer=1 #will be destroyed on tick
            self._my_rc_bomb_id=None
            return
        if not self.has_free_bombs():
            LOGD("EST: no bombs to drop")
            return
        check_bomb = state.board_get_bomb_at(x, y)
        if check_bomb!=None:
            LOGD("EST: no drop - ({},{}) already has bomb {}".format(x,y,check_bomb.ID)) 
            return
        nb = state.new_bomb( x, y, self.ID, self.get_current_blast_size(), 5-1, (BOMBTYPE_TIMER, BOMBTYPE_REMOTE )[ self.has_remote_perk()] )
        self.event_new_bomb(nb)

    def est_take_perk(self,x,y,state):
        #check for radius
        if state.BOARD[y][x]==EL_BOMB_BLAST_RADIUS_INCREASE:
            self.event_perk_blast()
        if state.BOARD[y][x]==EL_BOMB_IMMUNE:
            self.event_perk_immune()
        if state.BOARD[y][x]==EL_BOMB_REMOTE_CONTROL:
            self.event_perk_rc()
        if state.BOARD[y][x]==EL_BOMB_COUNT_INCREASE:
            self.event_perk_bomb_counts()
        if state.BOARD[y][x]==EL_POISON_THROWER:
            self.event_perk_throw()
        if state.BOARD[y][x]==EL_POTION_EXPLODER:
            self.event_perk_explode()

    def est_try_move(self, state):
        dir = self._est_next_move

        ## simple AI
        if self.ID!=0: 
            if self.has_free_bombs():
                self.est_try_drop_bomb(self.x(), self.y(), state)
            return

        if self._est_next_move==None:
            return

        dx, dy = MOVES[dir]
        ox, oy = self._X, self._Y
        nx, ny = ox+dx, oy+dy

        if self._est_act_pre:
            self.est_try_drop_bomb(ox,oy,state)

        #moving to new cell - all barriers
        if (dx!=0 or dy!=0) and state.BOARD[ny][nx] not in ELS_BLOCKED: 
            self.event_moved(nx, ny)
            #perks
            self.est_take_perk(nx,ny,state)
        #stay
        elif dx==0 and dy==0:
            pass
        #blocked, just stay
        else:
            LOGD("EST: player {} can't move to ({},{})".format(self.ID, nx,ny))

        if self._est_act_post:
            self.est_try_drop_bomb(nx,ny,state)

        #####################
        self._est_next_move = None
        self._est_act_pre   = None
        self._est_act_post  = None




BOMBTYPE_UNKNOWN = 0
BOMBTYPE_TIMER   = 1
BOMBTYPE_REMOTE  = 2

class Bomb:
    ID = 0
    
    blast = None
    timer = None
    bomb_type = False
    owner = None
    rc_timer  = None

    X = 0
    Y = 0

    _processed = False
    _is_alive = False

    def __init__(self, id, owner=None, blast=None, timer=None, btype=False):
        self.ID = id
        self.blast = blast
        self.timer = timer
        self.bomb_type = btype
        self.owner = owner
        self._is_alive = True
        self.rc_timer = 0

    def dump(self):
        LOGD("===== BOMB {} =========".format(self.ID))
        LOGD(" X,Y = {}, {}".format(self.X, self.Y))
        LOGD(" blast = {}".format(self.blast))
        LOGD(" timer = {}".format(self.timer))
        LOGD(" bomb_type = {}".format(self.bomb_type))
        LOGD(" owner = {}".format(self.owner))
        LOGD("=========================\n")


    def dump_as_code(self):
        LOGD("  ({}, {}) : ({}, {}, {}, {}, {}),".format(self.X, self.Y, self.ID, self.blast, self.timer, self.bomb_type, self.owner) )

    def tick(self):
        if self.bomb_type!=BOMBTYPE_REMOTE and self.timer>0:
            self.timer -= 1
        if self.timer==0: # and self.bomb_type==BOMBTYPE_TIMER
            LOGD("BOMB {} is AUTO-detonating!!!".format(self.ID))
            self._is_alive = False
        if self.bomb_type==BOMBTYPE_REMOTE and self.timer>0:
            self.rc_timer+=1

    def trigger(self):
        if self.timer>0 and self.bomb_type==BOMBTYPE_REMOTE:
            self.timer = 0
            LOGD("BOMB {} TRIGGERRING".format(self.ID))

    def event_bomb_updated_timer(self, newtimer, gstate):
        if newtimer==5 or self.timer+1==newtimer: # RC - count freezed
            if self.bomb_type!=BOMBTYPE_REMOTE:
                LOGD("BOMB {} TYPE now is : RC".format(self.ID))
                self.bomb_type=BOMBTYPE_REMOTE
                self.timer=5
                p=gstate.players().get( self.owner, None)
                if p!=None:
                    p.event_new_rc_bomb(self)

        else: # count go - detect RC
            if self.timer!=newtimer:
                LOGD("BOMB {} TYPE now is : TIMER_{}".format(self.ID, newtimer))
                self.bomb_type=BOMBTYPE_TIMER
                self.timer=newtimer

    def est_boom(self,state):
        blast_size = self.blast
        x = self.X
        y = self.Y
        assert(self.timer==0)
        state.board_object_replace(x, y, state.BOARD[y][x], EL_BOOM)
        for dx, dy in MOVES[:4]:
            for w in range(1, blast_size + 1): # blastsize+bomb
                nx = x+dx*w
                ny = y+dy*w

                if not state.is_onboard(nx,ny):
                    break

                t=state.BOARD[ny][nx]
                if t == EL_WALL:
                    break
                elif t == EL_DESTROY_WALL:
                    state.board_object_replace(nx, ny, state.BOARD[ny][nx], EL_BOOM)
                    break
                elif t in [EL_OTHER_BOMB_BOMBERMAN, EL_BOMB_BOMBERMAN, EL_OTHER_BOMBERMAN, EL_BOMBERMAN]:
                    state.board_object_replace(nx, ny, state.BOARD[ny][nx], EL_BOOM)
                    for p in state.PLAYERS.values():
                        if p.x()==nx and p.y()==ny:
                            LOGD("EST: BOOM Player {} at ({},{})".format(p.ID, p.x(), p.y()))
                            p.set_alive(False)
                    break
                elif t in [ EL_BOMB_TIMER_5, EL_BOMB_TIMER_4, EL_BOMB_TIMER_3, EL_BOMB_TIMER_2, EL_BOMB_TIMER_1]:
                    pass
                elif t == EL_NONE:
                    state.board_object_replace(nx, ny, state.BOARD[ny][nx], EL_BOOM)
                else:
                    state.board_object_replace(nx, ny, state.BOARD[ny][nx], EL_BOOM)
        

class Chopper:
    ID = 0
    X  = 0
    Y  = 0
    PX = 0
    PY = 0
    type = None
    _is_alive = False #on board, not type Dead Meat
    _processed = False

    NEAR_MOVES    = []
    PREV_NEAR_MOVES    = []    

    def __init__(self, id, x=0, y=0, t=None):
        self.ID=id
        self.X=x
        self.Y=y
        self.type=t
        self._is_alive=True #

    def dump(self):
        LOGD("===== CHOPPER {} =========".format(self.ID))
        LOGD(" X,  Y  = {}, {}".format(self.X,  self.Y))
        LOGD(" PX, PY = {}, {}".format(self.PX, self.PY))
        LOGD(" type = {}".format(self.type))
        LOGD(" isAlive = {}".format(self._is_alive))
        LOGD("=========================\n")

    def dump_as_code(self):
        LOGD("  ({}, {}) : ({}, {}, {}, {}),".format(self.X, self.Y, self.PX, self.PY, self.type, self._is_alive) )


    def set_alive(self, state):
        if self._is_alive!=state:
            LOGD("CHOPPER {} ".format(self.ID) + ("DIED","RESPAWNED")[state])
            self._is_alive=state

    def set_type(self, t):
        if self.type!=t:
            LOGD("CHOPPER becomes {} ".format(self.ID) + ("MEAT","DEAD_MEAT")[t==EL_DEAD_MEAT_CHOPPER])
            self.type=t

    def event_moved(self, x, y): #pos updated - i.e. next round - update pwned perks!
        self.PX = self.X
        self.PY = self.Y
        self.X  = x
        self.Y  = y
        if x!= self.PX and y!=self.PY:
            LOGD("CHOPPER {} MOVED to: {},{}".format(self.ID,x,y))

    def reset_processed(self):
        self._processed=False

    def set_processed(self):
        self._processed=True

    def env_reset_stats(self):
        self.PREV_NEAR_MOVES    = self.NEAR_MOVES
        self.NEAR_MOVES    = []

    def env_found_move(self, dir, t):
        self.NEAR_MOVES.append( (dir,t) )


    def get_last_move(self):
        return dx2dir( self.PX, self.PY, self.X, self.Y )

    def est_try_move(self, dir, state):
        if dir==4:
            return False

        dx, dy = MOVES[dir]
        ox, oy = self.X, self.Y
        nx, ny = ox+dx, oy+dy

        BLOCKS = [EL_WALL] if self.type==EL_DEAD_MEAT_CHOPPER else ELS_CHOPPER_NO_MOVE

        #moving to new cell - all barriers
        if (dx!=0 or dy!=0) and state.BOARD[ny][nx] not in BLOCKS: 
            self.event_moved(nx, ny)
            return True
        elif dx==0 and dy==0:
            pass
        #blocked, just stay
        else:
            LOGD("EST: chopper {} can't move to ({},{})".format(self.ID, nx,ny))
        return False

    def check_if_can_move(self, dir, state):
        if dir==4:
            return False

        dx, dy = MOVES[dir]
        ox, oy = self.X, self.Y
        nx, ny = ox+dx, oy+dy

        BLOCKS = [EL_WALL] if self.type==EL_DEAD_MEAT_CHOPPER else ELS_CHOPPER_NO_MOVE

        #moving to new cell - all barriers
        if (dx!=0 or dy!=0) and state.BOARD[ny][nx] not in BLOCKS: 
            return True
        elif dx==0 and dy==0:
            pass
        #blocked, just stay
        else:
            LOGD("CHECK: chopper {} can't move to ({},{})".format(self.ID, nx,ny))
        return False


class GameState:

    BOARD_SZ = None

    ME      = Player(0)
    OBJECTS =  None
    PLAYERS  = { ME.ID : ME }
    BOMBS    = {}
    CHOPPERS = {}

    
    BOARD = None
    BOARD_PREV = None

    DANGERS   = None
    DANGERS_t = None

    _players_id_cnt = 1
    _bombs_id_cnt = 1
    _chopper_id_cnt = 1
    _game_time = 0
    
    _dead_meat_choppers = None
    _meat_choppers = None


    HISTORY_DIR = ""
    HISTORY_FNAME = None
    HISTORY_LOGGER = None
    counter = 0 #just to track in logs


    def __init__(self, qtgame, reset_history=True):
        self.qtgame = qtgame
        self.init_from_config()
        self.HISTORY_DIR = os.path.abspath("history")
        if reset_history:
            try:
                shutil.rmtree(self.HISTORY_DIR)
            except:
                pass
            if REPLAY_RECORD_ON:
                os.mkdir(self.HISTORY_DIR)
                self.counter = REPLAY_RECORD_START        

    def clone(self):
        cloned=GameState(self.qtgame, reset_history=False)
        cloned.OBJECTS   =deepcopy(self.OBJECTS)
        cloned.PLAYERS   =deepcopy(self.PLAYERS)
        cloned.BOMBS     =deepcopy(self.BOMBS)
        cloned.CHOPPERS  =deepcopy(self.CHOPPERS)
        cloned.BOARD     =deepcopy(self.BOARD)
        cloned.BOARD_PREV=deepcopy(self.BOARD_PREV)
        cloned.DANGERS   =deepcopy(self.DANGERS)
        cloned.DANGERS_t =deepcopy(self.DANGERS_t)
        
        cloned.ME = cloned.PLAYERS[0]
        cloned.BOARD_SZ = self.BOARD_SZ
        cloned._players_id_cnt      = self._players_id_cnt
        cloned._chopper_id_cnt      = self._chopper_id_cnt
        cloned._bombs_id_cnt        = self._bombs_id_cnt
        cloned._game_time           = self._game_time
        cloned._dead_meat_choppers  = deepcopy(self._dead_meat_choppers)
        cloned._meat_choppers       = deepcopy(self._meat_choppers)

        return cloned

    def is_onboard(self,x,y):
        return x>=1 and x<self.BOARD_SZ-1 and y>=1 and y<self.BOARD_SZ-1 #no need check edges

    def init_from_config(self):
        config_init() #due static initialization need sure that config read
        if self.BOARD_SZ==None:
            self.BOARD_SZ = CONFIG["boardSize"]
        if self.BOARD==None:
            self.BOARD = [ [EL_NONE]*self.BOARD_SZ for _ in range(self.BOARD_SZ) ]
        if self.DANGERS==None:
            self.DANGERS = [ [EL_NONE]*self.BOARD_SZ for _ in range(self.BOARD_SZ) ]
        if self.DANGERS_t==None:
            self.DANGERS_t = [ [0]*self.BOARD_SZ for _ in range(self.BOARD_SZ) ]

    def me(self):
        return self.ME

    def players(self):
        return self.PLAYERS

    def bombs(self):
        return self.BOMBS

    def choppers(self):
        return self.CHOPPERS

    def my_bombs(self):
        return [ self.BOMBS[bid] for bid in self.me()._my_bombs_ids ]

    def my_rc_bomb(self):
        if self.me()._my_rc_bomb_id!=None:
            return self.BOMBS[self.me()._my_rc_bomb_id]
        return None

    def me_safe_to_drop_bomb(self):
        mx , my = self.ME.x(), self.ME.y()
        return not self.if_on_my_bombs_fireline(mx, my)

    def new_player(self):
        pid = self._players_id_cnt
        self._players_id_cnt+=1
        p = Player(pid)
        self.PLAYERS[p.ID]=p
        return p

    def new_bomb(self, x, y, owner, blast, btimer, btype):
        bid = self._bombs_id_cnt
        self._bombs_id_cnt+=1
        if btype==BOMBTYPE_REMOTE:
            timer=5
        b = Bomb(bid, owner, blast, btimer, btype)
        b.X = x
        b.Y = y
        self.BOMBS[b.ID]=b
        LOGD("BOMB NEW: id={} ({},{}) owner={} blast={} btimer={} btype={}".format(b.ID, b.X, b.Y, b.owner, b.blast, b.timer, b.bomb_type))
        return b

    def new_chopper(self, x, y, t):
        cid = self._chopper_id_cnt
        self._chopper_id_cnt+=1
        c = Chopper(cid, x, y, t)
        self.CHOPPERS[c.ID]=c
        LOGD("CHOPPER NEW: id={} ({},{}) type={}".format(c.ID, c.X, c.Y, c.type))
        return c

    def event_player_killed(self, pid): #pos updated - i.e. next round - update pwned perks!
        if pid!=0:
            self.PLAYERS.pop(pid, None)
            LOGD("PLAYER {} DISMISSED".format(pid))
        else:
            self.ME.set_alive(False)

    def event_chopper_killed(self, pid): #pos updated - i.e. next round - update pwned perks!
        self.CHOPPERS.pop(pid, None)
        LOGD("CHOPPER {} DISMISSED".format(pid))

    def find_objects(self, board, t):
        res = []
        for x in range(self.BOARD_SZ):
            for y in range(self.BOARD_SZ):
                if board[y][x] in t:
                    res.append( (x,y) )

    def find_all_objects(self, board):
        res = defaultdict(list)
        for x in range(self.BOARD_SZ):
            for y in range(self.BOARD_SZ):
                t = board[y][x]
                res[t].append( (x,y) )
        return res

    def players_reset_processed_status(self):
        for i,p in self.PLAYERS.items():
            p.reset_processed()

    def choppers_reset_processed_status(self):
        for i,p in self.CHOPPERS.items():
            p.reset_processed()

    def B_remove_pid(self, B, pid):
        for x in range(self.BOARD_SZ): #speedup: as variant remeber cells
            for y in range(self.BOARD_SZ):
                if pid in B[y][x]:
                    B[y][x].remove(pid)

    # BOARD is prev state
    # env stats is prev yet
    def update_players_from(self, objects):
        players_new = []
        players_new += [ [x,y,EL_OTHER_BOMBERMAN,     None, False] for x,y in objects.get(EL_OTHER_BOMBERMAN, []) ]
        players_new += [ [x,y,EL_OTHER_BOMB_BOMBERMAN,None, False] for x,y in objects.get(EL_OTHER_BOMB_BOMBERMAN, []) ]
        players_new += [ [x,y,EL_OTHER_DEAD_BOMBERMAN,None, False] for x,y in objects.get(EL_OTHER_DEAD_BOMBERMAN, []) ]
        
       
        B = [ [ [] for _ in range(self.BOARD_SZ)] for _ in range(self.BOARD_SZ)]
        #enum olds
        for pid, p in self.PLAYERS.items():
            if pid==0: continue 
            ox, oy = p.x(), p.y()
            for d, t in p.NEAR_MOVES:
                dx, dy = MOVES[d]
                nx, ny = ox+dx, oy+dy
                if not self.is_onboard(nx, ny):
                    continue
                B[ny][nx].append(p.ID)
        #
        flag = 0
        while flag<2:
            flag+=1
            for i in range(len(players_new)):
                if players_new[i][4]:
                    continue
                px = players_new[i][0]
                py = players_new[i][1]
                pt = players_new[i][2]
                if len(B[py][px])==0: #surely new player
                    np = self.new_player()
                    np.set_alive( False if pt==EL_OTHER_DEAD_BOMBERMAN else True)
                    np.event_moved( px, py )
                    np.set_processed()
                    players_new[i][3] = np.ID
                    players_new[i][4] = True
                    flag=0
                elif len(B[py][px])==1: #surely moved
                    pid = B[py][px][0]
                    np = self.PLAYERS[pid]
                    np.set_alive( False if pt==EL_OTHER_DEAD_BOMBERMAN else True)
                    np.event_moved( px, py )
                    np.set_processed()
                    players_new[i][3] = pid
                    players_new[i][4] = True
                    #update B
                    self.B_remove_pid(B, pid)
                    flag=0
        
        #most ineteresting - we have few old and few new, not 
        #non-processed new
        rest = [ ]
        for i,p in enumerate(players_new):
            if not p[4]: #not yet assigned
                rest.append( (p[3], B[p[1]][p[0]]) )

        for i,p in self.PLAYERS.items():
            if i==0:
                continue #me checked not here
            if not p._processed: 
                if len(rest)==0:
                    p.set_alive(False)
                    LOGD("PLAYER {} DISAPPEARED".format(p.ID))
                    self.B_remove_pid(B, p.ID)
                else:
                    pass

    def history_start(self):
        if REPLAY_RECORD_ON:
            fname = os.path.join(self.HISTORY_DIR, "{:05}.txt".format(self.counter))
            self.HISTORY_FNAME = fname
            self.HISTORY_LOGGER = LoggerFile(fname)
        else:
            self.HISTORY_LOGGER = LoggerFile()

    def history_close(self):
        self.HISTORY_FNAME = None
        self.HISTORY_LOGGER = None

    def history_write(self, s):
        if self.HISTORY_LOGGER:
            self.HISTORY_LOGGER.log(s)

    def history_store_state(self, title):
        if not self.HISTORY_LOGGER:
            return
        self.history_write("\n" + title)
        #self.history_write("TOBJ_IDXCNT: {}".format(TOBJ_IDXCNT))

        #self.BOARD.store_state(self.HISTORY_LOGGER)
        logger = self.HISTORY_LOGGER
        logger.log("\nME:")
        logger.log_object(self.ME)

        logger.log("\nPLAYERS:")
        self.players_store_state(logger)

        logger.log("\nCHOPPERS:")
        self.choppers_store_state(logger)

        logger.log("\nBOMBS:")
        self.bombs_store_state(logger)

        #logger.log("\nPERKS:")
        #self.PERKS.store_state(logger)

    def history_print_input(self):
        if not self.HISTORY_LOGGER:
            return
        self.BOARD.store_print_input(self.HISTORY_LOGGER)




    def update_choppers_from(self, objects):

        choppers_new = []
        choppers_new += [ [x,y,EL_MEAT_CHOPPER,     None, False] for x,y in objects.get(EL_MEAT_CHOPPER, []) ]
        choppers_new += [ [x,y,EL_DEAD_MEAT_CHOPPER,None, False] for x,y in objects.get(EL_DEAD_MEAT_CHOPPER, []) ]

        B = [ [ [] for _ in range(self.BOARD_SZ)] for _ in range(self.BOARD_SZ)]
        #enum olds
        for pid, p in self.CHOPPERS.items():
            ox, oy = p.X, p.Y
            for d, t in p.NEAR_MOVES:
                dx, dy = MOVES[d]
                nx, ny = ox+dx, oy+dy
                if not self.is_onboard(nx, ny):
                    continue
                B[ny][nx].append(p.ID)
        #
        flag = 0
        while flag<2:
            flag+=1
            for i in range(len(choppers_new)):
                if choppers_new[i][4]:
                    continue
                px = choppers_new[i][0]
                py = choppers_new[i][1]
                pt = choppers_new[i][2]
                if len(B[py][px])==0: #surely new chopper
                    nc = self.new_chopper(px, py, pt)
                    #nc.set_alive( False if pt==EL_DEAD_MEAT_CHOPPER else True)                    
                    nc.event_moved( px, py )
                    nc.set_processed()
                    choppers_new[i][3] = nc.ID
                    choppers_new[i][4] = True
                    flag=0
                elif len(B[py][px])==1: #surely moved
                    cid = B[py][px][0]
                    nc = self.CHOPPERS[cid]
                    #nc.set_alive( False if pt==EL_DEAD_MEAT_CHOPPER else True)                    
                    nc.set_type(pt)
                    nc.event_moved( px, py )
                    nc.set_processed()
                    choppers_new[i][3] = cid
                    choppers_new[i][4] = True
                    #update B
                    self.B_remove_pid(B, cid)
                    flag=0
        
        #most ineteresting - we have few old and few new, not 
        #non-processed new
        rest = [ ]
        for i,p in enumerate(choppers_new):
            if not p[4]: #not yet assigned
                rest.append( (p[3], B[p[1]][p[0]]) )

        for i,p in self.CHOPPERS.items():
            if not p._processed: 
                if len(rest)==0:
                    p.set_alive(False)
                    LOGD("CHOPPER {} DISAPPEARED".format(p.ID))
                    self.B_remove_pid(B, p.ID)
                else:
                    pass



    def board_get_bomb_at(self, x, y):
        for i,b in self.BOMBS.items():
            if b.X==x and b.Y==y:
                return b
        return None

    def board_get_player_at(self, x, y):
        for i,b in self.PLAYERS.items():
            if b.x()==x and b.y()==y:
                return b
        return None

    def board_get_player_at_past(self, x, y):
        for i,b in self.PLAYERS.items():
            if b._PX==x and b._PY==y:
                return b
        return None

    def objects_get(self, objects, targets):
        res_xy = []
        res_t  = []
        for t in targets:
            r = objects.get(t, None)
            if r!=None: # r == lsi
                res_xy += list(r)
                res_t += [t]*len(r)
        return (res_xy, res_t)

    # BOARD   prev state, 
    # env stats is prev yet
    # PLAYERS new  state
    def update_bombs_from(self, objects):
        all_bombs_xy, _    = self.objects_get(objects, ELS_BOMBS)
        all_choppers_xy, _ = self.objects_get(objects, [EL_MEAT_CHOPPER, EL_DEAD_MEAT_CHOPPER] )
        #remove detonated 
        bombs2remove = []
        for i,b in self.BOMBS.items():            
            if (b.X, b.Y) not in all_bombs_xy:
                if b.timer==0:
                    bombs2remove.append( i )
                elif (b.X, b.Y) in all_choppers_xy:
                    LOGD("BOMB under CHOPPER?")
                else:
                    #destroyed somehow else
                    bombs2remove.append( i )
        for i in bombs2remove:
            #detonated, destroyed etc
            self.BOMBS.pop(i, None)

        #
        objects_bombermans_xy, _ = self.objects_get(objects, [EL_OTHER_BOMB_BOMBERMAN, EL_BOMB_BOMBERMAN])
        for i, (x,y) in enumerate(objects_bombermans_xy):
            b = self.board_get_bomb_at(x, y)
            if b==None: #new bomb
                p = self.board_get_player_at(x,y)
                if p!=None: #found player
                    nb = self.new_bomb( x, y, p.ID, p.get_current_blast_size(), 5-1, (BOMBTYPE_TIMER, BOMBTYPE_REMOTE )[ p.has_remote_perk()] )
                    p.event_new_bomb(nb)
                else:#unknown bomb
                    nb = self.new_bomb( x, y, -1, CONFIG["bombPower"], 5-1, BOMBTYPE_UNKNOWN )

        objects_bombs_xy, objects_bombs_type = self.objects_get(objects, [EL_BOMB_TIMER_1, EL_BOMB_TIMER_2, EL_BOMB_TIMER_3, EL_BOMB_TIMER_4, EL_BOMB_TIMER_5])
        for i,(x,y) in enumerate(objects_bombs_xy):
            b = self.board_get_bomb_at(x, y)
            brdtimer = ord( objects_bombs_type[i] )-ord(EL_BOMB_TIMER_1)+1
            if b==None: #new bomb
                #try find player
                p = self.board_get_player_at_past(x,y)
                if p!=None: #found player
                    nb = self.new_bomb(x, y, p.ID, p.get_current_blast_size(), brdtimer, (BOMBTYPE_TIMER, BOMBTYPE_REMOTE )[ p.has_remote_perk()] )
                    p.event_new_bomb(nb)
                else:#unknown bomb
                    nb = self.new_bomb( x, y, -1, CONFIG["bombPower"], brdtimer, BOMBTYPE_UNKNOWN )
            else: #existing bomb 
                b.event_bomb_updated_timer(brdtimer, self)
        
        for p in self.PLAYERS.values():
            bombs = [ b for b in self.BOMBS.values() if b.owner==p.ID]
            p.update_my_bombs(bombs)




    def remove_dead_players(self):
        dead = list( id for id,p in self.PLAYERS.items() if not p._is_alive)
        for idx in dead:
            self.event_player_killed(idx)

    def remove_dead_choppers(self):
        dead = list( id for id,p in self.CHOPPERS.items() if not p._is_alive)
        for idx in dead:
            self.event_chopper_killed(idx)

    def reset_game(self):
        self.ME = Player(0)
        self.PLAYERS = { self.ME.ID : self.ME }
        self.BOARD = None
        self.BOARD_PREV = None
        self.DANGERS = None
        self.DANGERS_t = None
        self.CHOPPERS={}
        self._game_time = 0
        self._players_id_cnt = 1
        self._bombs_id_cnt = 1
        self._chopper_id_cnt = 1        
        self._my_bombs_cnt = 0
        self._my_rc_bomb = 0
        self._dead_meat_choppers = 0
        self._meat_choppers = 0


    def dmap_put_bombs(self):
        for i,bomb in self.bombs().items():
            blast_size = bomb.blast
            x = bomb.X
            y = bomb.Y
            t = bomb.timer
            if bomb.bomb_type == BOMBTYPE_REMOTE and bomb.owner!=0:
                t=1
            for dx, dy in MOVES[:4]:
                for w in range(blast_size + 1): # blastsize+bomb
                    nx = x+dx*w
                    ny = y+dy*w
                    if not self.is_onboard(nx,ny):
                        continue
                    if (dx!=0 or dy!=0) and w>0 and self.BOARD[ny][nx] in ELS_BLAST_BLOCKINGS:
                        break
                    f = chr(t+ord(EL_BOMB_BLAST_1)-1)
                    if self.DANGERS[ny][nx] in ELS_BLASTS:
                        f=min(f, self.DANGERS[ny][nx])
                    self.DANGERS[ny][nx]=f
                    self.DANGERS_t[ny][nx]=max(DANGERS_TYPE_BLAST, self.DANGERS_t[ny][nx])
            #print_board(bdangers, True)

    def dmap_put_chopper(self, x, y, target, dist, dw, allowed_cells):
        V = [ [0]*self.BOARD_SZ for _ in range(self.BOARD_SZ)]
        M = deque()
        M.append( (x,y,0) )

        self.DANGERS[y][x] = EL_BOMB_BLAST_1
        while M:
            x, y, w  = M.popleft()
            if w>dist:
                break

            if V[y][x]==0: #not checked
                V[y][x] = 1

                if w!=0 and self.BOARD[y][x] in allowed_cells:
                    nw = w
                    if nw>dw: nw-=dw
                    bl = min(nw, 5-1 ) # BLAST 5 is the last
                    f = chr(ord(EL_BOMB_BLAST_1) + bl - 1 ) #BLAST1=5
                    if self.DANGERS[y][x] in ELS_BLASTS:
                        f=min(f, self.DANGERS[y][x])
                    self.DANGERS[y][x]=f
                    if target==EL_MEAT_CHOPPER:
                        self.DANGERS_t[y][x]=max(DANGERS_TYPE_CHOPPER     , self.DANGERS_t[y][x])
                    if target==EL_DEAD_MEAT_CHOPPER:
                        self.DANGERS_t[y][x]=max(DANGERS_TYPE_DEAD_CHOPPER, self.DANGERS_t[y][x])


            for i, (dx,dy) in enumerate(MOVES[:4]): 
                nx, ny, nw = x+dx, y+dy, w+1
                if not self.is_onboard(nx,ny): #outboard
                    continue
                if V[ny][nx]!=0:          #already checked
                    continue 
                if ( self.BOARD[ny][nx] not in allowed_cells):
                    continue
                M.append( (nx, ny, nw) )    

    def dmap_put_choppers(self):
        tlist = self.OBJECTS.get(EL_MEAT_CHOPPER, None) #board_get_objects(borig, [EL_MEAT_CHOPPER])
        if tlist!=None:
            for x,y in tlist:
                self.dmap_put_chopper(x,y,EL_MEAT_CHOPPER, 4, 0, ELS_NOT_DANGER2MOVE+[EL_OTHER_BOMBERMAN, EL_OTHER_BOMB_BOMBERMAN, EL_BOMB_BOMBERMAN])
        tlist = self.OBJECTS.get(EL_DEAD_MEAT_CHOPPER, None)
        if tlist!=None:
            for x,y in tlist:
                self.dmap_put_chopper(x,y,EL_DEAD_MEAT_CHOPPER, 5, 1, ELS_NOT_DANGER2MOVE+[EL_OTHER_BOMBERMAN, EL_OTHER_BOMB_BOMBERMAN, EL_BOMB_BOMBERMAN])
            

    def fill_dangers_map(self):
        self.DANGERS   = [ [EL_NONE]*self.BOARD_SZ for _ in range(self.BOARD_SZ) ]
        self.DANGERS_t = [ [0]*self.BOARD_SZ for _ in range(self.BOARD_SZ) ]
        self.dmap_put_bombs()
        self.dmap_put_choppers()


    def update_board_from(self, board_string):
        #remove dead first
        self.players_reset_processed_status()
        self.remove_dead_players()
        self.choppers_reset_processed_status()
        self.remove_dead_choppers()

        ###
        LOGD("BOARD STRING LEN = {}".format(len(board_string)))
        board_string=board_string.replace('\n', '')
        SZ    = int(sqrt(len(board_string)))
        if SZ!=23: #hardcoded
            LOGD("Wrong input board size!!!")
            return GAMERES_WRONG_INPUT
        board_input = list( list(c for c in board_string[r*SZ:((r+1)*SZ)]) for r in range(SZ) )
        
        #print_board(board_input, True, DFILE)

        self.OBJECTS=objects_new = self.find_all_objects(board_input)

        objects_present = set(k for k in objects_new.keys())
        game_off = set([EL_WALL, EL_NONE, EL_DEAD_BOMBERMAN, EL_OTHER_DEAD_BOMBERMAN])
        if objects_present.issubset(game_off):
            #init new game
            self.reset_game()
            return GAMERES_INACTIVE
        self._game_time+=1

        me =  objects_new.get(EL_DEAD_BOMBERMAN, None )

        
        ## Identify/update me
        if me!=None : # I dead :(
            self.ME.set_alive(False)
        else:
            me =    objects_new.get(EL_BOMB_BOMBERMAN, []) + objects_new.get(EL_BOMBERMAN, [])
            if len(me)==0:
                LOGD("Can't find myself - I killed!!!!!")
                return GAMERES_OVER
            elif len(me)>1:
                LOGD("Too much mee - something wrong!!!")
                BREAK
            else:
                x,y = me[0]
                self.ME.set_alive(True)
                self.ME.event_moved(x,y)
                self.ME.set_processed()
        
        ## Identify/update rest of players
        self.update_players_from(objects_new)
        
        ## Identify/update bombs
        self.update_bombs_from(objects_new)

        ## Identify/update bombs
        self.update_choppers_from(objects_new)

        ##pre find objects
        self._dead_meat_choppers = objects_new.get(EL_DEAD_MEAT_CHOPPER, [])
        self._meat_choppers = objects_new.get(EL_MEAT_CHOPPER, [])

        ##
        self.BOARD_PREV = self.BOARD
        self.BOARD = board_input
        
        for p in self.PLAYERS.values():
            self.test_player_env(p) #update player environment

        self.players_get_perks()

        for p in self.CHOPPERS.values():
            self.test_chopper_env(p) #update player environment

        ########## PRAPARE DANGERS MAP ########################
        self.fill_dangers_map()

        ## DUMP DANGERS MAP
        if DEBUG_VERBOSE:
            print_board(self.DANGERS, True)

            ## DUMP PLAYERS
            for p in self.PLAYERS.values():
                p.dump()
            LOGD(" DEBUGPLAYERS = {")
            for p in self.PLAYERS.values():
                p.dump_as_code()
            LOGD(" }")
            
            ## DUMP BOMBS
            for b in self.BOMBS.values():
                b.dump()
            LOGD(" DEBUGBOMBS = {")
            for b in self.BOMBS.values():
                b.dump_as_code()
            LOGD(" }")


        return GAMERES_OK


    #check current player enviroment
    def test_player_env(self, player):
        BRD = self.BOARD
        px = player.x()
        py = player.y()
        player.env_reset_stats()
        for i, (dx,dy) in enumerate(MOVES):
            nx, ny = px+dx, py+dy
            if not self.is_onboard(nx, ny):
                continue
            t=BRD[ny][nx]
            if t in ELS_BOMBS:
                player.env_found_bomb( nx, ny, t )
            if t in EL_MEAT_CHOPPER:
                player.env_found_chopper( nx, ny, t )
            if t in [EL_OTHER_BOMBERMAN,EL_OTHER_BOMB_BOMBERMAN] and i!=4: #don't count hiself
                player.env_found_player( nx, ny, t )
            if t in ELS_PERKS:
                player.env_found_perk( nx, ny, t )
            if i==4 or t not in ELS_BLOCKED: #can stay at bomb
                player.env_found_move( i, t )
        #LOGD()
        
    #check chopper enviroment
    def test_chopper_env(self, chopper):
        BRD = self.BOARD
        px = chopper.X
        py = chopper.Y
        pt = chopper.type
        chopper.env_reset_stats()
        for i, (dx,dy) in enumerate(MOVES[:4]): #always moves, not stop
            nx, ny = px+dx, py+dy
            if not self.is_onboard(nx, ny):
                continue
            t=BRD[ny][nx]
            if pt==EL_DEAD_MEAT_CHOPPER:
                if t != EL_WALL: 
                    chopper.env_found_move( i, t )
            else:
                if t not in ELS_CHOPPER_NO_MOVE: 
                    chopper.env_found_move( i, t )
        
    def players_get_perks(self):
        for p in self.PLAYERS.values():
            px, py = p.x(), p.y()
            #check for radius
            if self.BOARD_PREV!=None:
                if self.BOARD_PREV[py][px]==EL_BOMB_BLAST_RADIUS_INCREASE:
                    p.event_perk_blast()
                if self.BOARD_PREV[py][px]==EL_BOMB_IMMUNE:
                    p.event_perk_immune()
                if self.BOARD_PREV[py][px]==EL_BOMB_REMOTE_CONTROL:
                    p.event_perk_rc()
                if self.BOARD_PREV[py][px]==EL_BOMB_COUNT_INCREASE:
                    p.event_perk_bomb_counts()
                if self.BOARD_PREV[py][px]==EL_POISON_THROWER:
                    p.event_perk_throw()
                if self.BOARD_PREV[py][px]==EL_POTION_EXPLODER:
                    p.event_perk_explode()


    def tact(self, cmd):
        #
        for i,p in self.PLAYERS.items():
            p.tick()

        act = "ACT" in cmd
        if act:
            my_rc = self.my_rc_bomb()
            if my_rc!=None:
                LOGD("PLAYER {} : DETONATE BOMB {}".format(self.me().ID, my_rc.ID))
                my_rc.trigger()
            else:
                LOGD("PLAYER {} : WILL DROP BOMB".format(self.me().ID))
            

        bombs2remove = []
        for i,b in self.BOMBS.items():
            b.tick()
            if not b._is_alive: 
                bombs2remove.append(i)
        for i in bombs2remove:
            self.BOMBS.pop(i, None)

    def me_dst2dead_meat_chopper(self):
        if self._dead_meat_choppers==None:
            return None
        #moves through walls!
        res = None
        mx = self.me().x()
        my = self.me().y()
        for cx, cy in self._dead_meat_choppers:
            d = abs(mx-cx) + abs(my-cy)
            if res==None or d<res:
                res=d
        return res

   
    def if_on_fireline(self, mx, my, bx, by, blast):
        for dx, dy in MOVES[:4]:
            for w in range( blast + 1):
                x = bx + dx*w
                y = by + dy*w
                if not self.is_onboard(x, y):
                    continue
                t=self.BOARD[y][x]
                if t in  [EL_WALL, EL_DESTROY_WALL]:
                    break
                if my==y and mx==x:
                    return True
        return False


    def if_on_any_fireline(self, x, y):
        for bomb in self.BOMBS.values():
            if self.if_on_fireline( x, y, bomb.X, bomb.Y, bomb.blast):
                return True
        return False

    def if_me_on_any_fireline(self):
        mx = self.me().x()
        my = self.me().y()
        return self.if_on_any_fireline(mx, my)

    def if_others_on_any_fireline(self):
        for player in self.PLAYERS.values():
            px = player.x()
            py = player.y()
            if self.if_on_any_fireline(px, py):
                return True
        return False

    def if_on_my_rc_fireline(self, px, py):
        my_rc = self.my_rc_bomb()
        if my_rc==None:
            return
        return self.if_on_fireline( px, py, my_rc.X, my_rc.Y, my_rc.blast)


    def if_on_my_bombs_fireline(self, px, py):
        for b in self.my_bombs():
            res=self.if_on_fireline( px, py, b.X, b.Y, b.blast)
            if res:
                return True
        return False

    def if_any_on_throw_fireline(self, mx, my):
        #check if any hero on throw fireline
        for player in self.PLAYERS.values():
            px = player.x()
            py = player.y()
            if self.if_on_fireline(mx, my, px, py, 5):
                return dx2dir(mx, my, px, py)
        return None

    def applyAllHeroes(self):
        for player in self.PLAYERS.values():
            player.est_try_move(self)
            

    def meatChopperEatHeroes(self):
        dead=self.OBJECTS.get(EL_DEAD_MEAT_CHOPPER, None)
        if dead==None:
            return
        for dx, dy in dead:
            for p in self.PLAYERS.values():
                if p.x()==dx and p.y()==dy:
                    LOGD("EST: Dead Meatchoppers eats player {}".format(p.ID))
                    p.set_alive(False)
        
    def tactAllBombs(self):
        bombs2remove = []
        for i,b in self.BOMBS.items():
            b.tick()
            if not b._is_alive: 
                ## check for killed
                b.est_boom(self)
                bombs2remove.append(i)
        for i in bombs2remove:
            self.BOMBS.pop(i, None)        

    def tactAllHeroes(self):
        for player in self.PLAYERS.values():
            player.tick()


    def moveChoppers(self):
        px, py = self.me().x(), self.me().y()
        res=False
        for ch in self.CHOPPERS.values():
            if ch.type==EL_DEAD_MEAT_CHOPPER: #moves always to player if attack us, but we don't know for certain - suppose worst
                cx, cy = ch.X, ch.Y
                if cx != px :
                    dx  = (-1,1) [cx<px]
                    dir = MOVES_MAP.get( (dx, 0) )
                    res = ch.est_try_move( dir , self)
                if cy != py and not res:
                    dy = (-1,1) [cy<py]
                    dir = MOVES_MAP.get( (0, dy) )
                    res = ch.est_try_move( dir , self)
            elif ch.type==EL_MEAT_CHOPPER:
                cx, cy = ch.X, ch.Y
                if cx != px :
                    dx  = (-1,1) [cx<px]
                    dir = MOVES_MAP.get( (dx, 0) )
                    res = ch.est_try_move( dir , self)
                if cy != py and not res:
                    dy = (-1,1) [cy<py]
                    dir = MOVES_MAP.get( (0, dy) )
                    res = ch.est_try_move( dir , self)                

    def board_next_tick(self):
        self.applyAllHeroes()
        self.meatChopperEatHeroes()
        self.moveChoppers()
        self.meatChopperEatHeroes()
        self.tactAllBombs()
        #tackAllPerks()
        self.tactAllHeroes()


    def chopper_predicted_positions(self):
        res = []
        for c in self.CHOPPERS.values():
            rx = c.X
            ry = c.Y
            pdir = c.get_last_move()
            if pdir!=None and  c.check_if_can_move( pdir , self ):
                dx, dy = MOVES[pdir]
                rx += dx
                ry += dy
            res.append( (rx,ry) ) 
        return res

    def board_object_find(self, x, y, t):
        for i,(ox,oy) in enumerate( self.OBJECTS[t] ):
            if x==ox and y==oy:
                return i
        return None

    def board_object_insert(self, x, y, t):
        self.BOARD[y][x] = t
        self.OBJECTS[t].append( (x,y) )

    def board_object_remove(self, x, y, t, tblank):
        assert(self.BOARD[y][x] == t)
        idx=self.board_object_find( x,y,t )
        if idx!=None:
            self.OBJECTS[t] = self.OBJECTS[t][:idx] + self.OBJECTS[t][idx+1:]

    def board_object_replace(self, x, y, told, tnew):
        assert( self.BOARD[y][x] == told)
        self.board_object_remove( x,y,told,tnew )
        self.OBJECTS[tnew].append( (x,y) )

    def board_generate(self):
        SZ = self.BOARD_SZ
        bnew = [ [EL_NONE]*SZ for _ in range(SZ) ]

        
        #copy walls
        for x,y in self.OBJECTS[EL_WALL]:
            assert(bnew[y][x]==EL_NONE)
            bnew[y][x]=EL_WALL
        for x,y in self.OBJECTS[EL_DESTROY_WALL]:
            assert(bnew[y][x]==EL_NONE)
            bnew[y][x]=EL_DESTROY_WALL

        #put perks
        for t in ELS_PERKS:
            for x,y in self.OBJECTS[t]:
                assert(bnew[y][x]==EL_NONE)
                bnew[y][x]=t

        #put choppers
        for t in ELS_CHOPPERS:
            for x,y in self.OBJECTS[t]:
                assert(bnew[y][x]==EL_NONE)
                bnew[y][x]=t

        #put bombs
        for b in self.BOMBS.values():
            x,y=b.X,b.Y
            if bnew[y][x] not in ELS_NOT_DANGER2MOVE:
                BREAK
            if b.bomb_type==BOMBTYPE_REMOTE:
                bnew[y][x] = EL_BOMB_TIMER_5
            elif b.bomb_type==BOMBTYPE_TIMER:
                bnew[y][x] = chr(ord(EL_BOMB_TIMER_1) + b.timer - 1)
            else:
                bnew[y][x] = chr(ord(EL_BOMB_TIMER_1) + b.timer - 1)

        #put players
        for p in self.PLAYERS.values():
            if not p._is_alive:
                continue
            x,y=p.x(),p.y()
            bomb_is_here = bnew[y][x] in ELS_BOMBS
            if p.ID==0:
                bnew[y][x] = (EL_BOMBERMAN, EL_BOMB_BOMBERMAN)[bomb_is_here]
            else:
                bnew[y][x] = (EL_OTHER_BOMBERMAN, EL_OTHER_BOMB_BOMBERMAN)[bomb_is_here]

        return bnew

    def do_next_cmd(self, cmd):
        LOGD("\n>>>>>>>>>>>>>>>>>>>>>>>>> DO CMD: {} >>>>>>>>>>>>>>>>>>>>>>>>>".format(cmd))
        cmds = cmd.split(",")
        board = deepcopy( self.BOARD )
        #print_board(board,True)
        x, y = self.me().x(), self.me().y()

        act_pre = False
        act_post= False
        for i,c in enumerate(cmds[:2]):
            if c=="ACT":
                if i==0:
                    act_pre=True
                else:
                    act_post=True
            else:
                self.me()._est_next_move = ACTIONS_MAP.get(c,"STOP")
        self.me()._est_act_post = act_post
        self.me()._est_act_pre  = act_pre

        self.board_next_tick()
        

        board_next=self.board_generate()

        board_string=  "".join( "".join(r)  for r in board_next )
        res = self.update_board_from( board_string )
        
        LOGD("<<<<<<<<<<<<<<<<<<<<<<< RES = {}  <<<<<<<<<<<<<<<<<<<<<<<<<</n".format( GAMERES2STR[res]))
        return res

    def players_store_state(self, logger):
        for i,p in enumerate(self.PLAYERS.values()):
            logger.log_types(p)
            logger.log("{}: ".format(i), endl='')
            logger.log_object(p, False)
        logger.log("===")

    def choppers_store_state(self, logger):
        for i,p in enumerate(self.CHOPPERS.values()):
            logger.log_types(p)
            logger.log("{}: ".format(i), endl='')
            logger.log_object(p, False)
        logger.log("===")

    def bombs_store_state(self, logger):
        for i,p in enumerate(self.BOMBS.values()):
            logger.log_types(p)
            logger.log("{}: ".format(i), endl='')
            logger.log_object(p, False)
        logger.log("===")


if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
