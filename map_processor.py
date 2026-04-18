import osmnx as ox
import networkx as nx
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
            edge = MapEdge(
                u=u, 
                v=v, 
                length=data.get('length', 0),
                oneway=data.get('oneway', False)
            )
            edges_list.append(edge)
        return edges_list