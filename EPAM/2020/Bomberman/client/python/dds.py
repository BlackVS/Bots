#!/usr/bin/env python3

from time import *
from random import *
from board import *
from element import *
from direction import *
from collections import *
from copy import copy, deepcopy
import boardQt


GSTATE = GameState()


ACTIONS = ['LEFT' , 'RIGHT', 'UP', 'DOWN', 'STOP', 'ACT']
MOVES   = [(-1, 0), (1,0),  (0,-1), (0,1), (0,0)]
DEEP_MAX = 23*23

GLOBAL_BOARD_DANGERS = None
GLOBAL_BOARD_DANGERS_t = None

MOVE_NO_RISK   = 0
MOVE_LOW_RISK  = 1
MOVE_MID_RISK  = 2
MOVE_HIGH_RISK = 3
MOVE_DEAD      = 4
MOVE_RATE_MAX  = 5

SZ = None

def DIST1(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)


def if_move_towards(px,py,tx,ty,dir):
    dx, dy = MOVES[dir]
    d1 = DIST1(px,py,tx,ty)
    d2 = DIST1(px+dx,py+dy,tx,ty)
    return d2<d1

def do_move_towards(px,py,dir):
    dx, dy = MOVES[dir]
    return (px+dx,py+dy)

def path2str(p):
    return "-".join( map(lambda m: ACTIONS[m], p) ) 

# def is_danger(x, y, t, lifes, bdangers, bdangers_t):
#     if bdangers[y][x] == EL_NONE:
#         return False
#     if t>lifes: #no immune at this time momemnt
#         return True
#     # have immune but only for blasts
#     return bdangers_t[y][x]>DANGERS_TYPE_BLAST


def is_danger(x, y, t, lifes, bdangers, bdangers_t):
    if bdangers[y][x] in [EL_NONE, EL_BOMB_BLAST_5, EL_BOMB_BLAST_4]:
        return False
    if bdangers_t[y][x] == DANGERS_TYPE_BLAST:
        if lifes>=t:
            return False
        t_blastmax = ord(bdangers[y][x])-ord(EL_BOMB_BLAST_1)+1
        if t>t_blastmax:
            return False #already detonated
        return True
    # have immune but only for blasts
    return bdangers_t[y][x]>DANGERS_TYPE_BLAST

def get_danger(x, y, t, lifes, bdangers, bdangers_t):
    bd = bdangers[y][x]
    if bd == EL_NONE:
        return bd
    if t>lifes: #no immune at this time momemnt
        return bd
    # have immune but only for blasts
    if bdangers_t[y][x]<=DANGERS_TYPE_BLAST:
        return EL_NONE
    return bd

def get_move_by_cmd(x,y,d):
    dx = Direction(d).get_x()
    dy = Direction(d).get_y()
    return (x+dx, y+dy)

def get_move_by_idx(x,y,d):
    dx = MOVES[d][0]
    dy = MOVES[d][1]
    return (x+dx, y+dy)

def is_onboard(x,y):
    return x>=0 and x<SZ and y>=0 and y<SZ

def player_get_possible_moves(x, y, borig, bdangers, lifes):
    global SZ
    res = []
    for i, (dx,dy) in enumerate(MOVES[:4]):
        nx = x + dx
        ny = y + dy
        if borig[ny][nx] not in ELS_NO_MOVE:
            if bdangers[ny][nx] != EL_BOMB_BLAST_1: #immedeatly dead
                res.append(i)
    return res

# pos and move time
def rate_move(x, y, t, borig, bdangers, dangerst, lifes):
    global SZ
    res = MOVE_NO_RISK
    if lifes<t and t==1 and borig[y][x] in [ EL_BOMB_TIMER_1, EL_MEAT_CHOPPER, EL_DEAD_MEAT_CHOPPER]:
        return MOVE_DEAD

    #furher from chopper less risk
    if borig[y][x] in ELS_CHOPPERS:
        if t<2:
            res=max(res, MOVE_HIGH_RISK)
        elif t<4:
            res=max(res, MOVE_MID_RISK)
        else:
            res=max(res, MOVE_LOW_RISK)

    #chopper case
    dead_choppers_cnt = 0
    if t<6 :
        dead_choppers_cnt = count_objects_around(borig, x, y, [EL_DEAD_MEAT_CHOPPER])
        if dead_choppers_cnt>0:
            res=max(res, MOVE_DEAD)

    choppers_cnt = 0
    if t<6 :
        choppers_cnt = count_objects_around(borig, x, y, [EL_MEAT_CHOPPER])
        if choppers_cnt>0:
            res=max(res, MOVE_HIGH_RISK)

    #timers
    if bdangers[y][x] != EL_NONE:
        if dangerst[y][x] == DANGERS_TYPE_BLAST and lifes>=t:
            #LOG("")
            pass #can cross absolutly safe
        else:
            #crossing blast
            btime = ord(bdangers[y][x])-ord(EL_BOMB_BLAST_1)+1 #time to fire
            d = btime-t #same time - killed
            if d<0: #not this time
                res=max(res, MOVE_LOW_RISK)
            elif d==0:
                return MOVE_DEAD
            elif d<2:
                res=max(res, MOVE_MID_RISK)
            elif d<4:
                res=max(res, MOVE_MID_RISK)
            else:
                res=max(res, MOVE_LOW_RISK)
    
    if borig[y][x] == EL_OTHER_BOMBERMAN:  
        res=max(res, MOVE_MID_RISK)

    return res

def check_near(board, x, y, t):
    for dx, dy in MOVES:
        nx=x+dx
        ny=y+dy
        if nx>0 and nx<SZ and y>0 and ny<SZ and board[ny][nx] in t:
            return True
    return False

def get_nearest(x, y, t, board):
    for i, (dx, dy) in enumerate(MOVES[:4]):
        nx=x+dx
        ny=y+dy
        if nx>0 and nx<SZ and y>0 and ny<SZ and board[ny][nx] in t:
            return ACTIONS[i]
    return ""


def count_fire_targets(board, x, y ):
    blast_size=GSTATE.me().get_current_blast_size()

    #predictions
    ch_future = GSTATE.chopper_predicted_positions()

    res=0
    for dx, dy in MOVES[:4]:
        nx, ny = x, y
        for w in range(blast_size):
            nx+=dx
            ny+=dy
            if nx>0 and nx<SZ and y>0 and ny<SZ:
                if board[ny][nx]==EL_OTHER_BOMBERMAN:
                    res+=20
                # if board[ny][nx] in ELS_CHOPPERS: => use predictions
                #     res+=10
                if board[ny][nx]==EL_DESTROY_WALL:
                    res+=1
                if board[ny][nx] in ELS_NO_MOVE:
                    break
                if board[ny][nx] in ELS_PERKS:
                    return 0
            for cx, cy in ch_future:
                if cx==nx and cy==ny: #
                    res+=10
    return res

def check_move(px, py, move, targets, borig, bdangers, bdangerst, lifes, ignoreWalls=False, maxrisk=MOVE_MID_RISK+0.6, maxdepth=20):
    global SZ

    dx, dy = MOVES[move]
    # if DEBUG_PRINT:
    #     print("CHECK_MOVE: {} = {} {}".format( ACTIONS[move], dx,dy))

    V = [ [0]*SZ for _ in range(SZ)]
    if dx!=0 or dy!=0: #to not back to current but stay at home is possible move too
        V[py][px] = -1

    x=px+dx
    y=py+dy


    w = 1
    r = rate_move(x, y, w, borig, bdangers, bdangerst, lifes)

    M = deque()
    M.append( (x,y,w,r,[move]) )

    wdanger = is_danger(x,y,w,lifes,bdangers,bdangerst)
    if bdangers[y][x] == EL_BOMB_BLAST_1 and wdanger:
        #(r_rate, r_space, r_dims, r2wall, r2bomber)
        return (MOVE_DEAD, 0)


    cur_r = MOVE_DEAD
    cur_w = 0

    BLOCKS = ELS_NO_MOVE_EXCEPT_DWALL if ignoreWalls else  ELS_NO_MOVE
    while M:
        x, y, w, r, m  = M.popleft()
        wdanger = is_danger(x,y,w,lifes,bdangers,bdangerst)

        dd=DIST1(px, py, x, y)
        if dd>maxdepth:
            continue

        if borig[y][x] in BLOCKS: #can't move - skip
            return (MOVE_DEAD, 0) #fail sitation


        if V[y][x]!=0 and m[-1]!=4: #already processed and not wait
            continue


        if borig[y][x] in targets:
            if bdangers[y][x] != EL_NONE and wdanger:
                #LOG("")
                pass
            else:
                r = max(r, rate_move(x, y, w, borig, bdangers, bdangerst, lifes))
                if r<=maxrisk:
                    #print("FOUND {} =  {} : {}".format(nw, nr, path2str(nm)))
                    return (r, w)
                else:
                    if r<MOVE_DEAD:
                        if r<cur_r:
                            cur_r=r
                            cur_w=w

        if r>maxrisk:
            continue

        if V[y][x]==0:
            V[y][x] = 1
        else: 
            V[y][x]+=1

        #print_board(V)


        for i, (dx,dy) in enumerate(MOVES[:4]) : #including stops
            #print("check={}".format(ACTIONS[i]))
            nx, ny, nw, nm  = x+dx, y+dy, w+1, m+[i]
            nr = max(r, rate_move(nx, ny, nw, borig, bdangers, bdangerst, lifes))
            ndanger = is_danger(nx,ny,nw,lifes,bdangers,bdangerst)
            
            if not is_onboard(nx,ny): #outboard
                continue

            if V[ny][nx]!=0:          #already checked
                continue 

            if borig[ny][nx] in targets:
                # dangerous block
                if borig[ny][nx] in BLOCKS and ndanger and w<3:
                    nr = MOVE_DEAD
                # high risk to pass
                elif borig[ny][nx] not in BLOCKS and ndanger and lifes<nw:
                    pass #nr = max(r, MOVE_HIGH_RISK)
                elif nr<MOVE_HIGH_RISK:
                    #print("FOUND {} =  {} : {}".format(nw, nr, path2str(nm)))
                    return (nr, nw)
                if nr>=MOVE_DEAD:
                    continue

            if (borig[ny][nx] in BLOCKS) or nw>=DEEP_MAX: #wall or stop deepr
                continue

            if bdangers[ny][nx] != EL_NONE: #next is blast
                #try stops
                minr  = MOVE_DEAD
                wtime = None
                for iw in range(0,6):
                    r0 = rate_move(x, y, w+iw, borig, bdangers, bdangerst, lifes)
                    if r0>=MOVE_DEAD:
                        break #can'stay more
                    r1 = rate_move(nx,ny,nw+iw, borig, bdangers, bdangerst, lifes)
                    rr = max(r0, r1)
                    if rr<minr or wtime==None:
                        minr=rr
                        wtime=iw
                if minr<MOVE_DEAD and wtime>0:
                    nr = max(r, minr)
                    M.append( (nx, ny, nw+wtime, nr, m+[4]*wtime+[i]) )    
                    continue
                elif wtime==0: #no risk
                    pass
                
            #rest
            if nr<MOVE_DEAD:
                M.append( (nx, ny, nw, nr, nm) )    

    # if cur_r!=MOVE_DEAD:
    #     print("FOUND ONLY HI RISK MOVE risk={} dst={}".format(cur_r,cur_w))
    return (cur_r, cur_w)




def check_move_wall(px, py, move, borig, bdangers, bdangerst, lifes, maxrisk=MOVE_MID_RISK+0.6, maxdepth=30):
    global SZ

    dx, dy = MOVES[move]
    # if DEBUG_PRINT:
    #     print("CHECK_MOVE: {} = {} {}".format( ACTIONS[move], dx,dy))

    V = [ [0]*SZ for _ in range(SZ)]
    if dx!=0 or dy!=0: #to not back to current but stay at home is possible move too
        V[py][px] = -1

    x=px+dx
    y=py+dy


    w = 1
    r = rate_move(x, y, w, borig, bdangers, bdangerst, lifes)

    M = deque()
    M.append( (x,y,w,r,[move]) )

    wdanger = is_danger(x,y,w,lifes,bdangers,bdangerst)
    if bdangers[y][x] == EL_BOMB_BLAST_1 and wdanger:
        #(r_rate, r_space, r_dims, r2wall, r2bomber)
        return (MOVE_DEAD, 0)


    cur_r = MOVE_DEAD
    cur_w = 0

    BLOCKS = ELS_NO_MOVE
    while M:
        x, y, w, r, m  = M.popleft()
        cb = count_objects_around(borig, x,y, [EL_DESTROY_WALL])

        wdanger = is_danger(x,y,w,lifes,bdangers,bdangerst)

        dd=DIST1(px, py, x, y)
        if dd>maxdepth:
            continue

        if borig[y][x] in BLOCKS: #can't move - skip
            continue


        if V[y][x]!=0 and m[-1]!=4: #already processed and not wait
            continue

        if wdanger:
           continue

        r = max(r, rate_move(x, y, w, borig, bdangers, bdangerst, lifes))
        if r<=maxrisk and cb>1:
            #print("FOUND {} =  {} : {}".format(nw, nr, path2str(nm)))
            return (r, w)
        else:
            if r<MOVE_DEAD:
                if r<cur_r:
                    cur_r=r
                    cur_w=w
        if r>maxrisk:
            continue

        if V[y][x]==0:
            V[y][x] = 1
        else: 
            V[y][x]+=1


        for i, (dx,dy) in enumerate(MOVES[:4]) : #including stops
            #print("check={}".format(ACTIONS[i]))
            nx, ny, nw, nm  = x+dx, y+dy, w+1, m+[i]
            nr = max(r, rate_move(nx, ny, nw, borig, bdangers, bdangerst, lifes))
            ndanger = is_danger(nx,ny,nw,lifes,bdangers,bdangerst)

            if not is_onboard(nx,ny): #outboard
                continue

            if V[ny][nx]!=0:          #already checked
                continue 

            if borig[ny][nx] in BLOCKS: #can't move - skip
                continue

            if ndanger:
                continue

            if nr<=maxrisk and cb>1:
                #print("FOUND {} =  {} : {}".format(nw, nr, path2str(nm)))
                return (r, w)
            else:
                if nr<MOVE_DEAD:
                    if nr<cur_r:
                        cur_r=nr
                        cur_w=nw
            #rest
            if nr<MOVE_DEAD:
                M.append( (nx, ny, nw, nr, nm) )    

    # if cur_r!=MOVE_DEAD:
    #     print("FOUND ONLY HI RISK MOVE risk={} dst={}".format(cur_r,cur_w))
    return (cur_r, cur_w)




def check_move_farthest_safe(px, py, move, targets, borig, bdangers, bdangerst, lifes, maxdepth=10):
    global SZ

    dx, dy = MOVES[move]
    # if DEBUG_PRINT:
    #     print("CHECK_MOVE: {} = {} {}".format( ACTIONS[move], dx,dy))

    V = [ [0]*SZ for _ in range(SZ)]
    if dx!=0 or dy!=0: #to not back to current but stay at home is possible move too
        V[py][px] = -1

    x=px+dx
    y=py+dy

    w = 1
    r = rate_move(x, y, w, borig, bdangers, bdangerst, lifes )
    wdanger = is_danger(x,y,w,lifes,bdangers,bdangerst)

    M = deque()
    M.append( (x,y,w,r,[move]) )

    if bdangers[y][x] == EL_BOMB_BLAST_1 and wdanger:
                                       # not (bdangerst[y][x] <= DANGERS_TYPE_BLAST and lifes>=w):
        #(r_rate, r_space, r_dims, r2wall, r2bomber)
        return (MOVE_DEAD, None, None, None, None)


    if bdangers[y][x] in [EL_MEAT_CHOPPER, EL_DEAD_MEAT_CHOPPER]:
        #(r_rate, r_space, r_dims, r2wall, r2bomber)
        return (MOVE_DEAD, None, None, None, None)

    res_r = MOVE_DEAD
    res_dd= 0
    res_x = None
    res_y = None
    res_m = []
    while M:
        x, y, w, r, m  = M.popleft()
        wdanger = is_danger(x,y,w,lifes,bdangers,bdangerst)
        dd = DIST1(px, py, x, y)
        ww = sum( 1 for i in m if i!=4)

        if (w==1 and move==4 and borig[y][x] in [EL_BOMB_BOMBERMAN, EL_BOMBERMAN]):
            pass
        elif borig[y][x] in ELS_NO_MOVE:
            return (MOVE_DEAD, None, None, None, None) 

        if V[y][x]!=0 and m[-1]!=4: #already processed and not wait
            continue

        if r>=MOVE_DEAD:
            continue

        if ww>maxdepth:
            continue

        if borig[y][x] in targets:
            if bdangers[y][x] in ELS_DANGERS:
                pass
            elif bdangers[y][x] in ELS_BLASTS and wdanger:
                pass
            else:
                r = max(r, rate_move(x, y, w, borig, bdangers, bdangerst, lifes))
                if r<=MOVE_MID_RISK:
                    if (r<res_r and dd==res_dd) or (dd>res_dd):
                       res_r=r
                       res_dd=dd
                       res_x=x
                       res_y=y
                       res_m=m
                else:
                    continue

        if V[y][x]==0:
            V[y][x] = 1
        else: 
            V[y][x]+=1


        #for i, (dx,dy) in enumerate(MOVES[:4]) : #including stops
        for i, (dx,dy) in enumerate(MOVES[:4]) : #including stops
            nx, ny, nw, nm  = x+dx, y+dy, w+1, m+[i]
            ndanger = is_danger(nx,ny,nw,lifes,bdangers,bdangerst)
            nr = max(r, rate_move(nx, ny, nw, borig, bdangers, bdangerst, lifes))
            dd = DIST1(px, py, nx, ny)
            if not is_onboard(nx,ny): #outboard
                continue

            if V[ny][nx]!=0:          #already checked
                continue 

            if borig[ny][nx] in targets:
                if borig[ny][nx] in ELS_NO_MOVE and bdangers[y][x] in ELS_DANGERS and w<3:
                    nr = MOVE_DEAD
                elif borig[ny][nx] in ELS_NO_MOVE and bdangers[y][x] in ELS_BLASTS and w<3 and ndanger:
                    nr = MOVE_DEAD
                elif borig[ny][nx] not in ELS_NO_MOVE and bdangers[y][x] in ELS_DANGERS:
                    pass #nr = max(r, MOVE_HIGH_RISK)
                elif borig[ny][nx] not in ELS_NO_MOVE and bdangers[y][x] in ELS_BLASTS and ndanger:
                    pass #nr = max(r, MOVE_HIGH_RISK)
                elif nr<=MOVE_MID_RISK:
                    if (r<res_r and dd==res_dd) or (dd>res_dd):
                       res_r=r
                       res_dd=dd
                       res_x=x
                       res_y=y
                       res_m=m
                if nr>=MOVE_DEAD:
                    continue

            if (borig[ny][nx] in ELS_NO_MOVE) or nw>=DEEP_MAX: #wall or stop deepr
                continue

            if w<5 and bdangers[ny][nx] != EL_NONE: #next is blast, make sense wait only nearest, next will disapper
                #try stops
                minr  = MOVE_DEAD
                wtime = None
                for iw in range(0,6):
                    r0 = rate_move(x, y, w+iw, borig, bdangers, bdangerst, lifes)
                    if r0>=MOVE_DEAD:
                        break #can'stay more
                    r1 = rate_move(nx,ny,nw+iw, borig, bdangers, bdangerst, lifes)
                    rr = max(r0, r1)
                    if rr<minr or wtime==None:
                        minr=rr
                        wtime=iw
                if minr<MOVE_DEAD and wtime>0:
                    nr = max(r, minr)
                    M.append( (nx, ny, nw+wtime, nr, m+[4]*wtime+[i]) )    
                    continue
                elif wtime==0: #no risk
                    pass
                
            #rest
            if nr<MOVE_DEAD:
                M.append( (nx, ny, nw, nr, nm) )    

    # if cur_r!=MOVE_DEAD:
    #     print("FOUND ONLY HI RISK MOVE risk={} dst={}".format(cur_r,cur_w))
    return  (res_r, res_dd, res_x, res_y, res_m)

def count_objects_around(board, x, y, t):
    res=0
    for dx,dy in MOVES[:4]: 
        if is_onboard(x+dx, y+dy):
            if board[y+dy][x+dx] in t:
                res+=1
    return res



def get_dist2targets(x, y, bmain, targets):
    global SZ

    V = [ [0]*SZ for _ in range(SZ)]

    M = deque()
    M.append( (x,y,0) )

    while M:
        x, y, w  = M.popleft()
        
        # if bmain[y][x] in ELS_NO_MOVE: #can't move - skip
        #     assert() #fail sitation

        if V[y][x]==0: #not checked
            V[y][x] = 1
            if bmain[y][x] in targets:
                return w

        #print_board(board)

        for i, (dx,dy) in enumerate(MOVES[:4]): 
            nx, ny, nw = x+dx, y+dy, w+1
            if not is_onboard(nx,ny): #outboard
                continue
            if V[ny][nx]!=0:          #already checked
                continue 
            if ( bmain[ny][nx]in ELS_NO_MOVE):
                continue
            M.append( (nx, ny, nw) )    

    return SZ*SZ #

def estimate_my_move( move ):
    LOGD("ESTIMATE MOVE {}".format(move))
    ns = GSTATE.clone()

    for _tries in range(PREDICT_TRIES):
        res=ns.do_next_cmd( move )

        # print_board(ns.BOARD, True)
        # print_board(ns.DANGERS, True)
        if res==GAMERES_OVER:
            return MOVE_DEAD

        taway_risk, taway_dst, taway_move, taway_x, taway_y, taway_path = get_best_safe_farthest_move( [0,1,2,3,4], ns.me().x(), ns.me().y(), ELS_NOT_DANGER2MOVE, ns.BOARD, ns.DANGERS, ns.DANGERS_t, ns.me().lifes())
        LOGD("RATE MOVE, deep={}: {} = {} {} {} target=({},{}) path={}".format(_tries, move, taway_risk, taway_dst, taway_move, taway_x, taway_y, taway_path))
        if taway_risk>=MOVE_DEAD:
            break
        move=ACTIONS[taway_move]
    return taway_risk


def get_best_move(moves, x, y, targets, nstate, ignoreWalls=False):
    r_safe_move = None
    r_safe_dist = None
    r_safe_rate  = MOVE_DEAD
    r_risky_move = None
    r_risky_dist = None
    r_risky_rate  = MOVE_DEAD
    bmain = nstate.BOARD
    bdangers = nstate.DANGERS
    bdangerst = nstate.DANGERS_t
    lifes = nstate.me().lifes()
    for m in moves:
        r2_rate, r2_dist = check_move(x, y, m, targets, bmain, bdangers, bdangerst, lifes, ignoreWalls)
        if r2_rate>=MOVE_DEAD:
            continue
        #if r2_rate<MOVE_HIGH_RISK:
        nx, ny = get_move_by_idx(x, y, m)
        #
        ncnt = count_objects_around(bmain, nx, ny, ELS_NO_MOVE)
        r2_rate = r2_rate + ncnt/3

        # already counted in rate move
        #nchoppers = count_objects_around(bmain, nx, ny, ELS_CHOPPERS)
        #r2_rate += 0.5*nchoppers
        if  (r_safe_dist     == None           or  r2_dist < r_safe_dist) or \
            (r2_rate         == r_safe_rate    and r2_dist < r_safe_dist) or \
            (r2_dist         == r_safe_dist    and r2_rate < r_safe_rate) or \
            (r2_rate         <  MOVE_HIGH_RISK and r2_dist < r_safe_dist):
                r_safe_dist=r2_dist
                r_safe_move=m
                r_safe_rate=r2_rate
        if  (r_risky_dist    == None           or  r2_dist < r_risky_dist) or \
            (r2_rate         == r_risky_rate   and r2_dist < r_risky_dist) or \
            (r2_dist         == r_risky_dist   and r2_rate < r_risky_rate) or \
            (r2_rate         < MOVE_HIGH_RISK  and r2_dist < r_safe_dist):
                r_risky_dist=r2_dist
                r_risky_move=m
                r_risky_rate=r2_rate
    if r_safe_rate!=MOVE_DEAD:
        #LOG("SAFE MOVE FOUND")
        return (r_safe_rate, r_safe_dist, r_safe_move)
    if r_risky_rate!=MOVE_DEAD:
        LOG("RISKY MOVE FOUND ONLY")
    return (r_risky_rate, r_risky_dist, r_risky_move)


def get_best_move_wall(moves, x, y, nstate, lifes):
    r_safe_move = None
    r_safe_dist = None
    r_safe_rate  = MOVE_DEAD
    r_risky_move = None
    r_risky_dist = None
    r_risky_rate  = MOVE_DEAD
    bmain = nstate.BOARD
    bdangers = nstate.DANGERS
    bdangerst = nstate.DANGERS_t
    lifes = nstate.me().lifes()
    for m in moves:
        r2_rate, r2_dist = check_move_wall(x, y, m, bmain, bdangers, bdangerst, lifes)
        if r2_rate>=MOVE_DEAD:
            continue
        #if r2_rate<MOVE_HIGH_RISK:
        nx, ny = get_move_by_idx(x, y, m)
        #
        ncnt = count_objects_around(bmain, nx, ny, ELS_NO_MOVE)
        r2_rate = r2_rate + ncnt/3

        # already counted in rate move
        #nchoppers = count_objects_around(bmain, nx, ny, ELS_CHOPPERS)
        #r2_rate += 0.5*nchoppers
        if  (r_safe_dist     == None           or  r2_dist < r_safe_dist) or \
            (r2_rate         == r_safe_rate    and r2_dist < r_safe_dist) or \
            (r2_dist         == r_safe_dist    and r2_rate < r_safe_rate) or \
            (r2_rate         <  MOVE_HIGH_RISK and r2_dist < r_safe_dist):
                r_safe_dist=r2_dist
                r_safe_move=m
                r_safe_rate=r2_rate
        if  (r_risky_dist    == None           or  r2_dist < r_risky_dist) or \
            (r2_rate         == r_risky_rate   and r2_dist < r_risky_dist) or \
            (r2_dist         == r_risky_dist   and r2_rate < r_risky_rate) or \
            (r2_rate         < MOVE_HIGH_RISK  and r2_dist < r_safe_dist):
                r_risky_dist=r2_dist
                r_risky_move=m
                r_risky_rate=r2_rate
    if r_safe_rate!=MOVE_DEAD:
        #LOG("SAFE MOVE FOUND")
        return (r_safe_rate, r_safe_dist, r_safe_move)
    if r_risky_rate!=MOVE_DEAD:
        LOG("RISKY MOVE FOUND ONLY")
    return (r_risky_rate, r_risky_dist, r_risky_move)

def get_best_safe_farthest_move(moves, x, y, targets, bmain, bdangers, bdangerst, lifes):
    r_safe_move = None
    r_safe_dist = 0
    r_safe_rate  = MOVE_DEAD
    r_safe_x = None
    r_safe_y = None
    r_safe_path = []
    for m in moves:
        r2_rate, r2_dist, r2_x, r2_y, r2_path = check_move_farthest_safe(x, y, m, targets, bmain, bdangers, bdangerst, lifes)
        if r2_rate>=MOVE_DEAD:
            continue
        nx, ny = get_move_by_idx(x, y, m)
        if  (r2_rate<=MOVE_MID_RISK and r2_dist>=r_safe_dist):
                r_safe_dist=r2_dist
                r_safe_move=m
                r_safe_rate=r2_rate
                r_safe_x = r2_x
                r_safe_y = r2_y
                r_safe_path = r2_path
    if r_safe_move != None:
        LOGD("SAFE point is ({},{})".format(r_safe_x, r_safe_y))
    return (r_safe_rate, r_safe_dist, r_safe_move, r_safe_x, r_safe_y, r_safe_path)

#without rates
def find_path_to_nearest(x, y, bmain, bdangers, targets, maxdist):
    global SZ

    V = [ [0]*SZ for _ in range(SZ)]

    M = deque()
    M.append( (x,y,0,[]) )

    ALLOWED = [     EL_BOMB_BLAST_RADIUS_INCREASE, 
                    EL_BOMB_COUNT_INCREASE,
                    EL_BOMB_IMMUNE,
                    EL_BOMB_REMOTE_CONTROL,
                    EL_BOOM,
                    EL_DESTROYED_WALL,
                    EL_DEAD_BOMBERMAN,
                    EL_OTHER_DEAD_BOMBERMAN,
                    EL_OTHER_BOMBERMAN,
                    EL_OTHER_BOMB_BOMBERMAN,
                    EL_NONE ]


    DANGERS = [] #we will no got him, just check
    while M:
        x, y, w, p  = M.popleft()
        
        if w>maxdist:
            break

        if V[y][x]==0: #not checked
            V[y][x] = 1
            if bmain[y][x] in targets:
                return (x,y,w,p)

        for i, (dx,dy) in enumerate(MOVES[:4]): 
            nx, ny, nw = x+dx, y+dy, w+1
            if not is_onboard(nx,ny): #outboard
                continue
            if V[ny][nx]!=0:          #already checked
                continue 
            if (bmain[ny][nx] not in ALLOWED) or (bdangers[ny][nx] in DANGERS):
                continue
            M.append( (nx, ny, nw, p+[i]) )    

    return (None, None, None, None)

CASE_NONE           = 0
CASE_STAY_NO_ACT    = 1
CASE_ACT_AND_GO     = 2
CASE_ENEMY_HAS_RC_GO_AWAY   = 3
CASE_GO_AND_ACT     = 4
CASE_GO_TO_ACT_IF_FROM = 5

def check_if_player_blocked(x, y, t, d, moves, bmain, bdangers):
    res=0
    for dx,dy in moves: 
        px, py = x+dx, y+dy
        if is_onboard(px, py):
            if bmain[py][px] in t or bdangers[py][px] in d:
                res+=1
    return res

def check_case_bomber_near(x, y, bmain, bdangers):
    res = []
    #1. Find nearest bomber not far as 5 for example
    # for bomber in GSTATE.players().values():
    #     if bomber.ID==0: continue
    #     bx, by = bomber.x(), bomber.y()
    #     if DIST1(x, y, bx, by)>5: #fast check 
    #         return (None, None, None)
    tx, ty, tdst, tpath = find_path_to_nearest(x, y, bmain, bdangers, [EL_OTHER_BOMB_BOMBERMAN,  EL_OTHER_BOMBERMAN], 5)
    if tdst==None:
        return res
    LOG("OTHER BOMBERMAN DETECTED : ({},{}) dst={} path={}".format(tx, ty, tdst, tpath))
    enemy = GSTATE.board_get_player_at(tx, ty)
    if tdst==1: #check if can block just staying
        # case 0 : arounf only walls and me - put bomb
        blocks  =  [EL_WALL, EL_DESTROY_WALL,  EL_OTHER_BOMBERMAN, EL_BOMBERMAN ]
        blocksd =  [EL_BOMB_BLAST_1, EL_BOMB_BLAST_2]
        blocks_cnt = check_if_player_blocked(tx, ty, blocks, blocksd, MOVES, bmain, bdangers)
        if blocks_cnt==5 and GSTATE.me().has_free_bombs():
            res. append( ( CASE_ACT_AND_GO, tx, ty, tdst, tpath) )
        else:
            # case 1 : just wait, not ccompatible with case 0
            blocks  =  [EL_WALL, EL_DESTROY_WALL,  EL_OTHER_BOMBERMAN, EL_OTHER_BOMB_BOMBERMAN, EL_BOMBERMAN, EL_BOMB_TIMER_5,  EL_BOMB_TIMER_4,  EL_BOMB_TIMER_3, EL_BOMB_TIMER_2,  EL_BOMB_TIMER_1 ]
            blocksd =  [EL_BOMB_BLAST_1, EL_BOMB_BLAST_2]
            blocks_cnt = check_if_player_blocked(tx, ty, blocks, blocksd, MOVES, bmain, bdangers)
            if blocks_cnt==5:
                res. append( ( CASE_STAY_NO_ACT, tx, ty, tdst, tpath) )
    #case 2
    elif enemy!=None and tdst<enemy.get_current_blast_size() and enemy.has_remote_perk(): # and enemy.has_free_bombs():
        res. append( ( CASE_ENEMY_HAS_RC_GO_AWAY, tx, ty, tdst, tpath) )
    #case 3
    elif tdst==2: #on one line - two variants, 
        res. append( ( CASE_GO_AND_ACT, tx, ty, tdst, tpath) )
    elif tdst==3: #on one line - two variants, 
        res. append( ( CASE_GO_TO_ACT_IF_FROM, tx, ty, tdst, tpath) )
    else:
        pass

    #return trisk, tdst, tmove
    return res


BLOCKED_COUNTER = 0
DEAD_CHOP_XY = []

def solve(board_string):
    global SZ, BLOCKED_COUNTER, DEAD_CHOP_XY
    global GLOBAL_BOARD_DANGERS_t
    global GLOBAL_BOARD_DANGERS

    
    time_start = time()
    if GSTATE.update_board_from(board_string) != GAMERES_OK:
        LOG("GAME PAUSE")
        return "STOP"


    # if DEBUG:
    #     GSTATE.bombs()[1].owner=0

    LOG("TIME : {} - update_board_from".format(time()-time_start))

    BOARDDANGERS   = GLOBAL_BOARD_DANGERS   = GSTATE.DANGERS
    BOARDDANGERS_t = GLOBAL_BOARD_DANGERS_t = GSTATE.DANGERS_t
    BOARDORIG = GSTATE.BOARD
    SZ = GSTATE.BOARD_SZ

    # print_board(BOARDORIG, True, DFILE)
    # print_board(BOARDDANGERS, True, DFILE)
    # for d in BOARDDANGERS_t:
    #         print(d)

    print_board(BOARDORIG, True, DFILE, boardQt.qt_game)
    print_board(BOARDDANGERS, True)

    x = GSTATE.me().x()
    y = GSTATE.me().y()
    lifes = GSTATE.me().lifes()
    # self destroy    
    is_blocked=count_objects_around(BOARDORIG, x,y,[EL_WALL, EL_DESTROY_WALL])==4
    if is_blocked:
        if BLOCKED_COUNTER==0:
            BLOCKED_COUNTER=50
            return "STOP"
        BLOCKED_COUNTER-=1
        if BLOCKED_COUNTER==1:
            BLOCKED_COUNTER=0
            return "ACT,STOP"

    p_moves = player_get_possible_moves(x,y, BOARDORIG, BOARDDANGERS, lifes)
    LOG("POSSIBLE MOVES {}".format(p_moves))

    twall2_risk,   twall2_dst,   twall2_move  = get_best_move_wall(p_moves, x, y, GSTATE, lifes)
    LOG("TWALL2_RISK : {} {} {}".format(twall2_risk,   twall2_dst,   twall2_move ))

    twall_risk,   twall_dst,   twall_move  = get_best_move(p_moves, x, y, [EL_DESTROY_WALL], GSTATE)
    LOG("TWALL_RISK : {} {} {}".format(twall_risk,   twall_dst,   twall_move ))

    tbomber_risk, tbomber_dst, tbomber_move = get_best_move(p_moves, x, y, [EL_OTHER_BOMBERMAN, EL_OTHER_BOMB_BOMBERMAN], GSTATE)
    LOG("TBOMBER_RISK free: {} {} {}".format(tbomber_risk, tbomber_dst, tbomber_move ))

    tmeat_risk, tmeat_dst, tmeat_move = get_best_move(p_moves, x, y, [EL_MEAT_CHOPPER], GSTATE)
    LOG("TMEAT_RISK free: {} {} {}".format(tmeat_risk, tmeat_dst, tmeat_move ))

    tmeat_x, tmeat_y, tmeat_dst, tmeat_path = find_path_to_nearest(x, y, BOARDORIG, BOARDDANGERS, [EL_MEAT_CHOPPER], 50)
    LOG("TMEAT nearest: ({},{}) : {} {}".format(tmeat_x, tmeat_y, tmeat_dst, tmeat_path ))

    if tbomber_risk>=MOVE_DEAD: #try get blocked ones
        tbomber_risk, tbomber_dst, tbomber_move = get_best_move(p_moves, x, y, [EL_OTHER_BOMBERMAN, EL_OTHER_BOMB_BOMBERMAN], GSTATE, True)
        LOG("TBOMBER_RISK free: {} {} {}".format(tbomber_risk, tbomber_dst, tbomber_move ))


    tfree_risk,   tfree_dst,   tfree_move  = get_best_move(p_moves, x, y, ELS_NOT_DANGER2MOVE, GSTATE)
    LOG("TFREE_RISK : {} {} {}".format(tfree_risk,   tfree_dst,   tfree_move ))

    print("TIME TFREE: {} - RISKS GEN".format(time()-time_start))

    taway_risk, taway_dst,   taway_move, taway_x, taway_y, taway_path = get_best_safe_farthest_move( p_moves, x, y, ELS_NOT_DANGER2MOVE, BOARDORIG, BOARDDANGERS, BOARDDANGERS_t, lifes)
    LOG("TAWAY_RISK : {} {} {} target=({},{}) path={}".format(taway_risk,   taway_dst,   taway_move, taway_x, taway_y, taway_path ))
    print("TIME TAWAY: {} ".format(time()-time_start))

    tstop_risk, tstop_dst,   tstop_move, tstop_x, tstop_y, tstop_path  = get_best_safe_farthest_move( [4], x, y, [EL_DESTROY_WALL], BOARDORIG, BOARDDANGERS, BOARDDANGERS_t, lifes)
    LOG("TSTOP_RISK : {} {} {} target=({},{}) path={}".format(tstop_risk,   tstop_dst,   tstop_move, tstop_x, tstop_y, tstop_path ))
    print("TIME TSTOP: {} ".format(time()-time_start))

  
    tperk_risk,   tperk_dst,   tperk_move  = get_best_move(p_moves, x, y, ELS_PERKS, GSTATE)
    LOG("TPERK_RISK : {} {} {}".format(twall_risk,   twall_dst,   twall_move ))
    
    print("TIME : {} - risks + get_best_move".format(time()-time_start))

    cmd = 'STOP'
    #ATTACK bombers first
    a_bomber_near = False

    tchop_dst_xy  = get_dist2targets(x, y, BOARDORIG, ELS_CHOPPERS)
    LOG("TCHOP_DST_XY = {}".format(tchop_dst_xy))
    print("TIME : {} - get_dist2targets tchop_dst_xy".format(time()-time_start))
    
    deadchop_dst = GSTATE.me_dst2dead_meat_chopper()
    print("TIME : {} - me_dst2dead_meat_chopper 1".format(time()-time_start))

    away_from_dead_chopper = deadchop_dst!=None and deadchop_dst<6
    if away_from_dead_chopper:
        DEAD_CHOP_XY.append(deadchop_dst)
        LOG("DEAD_CHOP detected!!!!")

    no_fire = False
    # if tchop_dst_xy<3:
    #     LOG("NO FIRE : chopper too close")
    #     no_fire = True

    safe2drop = GSTATE.me_safe_to_drop_bomb()
    if not safe2drop:
        LOG("NO FIRE : NOT SAFE to DROP")
        no_fire = True
    
    cmd_found = 'STOP'
    tmeat_near = tmeat_dst !=None  and tmeat_dst<=5
    if tperk_risk<MOVE_DEAD and tperk_dst!=None and tperk_dst<20 and not tmeat_near:
        cmd_found=ACTIONS[tperk_move]
        LOG("Attack perk")
        no_fire = tperk_dst<4
    elif GSTATE.my_rc_bomb() and GSTATE.if_on_my_rc_fireline(x, y):
        if twall2_risk<MOVE_DEAD and twall2_move!=None:
            cmd_found = ACTIONS[twall2_move]
            LOG("Away from bomb")
        elif twall_risk<MOVE_DEAD and twall_move!=None:
            cmd_found = ACTIONS[twall_move]
            LOG("Away from bomb")
        elif taway_risk<MOVE_DEAD and taway_move!=None:
            cmd_found = ACTIONS[taway_move]
            LOG("Away from bomb")
    elif tmeat_risk<=MOVE_HIGH_RISK and tmeat_dst!=None:
        cmd_found=ACTIONS[tmeat_move]
        LOG("Attack choppers")
    elif twall2_risk<MOVE_DEAD and twall2_dst!=None:
        cmd_found=ACTIONS[twall2_move]
        LOG("Attack wallS")
    elif twall_risk<MOVE_DEAD and twall_dst!=None:
        cmd_found=ACTIONS[twall_move]
        LOG("Attack wall")
    # elif tbomber_risk<MOVE_DEAD and tbomber_dst==1 and taway_risk<=MOVE_MID_RISK:
    #     cmd_found=ACTIONS[taway_move]
    #     a_bomber_near = True
    #     LOG("Attack bomber and away safe road")
    # elif tbomber_risk<MOVE_DEAD and tbomber_dst!=None:
    #     cmd_found=ACTIONS[tbomber_move]
    #     a_bomber = True
    #     LOG("Attack bomber")
    elif tfree_risk<MOVE_DEAD and tfree_dst!=None:
        cmd_found=ACTIONS[tfree_move]
        LOG("Attack free")
    else:
        LOG("NO SOLUTIONS")    


    cmd_pre=cmd_post=""

    ########################################################################
    # CHECK for SPECIAL cases
    tcases = check_case_bomber_near(x, y, BOARDORIG, BOARDDANGERS) if not away_from_dead_chopper else []
    tspecial=False
    danger_xy = get_danger(x,y,1,lifes,BOARDDANGERS,BOARDDANGERS_t)
    cnt_around_xy = count_objects_around(BOARDORIG, x, y, ELS_NO_MOVE)
    if tcases:
        LOG("CHECK SPECIAL CASES")
        for tcase, tx, ty, tdst, tpath in tcases:
            tcmd = tpath[0]
            fx, fy = do_move_towards(x,y,tcmd)
            danger_new_xy = get_danger(fx,fy,1,lifes,BOARDDANGERS,BOARDDANGERS_t)
            is_danger_new_xy = danger_new_xy<EL_BOMB_BLAST_2
            if tcase==CASE_STAY_NO_ACT:
                #check if we can just stay
                if  (tstop_risk<=MOVE_MID_RISK and tstop_dst>2):
                    cmd='STOP'
                    tspecial=True
                    LOG("SPECCASE: CASE_STAY_NO_ACT, enemy=({},{}) path={}".format(tx,ty,tpath))
                    break
            if tcase==CASE_ENEMY_HAS_RC_GO_AWAY: 
                    cmd=cmd_found
                    tspecial=True #to block dropping bombs
                    LOG("SPECCASE: CASE_ENEMY_HAS_RC_GO_AWAY, enemy=({},{}) path={}".format(tx,ty,tpath))
                    break
            if tcase==CASE_ACT_AND_GO:
                #check if we can just stay
                if  (taway_risk<=MOVE_MID_RISK and taway_dst>2) and not is_danger_new_xy:
                    cmd = ACTIONS[tcmd]
                    cmd_pre="ACT,"
                    tspecial=True
                    LOG("SPECCASE: CASE_ACT_AND_GO, enemy=({},{}) path={}".format(tx,ty,tpath))
                    break
            if tcase==CASE_GO_AND_ACT:
                #check if we can just stay
                if  (taway_risk<=MOVE_MID_RISK and taway_dst>2) and not is_danger_new_xy:
                    cmd = ACTIONS[tcmd]
                    if cnt_around_xy>2: #can'b easily locked
                        pass
                    elif if_move_towards(x,y,tx,ty,tcmd):
                        LOG("SPECCASE: move to tbomber")
                        cmd_post=",ACT"
                    else:
                        LOG("SPECCASE: move away from bomber")
                        cmd_pre="ACT,"
                    tspecial=True
                    LOG("SPECCASE: CASE_GO_AND_ACT, enemy=({},{}) path={}".format(tx,ty,tpath))
                    break
            if tcase==CASE_GO_TO_ACT_IF_FROM:
                if  (taway_risk<=MOVE_MID_RISK and taway_dst>2) and not danger_xy and not is_danger_new_xy:
                    if BOARDORIG[y][x] in [EL_BOMB_BOMBERMAN] or danger_xy>EL_BOMB_BLAST_2: #hi risk
                        pass #don't attack due to hi risk to be blocked
                    else:
                        cmd = ACTIONS[tcmd]
                        if if_move_towards(x,y,tx,ty,tcmd):
                            cmd_post=",ACT"
                            LOG("SPECCASE: move to tbomber ")
                            pass #just go closer, no bombs
                        else:
                            cmd_pre="ACT," #away - put bomb
                            LOG("SPECCASE: move away from bomber")
                        tspecial=True
                        LOG("SPECCASE: CASE_GO_TO_ACT_IF_FROM, enemy=({},{}) path={}".format(tx,ty,tpath))
                        break

    ########################################################################
    if away_from_dead_chopper and taway_risk<MOVE_DEAD and taway_dst!=None:
        cmd=ACTIONS[taway_move]
        LOG("AWAY from dead chopper free!!!")
    elif tspecial:
        LOG("SPECIAL case - just do it")
    else:
        cmd=cmd_found
        LOG("Do found command")
 
    ### POST CHECK
    if not tspecial:
        wanted = [EL_BOMB_IMMUNE, EL_BOMB_BLAST_RADIUS_INCREASE, EL_BOMB_REMOTE_CONTROL, EL_BOMB_COUNT_INCREASE]
        bomber_close = tbomber_risk<=MOVE_HIGH_RISK and tbomber_dst<5
        LOG("Other bomber near")
        if check_near(BOARDORIG,x,y,wanted) and (twall_risk<MOVE_MID_RISK or tfree_risk<MOVE_MID_RISK) and not bomber_close:
            cmd_near = get_nearest(x,y,wanted, BOARDORIG)
            if cmd_near!=None:
                cmd=cmd_near
                LOG("Take near perk!!!")

    nx, ny = get_move_by_cmd(x,y,cmd)
    #print("TIME : {} - get_move_by_cmd".format(time()-time_start))

    #no_fire = no_fire or tchop_dst_xy<3 #or tdchop_dst<6
   
    targets_pre  = count_fire_targets(BOARDORIG, x, y, )
    LOG("TARGETS_PRE  ORIG  = {}".format(targets_pre))
    targets_post = count_fire_targets(BOARDORIG, nx, ny)
    LOG("TARGETS_POST ORIG = {}".format(targets_post))

    #print("TIME : {} - count_fire_targets".format(time()-time_start))

    check_pre =estimate_my_move("ACT,"+cmd) <= MOVE_MID_RISK
    check_post=estimate_my_move(cmd+",ACT") <= MOVE_MID_RISK
    #print("TIME : {} - put_and_check__bomb".format(time()-time_start))

    ME = GSTATE.me()

    if away_from_dead_chopper and deadchop_dst<4 and GSTATE.my_rc_bomb()==None and safe2drop:
        cmd_pre="ACT,"
    elif tspecial==True:
        LOGD("Speical case: ACT checked already")
    elif not no_fire:
        if GSTATE.my_rc_bomb()!=None: #my rc bomb on board
            bomb = GSTATE.my_rc_bomb()
            me_onfire = GSTATE.if_on_my_rc_fireline(nx, ny)
            rc_targets = count_fire_targets(BOARDORIG, bomb.X, bomb.Y)
            if (not me_onfire): # and encnt>0:
                if (bomb.rc_timer > 1):
                    LOGD("RC REMOTE trigger due to timeout")
                    cmd_pre="ACT,"
                    cmd_post=""
                elif rc_targets>1:
                    LOGD("RC REMOTE trigger - enemy catched")
                    cmd_pre="ACT,"
                    cmd_post=""
            else:
                if taway_risk<MOVE_DEAD and taway_move!=None:
                    cmd = ACTIONS[taway_move]
                elif twall_risk<MOVE_DEAD and twall_move!=None:
                    cmd = ACTIONS[twall_move]
        else:
            if a_bomber_near and check_pre:
                cmd_pre="ACT,"
            # elif targets_pre>targets_post and check_pre:
            #     cmd_pre="ACT,"
            # elif targets_post>targets_pre and check_post:
            #     cmd_post=",ACT"
            # elif targets_post>0  and check_post:
            #     cmd_post=",ACT"
            elif targets_pre>1 and check_pre and not tmeat_near:
                cmd_pre="ACT,"
            elif targets_post>1 and check_post:
                cmd_post=",ACT"
            elif targets_post>0  and check_post:
                cmd_post=",ACT"
            else:
                print("NOTHING or CAN'T ACT")
    else:
        LOG("NO FIRE")

    cmd=cmd_pre+cmd+cmd_post

    LOG("ESTIMATE FINAL MOVE: cmd={}".format(cmd))
    risk = estimate_my_move(cmd) 
    checked = set([cmd] )
    if risk >= MOVE_DEAD:
        
        LOG("BAAAAD MOVE, try just go away")
        LOG("TRY FIND ANY SAFE")

        if cmd_found != cmd:
            cmd = cmd_found
            risk = estimate_my_move(cmd) 
            LOG("GO to FOUND -> {}".format(cmd, ("SAFE","NOT SAFE")[risk>=MOVE_DEAD]))
            checked.add( cmd )

        if risk>=MOVE_DEAD and taway_risk<MOVE_DEAD and taway_move!=None:
            cmd = ACTIONS[taway_move]
            risk = taway_risk
            LOG("GO AWAY, cmd={} risk={} ".format(cmd, risk))
        
        if risk>=MOVE_DEAD and tperk_risk<MOVE_DEAD and tperk_move!=None:
            cmd = ACTIONS[tperk_move]
            risk = tperk_risk
            LOG("GO to PERK, cmd={} risk={} ".format(cmd, risk))

        if risk>=MOVE_DEAD and tfree_risk<MOVE_DEAD and tfree_move!=None:
            cmd = ACTIONS[tfree_move]
            risk = tfree_risk
            LOG("GO to FREE, cmd={} risk={} ".format(cmd, risk))

        if risk>=MOVE_DEAD and twall_risk<MOVE_DEAD and twall_move!=None:
            cmd = ACTIONS[twall_move]
            risk = twall_risk
            LOG("GO to WALL, cmd={} risk={} ".format(cmd, risk))

        min_risk = MOVE_DEAD
        min_move = "STOP"
        if risk>=MOVE_DEAD:
            for cmd in ACTIONS:
                if cmd not in checked:
                    risk = estimate_my_move(cmd) 
                    LOG("GO to WALL -> {}".format(cmd, ("SAFE","NOT SAFE")[risk>=MOVE_DEAD]))
                    checked.add( cmd )
                    if risk<min_risk:
                        min_move = cmd
                        min_risk = risk 
            if min_risk<MOVE_DEAD:
                cmd = min_move
                   
        if risk<MOVE_DEAD:
            LOG("LIVE")
        else:
            LOG("OR DIE!!!!!!")
            cmd = "STOP"

    GSTATE.tact(cmd)
    LOG("TIME : {} - FINAL".format(time()-time_start))
    return cmd
#    return 'ACT'

class DirectionSolver:
    """ This class should contain the movement generation algorithm."""

    def __init__(self):
        pass

    def get(self, board_string):
        #time_start = time()
        LOG("=================================================================================================================")
        LOG("=================================================================================================================")
        LOG("=================================================================================================================")
        #LOG("INPUT STRING: len={} {}".format(len(board_string), board_string))
        res=solve(board_string)
        LOG("FINAL COMMAND  {}".format(res))
        #print("TIME: {}".format(time()-time_start))
        return res


if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
