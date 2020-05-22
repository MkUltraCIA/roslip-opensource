import redis
import os
from flask import Flask, make_response, jsonify
from pathlib import Path
from redis import Redis
import time
import json

# database
db = Redis(os.environ["REDIS_URI"],
           os.environ["REDIS_PORT"],
           password=os.environ["REDIS_PW"])

# app
app = Flask(__name__)


@app.route("/")
def index():
    return "server live"


TIMEOUT = 10
QUERY = 0.1


# returns tile data
# checks for existing data in redis, creates request key if not already there
@app.route("/<int:x>/<int:y>")
def tile(x, y):
    t_key = "tiles:{},{}".format(x, y)
    data = db.get(t_key)
    if data is None:
        db.rpush("requests", "{},{}".format(x, y))

        s = 0
        while data is None:
            data = db.get(t_key)

            time.sleep(QUERY)
            s += QUERY
            if s >= TIMEOUT:
                return "timeout", 408

    r = make_response(data)
    r.headers["Content-Type"] = "application/json"

    return r


@app.route("/preload/<int:x>/<int:y>/<int:r>")
def preload(x, y, r):
    for tx in range(x - r, x + r + 1):
        for ty in range(y - r, y + r + 1):
            db.rpush("requests", "{},{}*".format(tx, ty))

    return jsonify({"x": x, "y": y})


@app.route("/<int:x0>/<int:y0>/<int:x1>/<int:y1>")
def tiles(x0, y0, x1, y1):
    return "hi"
