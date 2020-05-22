class Building(object):
    def __init__(self, data):
        self._data = data
        self.id = data["id"]

        properties = data.get("properties", {})
        self.levels = properties.get("levels", 1)
        self.height = properties.get("height", 4.25 * self.levels)

        self.geometry = data["geometry"].get("coordinates", [[]])

    def dict(self):
        return {
            "id": self.id,
            # "levels": self.levels,
            "ht": self.height,
            "pts": self.geometry
        }


class Buildings(object):
    def __init__(self, bldgs):
        self.buildings = [Building(bldg) for bldg in bldgs]

    def add_building(self, data):
        self.buildings.append(Building(data))

    def dict(self):
        return [bldg.dict() for bldg in self.buildings]
