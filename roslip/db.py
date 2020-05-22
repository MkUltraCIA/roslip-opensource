import os
from redis import Redis
from roslip.config import config

REDIS_URI = config["REDIS_URI"]
REDIS_PORT = config["REDIS_PORT"]
REDIS_PW = config["REDIS_PW"]


def get_db():
    return Redis(REDIS_URI,
                 REDIS_PORT,
                 password=REDIS_PW)
