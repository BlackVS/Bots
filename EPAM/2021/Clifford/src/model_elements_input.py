#!/usr/bin/env python3

import colors as COLOR
### ELEMENTS on BOARD (Input)

# Empty space - where the hero can move.
EL_NONE=' '

# A wall where you can shoot a hole.
EL_BRICK='#'

# The wall is restored over time. When the process begins we
# see a timer.
EL_PIT_FILL_1='1'

# The wall is restored over time. When the process begins we
# see a timer.
EL_PIT_FILL_2='2'

# The wall is restored over time. When the process begins we
# see a timer.
EL_PIT_FILL_3='3'

# The wall is restored over time. When the process begins we
# see a timer.
EL_PIT_FILL_4='4'

# Indestructible wall - It cannot be destroyed with a shot.
EL_STONE='☼'

# At the moment of the shot we see the wall like this.
EL_CRACK_PIT='*'

# Clue knife. Collect a series of clues to get the maximum
# points.
EL_CLUE_KNIFE='$'

# Clue glove. Collect a series of clues to get the maximum
# points.

EL_CLUE_GLOVE='&'

# Clue ring. Collect a series of clues to get the maximum
# points.
EL_CLUE_RING='@'

# Your hero is dead. In the next tick it will disappear and
# appear in a new location.
EL_HERO_DIE='O'

# Your hero is climbing the ladder.
EL_HERO_LADDER='A'

# Your hero runs to the left.
EL_HERO_LEFT='◄'

# Your hero runs to the right.
EL_HERO_RIGHT='►'

# Your hero is falling.
EL_HERO_FALL='U' #b'\xEF\xBB\xBF\x55'.decode()

# Your hero is crawling along the pipe.
EL_HERO_PIPE='I'

# Your hero in the pit.
EL_HERO_PIT='E'

# Your shadow-hero is dead. In the next tick it will
# disappear and appear in a new location.
EL_HERO_MASK_DIE='o'

# Your shadow-hero is climbing the ladder.
EL_HERO_MASK_LADDER='a'

# Your shadow-hero runs to the left.
EL_HERO_MASK_LEFT='h'

# Your shadow-hero runs to the right.
EL_HERO_MASK_RIGHT='w'

# Your shadow-hero is falling.
EL_HERO_MASK_FALL='u'

# Your shadow-hero is crawling along the pipe.
EL_HERO_MASK_PIPE='i'

# Your shadow-hero in the pit.
EL_HERO_MASK_PIT='e'

# Other hero is dead. In the next tick it will disappear and
# appear in a new location.
EL_OTHER_HERO_DIE='C'

# Other hero is climbing the ladder.
EL_OTHER_HERO_LADDER='D'

# Other hero runs to the left.
EL_OTHER_HERO_LEFT='«'

# Other hero runs to the right.
EL_OTHER_HERO_RIGHT='»'

# Other hero is falling.
EL_OTHER_HERO_FALL='F'

# Other hero is crawling along the pipe.
EL_OTHER_HERO_PIPE='J'

# Other hero in the pit.
EL_OTHER_HERO_PIT='K'

# Other shadow-hero is dead. In the next tick it will
# disappear and appear in a new location.
EL_OTHER_HERO_MASK_DIE='c'

# Other shadow-hero is climbing the ladder.
EL_OTHER_HERO_MASK_LADDER='d'

# Other shadow-hero runs to the left.
EL_OTHER_HERO_MASK_LEFT='Z'

# Other shadow-hero runs to the right.
EL_OTHER_HERO_MASK_RIGHT='z'

# Other shadow-hero is falling.
EL_OTHER_HERO_MASK_FALL='f'

# Other shadow-hero is crawling along the pipe.
EL_OTHER_HERO_MASK_PIPE='j'

# Other shadow-hero in the pit.
EL_OTHER_HERO_MASK_PIT='k'

# Enemy hero is dead. In the next tick it will disappear and
# appear in a new location.
EL_ENEMY_HERO_DIE='L'

# Enemy hero is climbing the ladder.
EL_ENEMY_HERO_LADDER='N'

# Enemy hero runs to the left.
EL_ENEMY_HERO_LEFT='P'

# Enemy hero runs to the right.
EL_ENEMY_HERO_RIGHT='Q'

# Enemy hero is falling.
EL_ENEMY_HERO_FALL='R'

# Enemy hero is crawling along the pipe.
EL_ENEMY_HERO_PIPE='T'

# Enemy hero in the pit.
EL_ENEMY_HERO_PIT='V'

# Enemy shadow-hero is dead. In the next tick it will
# disappear and appear in a new location.
EL_ENEMY_HERO_MASK_DIE='l'

# Enemy shadow-hero is climbing the ladder.
EL_ENEMY_HERO_MASK_LADDER='n'

# Enemy shadow-hero runs to the left.
EL_ENEMY_HERO_MASK_LEFT='p'

# Enemy shadow-hero runs to the right.
EL_ENEMY_HERO_MASK_RIGHT='q'

# Enemy shadow-hero is falling.
EL_ENEMY_HERO_MASK_FALL='r'

# Enemy shadow-hero is crawling along the pipe.
EL_ENEMY_HERO_MASK_PIPE='t'

# Enemy shadow-hero in the pit.
EL_ENEMY_HERO_MASK_PIT='v'

# Robber is climbing the ladder.
EL_ROBBER_LADDER='X'

# Robber runs to the left. Robber picks up the nearest prey
# and hunts for it until it overtakes it.
EL_ROBBER_LEFT=')'

# Robber runs to the right. Robber picks up the nearest prey
# and hunts for it until it overtakes it.
EL_ROBBER_RIGHT='('

# Robber is falling.
EL_ROBBER_FALL='x'

# Robber is crawling along the pipe.
EL_ROBBER_PIPE='Y'

# Robber in the pit.
EL_ROBBER_PIT='y'

# Opened golden gates. Can only be locked with a golden key.
EL_OPENED_DOOR_GOLD='g'

# Opened silver gates. Can only be locked with a silver key.
EL_OPENED_DOOR_SILVER='s'

# Opened bronze gates. Can only be locked with a bronze key.
EL_OPENED_DOOR_BRONZE='b'

# Closed golden gates. Can only be opened with a golden key.
EL_CLOSED_DOOR_GOLD='G'

# Closed silver gates. Can only be opened with a silver key.
EL_CLOSED_DOOR_SILVER='S'

# Closed bronze gates. Can only be opened with a bronze key.
EL_CLOSED_DOOR_BRONZE='B'

# Golden key. Helps open/close golden gates. The key can only
# be used once.
EL_KEY_GOLD='+'

# Silver key. Helps open/close silver gates. The key can only
# be used once.
EL_KEY_SILVER='-'

# Bronze key. Helps open/close bronze gates. The key can only
# be used once.
EL_KEY_BRONZE='!'

# Bullet. After the shot by the hero the bullet flies until
# it meets an obstacle. The bullet kills the hero. It
# ricochets from the indestructible wall (no more than 1
# time). The bullet destroys the destructible wall.
EL_BULLET='•'

# Ladder - the hero can move along the level along it.
EL_LADDER='H'

# Pipe - the hero can also move along the level along it but
# only horizontally.
EL_PIPE='~'

# Back door - allows the hero to secretly move to another
# random place on the map.
EL_BACKWAY='W'

# Disguise potion - endow the hero with additional abilities.
# The hero goes into shadow mode.
EL_MASK_POTION='m'




## Sprites
SPRITES_COLORS = {
    EL_STONE  :  COLOR.DARK_GREY, 
    EL_BRICK  :  COLOR.BROWN,
    EL_NONE   :  COLOR.BLACK,
}


SPRITES = {
    #input board
    EL_BACKWAY              :    './sprites/input/backway.png',
    EL_BRICK                :    './sprites/input/brick.png',
    EL_BULLET               :    './sprites/input/bullet.png',
    EL_CLOSED_DOOR_BRONZE   :    './sprites/input/closed_door_bronze.png',
    EL_CLOSED_DOOR_GOLD     :    './sprites/input/closed_door_gold.png',
    EL_CLOSED_DOOR_SILVER   :    './sprites/input/closed_door_silver.png',
    EL_CLUE_GLOVE           :    './sprites/input/clue_glove.png',
    EL_CLUE_KNIFE           :    './sprites/input/clue_knife.png',
    EL_CLUE_RING            :    './sprites/input/clue_ring.png',
    EL_CRACK_PIT            :    './sprites/input/crack_pit.png',
    
    
    EL_ENEMY_HERO_DIE       :    './sprites/input/enemy_hero_die.png',
    EL_ENEMY_HERO_FALL      :    './sprites/input/enemy_hero_fall.png',
    EL_ENEMY_HERO_LADDER    :    './sprites/input/enemy_hero_ladder.png',
    EL_ENEMY_HERO_LEFT      :    './sprites/input/enemy_hero_left.png',
    EL_ENEMY_HERO_MASK_DIE  :    './sprites/input/enemy_hero_mask_die.png',
    EL_ENEMY_HERO_MASK_FALL :    './sprites/input/enemy_hero_mask_fall.png',
    EL_ENEMY_HERO_MASK_LADDER:   './sprites/input/enemy_hero_mask_ladder.png',
    EL_ENEMY_HERO_MASK_LEFT :    './sprites/input/enemy_hero_mask_left.png',
    EL_ENEMY_HERO_MASK_PIPE :    './sprites/input/enemy_hero_mask_pipe.png',
    EL_ENEMY_HERO_MASK_PIT  :    './sprites/input/enemy_hero_mask_pit.png',
    EL_ENEMY_HERO_MASK_RIGHT:    './sprites/input/enemy_hero_mask_right.png',
    EL_ENEMY_HERO_PIPE      :    './sprites/input/enemy_hero_pipe.png',
    EL_ENEMY_HERO_PIT       :    './sprites/input/enemy_hero_pit.png',
    EL_ENEMY_HERO_RIGHT     :    './sprites/input/enemy_hero_right.png',
    
    EL_HERO_DIE             :    './sprites/input/hero_die.png',
    EL_HERO_FALL            :    './sprites/input/hero_fall.png',
    EL_HERO_LADDER          :    './sprites/input/hero_ladder.png',
    EL_HERO_LEFT            :    './sprites/input/hero_left.png',
    EL_HERO_MASK_DIE        :    './sprites/input/hero_mask_die.png',
    EL_HERO_MASK_FALL       :    './sprites/input/hero_mask_fall.png',
    EL_HERO_MASK_LADDER     :    './sprites/input/hero_mask_ladder.png',
    EL_HERO_MASK_LEFT       :    './sprites/input/hero_mask_left.png',
    EL_HERO_MASK_PIPE       :    './sprites/input/hero_mask_pipe.png',
    EL_HERO_MASK_PIT        :    './sprites/input/hero_mask_pit.png',
    EL_HERO_MASK_RIGHT      :    './sprites/input/hero_mask_right.png',
    EL_HERO_PIPE            :    './sprites/input/hero_pipe.png',
    EL_HERO_PIT             :    './sprites/input/hero_pit.png',
    EL_HERO_RIGHT           :    './sprites/input/hero_right.png',

    EL_OTHER_HERO_DIE       :    './sprites/input/other_hero_die.png',
    EL_OTHER_HERO_FALL      :    './sprites/input/other_hero_fall.png',
    EL_OTHER_HERO_LADDER    :    './sprites/input/other_hero_ladder.png',
    EL_OTHER_HERO_LEFT      :    './sprites/input/other_hero_left.png',
    EL_OTHER_HERO_MASK_DIE  :    './sprites/input/other_hero_mask_die.png',
    EL_OTHER_HERO_MASK_FALL :    './sprites/input/other_hero_mask_fall.png',
    EL_OTHER_HERO_MASK_LADDER:   './sprites/input/other_hero_mask_ladder.png',
    EL_OTHER_HERO_MASK_LEFT :    './sprites/input/other_hero_mask_left.png',
    EL_OTHER_HERO_MASK_PIPE :    './sprites/input/other_hero_mask_pipe.png',
    EL_OTHER_HERO_MASK_PIT  :    './sprites/input/other_hero_mask_pit.png',
    EL_OTHER_HERO_MASK_RIGHT:    './sprites/input/other_hero_mask_right.png',
    EL_OTHER_HERO_PIPE      :    './sprites/input/other_hero_pipe.png',
    EL_OTHER_HERO_PIT       :    './sprites/input/other_hero_pit.png',
    EL_OTHER_HERO_RIGHT     :    './sprites/input/other_hero_right.png',

    EL_KEY_BRONZE           :    './sprites/input/key_bronze.png',
    EL_KEY_GOLD             :    './sprites/input/key_gold.png',
    EL_KEY_SILVER           :    './sprites/input/key_silver.png',
    EL_LADDER               :    './sprites/input/ladder.png',
    EL_MASK_POTION          :    './sprites/input/mask_potion.png',
    EL_NONE                 :    './sprites/input/none.png',

    EL_OPENED_DOOR_BRONZE   :    './sprites/input/opened_door_bronze.png',
    EL_OPENED_DOOR_GOLD     :    './sprites/input/opened_door_gold.png',
    EL_OPENED_DOOR_SILVER   :    './sprites/input/opened_door_silver.png',
    
    
    EL_PIPE         :    './sprites/input/pipe.png',
    EL_PIT_FILL_1   :    './sprites/input/pit_fill_1.png',
    EL_PIT_FILL_2   :    './sprites/input/pit_fill_2.png',
    EL_PIT_FILL_3   :    './sprites/input/pit_fill_3.png',
    EL_PIT_FILL_4   :    './sprites/input/pit_fill_4.png',
    EL_ROBBER_FALL  :    './sprites/input/robber_fall.png',
    EL_ROBBER_LADDER:    './sprites/input/robber_ladder.png',
    EL_ROBBER_LEFT  :    './sprites/input/robber_left.png',
    EL_ROBBER_PIPE  :    './sprites/input/robber_pipe.png',
    EL_ROBBER_PIT   :    './sprites/input/robber_pit.png',
    EL_ROBBER_RIGHT :    './sprites/input/robber_right.png',
    EL_STONE        :    './sprites/input/stone.png'
}


if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
