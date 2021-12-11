#!/usr/bin/env python3

from command import *
from gamestate import *
from config import *
from logger import *
import time
import random
import os, sys
""" This class should contain the movement generation algorithm."""

HISTORY = []

_cnt_cmd = 0

def replay_parse_values(s):
    res = dict()
    for t in s.strip().split(" "):
        if not t: continue
        k,v = t.strip().split("=")
        k = k.strip()
        v = v.strip()
        res[k]=v
    return res

def object_update_attrs(obj, types, data):
    for k,v in data.items():
        if not hasattr(obj,k):
            ASSERT()
            return
        if not k in types:
            ASSERT()
            return
        t = types[k]
        if t == "int":
            setattr(obj,k,int(v))
        elif t == "str":
            setattr(obj,k,v)
        elif t == "bool":
            setattr(obj,k,v=='True')
        elif t == "NoneType" and v=="None":
            setattr(obj,k,None)
        else:
            ASSERT()
            return
            
            
class DirectionSolver:

    gstate = None
    qtgame = None

    #REPLAY
    replay_dir = None
    replay_record_id = None
    replay_load_state = False

    replay_record_fname = None

    def __init__(self, qtgame):
        self.qtgame = qtgame
        self.gstate = GameState(qtgame)

    def log(self, s):
        self.gstate.history_write(s)

    def log_info(self, s):
        self.gstate.history_write("INFO: "+s)

    def get(self, board_string):
        global HISTORY

        self.gstate.history_start()
        #print(">>>>>>>>>>> GET")
        time_start = time.time()
        LOGC("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        LOGC(board_string)

        cmd=COMMANDS[CMD_NULL]
        
        self.log("\nBOARDSTRING:")
        self.log(board_string)

        self.gstate.history_store_state("BEFORE:")
        self.gstate.update_from(board_string)
        self.gstate.history_print_input()
        self.gstate.history_store_state("UPDATED:")
        cmd =  self.next_command()

        if len(HISTORY)<30:
            HISTORY.append(cmd)
        else:
            HISTORY = HISTORY[1:] + [cmd]

        LOGALWAYS("TIME: {}".format(time.time()-time_start))
        LOG("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

        self.gstate.history_close()
        return cmd

    def next_command(self):
        global _cnt_cmd
        cmd = CMD_NULL
        self.log_info("get_next_command")
        cmd = self.gstate.get_next_command()
        self.log_info("CMD <{}>".format(cmd))
        self.gstate.print_board("Next CNT={} CMD={} ".format(self.gstate.BOARD.counter-1, COMMANDS[cmd] ))
        self.gstate.draw_board("Next CNT={} CMD={} ".format(self.gstate.BOARD.counter-1, COMMANDS[cmd] ))

        self.log_info("me_do_cmd")
        self.gstate.BOARD.me_do_cmd(cmd, self.gstate.HISTORY_LOGGER)
        _command = COMMANDS[ cmd ]
        #print("Sending Command: {}\n".format(_command))
        LOG("Sending Command: {}\n".format(_command))
        self.log_info("Sending Command <{}>\n".format(_command))
        return _command


    def replay(self):
        self.replay_dir = os.path.abspath( os.path.join(config.REPLAY_RECORDS_DIR, config.REPLAY_RECORD_SET) )
        self.replay_load_state = config.REPLAY_RECORD_LOAD_INITIAL_STATE
        self.replay_record_id = config.REPLAY_RECORD_START
        LOG("REPLAY:")
        LOG("REPLAY DIR: {}".format(self.replay_dir))
        LOG("REPLAY Start record: {}".format(self.replay_record_id))
        LOG("REPLAY Load initial state: {}:".format(self.replay_load_state))
        while self.replay_play_next():
            time.sleep(config.REPLAY_DELAY)

    def replay_state_cleanup(self):
        self.gstate.BOARD.cleanup()

    def replay_state_update_ME(self, snames, svalues):
        types  = replay_parse_values(snames)
        values = replay_parse_values(svalues)
        object_update_attrs(self.gstate.BOARD.ME, types, values)

    def replay_state_update_OBJECTS(self, data, objects):
        types  = replay_parse_values(data[0])
        values = replay_parse_values(data[1])
        object_update_attrs(objects, types, values)
        for i,s in enumerate(data[2:]):
            if s.startswith("==="):
                break
            if i&1==0:
                types  = replay_parse_values(s)
                continue
            idx, v = s.split(":")
            idx = idx.strip()
            values = replay_parse_values(v)
            obj = objects.object_new()
            object_update_attrs(obj, types, values)
            objects.object_restore(obj)

    def replay_state_update_ZOMBIES(self, data):
        types  = replay_parse_values(data[0])
        values = replay_parse_values(data[1])
        players = self.gstate.BOARD.ZOMBIES
        object_update_attrs(players, types, values)
        for i,s in enumerate(data[2:]):
            if s.startswith("==="):
                break
            if i==0:
                types  = replay_parse_values(s)
                continue
            idx, v = s.split(":")
            idx = idx.strip()
            values = replay_parse_values(v)
            player = TPlayer(ETANK_TYPE_OTHER)
            object_update_attrs(player, types, values)
            players.append(player)

    def replay_play_next(self):
        global TOBJ_IDXCNT
        self.replay_record_fname = os.path.join( self.replay_dir, "{:05}.txt".format(self.replay_record_id))
        board_string = ""
        if not os.path.isfile(self.replay_record_fname):
            LOG("File {} not found!!!".format(self.replay_record_fname))
            return False
        with open(self.replay_record_fname, "rt", encoding='utf-8') as frec:
            lines = frec.readlines()
            if self.replay_load_state:
                self.replay_state_cleanup()
            for i,s in enumerate(lines):
                if not s:
                    continue
                if s.startswith("INFO"):
                    continue
                if s.startswith("TOBJ_IDXCNT"):
                    TOBJ_IDXCNT = int( s.split(":")[1].strip() )
                    continue
                if s.startswith("BOARDSTRING"):
                    board_string = lines[i+1]
                    if not self.replay_load_state:
                        break #no sense read more
                if s.startswith("INPUTBOARD"): #all initial data read
                    break
                if s.startswith("ME:"):
                    self.replay_state_update_ME(lines[i+1], lines[i+2])
                if s.startswith("PLAYERS:"):
                    self.replay_state_update_OBJECTS(lines[i+1:], self.gstate.BOARD.PLAYERS)
                if s.startswith("ZOMBIES:"):
                    self.replay_state_update_OBJECTS(lines[i+1:], self.gstate.BOARD.ZOMBIES)
                if s.startswith("BULLETS:"):
                    self.replay_state_update_OBJECTS(lines[i+1:], self.gstate.BOARD.BULLETS)
                # if s.startswith("PERKS:"):
                #     self.replay_state_update_OBJECTS(lines[i+1:], self.gstate.BOARD.PERKS)
            if board_string:
                self.get(board_string)
            #next
            self.replay_record_id+=1
            self.replay_load_state = False #not load next states
            return True
        return False


if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
