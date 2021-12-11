#!/usr/bin/env python3
import os, sys
import json
import element


#CUBE_DEPTH = 11 #at least aiTicksPerShoot+1
#CUBE_DEPTH = 35 #
CUBE_DEPTH = 30

CONFIG_FILE = "config_day10.json"


#######################################################################################################################################
REMOTE_URL = "https://epam-botchallenge.com/codenjoy-contest/board/player/k8qxbky99cmnbwsin6d6?code=3421237908643833295"

#######################################################################################################################################

#NULL_FIX = True


DEBUG = False
#DEBUG = True


########### RECORD ##########################

REPLAY_RECORD_ON = False
#REPLAY_RECORD_ON = True


########### REPLAY ##########################

#### Usual paly mode (remote server)
# REPLAY_PLAY_ON = False
# REPLAY_RECORD_START = 0

#### REPLAY stored records
REPLAY_PLAY_ON = True
REPLAY_RECORD_START = 0
REPLAY_RECORD_SET = "20"

REPLAY_RECORDS_DIR = "../../records"
REPLAY_DELAY = 0.5
REPLAY_RECORD_LOAD_INITIAL_STATE = True
#REPLAY_RECORD_LOAD_INITIAL_STATE = False


## show next few levels of cube
DEBUG_CUBE = False
#DEBUG_CUBE = True
DEBUG_CUBE_DEPTH = 3
DEBUG_CUBE_DELAY = 0.5
#DEBUG_CUBE_DELAY = 0.15

#DEBUG_TEST_MAP = True
DEBUG_TEST_MAP = False

LOGFILENAME="log.txt"

#QT_BOARD_SHOW = False
QT_BOARD_SHOW = True

QT_BOARD_SHOW_ATTACK_MAP_AI = False
#QT_BOARD_SHOW_ATTACK_MAP_AI = True

QT_BOARD_SHOW_ATTACK_MAP_OTHER = False
#QT_BOARD_SHOW_ATTACK_MAP_OTHER = True

#QT_BOARD_SHOW_ZOMBIE_MOVES = False
QT_BOARD_SHOW_ZOMBIE_MOVES = True

#QT_BOARD_SHOW_PLAYERS_MOVES =False
QT_BOARD_SHOW_PLAYERS_MOVES =True

QT_BOARD_SHOW_BULLETS_INFO =False
#QT_BOARD_SHOW_BULLETS_INFO =True

QT_BOARD_SIMPLE_GRAPHIC = False


DANGER_SCALED = False

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


_config_inited = False

def read_config(path):
    #read config
    config=dict()
    try:
        print("Parsing config file (json)...")
        path=os.path.join(path)
        with open(path) as f:
            config = json.load(f)
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)
        return None
    finally:
        print("JSON succesfully parsed.")
        for section,cfg in config.items():
            print("{} : {}".format(section,cfg))
        #mod = sys.modules[self.__module__]
    
    return config

def config_init():
    global CONFIG, _config_inited
    if _config_inited: return
    CONFIG = read_config(CONFIG_FILE)
    _config_inited=True

CONFIG = read_config(CONFIG_FILE)
_config_inited=True
