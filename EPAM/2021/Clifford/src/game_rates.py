#!/usr/bin/env python3


from model_defs import *
from config import CONFIG

Infinite = 1000000

DANGER_SCALED = False

PLAYER_NOT_HIT_LAST_DUMMY = False
PLAYER_NOT_HIT_LAST       = True

QSTAR_CHECK_FIRE = True

RATE_MOVE_STEP      = [0, 1, 2.1]  # 2.1 - for case if palyer can for example jump in 2

# RATE_MOVE_TAKE_PERK = {
#     PERKTYPE.UNKNOWN : -10,
#     PERKTYPE.GLOVE   : -10,
#     PERKTYPE.KNIFE   : -11,
#     PERKTYPE.RING    : -12,
#     PERKTYPE.MASK    : 0-15
# }

RATE_MOVE_TAKE_PERK = {
    PERKTYPE.UNKNOWN : -5,
    PERKTYPE.GLOVE   : -50,
    PERKTYPE.KNIFE   : -50,
    PERKTYPE.RING    : -50,
    PERKTYPE.MASK    : -50
}


RATE_MOVE_HIT_PLAYER = -5

PLAYER_SAME_POSITION_DETECT = 10

SIMULATE_PLAYERS_AUTOFIRE_TICK0 = True
SIMULATE_PLAYERS_AUTOFIRE_NEXT  = False


#                   ME      1     2     3
FORCE_DUEL_MAP   = [None, True, True, True]
FORCE_DUEL_RISKS = [0   ,  100,  100,  50 ]

CUBE_FORCE_DUEL = True
CUBE_MAX_FIRE_DISTANCE_CHECK = 20

RATE_HIT_PLAYER_DUMMY = CONFIG.SCORE.Kill_hero_score
RATE_HIT_PLAYER_FORCE_DUEL = CONFIG.SCORE.Kill_hero_score//4 #due to risky
RATE_HIT_PLAYER_CUBE = CONFIG.SCORE.Kill_hero_score//4 #due to not fact that hit, just try 
RATE_HIT_PLAYER_NEIGHBOUR_CUBE = CONFIG.SCORE.Kill_hero_score//4 #due to not fact that hit, just try 





#FORCE_DUEL = False
FORCE_HARVEST = False
FORCE_ATTACK_PLAYERS = True
FORCE_STAYED_AT_PORTALS = False

ZOMBIE_CAN_CHANGE_DIRECTION = True


#FLASHING_PERKS = True
FLASHING_PERKS = False



DO_NOT_ATTACK_IMMORTAL = 5 #do not attack if immortal at least X moves
CHECK_BULLET_NEW = True


RATE_DEATH = 100
RATE_RISKY = (RATE_DEATH*3)//4
RATE_VERY_RISKY = (RATE_DEATH*9)//10
RATE_FIRE_MAKE_SHOT = -5

DANGER_RATE_DEATH = RATE_DEATH


#DANGER_RATE_PLAYER_CAN_FIRE   = (100,90)[FORCE_DUEL]
#DANGER_RATE_PLAYER_COULD_FIRE = (80,50)[FORCE_DUEL]


DANGER_AI_SIDEATTACK            = 80
DANGER_AI_SIDEATTACK_SIMULATION = 60

# Dangers
DANGER_RATE_ZOMBIE           = RATE_DEATH #death
DANGER_RATE_NEAR_ZOMBIE_FACE = RATE_DEATH #int(RATE_DEATH*0.9)
DANGER_RATE_NEAR_ZOMBIE_BACK = (RATE_DEATH*2)//3

DANGER_RATE_NEAR_PLAYER_BACK = (RATE_DEATH*2)//3 #can fire - high risk
DANGER_RATE_NEAR_PLAYER_FACE = (RATE_DEATH*8)//10 #can fire - high risk
DANGER_RATE_NEAR_PLAYER_DIAG = RATE_DEATH//2
DANGER_RATE_PLAYER           = RATE_DEATH//2 #mrisky to jump - can move and fire


#DANGER_DIST_RADIUS = 3
#DANGER_DIST_DECAY  = 5

DANGER_DIST_RADIUS = 3
DANGER_DIST_DECAY  = 5


