import math
from heapq import heappush, heappop

class RouteFinder:
    def __init__(self, graph):
        self.graph = graph

    def haversine_distance(self, node1, node2):
        R = 6371000        
        phi1, phi2 = math.radians(node1.lat), math.radians(node2.lat)
        dphi = math.radians(node2.lat - node1.lat)
        dlambda = math.radians(node2.lon - node1.lon)
        
        a = math.sin(dphi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(dlambda/2)**2
            
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c