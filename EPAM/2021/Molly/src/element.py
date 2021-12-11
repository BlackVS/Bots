#! /usr/bin/env python3

###
# #%L
# Codenjoy - it's a dojo-like platform from developers to developers.
# %%
# Copyright (C) 2018 Codenjoy
# %%
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
# #L%
###

from argparse import ArgumentError

EL_BOMBERMAN = b'\xe2\x98\xba'.decode()         # encoded '☺' char
EL_BOMB_BOMBERMAN = b'\xe2\x98\xbb'.decode()    # encoded '☻' char
EL_DEAD_BOMBERMAN = b'\xd1\xa0'.decode()        # encoded 'Ѡ' char
# The Enemies
EL_OTHER_BOMBERMAN = b'\xe2\x99\xa5'.decode()       # encoded '♥' char
EL_OTHER_BOMB_BOMBERMAN = b'\xe2\x99\xa0'.decode()  # encoded '♠' char
EL_OTHER_DEAD_BOMBERMAN = b'\xe2\x99\xa3'.decode()  # encoded '♣' char

EL_ENEMY_HERO       =b'\xc3\xb6'.decode()       # encoded'ö',
EL_ENEMY_POTION_HERO=b'\xc3\x96'.decode()       # encoded'Ö',
EL_ENEMY_DEAD_HERO  =b'\xc3\xb8'.decode()       # encoded'ø'

# The Bombs
EL_BOMB_TIMER_5 = '5'
EL_BOMB_TIMER_4 = '4'
EL_BOMB_TIMER_3 = '3'
EL_BOMB_TIMER_2 = '2'
EL_BOMB_TIMER_1 = '1'


EL_BOMB_BLAST_5 = 'E'
EL_BOMB_BLAST_4 = 'D'
EL_BOMB_BLAST_3 = 'C'
EL_BOMB_BLAST_2 = 'B'
EL_BOMB_BLAST_1 = 'A'


EL_RISK_1 = 'a'
EL_RISK_2 = 'b'
EL_RISK_3 = 'c'
EL_RISK_4 = 'd'
EL_RISK_5 = 'e'


EL_BOOM = b'\xd2\x89'.decode()  # encoded '҉character
# Walls
EL_WALL = b'\xe2\x98\xbc'.decode() # encoded '☼' char
EL_DESTROY_WALL = '#'
EL_DESTROYED_WALL = 'H'
# Meatchoopers
EL_MEAT_CHOPPER = '&'
EL_DEAD_MEAT_CHOPPER = 'x'
#Perks
EL_BOMB_BLAST_RADIUS_INCREASE = '+'
EL_BOMB_COUNT_INCREASE = 'c'
EL_BOMB_IMMUNE = 'i'
EL_BOMB_REMOTE_CONTROL = 'r'

#new
# Hero can shoot by poison cloud. Using: ACT(1)+Direction.
# Temporary.
EL_POISON_THROWER='T'

# Hero can explode all potions on the field. Using: ACT(2).
# Temporary.
EL_POTION_EXPLODER='A'


# Space
EL_NONE = ' '

ELS_DANGERS = [
    EL_OTHER_BOMBERMAN,
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1,
#    EL_BOOM,
    EL_MEAT_CHOPPER,
    EL_DEAD_MEAT_CHOPPER #BUG????
]

EL_RISKS = [
    EL_RISK_1,
    EL_RISK_2,
    EL_RISK_3,
    EL_RISK_4,
    EL_RISK_5
]

ELS_CHOPPERS = [
    EL_MEAT_CHOPPER,
    EL_DEAD_MEAT_CHOPPER #BUG????
]

#not danger to move through
ELS_NOT_DANGER2MOVE = [  
                    EL_BOMB_BLAST_RADIUS_INCREASE, 
                    EL_BOMB_COUNT_INCREASE,
                    EL_BOMB_IMMUNE,
                    EL_BOMB_REMOTE_CONTROL,
                    EL_BOOM,
                    EL_POISON_THROWER,
                    EL_POTION_EXPLODER,

                    #EL_DEAD_MEAT_CHOPPER, Bug?????
                    EL_DESTROYED_WALL,
                    EL_DEAD_BOMBERMAN,
                    EL_OTHER_DEAD_BOMBERMAN,
                    #EL_BOMBERMAN,
                    EL_OTHER_BOMBERMAN,
                    EL_NONE ]

ELS_CHOPPER_NO_MOVE = [
    EL_WALL,
    EL_DESTROY_WALL,
]

ELS_NO_MOVE = [
    EL_WALL,
    EL_DESTROY_WALL,
    EL_OTHER_BOMBERMAN,
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1   
]

ELS_NO_MOVE_EXCEPT_DWALL = [
    EL_WALL,
    EL_OTHER_BOMBERMAN,
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1   
]

ELS_NO_MOVE_EXCEPT_ME = [
    EL_WALL,
    EL_DESTROY_WALL,
    EL_OTHER_BOMBERMAN,
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1   
]

ELS_BLOCKED = [
    EL_WALL,
    EL_DESTROY_WALL,
    EL_OTHER_BOMBERMAN,
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMBERMAN,
    EL_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1   
]

ELS_BOMBS = [
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1   
]

ELS_BLAST_BLOCKINGS = [
    EL_WALL,
    EL_DESTROY_WALL,
    EL_OTHER_BOMB_BOMBERMAN,
    EL_BOMB_BOMBERMAN,
    EL_BOMB_TIMER_5,
    EL_BOMB_TIMER_4,
    EL_BOMB_TIMER_3,
    EL_BOMB_TIMER_2,
    EL_BOMB_TIMER_1   
]

ELS_PERKS = [
    EL_BOMB_BLAST_RADIUS_INCREASE,
    EL_BOMB_COUNT_INCREASE,
    EL_BOMB_IMMUNE,
    EL_BOMB_REMOTE_CONTROL,
    EL_POISON_THROWER,
    EL_POTION_EXPLODER,

]

ELS_BLASTS = [EL_BOMB_BLAST_5 , EL_BOMB_BLAST_4, EL_BOMB_BLAST_3, EL_BOMB_BLAST_2, EL_BOMB_BLAST_1]

_ELEMENTS = dict(
    # The Bomberman
    BOMBERMAN = b'\xe2\x98\xba'.decode(),  # encoded '☺' char
    BOMB_BOMBERMAN = b'\xe2\x98\xbb'.decode(),  # encoded '☻' char
    DEAD_BOMBERMAN = b'\xd1\xa0'.decode(),  # encoded 'Ѡ' char
    # The Enemies
    OTHER_BOMBERMAN = b'\xe2\x99\xa5'.decode(),  # encoded '♥' char
    OTHER_BOMB_BOMBERMAN = b'\xe2\x99\xa0'.decode(),  # encoded '♠' char
    OTHER_DEAD_BOMBERMAN = b'\xe2\x99\xa3'.decode(),  # encoded '♣' char
    # The Bombs
    BOMB_TIMER_5 = '5',
    BOMB_TIMER_4 = '4',
    BOMB_TIMER_3 = '3',
    BOMB_TIMER_2 = '2',
    BOMB_TIMER_1 = '1',
    BOOM = b'\xd2\x89'.decode(),  # encoded '҉character
    # Walls
    WALL = b'\xe2\x98\xbc'.decode(), # encoded '☼' char
    DESTROY_WALL = '#',
    DESTROYED_WALL = 'H',
    # Meatchoopers
    MEAT_CHOPPER = '&',
    DEAD_MEAT_CHOPPER = 'x',
    #Perks
    BOMB_BLAST_RADIUS_INCREASE = '+',
    BOMB_COUNT_INCREASE = 'c',
    BOMB_IMMUNE = 'i',
    BOMB_REMOTE_CONTROL = 'r',
    # Space
    NONE = ' ',
    #new
    EL_POISON_THROWER='T',
    EL_POTION_EXPLODER='A'
)

def value_of(char):
    """ Test whether the char is valid Element and return it's name."""
    for value, c in _ELEMENTS.items():
        if char == c:
            return value
    else:
        raise ArgumentError("No such Element: {}".format(char))


class Element:
    """ Class describes the Element objects for Bomberman game."""
    def __init__(self, n_or_c):
        """ Construct an Element object from given name or char."""
        for n, c in _ELEMENTS.items():
            if n_or_c == n or n_or_c == c:
                self._name = n
                self._char = c
                break
        else:
            raise ArgumentError("No such Element: {}".format(n_or_c))
            
    def get_char(self):
        """ Return the Element's character."""
        return self._char
    
    def __eq__(self, otherElement):
        return (self._name == otherElement._name and
                self._char == otherElement._char)


if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
