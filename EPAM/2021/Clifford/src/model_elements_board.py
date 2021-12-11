#! /usr/bin/env python3
import colors as COLOR
import model_directions as DIR
from model_object_perk import PERKTYPE

### ELEMENTS on BOARD (Input)
EB_UNKNOWN  = '?'
EB_WALL     = '█'
EB_BRICK    = '#'
EB_SPACE    = ' '

EB_BACKWAY  = 'O'
EB_LADDER   = 'L'
EB_PIPE     = '-'

EB_DOOR_BRONZE_OPENED   = 'b'
EB_DOOR_BRONZE_CLOSED   = 'B'

EB_DOOR_GOLD_OPENED   = 'g'
EB_DOOR_GOLD_CLOSED   = 'G'
    
EB_DOOR_SILVER_OPENED   = 's'
EB_DOOR_SILVER_CLOSED   = 'S'


# bullet->brick: * _x7 4 3 2 1 brick
EB_PIT_EMPTY     = '*'
EB_ZOMBIE_IN_PIT = 'X'
EB_PLAYER_IN_PIT = 'x'

EB_PIT_1   = '1'
EB_PIT_2   = '2'
EB_PIT_3   = '3'
EB_PIT_4   = '4'


E_BULLET  = '•'

SPRITES_COLORS = {
    EB_WALL    :  COLOR.DARK_GREY, 
    EB_BRICK   :  COLOR.BROWN,
    EB_SPACE   :  COLOR.BLACK,
}

SPRITES = {
    EB_UNKNOWN :   './sprites/board/unknown.png',
    EB_WALL    :   './sprites/board/wall.png',
    EB_BRICK   :   './sprites/board/brick.png',    
    EB_SPACE   :   './sprites/board/space.png',   
    EB_BACKWAY :   './sprites/board/backway.png',
    EB_LADDER  :   './sprites/board/ladder.png',
    EB_PIPE    :   './sprites/board/pipe.png',

    EB_DOOR_BRONZE_OPENED   :   './sprites/board/opened_door_bronze.png',
    EB_DOOR_BRONZE_CLOSED   :   './sprites/board/closed_door_bronze.png',

    EB_DOOR_GOLD_OPENED     :   './sprites/board/opened_door_gold.png',
    EB_DOOR_GOLD_CLOSED     :   './sprites/board/closed_door_gold.png',
    
    EB_DOOR_SILVER_OPENED   :   './sprites/board/opened_door_silver.png',
    EB_DOOR_SILVER_CLOSED   :   './sprites/board/closed_door_silver.png',


    EB_PIT_EMPTY      : './sprites/board/crack_pit.png',
    EB_ZOMBIE_IN_PIT  : './sprites/board/crack_pit.png',
    EB_PLAYER_IN_PIT  : './sprites/board/crack_pit.png',
    #EB_PIT_0  :   './sprites/board/crack_pit.png',
    EB_PIT_1  :   './sprites/board/pit_fill_1.png',
    EB_PIT_2  :   './sprites/board/pit_fill_2.png',
    EB_PIT_3  :   './sprites/board/pit_fill_3.png',
    EB_PIT_4  :   './sprites/board/pit_fill_4.png',
    #
    E_BULLET :   './sprites/board/bullet.png',
}


SPRITES_HERO_DIR = {
    DIR.DIR_UNKNOWN : './sprites/board/hero.png',
    DIR.DIR_STOP    : './sprites/board/hero.png',
    DIR.DIR_UP      : './sprites/board/hero.png',
    DIR.DIR_DOWN    : './sprites/board/hero.png',
    DIR.DIR_LEFT    : './sprites/board/hero_left.png',
    DIR.DIR_RIGHT   : './sprites/board/hero_right.png',
}

SPRITES_PLAYER_DIR   = {
    DIR.DIR_UNKNOWN : './sprites/board/player.png',
    DIR.DIR_STOP    : './sprites/board/player.png',
    DIR.DIR_UP      : './sprites/board/player.png',
    DIR.DIR_DOWN    : './sprites/board/player.png',
    DIR.DIR_LEFT    : './sprites/board/player_left.png',
    DIR.DIR_RIGHT   : './sprites/board/player_right.png',
}

SPRITES_ZOMBIE_DIR   = {
    DIR.DIR_UNKNOWN : './sprites/board/robber.png',
    DIR.DIR_STOP    : './sprites/board/robber.png',
    DIR.DIR_UP      : './sprites/board/robber.png',
    DIR.DIR_DOWN    : './sprites/board/robber.png',
    DIR.DIR_LEFT    : './sprites/board/robber_left.png',
    DIR.DIR_RIGHT   : './sprites/board/robber_right.png',
}


SPRITES_PERKS = {
    PERKTYPE.UNKNOWN   :    './sprites/board/clue_unknown.png',
    PERKTYPE.GLOVE     :    './sprites/board/clue_glove.png',
    PERKTYPE.KNIFE     :    './sprites/board/clue_knife.png',
    PERKTYPE.RING      :    './sprites/board/clue_ring.png',
    PERKTYPE.MASK      :    './sprites/board/clue_mask.png',
}


SPRITES_BULLET_DIR   = {
    DIR.DIR_UNKNOWN : './sprites/board/bullet.png',
    DIR.DIR_LEFT    : './sprites/board/bullet_left.png',
    DIR.DIR_RIGHT   : './sprites/board/bullet_right.png',
    DIR.DIR_UP      : './sprites/board/bullet_up.png',
    DIR.DIR_DOWN    : './sprites/board/bullet_down.png',
}

if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
