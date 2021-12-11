#! /usr/bin/env python3

import copy
from bigboard import *
from trackobjects_custom import *
from command import *
from collections import *
from element import *
from qstar import *
import time

GOAL_ATTACK_MAP_AI    = 1
GOAL_ATTACK_MAP_OTHER = 2
#GOAL_ATTACK_AI    = 2 -> NEAR_AI
#GOAL_ATTACK_OTHER = 3 => NEAR_OTHER
GOAL_PERKS        = 4
GOAL_AVOID        = 5
GOAL_GO_NEAR_AI   = 6
GOAL_GO_NEAR_OTHER = 7

#GOAL_WALL         = 
#GOAL_PROFIT       = 

GOAL_CUSTOM_TARGET_NEAR    = 10
GOAL_CUSTOM_RATE_CUSTOM_GOALS_HIT = 11


class BoardsCube(QStar):
    gstate = None
    cube = None

    VMAP = None

    GOALS = []

    HISTORY = []
    HISTORY_LONG = []
    _bigboard = None
    _depth  = None

    attack_mode = ""

    def __init__(self, bigboard, qtgame, gstate, depth=CUBE_DEPTH):
        self.cube = []
        self._bigboard=bigboard
        self._depth=depth
        self.gstate = gstate

        for i in range(depth):
            if i==0:
                board = bigboard.clone(i)
                board.tick0() #some estimation staff for t=0
                board.make_dangers_map(False)
                board.make_objects_map() #OBJECTS_PREV will stay from old
            else:
                board=self.cube[-1].clone(i)
                board.tick()
                board.make_dangers_map(True)
                board.make_objects_map()
            self.cube.append(board)
        self.reset_vmap()
        self.cube_after_init_check()
        self.cube_make_attack_maps()
        if DEBUG_CUBE:
            for i,board in enumerate(self.cube):
                if qtgame and i<=DEBUG_CUBE_DEPTH:
                    time.sleep(DEBUG_CUBE_DELAY)
                    qtgame.update_from(board, gstate, "\n: tick {}".format(i))
            time.sleep(DEBUG_CUBE_DELAY)


    def reset_vmap(self):
        self.VMAP = []
        for t in range(self._depth):
            m = [ [QNode(x,y,t) for x in range(self._bigboard.width)] for y in range(self._bigboard.height) ]
            self.VMAP.append(m)        

    def not_go_further(self, node):
        return False


    def qstar_move_to(self, player, cmd, dstx, dsty, t):
        #
        player.tick()
        board = self.get_board(t)

        player.store_last_pos()
        player.do_cmd(cmd)
        #player.tick()
        player.moved(dstx, dsty, player.get_final_direction_after_cmd(cmd), False)

        if board.BOARD[dsty][dstx]==EICE:
            player.moved_on_ice(True)
        else:
            player.moved_on_ice(False)
        return

    def is_goal_reached(self, node):
        # if we reach any exit for example
        board = self.get_board(node.t)

        if GOAL_ATTACK_MAP_AI in self.GOALS and board.ATTACK_MAP_AI and board.ATTACK_MAP_AI[node.y][node.x]:
            # 
            if node.parent_cmd!=None and node.parent_cmd in COMMANDS_FIRE:
            #### чуть не так - цель достигнута если это команда стрельбы!
                return True

        if GOAL_ATTACK_MAP_OTHER in self.GOALS and board.ATTACK_MAP_OTHER and board.ATTACK_MAP_OTHER[node.y][node.x]:
            # 
            if node.parent_cmd!=None and node.parent_cmd in COMMANDS_FIRE:
            #### чуть не так - цель достигнута если это команда стрельбы!
                return True

        if GOAL_CUSTOM_TARGET_NEAR in self.GOALS:
            if board.is_elements_near(node.x,node.y,self.GOALS):
                return True

        if GOAL_GO_NEAR_AI in self.GOALS:
            #if board.ZOMBIES.is_near_HV(node.x, node.y, 3):
            if board.ZOMBIES.is_near(node.x, node.y, 3):
                return True
             
        #slow
        # if GOAL_ATTACK_AI in self.GOALS:
        #     for d in DIR_ALL:
        #         if self.cube_can_hit_targets(node, d, board.ZOMBIES):
        #             return True

        if GOAL_GO_NEAR_OTHER in self.GOALS:
            if board.PLAYERS.is_near_HV(node.x, node.y, 3):
                return True

        if GOAL_PERKS in self.GOALS:
            if board.PERKS.is_at(node.x, node.y):
                return True

        if GOAL_AVOID in self.GOALS:
            c = board.BOARD[node.y][node.x]
            if c in ELS_FREE_SPACE:
                return True

        ### Just move somewhere????
        return False

    def get_dist2goal(self, node):
        t = min(node.t, len(self.VMAP)-1)
        board = self.cube[t]
        vmap  = self.VMAP[t]

        res = 1000000 #must be greate of any distance in map! 

        if GOAL_CUSTOM_TARGET_NEAR in self.GOALS:
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


    def cube_time_scale_fire(self, r, t):
        t=min( t, len(RATE_FIRE_SCALES)-1)
        return int(r*RATE_FIRE_SCALES[t])

    def cube_rate_fire(self, node, cmd):
        #fire if only target available for example
        if not cmd in COMMANDS_FIRE:
            return 0
        
        t0 = self.time2layer(node.t)
        tl = len(self.VMAP)-1
        #flastlayer = t0==tl

        board0 = self.get_board(t0)
        #me0 = board0.ME
        me_can_fire =  board0.ME.can_fire()

        mdir = DIR_UNKNOWN
        if cmd==CMD_FIRE:
            mdir = board0.ME.rotation
        else:
            mdir = MAP_COMMANDS_FIRE2DIR[cmd]

        if mdir == DIR_UNKNOWN:
            LOG("CAN't check fire: PLAYER dir unknown!!!!")
            return 0

        res    = 0
        t      = t0
        mx, my = node.x, node.y
        dx, dy = DIR2XY[mdir]


        fCont = True
        x,  y  = mx, my
        while fCont:
            t+=1
            t = min(t, tl)
            board = self.get_board(t)

            for th in range(2):
                x += dx
                y += dy

                if not board.is_onboard(x,y):
                    fCont=False
                    break

                c = board.BOARD[y][x]

                if c == ETREE:
                    res+=RATE_FIRE_TREE

                if board.PERKS.is_at(x,y):
                    res+=PENALTY_FIRE_PERK
                    fCont=False
                    break

                if GOAL_CUSTOM_RATE_CUSTOM_GOALS_HIT in self.GOALS:
                    if c in self.GOALS:
                        res+=FIRE_CUSTOM_RATES.get(c,0)

                if c in ELS_BULLET_BARRIER: #PERKS not on BOARD!!! They in Perks
                    fCont=False
                    break

                # HIT PREDICTION
                #check for player            
                p = board.PLAYERS.get_at(x,y)
                if p!=None:
                    if not p.is_immortal(1):
                        if p.cnt_same_position>=PLAYER_SAME_POSITION_DETECT:
                            res+=self.cube_time_scale_fire(RATE_FIRE_PLAYER, t)
                        else:
                            bForceAttack = False
                            if FORCE_DUEL and t0==0 and me_can_fire: #Duel only at first move
                                p0 = board0.PLAYERS.objects_get_by_id(p.ID) #take zombie at initial time
                                zdx, zdy = abs(mx-p0.X), abs(my-p0.Y)
                                if zdx==0 or zdy==0:#on one fireline only!!!
                                    bForceAttack = max(zdx,zdy)<=2 
                            if bForceAttack:
                                res+=RATE_FIRE_PLAYER_FORCE_DUEL
                            else:
                                res+=self.cube_time_scale_fire(RATE_FIRE_PLAYER, t)

                z = board.ZOMBIES.get_at(x,y) 
                if z!=None:
                    if z.est_is_stuck:
                        res+=self.cube_time_scale_fire(RATE_FIRE_ZOMBIE_EST_STUCK, t)
                    else:
                        bForceAttack = False
                        if FORCE_DUEL and t0==0 and me_can_fire:
                            z0 = board0.ZOMBIES.objects_get_by_id(z.ID) #take zombie at initial time
                            zdx, zdy = abs(mx-z0.X), abs(my-z0.Y)
                            if zdx==0 or zdy==0:#on one fireline only!!!
                                bForceAttack = max(zdx,zdy)<=2 
                        if bForceAttack:
                            res+=RATE_FIRE_ZOMBIE_FORCE_DUEL
                        else:
                            res+=self.cube_time_scale_fire(RATE_FIRE_ZOMBIE, t)

                #try hit neighbor
                if t==1 and th==0:
                    if board0.PLAYERS.is_at(x,y):
                        res+=self.cube_time_scale_fire(RATE_FIRE_PLAYER, t)

                    zombie = board0.ZOMBIES.get_at(x,y)
                    if zombie!=None and not zombie.can_fire():
                        res+=RATE_FIRE_ZOMBIE_DUEL_SAFE


       
        # if res:
        #     LOG("FIRE rate of {} = {}".format( COMMANDS[cmd],res))
        return res


    #too slow
    # def cube_can_hit_targets(self, node, mdir, targets):
    #     return False

    def get_possible_moves(self, node):

        t0 = self.time2layer(node.t)
        x0, y0 = node.x, node.y

        flastlayer = t0==(len(self.VMAP)-1)

        res = set()
        if flastlayer:
            moves = COMMANDS_NOTSTAY #to not stuck in recursion
        else:
            #moves = (COMMANDS_ANY_NOT_FIRE, COMMANDS_ANY)[t0==0]
            moves = COMMANDS_ANY

        board0 = self.get_board(t0)
        
        if node.player and node.player.sliding_cnt>0:
            cparent=(node.parent_cmd, self._bigboard.last_cmd)[t0==0]
            if cparent == CMD_FIRE:
                cparent-=CMD_FIRE
            moves=[cparent]


        c0 = board0.BOARD[x0][y0]
        for cmd in moves:
            dx, dy, fire = COMMANDS_XYF[cmd]

            #check if wall or die
            x1, y1, t1 = x0+dx, y0+dy, t0+1

            board1=self.get_board(t1)

            if not board1.is_onboard(x1, y1):
                continue

            c1 = board1.BOARD[y1][x1]

            if c1 in ELS_PLAYER_NO_MOVES:
                continue


            #check if bullet hits
            chance = board0.BULLETS.hit_chance(x1, y1)
            if chance==100:
                continue

            # bullet is shifted in time !!!
            if CHECK_BULLET_NEW: #!!! NEED TO ADAPT
                if board0.BULLETS.is_at(x0,y0): #bullet at old position
                    continue
                if board0.BULLETS.is_at(x1,y1): #if we go to cell were was bullet - also dead
                    continue
                if board1.BULLETS.is_at(x1,y1): #bullet at new position
                    continue
            else: #assured already
                if board0.BULLETS.is_at(x0,y0): #bullet at old position
                    continue
                if board0.BULLETS.is_at(x1,y1): #if we go to cell were was bullet - also dead
                    continue
                if board1.BULLETS.is_at(x1,y1): #bullet at new position
                    continue

            if cmd in COMMANDS_FIRE:
                # if t0==0 and board0.ME.can_fire():
                #     #r = board.rate_move_fire(cmd)
                #     r = self.cube_rate_fire(node, cmd)
                #     if r<=RATE_FIRE_MAKE_SHOT:
                #         res.add(cmd)
                if board0.ME.can_fire():
                    r = self.cube_rate_fire(node, cmd)
                    if r<=RATE_FIRE_MAKE_SHOT:
                        res.add(cmd)
                continue

            if board1.PLAYERS.is_at(x1,y1): 
                continue

            if board1.ZOMBIES.is_at(x1,y1): 
                continue
            
            zmb = board0.ZOMBIES.get_at(x1,y1) #zombie stay in position were I wil go and looks to me - not move
            if zmb!=None:
                zest, zx, zy = zmb.estimate_next_pos()
                if zest and zx==x0 and zy==y0 and cmd not in COMMANDS_FIRE: #swap me and zombie impossible but can fire
                    continue

            if board1.DANGERS_MAP:
                d = board1.DANGERS_MAP[y1][x1]
                if d==RATE_DEATH:
                    continue
            
            # if GOAL_PERKS in self.GOALS:
            #     if board0.PERKS.is_at(x0, y0): #I'm already got perk
            #         continue

            res.add(cmd)
        return res

    def get_neighbor(self, node, cmd):
        dt = 1
        dx, dy, fire = COMMANDS_XYF[cmd]
        nx, ny, nt = node.x+dx, node.y+dy, node.t+dt
        vmap  = self.get_vmap(nt)
        return vmap[ny][nx]


    def rate_move(self, node, cmd):
        # Rate this move
        dt = 1
        dx, dy, fire = COMMANDS_XYF[cmd]

        x0, y0, t0 = node.x, node.y, node.t
        x1, y1, t1 = x0+dx, y0+dy, t0+dt

        board0 = self.get_board(t0)
        board1 = self.get_board(t1)

        res = RATE_MOVE_STEP[dt] # minimal rate to allow find shortest paths

        b0 = board0.BOARD[y0][x0]
        b1 = board1.BOARD[y1][x1]

        # #if perk in new position
        # if b1 in ELS_PERKS:
        #     #res += RATE_MOVE_PERK #try get perk
        #     res += RATE_MOVE_TAKE_PERK[b1]

        perk1 = board1.PERKS.get_perk_at(x1,y1)
        if perk1!=None:
            res += RATE_MOVE_TAKE_PERK[perk1.perk_type]
        bIgnoreDanger = False

        if cmd in COMMANDS_FIRE:
            #profit = board.rate_move_fire(cmd)
            profit = self.cube_rate_fire(node, cmd)
            if profit!=0: #<0
                res+=profit
                #LOG("CAN FIRE cmd={} t={} at ({},{}), profit={}".format(COMMANDS[cmd], node.t, node.x, node.y, profit))

        if not bIgnoreDanger:
            #check danger map
            if board1.DANGERS_MAP:
                d1 = board1.DANGERS_MAP[y1][x1]
                if d1:
                    res += d1
        return res


    def get_best_path(self, srcX, srcY):
        if not self.cube: 
            return None

        res = None
        board = self.cube[0]
        start = self.VMAP[0][srcY][srcX]
        start.player = copy.deepcopy(board.ME)

        print("AUTO    : ", end="")        


        #check for special cases
        # case: P-M

        #check for fire

        ### Attack nearest palyer
        #self.attack_mode = "ATTACK: OTHER"
        #self.GOALS = {GOAL_ATTACK_MAP_OTHER}
        #self.reset_vmap()
        #score, res = self.search(start, False)
        #LOG("RES ATTACK NEAREST: score={} res={}".format(score, res))
        #nobody2attack = res==None
        #if res!=None and score<RATE_VERY_RISKY:
        #    return res


        ### 1
        #nobody2attack = False #usually if in jail
        #self.attack_mode = "ATTACK: AI+PERKS"
        #self.GOALS = {GOAL_ATTACK_MAP_AI, GOAL_PERKS, GOAL_GO_NEAR_AI, GOAL_GO_NEAR_OTHER}
        #self.reset_vmap()
        #score, res = self.search(start)
        #LOGF("RES ANY GOALS: score={} res={}".format(score, res))
        #nobody2attack = res==None
        #if res!=None and score<RATE_RISKY:
        #     return res

        nobody2attack = False #usually if in jail
        self.attack_mode = "ATTACK: AI+PERKS"
        self.GOALS = {GOAL_ATTACK_MAP_AI, GOAL_ATTACK_MAP_OTHER, GOAL_PERKS, GOAL_GO_NEAR_AI, GOAL_GO_NEAR_OTHER}
        self.reset_vmap()
        score, res = self.search(start, True)
        LOGF("RES ANY GOALS: score={} res={}".format(score, res))
        nobody2attack = res==None
        if res!=None and score<RATE_RISKY:
            return res

        if nobody2attack:
            if board.ME.can_fire(): #digging in jail
                self.attack_mode = "ATTACK: DIGGING"               
                self.GOALS = {GOAL_CUSTOM_TARGET_NEAR, GOAL_CUSTOM_RATE_CUSTOM_GOALS_HIT} | ELS_WALLS
                self.reset_vmap()
                score, res = self.search(start, True, set(COMMANDS_FIRE))
                LOGF("RES DIGGING: score={} res={}".format(score, res))
                if res!=None and score<RATE_RISKY:
                    return res
            else:
                #go to nearest walls
                self.attack_mode = "ATTACK: go to WALLS"
                self.GOALS = {GOAL_CUSTOM_TARGET_NEAR} | ELS_WALLS
                self.reset_vmap()
                score, res = self.search(start, True)
                LOGF("RES DIGGING: score={} res={}".format(score, res))
                if res!=None and score<RATE_RISKY:
                    return res

        self.attack_mode = "ATTACK: AVOID"               
        self.GOALS = {GOAL_AVOID}
        self.reset_vmap()
        score, res = self.search(start)
        LOGF("RES AVOID: score={} res={}".format(score, res))
        if res!=None and score<RATE_VERY_RISKY:
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

    def cube_after_init_check(self):
        # check all object - fire goals - for lifespan
        board0 = self._bigboard
        for ib in range(board0.BULLETS.size()):
            b=board0.BULLETS.get(ib)
            if b.direction==DIR_UNKNOWN: #unknown - skip check
                continue
            dx, dy = DIR2XY[b.direction]

            t = 0
            mx, my = b.X, b.Y

            fCont = True
            x,  y  = mx, my
            while fCont:
                t+=1
                board = self.get_board(t)

                for th in range(2):
                    x += dx
                    y += dy

                    if not board.is_onboard(x,y):
                        fCont=False
                        break

                    c = board.BOARD[y][x]
                    if c in ELS_BULLET_BARRIER:
                        fCont=False
                        break

                    objects = board.OBJECTS_MAP.get( (x,y),None)
                    if objects==None:
                        continue
                    objid, obj = objects 
                    #cloned object!
                    o = board0.OBJECTS_MAP_ID2OBJ.get(objid, None)
                    if o!=None:
                        if o.est_lifetime==None or t<o.est_lifetime:
                            o.est_lifetime = t
                            o.est_killer_id = b.parent_id
        

    def cube_make_attack_maps(self):
        self._bigboard.make_attack_map2()
        for b in self.cube:
            b.make_attack_map2()
