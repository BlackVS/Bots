#! /usr/bin/env python3

import copy
from posixpath import basename
# from bigboard import *
from model import *
# from command import *
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

    time_start = 0

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

    def time_reset(self):
        self.time_start = time.time()

    def time_get(self):
        return time.time()-self.time_start

    def time_log(self, title="TIME: ", suffix=""):
        LOGALWAYS(title + " {:05f} ".format(self.time_get()) + suffix )

    def print_board(self, title):
        if self.BOARD:
            self.BOARD.print()
    
    def draw_board_input(self, input):
        if self.qtgame and config.QT_BOARD_SHOW_INPUT:
            w  = h = int(sqrt(len(input)))  # size of the board 
            self.qtgame.draw_board_input(input, w ,h)

    def draw_board_big(self, title):
        if self.qtgame and not config.QT_BOARD_SHOW_INPUT:
            self.qtgame.draw_board_big(self.BOARD, self, title)

    def draw_board_custom(self, board, title):
        if self.qtgame and not config.QT_BOARD_SHOW_INPUT:
            self.qtgame.draw_board_big(board, self, title)

    def process_tick(self, cmd):
        self.BOARD.process_tick(cmd, self.HISTORY_LOGGER)
        
    def process_input_board(self, input):
        if not self.BOARD:
            return False
        self.draw_board_input(input)
        res = self.BOARD.process_input_board(input)
        #self.draw_board_big("Next CNT={} ".format(self.BOARD.counter-1 ))
        #self.OBJECTS = objects_new = self.find_all_objects(board_input)
        return res
        
    #special cases
    def check_special_move_fire_flow(self):
        res = None
        score = RATE_DEATH
        return res, score

        mx, my = self.BOARD.ME.X, self.BOARD.ME.Y

        # fire floor and check rate
        for c in [CMDS.CMD_FIRE_FLOOR_LEFT, CMDS.CMD_FIRE_FLOOR_RIGHT]:
            if c in self.BOARD.PLAYER_POSSIBLE_MOVES[my][mx]:
                continue
            board_spec = self.BOARD.clone(0) 
            cmd_base = CMDS.COMAMNDS_SPECIAL[c]
            dx, dy = cmd_base[2]
            board_spec.BOARD[my+dy][mx+dx] = ELB.EB_PIT

            # if config.REPLAY_PLAY_ON:
            #     self.draw_board_custom(board_spec, "SPEC: CMD={} ".format(cmd_base[0]))

            cube = BoardsCube(board_spec, self.qtgame, self)
            r, s = cube.get_best_move(mx, my)
            if r!=None and s<score:
                res   = r
                score = s
        return res, score


    def get_next_command(self):
        board = self.BOARD
        cube = BoardsCube(self.BOARD, self.qtgame, self)
        cmd = CMDS.CMD_NULL
        self.last_cmd = None
        if board.ME.is_alive():
            #res_floow, score_floor = self.check_special_move_fire_flow()

            res, score = cube.get_best_move( self.BOARD.ME.X, self.BOARD.ME.Y )
            if res:
                cmd=res[0]
                if cmd in CMDS.COMMANDS_COMPLEX:
                    cmd=CMDS.COMMAND_GET_FIRST_MOVE(cmd)
                self.last_cmd = res
        else:
            LOG("ME is DEAD - can't get next move!!!!")
        #print("inner cmd={}".format(COMMANDS[cmd]))
        LOG("inner cmd={} mode={}".format(CMDS.COMMAND_DESC(cmd), cube.attack_mode))

        # cmd = CMDS.CMD_RIGHT
        # if self.BOARD.ME.can_fire():
        #     cmd = CMDS.CMD_FIRE_LEFT
            
        return cmd


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


        