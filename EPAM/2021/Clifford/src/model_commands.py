#!/usr/bin/env python3

import model_directions as DIR

CMD_NULL        = -1

#basic commands
CMD_STOP        = 0

CMD_UP          = 1
CMD_DOWN        = 2
CMD_LEFT        = 3
CMD_RIGHT       = 4

CMD_MOVE_MASK_DEPRECATED   = 7 #inner


CMD_DIE              = 8
CMD_FIRE_LEFT        = 9   #stop and fire
CMD_FIRE_RIGHT       = 10  #stop and fire at the floor
CMD_FIRE_FLOOR_LEFT  = 11  #stop and fire at the floor
CMD_FIRE_FLOOR_RIGHT = 12  #stop and fire
CMD_OPEN_DOOR        = 13
CMD_CLOSE_DOOR       = 14
CMD_FIRE             = 15
#
CMD_FIRE_UP        = 16   #stop and fire
CMD_FIRE_DOWN      = 17  #stop and fire at the floor


#SPEC, COMPLEX
CMD_FIRE_FLOOR_LEFT_GO  = 20  #stop, fire at the floow and jump in hole
CMD_FIRE_FLOOR_RIGHT_GO = 21  #stop, fire at the floow and jump in hole


CMDS_ZOMBIE = {CMD_UP, CMD_DOWN, CMD_LEFT, CMD_RIGHT}

CMDS_FIRE = (
    CMD_FIRE,
    CMD_FIRE_LEFT,
    CMD_FIRE_RIGHT,
    CMD_FIRE_FLOOR_LEFT,
    CMD_FIRE_FLOOR_RIGHT,
    CMD_FIRE_FLOOR_LEFT_GO,
    CMD_FIRE_FLOOR_RIGHT_GO
)

CMDS_FIRE_BULLET = {
    CMD_FIRE        : DIR.DIR_UNKNOWN,
    CMD_FIRE_LEFT   : DIR.DIR_LEFT,
    CMD_FIRE_RIGHT  : DIR.DIR_RIGHT,
    CMD_FIRE_UP     : DIR.DIR_UP,
    CMD_FIRE_DOWN   : DIR.DIR_DOWN
}

#BASE COMMANDS
COMMANDS_BASE = {
    # CMD                     0:SEND              1:MOVESHIFT  2:W  3:DIR_AFTER         4:RATE  
    CMD_NULL  :             ( ""                , (0,0),   1,   DIR.DIR_UNKNOWN,    1 ),
    CMD_DIE   :             ( "ACT(0)"          , (0,0),   1,   DIR.DIR_UNKNOWN,    1 ),
    CMD_STOP  :             ( ""                , (0,0),   1,   DIR.DIR_STOP,       1 ),
    CMD_LEFT  :             ( "LEFT"            , (-1, 0), 1,   DIR.DIR_LEFT,       1 ),
    CMD_RIGHT :             ( "RIGHT"           , ( 1, 0), 1,   DIR.DIR_RIGHT,      1 ),
    CMD_UP    :             ( "UP"              , ( 0,-1), 1,   DIR.DIR_UP,         1 ),
    CMD_DOWN  :             ( "DOWN"            , ( 0, 1), 1,   DIR.DIR_DOWN,       1 ),
    CMD_FIRE_FLOOR_LEFT :   ( "ACT,LEFT"        , (0,0),   1,   DIR.DIR_LEFT,       1 ),
    CMD_FIRE_FLOOR_RIGHT:   ( "ACT,RIGHT"       , (0,0),   1,   DIR.DIR_RIGHT,      1 ),
    CMD_FIRE :              ( "ACT(1)"          , (0,0),   1,   DIR.DIR_SAME,       1 ),
    CMD_FIRE_LEFT  :        ( "ACT(1),LEFT"     , (0,0),   1,   DIR.DIR_LEFT,       1 ),
    CMD_FIRE_RIGHT :        ( "ACT(1),RIGHT"    , (0,0),   1,   DIR.DIR_RIGHT,      1 ),
    CMD_FIRE_UP    :        ( "ACT(1),UP"       , (0,0),   1,   DIR.DIR_STOP,       1 ), #on ladder unknown
    CMD_FIRE_DOWN  :        ( "ACT(1),DOWN"     , (0,0),   1,   DIR.DIR_STOP,       1 ), #on ladder unknown
    CMD_OPEN_DOOR  :        ( "ACT(2)"          , (0,0),   1,   DIR.DIR_STOP,       1 ),
    CMD_CLOSE_DOOR :        ( "ACT(3)"          , (0,0),   1,   DIR.DIR_STOP,       1 ),
}
COMMAND_BASE_NONE = COMMANDS_BASE[CMD_NULL]

COMMANDS_COMPLEX = {
    # CMD                       0:DESCRIPTION                     1:CMD_SEQUENCE                               2:Total shift  3:W   4:Final dir     5:RATE
    CMD_FIRE_FLOOR_LEFT_GO  : ( "Fire left  floor and jump down", (CMD_FIRE_FLOOR_LEFT,  CMD_LEFT,  CMD_DOWN), (-1, 1),       3,    DIR.DIR_STOP,   3.1 ),
    CMD_FIRE_FLOOR_RIGHT_GO : ( "Fire right floor and jump down", (CMD_FIRE_FLOOR_RIGHT, CMD_RIGHT, CMD_DOWN), ( 1, 1),       3,    DIR.DIR_STOP,   3.1 ), #if can go other way same lenth - go
}

COMAMNDS_SPECIAL = {
    # CMD                     0:SEND              1:PLAYER SHIFT  2.TARGET
    CMD_FIRE_FLOOR_LEFT :   ( "ACT,LEFT"        , (0,0),   (-1,1) ),
    CMD_FIRE_FLOOR_RIGHT:   ( "ACT,RIGHT"       , (0,0),   ( 1,1) )
}

QTMDD = 10
QT_COMMANDS_VIEW = {
    #                       x1,y1,x2,y2,clridx        color is    0:no move 1:move 2:fire
    CMD_STOP  :                 ( -5,  -3,   5,  -3,    0),
    CMD_LEFT  :                 ( 0,    0, -10,   0,    1),
    CMD_RIGHT :                 ( 0,    0,  10,   0,    1),
    CMD_UP    :                 ( 0,    0,   0, -10,    1),
    CMD_DOWN  :                 ( 0,    0,   0,  10,    1),
    CMD_FIRE_FLOOR_LEFT :       ( 0,    0, -10,  10,    2),
    CMD_FIRE_FLOOR_RIGHT:       ( 0,    0,  10,  10,    2),
    CMD_FIRE :                  ( -5,  -5,   5,  -5,    2),
    CMD_FIRE_LEFT  :            ( 0,    2, -10,   2,    2),
    CMD_FIRE_RIGHT :            ( 0,    2,  10,   2,    2),
    CMD_OPEN_DOOR  :            ( 0,    0,   0,   0,    None),
    CMD_CLOSE_DOOR :            ( 0,    0,   0,   0,    None),
    CMD_FIRE_FLOOR_LEFT_GO  :   ( 0,    0,  -5,  10,    2),
    CMD_FIRE_FLOOR_RIGHT_GO :   ( 0,    0,   5,  10,    2),
}

def COMMAND_GET_FIRST_MOVE(c):
    if c in COMMANDS_COMPLEX:
        return COMMANDS_COMPLEX[c][1][0]
    return c
    
def COMMAND_DESC(c):
    if c in COMMANDS_COMPLEX:
        return COMMANDS_COMPLEX[c][0]
    return COMMANDS_BASE[c][0]

def COMMAND_BASE_STR(c):
    return COMMANDS_BASE.get(c , COMMAND_BASE_NONE)[0]

def COMMAND_BASE_DXYD(c):
    d = COMMANDS_BASE[c]
    return *d[1], d[3]
    
def QSTAR_COMMAND_DXYW_TOTAL(c):
    if c in COMMANDS_COMPLEX:
        t = COMMANDS_COMPLEX[c]
        return ( *t[2], t[3])
    t = COMMANDS_BASE[c]
    return (*t[1], t[2])

def QSTAR_COMMAND_DXYWR_TOTAL(c):
    if c in COMMANDS_COMPLEX:
        t = COMMANDS_COMPLEX[c]
        return ( *t[2], t[3], t[5])
    t = COMMANDS_BASE[c]
    return (*t[1], t[2], t[4])

def QSTAR_GET_DIR_AFTER_CMD(c):
    if c in COMMANDS_COMPLEX:
        t = COMMANDS_COMPLEX[c]
        return t[4]
    t = COMMANDS_BASE[c]
    return t[3]

def QSTAR_RATE_CMD(c):
    if c in COMMANDS_COMPLEX:
        t = COMMANDS_COMPLEX[c]
        return t[5]
    t = COMMANDS_BASE[c]
    return t[4]

def COMMAND_HAS_FIRE(c):
    return c in CMDS_FIRE

def COMMAND_FIRE2DIR(c):
    return CMDS_FIRE_BULLET.get(c, None)


if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
