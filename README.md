## Quy trình xử lý dữ liệu bản đồ 

Phần này hướng dẫn chi tiết cách trích xuất, lọc và chuẩn hóa dữ liệu từ OpenStreetMap (OSM) để phục vụ thuật toán tìm đường A*.

---

### 1. Công cụ yêu cầu
* **Osmium-tool**: Xử lý cắt và lọc file `.pbf`.
* **OSMnx**: Thư viện Python dùng để nạp dữ liệu XML thành đồ thị NetworkX.

---

### 2. Các câu lệnh xử lý dữ liệu

Thực hiện các bước sau để tối ưu hóa dung lượng file bản đồ trước khi đưa vào mã nguồn:

**Bước 1: Cắt vùng bản đồ mục tiêu (Bounding Box)**
Xác định tọa độ khu vực (MinLon, MinLat, MaxLon, MaxLat) để giảm tải cho hệ thống.
```bash
osmium extract -b 105.70,21.03,105.76,21.08 vietnam-latest.osm.pbf -o targeted_area.osm.pbf 
```

**Bước 2: Lọc dữ liệu đường bộ (Highway Filtering)
Chỉ giữ lại các đối tượng là đường giao thông, loại bỏ các dữ liệu rác như cây cối, tòa nhà.**
``` bash
osmium tags-filter targeted_area.osm.pbf w/highway -o roads_only.osm.pbf 
```
**Bước 3: Chuyển đổi định dạng sang XML
Chuyển file nhị phân sang định dạng XML để thư viện Python có thể đọc trực tiếp.**

``` bash
osmium cat roads_only.osm.pbf -o map_data.osm
```

## Chạy ứng dụng web local

Dự án đã thêm một ứng dụng Flask đơn giản để hiển thị bản đồ và tìm đường bằng thuật toán A*.

1. Cài thư viện:
```bash
pip install -r requirements.txt
```
2. Chạy server:
```bash
python app.py
```
3. Mở trình duyệt vào:
```text
http://127.0.0.1:5000
```

> Trên giao diện, click `Chọn Bắt đầu`, chọn điểm trên bản đồ, sau đó click `Chọn Kết thúc` và chọn điểm đích. Cuối cùng nhấn `Tìm đường` để chạy A*.

## Mở rộng bản đồ sang toàn bộ khu vực Hà Nội (12 quận)

Để xử lý quy mô lớn hơn, ví dụ toàn bộ 12 quận nội thành Hà Nội: Ba Đình, Hoàn Kiếm, Đống Đa, Hai Bà Trưng, Cầu Giấy, Tây Hồ, Thanh Xuân, Hoàng Mai, Long Biên, Hà Đông, Bắc Từ Liêm và Nam Từ Liêm.

### 1. Thực hiện mở rộng vùng trích xuất
Sử dụng `osmium` để trích xuất vùng bản đồ Hà Nội từ file `.pbf` gốc.

```bash
osmium extract -b 105.68,20.94,106.05,21.12 vietnam-latest.osm.pbf -o hanoi_12_districts.osm.pbf
```

### 2. Lọc chỉ giữ dữ liệu đường bộ
Giữ lại các bản ghi `highway` hợp lệ cho xe chạy. Câu lệnh sau giữ lại các loại đường chính và tránh các đường đi bộ hoặc xe đạp.

```bash
osmium tags-filter hanoi_12_districts.osm.pbf \
  w/highway=motorway,motorway_link,trunk,trunk_link,primary,primary_link,secondary,secondary_link,tertiary,tertiary_link,unclassified,residential,service,road \
  -o hanoi_12_districts_roads.osm.pbf
```

### 3. Chuyển sang file XML `.osm`
Đổi sang định dạng XML để `osmnx` có thể nạp trực tiếp.

```bash
osmium cat hanoi_12_districts_roads.osm.pbf -o hanoi_12_districts_roads.osm
```

### 4. Nạp bản đồ lớn hơn vào ứng dụng
Dự án hiện đã hỗ trợ đọc file mặc định `maps/hanoi_12_districts_roads.osm`.

Nếu bạn muốn chỉ định file khác, bạn có thể sửa biến `MAP_FILE` trong `app.py`, hoặc dùng biến môi trường `MAP_FILE`:

```bash
set MAP_FILE=maps/hanoi_12_districts_roads.osm
python app.py
```

Hoặc với PowerShell:

```powershell
$env:MAP_FILE = "maps/hanoi_12_districts_roads.osm"
python app.py
```

Nếu file cấu hình không tồn tại thì ứng dụng sẽ tự động chuyển về `maps/small_map.osm`.

### 5. Lưu ý hiệu năng và chất lượng dữ liệu
- File bản đồ Hà Nội lớn hơn nhiều so với `small_map.osm` nên quá trình nạp và tìm đường có thể chậm hơn.
- Nếu cần tối ưu hơn, có thể tiếp tục chia bản đồ theo quận hoặc dùng bộ lọc `highway` thêm các loại đường phù hợp.
- Dữ liệu đường đi hoàn toàn phụ thuộc vào OpenStreetMap. Nếu khu vực sau Petro Nhổn không có đường thực tế trong OSM, thì ứng dụng cũng sẽ không tìm được đường đi hợp lệ qua khu vực đó.
- Ngược lại, nếu OSM chứa đường ảo hoặc đường nội bộ không phù hợp, bạn cần kiểm tra lại file `.osm` hoặc bổ sung bộ lọc `highway` để loại bỏ các đối tượng không phải đường xe chạy.

> Với cách này, bạn sẽ mở rộng vùng bản đồ toàn Hà Nội 12 quận mà vẫn giữ được luồng xử lý hiện tại của dự án.

## Cách thức hoạt động của dự án

Dự án gồm hai phần chính:
- Xử lý dữ liệu bản đồ và xây dựng đồ thị đường đi.
- Ứng dụng web hiển thị bản đồ, chọn điểm và tìm đường bằng thuật toán A*.

### Luồng xử lý dữ liệu bản đồ
1. Dùng `osmium` để cắt vùng bản đồ mong muốn từ file `.pbf` nguyên gốc.
2. Lọc chỉ giữ lại các thẻ `highway` để thu được dữ liệu đường bộ sạch hơn.
3. Chuyển file đã lọc sang định dạng XML (`.osm`) để Python và `osmnx` có thể nạp.
4. `MapProcessor.load_graph()` sử dụng `osmnx.graph_from_xml()` để xây dựng đồ thị NetworkX từ file XML.
5. `MapProcessor.extract_nodes()` và `MapProcessor.extract_edges()` đọc các node/edge từ đồ thị và tạo các đối tượng `MapNode`, `MapEdge`.

### Luồng backend
1. `app.py` khởi tạo `MapProcessor` với file bản đồ `maps/small_map.osm`.
2. Gọi `processor.load_graph()` để nạp đồ thị và tạo `RouteFinder(graph)`.
3. Endpoint `/map-data` trả về danh sách `nodes` và `edges` dưới dạng JSON để frontend hiển thị.
4. Endpoint `/closest-node` nhận tọa độ của người dùng, quét toàn bộ node trong đồ thị và tìm node gần nhất bằng công thức Haversine.
5. Endpoint `/find-path` nhận `start_lat`, `start_lon`, `end_lat`, `end_lon`, tìm node gần nhất tương ứng, rồi gọi `route_finder.a_star()`.
6. Kết quả trả về là danh sách node trên đường đi, tổng khoảng cách và thông tin node bắt đầu/kết thúc.

### Luồng frontend
1. `templates/index.html` tải thư viện Leaflet và `static/app.js`.
2. Khi trang mở, frontend gọi `/map-data` để hiển thị toàn bộ đường phố dưới dạng polyline trên bản đồ.
3. Người dùng nhấn `Chọn Bắt đầu` hoặc `Chọn Kết thúc`, rồi click một điểm trên bản đồ.
4. Với mỗi click, frontend gọi `/closest-node` để xác định node đồ thị gần nhất và hiển thị marker.
5. Khi nhấn `Tìm đường`, frontend gửi tọa độ bắt đầu/kết thúc tới `/find-path`.
6. Nếu tìm được đường đi, frontend vẽ đường đi màu đỏ và cập nhật tổng khoảng cách.

### Luồng thuật toán A*
1. `RouteFinder.a_star(start_id, goal_id)` chạy trên đồ thị định hướng của `osmnx`.
2. Hàm heuristic dùng khoảng cách Haversine giữa node hiện tại và đích.
3. Chi phí cạnh (`_edge_cost`) ưu tiên giá trị `length` nếu có, còn không thì dùng khoảng cách Haversine giữa hai node.
4. A* duyệt các node theo `f_score = g_score + heuristic` và lưu lại đường đi tốt nhất bằng `came_from`.
5. Khi đến node đích, `_reconstruct_path()` tạo lại chuỗi node từ đích về bắt đầu.
6. `get_path_length(path)` tính tổng chiều dài của đường đi dựa trên dữ liệu cạnh hoặc khoảng cách Haversine.

### Các tệp hữu ích khác
- `main.py`: ví dụ kiểm tra nạp đồ thị, đếm số node và edge, in thông tin node mẫu.
- `map_processor.py`: xử lý nạp bản đồ, trích xuất node/edge và tìm node gần nhất.
- `algorithms.py`: triển khai thuật toán A* tìm đường tốt nhất trên đồ thị.
- `models.py`: định nghĩa các lớp `MapNode` và `MapEdge` để lưu dữ liệu bản đồ.

## Tóm tắt luồng chính
1. Chuẩn bị dữ liệu OSM bằng `osmium`.
2. Nạp đồ thị với `osmnx` trong `MapProcessor`.
3. Khởi động Flask và đưa dữ liệu bản đồ ra frontend.
4. Người dùng chọn hai điểm, frontend tìm node gần nhất và yêu cầu tìm đường.
5. Backend chạy A* và trả đường đi về, frontend vẽ tuyến đường trên bản đồ.
