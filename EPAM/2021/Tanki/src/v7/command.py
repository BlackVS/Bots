#!/usr/bin/env python3

from directions import *
CMD_NULL        = 0

#basic commands
CMD_STOP = CMD_NULL

CMD_UP          = 1
CMD_DOWN        = 2
CMD_LEFT        = 3
CMD_RIGHT       = 4
CMD_FIRE        = 10

#compound commands
CMD_FIRE_AND_LEFT   = CMD_FIRE+CMD_LEFT
CMD_FIRE_AND_RIGHT  = CMD_FIRE+CMD_RIGHT
CMD_FIRE_AND_UP     = CMD_FIRE+CMD_UP
CMD_FIRE_AND_DOWN   = CMD_FIRE+CMD_DOWN

COMMANDS_MOVE = {CMD_LEFT, CMD_RIGHT, CMD_UP, CMD_DOWN}

COMMANDS_FIRE = {   CMD_FIRE, #fire to old direction?
                    CMD_FIRE_AND_LEFT,  
                    CMD_FIRE_AND_RIGHT,
                    CMD_FIRE_AND_UP,
                    CMD_FIRE_AND_DOWN,
}

COMMANDS_MOVE_AND_FIRE = {
    CMD_FIRE_AND_LEFT,  
    CMD_FIRE_AND_RIGHT,
    CMD_FIRE_AND_UP,
    CMD_FIRE_AND_DOWN,
}

MAP_COMMANDS_FIRE2DIR = {
    CMD_FIRE_AND_LEFT  : DIR_LEFT,
    CMD_FIRE_AND_RIGHT : DIR_RIGHT,
    CMD_FIRE_AND_UP    : DIR_UP,
    CMD_FIRE_AND_DOWN  : DIR_DOWN,
}

COMMANDS2DIR = {
    CMD_UP             : DIR_UP,
    CMD_DOWN           : DIR_DOWN,
    CMD_LEFT           : DIR_LEFT,
    CMD_RIGHT          : DIR_RIGHT,
    CMD_FIRE_AND_LEFT  : DIR_LEFT,
    CMD_FIRE_AND_RIGHT : DIR_RIGHT,
    CMD_FIRE_AND_UP    : DIR_UP,
    CMD_FIRE_AND_DOWN  : DIR_DOWN,
}

COMMANDS_NOTSTAY      = COMMANDS_MOVE | COMMANDS_MOVE_AND_FIRE
COMMANDS_ANY          = COMMANDS_MOVE | COMMANDS_FIRE | {CMD_NULL}
COMMANDS_ANY_NOT_FIRE = COMMANDS_MOVE | {CMD_NULL}

COMMANDS = {
    CMD_STOP : "",

    CMD_LEFT  : "LEFT",
    CMD_RIGHT : "RIGHT",
    CMD_UP    : "UP",
    CMD_DOWN  : "DOWN",
    CMD_FIRE       : "ACT",

    #fire in current direction and turn and move to
    CMD_FIRE_AND_LEFT   : "ACT,LEFT",  
    CMD_FIRE_AND_RIGHT  : "ACT,RIGHT",
    CMD_FIRE_AND_UP     : "ACT,UP",
    CMD_FIRE_AND_DOWN   : "ACT,DOWN",

    CMD_NULL : ""
}

COMMANDS_MOVE_DXY = {
    CMD_STOP  : (0 ,0),
    CMD_LEFT  : (-1, 0),
    CMD_RIGHT : ( 1, 0),
    CMD_UP    : ( 0,-1),
    CMD_DOWN  : ( 0, 1),

    CMD_FIRE  : (0,0),

    CMD_FIRE_AND_LEFT   : (-1, 0),  
    CMD_FIRE_AND_RIGHT  : ( 1, 0),
    CMD_FIRE_AND_UP     : ( 0,-1),
    CMD_FIRE_AND_DOWN   : ( 0, 1),

    CMD_NULL : (0,0),
}

COMMANDS_XYF = {
    CMD_STOP  : ( 0, 0, False),
    CMD_LEFT  : (-1, 0, False),
    CMD_RIGHT : ( 1, 0, False),
    CMD_UP    : ( 0,-1, False),
    CMD_DOWN  : ( 0, 1, False),

    CMD_FIRE  : (0, 0, True),

    CMD_FIRE_AND_LEFT   : (-1, 0, True),  
    CMD_FIRE_AND_RIGHT  : ( 1, 0, True),
    CMD_FIRE_AND_UP     : ( 0,-1, True),
    CMD_FIRE_AND_DOWN   : ( 0, 1, True),

    CMD_STOP  : ( 0, 0, False),
}

if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
