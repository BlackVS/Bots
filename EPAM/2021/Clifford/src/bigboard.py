#! /usr/bin/env python3

# import element as EL
from enum import auto
import json
import copy
import time
from math import sqrt
# from element import *
from config import *
# from trackobjects_custom import *
# from perks import *

from logger import *
import game_rates as GAME_CONFIG

from model import *

from types import SimpleNamespace

from model_commands import CMD_FIRE

def print_input(data):
    if not DEBUG:
        return
    w = h = int(sqrt(len(data)))  # size of the board 
    for i in range(h):
        LOG("{:2} : {}".format(i,data[i*w: (i+1)*w]))


def dist(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)


def scaled_danger(dg, d):
    if d<=GAME_CONFIG.DANGER_DIST_RADIUS:
        return dg
    res = dg - ((d - GAME_CONFIG.DANGER_DIST_RADIUS)*dg)//GAME_CONFIG.DANGER_DIST_DECAY
    return max(0, res)

def scaled_danger_me(dg, mx, my, x, y):
    if mx==None or my==None:
        return dg #not scale if me hidden
    d = dist(mx, my, x, y)
    if d<=GAME_CONFIG.DANGER_DIST_RADIUS:
        return dg
    res = dg - ((d - GAME_CONFIG.DANGER_DIST_RADIUS)*dg)//GAME_CONFIG.DANGER_DIST_DECAY
    return max(0, res)

def dist2me(mx,my,x,y):
    if mx==None or my==None:
        return 0 #unknown
    return abs(x1-x2)+abs(y1-y2)

class BigBoard:
    width  = 0
    height = 0

    last_string = ""    
    last_string_same_cnt = 0
    last_cmd = CMDS.CMD_NULL

    counter = 0 #just to track in logs
    round_tick_cnt = 0


    #global board
    BOARD_STR = None

    BOARD     = None #non-movable elements of board i.e. walls, laser guns, exits, starts etc
    DANGERS_MAP = None
    ATTACK_MAP_AI  = None
    ATTACK_MAP_OTHER = None
    #VISIBILITY_MAP = None


    # Objects

    ## ME
    ME          = TPlayer(PTYPE.ME)

    ## COLLECTIONS
    PLAYERS = TPlayers(PTYPE.OTHER)
    ZOMBIES = TPlayers(PTYPE.ZOMBIE)
    BULLETS = TBullets()
    PERKS   = Perks()


    ### GLOBAL STORAGE
    global_board_idx = None

    #HISTORY
    OBJECTS_MAP        = dict()
    OBJECTS_MAP_ID2OBJ = dict()
    OBJECTS_MAP_PREV   = dict()

    ## inner
    PERKS_OLD = None

    PLAYER_POSSIBLE_DIRS = None
    PLAYER_POSSIBLE_MOVES = None
    
    def __init__(self):
        self.width  = 0
        self.height = 0

    def is_game_start(self):
        return self.last_string_same_cnt>=4

    def cleanup(self):
        global IDXCNT
        IDXCNT = 1

        reset_tracking()

        self.BOARD = [ [ELB.EB_UNKNOWN] * self.width for _ in range(self.height) ]
        self.ME         = TPlayer(PTYPE.ME)
        self.ZOMBIES    = TPlayers(PTYPE.ZOMBIE)
        self.PLAYERS    = TPlayers(PTYPE.OTHER)
        self.BULLETS    = TBullets()
        self.PERKS = Perks()

        self.global_board_idx= None

        self.OBJECTS_MAP        = dict()
        self.OBJECTS_MAP_PREV   = dict()

        self.last_cmd = CMDS.CMD_NULL

        self.PLAYER_POSSIBLE_MOVES = None
        self.PLAYER_POSSIBLE_DIRS  =None

        self.round_tick_cnt = 0


    def clone(self, t):
        res = BigBoard()
        res.width       = self.width
        res.height      = self.height
        #res.BOARD       = copy.deepcopy(self.BOARD)
        res.BOARD       = copy.deepcopy(self.BOARD)
        res.ME          = copy.deepcopy(self.ME)
        res.ZOMBIES = copy.deepcopy(self.ZOMBIES) #movable object
        res.PLAYERS = copy.deepcopy(self.PLAYERS) #movable object
        res.BULLETS = copy.deepcopy(self.BULLETS) #movable object
        res.PERKS   = self.PERKS.clone()

        #will be recreated
        if t==0:
            res.OBJECTS_MAP = copy.deepcopy(self.OBJECTS_MAP) #movable object
            res.OBJECTS_MAP_PREV = copy.deepcopy(self.OBJECTS_MAP_PREV) #movable object
            res.PLAYER_POSSIBLE_MOVES =copy.deepcopy(self.PLAYER_POSSIBLE_MOVES)
            res.PLAYER_POSSIBLE_DIRS = copy.deepcopy(self.PLAYER_POSSIBLE_DIRS)
        return res


    def resize(self, new_width, new_height):
        if self.BOARD == None or new_width > self.width or new_height > self.height:

            new_width  = max(new_width,  self.width)
            new_height = max(new_height, self.height)

            board     = [ [ELB.EB_UNKNOWN] * new_width for _ in range(new_height) ]
            if self.BOARD:
                for y in range(self.height):
                    for x in range(self.width): #to-do: via slice copying
                        board[y][x]    =self.BOARD[y][x]

            
            self.BOARD=board
            self.width  = new_width
            self.height = new_height

    def is_onboard(self,x,y):
        return x>=0 and y>=0 and x<self.width and y<self.height

    def get_board_item(self, x, y):
        if not self.is_onboard(x,y):
            return None
        return self.BOARD[y][x]

    #try detect parents of bullets
    def bullets_after_finish(self):
        for ib in range(self.BULLETS.size()):
            b=self.BULLETS.get(ib)
            if b.DIR!=DIR_UNKNOWN:
                continue
            #try detect rotation - check all old neighbours
            NXY = BULLET_MOVES_DXY_TRACK
            pid = None
            pobj = None
            pdx = None
            pdy = None
            for dx,dy in NXY:
                nx = b.X+dx
                ny = b.Y+dy
                if not self.is_onboard(nx,ny):
                    continue
                pr = self.OBJECTS_MAP_PREV.get( (nx,ny), None )
                if pr==None:
                    continue
                if pid==None:
                    pid  = pr[0]
                    pobj = pr[1]
                    pdx = -dx
                    pdy = -dy
                else:#few variants, can't detect easily
                    pid =None
                    break
            if pid!=None and pid!=0:
                b.parent_id=pid
                b.DIR = dxy2dir( pdx, pdy )
                pobj.event_just_fired()
                #LOG("JUST FIRED ID={} gun_cnt={}".format(pid, pobj.shot_counter))

    def perks_after_finish(self):
        perks_old = self.PERKS_OLD
        if self.ME.is_alive:
            perk = perks_old.get_perk_at(self.ME.X, self.ME.Y)
            if perk!=None:
                self.ME.got_perk( perk )
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            perk = perks_old.get_perk_at(p.X, p.Y)
            if perk!=None:
                p.got_perk( perk )
        
    def players_after_finish(self):
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)

    def zombies_after_finish(self):
        for ip in range(self.ZOMBIES.size()):
            p=self.ZOMBIES.get(ip)

    def me_after_finish(self):
        p=self.ME
        if p==None or p.X==None or p.Y==None:
            return

    def store_print_input(self, logger):
        if not logger:
            return
        logger.log("\nINPUTBOARD:")
        data = self.BOARD_STR
        w = h = int(sqrt(len(data)))  # size of the board 
        for i in range(h):
            logger.log("{:2} : {}".format(i,data[i*w: (i+1)*w]))

    def store_state(self, logger):
        if not logger:
            return
        #ME:
        logger.log("\nME:")
        logger.log_object(self.ME)

        logger.log("\nPLAYERS:")
        self.PLAYERS.store_state(logger)

        logger.log("\nZOMBIES:")
        self.ZOMBIES.store_state(logger)

        logger.log("\nBULLETS:")
        self.BULLETS.store_state(logger)

        logger.log("\nPERKS:")
        self.PERKS.store_state(logger)



    def process_board_before_start(self):
        self.bullets_before_start()
        self.perks_before_start()
        self.players_before_start()
        self.zombies_before_start()
        self.me_before_start()

    # Just moves objects without simulation
    def process_tick(self, cmd, logger):
        self.me_do_cmd(cmd, logger)
        self.PLAYERS.tick()
        self.ZOMBIES.tick()
        self.BULLETS.tick()
        self.PERKS.tick()

    def process_tracking_start(self):
        self.BULLETS.tracking_init(self.width, self.height)
        self.ZOMBIES.tracking_init(self.width, self.height)
        self.PLAYERS.tracking_init(self.width, self.height)
        self.PERKS.tracking_start(self.width, self.height)

    def process_tracking_finish(self):
        self.ZOMBIES.tracking_finish()
        self.PLAYERS.tracking_finish()
        self.BULLETS.tracking_finish()
        self.PERKS.tracking_finish()

    def process_tracking_after_finish(self):
        self.bullets_after_finish()
        self.perks_after_finish()
        self.players_after_finish()
        self.zombies_after_finish()
        self.me_after_finish()

    def process_input_board(self, input):
        LOG("===================================================================================")
        LOG("CNT = {}".format(BigBoard.counter))
        LOG("===================================================================================")
        BigBoard.counter+=1

       
        board_str = input.replace('\n', '')

        game_over = False
        if board_str==self.last_string:
            self.last_string_same_cnt +=1
        else:
            self.last_string_same_cnt = 0
            self.last_string = board_str
        self.BOARD_STR=board_str

        print_input(board_str)

        w  = h = int(sqrt(len(board_str)))  # size of the board 


        # if self.last_string_same_cnt>3:
        if ELI.EL_HERO_DIE in input:
            game_over = True
            print("!!!RESET!!!")




        if game_over:
            self.cleanup()
            #return False #- not return to not miss
            

        self.process_board_before_start()
        

        ####
        self.OBJECTS_MAP_PREV = self.OBJECTS_MAP
        self.resize( w, h )
        self.reset_stats()
        

        self.process_tracking_start()

        self.PERKS_OLD = copy.deepcopy(self.PERKS)

        self.update_layer_ground(board_str)
        self.update_layer_objects(board_str)

        self.process_tracking_finish()

        self.make_objects_map()

        self.process_tracking_after_finish()

        self.make_dangers_map(False)

        self.make_possible_moves_map()

        self.round_tick_cnt+=1
        return not game_over

    def reset_stats(self):
        return 


    def update_layer_ground(self, data_string):
        w  = int(sqrt(len(data_string)))
        
        for y in range(w):
            for x in range(w):
                # if y==25 and x==25:
                #     print(1)
                cinp = data_string[y*w+x]
                
                ## first apply MAP
                cbrd = MAPI2B.MAP_INPUT2BOARD_GROUND.get(cinp, None)
                if cbrd==None:
                    continue
                self.BOARD[y][x]=cbrd[0] #no update params yet
                if cbrd[1]: #custom data
                    #check possible maskings
                    collnames = cbrd[1].get("_COULDMASK", None)
                    if collnames:
                        if isinstance(collnames, str):
                            collnames = [collnames]
                        for collname in collnames:
                            collection = getattr(self, collname, None)
                            if collection==None:
                                LOG("ERROR: no {} collection found".format(collname))
                                return
                            collection.could_be_masked(x,y)


    def update_object(self, newX, newY, data,):
        objname = getattr(data, "object", None)
        if objname!=None: #specific object update
            obj = getattr(self, objname, None)
            if obj==None:
                LOG("ERROR: no {} object found".format(objname))
                return
            obj.update_params(data)
            obj.update_pos(newX, newY)
            return
        collname = getattr(data, "collection", None)
        if collname!=None: #specific object update
            collection = getattr(self, collname, None)
            if collection==None:
                LOG("ERROR: no {} collection found".format(collname))
                return

            obj=collection.tracking_add_object(newX, newY, data)
            if obj!=None:
                obj.update_params(data)
        



    def update_layer_objects(self, data_string):
        w  = int(sqrt(len(data_string)))
        
        for y in range(w):
            for x in range(w):
                cinp = data_string[y*w+x]
                cbrd = MAPI2B.MAP_INPUT2OBJECT.get(cinp, None)
                if cbrd==None:
                    continue
                
                cprops = { k:v for k,v in cbrd.items() if k[0]!='_' }
                data = SimpleNamespace(**cprops)


                #check possible maskings
                collnames = cbrd.get("_COULDMASK", None)
                found_masked = False
                if collnames:
                    if isinstance(collnames, str):
                        collnames = [collnames]
                    for collname in collnames:
                        # if collname=="ZOMBIES":
                        #     print(1)
                        collection = getattr(self, collname, None)
                        if collection==None:
                            LOG("ERROR: no {} collection found".format(collname))
                            return
                        found_masked = found_masked or collection.could_be_masked(x,y)



                objectcoll = getattr(data, "collection", None)
                ignoreitem = objectcoll and collnames and (objectcoll in collnames) and found_masked
                if not ignoreitem:
                    self.update_object(x, y, data)


    def print(self, title=None):
        if not DEBUG:
            return

        #board 

        # res = []
        # for y in range(self.height):
        #     r = copy.copy(self.BOARD[y])
        #     res.append( r )

        # for iz in range(self.ZOMBIES.size()):
        #     z=self.ZOMBIES.get(iz)
        #     res[z.Y][z.X] = DIR2TANK_AI[z.DIR]

        # for ip in range(self.PLAYERS.size()):
        #     p=self.PLAYERS.get(ip)
        #     if ip==0:
        #         res[p.Y][p.X] = DIR2TANK[p.DIR]
        #     else:
        #         res[p.Y][p.X] = DIR2TANK_OTHER[p.DIR]

        # for ib in range(self.BULLETS.size()):
        #     b=self.BULLETS.get(ib)
        #     res[b.Y][b.X] = EBULLET

        # #FILELOG
        # if title:
        #     LOGF(title)
        # for r in res:
        #     LOGF("".join( r))
        # #print players, zombies, shots
        # for i in range(self.PLAYERS.size()):
        #     p = self.PLAYERS.get(i)
        #     LOGF("PLAYER id={} x={} y={} fly={}".format(p.ID,p.X,p.Y,p.DIR))

        # for i in range(self.ZOMBIES.size()):
        #     z = self.ZOMBIES.get(i)
        #     LOGF("ZOMBIE id={} x={} y={}".format(z.ID,z.X,z.Y))

        # for i in range(self.BULLETS.size()):
        #     z = self.BULLETS.get(i)
        #     LOGF("BULLET id={} x={} y={}".format(z.ID,z.X,z.Y))

        # LOGF("\n")


    def simulate_bullets(self):
        self.BULLETS.simulate(self)
        self.BULLETS.remove() #remove not active

    def simulate_PLAYERS(self, autofire=False):
        for i in range(self.PLAYERS.size()):
            p = self.PLAYERS.get(i)
            if p.is_alive():
                allowed_moves = list(self.PLAYER_POSSIBLE_MOVES[p.Y][p.X])
                if allowed_moves and len(allowed_moves)==1: #only one move!
                    #no choice - do
                    if autofire and not p.is_dummy():
                        p.simulate( allowed_moves[0], self, (self.ME.X, self.ME.Y) )
                    else:
                        p.simulate( allowed_moves[0], self)
                else:
                    #just tick
                    p.tick()
                    #and auto fire
                    if autofire and not p.is_dummy():
                        p.simulate_autofire(self, self.ME.X, self.ME.Y )

    def simulate_PLAYERS_tick0(self, autofire=False): #no tick/inner state update, just bullets generation or similar
        if not autofire:
            return #nothing to do
        for i in range(self.PLAYERS.size()):
            p = self.PLAYERS.get(i)
            if p.is_alive():
                if autofire and not p.is_dummy():
                    p.simulate_autofire(self, self.ME.X, self.ME.Y )

    def simulate_ZOMBIES(self):
        for i in range(self.ZOMBIES.size()):
            p = self.ZOMBIES.get(i)
            if p.is_alive():
                allowed_moves = list(self.PLAYER_POSSIBLE_MOVES[p.Y][p.X]) #zombie has same move model
                if allowed_moves and len(allowed_moves)==1:
                    #no choice - do
                    p.simulate( allowed_moves[0], self )
                else:
                    #just tick
                    p.tick()

    def tick_AIs(self):
        self.ZOMBIES.tick() #update perks
        for i in range(self.ZOMBIES.size()):
            z = self.ZOMBIES.get(i)
            if z.DIR == DIR_UNKNOWN:
                continue #
            nres, nx, ny = z.estimate_next_pos()
            if not nres:
                continue
            if not self.is_onboard(nx,ny):
                continue
            c = self.BOARD[ny][nx]
            if c not in MMOVES.ZOMBIE_BARRIER:
                z.tick_moved_event(nx, ny, z.DIR, False)
            else:
                z.DIR=DIR_UNKNOWN #don't know where will go
                z.est_is_stuck = True #to reduce profit from hitting it
            
    def tick_PLAYERS(self):
        self.PLAYERS.tick() #update perks
        for i in range(self.PLAYERS.size()):
            z = self.PLAYERS.get(i)
            z.tick()
            if z.DIR == DIR_UNKNOWN:
                continue #
            nres, nx, ny = z.estimate_next_pos()
            if not nres:
                continue
            if not self.is_onboard(nx,ny):
                continue
            c = self.BOARD[ny][nx]
            if c not in MMOVES.PLAYER_BARRIER:
                z.tick_moved_event(nx, ny, z.DIR, False)
            else:
                z.DIR=DIR_UNKNOWN #don't know where will go
                z.est_is_stuck = True #to reduce profit from hitting it
            

    def simulate(self):
        self.simulate_bullets()
        self.simulate_PLAYERS( GAME_CONFIG.SIMULATE_PLAYERS_AUTOFIRE_NEXT)
        self.simulate_ZOMBIES()
        self.PERKS.tick()
        self.ME.tick()

    def simulate_tick0(self): #
        self.simulate_PLAYERS_tick0( GAME_CONFIG.SIMULATE_PLAYERS_AUTOFIRE_TICK0)
      

    def scalefire(self, r, t):
        if not self.ME.perk_deathray_cnt:
            t=min( t, len(RATE_FIRE_SCALES)-1)
            return int(r*RATE_FIRE_SCALES[t])
        return r

    def update_danger_at(self, x, y, dg, scaled):
        if not self.is_onboard(x,y):
            return
        dangers = self.DANGERS_MAP
        if scaled:
            mx = self.ME.X
            my = self.ME.Y
            dg = scaled_danger_me(dg, mx, my, x, y)
        dangers[y][x] = max(dangers[y][x], dg)


    def update_danger_dir(self, x, y, dx, dy, dd, dg, scaled, ignored=[], barrier=[]):
        for i in range(dd+1):
            ny = y+i*dy
            nx = x+i*dx
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            if c in barrier:
                break
            self.update_danger_at(nx, ny, dg, scaled)

    def update_danger_dir_decayed(self, x, y, dx, dy, dd, dg, scaled, ignored=[], barrier=[], decay=[1, 0.8, 0.7] ):
        for i in range(dd+1):
            ny = y+i*dy
            nx = x+i*dx
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            if c in barrier:
                break
            if i<len(decay):
                dgscaled = int(decay[i]*dg)
            else:
                dgscaled = int(decay[-1]*dg)
            self.update_danger_at(nx, ny, dgscaled, scaled)

    def update_danger_HV(self, x, y, dx, dy, dg, scaled, ignored=[]):
        ny = y
        for nx in range(x-dx, x+dx+1):
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            self.update_danger_at(nx, ny, dg, scaled)

        nx = x
        for ny in range(y-dy, y+dy+1):
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            self.update_danger_at(nx, ny, dg, scaled)


    def update_danger_H(self, x, y, dx, dg, scaled, ignored=[]):
        ny = y
        for nx in range(x-dx, x+dx+1):
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            self.update_danger_at(nx, ny, dg, scaled)

    def update_danger_V(self, x, y, dy, dg, scaled, ignored=[]):
        nx = x
        for ny in range(y-dy, y+dy+1):
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            self.update_danger_at(nx, ny, dg, scaled)

    def update_danger_HV_MAP(self, x, y, dx, dy, dgmap, scaled, ignored=[]):
        ny = y
        for nx in range(x-dx, x+dx+1):
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            d = dist(x,y,nx,ny)
            dg = dgmap[d]
            if dg>0:
                self.update_danger_at(nx, ny, dg, scaled)

        nx = x
        for ny in range(y-dy, y+dy+1):
            if not self.is_onboard(nx,ny):
                continue            
            c=self.BOARD[ny][nx]
            if c in ignored:
                continue
            d = dist(x,y,nx,ny)
            dg = dgmap[d]
            if dg>0:
                self.update_danger_at(nx, ny, dg, scaled)

    def update_danger_cross(self, x, y,  dg, scaled):
        self.update_danger_at(x-1, y-1, dg, scaled)
        self.update_danger_at(x+1, y-1, dg, scaled)
        self.update_danger_at(x-1, y+1, dg, scaled)
        self.update_danger_at(x+1, y+1, dg, scaled)

    #simulation means elements on board after simulated tick
    # simulation: we shifted zombiez, players to simulated postion but they could stay at other and fire
    #             for simplicity check only stay and fire at old 

    def make_dangers_map(self, simulation):
        #make danger map (potential filed like)
        dangers = [ [0]* self.width for _ in range(self.height) ]
        self.DANGERS_MAP = dangers

        if self.ME.is_immortal_nextXmoves(3):
            #river, dangers gives only penalty - I give 3 moves to go away from dangers
            return dangers


        mx = self.ME.X
        my = self.ME.Y
        me_can_fire = self.ME.can_fire()
        m_in_mask = self.ME.is_immortal_nextXmoves(3)

        if mx!=None and my!=None:
            ## Bullets
            for ib in range(self.BULLETS.size()):
                b=self.BULLETS.get(ib)
                dxy = DGS.BULLET_DANGER_DIST.get( b.DIR, None)
                if dxy==None:
                    #print(1)
                    pass
                else:
                    for dx,dy in dxy:
                        nx, ny = b.X+dx, b.Y+dy
                        if not self.is_onboard(nx,ny):
                            continue
                        dg = GAME_CONFIG.DANGER_RATE_DEATH #scaled_danger_me(GAME_CONFIG.DANGER_RATE_DEATH, mx, my, nx, ny)
                        dangers[ny][nx] = max(dangers[ny][nx], dg)


        # players
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.is_dummy():
                continue
            if m_in_mask:
                continue
            c = self.BOARD[p.Y][p.X]

            self.update_danger_dir(p.X, p.Y,  1, 0, 5, GAME_CONFIG.RATE_DEATH//2, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            self.update_danger_dir(p.X, p.Y, -1, 0, 5, GAME_CONFIG.RATE_DEATH//2, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            self.update_danger_dir(p.X, p.Y, 0,  1, 5, GAME_CONFIG.RATE_DEATH//2, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            self.update_danger_dir(p.X, p.Y, 0, -1, 5, GAME_CONFIG.RATE_DEATH//2, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)

            self.update_danger_dir(p.X, p.Y,  1, 0, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            self.update_danger_dir(p.X, p.Y, -1, 0, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            self.update_danger_dir(p.X, p.Y, 0,  1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            self.update_danger_dir(p.X, p.Y, 0, -1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)

            # if c in [ELB.EB_LADDER]: #глюк - на лестнице стреляет!
            #     self.update_danger_dir(p.X, p.Y, 0,  1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            #     self.update_danger_dir(p.X, p.Y, 0, -1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)


        #zombies
        for iz in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(iz)

            if m_in_mask:
                continue

            c = self.BOARD[z.Y][z.X]
            cbelow = self.BOARD[z.Y+1][z.X]
            cleft  = self.BOARD[z.Y][z.X-1]
            cright = self.BOARD[z.Y][z.X+1]

            if c == ELB.EB_LADDER:
                self.update_danger_dir_decayed(z.X, z.Y, 0,  1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
                self.update_danger_dir_decayed(z.X, z.Y, 0, -1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
                self.update_danger_at(z.X-1, z.Y, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED)
                self.update_danger_at(z.X+1, z.Y, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED)
            elif c == ELB.EB_PIPE:
                self.update_danger_dir_decayed(z.X, z.Y,  1, 0, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
                self.update_danger_dir_decayed(z.X, z.Y, -1, 0, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
                self.update_danger_dir_decayed(z.X, z.Y, 0, 1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
            elif c == ELB.EB_ZOMBIE_IN_PIT: #stuck
                    #print("Zombie {} in PIT".format(z.ID))
                    pass
            else:
                if cbelow in MMOVES.PLAYER_CAN_STAY_ON:
                    self.update_danger_dir_decayed(z.X, z.Y,  1, 0, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
                    self.update_danger_dir_decayed(z.X, z.Y, -1, 0, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)
                else: #Falling?
                    self.update_danger_dir_decayed(z.X, z.Y, 0, 1, 2, GAME_CONFIG.RATE_DEATH, GAME_CONFIG.DANGER_SCALED, barrier=MMOVES.PLAYER_BARRIER)


        return dangers


    def make_attack_put_fireline(self, attackmap, targetx, targety, tdir, mindist, maxdist):
        dx, dy = DIR2XY[tdir]
        if dx==0 and dy==0:
            return
        nx, ny = targetx, targety
        for d in range(maxdist+1):
            if not self.is_onboard(nx, ny):
                break
            c = self.BOARD[ny][nx]
            if c in MMOVES.BULLET_BARRIER: 
                break
            if d>=mindist:
                attackmap[ny][nx]+=1
            nx+=dx
            ny+=dy


    def make_attack_of_object(self, attackmap, obj, duel=False, sideattack=None):
        attack = attackmap

        targetx = obj.X
        targety = obj.Y
        targetrot = obj.DIR 
        target_can_fire = obj.can_fire()
        attack_time = 1000

        # if obj.est_killer_id==0: #will be killed by me already - no sense to fire
        #     return
        if obj.est_lifetime!=None:
            attack_time = obj.est_lifetime-1 # at est_lifetime it will die

        mindist = 1
        if target_can_fire:
            mindist =(3,2)[duel]

        maxdist = attack_time*2
        if targetrot==DIR_UNKNOWN: #stayed
            for d in DIR_ALL:
                self.make_attack_put_fireline(attackmap, targetx, targety, d, mindist, maxdist)
        else:
            self.make_attack_put_fireline(attackmap, targetx, targety, targetrot, mindist, maxdist)
            self.make_attack_put_fireline(attackmap, targetx, targety, DIR_REVERSE[targetrot], mindist, maxdist)

            if sideattack!=None:
                for d in DIR_ROT[targetrot]:
                    self.make_attack_put_fireline(attackmap, targetx, targety, d, mindist, sideattack)

            #prediction
            shift = 1
            dt = 2
            dx, dy = DIR2XY[targetrot]

            t=1
            while t<=attack_time:
                newx=targetx+dx
                newy=targety+dy
                if not self.is_onboard(newx,newy):
                    break
                c = self.BOARD[newy][newx]
                if c in MMOVES.PLAYER_BARRIER:
                    #edge case
                    if t==1:
                        for d in DIR_ALL:
                            self.make_attack_put_fireline(attackmap, targetx, targety, d, mindist, 6) #уперся в стенку - на всякие случай можно сбоку бахнуть, если недалеко   
                    break
                # object can be here - make fire points to hit it
                for d in DIR_ROT[targetrot]:
                    self.make_attack_put_fireline(attackmap, newx, newy, d, shift, shift+1)
                targetx, targety = newx, newy
                shift+=dt
                t+=1

    def make_objects_map(self):
        self.OBJECTS_MAP=dict()
        self.OBJECTS_MAP_ID2OBJ=dict()
        if self.ME.is_alive():
            self.OBJECTS_MAP[ (self.ME.X, self.ME.Y) ] = (self.ME.ID, self.ME)
            self.OBJECTS_MAP_ID2OBJ[self.ME.ID] = self.ME
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.is_immortal_nextXmoves(GAME_CONFIG.DO_NOT_ATTACK_IMMORTAL): #do not attack is immortal 
                continue
            self.OBJECTS_MAP[ (p.X, p.Y) ] = (p.ID, p)
            self.OBJECTS_MAP_ID2OBJ[p.ID] = p
        for iz in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(iz)
            self.OBJECTS_MAP[ (z.X, z.Y) ] = (z.ID, z)
            self.OBJECTS_MAP_ID2OBJ[z.ID] = z
        for o in self.OBJECTS_MAP_ID2OBJ.values():
            o.est_killer_id=None
            o.est_lifetime =None
            o.est_is_target=False

    # do ONLY BASE commands !!!!
    def me_do_cmd(self, cmd, logger):
        if cmd==CMDS.CMD_NULL:
            return
        fdir = CMDS.COMMAND_FIRE2DIR(cmd)
        if fdir!=None:
            #bullet at my position 
            if fdir == CMDS.CMD_FIRE:
                # with my direction
                fdir=self.ME.DIR
            logger.log_info("FIRE to {}".format(DIR2STR[fdir]))
            delayed_appear_cnt = (0,1)[fdir!=self.ME.DIR]
            bullet = self.BULLETS.add_custom_bullet(self.ME.X, self.ME.Y, fdir, delayed_appear_cnt) 
            bullet.parent_id = 0 #ME
            logger.log("FIRE BULLET:")
            logger.log_object(bullet)


        dx, dy, mdir = CMDS.COMMAND_BASE_DXYD(cmd)
        if mdir==DIR_SAME:
            mdir = self.ME.DIR

        if self.ME.is_alive():
            self.ME.do_cmd(cmd) #updates only perks counters
            #tree case, estimate move
            nx, ny = self.ME.X+dx, self.ME.Y+dy
            if not self.is_onboard(nx,ny):
                return
            c = self.BOARD[ny][nx]
            if c not in MMOVES.PLAYER_BARRIER:
                self.ME.tick_moved_event(nx, ny, mdir, False)
        self.last_cmd = cmd


    def is_elements_near(self,x,y, els):
        ny = y
        for nx in range(x-1, x+2):
            if not self.is_onboard(nx, ny):
                continue
            c = self.BOARD[ny][nx]
            if c in els:
                return True

        nx = x
        for ny in range(y-1, y+2):
            if not self.is_onboard(nx, ny):
                continue
            c = self.BOARD[ny][nx]
            if c in els:
                return True

        return False

    def get_element_near(self,x,y, els):
        ny = y
        for nx in range(x-1, x+2):
            if not self.is_onboard(nx, ny):
                continue
            c = self.BOARD[ny][nx]
            if c in els:
                return (nx,ny,c)

        nx = x
        for ny in range(y-1, y+2):
            if not self.is_onboard(nx, ny):
                continue
            c = self.BOARD[ny][nx]
            if c in els:
                return (nx,ny,c)

        return None

    def hit_distance(self, sx, sy, sfire, tx, ty):
        dirs = [sfire]
        if sfire==DIR_UNKNOWN:
            dirs = DIR_ALL
        res = None
        for d in dirs:
            dx, dy = DIR2XY[d]
            if dx==0 and sx!=tx:
                continue
            if dy==0 and sy!=ty:
                continue
            if (dx<0 and tx>sx) or (dx>0 and tx<sx):
                continue
            if (dy<0 and ty>sy) or (dy>0 and ty<sy):
                continue
            nx, ny = sx, sy
            dst=0
            while True:
                nx+=dx
                ny+=dy
                dst+=1
                if not self.is_onboard(nx, ny):
                    break
                c = self.BOARD[ny][nx]
                if c in EL.ELS_BULLET_BARRIER:
                    break
                if (nx==tx and ny==ty) and (res==None or dst<res):
                    res=dst
                    break
        return res


    def bullets_before_start(self):
        return 

    def perks_before_start(self):
        return 
    
    def players_before_start(self):
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            p.store_last_pos()

    def zombies_before_start(self):
        for iz in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(iz)
            z.store_last_pos()
        return 
    
    def me_before_start(self):
        self.ME.store_last_pos()
        return 

    def player_calc_possible_moves(self, px, py):
        return set()
    
    def moves_map_remove_move(self, pmap, elx, ely, target_dir, target_move):
        dx, dy = DIR2XY[target_dir]
        tx, ty = elx+dx, ely+dy
        if not self.is_onboard(tx, ty):
            return False
        pmap[ty][tx].discard(target_move)
        return True

    def make_possible_moves_map(self):
        # two methods:
        # - allow all and then disable frobidden iterating obstacles <-
        # - disable all and iterarting cells check for possible moves
        width, height = self.width, self.height
        self.PLAYER_POSSIBLE_DIRS  = pmap = [ [set(PLAYER_TRACK_POSSIBLE_DIRS) for x in range(width)] for y in range(height) ]
        self.PLAYER_POSSIBLE_MOVES = mmap = [ [set() for x in range(width)] for y in range(height) ]
        
        #boundaries
        for x in range(width):
            pmap[0][x].discard(DIR_LEFT)
            pmap[height-1][x].discard(DIR_RIGHT)
        for y in range(height):
            pmap[y][0].discard(DIR_UP)
            pmap[y][width-1].discard(DIR_DOWN)

        # first remove
        for y in range(height):
            for x in range(width):
                # if y==self.ME.Y and x==self.ME.X:
                #     print(1)
                c = self.BOARD[y][x]
                if c==ELB.EB_WALL:
                    pmap[y][x] = set() #
                if c in MMOVES.PLAYER_BARRIER:
                    self.moves_map_remove_move(pmap, x,y, DIR_LEFT,  DIR_RIGHT)
                    self.moves_map_remove_move(pmap, x,y, DIR_RIGHT, DIR_LEFT)
                    self.moves_map_remove_move(pmap, x,y, DIR_UP,    DIR_DOWN)
                    self.moves_map_remove_move(pmap, x,y, DIR_DOWN,  DIR_UP)
                    pmap[y][x].discard(DIR_UP)
                if c in MMOVES.PLAYER_FALL_STAYING_ON: 
                    nx, ny = x, y-1
                    if self.is_onboard(nx, ny):
                        nc = self.BOARD[ny][nx]
                        if nc not in MMOVES.PLAYER_NOT_FALL:
                            pmap[ny][nx] &= {DIR_DOWN}
                if c in MMOVES.PLAYER_NOT_UP:
                    pmap[y][x].discard(DIR_UP)

        #then add
        for y in range(height):
            for x in range(width):
                c = self.BOARD[y][x]
                if c == ELB.EB_LADDER:
                    nx, ny = x, y-1
                    if self.is_onboard(nx, ny):
                        nc = self.BOARD[ny][nx]
                        if nc in MMOVES.PLAYER_FREE2GO:
                            pmap[y][x].add(DIR_UP)
                
                if c == ELB.EB_PIPE:
                    for nx, ny, dd in [ (x-1,y, DIR_LEFT), (x+1,y, DIR_RIGHT) ]:
                        if self.is_onboard(nx, ny):
                            nc = self.BOARD[ny][nx]
                            if nc in MMOVES.PLAYER_FREE2GO:
                                pmap[y][x].add(dd)

        ######################################################################################################
        #make moves from dirs
        for y in range(height):
            for x in range(width):
                dirs = pmap[y][x]
                res   = set()
                for d in dirs:
                    # if d==DIR_STOP:
                    #     continue
                    cmds = MMOVES.PLAYER_DIR2COMMANDS[d]
                    for m in cmds:
                        if m in [ CMDS.CMD_FIRE_FLOOR_LEFT, CMDS.CMD_FIRE_FLOOR_LEFT_GO ]:
                            nc1 = self.get_board_item(x-1, y+1)
                            nc2 = self.get_board_item(x-1, y)
                            if nc1 in [ELB.EB_BRICK] and nc2 not in MMOVES.BULLET_CANT_HIT_UNDER and not self.ZOMBIES.is_at(x-1, y) and not self.PERKS.is_at(x-1,y):
                                res.add(m)
                        elif m in [ CMDS.CMD_FIRE_FLOOR_RIGHT, CMDS.CMD_FIRE_FLOOR_RIGHT_GO ]:
                            nc1 = self.get_board_item(x+1, y+1)
                            nc2 = self.get_board_item(x+1, y)
                            if nc1 in [ELB.EB_BRICK] and nc2 not in MMOVES.BULLET_CANT_HIT_UNDER and not self.ZOMBIES.is_at(x+1, y) and not self.PERKS.is_at(x+1,y):
                                res.add(m)
                        else:
                            res.add(m)
                mmap[y][x] = res
#        print(10)    

    def player_is_falling(self, px, py):
        # if not self.is_onboard(nx, ny):
        #     return False
        # players is falling if in air and nothing under feets
        c = self.BOARD[py][px]
        cunder = self.BOARD[py+1][px]
        if c in MMOVES.PLAYER_FALL_IF_IN:
            if cunder not in MMOVES.PLAYER_CAN_STAY_ON:
                return True
        return False

    #flat, nt in cube< for short distances make sense only
    def bullet_can_hit_player_dist(self, x, y, dx, dy, dmax, notFireTwice=True):
        ny = y
        nx = x
        if notFireTwice and self.BULLETS.get_at(nx,ny):
            return None
        for i in range(dmax):
            ny+=dy
            nx+=dx
            if not self.is_onboard(nx,ny):
                break
            c=self.BOARD[ny][nx]
            if c in MMOVES.BULLET_BARRIER:
                break
            player_here = self.PLAYERS.get_at(nx, ny)
            if player_here: #first ch
                return i
            bullet_here = notFireTwice and self.BULLETS.get_at(nx,ny)
            if bullet_here:
                break
        return None

    def target_already_under_attack(self, x, y, fdir, targetX, targetY, dmax=30):
        ny = y
        nx = x
        dx, dy = DIR2XY[fdir]

        dd = max(targetX-x,targetY-y)
        dd = min(dd, dmax)
        for i in range(dd):
            ny+=dy
            nx+=dx
            if not self.is_onboard(nx,ny):
                break
            c=self.BOARD[ny][nx]
            if c in MMOVES.BULLET_BARRIER:
                break
            bul = self.BULLETS.get_at(nx, ny)
            if bul!=None:
                if (bul.DIR==fdir or bul.DIR==DIR_UNKNOWN):
                    return True
        return False

    def bullet_can_hit_target_dist(self, x, y, targetX, targetY, cmd, maxdist, checkIfNear=False):
        nx, ny = x, y
        fdir = CMDS.COMMAND_FIRE2DIR(cmd)
        if fdir==None:
            return None

        dx, dy = DIR2XY[fdir]
        for d in range(1, maxdist+1):
            ny+=dy
            nx+=dx
            if not self.is_onboard(nx,ny):
                break
            c=self.BOARD[ny][nx]
            if c in MMOVES.BULLET_BARRIER:
                break
            if nx==targetX and ny==targetY:
                return d
            dH = abs(nx-targetX)
            dV = abs(ny-targetY)
            if checkIfNear:
                if (dH==0 and dV==1) or (dH==1 and dV==0):
                    return d+1
        return None

    def player_to_target_hit_cmds(self, px, py, tx, ty, maxdist=30, checkIfNear=False):
        cmd_fires = set(self.PLAYER_POSSIBLE_MOVES[py][px])
        cmd_fires = cmd_fires & {CMDS.CMD_FIRE_LEFT, CMDS.CMD_FIRE_RIGHT, CMDS.CMD_FIRE_UP, CMDS.CMD_FIRE_DOWN}
        res = []
        for cmd in cmd_fires:
            dst_hit = self.bullet_can_hit_target_dist(px, py, tx, ty, cmd, maxdist, checkIfNear)
            if dst_hit!=None:
                res.append( (cmd,dst_hit) )
        return res

    def is_only_one_dummy_player_left(self):
        cnt = 0
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.is_dummy():
                cnt+=1
            else:
                return False
        return cnt==1

    def is_only_one_player_left(self):
        cnt = 0
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.is_alive():
                cnt+=1
        return cnt==1
        

if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
