import math
from heapq import heappush, heappop

class RouteFinder:
    def __init__(self, graph):
        self.graph = graph

    def haversine_distance(self, node1, node2):
        R = 6371000
        phi1, phi2 = math.radians(node1['lat']), math.radians(node2['lat'])
        dphi = math.radians(node2['lat'] - node1['lat'])
        dlambda = math.radians(node2['lon'] - node1['lon'])

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _heuristic(self, node_id, goal_id):
        node = self.graph.nodes[node_id]
        goal = self.graph.nodes[goal_id]
        return self.haversine_distance({'lat': node['y'], 'lon': node['x']}, {'lat': goal['y'], 'lon': goal['x']})

    def _edge_cost(self, u, v, data):
        if data.get('length') is not None:
            return data['length']
        u_node = self.graph.nodes[u]
        v_node = self.graph.nodes[v]
        return self.haversine_distance({'lat': u_node['y'], 'lon': u_node['x']}, {'lat': v_node['y'], 'lon': v_node['x']})

    def a_star(self, start_id, goal_id):
        if start_id not in self.graph or goal_id not in self.graph:
            return None

        open_set = []
        heappush(open_set, (0, start_id))
        came_from = {}
        g_score = {start_id: 0}
        f_score = {start_id: self._heuristic(start_id, goal_id)}
        closed = set()

        while open_set:
            _, current = heappop(open_set)
            if current == goal_id:
                return self._reconstruct_path(came_from, current)

            if current in closed:
                continue
            closed.add(current)

            for _, neighbor, data in self.graph.out_edges(current, data=True):
                tentative = g_score[current] + self._edge_cost(current, neighbor, data)
                if tentative < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f_score[neighbor] = tentative + self._heuristic(neighbor, goal_id)
                    heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def get_path_length(self, path):
        if not path or len(path) < 2:
            return 0.0

        total = 0.0
        for u, v in zip(path, path[1:]):
            edge_data = None
            if self.graph.has_edge(u, v):
                edge_data = next(iter(self.graph.get_edge_data(u, v).values()))
            if edge_data is not None:
                total += self._edge_cost(u, v, edge_data)
            else:
                node_u = self.graph.nodes[u]
                node_v = self.graph.nodes[v]
                total += self.haversine_distance({'lat': node_u['y'], 'lon': node_u['x']}, {'lat': node_v['y'], 'lon': node_v['x']})
        return total