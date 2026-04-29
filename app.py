from flask import Flask, jsonify, render_template, request
from map_processor import MapProcessor
from algorithms import RouteFinder

app = Flask(__name__)

# Dùng file bản đồ đã cắt sẵn
MAP_FILE = "maps/small_map.osm"
processor = MapProcessor(MAP_FILE)
graph = processor.load_graph()
route_finder = RouteFinder(graph)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map-data')
def map_data():
    nodes = []
    for node_id, data in graph.nodes(data=True):
        nodes.append({
            'id': node_id,
            'lat': data['y'],
            'lon': data['x']
        })

    edges = []
    for u, v, data in graph.edges(data=True):
        u_lat = graph.nodes[u]['y']
        u_lon = graph.nodes[u]['x']
        v_lat = graph.nodes[v]['y']
        v_lon = graph.nodes[v]['x']
        coords = [
            [u_lat, u_lon],
            [v_lat, v_lon]
        ]
        geometry = data.get('geometry')
        if geometry is not None:
            if hasattr(geometry, 'coords'):
                coords = [[pt[1], pt[0]] if isinstance(pt, tuple) else [pt.y, pt.x] for pt in geometry.coords]
            else:
                coords = [[pt[1], pt[0]] for pt in geometry]

        edges.append({
            'u': u,
            'v': v,
            'coords': coords,
            'length': data.get('length', 0),
            'oneway': data.get('oneway', False)
        })

    return jsonify({
        'nodes': nodes,
        'edges': edges
    })

@app.route('/closest-node')
def closest_node():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    node_id, distance = processor.find_closest_node(lat, lon)
    node = graph.nodes[node_id]
    return jsonify({
        'id': node_id,
        'lat': node['y'],
        'lon': node['x'],
        'distance': distance
    })

@app.route('/find-path', methods=['POST'])
def find_path():
    payload = request.json or {}
    start_lat = payload.get('start_lat')
    start_lon = payload.get('start_lon')
    end_lat = payload.get('end_lat')
    end_lon = payload.get('end_lon')

    if start_lat is None or start_lon is None or end_lat is None or end_lon is None:
        return jsonify({'error': 'Yêu cầu truyền start_lat, start_lon, end_lat, end_lon'}), 400

    start_node_id, start_distance = processor.find_closest_node(start_lat, start_lon)
    end_node_id, end_distance = processor.find_closest_node(end_lat, end_lon)

    path = route_finder.a_star(start_node_id, end_node_id)
    if path is None:
        return jsonify({'error': 'Không tìm được đường đi'}), 404

    path_coords = []
    for node_id in path:
        node = graph.nodes[node_id]
        path_coords.append({
            'id': node_id,
            'lat': node['y'],
            'lon': node['x']
        })

    total_distance = route_finder.get_path_length(path)
    return jsonify({
        'start_node': {'id': start_node_id, 'lat': graph.nodes[start_node_id]['y'], 'lon': graph.nodes[start_node_id]['x'], 'snap_distance': start_distance},
        'end_node': {'id': end_node_id, 'lat': graph.nodes[end_node_id]['y'], 'lon': graph.nodes[end_node_id]['x'], 'snap_distance': end_distance},
        'path': path_coords,
        'distance': total_distance
    })

if __name__ == '__main__':
    app.run(debug=True)
