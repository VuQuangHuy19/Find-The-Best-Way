# Tài liệu mô tả dự án: Delivery-Route-Optimization

## 1. Giới thiệu chức năng
Dự án **Delivery-Route-Optimization** tập trung vào việc tối ưu hóa tuyến đường giao hàng dựa trên dữ liệu bản đồ thực tế. Hệ thống cho phép trích xuất, lọc, và chuẩn hóa dữ liệu bản đồ từ OpenStreetMap (OSM) để xây dựng đồ thị mạng lưới giao thông, từ đó tạo nền tảng áp dụng các thuật toán tìm đường (định hướng áp dụng thuật toán A*).

## 2. Công nghệ sử dụng
- **Python**: Ngôn ngữ lập trình chính.
- **Osmium-tool**: Công cụ Command-line xử lý dữ liệu bản đồ OSM gốc (cắt khu vực, lọc lớp dữ liệu `.pbf`).
- **OSMnx**: Thư viện Python dùng để nạp dữ liệu XML từ OSM thành cấu trúc đồ thị (Graph).
- **NetworkX**: Thư viện Python xử lý, lưu trữ và phân tích đồ thị đường đi.
- **Môi trường ảo (venv)**: Để phân lập và quản lý các thư viện phụ thuộc (dependencies).

## 3. Cấu trúc thư mục và file

```text
Delivery-Route-Optimization/
│
├── .gitignore          # Cấu hình bỏ qua các file/thư mục không đưa lên Git (venv, __pycache__).
├── README.md           # Hướng dẫn chi tiết quy trình xử lý dữ liệu bản đồ (cắt, lọc, đổi định dạng).
├── main.py             # File thực thi chính để nạp bản đồ, trích xuất dữ liệu Nodes & Edges.
├── algorithms.py       # Chứa lớp các thuật toán tính toán không gian và tìm đường.
├── models.py           # Định nghĩa cấu trúc dữ liệu mô phỏng đối tượng trên bản đồ.
├── map_processor.py    # Module đảm nhiệm chức năng xử lý file XML bản đồ, chuyển thành Graph.
├── maps/               # Thư mục chứa dữ liệu bản đồ gốc và đã qua xử lý.
│   ├── hanoi_roads_only.osm.pbf
│   ├── small_map.osm
│   └── small_roads_only.osm.pbf
└── venv/               # Môi trường ảo Python của dự án.
```

## 4. Chi tiết cấu trúc mã nguồn (Components)

### 4.1. `models.py` (Mô hình dữ liệu)
Định nghĩa 2 thành phần cốt lõi cấu tạo nên đồ thị không gian:
- **`MapNode`**: Đại diện cho 1 điểm trên bản đồ (như ngã tư, ngã rẽ). Chứa các thuộc tính: `id` (mã định danh từ OSM), `lat` (vĩ độ), `lon` (kinh độ).
- **`MapEdge`**: Đại diện cho 1 đoạn đường nối giữa 2 điểm (Nodes). Chứa các thuộc tính: `u` (ID node bắt đầu), `v` (ID node kết thúc), `length` (chiều dài thực tế của đoạn đường), `oneway` (boolean xác định đường một chiều hay hai chiều).

### 4.2. `map_processor.py` (Xử lý dữ liệu bản đồ)
Chứa class **`MapProcessor`** thực hiện quá trình đưa dữ liệu vào mã nguồn Python:
- Nạp file `.osm` (XML) bằng thư viện `osmnx` qua hàm `load_graph()`.
- Phương thức `extract_nodes()`: Trích xuất các node từ đồ thị của NetworkX, chuyển đổi thành tập hợp (dictionary) các đối tượng `MapNode`.
- Phương thức `extract_edges()`: Trích xuất các cạnh nối, lấy thông tin chiều dài và hướng di chuyển để tạo danh sách đối tượng `MapEdge`.

### 4.3. `algorithms.py` (Thuật toán)
- Hiện tại có class **`RouteFinder`** để quản lý việc tìm đường.
- Định nghĩa hàm **`haversine_distance(node1, node2)`**: Thuật toán tính khoảng cách đường chim bay giữa hai tọa độ địa lý (GPS) trên bề mặt Trái đất. Hàm này rất quan trọng vì nó thường được dùng làm hàm tính heuristic (H-cost) trong thuật toán A*.

### 4.4. `main.py` (Chương trình chính)
Quy trình thực thi hiện tại nhằm kiểm tra việc load dữ liệu:
1. Chỉ định đường dẫn tới bản đồ mục tiêu (`maps/small_map.osm`).
2. Khởi tạo đối tượng `MapProcessor` và tiến hành nạp thành đồ thị (`load_graph`).
3. Thực hiện trích xuất tổng thể danh sách các Nodes và Edges.
4. Xuất log ra màn hình console (số lượng Nodes/Edges, in thử vĩ độ, kinh độ của một Node để xác minh thao tác đọc dữ liệu đã thành công).

## 5. Quy trình xử lý dữ liệu (Data Processing Pipeline)
Dữ liệu của dự án được tiền xử lý chặt chẽ (đã hướng dẫn trong `README.md`) nhằm giảm thiểu dung lượng bộ nhớ khi xử lý thuật toán:
1. **Cắt vùng (Bounding Box)**: Dùng `osmium extract` cắt một khu vực nhất định (ví dụ: một quận của Hà Nội) dựa trên Min/Max kinh-vĩ độ.
2. **Lọc đường bộ (Highway Filtering)**: Sử dụng `osmium tags-filter` để chỉ giữ lại các đối tượng là đường giao thông, loại bỏ đi nhà cửa, sông hồ, rừng cây,...
3. **Chuyển đổi sang XML**: Đổi file nén nhị phân dạng `.pbf` sang định dạng XML phẳng (`.osm`) bằng lệnh `osmium cat`, từ đó thư viện Python (như OSMnx) mới có thể đọc và biểu diễn thành cấu trúc dữ liệu đồ thị.
