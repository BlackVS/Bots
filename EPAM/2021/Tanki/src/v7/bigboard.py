#! /usr/bin/env python3

import element as EL
import json
import copy
from math import sqrt
from element import *
from config import *
from trackobjects_custom import *
from perks import *
from game_rates import *
from logger import *
import game_rates as GAME_CONFIG

def print_input(data):
    if not DEBUG:
        return
    w = h = int(sqrt(len(data)))  # size of the board 
    for i in range(h):
        LOG("{:2} : {}".format(i,data[i*w: (i+1)*w]))


def dist(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)


def scaled_danger(dg, d):
    if d<=DANGER_DIST_RADIUS:
        return dg
    res = dg - ((d - DANGER_DIST_RADIUS)*dg)//DANGER_DIST_DECAY
    return max(0, res)

def scaled_danger_me(dg, mx, my, x, y):
    if mx==None or my==None:
        return dg #not scale if me hidden
    d = dist(mx, my, x, y)
    if d<=DANGER_DIST_RADIUS:
        return dg
    res = dg - ((d - DANGER_DIST_RADIUS)*dg)//DANGER_DIST_DECAY
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
    last_cmd = CMD_NULL

    counter = 0 #just to track in logs


    #global board
    BOARD_STR = None

    BOARD     = None #non-movable elements of board i.e. walls, laser guns, exits, starts etc
    DANGERS_MAP = None
    ATTACK_MAP_AI  = None
    ATTACK_MAP_OTHER = None

    # Objects

    ## Players
    ME          = TPlayer(ETANK_TYPE_ME)

    # PERKS = []      # x y

    ZOMBIES = TPlayers(ETANK_TYPE_AI)
    PLAYERS = TPlayers(ETANK_TYPE_OTHER)
    BULLETS = TBullets()
    PERKS   = Perks()

    HAS_PLAYERS = False
    HAS_ZOMBIES = False

    ### GLOBAL STORAGE
    global_board_idx = None

    #PERKS

    #HISTORY
    OBJECTS_MAP        = dict()
    OBJECTS_MAP_ID2OBJ = dict()
    OBJECTS_MAP_PREV   = dict()

    def __init__(self):
        self.width  = 0
        self.height = 0

    def is_game_start(self):
        return self.last_string_same_cnt>=4

    def cleanup(self):
        global IDXCNT
        IDXCNT = 1

        reset_tracking()

        #not reset width due to the same
        #self.width  = 0 
        #self.height = 0
        #self.BOARD      = None #non-movable elements of board i.e. walls, laser guns, exits, starts etc
        self.BOARD = [ [EL.ESPACE] * self.width for _ in range(self.height) ]

        self.ME         = TPlayer(ETANK_TYPE_ME)
        self.ZOMBIES    = TPlayers(ETANK_TYPE_AI)
        self.PLAYERS    = TPlayers(ETANK_TYPE_OTHER)
        self.BULLETS    = TBullets()
        self.PERKS = Perks()

        self.HAS_PLAYERS = False
        self.HAS_ZOMBIES = False
        self.global_board_idx= None


        self.OBJECTS_MAP        = dict()
        self.OBJECTS_MAP_PREV   = dict()

        self.last_cmd = CMD_NULL


    def clone(self, t):
        res = BigBoard()
        res.width       = self.width
        res.height      = self.height
        #res.BOARD       = copy.deepcopy(self.BOARD)
        res.BOARD       = self.BOARD #static elements are the same all the time (supposed %)
        res.ME          = copy.deepcopy(self.ME)
        res.HAS_PLAYERS = self.HAS_PLAYERS 
        res.HAS_ZOMBIES = self.HAS_ZOMBIES 
        res.ZOMBIES = copy.deepcopy(self.ZOMBIES) #movable object
        res.PLAYERS = copy.deepcopy(self.PLAYERS) #movable object
        res.BULLETS = copy.deepcopy(self.BULLETS) #movable object

        #res.PERKS   = copy.deepcopy(self.PERKS)
        res.PERKS   = self.PERKS.clone()

        #will be recreated
        if t==0:
            res.OBJECTS_MAP = copy.deepcopy(self.OBJECTS_MAP) #movable object
            res.OBJECTS_MAP_PREV = copy.deepcopy(self.OBJECTS_MAP_PREV) #movable object
        return res


    def resize(self, new_width, new_height):
        if self.BOARD == None or new_width > self.width or new_height > self.height:

            new_width  = max(new_width,  self.width)
            new_height = max(new_height, self.height)

            board     = [ [EL.ESPACE] * new_width for _ in range(new_height) ]
            if self.BOARD:
                for y in range(self.height):
                    for x in range(self.width): #to-do: via slice copying
                        board[y][x]    =self.BOARD[y][x]

            self.BOARD=board
            self.width  = new_width
            self.height = new_height

    def is_onboard(self,x,y):
        return x>=0 and y>=0 and x<self.width and y<self.height

    #try detect parents of bullets
    def bullets_after_finish(self):
        for ib in range(self.BULLETS.size()):
            b=self.BULLETS.get(ib)
            if b.direction!=DIR_UNKNOWN:
                continue
            #try detect rotation - check all old neighbours
            NXY = [ (0,1), (0,-1), (1,0), (-1,0), (0,2), (0,-2), (2,0), (-2,0)]
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
                b.direction = dxy2dir( pdx, pdy )
                pobj.event_just_fired()
                LOG("JUST FIRED ID={} gun_cnt={}".format(pid, pobj.shot_counter))

    def perks_after_finish(self,perks_old):
        if self.ME.is_alive:
            perk = perks_old.get_perk_at(self.ME.X, self.ME.Y)
            if perk!=None:
                self.ME.got_perk( perk.perk_type )
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            perk = perks_old.get_perk_at(p.X, p.Y)
            if perk!=None:
                p.got_perk( perk )
        
    def players_after_finish(self):
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if self.BOARD[p.Y][p.X] == EICE:
                p.moved_on_ice(True)
            else:
                p.moved_on_ice(False)

    def zombies_after_finish(self):
        for ip in range(self.ZOMBIES.size()):
            p=self.ZOMBIES.get(ip)
            if self.BOARD[p.Y][p.X] == EICE:
                p.moved_on_ice(True)
            else:
                p.moved_on_ice(False)

    def me_after_finish(self):
        p=self.ME
        if p==None or p.X==None or p.Y==None:
            return
        if self.BOARD[p.Y][p.X] == EICE:
            p.moved_on_ice(True)
        else:
            p.moved_on_ice(False)

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

    def update_from(self, input):
        LOG("===================================================================================")
        LOG("CNT = {}".format(BigBoard.counter))
        LOG("===================================================================================")
        BigBoard.counter+=1

        
        board_str = input.replace('\n', '')

        levelFinished = False
        if board_str==self.last_string:
            self.last_string_same_cnt +=1
        else:
            self.last_string_same_cnt = 0
            self.last_string = board_str
        self.BOARD_STR=board_str


        if self.last_string_same_cnt>3:
            levelFinished = True
            print("!!!RESET!!!")


        print_input(board_str)

        c1 = set(board_str)

        has_me      = c1 & set(ELS_TANK_ME)
        has_players = c1 & set(ELS_TANKS_OTHER)
        has_zombies = c1 & set(ELS_TANKS_AI)

        if levelFinished:
            self.cleanup()
            #return False #- not return to not miss

        if not has_me: #could be hidden
            pass #already do_cmd before


        w  = h = int(sqrt(len(board_str)))  # size of the board 

        self.bullets_before_start()
        self.perks_before_start()
        self.players_before_start()
        self.zombies_before_start()
        self.me_before_start()

        #tick
        self.PLAYERS.tick()
        self.ZOMBIES.tick()
        self.PERKS.tick()
        
        ####
        self.OBJECTS_MAP_PREV = self.OBJECTS_MAP
        


        self.resize( w, h )
        
        self.reset_stats()
        
        self.BULLETS.tracking_init(self.width, self.height)
        self.ZOMBIES.tracking_init(self.width, self.height)
        self.PLAYERS.tracking_init(self.width, self.height)
        self.PERKS.tracking_start(self.width, self.height)

        perks_old = copy.deepcopy(self.PERKS)
        self.update_layer(board_str)

        self.ZOMBIES.tracking_finish()

        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.updated:
                continue
            if p.est_in_tree>10:
                p.est_in_tree=0
                continue
            tr = self.get_element_near(p.X, p.Y, [ETREE])
            if tr==None:
                continue
            tx, ty, tt = tr[0], tr[1], tr[2]
            p.moved(tx,ty,p.rotation,True)
            p.updated=True
            p.est_in_tree+=1

        self.PLAYERS.tracking_finish()
        self.BULLETS.tracking_finish()
        self.PERKS.tracking_finish()

        #after finish tracking 
        self.make_objects_map()

        self.bullets_after_finish()
        self.perks_after_finish(perks_old)
        self.players_after_finish()
        self.zombies_after_finish()
        self.me_after_finish()

        self.make_dangers_map(False)
        #self.make_attack_map() - in cube!!!

        return True

    def reset_stats(self):
        self.HAS_PLAYERS = False
        self.HAS_ZOMBIES = False


        

    def update_layer(self, data_string):
        w  = int(sqrt(len(data_string)))
        
        for y in range(w):
            for x in range(w):
                c = data_string[y*w+x]

                if c in ELS_DESTROYED_WALLS:
                    c = EDESTROYED_WALLS_MAP[c]

                if c in EL.ESTATIC_ELEMENTS:
                    self.BOARD[y][x]=c


                #players
                if c in EL.ELS_TANK_ME:
                    self.ME.moved(x, y, EL.TANK2DIR[c], False)
                    self.ME.set_alive(True)

                if c in EL.ELS_TANKS_OTHER:
                    self.PLAYERS.tracking_add_object(x, y, TANK2DIR[c])
                    self.HAS_PLAYERS=True

                if c in EL.ELS_TANKS_AI:
                    obj=self.ZOMBIES.tracking_add_object(x, y, TANK2DIR[c])
                    obj.ai_has_perk = c == EAI_TANK_PRIZE
                    self.HAS_ZOMBIES=True
                    #masks perks
                    self.PERKS.perk_could_be_masked(x,y)
            
                if c == EBANG: #could be!
                    obj=self.ZOMBIES.tracking_could_be_object(x, y, DIR_UNKNOWN)
                    self.HAS_ZOMBIES=obj!=None

                if c == EBULLET:
                    self.BULLETS.tracking_add_object(x,y)

                if c in ELS_PERKS: 
                    self.PERKS.perk_found(x,y,c)


                


    def print(self, title=None):
        if not DEBUG:
            return

        #board 

        res = []
        for y in range(self.height):
            r = copy.copy(self.BOARD[y])
            res.append( r )

        for iz in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(iz)
            res[z.Y][z.X] = DIR2TANK_AI[z.rotation]

        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if ip==0:
                res[p.Y][p.X] = DIR2TANK[p.rotation]
            else:
                res[p.Y][p.X] = DIR2TANK_OTHER[p.rotation]

        for ib in range(self.BULLETS.size()):
            b=self.BULLETS.get(ib)
            res[b.Y][b.X] = EBULLET

        #FILELOG
        if title:
            LOGF(title)
        for r in res:
            LOGF("".join( r))
        #print players, zombies, shots
        for i in range(self.PLAYERS.size()):
            p = self.PLAYERS.get(i)
            LOGF("PLAYER id={} x={} y={} fly={}".format(p.ID,p.X,p.Y,p.rotation))

        for i in range(self.ZOMBIES.size()):
            z = self.ZOMBIES.get(i)
            LOGF("ZOMBIE id={} x={} y={}".format(z.ID,z.X,z.Y))

        for i in range(self.BULLETS.size()):
            z = self.BULLETS.get(i)
            LOGF("BULLET id={} x={} y={}".format(z.ID,z.X,z.Y))

        LOGF("\n")


    def tick_bullets(self):
        to_remove = []
        for i in range(self.BULLETS.size()):
            b = self.BULLETS.get(i)
            if b.direction == DIR_UNKNOWN:
                continue
            for j in range(2):
                b.tick()
                if not self.is_onboard(b.X, b.Y):
                    to_remove.append(i)
                    continue
                c = self.BOARD[b.Y][b.X]
                if c in ELS_BULLET_BARRIER:
                    b.toremove=True
        self.BULLETS.remove()


    def tick_AIs(self):
        self.ZOMBIES.tick() #update perks
        for i in range(self.ZOMBIES.size()):
            z = self.ZOMBIES.get(i)
            if z.rotation == DIR_UNKNOWN:
                continue #
            nres, nx, ny = z.estimate_next_pos()
            if not nres:
                continue
            if not self.is_onboard(nx,ny):
                continue
            c = self.BOARD[ny][nx]
            if c not in ELS_AI_BARRIER:
                z.moved(nx, ny, z.rotation, False)
            else:
                z.rotation=DIR_UNKNOWN #don't know where will go
                z.est_is_stuck = True #to reduce profit from hitting it
            

    def tick(self):
        self.tick_bullets()
        self.PLAYERS.tick()
        self.tick_AIs()
        self.PERKS.tick()
        self.ME.tick()

    def tick0(self):
        pass
      

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

    # def update_danger_around(self, x, y, dx, dy, dmap, dexclude, scaled):
    #     for nx in range(x-dx, x+dx+1):
    #         for ny in range(y-dy, y+dy+1):
    #             if not self.is_onboard(nx,ny):
    #                 continue
    #             c=self.BOARD[ny][nx]
    #             if c in dexclude:
    #                 continue
    #             d = dist(x,y,nx,ny)
    #             dg = dmap[d]
    #             if dg>0:
    #                 self.update_danger_at(nx, ny, dg, scaled)

    #simulation means elements on board after simulated tick
    # simulation: we shifted zombiez, players to simulated postion but they could stay at other and fire
    #             for simplicity check only stay and fire at old 

    def make_dangers_map(self, simulation):
        #make danger map (potential filed like)
        dangers = [ [0]* self.width for _ in range(self.height) ]
        self.DANGERS_MAP = dangers

        if self.ME.is_immortal(3):
            #river, dangers gives only penalty - I give 3 moves to go away from dangers
            return dangers


        mx = self.ME.X
        my = self.ME.Y
        me_can_fire = self.ME.can_fire()

        ## Bullets
        for ib in range(self.BULLETS.size()):
            b=self.BULLETS.get(ib)
            dxy = DIRBULLET_DANGER[b.direction]
            for dx,dy in dxy:
                nx, ny = b.X+dx, b.Y+dy
                if not self.is_onboard(nx,ny):
                    continue
                dg = scaled_danger_me(DANGER_RATE_DEATH, mx, my, nx, ny)
                dangers[ny][nx] = max(dangers[ny][nx], dg)


        #players
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.not_moving_long():
                continue
            if p.can_fire():
                # dhit = p.hit_distance(p.X, p.Y, DIR_UNKNOWN, mx, my)
                # if dhit!=None and me_can_fire:
                #     # self.update_danger_HV(p.X, p.Y, 2, 2, DANGER_RATE_PLAYER_CAN_FIRE//2, DANGER_SCALED)
                #     pass
                # else:
                
                #self.update_danger_cross(p.X, p.Y, DANGER_RATE_PLAYER_CAN_FIRE, DANGER_SCALED)
                self.update_danger_HV(p.X, p.Y, 2, 2, DANGER_RATE_PLAYER_CAN_FIRE, DANGER_SCALED)
            if simulation and p.could_fire():
                #self.update_danger_cross(p.X, p.Y, DANGER_RATE_PLAYER_CAN_FIRE, DANGER_SCALED)
                self.update_danger_HV(p.PX, p.PY, 2, 2, DANGER_RATE_PLAYER_COULD_FIRE, DANGER_SCALED)

        #zombies
        for iz in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(iz)
            if z.can_fire():
                # dhit = self.hit_distance(z.X, z.Y, DIR_UNKNOWN, mx, my)
                # if dhit!=None and me_can_fire:
                #     #self.update_danger_HV(z.X, z.Y, 2, 2, DANGER_AI_SIDEATTACK//2, DANGER_SCALED)
                #     pass
                # else:
                self.update_danger_HV(z.X, z.Y, 2, 2, DANGER_AI_SIDEATTACK, DANGER_SCALED)
            if GAME_CONFIG.ZOMBIE_CAN_CHANGE_DIRECTION:
                if simulation and z.could_fire():
                    self.update_danger_HV(z.PX, z.PY, 2, 2, DANGER_AI_SIDEATTACK_SIMULATION, DANGER_SCALED)


        #grass, river, ice
        for y in range(self.height):
            for x in range(self.width): 
                c = self.BOARD[y][x]
                if c == ETREE:
                    self.update_danger_HV_MAP(x, y, 2, 2, DANGER_TREEN_MAP, DANGER_SCALED, [ETREE])
                if c == EICE:
                    self.update_danger_at(x, y, DANGER_ICE, False)


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
            if c in ELS_BULLET_BARRIER: #PERKS!!!!!
                break
            if d>=mindist:
                attackmap[ny][nx]+=1
            nx+=dx
            ny+=dy


    def make_attack_of_object(self, attackmap, obj, duel=False, sideattack=None):
        attack = attackmap

        targetx = obj.X
        targety = obj.Y
        targetrot = obj.rotation 
        target_can_fire = obj.can_fire()
        attack_time = 1000

        if obj.est_killer_id==0: #will be killed by me already - no sense to fire
            return
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
                if c in ELS_PLAYER_NO_MOVES:
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
            

    def make_attack_map2(self):
        self.ATTACK_MAP_AI    = [ [0]* self.width for _ in range(self.height) ]
        self.ATTACK_MAP_OTHER = [ [0]* self.width for _ in range(self.height) ]

        for iz in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(iz)
            self.make_attack_of_object(self.ATTACK_MAP_AI, z, FORCE_DUEL)

        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.is_immortal(DO_NOT_ATTACK_IMMORTAL): #do not attack is immortal 
                continue
            self.make_attack_of_object(self.ATTACK_MAP_OTHER, p, FORCE_DUEL, 6)

    def make_objects_map(self):
        self.OBJECTS_MAP=dict()
        self.OBJECTS_MAP_ID2OBJ=dict()
        if self.ME.alive:
            self.OBJECTS_MAP[ (self.ME.X, self.ME.Y) ] = (self.ME.ID, self.ME)
            self.OBJECTS_MAP_ID2OBJ[self.ME.ID] = self.ME
        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            if p.is_immortal(DO_NOT_ATTACK_IMMORTAL): #do not attack is immortal 
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

    def me_do_cmd(self, cmd, logger):
        dir = DIR_UNKNOWN
        if cmd in COMMANDS_FIRE:
            #bullet at my position
            if cmd == CMD_FIRE:
                dir=self.ME.rotation
            else:
                dir=MAP_COMMANDS_FIRE2DIR[cmd]
            logger.log_info("FIRE to {}".format(DIRECTIONS[dir]))
            bullet = self.BULLETS.add_custom_bullet(self.ME.X, self.ME.Y, dir) 
            bullet.parent_id = 0 #ME
            logger.log("FIRE BULLET:")
            logger.log_object(bullet)
        elif cmd==CMD_STOP:
            dir = self.ME.rotation
        else:
            dir = COMMANDS2DIR[cmd]

        if self.ME.alive:
            self.ME.do_cmd(cmd) #updates only perks counters
            #tree case, estimate move
            dx, dy, fire = COMMANDS_XYF[cmd]
            nx, ny = self.ME.X+dx, self.ME.Y+dy
            if not self.is_onboard(nx,ny):
                return
            c = self.BOARD[ny][nx]
            if c not in ELS_PLAYER_NO_MOVES:
                self.ME.moved(nx, ny, dir, False)
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
                if c in ELS_BULLET_BARRIER:
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
    


if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
