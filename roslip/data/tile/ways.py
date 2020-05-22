from roslip.util import *
from shapely.geometry import Polygon


def t2c(z, x, y):
    n = 2 ** z
    lon_deg = x / n * 360 - 180
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


class Road(object):
    def __init__(self, type_, pts):
        self.type_ = type_
        self.pts = pts

    @classmethod
    def from_obj(cls, obj):
        if obj["properties"]["kind"] in ["ferry"]:
            return []

        geometry = obj["geometry"]

        type_ = obj["properties"].get("kind_detail", None)
        if geometry["type"] == "LineString":
            return [cls(type_, geometry["coordinates"])]
        else:
            return [cls(type_, coords) for coords in geometry["coordinates"]]

    def dict(self):
        ret = {
            "pts": self.pts,
            "type": self.type_
        }

        return ret


class Tile(object):
    def __init__(self, z, x, y):
        self.z = z
        self.x = x
        self.y = y

        self.lat0, self.lon0 = tile_to_coord(x, y)
        self.lat1, self.lon1 = tile_to_coord(x + 1, y + 1)

        self.nodes = {}
        self.ways = {
            "roads": [],
            "natural": [],
            "earth": []
        }

    @classmethod
    def from_json(cls, obj, z, x, y):
        tile = cls(z, x, y)

        if "roads" in obj:
            for road in obj["roads"].get("features", []):
                tile.ways["roads"] += Road.from_obj(road)

        water_polys = []
        if "water" in obj:
            for water in obj["water"]["features"]:
                geometry = water["geometry"]
                if geometry["type"] == "Polygon":
                    coords = []
                    for c in geometry["coordinates"][0]:
                        coords.append((c[1], c[0]))
                    water_polys.append(Polygon(coords))
                elif geometry["type"] in ("MultiPolygon",):
                    for uclist in geometry["coordinates"]:
                        for clist in uclist:
                            coords = [(c[1], c[0]) for c in clist]
                            water_polys.append(Polygon(coords))

        if "earth" in obj:
            for earth in obj["earth"]["features"]:
                geometry = earth["geometry"]
                if geometry["type"] == "Polygon":
                    poly = Polygon([(c[1], c[0]) for c in geometry["coordinates"][0]])
                    for water in water_polys:
                        poly = poly.difference(water)

                    polys = poly.geoms if poly.geom_type == "MultiPolygon" else [poly]
                    for p in polys:
                        tile.ways["earth"].append(list(p.exterior.coords))
                elif geometry["type"] == "MultiPolygon":
                    for uclist in geometry["coordinates"]:
                        for clist in uclist:
                            poly = Polygon([(c[1], c[0]) for c in clist])
                            for water in water_polys:
                                poly = poly.difference(water)

                            polys = poly.geoms if poly.geom_type in ("MultiPolygon", "GeometryCollection") else [poly]
                            for p in polys:
                                tile.ways["earth"].append(list(p.exterior.coords))

        return tile

    @property
    def bounds(self):
        return t2c(self.z, self.x, self.y) + t2c(self.z, self.x + 1, self.y + 1)

    def dict(self):
        r = {
            "roads": [v.dict() for v in self.ways["roads"]],
            "earth": self.ways["earth"]
        }

        return r
