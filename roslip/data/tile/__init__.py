import json
import os

from roslip.data.tile import ways, buildings, api
from roslip.util import *
from redis import Redis
from pathlib import Path
from multiprocessing import Process
from diskcache import FanoutCache as Cache
from roslip.db import get_db

CACHE_EXPIRE = 30 * 24 * 60 * 60  # 1 month


def get_tile_redis(x, y, permanent, proxy=None):
    db = get_db()

    square = [tile_to_coord(x, y), tile_to_coord(x + 1, y), tile_to_coord(x + 1, y + 1), tile_to_coord(x, y + 1)]

    db.set("test", 1)

    kname = "tiles:{},{}".format(x, y)

    with Cache(str(Path.home() / "roslipcache")) as cache:
        # first check cache

        # to_write = ""

        if kname in cache:
            print("exists in cache")

            to_write = cache.get(kname)
            cache.touch(kname, expire=CACHE_EXPIRE)

            obj = None
        else:

            road_data, buildings_data = api.get_data(x, y, proxy=proxy)

            bldgs = buildings.Buildings(buildings_data).dict()
            rds = ways.Tile.from_json(road_data, 15, x, y)
            rds = rds.dict() if rds else {}

            obj = {
                "buildings": bldgs,
                "ways": rds
            }

            to_write = json.dumps(obj, separators=(',', ':'))

            cache.set(kname, to_write, expire=CACHE_EXPIRE)

        db.set(kname, to_write, ex=None if permanent else 40)

    db.close()

    return obj

# test = get_tile_redis(*atl)
# pyperclip.copy(txt)
