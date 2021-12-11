#!/usr/bin/env python3


CMD_NULL        = 0
CMD_DIE         = 1

CMD_LEFT        = 2
CMD_RIGHT       = 3
CMD_UP          = 4
CMD_DOWN        = 5

CMD_JUMP        = 6
CMD_JUMP_LEFT   = 7 
CMD_JUMP_RIGHT  = 8
CMD_JUMP_UP     = 9
CMD_JUMP_DOWN   = 10

CMD_PULL_LEFT   = 11
CMD_PULL_RIGHT  = 12
CMD_PULL_UP     = 13
CMD_PULL_DOWN   = 14

CMD_FIRE_LEFT   = 15
CMD_FIRE_RIGHT  = 16
CMD_FIRE_UP     = 17
CMD_FIRE_DOWN   = 18


COMMANDS_MOVE = [ CMD_LEFT, CMD_RIGHT, CMD_UP, CMD_DOWN]
COMMANDS_JUMP = [ CMD_JUMP, CMD_JUMP_LEFT, CMD_JUMP_RIGHT, CMD_JUMP_UP, CMD_JUMP_DOWN]
COMMANDS_PULL = [ CMD_PULL_LEFT, CMD_PULL_RIGHT, CMD_PULL_UP, CMD_PULL_DOWN]
COMMANDS_FIRE = [ CMD_FIRE_LEFT, CMD_FIRE_RIGHT, CMD_FIRE_UP, CMD_FIRE_DOWN]

#COMMANDS_NOTSTAY = COMMANDS_MOVE + COMMANDS_PULL + [CMD_JUMP_LEFT, CMD_JUMP_RIGHT, CMD_JUMP_UP, CMD_JUMP_DOWN]
COMMANDS_NOTSTAY = COMMANDS_MOVE + [CMD_JUMP_LEFT, CMD_JUMP_RIGHT, CMD_JUMP_UP, CMD_JUMP_DOWN]

#COMMANDS_ANY = COMMANDS_MOVE + COMMANDS_JUMP + COMMANDS_PULL + COMMANDS_FIRE + [CMD_NULL] #+ CND_DIE
COMMANDS_ANY = COMMANDS_MOVE + COMMANDS_JUMP + COMMANDS_FIRE + [CMD_NULL] #+ CND_DIE
COMMANDS_ANY_NO_FIRE = COMMANDS_MOVE + COMMANDS_JUMP + [CMD_NULL] #+ CND_DIE

COMMANDS_XYTF = {
        CMD_NULL        : ( 0, 0, 1, False),
        CMD_LEFT        : (-1, 0, 1, False),
        CMD_RIGHT       : ( 1, 0, 1, False),
        CMD_UP          : ( 0,-1, 1, False),
        CMD_DOWN        : ( 0, 1, 1, False),
        CMD_JUMP        : ( 0, 0, 2, True ),
        CMD_JUMP_LEFT   : (-2, 0, 2, True ),
        CMD_JUMP_RIGHT  : ( 2, 0, 2, True ),
        CMD_JUMP_UP     : ( 0,-2, 2, True ),
        CMD_JUMP_DOWN   : ( 0, 2, 2, True ),
        CMD_PULL_LEFT   : (-1, 0, 1, False),
        CMD_PULL_RIGHT  : ( 1, 0, 1, False),
        CMD_PULL_UP     : ( 0,-1, 1, False),
        CMD_PULL_DOWN   : ( 0, 1, 1, False),
        CMD_FIRE_LEFT   : ( 0, 0, 1, False),
        CMD_FIRE_RIGHT  : ( 0, 0, 1, False),
        CMD_FIRE_UP     : ( 0, 0, 1, False),
        CMD_FIRE_DOWN   : ( 0, 0, 1, False),
}

COMMANDS = {
    CMD_DIE     :   "ACT(0)",
    CMD_LEFT    :   "LEFT",
    CMD_RIGHT   :   "RIGHT",
    CMD_UP      :   "UP",
    CMD_DOWN    :   "DOWN",

    CMD_JUMP        :   "ACT(1)",
    CMD_JUMP_LEFT   :   "ACT(1),LEFT",
    CMD_JUMP_RIGHT  :   "ACT(1),RIGHT",
    CMD_JUMP_UP     :   "ACT(1),UP",
    CMD_JUMP_DOWN   :   "ACT(1),DOWN",

    CMD_PULL_LEFT   :   "ACT(2),LEFT",
    CMD_PULL_RIGHT  :   "ACT(2),RIGHT",
    CMD_PULL_UP     :   "ACT(2),UP",
    CMD_PULL_DOWN   :   "ACT(2),DOWN",

    CMD_FIRE_LEFT   :   "ACT(3),LEFT",
    CMD_FIRE_RIGHT  :   "ACT(3),RIGHT",
    CMD_FIRE_UP     :   "ACT(3),UP",
    CMD_FIRE_DOWN   :   "ACT(3),DOWN",

    CMD_NULL : ""
}

COMMANDS_REVERSE = {
    CMD_DIE     :   "ACT(0)",
    CMD_LEFT    :   "LEFT",
    CMD_RIGHT   :   "RIGHT",
    CMD_UP      :   "DOWN",
    CMD_DOWN    :   "UP",

    CMD_JUMP        :   "ACT(1)",
    CMD_JUMP_LEFT   :   "ACT(1),LEFT",
    CMD_JUMP_RIGHT  :   "ACT(1),RIGHT",
    CMD_JUMP_UP     :   "ACT(1),DOWN",
    CMD_JUMP_DOWN   :   "ACT(1),UP",

    CMD_PULL_LEFT   :   "ACT(2),LEFT",
    CMD_PULL_RIGHT  :   "ACT(2),RIGHT",
    CMD_PULL_UP     :   "ACT(2),DOWN",
    CMD_PULL_DOWN   :   "ACT(2),UP",

    CMD_FIRE_LEFT   :   "ACT(3),LEFT",
    CMD_FIRE_RIGHT  :   "ACT(3),RIGHT",
    CMD_FIRE_UP     :   "ACT(3),DOWN",
    CMD_FIRE_DOWN   :   "ACT(3),UP",

    CMD_NULL : ""
}


COMMANDS_MEXT = {

    CMD_DIE     :   COMMANDS_ANY,
    CMD_LEFT    :   COMMANDS_ANY,
    CMD_RIGHT   :   COMMANDS_ANY,
    CMD_UP      :   COMMANDS_ANY,
    CMD_DOWN    :   COMMANDS_ANY,

    #actually next command ignored until jump finished
    CMD_JUMP        :   [CMD_NULL], 
    #but we imitate flying to uypdate hero position correctly
    CMD_JUMP_LEFT   :   [CMD_LEFT],
    CMD_JUMP_RIGHT  :   [CMD_RIGHT],
    CMD_JUMP_UP     :   [CMD_UP],
    CMD_JUMP_DOWN   :   [CMD_DOWN],

    CMD_PULL_LEFT   :   COMMANDS_ANY,
    CMD_PULL_RIGHT  :   COMMANDS_ANY,
    CMD_PULL_UP     :   COMMANDS_ANY,
    CMD_PULL_DOWN   :   COMMANDS_ANY,

    #actually usually except fire but it depends of perks
    CMD_FIRE_LEFT   :   COMMANDS_ANY,
    CMD_FIRE_RIGHT  :   COMMANDS_ANY,
    CMD_FIRE_UP     :   COMMANDS_ANY,
    CMD_FIRE_DOWN   :   COMMANDS_ANY,

    CMD_NULL        :   COMMANDS_ANY

}

COMMANDS_FIRE_DXY = {
    CMD_FIRE_LEFT   :   (-1,0),
    CMD_FIRE_RIGHT  :   (1,0),
    CMD_FIRE_UP     :   (0,-1),
    CMD_FIRE_DOWN   :   (0,1)      
}

if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
