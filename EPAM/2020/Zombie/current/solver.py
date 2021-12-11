#!/usr/bin/env python3

from command import *
from gamestate import *
from config import *
from logger import *
import time

""" This class should contain the movement generation algorithm."""

HISTORY = []
class DirectionSolver:

    gstate = None
    qtgame = None

    def __init__(self, qtgame):
        self.qtgame = qtgame
        self.gstate = GameState(qtgame)

    def get(self, board_string):
        global HISTORY
        #print(">>>>>>>>>>> GET")
        time_start = time.time()
        if TESTFILE:
            LOG("Load DEBUG")
            with open(TESTFILE,"rt",encoding='utf-8') as fin:
                board_string=fin.readline()
        LOG("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        LOG(board_string)
        
        cmd=COMMANDS[CMD_NULL]
        if self.gstate.update_from(board_string):
            cmd =  self.next_command()

        if len(HISTORY)<30:
            HISTORY.append(cmd)
        else:
            HISTORY = HISTORY[1:] + [cmd]
            if all(c==HISTORY[0] for c in HISTORY[1:]):
                LOG("SEPPUKA")
                cmd=COMMANDS[CMD_DIE]
                self.gstate.BOARD.ME.do_cmd(CMD_DIE)


        LOGALWAYS("TIME: {}".format(time.time()-time_start))
        LOG("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        return cmd

    def next_command(self):
        self.gstate.print()
        cmd = self.gstate.get_next_command()
        self.gstate.BOARD.ME.do_cmd(cmd)
        _command = COMMANDS_REVERSE[ cmd ]
        #print("Sending Command: {}\n".format(_command))
        LOG("Sending Command: {}\n".format(_command))
        return _command


if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
