#! /usr/bin/env python3

from trackobjects import *

from command import *
from config import *
from element import *
from directions import *
from logger import *
from game_rates import *

class TPlayer(TObject):

    rotation            = DIR_UNKNOWN
    alive               = True
    shot_counter        = 0
    shot_counter_prev   = None
    gun_reload_time     = None
    sliding_cnt = 0

    #
    player_type = None

    #Player ME and OTHER
    perk_IMMORTALITY_cnt = 0
    perk_BREAKING_WALLS_cnt = 0 
    perk_WALKING_ON_WATER_cnt = 0
    perk_VISIBILITY_cnt = 0
    perk_NO_SLIDING_cnt = 0
    
    #AI
    ai_has_perk = False

    #
    cnt_same_position = 0

    # bullets tracking
    est_lifetime  = None
    est_killer_id = None
    est_is_target = False

    LastX = None
    LastY = None

    est_in_tree = 0

    ### Tracking support
    def __init__(self, ttype, id=-1, x=None, y=None, updated=False):
        self.player_type=ttype
        if ttype==ETANK_TYPE_ME:
            id=0
        if ttype in [ETANK_TYPE_ME, ETANK_TYPE_OTHER]:
            self.gun_reload_time = CONFIG["tankTicksPerShoot"] - 1
        elif ttype == ETANK_TYPE_AI:
            self.gun_reload_time = CONFIG["aiTicksPerShoot"] - 1
        else:
            ASSERT()
        #tracking
        super().__init__(id, x, y, updated)
        #rest
        self.reset_player()

    def track_custom_update_from(self, object):
        self.alive              = object.alive

        #
        #self.rotation           = object.rotation
        if object.rotation!=DIR_UNKNOWN:
            self.rotation = object.rotation
        
        # save old values, not overwrite!
        #self.shot_counter       = object.shot_counter     - 
        #self.gun_reload_time    = object.gun_reload_time  
        #self.sliding_cnt

        #self.perk_IMMORTALITY_cnt      = object.perk_IMMORTALITY_cnt
        #self.perk_BREAKING_WALLS_cnt   = object.perk_BREAKING_WALLS_cnt 
        #self.perk_WALKING_ON_WATER_cnt = object.perk_WALKING_ON_WATER_cnt
        #self.perk_VISIBILITY_cnt       = object.perk_VISIBILITY_cnt      
        #self.perk_NO_SLIDING_cnt       = object.perk_NO_SLIDING_cnt      

        ## AI
        self.ai_has_perk = self.ai_has_perk or object.ai_has_perk

    ################### REST ###############################################################

    def reset_player(self):
        self.rotation=DIR_UNKNOWN
        self.alive=False
        self.shot_counter = 0
        self.shot_counter_prev = None
        self.cnt_same_position = 0
        self.est_lifetime=None
        self.est_killer_id=None
        self.est_is_target=False
        self.perk_IMMORTALITY_cnt = 0
        self.perk_BREAKING_WALLS_cnt = 0 
        self.perk_WALKING_ON_WATER_cnt = 0
        self.perk_VISIBILITY_cnt = 0
        self.perk_NO_SLIDING_cnt = 0
        self.sliding_cnt = 0
        self.LastX = None
        self.LastY = None
        self.est_in_tree = 0

    def is_immortal(self, next_X_moves):
        return self.perk_IMMORTALITY_cnt>=next_X_moves

    def not_moving_long(self):
        return self.cnt_same_position>=PLAYER_SAME_POSITION_DETECT

    def moved(self, x, y, rot, updatelastpos):
        # PX, PY - previous position without time
        if updatelastpos:
            self.LastX = x
            self.LastY = y

        if self.X!=x or self.Y!=y:
            self.PX = self.X
            self.PY = self.Y
            self.X = x
            self.Y = y
            self.rotation = rot

    def store_last_pos(self):
        self.LastX = self.X
        self.LastY = self.Y

    def event_just_fired(self):
        self.shot_counter = self.gun_reload_time

    def set_alive(self, alive):
        if alive!=self.alive:
            self.alive=alive
            if alive:
                print("Player {} respawn".format(self.ID))
            else:
                print("Player {} died".format(self.ID))
                self.reset_player()

    def is_alive(self):
        return self.alive

    def do_cmd(self, cmd):
        if cmd in COMMANDS_FIRE:
            if self.shot_counter!=0:
                LOG("False fire detect!!!!")
            if self.perk_BREAKING_WALLS_cnt==0:
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
        if perk==EPRIZE_IMMORTALITY:
            self.perk_IMMORTALITY_cnt=CONFIG["prizeWorking"]

        if perk==EPRIZE_BREAKING_WALLS:
            self.perk_BREAKING_WALLS_cnt=CONFIG["prizeWorking"]

        if perk==EPRIZE_WALKING_ON_WATER:
            self.perk_WALKING_ON_WATER_cnt=CONFIG["prizeWorking"]

        if perk==EPRIZE_VISIBILITY:
            self.perk_VISIBILITY_cnt=CONFIG["prizeWorking"]

        if perk==EPRIZE_NO_SLIDING:
            self.perk_NO_SLIDING_cnt=CONFIG["prizeWorking"]
            self.sliding_cnt=0 #if got on ice
        pass

    def tick_perks(self):
        if self.perk_IMMORTALITY_cnt:
            self.perk_IMMORTALITY_cnt-=1

        if self.perk_BREAKING_WALLS_cnt:
            self.perk_BREAKING_WALLS_cnt-=1

        if self.perk_WALKING_ON_WATER_cnt:
            self.perk_WALKING_ON_WATER_cnt-=1

        if self.perk_VISIBILITY_cnt:
            self.perk_VISIBILITY_cnt-=1

        if self.perk_NO_SLIDING_cnt:
            self.perk_NO_SLIDING_cnt-=1

        if self.sliding_cnt>0:
            self.sliding_cnt-=1


    def tick(self):
        #update timers
        self.shot_counter_prev=self.shot_counter
        if self.shot_counter>0:
            self.shot_counter -= 1
        self.tick_perks()

    def estimate_next_pos(self):
        if self.sliding_cnt:
            if self.player_type==ETANK_TYPE_ME: #me do differently! and checked in other place
                pass
            else: #AI and OTHER correctly tarces LastX, Y
                if self.LastX!=None and self.LastY!=None:
                    dx, dy = self.X-self.LastX, self.Y-self.LastY
                    return (True, self.X+dx, self.Y+dy)
        
        if self.player_type in [ETANK_TYPE_AI, ETANK_TYPE_ME]:
            dx, dy = DIR2XY[self.rotation]
            return (True, self.X+dx, self.Y+dy)
        return (False, self.X, self.Y) #not estimated yet usual players

    def moved_on_ice(self, is_sliding):
        if not is_sliding:
            self.sliding_cnt=0
            return 
        if self.sliding_cnt>0: #already sliding
            if self.LastX!=None and self.LastY!=None and self.LastX==self.X and self.LastY==self.Y: #barried
                self.sliding_cnt=0
            #self.sliding_cnt-=1 - will be decreased on tick with perks!!!
            pass
        else:
            self.sliding_cnt=CONFIG['slipperiness']


    def get_final_direction_after_cmd(self, cmd):
        dir = DIR_UNKNOWN
        if cmd in COMMANDS_FIRE:
            #bullet at my position
            if cmd == CMD_FIRE:
                dir=self.rotation
            else:
                dir=MAP_COMMANDS_FIRE2DIR[cmd]
        elif cmd==CMD_STOP:
            dir = self.rotation
        else:
            dir = COMMANDS2DIR[cmd]
        return dir

class TPlayers(TObjects):

    player_type = None
    def __init__(self, ttype):
        #super().__init__() - static object, not called
        self.player_type = ttype
        self.cleanup()

    #CUSTOM METHODS
    def object_new(self):
        return TPlayer(self.player_type)

    def create_object(self, x, y, t):
        obj = self.object_new()
        obj.X = x
        obj.Y = y
        obj.rotation = t
        return obj

    def tracking_add_object(self, x, y, t):
        obj = self.create_object(x, y, t)
        self.tobjects_new.append( obj )
        return obj

    def tracking_could_be_object(self, x, y, t):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            nres, nx, ny = p.estimate_next_pos()
            if nres and nx==x and ny==y:
                return self.tracking_add_object(x, y, p.rotation)
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



class TBullet(TObject):
    parent_id = None
    direction = DIR_UNKNOWN
    toremove = False

    def __init_(self, direction=DIR_UNKNOWN):
        self.direction = direction
        super.__init__()

    def custom_update_from(self, object):
        self.direction   = object.direction

    def estimate_next_pos(self):
        # if self.flying and self.PX!=None and self.PY!=None:
        #     dx, dy = self.X-self.PX, self.Y-self.PY
        #     return (True, self.X+dx, self.Y+dy)
        return (None, None, None) # (estimated, x, y)

    def tick(self):
        dx, dy = DIR2XY[self.direction]
        self.PX = self.X
        self.PY = self.Y
        self.X += dx
        self.Y += dy

    def hit_chance(self, x, y):
        dd = (0,1,2)
        if CHECK_BULLET_NEW:
            dd = (1,2)
        if self.direction!=DIR_UNKNOWN:
            dx, dy = DIR2XY[self.direction]
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

    def tracking_add_object(self, x, y):
        obj = self.create_object(x, y)
        self.tobjects_new.append( obj )
        return obj

    def possible_moves(self):
        return [ (-2, 0), (2,0), (0,-2), (0,2) ]


    def tracking_finish(self):
        super().tracking_finish()
        #update directions
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            if p.PX!=None and p.PY!=None:
                p.direction = dxy2dir(p.X-p.PX, p.Y-p.PY)

    def add_custom_bullet(self, x, y, dir):
        if dir==DIR_UNKNOWN:
            return
        obj = self.create_object(x, y)
        obj.direction = dir
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