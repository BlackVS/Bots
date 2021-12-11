#! /usr/bin/env python3

import copy
# from bigboard import *
from trackobjects_custom import *
from command import *
from cube import *
import shutil, os
import config

class GameState:
    gtgame = None

    BOARD   = None #bigboard
    HISTORY_DIR = ""
    HISTORY_FNAME = None
    HISTORY_LOGGER = None

    last_cmd = None

    def __init__(self, qtgame):
        self.qtgame = qtgame
        self.BOARD  = BigBoard()
        self.HISTORY_DIR = os.path.abspath("history")
        try:
            shutil.rmtree(self.HISTORY_DIR)
        except:
            pass
        if config.REPLAY_RECORD_ON:
            os.mkdir(self.HISTORY_DIR)
            BigBoard.counter = config.REPLAY_RECORD_START        

    def print_board(self, title):
        if self.BOARD:
            self.BOARD.print()
    
    def draw_board(self, title):
        if self.qtgame:
            self.qtgame.update_from(self.BOARD, self, title)

    def update_from(self, input):
        if not self.BOARD:
            return False
        return self.BOARD.update_from(input)
        #self.OBJECTS = objects_new = self.find_all_objects(board_input)

    def get_next_command(self):
        board = self.BOARD
        cube = BoardsCube(self.BOARD, self.qtgame, self)
        cmd = CMD_NULL
        self.last_cmd = None
        if board.ME.is_alive():
            res = cube.get_best_move( self.BOARD.ME.X, self.BOARD.ME.Y )
            if res:
                cmd=res[0]
                self.last_cmd = res
        else:
            LOG("ME is DEAD - can't get next move!!!!")
        #print("inner cmd={}".format(COMMANDS[cmd]))
        LOG("inner cmd={} mode={}".format(COMMANDS[cmd], cube.attack_mode))

        return cmd
        #return CMD_UP
        #return CMD_DOWN
        #return CMD_LEFT
        #return CMD_DIE

    def history_start(self):
        if config.REPLAY_RECORD_ON:
            fname = os.path.join(self.HISTORY_DIR, "{:05}.txt".format(BigBoard.counter))
            self.HISTORY_FNAME = fname
            self.HISTORY_LOGGER = LoggerFile(fname)
        else:
            self.HISTORY_LOGGER = LoggerFile()

    def history_close(self):
        self.HISTORY_FNAME = None
        self.HISTORY_LOGGER = None

    def history_write(self, s):
        if self.HISTORY_LOGGER:
            self.HISTORY_LOGGER.log(s)

    def history_store_state(self, title):
        if not self.HISTORY_LOGGER:
            return
        self.history_write("\n" + title)
        self.history_write("TOBJ_IDXCNT: {}".format(TOBJ_IDXCNT))
        self.BOARD.store_state(self.HISTORY_LOGGER)

    def history_print_input(self):
        if not self.HISTORY_LOGGER:
            return
        self.BOARD.store_print_input(self.HISTORY_LOGGER)


        