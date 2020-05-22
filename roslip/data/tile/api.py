import grequests
from roslip.util import *
from roslip.config import config
import time
import math

# constants
ROAD_URL = "http://tile.nextzen.org/tilezen/vector/v1/512/all/15/{}/{}.json?api_key=" + config["NEXTZEN"]
BLDG_URL = "http://data.osmbuildings.org/0.2/osm/tile/15/{}/{}.json"

ELEV_URL = "http://api.opentopodata.org/v1/srtm30m"


def roads_req(x, y, proxy=None):
    return grequests.get(ROAD_URL.format(x, y), proxies=proxy)


def buildings_req(x, y, proxy=None):
    return grequests.get(BLDG_URL.format(x, y), proxies=proxy)


def elev_req(x, y, proxy=None):
    pts = [tile_to_coord(x + 0.5, y + 0.5)]

    loc = "|".join(["{},{}".format(round(p[0], 6), round(p[1], 6)) for p in pts])

    return grequests.get(ELEV_URL, params={"locations": loc}, proxies=proxy)


RETRY = 5


def get_data(x, y, retry=False, proxy=None):
    def exception_hdl(req, exc):
        print(exc)

    rs = (roads_req(x, y, proxy=proxy), buildings_req(x, y, proxy=proxy))
    resp = grequests.map(rs, exception_handler=exception_hdl)

    if resp[0] is None or resp[1] is None:
        print(resp[0])
        return {}, []

    for r in resp:
        if not r.status_code == 200:
            print(r.status_code, r.text)

    codes = [r.status_code for r in resp]
    if 509 in codes or 429 in codes:
        raise Exception("Ratelimit")

        # if not retry:
        #     time.sleep(RETRY)
        #     return get_data(x, y, True)

    # roads, buildings, elevation
    return resp[0].json(), resp[1].json()["features"] if resp[1] and resp[1].status_code == 200 else []
