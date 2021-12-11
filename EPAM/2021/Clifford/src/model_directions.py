#!/usr/bin/env python3

# DIRECCTIONS
DIR_UNKNOWN = -1

DIR_STOP    = 0
DIR_UP      = 1
DIR_DOWN    = 2
DIR_LEFT    = 3
DIR_RIGHT   = 4
DIR_PIT = 5
#
DIR_SAME = 10  #just for callucations

DIR_REVERSE = [DIR_STOP, DIR_DOWN, DIR_UP, DIR_RIGHT, DIR_LEFT, DIR_PIT]

DIR2STR = {
    DIR_UNKNOWN : "UNKNOWN",
    DIR_UP      : "UP",
    DIR_DOWN    : "DOWN",
    DIR_LEFT    : "LEFT",
    DIR_RIGHT   : "RIGHT",
    DIR_STOP    : "STOP", #just stay
    DIR_PIT     : "In PIT" #stuck in pit
}

STR2DIR = {
    "UNKNOWN"   : DIR_UNKNOWN,
    "UP"        : DIR_UP,
    "DOWN"      : DIR_DOWN,
    "LEFT"      : DIR_LEFT,
    "RIGHT"     : DIR_RIGHT,
    "STOP"      : DIR_STOP
}

DIR_ALL  = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

DIR_VERT = [DIR_UP, DIR_DOWN]

DIR_HORZ = [DIR_LEFT, DIR_RIGHT]

DIR_ROT  = [
    (DIR_STOP, DIR_STOP),
    (DIR_LEFT, DIR_RIGHT),
    (DIR_LEFT, DIR_RIGHT),
    (DIR_UP, DIR_DOWN),
    (DIR_UP, DIR_DOWN)
]

DIR2XY = [ (0,0), (0,-1),  (0,1),  (-1,0),  (1,0) ]

XY2DIR = {
    ( 0, 0) : DIR_STOP,
    ( 0,-1) : DIR_UP,
    ( 0, 1) : DIR_DOWN,
    (-1, 0) : DIR_LEFT,
    ( 1, 0) : DIR_RIGHT,
}

# DIR_UP2    = [ ( 0,-1), ( 0,-2)]
# DIR_DOWN2  = [ ( 0, 1), ( 0, 2)]
# DIR_LEFT2  = [ (-1, 0), (-2,0) ]
# DIR_RIGHT2 = [ ( 1, 0), ( 2,0) ]

def sign(d):
    if d<0:
        return -1
    if d>0:
        return 1
    return 0

def dxy2dir(dx,dy):
    dx=sign(dx)
    dy=sign(dy)
    return XY2DIR[ (dx,dy) ]

def dircmp_are_same(a, b):
    return a==b

def dircmp_are_opposite(a, b):
    if a==b:
         return False
    if  (a in DIR_VERT and b in DIR_VERT) or (a in DIR_HORZ and b in DIR_HORZ):
        return True
    return False


if __name__ == '__main__':
    raise RuntimeError("This module is not designed to be ran from CLI")
