#! /usr/bin/env python3

import element as EL
import json
import copy
from math import sqrt
from player import *
from element import *
from config import *
from trackobjects import *
from game_rates import *
from logger import *

IDXCNT = 1


def print_input_json(data):

    if not DEBUG:
        return
    for k,v in data.items():
        if k!='layers':
            LOGF("{} :{}".format(k,v))

    layers=[]
    w = int(sqrt(len(data['layers'][0])))
    for l in data['layers']:
        layers.append( [l[i*w:(i+1)*w] for i in range(w)])

    #Short
    # for j in range(w):
    #     LOGF( "{}  {}  {}".format(
    #         layers[0][j], 
    #         layers[1][j], 
    #         layers[2][j], 
    #         )
    #     )

    ### TO FILE
    for k,v in data.items():
        if k!='layers':
            LOGF("{} :{}".format(k,v))

    layers=[]
    w = int(sqrt(len(data['layers'][0])))
    for l in data['layers']:
        layers.append( [  l[i*w:(i+1)*w] for i in range(w)])
    for j in range(w):
        LOGF( "{}  {}  {}".format(
            layers[0][j], 
            layers[1][j], 
            layers[2][j], 
            )
        )

def dist(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)

def scaled_danger(dg, d):
    if d<=DANGER_DIST_RADIUS:
        return dg
    res = dg - ((d - DANGER_DIST_RADIUS)*dg)//DANGER_DIST_DECAY
    return max(0, res)

def scaled_danger_zombie(dg, d):
    if d<=DANGERZ_DIST_RADIUS:
        return dg
    res = dg - ((d - DANGERZ_DIST_RADIUS)*dg)//DANGERZ_DIST_DECAY
    return max(0, res)

class TPlayer(TObject):
    flying = False
    alive  = True
    
    def __init_(self, flying=False, alive=True):
        self.flying = flying
        self.alive  = alive
        super.__init__()

    def custom_update_from(self, object):
        self.flying = object.flying
        self.alive  = object.alive

    def estimate_next_pos(self):
        if self.flying and self.PX!=None and self.PY!=None:
            dx, dy = self.X-self.PX, self.Y-self.PY
            return (True, self.X+dx, self.Y+dy)
        return (None, None, None) # (estimated, x, y)


class TPlayers(TObjects):

    def __init__(self):
        #super().__init__() - static object, not called
        self.cleanup()

    #CUSTOM METHODS
    def object_new(self):
        return TPlayer()



class BoardsStorage:
    storage = None
    IDXCNT  = 0

    def __init__(self):
        self.storage=dict()
        self.load()

    def normalize(self, board):
        for y in range(len(board)):
            for x in range(len(board[0])):
                b = board[y][x]
                if b in ELASER_GUN:
                    board[y][x] = ELASER_GUN_STATIC[b]
                if b in ELASER_SHOTS:
                    board[y][x] = EFLOOR
                if b in [EBOX]:
                    board[y][x] = EFLOOR

    def store(self, board):
        global_board = copy.deepcopy(board)
        self.normalize(global_board)
        self.storage[self.IDXCNT] = global_board
        self.IDXCNT+=1
        self.save()

    def update(self, bidx, board):
        global_board = copy.deepcopy(board)
        self.normalize(global_board)
        self.storage[bidx] = global_board
        self.save()

    def save(self):
        if GLOBAL_BOARDS_FILE and self.storage:
            with open(GLOBAL_BOARDS_FILE, "wt+", encoding='utf-8') as f:
                for id,brd in self.storage.items():
                    f.write("{} {}\n".format(len(brd),len(brd[0])))
                    for bb in brd:
                        f.write("".join(bb))
                        f.write("\n")

    def load(self):
        try:
            with open(GLOBAL_BOARDS_FILE, "rt", encoding='utf-8') as f:
                text = f.readlines()
                il = 0
                while il<len(text):
                    h, w = text[il].split()
                    il+=1
                    h=int(h)
                    w=int(w)
                    brd = [ [EUNKNOWN]*w for _ in range(h)]
                    for y in range(h):
                        s = text[il].rstrip("\n")
                        il+=1
                        if len(s)!=w:
                            LOG("BROKEN GLOBAL BOARDS FILE!!!!")
                            return
                        for x in range(w):
                            c = s[x]
                            if c in [EBOX]: #ignore
                                c=EFLOOR
                            brd[y][x]=s[x]
                    self.store(brd)
        except:
            print("No global map storage found!!!")
            pass


    def count_commons(self, brd, fx, fy, fragment):
        cnt = 0
        
        bw = len(brd[0])
        bh = len(brd)
        fw = len(fragment[0])
        fh = len(fragment)

        dw = min(fw, bw-fx)
        dh = min(fh, bh-fy)

        for oy in range(dh):
            for ox in range(dw):
                cf = fragment[oy][ox]
                cb = brd[fy+oy][fx+ox]
                if cb in [EBOX]:
                    cb = EFLOOR
                if cf in ESTATIC_ELEMENTS+ELASER_GUN and cf == cb:
                    cnt+=1
                # else:
                #     print(cf, cb)
        return (cnt*100)//(fw*fh)


    def search(self, bx, by, fragment):
        for id,brd in self.storage.items():
            if self.count_commons(brd, bx, by, fragment)>=90:
                return (id,brd)
        return (None,None)

global_storage = BoardsStorage()

class BigBoard:
    width  = 0
    height = 0

    counter = 0 #just to track in logs

    #global board

    BOARD     = None #non-movable elements of board i.e. walls, laser guns, exits, starts etc
    BOARD_IDS = None #ids of objects placed on board (laser guns)
    DANGERS_MAP = None
    ATTACK_MAP  = None
    VISIBILITY_MAP = None


    STARTS = set()
    ENDS   = set()

    # Objects

    ## Players
    ME      = Player(0)
    MYSTART = None

    # PERKS = []      # x y

    LASERSHOTS = []     # x y charging 

    ZOMBIES = TObjects()
    PLAYERS = TPlayers()

    HAS_GOLD    = False
    HAS_EXITS   = False
    HAS_PLAYERS = False
    HAS_ZOMBIES = False

    ### GLOBAL STORAGE
    global_board_idx = None

    ##LASER_GUN tracking
    lgun_counter     = 0
    lgun_counter_max = None
    lgun_counter_dt  = 0
    lgun_ready       = False


    #PERKS
    PERKS = dict()

    def __init__(self):
        self.width  = 0
        self.height = 0

    def cleanup(self):
        global IDXCNT
        IDXCNT = 1

        self.width  = 0
        self.height = 0
        self.BOARD      = None #non-movable elements of board i.e. walls, laser guns, exits, starts etc
        self.BOARD_IDS  = None #ids of objects placed on board (laser guns)
        self.STARTS     = set()
        self.ENDS       = set()
        self.ME         = Player(0)
        self.LASERSHOTS = []
        self.ZOMBIES    = TObjects()
        self.PLAYERS    = TPlayers()
        self.HAS_GOLD    = False
        self.HAS_EXITS   = False
        self.HAS_PLAYERS = False
        self.HAS_ZOMBIES = False
        self.global_board_idx= None

        self.lgun_counter     = 0
        self.lgun_counter_dt  = 0
        self.lgun_ready       = False
        #???? if same for all maps - don't cleanup max!!!
        self.lgun_counter_max = None

        self.PERKS = dict()

    def clone(self):
        res = BigBoard()
        res.width       = self.width
        res.height      = self.height
        #res.BOARD       = copy.deepcopy(self.BOARD)
        #res.BOARD_IDS   = copy.deepcopy(self.BOARD_IDS)
        res.BOARD       = self.BOARD #static elements are the same all the time (supposed %)
        res.STARTS      = self.STARTS
        res.ENDS        = self.ENDS
        res.ME          = copy.deepcopy(self.ME)
        res.LASERSHOTS  = copy.deepcopy(self.LASERSHOTS) #movable object
        res.HAS_GOLD    = self.HAS_GOLD
        res.HAS_EXITS   = self.HAS_EXITS
        res.HAS_PLAYERS = self.HAS_PLAYERS 
        res.HAS_ZOMBIES = self.HAS_ZOMBIES 
        res.ZOMBIES = copy.deepcopy(self.ZOMBIES) #movable object
        res.PLAYERS = copy.deepcopy(self.PLAYERS) #movable object

        res.lgun_counter        = self.lgun_counter
        res.lgun_counter_dt     = self.lgun_counter_dt
        res.lgun_ready          = self.lgun_ready
        res.lgun_counter_max    = self.lgun_counter_max

        res.ATTACK_MAP          = self.ATTACK_MAP
        res.PERKS               = self.PERKS
        return res


    def resize(self, new_width, new_height):
        if self.BOARD == None or new_width > self.width or new_height > self.height:

            new_width  = max(new_width,  self.width)
            new_height = max(new_height, self.height)

            board     = [ [EL.EUNKNOWN] * new_width for _ in range(new_height) ]
            if self.BOARD:
                for y in range(self.height):
                    for x in range(self.width): #to-do: via slice copying
                        board[y][x]    =self.BOARD[y][x]

            visi = [ [0] * new_width for _ in range(new_height) ]
            if self.VISIBILITY_MAP:
                for y in range(self.height):
                    for x in range(self.width): #to-do: via slice copying
                        visi[y][x]    =self.VISIBILITY_MAP[y][x]
            
            self.BOARD=board
            self.VISIBILITY_MAP=visi
            self.width  = new_width
            self.height = new_height

    def is_onboard(self,x,y):
        return x>=0 and y>=0 and x<self.width and y<self.height

    def lasergun_reset_stats(self):
        self.lgun_ready = False

    def lasergun_ready(self):
        self.lgun_ready = True

    def lasergun_update(self, autofire=False):
        if self.lgun_ready:
            if self.lgun_counter_dt == 0:
                self.lgun_counter = 0
                self.lgun_counter_dt = 1
            else:
                self.lgun_counter_max = self.lgun_counter
                self.lgun_counter = 0
            self.lasergun_fire_all()
        elif autofire:
            if self.lgun_counter_max!=None and self.lgun_counter==self.lgun_counter_max:
                self.lgun_counter = 0
                self.lasergun_fire_all()

    def lasergun_tick(self):
        if self.lgun_counter_dt==0:
            return
        self.lgun_counter += self.lgun_counter_dt

    def lasergun_fire_all(self):
        for y in range(self.height):
            for x in range(self.width):
                c = self.BOARD[y][x]
                if c == ELASER_MACHINE_READY_LEFT or c==ELASER_MACHINE_CHARGING_LEFT:
                    self.lasershots_update_at(ELASER_LEFT,  x, y, -1, 0)
                if c == ELASER_MACHINE_READY_RIGHT or c==ELASER_MACHINE_CHARGING_RIGHT:
                    self.lasershots_update_at(ELASER_RIGHT, x, y, 1, 0)
                if c == ELASER_MACHINE_READY_UP or c==ELASER_MACHINE_CHARGING_UP:
                    self.lasershots_update_at(ELASER_UP,    x, y, 0, -1)
                if c == ELASER_MACHINE_READY_DOWN or c==ELASER_MACHINE_CHARGING_DOWN:
                    self.lasershots_update_at(ELASER_DOWN,  x, y, 0, 1)

    def visibility_set_box(self, ox, oy):
        if self.is_onboard(ox,oy):
            self.VISIBILITY_MAP[oy][ox] = VISIBILITY_DURATION

    def visibility_tick(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.VISIBILITY_MAP[y][x]:
                    self.VISIBILITY_MAP[y][x]-=1

    def visibility_remove_invisible(self):
        temp = [EBOX, EGOLD] + EPERKS
        for y in range(self.height):
            for x in range(self.width):
                c=self.BOARD[y][x]
                v=self.VISIBILITY_MAP[y][x]
                if not v and c in temp:
                    self.BOARD[y][x]=EFLOOR

    def update_from_loaded_board(self):
        self.VISIBILITY_MAP = [ [0] * self.width for _ in range(self.height) ]
        for y in range(self.height):
            for x in range(self.width):
                c=self.BOARD[y][x]
                
                if c == EL.ESTART:
                    self.STARTS.add( (x,y) )

                if c == EL.EEXIT:
                    self.ENDS.add( (x,y) )
                    self.HAS_EXITS=True


    def update_from(self, input):
        global global_storage


        LOG("===================================================================================")
        LOG("CNT = {}".format(BigBoard.counter))
        LOG("===================================================================================")
        board = json.loads( input )

        print_input_json(board)

        showName = board['showName']
        levelFinished = board['levelFinished']
        levelProgress = board['levelProgress'] # {'current': 1, 'lastPassed': 0, 'total': 22}


        if levelFinished:
            if self.global_board_idx!=None:
                global_storage.update(self.global_board_idx, self.BOARD)
            else:
                if self.HAS_PLAYERS:
                    global_storage.store(self.BOARD)
            self.cleanup()
            return False

        w  = int(sqrt(len(board['layers'][0])))
        ox = board['offset']['x'] 
        oy = board['offset']['y'] 
        ## bug in input json
        # hx = board['heroPosition']['x']
        # hy = board['heroPosition']['y']
        # self.ME.moved(hx, hy, None)
        # self.ME.set_alive(True)

        ###############################
        if self.BOARD==None:
            #trye load global
            brdstatic = self.make_static_board(board['layers'][0])
            gidx, gboard = global_storage.search(ox, oy, brdstatic)
            if gidx!=None:
                self.global_board_idx = gidx
                self.BOARD = gboard
                self.width  = len(self.BOARD[0])
                self.height = len(self.BOARD)
                self.update_from_loaded_board()

        ###############################

        self.resize( ox+w, oy+w )
        
        self.reset_stats()
        
        self.lasergun_reset_stats()
        self.lasergun_tick()

        self.lasershots_reset_updated()
        self.lasershots_tick()

        self.ZOMBIES.tracking_init(self.width, self.height)
        self.PLAYERS.tracking_init(self.width, self.height)

        perks_old = copy.deepcopy(self.PERKS)
        self.update_layer1(ox, oy, board['layers'][0])
        self.update_layer2(ox, oy, board['layers'][1])
        self.update_layer3(ox, oy, board['layers'][2])
        if self.ME.is_alive and not self.ME.is_flying:
            perk = perks_old.get( (self.ME.X, self.ME.Y), None)
            if perk!=None:
                self.ME.got_perk( perk )

        self.ZOMBIES.tracking_finish()
        self.PLAYERS.tracking_finish()

        self.lasershots_remove_not_updated(ox, oy, w, w)

        self.lasergun_update()

        self.visibility_remove_invisible()
        self.visibility_tick()

        self.HAS_EXITS = len(self.ENDS)>0
        self.make_dangers_map()
        self.make_attack_map()

        BigBoard.counter+=1
        return True

    def reset_stats(self):
        self.HAS_GOLD    = False
        self.HAS_EXITS   = False
        self.HAS_PLAYERS = False
        self.HAS_ZOMBIES = False

    def lasershots_reset_updated(self):
        for l in self.LASERSHOTS:
            l.updated=False

    def lasershots_tick(self):
        for l in self.LASERSHOTS:
            l.tick()

    def lasershots_get_at(self, x, y):
        res = []
        for i,l in enumerate(self.LASERSHOTS):
            if l.x==x and l.y==y:
                res.append(i)
        return res

    def lasershots_active_is_at(self, x, y, t):
        for i,l in enumerate(self.LASERSHOTS):
            if l.x==x and l.y==y and l.t==t and l.active:
                return True
        return False

    def lasershots_any_active_at(self, x, y):
        for i,l in enumerate(self.LASERSHOTS):
            if l.x==x and l.y==y and l.active:
                return True
        return False

    def lasershots_update_at(self, t, x, y, dx, dy):
        shots_idx = self.lasershots_get_at(x,y)
        if shots_idx:
            for i in shots_idx: #not check t due to can be overlapped
                self.LASERSHOTS[i].updated=True
        else: #new found
            self.LASERSHOTS.append( LaserShot(t, x, y, dx, dy, True, True) )

    def lasershots_add_new(self, x, y, dx, dy, updated, autofire, nottrack):
        t = ELASERGUN_DX2T[ (dx,dy) ]
        l = LaserShot(t, x, y, dx, dy, updated, autofire)
        l.nottrack = nottrack
        self.LASERSHOTS.append( l ) 

    def lasershots_remove_not_updated(self, x, y, dx, dy):
        #remove not updated shots in visible area
        #invisible shots continue to live
        #res = [l for l in self.LASERSHOTS if l.updated]
        res = []
        for l in self.LASERSHOTS:
            #visible
            if l.x>=x and l.x<x+dx and l.y>=y and l.y<y+dy:
                if l.updated:
                    res.append(l)
                continue
            #invisible
            if l.x>=0 and l.x<self.width and l.y>=0 and l.y<self.height and self.BOARD[l.y][l.x] not in ELASERS_STOPS:
                l.updated = True
                res.append(l)
        self.LASERSHOTS=res


    def make_static_board(self, data_string):
        w  = int(sqrt(len(data_string)))
        brd = [[None]*w for _ in range(w)]
        for y in range(w):
            for x in range(w):
                ry = w-y-1
                c = data_string[ry*w+x]
                v = EUNKNOWN
                if c in ESTATIC_WALLS:
                    c = EWALL
                if c in EL.ESTATIC_ELEMENTS:
                    v = c
                elif c in  ELASER_GUN:
                    c = EL_REVERSE[c] #reverse
                    v = c
                brd[y][x]=v
        return brd


    def update_layer1(self, ox, oy, data_string):
        w  = int(sqrt(len(data_string)))
        
        self.PERKS=dict()

        for y in range(w):
            gy = oy + y
            for x in range(w):
                gx = ox + x
                if gx<0 or gy<0 or gx>=len(self.BOARD[0]) or gy>len(self.BOARD):
                    print("ERROR")
                    continue
                ry = w-y-1
                self.visibility_set_box(gx, gy)

                c = data_string[ry*w+x]
                
                if c == EL.EGOLD:
                    self.HAS_GOLD=True

                if c in EL.ESTATIC_WALLS:
                    c=EL.EWALL
                
                if c in EL.ESTATIC_ELEMENTS:
                    self.BOARD[gy][gx]=c

                if c == EL.ESTART:
                    self.STARTS.add( (gx,gy) )

                if c == EL.EEXIT:
                    self.ENDS.add( (gx,gy) )
                    self.HAS_EXITS=True

                if c in ELASER_GUN:
                    cr = EL_REVERSE[c] #reverse
                    self.BOARD[gy][gx]=cr
                
                if c in ELASER_GUN_READY:
                    self.lasergun_ready()
                #perks?
                if c in EPERKS: 
                    self.BOARD[gy][gx]=c
                    self.PERKS[(gx,gy)]=c

    def update_layer2(self, ox, oy, data_string):
        w  = int(sqrt(len(data_string)))
        
        for y in range(w):
            gy = oy + y
            for x in range(w):
                gx = ox + x

                ry = w-y-1
                c = data_string[ry*w+x]

                #players
                if c == EL.EROBO:
                    #found ME, alive, not-flying
                    if not self.ME.is_alive:
                        self.MYSTART=None
                    self.ME.moved(gx, gy, False)
                    self.ME.set_alive(True)

                if c == EL.EROBO_LASER or c == EROBO_FALLING:
                    #found ME, alive, not-flying
                    self.ME.moved(gx, gy, False)
                    self.ME.set_alive(False)
                    self.MYSTART=None

                if c == EL.EROBO_FALLING: #die
                    #found ME, alive, not-flying
                    self.ME.moved(gx, gy, False)
                    self.ME.set_alive(False)
                    self.MYSTART=None

                if c == EL.EROBO_OTHER:
                    self.PLAYERS.tracking_add_object(gx, gy)
                    self.HAS_PLAYERS=True
                
                if c == EL.EROBO_OTHER_LASER:
                    obj = self.PLAYERS.tracking_add_object(gx, gy)
                    obj.alive = False

                if c == EL.EROBO_OTHER_FALLING: #die
                    #self.PLAYERS.tracking_add_object(gx, gy)
                    pass


                if c == EL.EBOX:
                    self.BOARD[gy][gx]=c

                if c in  [EFEMALE_ZOMBIE, EMALE_ZOMBIE]: #, EZOMBIE_DIE
                    self.ZOMBIES.tracking_add_object(gx, gy)
                    self.HAS_ZOMBIES=True

                cr = EL_REVERSE.get(c, None) #reverse
                if cr == ELASER_LEFT:
                    self.lasershots_update_at(cr, gx, gy,-1, 0)
                if cr == ELASER_RIGHT:
                    self.lasershots_update_at(cr, gx, gy, 1, 0)
                if cr == ELASER_UP:
                    self.lasershots_update_at(cr, gx, gy, 0, -1)
                if cr == ELASER_DOWN:
                    self.lasershots_update_at(cr, gx, gy, 0, 1)

        pass


    def update_layer3(self, ox, oy, data_string):
        w  = int(sqrt(len(data_string)))
        
        for y in range(w):
            gy = oy + y
            for x in range(w):
                gx = ox + x

                ry = w-y-1
                c = data_string[ry*w+x]

                #players
                if c == EL.EROBO_FLYING:
                    #found ME, alive, not-flying
                    self.ME.moved(gx, gy, True)

                if c == EL.EROBO_OTHER_FLYING:
                    obj = self.PLAYERS.tracking_add_object(gx, gy)
                    obj.flying = True
                    self.HAS_PLAYERS=True


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
            res[z.Y][z.X] = EMALE_ZOMBIE

        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            res[p.Y][p.X] = (EROBO_OTHER, EROBO_OTHER_FLYING)[p.flying]

        for l in self.LASERSHOTS: #last - to see shots
            res[l.y][l.x] = l.t

        res[self.ME.Y][self.ME.X] = (EROBO, EROBO_LASER)[self.ME.is_flying] #laser is better %) 

        ###### dangers

        # if title:
        #     print(title)
        # for i,r in enumerate(res):
        #     sb = "".join( res[i] ) 
        #     sd = " ".join( "{:3}".format(d) for d in self.DANGERS_MAP[i]) 
        #     res[i] = "{:2}: {}    |    {}".format(i,sb,sd)

        # for r in res:
        #     print( r )


        #FILELOG
        if title:
            LOGF(title)
        for r in res:
            LOGF("".join( r))
        #print players, zombies, shots
        for i in range(self.PLAYERS.size()):
            p = self.PLAYERS.get(i)
            LOGF("PLAYER id={} x={} y={} fly={}".format(p.ID,p.X,p.Y,p.flying))
        for i in range(self.ZOMBIES.size()):
            z = self.ZOMBIES.get(i)
            LOGF("ZOMBIE id={} x={} y={}".format(z.ID,z.X,z.Y))
        lshots = sorted(self.LASERSHOTS, key=lambda l: l.y*100+l.x)
        for i,l in enumerate(lshots):
            LOGF("LASERSHOT t={} y={} x={} dx={} dy={} updated={} active={}".format(l.t,l.y,l.x,l.dx,l.dy,l.updated,l.active))
        LOGF("\n")

    def tick(self):
        # move existing lasers
        self.lasershots_reset_updated()
        self.lasershots_tick()
        for l in self.LASERSHOTS:
            if l.x<0 or l.y<0 or l.x>=self.width or l.y>=self.height:
                continue
            c = self.BOARD[l.y][l.x]
            l.updated = c not in ELASERS_STOPS
        self.lasershots_remove_not_updated(0,0,self.width,self.height)

        # laserguns autofire
        self.lasergun_reset_stats()
        self.lasergun_tick()
        self.lasergun_update(True)

    def tick0(self):
        # other players which near - autofire
        mx = self.ME.X
        my = self.ME.Y
        dmin = 1
        dmax = 5
        gmode=GameConfig.get_game_mode()

        for ip in range(self.PLAYERS.size()):
            p=self.PLAYERS.get(ip)
            px, py = p.X, p.Y
            dx = abs(mx-px)
            dy = abs(my-py)
            tx, ty = (mx+px)//2, (my+py)//2

            if p.alive and gmode != GAME_MODE_BERSERK:
                if dx==0 and dy>=dmin and dy<=dmax:
                    if my<py:  # vertical up shot to me
                        self.lasershots_add_new(px, py, 0,-1, True, False, True) #1 tick delay no track
                    if my>py:  #vertical down shot to me
                        self.lasershots_add_new(px, py, 0, 1, True, False, True) #1 tick delay no track
                if dy==0 and dx>=dmin and dx<=dmax:
                    if mx>px:  # horizontal right shot to me
                        self.lasershots_add_new(px, py, 1, 0, True, False, True) #1 tick delay no track
                    if mx<px:  # horizontal right shot to me
                        self.lasershots_add_new(px, py,-1, 0, True, False, True) #1 tick delay no track

            #special case - dead and alive
            if dx==0 and dy==2:
                if not p.alive:
                    pass
                if my<py:  # vertical up shot to me
                    if self.lasershots_active_is_at(tx, ty, ELASER_DOWN):
                        self.lasershots_add_new(tx, ty, 0, -1, True, True, False) 
                if my>py:  #vertical down shot to me
                    if self.lasershots_active_is_at(tx, ty, ELASER_UP):
                        self.lasershots_add_new(tx, ty, 0, 1, True, True, False) #
            if dy==0 and dx==2:
                if mx>px:  # horizontal right shot to me
                    if self.lasershots_active_is_at(tx, ty, ELASER_LEFT):  # P<M -> P<>M
                        self.lasershots_add_new(tx, ty, -1, 0, True, True, False) 
                if mx<px:  # horizontal right shot to me
                    if self.lasershots_active_is_at(tx, ty, ELASER_RIGHT):# M>P -> P<>M
                        self.lasershots_add_new(tx, ty,  1, 0, True, True, False) 

    def scalefire(self, r, t):
        if not self.ME.perk_deathray_cnt:
            t=min( t, len(RATE_FIRE_SCALES)-1)
            return int(r*RATE_FIRE_SCALES[t])
        return r

    def rate_move_fire(self, cmd):
        #fire if only target available for example
        if not cmd in COMMANDS_FIRE:
            return False
        
        if self.ME.is_flying:
            return 0 #can't fire in air

        gmode=GameConfig.get_game_mode()

        mdx, mdy = COMMANDS_FIRE_DXY[cmd]
        mx,  my  = self.ME.X, self.ME.Y

        res = 0

        #neigbour 1 and 2
        if mdx==0: #vertical move
            ndx1, ndy1 = -1, 0
            ndx2, ndy2 =  1, 0
        else: #horizontal move
            ndx1, ndy1 = 0, -1
            ndx2, ndy2 = 0, 1
        
        t = 0
        while True:
            ### ME moves
            mx+=mdx
            my+=mdy
            t +=1
            if not self.is_onboard(mx,my):
                break
            c = self.BOARD[my][mx]

            blocking = EFIRE_BLOCKING
            if self.ME.perk_unstop_cnt:
                blocking = EFIRE_BLOCKING_PERK_UNSTOP

            if c in blocking:
                break
            #####

            #check for player            
            if self.PLAYERS.is_at(mx,my):
                if t==1: #near - 100% fire
                    res+=self.scalefire(RATE_FIRE_NEIGHBOUR, t)
                elif t==2: #duel
                    res+=self.scalefire(RATE_FIRE_DUELER, t)
                else:
                    res+=self.scalefire(RATE_FIRE_PLAYER, t)
                
            if t==1 and self.PLAYERS.is_estimateted_at(mx, my):
                res+=self.scalefire(RATE_FIRE_NEIGHBOUR, t)

            # # in possible moves already
            #     if t==1 and self.PLAYERS.is_at(mx, my):
            #         res+=self.scalefire(RATE_FIRE_NEIGHBOUR, t)

            if self.ZOMBIES.is_at(mx,my):
                res+=self.scalefire(RATE_FIRE_ZOMBIE, t)

            if self.starts_is_at(mx, my):
                res+=RATE_FIRE_STARTS

            N = [ (mx+ndx1, my+ndy1), (mx+ndx2, my+ndy2) ]
            for nx, ny in N:
                if not self.is_onboard(nx,ny):
                    continue
                c = self.BOARD[ny][nx]
                if c in EFIRE_BLOCKING:
                    continue
                # if self.PLAYERS.is_at(nx,ny):#near ?
                #     res+=self.scalefire(RATE_FIRE_PLAYERN, t)
                if t<4 and self.ZOMBIES.is_at(nx,ny): #only if near
                    res+=self.scalefire(RATE_FIRE_ZOMBIEN, t)

        
        if res:
            LOG("FIRE rate of {} = {}".format(cmd,res))
        return res

    def make_dangers_map(self):
        #make danger map (potential field like)
        dangers = [ [0]* self.width for _ in range(self.height) ]

        #zombie first
        mx = self.ME.X
        my = self.ME.Y
        for i in range(self.ZOMBIES.size()):
            z=self.ZOMBIES.get(i)
            dangers[z.Y][z.X] = DANGER_RATE_ZOMBIE
            zd = dist(mx,my,z.X,z.Y)
            for dx, dy in self.ZOMBIES.possible_moves():
                nx, ny = z.X + dx, z.Y +dy
                if self.is_onboard(nx, ny):
                    nd = dist(mx,my,nx,ny)
                    dg = (DANGER_RATE_NEAR_ZOMBIE_BACK, DANGER_RATE_NEAR_ZOMBIE_FACE)[nd < zd]
                    dg = scaled_danger_zombie(dg, zd)
                    dangers[ny][nx] = max(dangers[ny][nx], dg)

        gmode=GameConfig.get_game_mode()
        dg_player_face = DANGER_RATE_NEAR_PLAYER_FACE
        dg_player_back = DANGER_RATE_NEAR_PLAYER_BACK
        dg_player_diag = DANGER_RATE_NEAR_PLAYER_DIAG
        if gmode == GAME_MODE_BERSERK:
            dg_player_face //= 2
            #dg_player_back //= 2 - still dangerous - kill in jump
            dg_player_diag //= 2

        #players 
        for i in range(self.PLAYERS.size()):
            z=self.PLAYERS.get(i)
            if not z.alive:
                continue
            zd = dist(mx,my,z.X,z.Y)

            if zd==1: #Face to Face - risk to get shot into face!!!!
                dangers[z.Y][z.X] = max(dangers[z.Y][z.X], dg_player_face)

            if zd==2: #risky to jump to player - can go back and fire!!!
                dangers[z.Y][z.X] = max(dangers[z.Y][z.X], DANGER_RATE_PLAYER)

            for dx, dy in [(-1, 0), (1,0), (0,-1), (0,1)]:
                nx, ny = z.X + dx, z.Y +dy
                if self.is_onboard(nx, ny):
                    nd = dist(mx,my,nx,ny)
                    dg = (dg_player_back, dg_player_face)[nd < zd]
                    dg = scaled_danger(dg, zd)
                    dangers[ny][nx] = max(dangers[ny][nx], dg)

            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]: #diagonal - risky to jump due to possible fire
                nx, ny = z.X + dx, z.Y +dy
                if self.is_onboard(nx, ny):
                    nd = dist(mx,my,nx,ny)
                    dg = dg_player_diag
                    dg = scaled_danger(dg, zd)
                    dangers[ny][nx] = max(dangers[ny][nx], dg)

        #zombie exits
        for y in range(self.height):
            for x in range(self.width):
                c = self.BOARD[y][x]
                if c==EZOMBIE_START:
                    dangers[y][x] = max(dangers[y][x], DANGER_RATE_ZOMBIE_EXIT)

        self.DANGERS_MAP = dangers
        return dangers


    def make_attack_line(self, attack, sx, sy, dx, dy, dmin, dmax):
        nx, ny = sx, sy
        for d in range(dmax+1):
            if not self.is_onboard(nx, ny):
                break
            c = self.BOARD[ny][nx]
            if c in EFIRE_BLOCKING: #PERKS!!!!!
                break
            if d>=dmin and c in [EFLOOR, ESTART]:
                attack[ny][nx]=True
            nx+=dx
            ny+=dy

    def starts_is_at(self, x, y):
        res = None
        for sx,sy in self.STARTS:
            if sx==x and sy==y:
                return True
        return False

    def get_starts_nearest(self, x, y):
        res  = None
        resd = None
        for sx,sy in self.STARTS:
            d = dist(sx,sy,x,y)
            if res==None or d<resd:
                res = (sx,sy)
                resd = d
        return res

    def make_attack_map(self):
        attack = [ [0]* self.width for _ in range(self.height) ]

        if GameConfig.get_game_mode_default() == GAME_MODE_AUTO:
            self.MYSTART = None #to allow reaasing

        if self.MYSTART==None and self.ME.is_alive:
            ns = self.get_starts_nearest(self.ME.X, self.ME.Y)
            self.MYSTART = {ns}
            #self.MYSTART= {(self.ME.X, self.ME.Y)}

        starts = self.MYSTART
        if not starts:
            starts = self.STARTS
        if GameConfig.get_game_mode() == GAME_MODE_BERSERK:
            dmax = BERSERK_STARTS_RANGE_MAX
            dmin = BERSERK_STARTS_RANGE_MIN
            for sx, sy in starts:
                self.make_attack_line(attack, sx, sy,  1,  0, dmin, dmax)
                self.make_attack_line(attack, sx, sy, -1,  0, dmin, dmax)
                self.make_attack_line(attack, sx, sy,  0, -1, dmin, dmax)
                self.make_attack_line(attack, sx, sy,  0,  1, dmin, dmax)

        else:
            dmax = ATTACK_STARTS_RANGE_MAX
            dmin = ATTACK_STARTS_RANGE_MIN
            for sx, sy in starts:
                self.make_attack_line(attack, sx, sy,  1,  0, dmin, dmax)
                self.make_attack_line(attack, sx, sy, -1,  0, dmin, dmax)
                self.make_attack_line(attack, sx, sy,  0, -1, dmin, dmax)
                self.make_attack_line(attack, sx, sy,  0,  1, dmin, dmax)

        self.ATTACK_MAP = attack
        return attack

if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
