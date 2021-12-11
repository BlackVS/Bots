#! /usr/bin/env python3

from trackobjects import *

from model_defs import *
from model_directions import *

import game_rates as GAME_CONFIG


from enum import Enum

class PTYPE(Enum):
    ME    = 0
    OTHER = 1
    ZOMBIE = 2

MAP_PLAYER_MOVES_DXY = {
    DIR_UNKNOWN: DIR2XY[DIR_UNKNOWN],
    DIR_STOP   : DIR2XY[DIR_STOP],
    DIR_LEFT   : DIR2XY[DIR_LEFT],
    DIR_RIGHT  : DIR2XY[DIR_RIGHT],
    DIR_UP     : DIR2XY[DIR_UP],
    DIR_DOWN   : DIR2XY[DIR_DOWN],
}

# MAP_PLAYER_POSSIBLE_MOVES_DIR = {
#     DIR_UNKNOWN: [ DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN, DIR_STOP ],
#     DIR_LEFT   : [ DIR_LEFT ],
#     DIR_RIGHT  : [ DIR_RIGHT ] ,
#     DIR_UP     : [ DIR_UP ],
#     DIR_DOWN   : [ DIR_DOWN ],
#     DIR_STOP   : [ DIR_STOP ],
# }

PLAYER_MOVES_DXY = [ 
    DIR2XY[DIR_LEFT], 
    DIR2XY[DIR_RIGHT],
    DIR2XY[DIR_UP],
    DIR2XY[DIR_DOWN],    
    DIR2XY[DIR_STOP],
]
    
PLAYER_TRACK_POSSIBLE_DIRS = [DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN, DIR_STOP ]

PLAYER_ALLOWED_MOVES_MAP = (
    CMDS.CMD_STOP,
    CMDS.CMD_UP,
    CMDS.CMD_DOWN,
    CMDS.CMD_LEFT,
    CMDS.CMD_RIGHT,
    CMDS.CMD_FIRE_LEFT,
    CMDS.CMD_FIRE_RIGHT,
    # CMDS.CMD_FIRE_FLOOR_LEFT,
    # CMDS.CMD_FIRE_FLOOR_RIGHT,
    CMDS.CMD_FIRE_FLOOR_LEFT_GO,
    CMDS.CMD_FIRE_FLOOR_RIGHT_GO
)

PLAYER_ALLOWED_MOVES_FIRST = (
    CMDS.CMD_STOP,
    CMDS.CMD_UP,
    CMDS.CMD_DOWN,
    CMDS.CMD_LEFT,
    CMDS.CMD_RIGHT,
    CMDS.CMD_FIRE_LEFT,
    CMDS.CMD_FIRE_RIGHT,
    # CMDS.CMD_FIRE_FLOOR_LEFT,
    # CMDS.CMD_FIRE_FLOOR_RIGHT,
    CMDS.CMD_FIRE_FLOOR_LEFT_GO,
    CMDS.CMD_FIRE_FLOOR_RIGHT_GO
)

PLAYER_ALLOWED_MOVES_NEXT = (
    CMDS.CMD_STOP,
    CMDS.CMD_UP,
    CMDS.CMD_DOWN,
    CMDS.CMD_LEFT,
    CMDS.CMD_RIGHT,
    #CMDS.CMD_FIRE_LEFT,
    #CMDS.CMD_FIRE_RIGHT,
    # CMDS.CMD_FIRE_FLOOR_LEFT,
    # CMDS.CMD_FIRE_FLOOR_RIGHT,
    CMDS.CMD_FIRE_FLOOR_LEFT_GO,
    CMDS.CMD_FIRE_FLOOR_RIGHT_GO
)

PLAYER_ALLOWED_MOVES_RUN_AWAY = (
    CMDS.CMD_UP,
    CMDS.CMD_DOWN,
    CMDS.CMD_LEFT,
    CMDS.CMD_RIGHT,
)

PLAYER_MOVES_LAST_LAYER = (
    CMDS.CMD_UP,
    CMDS.CMD_DOWN,
    CMDS.CMD_LEFT,
    CMDS.CMD_RIGHT,
)


MAP_ZOMBIE_MOVES_DXY = {
    DIR_UNKNOWN: DIR2XY[DIR_UNKNOWN],
    DIR_STOP   : DIR2XY[DIR_STOP],
    DIR_LEFT   : DIR2XY[DIR_LEFT],
    DIR_RIGHT  : DIR2XY[DIR_RIGHT],
    DIR_UP     : DIR2XY[DIR_UP],
    DIR_DOWN   : DIR2XY[DIR_DOWN],
}

MAP_ZOMBIE_POSSIBLE_MOVES_DIR = {
    DIR_UNKNOWN: [ DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN, DIR_STOP ],
    DIR_LEFT   : [ DIR_LEFT ],
    DIR_RIGHT  : [ DIR_RIGHT ] ,
    DIR_UP     : [ DIR_UP ],
    DIR_DOWN   : [ DIR_DOWN ],
    DIR_STOP   : [ DIR_STOP ],
}

ZOMBIE_MOVES_DXY = [ 
    DIR2XY[DIR_LEFT], 
    DIR2XY[DIR_RIGHT],
    DIR2XY[DIR_UP],
    DIR2XY[DIR_DOWN],    
    DIR2XY[DIR_STOP],
]
    
ZOMBIE_POSSIBLE_MOVES = [DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN, DIR_STOP ]



class TPlayer(TObject):

    # BASIC TYPES
    DIR    = DIR_UNKNOWN
    ALIVE  = False

    # CUSTOM
    MASK   = False

    # Inner
    LastX  = None
    LastY  = None
    cnt_same_position = 0

    # shots
    shot_counter        = 0
    shot_counter_prev   = None
    gun_reload_time     = None


    # PERKS
    PERK_FIRE_NO_DELAY = 0

    perk_IMMORTALITY_cnt = 0
    perk_GLOVE_cnt = 0
    perk_RING_cnt = 0
    perk_KNIFE_cnt = 0

    ### Tracking support
    def __init__(self, ptype, ID=-1, X=None, Y=None, updated=False):
        self.PTYPE = ptype
        if self.PTYPE==PTYPE.ME:
            ID=0
        self.gun_reload_time = CONFIG_CUSTOM.gun_reload_time

        #tracking
        super().__init__(ID, X, Y, updated)
        #rest
        self.reset()

    def track_custom_update_from(self, object):
        
        #update with new values!!!
        self.ALIVE = object.ALIVE
        self.MASK  = object.MASK
        if object.DIR!=DIR_UNKNOWN:
            self.DIR = object.DIR
        
        #save old values, not overwrite!
        #self.PERK_FIRE_NO_DELAY   = object.PERK_FIRE_NO_DELAY 
        #self.shot_counter       = object.shot_counter     - 
        #self.gun_reload_time    = object.gun_reload_time  
        #self.perk_IMMORTALITY_cnt      = object.perk_IMMORTALITY_cnt
        #self.perk_WALKING_ON_WATER_cnt = object.perk_WALKING_ON_WATER_cnt
        #self.perk_VISIBILITY_cnt       = object.perk_VISIBILITY_cnt      


    ################### REST ###############################################################

    def reset(self):
        self.DIR=DIR_UNKNOWN
        self.ALIVE=False

        self.LastX = None
        self.LastY = None
        self.cnt_same_position = 0

        self.shot_counter = 0
        self.shot_counter_prev = None

        self.PERK_FIRE_NO_DELAY = 0 


        self.perk_IMMORTALITY_cnt = 0
        self.perk_GLOVE_cnt = 0
        self.perk_RING_cnt = 0
        self.perk_KNIFE_cnt = 0

        # self.est_lifetime=None
        # self.est_killer_id=None
        # self.est_is_target=False

    #update from board
    def update_params(self, params):
        if hasattr(params, "X") and hasattr(params, "Y"):
            self.update_pos(params.X, params.Y)
        if hasattr(params, "DIR"):
            self.DIR = params.DIR
        if hasattr(params, "ALIVE"):
            self.set_alive(params.ALIVE)
        if hasattr(params, "MASK"):
            self.MASK = params.MASK

    def update_pos(self, x, y):
        if self.X!=x or self.Y!=y:
            self.PX = self.X
            self.PY = self.Y
            self.X = x
            self.Y = y
            self.cnt_same_position = 0
        else:
            self.cnt_same_position +=1

    def track_moved(self, x, y):
        if self.X==x and self.Y==y:
            self.cnt_same_position+=1
        else:
            self.cnt_same_position=0
        super().track_moved(x, y)

    # #during estimates ????
    def tick_moved_event(self, x, y, rot, updatelastpos):
        # PX, PY - previous position without time
        if updatelastpos:
            self.LastX = x
            self.LastY = y

        if self.X!=x or self.Y!=y:
            self.PX = self.X
            self.PY = self.Y
            self.X = x
            self.Y = y
            self.DIR = rot


    def is_immortal_nextXmoves(self, next_X_moves):
        return self.perk_IMMORTALITY_cnt>=next_X_moves

    def is_dummy(self):
        return self.cnt_same_position>=GAME_CONFIG.PLAYER_SAME_POSITION_DETECT

    def store_last_pos(self):
        self.LastX = self.X
        self.LastY = self.Y

    def event_just_fired(self):
        self.shot_counter = self.gun_reload_time

    def set_alive(self, alive):
        if alive!=self.ALIVE:
            self.ALIVE=alive
            if alive:
                #print("Player {} respawn".format(self.get_ID()))
                pass
            else:
                print("Player {} died".format(self.get_ID()))
                self.reset()

    def is_alive(self):
        return self.ALIVE

    def do_cmd(self, cmd):
        if CMDS.COMMAND_HAS_FIRE(cmd):
            if self.shot_counter!=0:
                LOG("False fire detect!!!!")
            if self.PERK_FIRE_NO_DELAY==0:
                self.shot_counter = self.gun_reload_time
            else:
                self.shot_counter=0
        else:
            if self.shot_counter>0:
                self.shot_counter -= 1

        self.tick_perks()
        return True
    
    def can_fire(self):
        return self.shot_counter == 0

    def could_fire(self):
        return self.shot_counter_prev == 0 and self.PX!=None and self.PY!=None

    def got_perk(self, perk):
        if perk.perk_type==PERKTYPE.GLOVE:
            self.perk_GLOVE_cnt+=1
        if perk.perk_type==PERKTYPE.KNIFE:
            self.perk_KNIFE_cnt+=1
        if perk.perk_type==PERKTYPE.RING:
            self.perk_RING_cnt+=1

        if perk.perk_type==PERKTYPE.MASK:
            self.perk_IMMORTALITY_cnt = CONFIG.GAME.Mask_ticks


    def tick_perks(self):
        if self.PERK_FIRE_NO_DELAY:
            self.PERK_FIRE_NO_DELAY-=1

        if self.perk_IMMORTALITY_cnt:
            self.perk_IMMORTALITY_cnt-=1

    def tick(self):
        #update timers
        self.shot_counter_prev=self.shot_counter
        if self.shot_counter>0:
            self.shot_counter -= 1
        self.tick_perks()


    def simulate_autofire(self, board, targetX, targetY):
        fcmds = board.player_to_target_hit_cmds(self.X, self.Y, targetX, targetY, maxdist=30, checkIfNear=True)
        if fcmds: #auto fire in all these directions %)
            for cmd, dst_hit in fcmds:
                fdir = CMDS.COMMAND_FIRE2DIR(cmd)
                bullet = board.BULLETS.add_custom_bullet(self.X, self.Y, fdir, 0) #no delay
                bullet.parent_id = self.ID # ME


    def simulate(self, cmd, board, autofire_to=None):
        # do cmd
        if cmd==None or cmd==CMDS.CMD_NULL:
            self.tick() #just tick
            return

        fdir = CMDS.COMMAND_FIRE2DIR(cmd)
        if fdir!=None: #i.e. not fire
            #bullet at my position 
            if fdir == CMDS.CMD_FIRE:
                # with my direction
                fdir=self.DIR
            delayed_appear_cnt = (0,1)[fdir!=self.DIR]
            bullet = board.BULLETS.add_custom_bullet(self.X, self.Y, fdir, delayed_appear_cnt) 
            bullet.parent_id = self.ID # ME


        dx, dy, mdir = CMDS.COMMAND_BASE_DXYD(cmd)
        if mdir==DIR_SAME:
            mdir = self.DIR

        if not self.is_alive():
            return

        self.do_cmd(cmd) #updates only perks counters
        #tree case, estimate move
        nx, ny = self.X+dx, self.Y+dy
        if not board.is_onboard(nx,ny):
            return
        c = board.BOARD[ny][nx]
        if c not in MMOVES.PLAYER_BARRIER:
            self.tick_moved_event(nx, ny, mdir, False)

        if autofire_to!=None and self.can_fire() and self.ID!=0: 
            self.simulate_autofire(board, autofire_to.X, autofire_to.Y)
            


    def estimate_next_pos(self):
        #if self.player_type in [ETANK_TYPE_AI, ETANK_TYPE_ME]:

        # dx, dy = DIR2XY[self.DIR]
        # return (True, self.X+dx, self.Y+dy)

        # dx, dy = DIR2XY[self.DIR]
        # if self.X!=self.PY or self.Y!=self.PY:
        #     return (True, self.X+dx, self.Y+dy)
        # return (False, self.X, self.Y)

        return (False, self.X, self.Y) #not estimated yet usual players

    def qstar_object_direction_after_cmd(self, cmd):
        dir=CMDS.QSTAR_GET_DIR_AFTER_CMD(cmd)
        if dir == DIR_UNKNOWN:
            dir=self.DIR
        return dir

    def track_possible_moves(self):
        return PLAYER_TRACK_POSSIBLE_DIRS

    def track_move_dir2xy(self, dir):
        return MAP_PLAYER_MOVES_DXY[dir]

    def take_perk_profit(self, perk):
        perk_type = perk.perk_type
        if perk_type == PERKTYPE.GLOVE:
            return CONFIG.SCORE.Glove_clue_score + self.perk_GLOVE_cnt * CONFIG.SCORE.Glove_clue_score_increment
        if perk_type == PERKTYPE.KNIFE:
            return CONFIG.SCORE.Knife_clue_score + self.perk_KNIFE_cnt * CONFIG.SCORE.Knife_clue_score_increment
        if perk_type == PERKTYPE.RING:
            return CONFIG.SCORE.Ring_clue_score + self.perk_RING_cnt * CONFIG.SCORE.Ring_clue_score_increment
        if perk_type == PERKTYPE.MASK:
            return 5 
        return 0

class TPlayers(TObjects):

    PTYPE = None
    def __init__(self, ptype):
        #super().__init__() - static object, not called
        self.PTYPE = ptype
        self.cleanup()

    #CUSTOM METHODS
    def object_new(self):
        return TPlayer(self.PTYPE)

    def create_object(self, x, y, DIR):
        obj = self.object_new()
        obj.X = x
        obj.Y = y
        obj.DIR = DIR
        return obj

    def tracking_add_object(self, x, y, data):
        DIR = getattr(data, "DIR", DIR_UNKNOWN)
        obj = self.create_object(x, y, DIR)
        self.tobjects_new.append( obj )
        return obj

    def tracking_could_be_object(self, x, y, t):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            nres, nx, ny = p.estimate_next_pos()
            if nres and nx==x and ny==y:
                return self.tracking_add_object(x, y, p.DIR)
        return None

    def tick(self):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            p.tick()

    def store_state(self, logger):
        logger.log_object(self)
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            logger.log_types(p)
            logger.log("{}: ".format(i), endl='')
            logger.log_object(p, False)
        logger.log("===")

    def could_be_masked(self, x, y):
        player = self.get_at(x,y) 
        if player!=None: #found just set updated
            player.updated = True
