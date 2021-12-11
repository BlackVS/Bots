#! /usr/bin/env python3

from game_rates import Infinite
import model_elements_input as MI
import model_elements_board as MB
import model_directions as MDIR


from model_object_player import PTYPE
from model_object_perk   import PERKTYPE
from config import CONFIG

#Elements which 100% defines ground
MAP_INPUT2BOARD_GROUND = {
    MI.EL_STONE  :   ( MB.EB_WALL,  None),
    MI.EL_BRICK  :   ( MB.EB_BRICK, None),

    MI.EL_NONE          :   ( MB.EB_SPACE, None),
    MI.EL_CLUE_GLOVE    :   ( MB.EB_SPACE, {"_COULDMASK":"BULLETS"}),
    MI.EL_CLUE_KNIFE    :   ( MB.EB_SPACE, {"_COULDMASK":"BULLETS"}),
    MI.EL_CLUE_RING     :   ( MB.EB_SPACE, {"_COULDMASK":"BULLETS"}),
    MI.EL_MASK_POTION   :   ( MB.EB_SPACE, {"_COULDMASK":"BULLETS"}),

    MI.EL_BACKWAY:   ( MB.EB_BACKWAY,  {"_COULDMASK":"BULLETS"}),

    MI.EL_LADDER                :   ( MB.EB_LADDER ,  {"_COULDMASK":"BULLETS"}),
    MI.EL_ROBBER_LADDER         :   ( MB.EB_LADDER ,  {"_COULDMASK":"BULLETS"}),
    MI.EL_HERO_LADDER           :   ( MB.EB_LADDER ,  None),
    MI.EL_HERO_MASK_LADDER      :   ( MB.EB_LADDER ,  None),
    MI.EL_OTHER_HERO_LADDER     :   ( MB.EB_LADDER ,  None),
    MI.EL_OTHER_HERO_MASK_LADDER:   ( MB.EB_LADDER ,  None),
    MI.EL_ENEMY_HERO_LADDER     :   ( MB.EB_LADDER ,  None),
    MI.EL_ENEMY_HERO_MASK_LADDER:   ( MB.EB_LADDER ,  None),

    MI.EL_PIPE                  :   ( MB.EB_PIPE   ,  {"_COULDMASK":"BULLETS"} ),
    MI.EL_ROBBER_PIPE           :   ( MB.EB_PIPE   ,  {"_COULDMASK":"BULLETS"}),
    MI.EL_ENEMY_HERO_MASK_PIPE  :   ( MB.EB_PIPE   ,  None),
    MI.EL_ENEMY_HERO_PIPE       :   ( MB.EB_PIPE   ,  None),
    MI.EL_HERO_MASK_PIPE        :   ( MB.EB_PIPE   ,  None),
    MI.EL_HERO_PIPE             :   ( MB.EB_PIPE   ,  None),
    MI.EL_OTHER_HERO_MASK_PIPE  :   ( MB.EB_PIPE   ,  None),
    MI.EL_OTHER_HERO_PIPE       :   ( MB.EB_PIPE   ,  None),

    MI.EL_OPENED_DOOR_BRONZE :   ( MB.EB_DOOR_BRONZE_OPENED,  None),
    MI.EL_CLOSED_DOOR_BRONZE :   ( MB.EB_DOOR_BRONZE_CLOSED,  None),

    MI.EL_OPENED_DOOR_GOLD   :   ( MB.EB_DOOR_GOLD_OPENED  ,  None),
    MI.EL_CLOSED_DOOR_GOLD   :   ( MB.EB_DOOR_GOLD_CLOSED  ,  None),
    
    MI.EL_OPENED_DOOR_SILVER :   ( MB.EB_DOOR_SILVER_OPENED,  None),
    MI.EL_CLOSED_DOOR_SILVER :   ( MB.EB_DOOR_SILVER_CLOSED,  None),

    MI.EL_CRACK_PIT          :   ( MB.EB_PIT_EMPTY,  {"_COULDMASK":"BULLETS"}),
    MI.EL_PIT_FILL_1         :   ( MB.EB_PIT_1,  {"_COULDMASK":"BULLETS"}),
    MI.EL_PIT_FILL_2         :   ( MB.EB_PIT_2,  {"_COULDMASK":"BULLETS"}),
    MI.EL_PIT_FILL_3         :   ( MB.EB_PIT_3,  {"_COULDMASK":"BULLETS"}),
    MI.EL_PIT_FILL_4         :   ( MB.EB_PIT_4,  {"_COULDMASK":"BULLETS"}),

    MI.EL_ENEMY_HERO_MASK_PIT:   ( MB.EB_PLAYER_IN_PIT,  None),
    MI.EL_ENEMY_HERO_PIT     :   ( MB.EB_PLAYER_IN_PIT,  None),
    MI.EL_HERO_MASK_PIT      :   ( MB.EB_PLAYER_IN_PIT,  None),
    MI.EL_HERO_PIT           :   ( MB.EB_PLAYER_IN_PIT,  None),
    MI.EL_OTHER_HERO_MASK_PIT:   ( MB.EB_PLAYER_IN_PIT,  None),
    MI.EL_OTHER_HERO_PIT     :   ( MB.EB_PLAYER_IN_PIT,  None),
    MI.EL_ROBBER_PIT         :   ( MB.EB_ZOMBIE_IN_PIT,  {"_COULDMASK":"BULLETS"}),
}


MAP_INPUT2OBJECT = {
    #ME
    MI.EL_HERO_DIE             : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":False },
    MI.EL_HERO_FALL            : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_DOWN },
    MI.EL_HERO_LADDER          : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_STOP },   
    MI.EL_HERO_LEFT            : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_LEFT },
    MI.EL_HERO_RIGHT           : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_RIGHT },
    MI.EL_HERO_PIT             : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_STOP },
    MI.EL_HERO_PIPE            : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_STOP },
    #ME with MASK
    MI.EL_HERO_MASK_DIE        : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":False },
    MI.EL_HERO_MASK_FALL       : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_DOWN },
    MI.EL_HERO_MASK_LADDER     : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_STOP },   
    MI.EL_HERO_MASK_LEFT       : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_LEFT },
    MI.EL_HERO_MASK_RIGHT      : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_RIGHT },
    MI.EL_HERO_MASK_PIT        : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_STOP },
    MI.EL_HERO_MASK_PIPE       : { "type":"TPlayer" , "object":"ME", "PTYPE":PTYPE.ME, "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_STOP },
    #OTHER
    MI.EL_OTHER_HERO_DIE             : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":False, "_COULDMASK": ["ZOMBIES"] },
    MI.EL_OTHER_HERO_FALL            : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_DOWN },
    MI.EL_OTHER_HERO_LADDER          : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_STOP },   
    MI.EL_OTHER_HERO_LEFT            : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_LEFT },
    MI.EL_OTHER_HERO_RIGHT           : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_RIGHT },
    MI.EL_OTHER_HERO_PIT             : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_STOP },
    MI.EL_OTHER_HERO_PIPE            : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":False, "ALIVE":True , "DIR": MDIR.DIR_STOP },
    #OTHER with MASK
    MI.EL_OTHER_HERO_MASK_DIE        : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":False, "_COULDMASK": ["ZOMBIES"] },
    MI.EL_OTHER_HERO_MASK_FALL       : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_DOWN },
    MI.EL_OTHER_HERO_MASK_LADDER     : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_STOP },   
    MI.EL_OTHER_HERO_MASK_LEFT       : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_LEFT },
    MI.EL_OTHER_HERO_MASK_RIGHT      : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_RIGHT },
    MI.EL_OTHER_HERO_MASK_PIT        : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_STOP },
    MI.EL_OTHER_HERO_MASK_PIPE       : { "collection":"PLAYERS", "PTYPE":PTYPE.OTHER,  "MASK":True,  "ALIVE":True , "DIR": MDIR.DIR_STOP },

    #Zombie
    MI.EL_ROBBER_FALL     : { "collection":"ZOMBIES", "PTYPE":PTYPE.ZOMBIE,  "MASK":False,  "ALIVE":True , "DIR": MDIR.DIR_DOWN,  "_COULDMASK": ["PERKS","BULLETS"]},
    MI.EL_ROBBER_LADDER   : { "collection":"ZOMBIES", "PTYPE":PTYPE.ZOMBIE,  "MASK":False,  "ALIVE":True , "DIR": MDIR.DIR_STOP,  "_COULDMASK": ["PERKS","BULLETS"]},   
    MI.EL_ROBBER_LEFT     : { "collection":"ZOMBIES", "PTYPE":PTYPE.ZOMBIE,  "MASK":False,  "ALIVE":True , "DIR": MDIR.DIR_LEFT,  "_COULDMASK": ["PERKS","BULLETS"]},
    MI.EL_ROBBER_PIPE     : { "collection":"ZOMBIES", "PTYPE":PTYPE.ZOMBIE,  "MASK":False,  "ALIVE":True , "DIR": MDIR.DIR_RIGHT, "_COULDMASK": ["PERKS","BULLETS"]},
    MI.EL_ROBBER_PIT      : { "collection":"ZOMBIES", "PTYPE":PTYPE.ZOMBIE,  "MASK":False,  "ALIVE":True , "DIR": MDIR.DIR_STOP,  "_COULDMASK": ["PERKS","BULLETS"]},
    MI.EL_ROBBER_RIGHT    : { "collection":"ZOMBIES", "PTYPE":PTYPE.ZOMBIE,  "MASK":False,  "ALIVE":True , "DIR": MDIR.DIR_STOP,  "_COULDMASK": ["PERKS","BULLETS"]},

    #PERKS
    MI.EL_CLUE_GLOVE     : { "collection":"PERKS", "PTYPE":PERKTYPE.GLOVE, "TICKS": Infinite},
    MI.EL_CLUE_KNIFE     : { "collection":"PERKS", "PTYPE":PERKTYPE.KNIFE, "TICKS": Infinite},
    MI.EL_CLUE_RING      : { "collection":"PERKS", "PTYPE":PERKTYPE.RING , "TICKS": Infinite},
    MI.EL_MASK_POTION    : { "collection":"PERKS", "PTYPE":PERKTYPE.MASK , "TICKS": Infinite},

    #BULLETS
    MI.EL_BULLET         : { "collection":"BULLETS", "DIR": MDIR.DIR_UNKNOWN, "_COULDMASK": ["BULLETS"]},

}
