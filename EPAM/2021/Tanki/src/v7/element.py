#! /usr/bin/env python3
from directions import *


EWALL='╬'
EWALL_DESTROYED_DOWN='╩'
EWALL_DESTROYED_UP='╦'
EWALL_DESTROYED_LEFT='╠'
EWALL_DESTROYED_RIGHT='╣'
EWALL_DESTROYED_DOWN_TWICE='╨'
EWALL_DESTROYED_UP_TWICE='╥'
EWALL_DESTROYED_LEFT_TWICE='╞'
EWALL_DESTROYED_RIGHT_TWICE='╡'
EWALL_DESTROYED_LEFT_RIGHT='│'
EWALL_DESTROYED_UP_DOWN='─'
EWALL_DESTROYED_UP_LEFT='┌'
EWALL_DESTROYED_RIGHT_UP='┐'
EWALL_DESTROYED_DOWN_LEFT='└'
EWALL_DESTROYED_DOWN_RIGHT='┘'

EAI_TANK_UP='?'
EAI_TANK_RIGHT='»'
EAI_TANK_DOWN='¿'
EAI_TANK_LEFT='«'
EAI_TANK_PRIZE='◘'

EOTHER_TANK_UP='˄'
EOTHER_TANK_RIGHT='˃'
EOTHER_TANK_DOWN='˅'
EOTHER_TANK_LEFT='˂'

ETANK_UP='▲'
ETANK_RIGHT='►'
ETANK_DOWN='▼'
ETANK_LEFT='◄'

EBULLET='•'
EBATTLE_WALL='☼'
EBANG='Ѡ'
EICE='#'
ETREE='%'
ERIVER='~'
ESPACE=' '

EPRIZE = '!'
EPRIZE_IMMORTALITY = '1'
EPRIZE_BREAKING_WALLS = '2'
EPRIZE_WALKING_ON_WATER = '3'
EPRIZE_VISIBILITY = '4'
EPRIZE_NO_SLIDING = '5'


###
EAI_TANK_UNKNOWN    = 'U1'
EOTHER_TANK_UNKNOWN = 'U2'
ETANK_UNKNOWN       = 'U2'

ETANK_TYPE_ME    = 'T1'
ETANK_TYPE_AI    = 'T2'
ETANK_TYPE_OTHER = 'T3'

EBULLET_LEFT  = 'BL'
EBULLET_RIGHT = 'BR'
EBULLET_UP    = 'BU'
EBULLET_DOWN  = 'BD'
###

TANK2DIR = {
    EAI_TANK_UP     : DIR_UP,
    EAI_TANK_RIGHT  : DIR_RIGHT,
    EAI_TANK_DOWN   : DIR_DOWN,
    EAI_TANK_LEFT   : DIR_LEFT,
    EAI_TANK_PRIZE  : DIR_UNKNOWN,
    EAI_TANK_UNKNOWN: DIR_UNKNOWN,

    EOTHER_TANK_UP   : DIR_UP,
    EOTHER_TANK_RIGHT: DIR_RIGHT,
    EOTHER_TANK_DOWN : DIR_DOWN,
    EOTHER_TANK_LEFT : DIR_LEFT,
    EOTHER_TANK_UNKNOWN : DIR_UNKNOWN,

    ETANK_UP        : DIR_UP,
    ETANK_RIGHT     : DIR_RIGHT,
    ETANK_DOWN      : DIR_DOWN,
    ETANK_LEFT      : DIR_LEFT,
    ETANK_UNKNOWN   : DIR_UNKNOWN,
}


EWALL_1_3 = "v"
EWALL_2_3 = "V"

ELS_DESTROYED_WALLS = {
    EWALL_DESTROYED_DOWN,
    EWALL_DESTROYED_UP,
    EWALL_DESTROYED_LEFT,
    EWALL_DESTROYED_RIGHT,
    EWALL_DESTROYED_DOWN_TWICE,
    EWALL_DESTROYED_UP_TWICE,
    EWALL_DESTROYED_LEFT_TWICE,
    EWALL_DESTROYED_RIGHT_TWICE,
    EWALL_DESTROYED_LEFT_RIGHT,
    EWALL_DESTROYED_UP_DOWN,
    EWALL_DESTROYED_UP_LEFT,
    EWALL_DESTROYED_RIGHT_UP,
    EWALL_DESTROYED_DOWN_LEFT,
    EWALL_DESTROYED_DOWN_RIGHT,
}

ELS_WALLS = {
    EWALL,
    EWALL_1_3,
    EWALL_2_3,
}

ESTATIC_ELEMENTS = {
    EWALL,
    EWALL_1_3,
    EWALL_2_3,
    # EWALL_DESTROYED_DOWN,
    # EWALL_DESTROYED_UP,
    # EWALL_DESTROYED_LEFT,
    # EWALL_DESTROYED_RIGHT,
    # EWALL_DESTROYED_DOWN_TWICE,
    # EWALL_DESTROYED_UP_TWICE,
    # EWALL_DESTROYED_LEFT_TWICE,
    # EWALL_DESTROYED_RIGHT_TWICE,
    # EWALL_DESTROYED_LEFT_RIGHT,
    # EWALL_DESTROYED_UP_DOWN,
    # EWALL_DESTROYED_UP_LEFT,
    # EWALL_DESTROYED_RIGHT_UP,
    # EWALL_DESTROYED_DOWN_LEFT,
    # EWALL_DESTROYED_DOWN_RIGHT,
    EBATTLE_WALL,
    EICE,
    ETREE,
    ERIVER,
    ESPACE
} 

ELS_FREE_SPACE  = { EICE, ETREE, ESPACE} #ERIVER

ELS_TANK_ME     = { ETANK_UP, ETANK_RIGHT, ETANK_DOWN, ETANK_LEFT}
ELS_TANKS_AI    = { EAI_TANK_UP, EAI_TANK_RIGHT, EAI_TANK_DOWN, EAI_TANK_LEFT, EAI_TANK_PRIZE}
ELS_TANKS_OTHER = { EOTHER_TANK_UP, EOTHER_TANK_RIGHT, EOTHER_TANK_DOWN, EOTHER_TANK_LEFT}

ELS_PERKS = { EPRIZE_IMMORTALITY, EPRIZE_BREAKING_WALLS, EPRIZE_WALKING_ON_WATER, EPRIZE_VISIBILITY, EPRIZE_NO_SLIDING, EPRIZE }

DIR2TANK        = [ ETANK_UNKNOWN, ETANK_UP, ETANK_DOWN, ETANK_LEFT, ETANK_RIGHT]
DIR2TANK_AI     = [ EAI_TANK_UNKNOWN, EAI_TANK_UP, EAI_TANK_DOWN, EAI_TANK_LEFT, EAI_TANK_RIGHT]
DIR2TANK_OTHER  = [ EOTHER_TANK_UNKNOWN, EOTHER_TANK_UP, EOTHER_TANK_DOWN, EOTHER_TANK_LEFT, EOTHER_TANK_RIGHT]
DIR2BULLET      = [ EBULLET, EBULLET_UP, EBULLET_DOWN, EBULLET_LEFT, EBULLET_RIGHT]

## Sprites



EDESTROYED_WALLS_MAP = {
    EWALL       : EWALL,

    EWALL_DESTROYED_DOWN        : EWALL_2_3,
    EWALL_DESTROYED_UP          : EWALL_2_3,
    EWALL_DESTROYED_LEFT        : EWALL_2_3,
    EWALL_DESTROYED_RIGHT       : EWALL_2_3,

    EWALL_DESTROYED_DOWN_TWICE  : EWALL_1_3,
    EWALL_DESTROYED_UP_TWICE    : EWALL_1_3,
    EWALL_DESTROYED_LEFT_TWICE  : EWALL_1_3,
    EWALL_DESTROYED_RIGHT_TWICE : EWALL_1_3,
    EWALL_DESTROYED_LEFT_RIGHT  : EWALL_1_3,
    EWALL_DESTROYED_UP_DOWN     : EWALL_1_3,
    EWALL_DESTROYED_UP_LEFT     : EWALL_1_3,
    EWALL_DESTROYED_RIGHT_UP    : EWALL_1_3,
    EWALL_DESTROYED_DOWN_LEFT   : EWALL_1_3,
    EWALL_DESTROYED_DOWN_RIGHT  : EWALL_1_3,
}

ESPRITES = {
    EWALL     : './sprites/wall.png',
    EWALL_1_3 : './sprites/wall_1_3.png',
    EWALL_2_3 : './sprites/wall_2_3.png',
    EWALL_DESTROYED_DOWN        : './sprites/wall_destroyed_down.png',
    EWALL_DESTROYED_UP          : './sprites/wall_destroyed_up.png',
    EWALL_DESTROYED_LEFT        : './sprites/wall_destroyed_left.png',
    EWALL_DESTROYED_RIGHT       : './sprites/wall_destroyed_right.png',
    EWALL_DESTROYED_DOWN_TWICE  : './sprites/wall_destroyed_down_twice.png',
    EWALL_DESTROYED_UP_TWICE    : './sprites/wall_destroyed_up_twice.png',
    EWALL_DESTROYED_LEFT_TWICE  : './sprites/wall_destroyed_left_twice.png',
    EWALL_DESTROYED_RIGHT_TWICE : './sprites/wall_destroyed_right_twice.png',
    EWALL_DESTROYED_LEFT_RIGHT  : './sprites/wall_destroyed_left_right.png',
    EWALL_DESTROYED_UP_DOWN     : './sprites/wall_destroyed_up_down.png',
    EWALL_DESTROYED_UP_LEFT     : './sprites/wall_destroyed_up_left.png',
    EWALL_DESTROYED_RIGHT_UP    : './sprites/wall_destroyed_right_up.png',
    EWALL_DESTROYED_DOWN_LEFT   : './sprites/wall_destroyed_down_left.png',
    EWALL_DESTROYED_DOWN_RIGHT  : './sprites/wall_destroyed_down_right.png',

    EAI_TANK_UP     : './sprites/ai_tank_up.png',
    EAI_TANK_RIGHT  : './sprites/ai_tank_right.png',
    EAI_TANK_DOWN   : './sprites/ai_tank_down.png',
    EAI_TANK_LEFT   : './sprites/ai_tank_left.png',
    EAI_TANK_PRIZE  : './sprites/ai_tank_prize.png',
    EAI_TANK_UNKNOWN : './sprites/ai_tank_unknown.png',

    EOTHER_TANK_UP      : './sprites/other_tank_up.png',
    EOTHER_TANK_RIGHT   : './sprites/other_tank_right.png',
    EOTHER_TANK_DOWN    : './sprites/other_tank_down.png',
    EOTHER_TANK_LEFT    : './sprites/other_tank_left.png',
    EOTHER_TANK_UNKNOWN : './sprites/other_tank_unknown.png',

    ETANK_UP    : './sprites/tank_up.png',
    ETANK_RIGHT : './sprites/tank_right.png',
    ETANK_DOWN  : './sprites/tank_down.png',
    ETANK_LEFT  : './sprites/tank_left.png',
    ETANK_UNKNOWN : './sprites/tank_unknown.png',

    EBULLET     : './sprites/bullet.png',
    EBATTLE_WALL: './sprites/battle_wall.png',
    EBANG       : './sprites/bang.png',
    EICE        : './sprites/ice.png',
    ETREE       : './sprites/tree.png',
    ERIVER      : './sprites/river.png',
    ESPACE      : './sprites/none.png',

    EBULLET_LEFT  : './sprites/laser_L',
    EBULLET_RIGHT : './sprites/laser_R',
    EBULLET_UP    : './sprites/laser_U',
    EBULLET_DOWN  : './sprites/laser_D',


    EPRIZE                  : './sprites/prize.png',
    EPRIZE_IMMORTALITY      : './sprites/prize_immortality.png',
    EPRIZE_BREAKING_WALLS   : './sprites/prize_breaking_walls.png',
    EPRIZE_WALKING_ON_WATER : './sprites/prize_walking_on_water.png',
    EPRIZE_VISIBILITY       : './sprites/prize_visibility.png',
    EPRIZE_NO_SLIDING       : './sprites/prize_sliding.png',
}

ELS_BULLET_BARRIER = {
    EBATTLE_WALL,
    EWALL,
    EWALL_1_3,
    EWALL_2_3,    
} | ELS_PERKS

ELS_AI_BARRIER = {
    ERIVER,
} | ELS_BULLET_BARRIER

ELS_PLAYER_NO_MOVES = ELS_AI_BARRIER

if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
