#! /usr/bin/env python3

from model_elements_board import *
from model_directions import *
import model_commands as CMDS

# Bullet. After the shot by the hero, the bullet flies until it meets an obstacle. 
# The bullet kills the hero. 
# It ricochets from the indestructible wall (no more than 1 time). 
# The bullet destroys the destructible wall.

BULLET_BARRIER = {
    EB_BRICK,
    EB_WALL,
} 

BULLET_CANT_HIT_UNDER = (
    EB_BRICK,
    EB_WALL,
    EB_LADDER,
    EB_BACKWAY #can but no sense
)

ZOMBIE_BARRIER = BULLET_BARRIER

PLAYER_BARRIER = BULLET_BARRIER

PLAYER_FALL_STAYING_ON = ( 
    EB_SPACE,   
    EB_BACKWAY,
    EB_DOOR_BRONZE_OPENED,
    EB_DOOR_BRONZE_CLOSED,
    EB_DOOR_GOLD_OPENED,
    EB_DOOR_GOLD_CLOSED,
    EB_DOOR_SILVER_OPENED,
    EB_DOOR_SILVER_CLOSED,
    EB_PIT_EMPTY, #тут тоже вроде не выпадает?
    EB_PIT_1,
    EB_PIT_2,
    EB_PIT_3,
    EB_PIT_4,
    EB_PIPE
)

PLAYER_FALL_IF_IN = ( 
    EB_SPACE,   
    EB_BACKWAY,
    EB_DOOR_BRONZE_OPENED,
    EB_DOOR_BRONZE_CLOSED,
    EB_DOOR_GOLD_OPENED,
    EB_DOOR_GOLD_CLOSED,
    EB_DOOR_SILVER_OPENED,
    EB_DOOR_SILVER_CLOSED,
    EB_PIT_EMPTY, #тут тоже вроде не выпадает?
    EB_PIT_1,
    EB_PIT_2,
    EB_PIT_3,
    EB_PIT_4,
)

PLAYER_NOT_UP = ( 
    EB_SPACE,   
    EB_BACKWAY,
    EB_DOOR_BRONZE_OPENED,
    EB_DOOR_BRONZE_CLOSED,
    EB_DOOR_GOLD_OPENED,
    EB_DOOR_GOLD_CLOSED,
    EB_DOOR_SILVER_OPENED,
    EB_DOOR_SILVER_CLOSED,
    EB_PIT_EMPTY,
    EB_PIT_1,
    EB_PIT_2,
    EB_PIT_3,
    EB_PIT_4,
    EB_PIPE,
    EB_UNKNOWN
)

PLAYER_CAN_STAY_ON = (
    EB_BRICK,
    EB_WALL,
    EB_LADDER,
    EB_PLAYER_IN_PIT,
    EB_ZOMBIE_IN_PIT,
)

PLAYER_NOT_FALL = ( 
    EB_LADDER,
)

PLAYER_FREE2GO = ( 
    EB_SPACE  ,   
    EB_BACKWAY,
    EB_DOOR_BRONZE_OPENED,
    EB_DOOR_BRONZE_CLOSED,
    EB_DOOR_GOLD_OPENED  ,
    EB_DOOR_GOLD_CLOSED  ,
    EB_DOOR_SILVER_OPENED,
    EB_DOOR_SILVER_CLOSED,
    EB_PIT_EMPTY,
    EB_PIT_1,
    EB_PIT_2,
    EB_PIT_3,
    EB_PIT_4,
    #
    EB_LADDER,
    EB_PIPE  ,
)


PLAYER_DIR2COMMANDS = {
    DIR_STOP    : [ ## base
                    CMDS.CMD_STOP, 
                    CMDS.CMD_FIRE_LEFT, 
                    CMDS.CMD_FIRE_RIGHT, 
                    CMDS.CMD_FIRE_FLOOR_LEFT, 
                    CMDS.CMD_FIRE_FLOOR_RIGHT, 
                    #CMDS.CMD_OPEN_DOOR, 
                    #CMDS.CMD_CLOSE_DOOR,
                    ## complex
                    CMDS.CMD_FIRE_FLOOR_LEFT_GO,
                    CMDS.CMD_FIRE_FLOOR_RIGHT_GO,
                    ],
    DIR_UP      : [CMDS.CMD_UP],
    DIR_DOWN    : [CMDS.CMD_DOWN],
    DIR_LEFT    : [CMDS.CMD_LEFT],
    DIR_RIGHT   : [CMDS.CMD_RIGHT],
}

BULLET_RICOCHET_FROM = [ EB_WALL ]
#with fire some troubles - if fire in same direction - will move, if in opposite - will stay - may be split to FIR_TOWARDS (moving), BACKWARS (stop with delay) ?
