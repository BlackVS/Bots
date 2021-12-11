#! /usr/bin/env python3

from typing import TypeVar, Generic, Type
from config import *
from logger import *
import copy
from model_directions import *

def B_remove_pid(B, pid):
    for y in range(len(B)):
        for x in range(len(B[0])): #speedup: as variant remeber cells
            if pid in B[y][x]:
                B[y][x].remove(pid)

class TObject:
    X  = None
    Y  = None
    PX = None
    PY = None  
    ID = -1
    #
    NEAR_MOVES      = []
    PREV_NEAR_MOVES = []
    updated         = False
    tick_moved      = False # if moved during tick i.e. ne wpos

    est_is_stuck    = False

    def __init__(self, id=-1, x=None, y=None, updated=False):
        self.reset()
        self.ID=id
        self.PX = None
        self.PY = None
        self.X = x
        self.Y = y
        self.updated = updated
        self.tick_moved = False


    def reset(self):
        #properties
        self.ID = 0
        self.X  = 0
        self.Y  = 0
        self.PX = 0
        self.PY = 0

        #tracking related
        self.updated = False
        self.tick_moved = False
        self.NEAR_MOVES    = []
        self.PREV_NEAR_MOVES    = []    

        #estimatin related
        self.est_is_stuck = False


    def get_ID(self):
        return self.ID


    #CUSTOM METHODS
    def track_custom_update_from(self, object):
        pass

    def track_possible_moves(self):
        raise NotImplementedError

    def track_move_dir2xy(self, dir):
        raise NotImplementedError

    def track_moved(self, x, y):
        if self.X!=x or self.Y!=y:
            self.PX = self.X
            self.PY = self.Y
            self.X = x
            self.Y = y

    def track_is_hidden(self):
        return False
    #########################################################


    def env_reset_stats(self):
        self.PREV_NEAR_MOVES    = self.NEAR_MOVES
        self.NEAR_MOVES    = []

    def env_found_move(self, dir):
        self.NEAR_MOVES.append( dir )


TOBJ_IDXCNT = 1
def reset_tracking():
    global TOBJ_IDXCNT
    TOBJ_IDXCNT = 1

def dist(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)
    
class TObjects:
    tobjects = []
    tobjects_new = []
    boardwidth = 0
    boardheight = 0

    def __init__(self):
        self.cleanup()

    def cleanup(self):
        self.tobjects = []
        self.tobjects_new = []

    def tracking_init(self, width, height):
        self.tobjects_new = []
        self.boardwidth  = width
        self.boardheight = height
        self.reset_updated()

    def tracking_add_object(self, x, y):
        obj = self.create_object(x, y)
        self.tobjects_new.append( obj )
        return obj

    def tracking_finish(self):
        self.update()
        self.tracking_remove_not_updated()

    def size(self):
        return len(self.tobjects)

    def get(self, i):
        if i>=0 and i<len(self.tobjects):
            return self.tobjects[i]
        return None

    def remove(self):
        self.tobjects = [o for o in self.tobjects if o.toremove!=True]

    def is_at(self, x, y):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            if p.X==x and p.Y==y:
                return True
        return False

    def is_near(self, x, y, dst):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            d = dist(p.X, p.Y, x, y)
            if d<dst:
                return True
        return False

    def is_near_HV(self, x, y, dst):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            dx = abs(p.X-x)
            dy = abs(p.Y-y)
            if dx!=0 and dy!=0:
                return False
            if dx<=dst and dy<=dst:
                return True
        return False

    def get_at(self, x, y):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            if p.X==x and p.Y==y:
                return p
        return None

    def get_all_at(self, x, y):
        res = []
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            if p.X==x and p.Y==y:
                res.append(p)
        return res

    def is_estimateted_at(self, x, y):
        for i in range(len(self.tobjects)):
            p=self.tobjects[i]
            res, ex, ey = p.estimate_next_pos()
            if res!=None and ex==x and ey==y:
                return True
        return False

    #CUSTOM METHODS
    def object_new(self):
        return TObject()

    #########################################################



    def create_object(self, x, y):
        obj = self.object_new()
        obj.X = x
        obj.Y = y
        return obj

    def reset_updated(self):
        for l in self.tobjects:
            l.updated=False

    def get_new_id(self):
        global TOBJ_IDXCNT
        TOBJ_IDXCNT+=1
        return TOBJ_IDXCNT
        

    def is_onboard(self,x,y):
        return x>=0 and y>=0 and x<self.boardwidth and y<self.boardheight


    #check enviroment
    def object_test_env(self, zo):
        zo.env_reset_stats()

        if zo.tick_moved:
            #object altready at new pos - we know 100%, treat as STOP in track
            zo.env_found_move( DIR_STOP )
            return

        #object on old pos and we must estimate it's possible found move
        px = zo.X
        py = zo.Y
        for dir in zo.track_possible_moves():
            dx, dy = zo.track_move_dir2xy(dir)
            nx, ny = px+dx, py+dy
            if not self.is_onboard(nx, ny):
                continue
            for zn in self.tobjects_new:
                if zn.X==nx and zn.Y==ny:
                    zo.env_found_move( dir )

    def objects_test_env(self):
        for z in self.tobjects:
            self.object_test_env(z)

    def update(self):
        self.objects_test_env() #check old possible moves

        B = [ [ [] for _ in range(self.boardwidth)] for _ in range(self.boardheight)]

        obj_new = [ [z.X, z.Y, z, None, False] for z in self.tobjects_new]

        # enum olds
        for z in self.tobjects:
            if z.updated:
                continue #not check if already or hidden
            ox, oy = z.X, z.Y
            for d in z.NEAR_MOVES:
                dx, dy = z.track_move_dir2xy(d)
                nx, ny = ox+dx, oy+dy
                if not self.is_onboard(nx, ny):
                    continue
                B[ny][nx].append(z.ID)
        
        flag = 0
        while flag<2:
            flag+=1
            for i in range(len(obj_new)):
                if obj_new[i][4]:
                    continue
                px = obj_new[i][0]
                py = obj_new[i][1]
                #pt = zombies_new[i][2]
                if len(B[py][px])==0: #surely new chopper
                    #nc = self.new_object(member_class, px, py, True)
                    nc = copy.deepcopy(obj_new[i][2]) #reuse ?
                    nc.ID = self.get_new_id()
                    nc.updated=True
                    self.tobjects.append(nc)
                    obj_new[i][3] = nc.ID
                    obj_new[i][4] = True
                    flag=0
                elif len(B[py][px])==1: #surely moved
                    cid = B[py][px][0]
                    nc = self.objects_get_by_id(cid)
                    if nc:
                        nc.track_moved( px, py )
                        nc.track_custom_update_from(obj_new[i][2])
                        nc.updated=True
                        obj_new[i][3] = cid
                        obj_new[i][4] = True
                    #update B
                    B_remove_pid(B, cid)
                    flag=0
        
        #most ineteresting - we have few old and few new, not 
        #non-processed new
        cnt_rest = 0
        for i,p in enumerate(obj_new):
            if not p[4]: #not yet assigned
                cnt_rest+=1
                nc = copy.deepcopy(obj_new[i][2]) #reuse ?
                nc.ID = self.get_new_id()
                nc.updated=True
                self.tobjects.append(nc)
                obj_new[i][3] = nc.ID
                obj_new[i][4] = True

        if cnt_rest:
            LOG("We can't track {} objects, recreated them".format(cnt_rest))



    def objects_get_by_id(self, id):
        for z in self.tobjects:
            if z.ID==id:
                return z
        return None

    def tracking_remove_not_updated(self):
        res = [l for l in self.tobjects if l.updated]
        self.tobjects=res


    def vars(self):
        return vars(self)

    def object_restore(self, obj):
        global TOBJ_IDXCNT
        TOBJ_IDXCNT = max( TOBJ_IDXCNT, obj.ID+1)
        self.tobjects.append( obj )

