import os, sys
import json
import element


#DEBUG_VERBOSE=True
DEBUG_VERBOSE=False

DFILE = "board_out"
#DFILE = ""

#######################################################################################################################################

#Sydorenko
#REMOTE_URL = "https://botchallenge.cloud.epam.com/codenjoy-contest/board/player/933f496rgd34y7h2kkus?code=2670892214592550791"
#NULL_FIX = True

#REMOTE_URL = "https://botchallenge.cloud.epam.com/codenjoy-contest/board/player/nm2agyr21pr69euq51xm?code=7440942336991867461&gameName=bomberman"
#NULL_FIX = True

REMOTE_URL = "http://127.0.0.1:8080/codenjoy-contest/board/player/g1?code=12345678901234567890"
NULL_FIX = False


#REMOTE_URL = "http://bomberman.coders.in.ua:8081/codenjoy-contest/board/player/g1?code=12345678901234567890"
#NULL_FIX = False

#######################################################################################################################################

QT_BOARD_SHOW = True
#QT_BOARD_SHOW = False


CONFIG_FILE = "config_v6.json"
CONFIG = None 


#DEBUG = True
DEBUG = False


# ☺ ☻
BOARDDEBUG = [
['☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼'],
['☼  #    #   #   #     ☼'],
['☼ ☼ ☼ ☼ ☼ ☼ ☼#☼ ☼ ☼ ☼ ☼'],
['☼#  # ###         #  &☼'],
['☼ ☼ ☼ ☼#☼#☼ ☼ ☼#☼ ☼#☼ ☼'],
['☼#     &### #    #    ☼'],
['☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼#☼ ☼ ☼ ☼'],
['☼# #   &      #      #☼'],
['☼ ☼ ☼ ☼ ☼ ☼ ☼#☼ ☼ ☼ ☼ ☼'],
['☼                   # ☼'],
['☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼'],
['☼                 &   ☼'],
['☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼'],
['☼         #☻      # # ☼'],
['☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼#☼ ☼ ☼ ☼'],
['☼          #       #  ☼'],
['☼#☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼'],
['☼  ## #  ## #        #☼'],
['☼ ☼ ☼ ☼#☼ ☼ ☼ ☼#☼ ☼ ☼ ☼'],
['☼    &##        #     ☼'],
['☼ ☼ ☼ ☼#☼ ☼ ☼ ☼ ☼ ☼ ☼ ☼'],
['☼     # # #         # ☼'],
['☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼☼'],



]

PREDICT_TRIES = 2

def PASS():
    pass

def ASSERT():
    BREAK

BREAK = PASS
if DEBUG:
    BREAK = BREAK


_config_inited = False

def LOG(s, write2file=True):
    print(s)
    if write2file and DFILE:
        with open(DFILE+".txt","at") as fout:
            fout.write(s+"\n")

def LOGD(s, write2file=True):
    if not DEBUG_VERBOSE:
        return
    print(s)
    if write2file and DFILE:
        with open(DFILE+".txt","at") as fout:
            fout.write(s+"\n")


def print_board(board, write2console=False, write2file="", bqt=None):
    
    # print to console
    if write2console:
        print("")
        for b in board:
            print(" ".join( (c,'Ж')[c==element.EL_BOOM] for c in b))
        print("\n")
    
    # draw graphics
    if bqt!=None: 
        bqt.set_board(board)
    
    # write to file
    if write2file!="":
        with open(DFILE+".txt","at") as fout:
            fout.write("\n>>>\n[\n")
            for b in board:
                fout.write( "['" + "".join(b) + "'],\n")
            fout.write("]\n<<<\n")


#cfg.get("api_use_tls",True)
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
