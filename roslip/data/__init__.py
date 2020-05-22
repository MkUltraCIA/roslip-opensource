import sys
from pathlib import Path
import random

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import os
import time
import random
import multiprocessing
import grequests
from redis import Redis

from roslip.data.tile import get_tile_redis
from roslip.db import get_db

# database
db = get_db()


def main():
    import requests

    checkproxies = [None]

    # "104.248.63.17:30588"

    print("checking proxy list")
    if True:
        data = ["104.248.63.17:30588"]
        print("found {} proxies".format(len(data)))

        for p in data:
            if not p:
                continue

            uri = "socks5://{}".format(p).replace("\n", "")
            print(uri)
            checkproxies.append({
                "http": uri,
                # "https": uri
            })
        print(checkproxies)

    print("testing proxies")

    def exception_handler(request, exception):
        print(exception)

    reqs = [grequests.get("http://www.openstreetmap.org/",
                          proxies=proxy) for proxy in checkproxies]

    i = 0
    failed = []
    for resp in grequests.map(reqs, exception_handler=exception_handler):
        succ = resp is not None and resp.ok

        if resp and not resp.ok:
            print(resp.text)

        proxy = checkproxies[i]

        if not succ:
            print("-", proxy.get("http") if proxy else "localhost")
            failed.append(i)
        else:
            print("+", proxy.get("http") if proxy else "localhost")

        i += 1

    proxies = []
    for i in range(len(checkproxies)):
        if i not in failed:
            proxies.append(checkproxies[i])

    print("data processer online")

    i = 0
    while True:
        if db.llen("requests") > 0:
            cf = db.lpop("requests")
            if cf is None:
                continue
            cf = cf.decode("utf-8").split("|")
            coords, flags = (cf[0], cf[1]) if len(cf) > 1 else (cf[0], None)

            tx, ty = map(int, coords.split(","))
            flags = map(str.lower, flags.split(",")) if flags else []

            t_key = "tiles:{},{}".format(tx, ty)
            if db.get(t_key):
                db.expire(t_key, None if "p" in flags else 40)
                continue

            print(tx, ty)

            p = multiprocessing.Process(target=get_tile_redis, args=(tx, ty, "p" in flags),
                                        kwargs={"proxy": random.choice(proxies) if len(checkproxies) > 0 else None})
            p.start()

        time.sleep(0.1)

        i += 1


if __name__ == "__main__":
    # multiprocessing.freeze_support()

    main()
