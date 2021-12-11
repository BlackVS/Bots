#! /usr/bin/env python3

import copy
from bigboard import *
from player import *
from command import *
from cube import *

class GameState:
    gtgame = None

    BOARD   = None #bigboard

    def __init__(self, qtgame):
        self.qtgame = qtgame
        self.BOARD = BigBoard()

    def print(self):
        if self.BOARD:
            self.BOARD.print()
        if self.qtgame:
            self.qtgame.update_from(self.BOARD)

    def update_from(self, input):
        if not self.BOARD:
            return False
        return self.BOARD.update_from(input)

    def get_next_command(self):
        board = self.BOARD
        cube = BoardsCube(self.BOARD, self.qtgame)
        cmd = CMD_NULL
        if board.ME.is_alive:
            res = cube.get_best_move( self.BOARD.ME.X, self.BOARD.ME.Y )
            if res:
                cmd=res[0]
        #print("inner cmd={}".format(COMMANDS[cmd]))
        LOG("inner cmd={}".format(COMMANDS[cmd]))

        return cmd


