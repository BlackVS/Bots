#! /usr/bin/env python3

import copy
from bigboard import *
# from trackobjects_custom import *
# from command import *
from collections import *
from model_commands import CMD_FIRE_FLOOR_RIGHT, CMD_FIRE_LEFT, CMD_LEFT
from model_game_goals import GOAL_AVOID
# from element import *
from qstar import *
import time
from model import *

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
                board.simulate_tick0() #some estimation staff for t=0
                board.make_dangers_map(False)
                board.make_objects_map() #OBJECTS_PREV will stay from old
            else:
                board=self.cube[-1].clone(i)
                board.make_possible_moves_map()
                board.simulate()
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
                    qtgame.draw_board_big(board, gstate, "\n: tick {}".format(i))
            time.sleep(DEBUG_CUBE_DELAY)



    ### VMAPS

    def reset_vmap(self):
        self.VMAP = []
        for t in range(self._depth):
            m = [ [QNode(x,y,t) for x in range(self._bigboard.width)] for y in range(self._bigboard.height) ]
            self.VMAP.append(m)        


    def get_vmap(self, t):
        t = min(t, len(self.VMAP)-1)
        return self.VMAP[t]


    ### CUSTOMIZED QSTAR
    def qstar_not_go_further(self, node):
        return False


    def qstar_move_to(self, player, cmd, dstx, dsty, t):
        #
        player.tick()
        board = self.get_board(t)

        player.store_last_pos()
        player.do_cmd(cmd)
        #player.tick()
        player.tick_moved_event(dstx, dsty, player.qstar_object_direction_after_cmd(cmd), False)

    def qstar_is_possible_multi_solution(self, node):
        # For a given node check if goal/goals reached
        return node.profit>0 and self.qstar_is_goal_reached_simple(node)


    def qstar_is_goal_reached_simple(self, node):
        # if we reach any exit for example
        board = self.get_board(node.t)

        # if GOAL_ATTACK_MAP_AI in self.GOALS and board.ATTACK_MAP_AI and board.ATTACK_MAP_AI[node.y][node.x]:
        #     # 
        #     if node.parent_cmd!=None and node.parent_cmd in CMDS.COMMANDS_FIRE:
        #     #### чуть не так - цель достигнута если это команда стрельбы!
        #         return True

        # if GOAL_ATTACK_MAP_OTHER in self.GOALS and board.ATTACK_MAP_OTHER and board.ATTACK_MAP_OTHER[node.y][node.x]:
        #     # 
        #     if node.parent_cmd!=None and node.parent_cmd in CMDS.COMMANDS_FIRE:
        #     #### чуть не так - цель достигнута если это команда стрельбы!
        #         return True

        if GOAL_CUSTOM_TARGET_NEAR in self.GOALS:
            if board.is_elements_near(node.x,node.y,self.GOALS):
                return True

        # if GOAL_GO_NEAR_AI in self.GOALS:
        #     #if board.ZOMBIES.is_near_HV(node.x, node.y, 3):
        #     if board.ZOMBIES.is_near(node.x, node.y, 3):
        #         return True
             
        #slow
        # if GOAL_ATTACK_AI in self.GOALS:
        #     for d in DIR_ALL:
        #         if self.cube_can_hit_targets(node, d, board.ZOMBIES):
        #             return True

        # if GOAL_GO_NEAR_OTHER in self.GOALS:
        #     if board.PLAYERS.is_near_HV(node.x, node.y, 2):
        #         return True

        if GOAL_PERKS in self.GOALS:
            if not board.player_is_falling(node.x, node.y): # final step should be stable or can't predict
                #get perk and stay
                if board.PERKS.is_at(node.x, node.y):
                    return True
                #or if already got perk and stay
                if node.perks>0:
                    return True

        if GOAL_CUSTOM_TARGET in self.GOALS:
            if board.BOARD[node.y][node.x] in self.GOALS:
                return True

        if GOAL_ME in self.GOALS:
            if node.x==board.ME.X and node.y==board.ME.Y:
                return True

        if GOAL_AVOID in self.GOALS:
            return True #any non death

        return False


    def qstar_get_dist2goal(self, node):
        t = min(node.t, len(self.VMAP)-1)
        board = self.cube[t]
        vmap  = self.VMAP[t]

        res = 1000000 #must be greate of any distance in map! 

        if GOAL_CUSTOM_TARGET_NEAR in self.GOALS:
            return 1 #just BFS to reduce time
        
        return res

    def qstar_zombie_get_possible_moves(self, node):
        t0 = self.time2layer(node.t)
        x0, y0 = node.x, node.y

        flastlayer = t0==(len(self.VMAP)-1)

        board0 = self.get_board(t0)

        res = set()

        moves = set(board0.PLAYER_POSSIBLE_MOVES[y0][x0]) & set(ZOMBIE_POSSIBLE_MOVES)

        c0 = board0.BOARD[y0][x0]

        if c0 == ELB.EB_ZOMBIE_IN_PIT:
            moves = set() #stuck in pit

        for cmd in moves:
            dx, dy, dt = CMDS.QSTAR_COMMAND_DXYW_TOTAL(cmd)
            x1, y1, t1 = x0+dx, y0+dy, t0+dt

            board1=self.get_board(t1)

            if not board1.is_onboard(x1, y1):
                continue

            c1 = board1.BOARD[y1][x1]

            if c1 in MMOVES.ZOMBIE_BARRIER:
                continue
            res.add(cmd)
        return res

    def qstar_get_possible_moves(self, node):
        if GOAL_ME in self.GOALS: #all moves for Zombie
            return self.qstar_zombie_get_possible_moves(node)

        t0 = self.time2layer(node.t)
        x0, y0 = node.x, node.y

        flastlayer = t0==(len(self.VMAP)-1)

        board0 = self.get_board(t0)

        res = set()

        if t0==0:
            allowed_moves = set(PLAYER_ALLOWED_MOVES_FIRST)
        else:
            allowed_moves = set(PLAYER_ALLOWED_MOVES_NEXT)

        if PLAYER_NOT_HIT_LAST_DUMMY and board0.is_only_one_dummy_player_left():
            allowed_moves = allowed_moves.difference(set(CMDS.CMDS_FIRE_BULLET))

        if PLAYER_NOT_HIT_LAST and board0.is_only_one_player_left():
            allowed_moves = allowed_moves.difference(set(CMDS.CMDS_FIRE_BULLET))

        if board0.PLAYER_POSSIBLE_MOVES:
            moves = set(board0.PLAYER_POSSIBLE_MOVES[y0][x0]) # copy!
            moves &= allowed_moves

        if flastlayer:
            moves &= set(PLAYER_MOVES_LAST_LAYER) #to not stuck in recursion

        c0 = board0.BOARD[y0][x0]
        for cmd in moves:
            if cmd == CMDS.CMD_NULL:
                cmd = CMDS.CMD_STOP
            dx, dy, dt = CMDS.QSTAR_COMMAND_DXYW_TOTAL(cmd)

            #check if wall or die
            x1, y1, t1 = x0+dx, y0+dy, t0+dt

            board1=self.get_board(t1)

            if not board1.is_onboard(x1, y1):
                continue

            c1 = board1.BOARD[y1][x1]



            # if c1 in MMOVES.PLAYER_BARRIER:
            #     continue

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

            #BERSERK MODE = push before DANGER MAP Check
            # if cmd in CMDS.COMMANDS_FIRE:
            #     if board0.ME.can_fire():
            #         r = self.cube_rate_fire(node, cmd)
            #         if r<=RATE_FIRE_MAKE_SHOT:
            #             res.add(cmd)
            #     continue

            if board1.PLAYERS.is_at(x1,y1): # !!!!
                if not board0.ME.is_immortal_nextXmoves(6): #5 due to have time to go away - can fire!
                    continue

            if board1.ZOMBIES.is_at(x1,y1): # !!!!
                if not board0.ME.is_immortal_nextXmoves(4): #5 due to have time to go away
                    continue
            
            zmb = board0.ZOMBIES.get_at(x1,y1) 
            if zmb!=None:
                continue

            if board1.DANGERS_MAP:
                d = board1.DANGERS_MAP[y1][x1]
                if d==RATE_DEATH:
                    continue
            
            # when search perks not go to blackholes
            if GOAL_PERKS in self.GOALS:
                if c1 == ELB.EB_BACKWAY:
                    continue
            # if GOAL_PERKS in self.GOALS:
            #     if board0.PERKS.is_at(x0, y0): #I'm already got perk
            #         continue

            res.add(cmd)
        return res

    def qstar_get_target(self, node, cmd):
        dx, dy, dt = CMDS.QSTAR_COMMAND_DXYW_TOTAL(cmd)
        nx, ny, nt = node.x+dx, node.y+dy, node.t+dt
        vmap  = self.get_vmap(nt)
        return vmap[ny][nx]

    def qstar_rate_move(self, node, cmd):
        profit = 0
        # Rate this move
        dx, dy, dt, dr = CMDS.QSTAR_COMMAND_DXYWR_TOTAL(cmd)

        x0, y0, t0 = node.x, node.y, node.t
        x1, y1, t1 = x0+dx,  y0+dy,  t0+dt

        board0 = self.get_board(t0)
        board1 = self.get_board(t1)

        res = dr # minimal rate to allow find shortest paths

        if GOAL_CONFIG_IGNORE_DANGERS in self.GOALS:
            return (res, profit)

        b0 = board0.BOARD[y0][x0]
        b1 = board1.BOARD[y1][x1]

        # #if perk in new position
        # if b1 in EL.ELS_PERKS:
        #     #res += RATE_MOVE_PERK #try get perk
        #     res += RATE_MOVE_TAKE_PERK[b1]

        perk1 = board1.PERKS.get_perk_at(x1,y1)
        if perk1!=None:
            if dx!=0 or dy!=0: #optimization
                if (perk1.X, perk1.Y) not in node.perks_taken:
                    res    += RATE_MOVE_TAKE_PERK[perk1.perk_type] #for min paths getting
                    profit += board0.ME.take_perk_profit(perk1)
        #bBerserk = True
        bIgnoreDanger = False

        if cmd in CMDS.CMDS_FIRE_BULLET:
            if QSTAR_CHECK_FIRE:
                #profit = board.rate_move_fire(cmd)
                pbullet = self.cube_rate_fire_profit(node, cmd)
                if pbullet!=0: #<0
                    profit += pbullet
                    res    += RATE_MOVE_HIT_PLAYER
                    #LOG("CAN FIRE cmd={} t={} at ({},{}), profit={}".format(COMMANDS[cmd], node.t, node.x, node.y, profit))

        if not bIgnoreDanger:
            #check danger map
            if board1.DANGERS_MAP:
                d1 = board1.DANGERS_MAP[y1][x1]
                if d1:
                    res += d1
        return (res, profit)

    #########################################################################################

    def get_board(self, t):
        t = min(t, len(self.cube)-1)
        return self.cube[t]

    def time2layer(self, t):
        t = min(t, len(self.VMAP)-1)
        return t


    def cube_time_scale_fire(self, r, t):
        t=min( t, len(RATE_FIRE_SCALES)-1)
        return int(r*RATE_FIRE_SCALES[t])

    def cube_rate_fire_profit(self, node, cmd):
        #fire if only target available for example
        if not cmd in CMDS.CMDS_FIRE_BULLET:
            return 0
        
        t0 = self.time2layer(node.t)
        tl = len(self.VMAP)-1
        #flastlayer = t0==tl

        board0 = self.get_board(t0)


        #me0 = board0.ME
        me_can_fire =  board0.ME.can_fire()

        mdir = DIR_UNKNOWN
        if cmd==CMDS.CMD_FIRE:
            mdir = board0.ME.DIR
        else:
            mdir = CMDS.CMDS_FIRE_BULLET[cmd]

        if mdir == DIR_UNKNOWN:
            LOG("CAN't check fire: PLAYER dir unknown!!!!")
            return 0

        res    = 0
        t      = t0
        mx, my = node.x, node.y
        dx, dy = DIR2XY[mdir]


        fCont = True
        x,  y  = mx, my
        while fCont and t<CUBE_MAX_FIRE_DISTANCE_CHECK:
            t+=1
            t = min(t, tl)
            board = self.get_board(t)

            for th in range(CONFIG_CUSTOM.bullet_hits_cells):
                x += dx
                y += dy

                if not board.is_onboard(x,y):
                    fCont=False
                    break

                c = board.BOARD[y][x]

                # if board.PERKS.is_at(x,y):
                #     res+=PENALTY_FIRE_PERK
                #     fCont=False
                #     break

                # if GOAL_CUSTOM_RATE_CUSTOM_GOALS_HIT in self.GOALS:
                #     if c in self.GOALS:
                #         res+=FIRE_CUSTOM_RATES.get(c,0)

                if c in MMOVES.BULLET_BARRIER:
                    fCont=False
                    break

                bul =  board.BULLETS.get_at(x,y)
                if bul!=None:
                    #already will be killed by somebody - not sense
                    if bul.DIR == mdir:
                        break
                    if bul.DIR == DIR_UNKNOWN:
                        break #may be already will be killed

                # HIT PREDICTION
                #check for player            
                p = board.PLAYERS.get_at(x,y)
                if p!=None:
                    if board0.target_already_under_attack(mx, my, mdir, p.X, p.Y):
                        pass
                    else:
                        if not p.is_immortal_nextXmoves(1):
                            if p.is_dummy():
                                res+=RATE_HIT_PLAYER_DUMMY
                            else:
                                bForceAttack = False
                                if CUBE_FORCE_DUEL and t0==0 and me_can_fire: #Duel only at first move
                                    p0 = board0.PLAYERS.objects_get_by_id(p.ID) #take zombie at initial time
                                    zdx, zdy = abs(mx-p0.X), abs(my-p0.Y)
                                    if zdx==0 or zdy==0:#on one fireline only!!!
                                        bForceAttack = max(zdx,zdy)<=2 
                                if bForceAttack:
                                    res+=RATE_HIT_PLAYER_FORCE_DUEL
                                else:
                                    res+=RATE_HIT_PLAYER_CUBE #self.cube_time_scale_fire(RATE_FIRE_PLAYER, t)

                # z = board.ZOMBIES.get_at(x,y) 
                # if z!=None:
                #     if z.est_is_stuck:
                #         res+=self.cube_time_scale_fire(RATE_FIRE_ZOMBIE_EST_STUCK, t)
                #     else:
                #         bForceAttack = False
                #         if FORCE_DUEL and t0==0 and me_can_fire:
                #             z0 = board0.ZOMBIES.objects_get_by_id(z.ID) #take zombie at initial time
                #             zdx, zdy = abs(mx-z0.X), abs(my-z0.Y)
                #             if zdx==0 or zdy==0:#on one fireline only!!!
                #                 bForceAttack = max(zdx,zdy)<=2 
                #         if bForceAttack:
                #             res+=RATE_FIRE_ZOMBIE_FORCE_DUEL
                #         else:
                #             res+=self.cube_time_scale_fire(RATE_FIRE_ZOMBIE, t)

                #try hit neighbor
                if t==1 and th==0:
                    if board0.PLAYERS.is_at(x,y):
                        res+=RATE_HIT_PLAYER_NEIGHBOUR_CUBE #self.cube_time_scale_fire(RATE_FIRE_PLAYER, t)

                    # zombie = board0.ZOMBIES.get_at(x,y)
                    # if zombie!=None and not zombie.can_fire():
                    #     res+=RATE_FIRE_ZOMBIE_DUEL_SAFE

        # if res:
        #     LOG("FIRE rate of {} = {}".format( COMMANDS[cmd],res))
        return res


    def cube_after_init_check(self):
        # check all object - fire goals - for lifespan
        board0 = self._bigboard
        for ib in range(board0.BULLETS.size()):
            b=board0.BULLETS.get(ib)
            if b.DIR==DIR_UNKNOWN: #unknown - skip check
                continue
            dx, dy = DIR2XY[b.DIR]

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
                    if c in MMOVES.BULLET_BARRIER:
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
        # self._bigboard.make_attack_map2()
        # for b in self.cube:
        #     b.make_attack_map2()
        return



    def has_stuck(self):
        if len(self.HISTORY)<CUBE_HISTORY_LEN:
            return False
        return all(c==self.HISTORY[0] for c in self.HISTORY[1:])

    def has_stuck_to_long(self):
        if len(self.HISTORY_LONG)<CUBE_LONG_HISTORY_LEN:
            return False
        return all(c==self.HISTORY_LONG[0] for c in self.HISTORY_LONG[1:])

    def get_best_move(self, srcX, srcY):
        res, score = self.get_best_path(srcX, srcY)

        if len(self.HISTORY)<CUBE_HISTORY_LEN:
            self.HISTORY.append(res)
        else:
            self.HISTORY=self.HISTORY[1:] + [res]

        if len(self.HISTORY_LONG)<CUBE_LONG_HISTORY_LEN:
            self.HISTORY_LONG.append(res)
        else:
            self.HISTORY_LONG=self.HISTORY_LONG[1:] + [res]

        return res, score

    def LOGRES(self, s, r): 
        if r==None:
            self.gstate.time_log("", " {} SCORE: {} CMDS: {}".format(self.attack_mode, s, r))
        else:
            self.gstate.time_log("", " {} SCORE: {:.2f} CMDS: {}".format(self.attack_mode, s, CMDS.COMMAND_DESC(r[0]) ) )

    def LOGRESMULTI(self, s, r, p, pp): 
        if r==None:
            self.gstate.time_log("", " {} SCORE: {} CMDS: {}".format(self.attack_mode, s, r))
        else:
            self.gstate.time_log("", " {} SCORE: {:3.2f} PROF_RATE: {:3.2f} PERK_RATE: {:3.2f} CMDS: {}".format(self.attack_mode, s, p, pp, CMDS.COMMAND_DESC(r[0]) ) )


    def get_best_path(self, srcX, srcY):
        if not self.cube: 
            return None


        risky_res   = None
        risky_score = RATE_DEATH

        board = self.cube[0]

        #return self.get_best_path_berserk(srcX, srcY)
        

        #print("AUTO    : ", end="")        
        print("AUTO    : ")
        mx, my = self.gstate.BOARD.ME.X, self.gstate.BOARD.ME.Y


        ##################################################################################
        # SPECIAL CASES

        ##################################################################################
        # CHECK if DUEL
        # if board.BOARD[my][mx-1] not in MMOVES.BULLET_BARRIER and board.PLAYERS.is_at(mx-2, my): #opposite - 100% can hit me
        #     return [CMDS.CMD_FIRE_LEFT], RATE_VERY_RISKY
        # if board.BOARD[my][mx+1] not in MMOVES.BULLET_BARRIER and board.PLAYERS.is_at(mx+2, my): #opposite - 100% can hit me
        #     return [CMDS.CMD_FIRE_RIGHT], RATE_VERY_RISKY
        # if board.BOARD[my][mx] == ELB.EB_LADDER: #can fire on ladder also up/down!!!
        #     if board.BOARD[my-1][mx] not in MMOVES.BULLET_BARRIER and board.PLAYERS.is_at(mx, my-2): #opposite - 100% can hit me
        #         return [CMDS.CMD_FIRE_UP], RATE_VERY_RISKY
        #     if board.BOARD[my+1][mx] not in MMOVES.BULLET_BARRIER and board.PLAYERS.is_at(mx, my+2): #opposite - 100% can hit me
        #         return [CMDS.CMD_FIRE_DOWN], RATE_VERY_RISKY
        if any(FORCE_DUEL_MAP):
            d = board.bullet_can_hit_player_dist(mx,my, -1,0, len(FORCE_DUEL_MAP))
            if d!=None and FORCE_DUEL_MAP[d]:
                print("DUEL LEFT")
                return [CMDS.CMD_FIRE_LEFT], RATE_VERY_RISKY
            d = board.bullet_can_hit_player_dist(mx,my,  1,0, len(FORCE_DUEL_MAP))
            if d!=None and FORCE_DUEL_MAP[d]:
                print("DUEL RIGHT")
                return [CMDS.CMD_FIRE_RIGHT], RATE_VERY_RISKY
            if board.BOARD[my][mx] == ELB.EB_LADDER:
                d = board.bullet_can_hit_player_dist(mx,my, 0,-1, len(FORCE_DUEL_MAP))
                if d!=None and FORCE_DUEL_MAP[d]:
                    print("DUEL UP")
                    return [CMDS.CMD_FIRE_UP], RATE_VERY_RISKY
                d = board.bullet_can_hit_player_dist(mx,my, 0,1, len(FORCE_DUEL_MAP))
                if d!=None and FORCE_DUEL_MAP[d]:
                    print("DUEL DOWN")
                    return [CMDS.CMD_FIRE_DOWN], RATE_VERY_RISKY
        

        ##################################################################################
        # CHECK if new Zombies


        zombies = self.gstate.BOARD.ZOMBIES
        zdist = Infinite
        zpath = None
        for iz in range(zombies.size()):
            z = zombies.get(iz)
            if z==None:
                continue
            dst = abs(z.X-mx)+abs(z.Y-my)
            if dst > 10:
                continue #not check if far
            zstart = self.VMAP[0][z.Y][z.X]
            zstart.player = copy.deepcopy(z)

            self.attack_mode = "ZOMBIE {} CHECK".format(z.ID)
            self.GOALS = {GOAL_ME, GOAL_CONFIG_IGNORE_DANGERS}
            self.reset_vmap()
            score, res = self.search_simple(zstart, search_nearest=True, allowed_moves=CMDS.CMDS_ZOMBIE )
            if score and score>4:
                continue #if near only
            #score = dist, res = moves of zombie
            if res==None:
                continue #can't reach me
            if score<zdist:
                zdist = score
                zpath = res
            self.LOGRES( score, res)

        start = self.VMAP[0][srcY][srcX]
        start.player = copy.deepcopy(board.ME)

        run_away = zdist!=Infinite and zdist<=1
        if run_away:
            allowed_player_first_move = PLAYER_ALLOWED_MOVES_RUN_AWAY
        else:
            allowed_player_first_move = PLAYER_ALLOWED_MOVES_FIRST




        if zdist!=Infinite and not run_away: #not fire if next
            self.attack_mode = "ATTACK: ZOMBIE"
            self.GOALS = {GOAL_AVOID}
            self.reset_vmap()
            score, res = self.search_simple(start, search_nearest=True, first_moves={ CMDS.CMD_STOP }, min_depth = 5 )
            self.LOGRES( score, res)
            if res!=None and score<RATE_VERY_RISKY:
                if (zpath[-1]==CMDS.CMD_LEFT) and (CMDS.CMD_FIRE_FLOOR_RIGHT in board.PLAYER_POSSIBLE_MOVES[my][mx]):
                    res[0]=CMDS.CMD_FIRE_FLOOR_RIGHT
                    return res, score
                if (zpath[-1])==CMDS.CMD_RIGHT and CMDS.CMD_FIRE_FLOOR_LEFT in board.PLAYER_POSSIBLE_MOVES[my][mx]:
                    res[0]=CMDS.CMD_FIRE_FLOOR_LEFT
                    return res, score


        # ### Collect perks
        # self.attack_mode = "ATTACK: PERKS, OPTIMAL x5"
        # self.GOALS = {GOAL_PERKS}
        # self.reset_vmap()
        # score, res, profit = self.search_multi(start, min_perks=5, max_len = max(5, CONFIG.ROUNDS.Time_per_Round - board.round_tick_cnt), first_moves=allowed_player_first_move)
        # self.LOGRESMULTI( score, res, profit)
        # if res!=None:
        #     if score<RATE_RISKY:
        #         return res, score
        #     if score<risky_score:
        #         risky_score = score
        #         risky_res = res

        # min_perks = 2
        # self.attack_mode = "ATTACK: PERKS, OPTIMAL x{}".format(min_perks)
        # self.GOALS = {GOAL_PERKS}
        # self.reset_vmap()
        # score, res, profit = self.search_multi(start, min_perks=min_perks, max_len = max(5, CONFIG.ROUNDS.Time_per_Round - board.round_tick_cnt), first_moves=allowed_player_first_move)
        # self.LOGRESMULTI( score, res, profit)
        # if res!=None:
        #     if score<RATE_RISKY:
        #         return res, score
        #     if score<risky_score:
        #         risky_score = score
        #         risky_res = res

        min_perks = 3
        self.attack_mode = "ATTACK: PERKS, OPTIMAL x{}".format(min_perks)
        self.GOALS = {GOAL_PERKS}
        self.reset_vmap()
        score, res, profit, perkrate = self.search_multi(start, min_perks=min_perks, max_len = 100, first_moves=allowed_player_first_move)
        self.LOGRESMULTI( score, res, profit, perkrate)
        #if res!=None and profit > 0.5 and perkrate>0.15:
        if res!=None and perkrate>0.2:
            if score<RATE_RISKY:
                return res, score
            if score<risky_score:
                risky_score = score
                risky_res = res

        min_perks = 3
        self.attack_mode = "ATTACK: BLACKHOLE HARVEST x{}".format(min_perks)
        self.GOALS = {GOAL_CUSTOM_TARGET} | {ELB.EB_BACKWAY}
        self.reset_vmap()
        score, res, profit, perkrate = self.search_multi(start, min_perks=1, max_len = max(5, CONFIG.ROUNDS.Time_per_Round - board.round_tick_cnt), first_moves=allowed_player_first_move)
        self.LOGRESMULTI( score, res, profit, perkrate)
        if res!=None and profit > 0.5:
            if score<RATE_RISKY:
                return res, score
            if score<risky_score:
                risky_score = score
                risky_res = res

        self.attack_mode = "ATTACK: NEAREST BLACK HOLE"
        self.GOALS = {GOAL_CUSTOM_TARGET} | {ELB.EB_BACKWAY}
        self.reset_vmap()
        score, res = self.search_simple(start, search_nearest=True, first_moves=allowed_player_first_move)
        self.LOGRES( score, res)
        if res!=None:
            if score<RATE_RISKY:
                return res, score
            if score<risky_score:
                risky_score = score
                risky_res = res

        # self.attack_mode = "ATTACK: PERKS, SIMPLE"
        # self.GOALS = {GOAL_PERKS}
        # self.reset_vmap()
        # score, res = self.search_simple(start, search_nearest=False)
        # nobody2attack = res==None
        # self.gstate.time_log("", " {} {}".format(score, self.attack_mode))
        # if res!=None and score<RATE_RISKY:
        #     return res

        self.attack_mode = "ATTACK: NEAREST SIMPLE PERKS"
        self.GOALS = {GOAL_PERKS}
        self.reset_vmap()
        score, res = self.search_simple(start, search_nearest=True, first_moves=allowed_player_first_move)
        self.LOGRES( score, res)
        if res!=None:
            if score<RATE_RISKY:
                return res, score
            if score<risky_score:
                risky_score = score
                risky_res = res


        # ### Attack nearest palyer
        # self.attack_mode = "ATTACK: NEAREST OTHER"
        # self.GOALS = {GOAL_ATTACK_MAP_OTHER, GOAL_GO_NEAR_OTHER}
        # self.reset_vmap()
        # score, res = self.search(start, True)
        # nobody2attack = res==None
        # self.gstate.time_log("", " {} {}".format(score, self.attack_mode))
        # if res!=None and score<RATE_RISKY:
        #     return res

        # ### 1
        # nobody2attack = False #usually if in jail
        # self.attack_mode = "ATTACK: AI+PERKS"
        # self.GOALS = {GOAL_ATTACK_MAP_AI, GOAL_PERKS, GOAL_GO_NEAR_AI, GOAL_GO_NEAR_OTHER}
        # self.reset_vmap()
        # score, res = self.search(start)
        # nobody2attack = res==None
        # self.gstate.time_log("", "{:4} {}".format(score, self.attack_mode))
        # if res!=None and score<RATE_RISKY:
        #     return res

        # nobody2attack = False #usually if in jail
        # self.attack_mode = "ATTACK: AI+PERKS"
        # self.GOALS = {GOAL_ATTACK_MAP_AI, GOAL_ATTACK_MAP_OTHER, GOAL_PERKS, GOAL_GO_NEAR_AI, GOAL_GO_NEAR_OTHER}
        # self.reset_vmap()
        # score, res = self.search(start, True)
        # nobody2attack = res==None
        # self.gstate.time_log("", " {} {}".format(score, self.attack_mode))
        # if res!=None and score<RATE_RISKY:
        #     return res

        # if nobody2attack:
        #     if board.ME.can_fire(): #digging in jail
        #         self.attack_mode = "ATTACK: DIGGING"               
        #         self.GOALS = {GOAL_CUSTOM_TARGET_NEAR, GOAL_CUSTOM_RATE_CUSTOM_GOALS_HIT} | EL.ELS_WALLS_GOAL
        #         self.reset_vmap()
        #         score, res = self.search(start, True, set(CMDS.COMMANDS_FIRE))
        #         self.gstate.time_log("", " {} {}".format(score, self.attack_mode))
        #         if res!=None and score<RATE_RISKY:
        #             return res
        #     else:
        #         #go to nearest walls
        #         self.attack_mode = "ATTACK: go to WALLS"
        #         self.GOALS = {GOAL_CUSTOM_TARGET_NEAR} | EL.ELS_WALLS_GOAL
        #         self.reset_vmap()
        #         score, res = self.search(start, True)
        #         self.gstate.time_log("", " {} {}".format(score, self.attack_mode))
        #         if res!=None and score<RATE_RISKY:
        #             return res

        # self.attack_mode = "ATTACK: AVOID"               
        # self.GOALS = {GOAL_AVOID}
        # self.reset_vmap()
        # score, res = self.search(start)
        # self.gstate.time_log("", " {} {}".format(score, self.attack_mode))
        # if res!=None and score<RATE_VERY_RISKY:
        #     return res

        self.attack_mode = "ATTACK: AVOID"               
        self.GOALS = {GOAL_AVOID}
        self.reset_vmap()
        score, res = self.search_simple(start, search_nearest=True, first_moves=allowed_player_first_move)
        self.LOGRES( score, res)
        if res!=None:
            if score<RATE_RISKY:
                return res, score
            if score<risky_score:
                risky_score = score
                risky_res = res

        self.gstate.time_log("", "FINALLY: {}, RISKY".format(risky_score))
        return risky_res, risky_score


        
