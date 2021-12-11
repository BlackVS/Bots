#!/usr/bin/env python3
import os, sys
import json
# import model import *
import config_clifford as CONFIG
from config_clifford_custom import CONFIG_CUSTOM

#CUBE_DEPTH = 11 #at least aiTicksPerShoot+1
#CUBE_DEPTH = 35 #at least aiTicksPerShoot+1 - full line motion prediction
CUBE_DEPTH = 15 # 30/2 - bullet full distance
CUBE_HISTORY_LEN = 5
CUBE_LONG_HISTORY_LEN = 10



#######################################################################################################################################
#VVS
REMOTE_URL = "https://dojorena.io/codenjoy-contest/board/player/dojorena1292?code=XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

#NULL_FIX = True

DEBUG = False
#DEBUG = True

########### RECORD ##########################

REPLAY_RECORD_ON = False
#REPLAY_RECORD_ON = True

########### REPLAY ##########################
REPLAY_PLAY_ON = False
REPLAY_RECORD_START = 0

# REPLAY_PLAY_ON = True
# REPLAY_RECORD_START = 2
# REPLAY_RECORD_SET = "00" 

REPLAY_RECORDS_DIR = "../RECORDS"
REPLAY_DELAY = 2
REPLAY_RECORD_LOAD_INITIAL_STATE = True
#REPLAY_RECORD_LOAD_INITIAL_STATE = False


DEBUG_CUBE = False
#DEBUG_CUBE = True
DEBUG_CUBE = False

DEBUG_CUBE_DEPTH = 5
DEBUG_CUBE_DELAY = 0.2
#DEBUG_CUBE_DELAY = 0.15

#DEBUG_TEST_MAP = True
DEBUG_TEST_MAP = False

LOGFILENAME="log.txt"

QT_BOARD_SHOW = False
#QT_BOARD_SHOW = True

QT_BOARD_SHOW_INPUT = False
#QT_BOARD_SHOW_INPUT = True




QT_BOARD_SHOW_DANGERS_MAP = False
#QT_BOARD_SHOW_DANGERS_MAP = True

QT_BOARD_SHOW_ATTACK_MAP_AI = False
#QT_BOARD_SHOW_ATTACK_MAP_AI = True

#QT_BOARD_SHOW_ATTACK_MAP_OTHER = False
QT_BOARD_SHOW_ATTACK_MAP_OTHER = True

QT_BOARD_SHOW_ZOMBIE_MOVES = False
#QT_BOARD_SHOW_ZOMBIE_MOVES = True

QT_BOARD_SHOW_PLAYERS_MOVES =False
#QT_BOARD_SHOW_PLAYERS_MOVES =True

QT_BOARD_SHOW_BULLETS_INFO =False
#QT_BOARD_SHOW_PLAYERS_MOVES =True

QT_BOARD_SHOW_MOVES_MAP = False
#QT_BOARD_SHOW_MOVES_MAP = True

QT_BOARD_SHOW_CMDS_MAP = False
#QT_BOARD_SHOW_CMDS_MAP = True

if not DEBUG:
    LOGFNAME = None
    #QT_BOARD_SHOW = False

def PASS():
    pass

def ASSERT():
    BREAK

BREAK = PASS
if DEBUG:
    BREAK = BREAK


