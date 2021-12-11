#!/usr/bin/env python3


from sys import version_info
from webclient import WebClient
from solver import * 
from urllib.parse import urlparse, parse_qs
from config import *
from logger import *

if QT_BOARD_SHOW:
    from boardQt import *


def get_url_for_ws(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)

    return "{}://{}/codenjoy-contest/ws?user={}&code={}".format('ws' if parsed_url.scheme == 'http' else 'wss',
                                                                parsed_url.netloc,
                                                                parsed_url.path.split('/')[-1],
                                                                query['code'][0])


def main():
    assert version_info[0] == 3, "You should run me with Python 3.x"

    config_init()
    qt_game = None

    if QT_BOARD_SHOW:
        qt_create_board()
        qt_game = Window()
        qt_game.play()

    url = REMOTE_URL
    direction_solver = DirectionSolver(qt_game)

    if not config.REPLAY_PLAY_ON:
        wcl = WebClient(url=get_url_for_ws(url), solver=direction_solver)
        wcl.run_forever()
    else:
        direction_solver.replay()
        qt_game=None
        exit()

if __name__ == '__main__':
    main()
