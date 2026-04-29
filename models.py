class MapNode:
    def __init__(self, node_id, lat, lon):
        self.id = node_id
        self.lat = lat
        self.lon = lon

class MapEdge:
    def __init__(self, u, v, length, oneway=False, geometry=None):
        self.u = u  # ID node bắt đầu
        self.v = v  # ID node kết thúc
        self.length = length
        self.oneway = oneway
        self.geometry = geometry