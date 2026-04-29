import math
import osmnx as ox
from models import MapNode, MapEdge

class MapProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.graph = None

    def load_graph(self):
        self.graph = ox.graph_from_xml(self.file_path)
        return self.graph

    def extract_nodes(self):
        nodes_dict = {}
        for node_id, data in self.graph.nodes(data=True):
            nodes_dict[node_id] = MapNode(node_id, data['y'], data['x'])
        return nodes_dict

    def extract_edges(self):
        edges_list = []
        for u, v, data in self.graph.edges(data=True):
            geometry = None
            if data.get('geometry') is not None:
                geometry = [(pt.y, pt.x) for pt in data['geometry'].coords]

            edge = MapEdge(
                u=u,
                v=v,
                length=data.get('length', 0),
                oneway=data.get('oneway', False),
                geometry=geometry
            )
            edges_list.append(edge)
        return edges_list

    def get_node(self, node_id):
        data = self.graph.nodes.get(node_id)
        if data is None:
            return None
        return MapNode(node_id, data['y'], data['x'])

    def find_closest_node(self, lat, lon):
        best_id = None
        best_dist = float('inf')
        for node_id, data in self.graph.nodes(data=True):
            d = self._haversine_distance(lat, lon, data['y'], data['x'])
            if d < best_dist:
                best_dist = d
                best_id = node_id
        return best_id, best_dist

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c