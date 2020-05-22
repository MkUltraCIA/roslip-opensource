import math


def coord_to_tile(lat, long, z=15):
    lat_rad = math.radians(lat)
    n = 2 ** z
    x = int((long + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(lat_rad)) / math.pi) / 2 * n)

    return x, y


def tile_to_coord(x, y, z=15):
    n = 2 ** z
    lon_deg = x / n * 360 - 180
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)

    return lat_deg, lon_deg


def t2c(z, x, y):
    n = 2 ** z
    lon_deg = x / n * 360 - 180
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg
