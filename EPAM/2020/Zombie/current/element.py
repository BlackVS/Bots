#! /usr/bin/env python3


from argparse import ArgumentError

#all layers
EUNKNOWN = "█"

################################################################################
#LAYER1
################################################################################

EFLOOR="."

# walls
EANGLE_IN_LEFT=b"\xe2\x95\x94".decode()     # encoded "╔" char
EWALL_FRONT=b"\xe2\x95\x90".decode()        # encoded "═" char
EANGLE_IN_RIGHT=b"\xe2\x94\x90".decode()    # encoded "┐" char
EWALL_RIGHT=b"\xe2\x94\x82".decode()        # encoded "│" char
EANGLE_BACK_RIGHT=b"\xe2\x94\x98".decode()  # encoded "┘" char
EWALL_BACK=b"\xe2\x94\x80".decode()         # encoded "─" char
EANGLE_BACK_LEFT=b"\xe2\x94\x94".decode()   # encoded "└" char
EWALL_LEFT=b"\xe2\x95\x91".decode()         # encoded "║" char
EWALL_BACK_ANGLE_LEFT=b"\xe2\x94\x8c".decode()      # encoded "┌" char
EWALL_BACK_ANGLE_RIGHT=b"\xe2\x95\x97".decode()     # encoded "╗" char
EANGLE_OUT_RIGHT=b"\xe2\x95\x9d".decode()   # encoded "╝" char
EANGLE_OUT_LEFT=b"\xe2\x95\x9a".decode()    # encoded "╚" char

ESPACE=" "

#custom
EWALL = "#"

# laser machine
ELASER_MACHINE_CHARGING_LEFT=b"\xcb\x82".decode()   # encoded "˂" char
ELASER_MACHINE_CHARGING_RIGHT=b"\xcb\x83".decode()  # encoded "˃" char
ELASER_MACHINE_CHARGING_UP=b"\xcb\x84".decode()     # encoded "˄" char
ELASER_MACHINE_CHARGING_DOWN=b"\xcb\x85".decode()   # encoded "˅" char

# lase machine ready
ELASER_MACHINE_READY_LEFT=b"\xe2\x97\x84".decode()  # encoded "◄" char
ELASER_MACHINE_READY_RIGHT=b"\xe2\x96\xba".decode() # encoded "►" char
ELASER_MACHINE_READY_UP=b"\xe2\x96\xb2".decode()    # encoded "▲" char
ELASER_MACHINE_READY_DOWN=b"\xe2\x96\xbc".decode()  # encoded "▼" char

# other stuff
ESTART="S"
EEXIT="E"
EHOLE="O"

EZOMBIE_START="Z"
EGOLD="$"

# perks
EUNSTOPPABLE_LASER_PERK="l"
EDEATH_RAY_PERK="r"
EUNLIMITED_FIRE_PERK="f"

# system elements, don"t touch it
EFOG="F"


################################################################################
#LAYER2
################################################################################

# empty space where player can go
EEMPTY="-"

EBOX="B"

# your robot
EROBO=b"\xe2\x98\xba".decode()  # encoded "☺" char
EROBO_FALLING="o"
EROBO_LASER=b"\xe2\x98\xbb".decode()  # encoded "☻" char

# other robot
EROBO_OTHER="X"
EROBO_OTHER_FALLING="x"
EROBO_OTHER_LASER="&"

# laser
ELASER_LEFT=b"\xe2\x86\x90".decode()  # encoded "←" char
ELASER_RIGHT=b"\xe2\x86\x92".decode()  # encoded "→" char
ELASER_UP=b"\xe2\x86\x91".decode()  # encoded "↑" char
ELASER_DOWN=b"\xe2\x86\x93".decode()  # encoded "↓" char

# zombie
EFEMALE_ZOMBIE=b"\xe2\x99\x80".decode()  # encoded "♀" char
EMALE_ZOMBIE=b"\xe2\x99\x82".decode()  # encoded "♂" char
EZOMBIE_DIE=b"\xe2\x9c\x9d".decode()  # encoded "✝" char

# system elements, don"t touch it
EBACKGROUND="G"

################################################################################
#LAYER3
################################################################################

EROBO_FLYING="*"
EROBO_OTHER_FLYING="^"

_ELEMENTS = dict(

    UNKNOWN = ("LAYER1", "█"),

    # empty space where player can go
    EMPTY=("LAYER2", "-"),
    FLOOR=("LAYER1", "."),

    # walls
    ANGLE_IN_LEFT=("LAYER1", b"\xe2\x95\x94".decode()),  # encoded "╔" char
    WALL_FRONT=("LAYER1", b"\xe2\x95\x90".decode()),  # encoded "═" char
    ANGLE_IN_RIGHT=("LAYER1", b"\xe2\x94\x90".decode()),  # encoded "┐" char
    WALL_RIGHT=("LAYER1", b"\xe2\x94\x82".decode()),  # encoded "│" char
    ANGLE_BACK_RIGHT=("LAYER1", b"\xe2\x94\x98".decode()),  # encoded "┘" char
    WALL_BACK=("LAYER1", b"\xe2\x94\x80".decode()),  # encoded "─" char
    ANGLE_BACK_LEFT=("LAYER1", b"\xe2\x94\x94".decode()),  # encoded "└" char
    WALL_LEFT=("LAYER1", b"\xe2\x95\x91".decode()),  # encoded "║" char
    WALL_BACK_ANGLE_LEFT=("LAYER1", b"\xe2\x94\x8c".decode()),  # encoded "┌" char
    WALL_BACK_ANGLE_RIGHT=("LAYER1", b"\xe2\x95\x97".decode()),  # encoded "╗" char
    ANGLE_OUT_RIGHT=("LAYER1", b"\xe2\x95\x9d".decode()),  # encoded "╝" char
    ANGLE_OUT_LEFT=("LAYER1", b"\xe2\x95\x9a".decode()),  # encoded "╚" char
    SPACE=("LAYER1", " "),

    # laser machine
    LASER_MACHINE_CHARGING_LEFT=("LAYER1", b"\xcb\x82".decode()),  # encoded "˂" char
    LASER_MACHINE_CHARGING_RIGHT=("LAYER1", b"\xcb\x83".decode()),  # encoded "˃" char
    LASER_MACHINE_CHARGING_UP=("LAYER1", b"\xcb\x84".decode()),  # encoded "˄" char
    LASER_MACHINE_CHARGING_DOWN=("LAYER1", b"\xcb\x85".decode()),  # encoded "˅" char

    # lase machine ready
    LASER_MACHINE_READY_LEFT=("LAYER1", b"\xe2\x97\x84".decode()),  # encoded "◄" char
    LASER_MACHINE_READY_RIGHT=("LAYER1", b"\xe2\x96\xba".decode()),  # encoded "►" char
    LASER_MACHINE_READY_UP=("LAYER1", b"\xe2\x96\xb2".decode()),  # encoded "▲" char
    LASER_MACHINE_READY_DOWN=("LAYER1", b"\xe2\x96\xbc".decode()),  # encoded "▼" char

    # other stuff
    START=("LAYER1", "S"),
    EXIT=("LAYER1", "E"),
    HOLE=("LAYER1", "O"),
    BOX=("LAYER2", "B"),
    ZOMBIE_START=("LAYER1", "Z"),
    GOLD=("LAYER1", "$"),

    # your robot
    ROBO=("LAYER2", b"\xe2\x98\xba".decode()),  # encoded "☺" char
    ROBO_FALLING=("LAYER2", "o"),
    ROBO_FLYING=("LAYER3", "*"),
    ROBO_LASER=("LAYER2", b"\xe2\x98\xbb".decode()),  # encoded "☻" char

    # other robot
    ROBO_OTHER=("LAYER2", "X"),
    ROBO_OTHER_FALLING=("LAYER2", "x"),
    ROBO_OTHER_FLYING=("LAYER3", "^"),
    ROBO_OTHER_LASER=("LAYER2", "&"),

    # laser
    LASER_LEFT=("LAYER2", b"\xe2\x86\x90".decode()),  # encoded "←" char
    LASER_RIGHT=("LAYER2", b"\xe2\x86\x92".decode()),  # encoded "→" char
    LASER_UP=("LAYER2", b"\xe2\x86\x91".decode()),  # encoded "↑" char
    LASER_DOWN=("LAYER2", b"\xe2\x86\x93".decode()),  # encoded "↓" char


    # zombie
    FEMALE_ZOMBIE=("LAYER2", b"\xe2\x99\x80".decode()),  # encoded "♀" char
    MALE_ZOMBIE=("LAYER2", b"\xe2\x99\x82".decode()),  # encoded "♂" char
    ZOMBIE_DIE=("LAYER2", b"\xe2\x9c\x9d".decode()),  # encoded "✝" char

    # perks
    UNSTOPPABLE_LASER_PERK=("LAYER1", "l"),
    DEATH_RAY_PERK=("LAYER1", "r"),
    UNLIMITED_FIRE_PERK=("LAYER1", "f"),

    # system elements, don"t touch it
    FOG=("LAYER1", "F"),
    BACKGROUND=("LAYER2", "G")
)

LASER_LEFTRIGHT = b"\xe2\x87\x84".decode() # 
LASER_TOPDOWN   = b"\xe2\x87\x85".decode() #

ELASER_GUN = [
    ELASER_MACHINE_CHARGING_LEFT,
    ELASER_MACHINE_CHARGING_RIGHT,
    ELASER_MACHINE_CHARGING_UP,
    ELASER_MACHINE_CHARGING_DOWN,
    ELASER_MACHINE_READY_LEFT,
    ELASER_MACHINE_READY_RIGHT,
    ELASER_MACHINE_READY_UP,
    ELASER_MACHINE_READY_DOWN,
]

ELASER_GUN_STATIC = {
    ELASER_MACHINE_CHARGING_LEFT  :ELASER_MACHINE_CHARGING_LEFT,
    ELASER_MACHINE_CHARGING_RIGHT :ELASER_MACHINE_CHARGING_RIGHT,
    ELASER_MACHINE_CHARGING_UP    :ELASER_MACHINE_CHARGING_UP,
    ELASER_MACHINE_CHARGING_DOWN  :ELASER_MACHINE_CHARGING_DOWN,
    ELASER_MACHINE_READY_LEFT     :ELASER_MACHINE_CHARGING_LEFT,
    ELASER_MACHINE_READY_RIGHT    :ELASER_MACHINE_CHARGING_RIGHT,
    ELASER_MACHINE_READY_UP       :ELASER_MACHINE_CHARGING_UP,
    ELASER_MACHINE_READY_DOWN     :ELASER_MACHINE_CHARGING_DOWN,
}

ELASER_GUN_READY = [
    ELASER_MACHINE_READY_LEFT,
    ELASER_MACHINE_READY_RIGHT,
    ELASER_MACHINE_READY_UP,
    ELASER_MACHINE_READY_DOWN,
]

ELASER_GUN_SHOT_MAP = {
    ELASER_MACHINE_READY_LEFT : ELASER_LEFT,
    ELASER_MACHINE_READY_RIGHT: ELASER_RIGHT,
    ELASER_MACHINE_READY_UP   : ELASER_UP,
    ELASER_MACHINE_READY_DOWN : ELASER_DOWN
}

ELASER_SHOTS = [
    ELASER_LEFT,
    ELASER_RIGHT,
    ELASER_UP,
    ELASER_DOWN
]

ESTATIC_ELEMENTS = [
    EFLOOR,
    EANGLE_IN_LEFT,
    EWALL_FRONT,
    EANGLE_IN_RIGHT,
    EWALL_RIGHT,
    EANGLE_BACK_RIGHT,
    EWALL_BACK,
    EANGLE_BACK_LEFT,
    EWALL_LEFT,
    EWALL_BACK_ANGLE_LEFT,
    EWALL_BACK_ANGLE_RIGHT,
    EANGLE_OUT_RIGHT,
    EANGLE_OUT_LEFT,
    ESPACE,
    ESTART,
    EEXIT,
    EHOLE,
    EZOMBIE_START,
    EGOLD,
    EFOG,
    EWALL, #custom - any wall
    EBOX,
]

ESTATIC_WALLS = [
    EANGLE_IN_LEFT,
    EWALL_FRONT,
    EANGLE_IN_RIGHT,
    EWALL_RIGHT,
    EANGLE_BACK_RIGHT,
    EWALL_BACK,
    EANGLE_BACK_LEFT,
    EWALL_LEFT,
    EWALL_BACK_ANGLE_LEFT,
    EWALL_BACK_ANGLE_RIGHT,
    EANGLE_OUT_RIGHT,
    EANGLE_OUT_LEFT,
]

ENOMOVES = ESTATIC_WALLS + ELASER_GUN + ELASER_SHOTS
ENOMOVES += [
    ESPACE,
    EHOLE,
    EWALL,
    EBOX,
]

EFIRE_TARGETS = [
    EFEMALE_ZOMBIE,
    EMALE_ZOMBIE,
    EROBO_OTHER
]

EFIRE_BLOCKING = ESTATIC_WALLS + ELASER_GUN
EFIRE_BLOCKING += [
    EWALL,
    EBOX
]

EFIRE_BLOCKING_PERK_UNSTOP = ESTATIC_WALLS + ELASER_GUN + [EWALL] #exclude eboxes

ELASERS_STOPS =[
    EANGLE_IN_LEFT,
    EWALL_FRONT,
    EANGLE_IN_RIGHT,
    EWALL_RIGHT,
    EANGLE_BACK_RIGHT,
    EWALL_BACK,
    EANGLE_BACK_LEFT,
    EWALL_LEFT,
    EWALL_BACK_ANGLE_LEFT,
    EWALL_BACK_ANGLE_RIGHT,
    EANGLE_OUT_RIGHT,
    EANGLE_OUT_LEFT,
    EWALL, #custom - any wall
    EBOX,
    EFEMALE_ZOMBIE,
    EMALE_ZOMBIE,
    EROBO,
    EROBO_OTHER,
    ELASER_MACHINE_CHARGING_LEFT,
    ELASER_MACHINE_CHARGING_RIGHT,
    ELASER_MACHINE_CHARGING_UP,
    ELASER_MACHINE_CHARGING_DOWN,
    ELASER_MACHINE_READY_LEFT,
    ELASER_MACHINE_READY_RIGHT,
    ELASER_MACHINE_READY_UP,
    ELASER_MACHINE_READY_DOWN,    
]


EPERKS = [ EUNSTOPPABLE_LASER_PERK, EDEATH_RAY_PERK, EUNLIMITED_FIRE_PERK ]

EL_REVERSE = {
    #
    ELASER_MACHINE_CHARGING_UP   : ELASER_MACHINE_CHARGING_DOWN,
    ELASER_MACHINE_CHARGING_DOWN : ELASER_MACHINE_CHARGING_UP,
    ELASER_MACHINE_READY_UP      : ELASER_MACHINE_READY_DOWN,
    ELASER_MACHINE_READY_DOWN    : ELASER_MACHINE_READY_UP,
    ELASER_UP                    : ELASER_DOWN,
    ELASER_DOWN                  : ELASER_UP,
    #
    ELASER_MACHINE_CHARGING_LEFT : ELASER_MACHINE_CHARGING_LEFT,
    ELASER_MACHINE_CHARGING_RIGHT: ELASER_MACHINE_CHARGING_RIGHT,
    ELASER_MACHINE_READY_LEFT    : ELASER_MACHINE_READY_LEFT,
    ELASER_MACHINE_READY_RIGHT   : ELASER_MACHINE_READY_RIGHT,
    ELASER_LEFT                  : ELASER_LEFT,
    ELASER_RIGHT                 : ELASER_RIGHT,
}

ELASERGUN_DX2T = {
    (-1, 0) : ELASER_LEFT,
    ( 1, 0) : ELASER_RIGHT,
    ( 0,-1) : ELASER_UP,
    ( 0, 1) : ELASER_DOWN,
}

if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
