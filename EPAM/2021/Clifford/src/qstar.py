#! /usr/bin/env python3
# # -*- coding: utf-8 -*-
""" generic A-Star path searching algorithm """

from abc import ABCMeta, abstractmethod
from heapq import heappush, heappop, heapify
import copy
from config import *
# from command import *
from logger import *
from game_rates import *



#only directed graph!!!!
class QNode:
    # user data
    x = None
    y = None
    t = None 
    depth = 0

    # system data
    parent = None
    parent_cmd = None
    
    fscore = Infinite
    gscore = Infinite
    profit = 0
    profit_stored = 0

    #here
    perks         = 0
    perks_taken   = set()

    closed   = False
    openlist = False

    #custom object
    player = None

    def __init__(self, x, y, t):
        self.x = x
        self.y = y
        self.t = t

    def __lt__(self, b):
        return self.fscore < b.fscore


class QStar:

    # @abstractmethod
    # def heuristic_cost_estimate(self, current, goal):
    #     """Computes the estimated (rough) distance between a node and the goal, this method must be implemented in a subclass. The second parameter is always the goal."""
    #     raise NotImplementedError

    # @abstractmethod
    # def distance_between(self, n1, n2):
    #     """Gives the real distance between two adjacent nodes n1 and n2 (i.e n2 belongs to the list of n1's neighbors).
    #        n2 is guaranteed to belong to the list returned by the call to neighbors(n1).
    #        This method must be implemented in a subclass."""
    #     raise NotImplementedError

    def reconstruct_paths_cmd(self, last):
        def _gen():
            current = last
            while current and current.parent:
                yield current.parent_cmd
                current = current.parent
        res = list(_gen())
        res.reverse()
        return res

    def reconstruct_paths_cmd_plus_profit(self, last):
        def _gen():
            current = last
            while current and current.parent:
                yield (current.parent_cmd, current.profit)
                current = current.parent
        res = list(_gen())
        res.reverse()
        return res

    def reconstruct_paths_nodes(self, last):
        def _gen():
            current = last
            while current:
                yield current
                current = current.parent
        return list(_gen())[::-1]

    @abstractmethod
    def qstar_get_dist2goal(self, node):
         raise NotImplementedError

    @abstractmethod
    def log(self, s):
         raise NotImplementedError
    
    @abstractmethod
    def qstar_get_possible_moves(self, node):
        # For a given node get list of possible moves
        raise NotImplementedError

    @abstractmethod
    def qstar_not_go_further(self, node):
        # for current node check if check next moves
        raise NotImplementedError

    @abstractmethod
    def qstar_rate_move(self, node, m):
        # Rate this move
        raise NotImplementedError

    @abstractmethod
    def qstar_is_goal_reached(self, node):
        # For a given node check if goal/goals reached
        raise NotImplementedError

    @abstractmethod
    def qstar_is_possible_multi_solution(self, node):
        # For a given node check if goal/goals reached
        raise NotImplementedError


    @abstractmethod
    def qstar_get_target(self, node, cmd):
        # Stop if solution found
        raise NotImplementedError

    #check move
    @abstractmethod
    def qstar_move_to(self, player, cmd, dstx, dsty, t):
        raise NotImplementedError

    def print_test_map(self,TESTMAP):
        print()
        LOG("\n")
        for tt in TESTMAP:
            st = ""
            for v in tt:
                s=v
                if type(v) == int:
                    v=int(v)
                s="{:^4}".format(v)
                st+=s
            print(st)
            #LOG(st)


    def search_simple(self, start, search_nearest=False, first_moves=None, allowed_moves = set(), min_depth=0):
        if len(self.GOALS)==0:
            print("NO GOALS!!!!")
            return None, None

        solves = []

        automin = True
        #if already at goal - return
        # ??? BLOCKED due to must check moves and dangers 
        # if self.is_goal_reached(start):
        #     gs = self.rate_move(start, CMD_NULL)
        #     if search_nearest:
        #         return (gs, self.reconstruct_paths_cmd(start) )
        #     #self.print_test_map(TESTMAP)
        #     solves.append( (gs, self.reconstruct_paths_cmd(start) ) )

        heap = []

        start.gscore = 0
        heappush(heap, start)
        start.openlist = True

        if DEBUG_TEST_MAP:
            TESTMAP = copy.deepcopy(self.cube[0].BOARD)

        first = True
        while heap:
            current = heappop(heap)
            current.openlist = False
            current.closed = True

            if DEBUG_TEST_MAP:
                TESTMAP[current.y][current.x] = current.gscore
                self.print_test_map(TESTMAP)

            if not first and self.qstar_is_goal_reached_simple(current):#not check first due to stay is also move and nust be rated
                if current.depth >= min_depth: 
                    if search_nearest:
                        return (current.gscore, self.reconstruct_paths_cmd(current) )
                    solves.append( (current.gscore, self.reconstruct_paths_cmd(current) ) )
                    continue

            first=False

            # if current.parent_cmd in CMDS.COMMANDS_FIRE:
            #     continue #do not check moves after fire

            if automin and current.gscore>=RATE_DEATH: #"i'm surely die if go there"
                continue

            if self.qstar_not_go_further(current):
                continue
            
            moves = self.qstar_get_possible_moves(current)
            if allowed_moves:
                moves &= allowed_moves
                
            if current.t==0:
                #restrict first moves to first_moves
                if first_moves:
                    moves = list( set(moves) & set(first_moves) )
                #LOGF("Possible moves: {}".format(moves))
            
            for m in moves:
                ndata = self.qstar_get_target(current, m)
                nplayer = copy.deepcopy(current.player)
                self.qstar_move_to(nplayer, m, ndata.x, ndata.y, ndata.t) 
                nrate, nprofit = self.qstar_rate_move(current, m)

                ngscore = current.gscore + nrate

                if ngscore >= ndata.gscore:
                    continue

                if ndata.closed: #already closed - just update parent
                    #loop check!!!
                    pnodes = self.reconstruct_paths_nodes(current)
                    if not ndata in pnodes:
                        ndata.parent=current
                        ndata.parent_cmd = m
                        ndata.player = nplayer
                    else:#loop detected
                        continue
                else:
                    ndata.gscore = ngscore
                    ndata.fscore = ngscore + self.qstar_get_dist2goal(ndata)
                    ndata.parent = current
                    ndata.parent_cmd = m
                    ndata.player = nplayer
                    ndata.depth = current.depth + 1

                    ndata.perks  = current.perks
                    ndata.perks_taken = copy.deepcopy(current.perks_taken)
                    if nprofit>0:
                        ndata.perks_taken.add( (ndata.x, ndata.y) )
                        ndata.perks+=1

                    if not ndata.openlist:
                        ndata.openlist = True
                        heappush(heap, ndata)
                    else:
                        # re-add the node in order to re-sort the heap
                        heap.remove(ndata)
                        heappush(heap, ndata)
        if not solves:
            print("NO SOLUTION FOUND!!!!!") 
            if DEBUG_TEST_MAP:
                self.print_test_map(TESTMAP)
            return (None,None)
        
        res = (Infinite, None)
        for solve in solves:
            if solve[0]<res[0]:
                res = solve

        if res[1]==None:
            return (None, None)

        return res




    def search_multi(self, start, min_perks = 1, max_len = 20, first_moves=set()):
        if len(self.GOALS)==0:
            print("NO GOALS!!!!")
            return None, None

        solves = []
        res_score = -Infinite
        res_path = None
        res_profit_per_time = 0
        res_perks_per_time = 0

        automin = True
        #if already at goal - return
        # ??? BLOCKED due to must check moves and dangers 
        # if self.is_goal_reached(start):
        #     gs = self.rate_move(start, CMD_NULL)
        #     if search_nearest:
        #         return (gs, self.reconstruct_paths_cmd(start) )
        #     #self.print_test_map(TESTMAP)
        #     solves.append( (gs, self.reconstruct_paths_cmd(start) ) )

        heap = []

        start.gscore = 0
        heappush(heap, start)
        start.openlist = True

        if DEBUG_TEST_MAP:
            TESTMAP = copy.deepcopy(self.cube[0].BOARD)

        first = True
        while heap:
            current = heappop(heap)
            current.openlist = False
            current.closed = True

            if DEBUG_TEST_MAP:
                TESTMAP[current.y][current.x] = current.gscore
                self.print_test_map(TESTMAP)

            if not first:
                if current.perks >= min_perks: #not check first due to stay is also move and nust be rated
                    if self.qstar_is_possible_multi_solution(current):
                        if current.profit>current.profit_stored:
                            solves.append( (current.gscore, self.reconstruct_paths_cmd(current), current.profit, current.perks ) )
                            current.profit_stored = current.profit


            # if current.parent_cmd in CMDS.COMMANDS_FIRE:
            #     continue #do not check moves after fire

            if automin and current.gscore>=RATE_DEATH: #"i'm surely die if go there"
                continue

            if current.depth >=max_len:
                continue

            if self.qstar_not_go_further(current):
                continue
            
            moves = set(self.qstar_get_possible_moves(current))

            if first and first_moves:
                moves = moves & set(first_moves)

            first=False

            for m in moves:
                ndata = self.qstar_get_target(current, m)
                nplayer = copy.deepcopy(current.player)
                self.qstar_move_to(nplayer, m, ndata.x, ndata.y, ndata.t) 
                nrate, nprofit = self.qstar_rate_move(current, m)

                ngscore = current.gscore + nrate

                if ngscore >= ndata.gscore:
                    continue

                if ndata.closed: #already closed - just update parent
                    #loop check!!!
                    pnodes = self.reconstruct_paths_nodes(current)
                    if not ndata in pnodes:
                        ndata.parent=current
                        ndata.parent_cmd = m
                        ndata.player = nplayer
                    else:#loop detected
                        continue
                else:
                    ndata.gscore = ngscore
                    ndata.fscore = ngscore + self.qstar_get_dist2goal(ndata)
                    ndata.parent = current
                    ndata.parent_cmd = m
                    ndata.depth = current.depth + 1

                    ndata.player = nplayer
                    ndata.profit = current.profit + nprofit #???
                    ndata.profit_stored = current.profit_stored
                    ndata.perks  = current.perks
                    ndata.perks_taken = copy.deepcopy(current.perks_taken)
                    if nprofit>0:
                        ndata.perks_taken.add( (ndata.x, ndata.y) )
                        ndata.perks+=1

                    if not ndata.openlist:
                        ndata.openlist = True
                        heappush(heap, ndata)
                    else:
                        # re-add the node in order to re-sort the heap
                        heap.remove(ndata)
                        heappush(heap, ndata)
        if not solves:
            print("NO SOLUTION FOUND!!!!!") 
            if DEBUG_TEST_MAP:
                self.print_test_map(TESTMAP)
            return (res_score, res_path, res_profit_per_time, res_perks_per_time )
        
        #res = (Infinite, None)
        for srate, spath, sprofit, sperks in solves:
            l = len(spath)
            p = sprofit/l # - l/20 # penalty for length
            if p>res_profit_per_time:
                res_score = srate
                res_path  = spath
                res_profit_per_time = p
                res_perks_per_time = sperks/l

        return (res_score, res_path, res_profit_per_time, res_perks_per_time )



