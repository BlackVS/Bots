#! /usr/bin/env python3
# # -*- coding: utf-8 -*-
""" generic A-Star path searching algorithm """

from abc import ABCMeta, abstractmethod
from heapq import heappush, heappop, heapify
import copy
from config import *
from command import *
from logger import *
from game_rates import *



#only directed graph!!!!
class QNode:
    # user data
    x = None
    y = None
    t = None 

    # system data
    parent = None
    parent_cmd = None
    fscore = Infinite
    gscore = Infinite

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

    def reconstruct_paths_nodes(self, last):
        def _gen():
            current = last
            while current:
                yield current
                current = current.parent
        return list(_gen())[::-1]

    @abstractmethod
    def get_dist2goal(self, node):
         raise NotImplementedError

    @abstractmethod
    def log(self, s):
         raise NotImplementedError
    
    @abstractmethod
    def get_possible_moves(self, node):
        # For a given node get list of possible moves
        raise NotImplementedError

    @abstractmethod
    def not_go_further(self, node):
        # for current node check if check next moves
        raise NotImplementedError

    @abstractmethod
    def rate_move(self, node, m):
        # Rate this move
        raise NotImplementedError

    @abstractmethod
    def is_goal_reached(self, node):
        # For a given node check if goal/goals reached
        raise NotImplementedError

    @abstractmethod
    def is_final_goal_reached(self, node):
        # Stop if solution found
        raise NotImplementedError

    @abstractmethod
    def get_neighbor(self, node, cmd):
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


    def search(self, start, search_nearest=False, first_moves=None):
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

            if not first and self.is_goal_reached(current): #not check first due to stay is also move and nust be rated
                if search_nearest:
                    return (current.gscore, self.reconstruct_paths_cmd(current) )
                #if DEBUG_TEST_MAP:
                #    self.print_test_map(TESTMAP)
                solves.append( (current.gscore, self.reconstruct_paths_cmd(current) ) )
                # if not minres_gscore or current.gscore<minres_gscore:
                #     minres_gscore = current.gscore
                continue

            first=False

            if current.parent_cmd in COMMANDS_FIRE:
                continue #do not check moves after fire

            if automin and current.gscore>RATE_DEATH: #"i'm surely die if go there"
                continue

            if self.not_go_further(current):
                continue
            
            moves = self.get_possible_moves(current)
            if current.t==0:
                #restrict first moves to first_moves
                if first_moves:
                    moves&=first_moves
                #LOGF("Possible moves: {}".format(moves))
            
            for m in moves:
                ndata = self.get_neighbor(current, m)
                nplayer = copy.deepcopy(current.player)
                self.qstar_move_to(nplayer, m, ndata.x, ndata.y, ndata.t) 
                nrate = self.rate_move(current, m)

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
                        pass
                else:
                    ndata.gscore = ngscore
                    ndata.fscore = ngscore + self.get_dist2goal(ndata)
                    ndata.parent = current
                    ndata.parent_cmd = m
                    ndata.player = nplayer

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




