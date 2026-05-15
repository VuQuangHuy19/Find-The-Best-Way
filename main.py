import os
from map_processor import MapProcessor

def main():
    osm_path = os.environ.get("MAP_FILE", "maps/hanoi_12_districts_roads.osm")
    if not os.path.exists(osm_path):
        print(f"[{osm_path}] không tồn tại, sẽ dùng fallback maps/small_map.osm.")
        osm_path = "maps/small_map.osm"
    
    processor = MapProcessor(osm_path)
    
    print("--- Đang nạp đồ thị bản đồ ---")
    G = processor.load_graph()
    
    nodes = processor.extract_nodes()
    edges = processor.extract_edges()
    
    print(f"Thành công!")
    print(f"Số lượng Nodes (Ngã rẽ/Điểm tọa độ): {len(nodes)}")
    print(f"Số lượng Edges (Đoạn đường nối): {len(edges)}")
    
    first_node_id = list(nodes.keys())[0]
    test_node = nodes[first_node_id]
    print(f"Ví dụ Node {test_node.id}: Lat {test_node.lat}, Lon {test_node.lon}")

if __name__ == "__main__":
    main()