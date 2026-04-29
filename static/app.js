const statusText = document.getElementById('status');
const startNodeText = document.getElementById('start-node');
const endNodeText = document.getElementById('end-node');
const distanceText = document.getElementById('distance');
const selectStartBtn = document.getElementById('select-start');
const selectEndBtn = document.getElementById('select-end');
const findPathBtn = document.getElementById('find-path');

let selecting = null;
let startPoint = null;
let endPoint = null;
let startNode = null;
let endNode = null;
let pathLayer = null;
let edgeLayer = null;
let startMarker = null;
let endMarker = null;

const map = L.map('map').setView([21.045, 105.716], 14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('/map-data')
    .then(response => response.json())
    .then(data => {
        const edges = data.edges;
        edgeLayer = L.layerGroup();
        edges.forEach(edge => {
            const polyline = L.polyline(edge.coords, {
                color: '#888',
                weight: 2,
                opacity: 0.7
            });
            edgeLayer.addLayer(polyline);
        });
        edgeLayer.addTo(map);
        statusText.innerText = 'Bản đồ đã tải xong.';
    })
    .catch(() => {
        statusText.innerText = 'Không thể tải dữ liệu bản đồ.';
    });

map.on('click', async (event) => {
    if (!selecting) {
        return;
    }

    const {lat, lng} = event.latlng;
    const response = await fetch(`/closest-node?lat=${lat}&lon=${lng}`);
    const node = await response.json();

    if (selecting === 'start') {
        startPoint = {lat, lon: lng};
        startNode = node;
        setMarker('start', node);
        startNodeText.innerText = `${node.id} (${node.lat.toFixed(6)}, ${node.lon.toFixed(6)})`;
    } else if (selecting === 'end') {
        endPoint = {lat, lon: lng};
        endNode = node;
        setMarker('end', node);
        endNodeText.innerText = `${node.id} (${node.lat.toFixed(6)}, ${node.lon.toFixed(6)})`;
    }

    selecting = null;
    selectStartBtn.classList.remove('active');
    selectEndBtn.classList.remove('active');
    statusText.innerText = 'Đã chọn điểm. Nhấn Tìm đường để chạy thuật toán.';
});

selectStartBtn.addEventListener('click', () => {
    selecting = 'start';
    selectStartBtn.classList.add('active');
    selectEndBtn.classList.remove('active');
    statusText.innerText = 'Click vào bản đồ để chọn điểm bắt đầu.';
});

selectEndBtn.addEventListener('click', () => {
    selecting = 'end';
    selectEndBtn.classList.add('active');
    selectStartBtn.classList.remove('active');
    statusText.innerText = 'Click vào bản đồ để chọn điểm kết thúc.';
});

findPathBtn.addEventListener('click', async () => {
    if (!startPoint || !endPoint) {
        statusText.innerText = 'Cần chọn cả điểm bắt đầu và điểm kết thúc.';
        return;
    }

    statusText.innerText = 'Đang tìm đường...';
    const response = await fetch('/find-path', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            start_lat: startPoint.lat,
            start_lon: startPoint.lon,
            end_lat: endPoint.lat,
            end_lon: endPoint.lon
        })
    });
    const result = await response.json();

    if (!response.ok) {
        statusText.innerText = `Lỗi: ${result.error}`;
        return;
    }

    drawPath(result.path);
    distanceText.innerText = result.distance.toFixed(2);
    statusText.innerText = `Đã tìm đường từ node ${result.start_node.id} đến node ${result.end_node.id}.`;
});

function setMarker(type, node) {
    const markerOptions = {
        start: {color: 'green'},
        end: {color: 'red'}
    }[type];

    const marker = L.circleMarker([node.lat, node.lon], {
        radius: 8,
        color: markerOptions.color,
        fillColor: markerOptions.color,
        fillOpacity: 0.8
    }).bindPopup(`${type === 'start' ? 'Bắt đầu' : 'Kết thúc'}: ${node.id}`);

    if (type === 'start') {
        if (startMarker) { map.removeLayer(startMarker); }
        startMarker = marker;
    } else {
        if (endMarker) { map.removeLayer(endMarker); }
        endMarker = marker;
    }
    marker.addTo(map).openPopup();
}

function drawPath(path) {
    if (pathLayer) {
        map.removeLayer(pathLayer);
    }
    const coords = path.map(node => [node.lat, node.lon]);
    pathLayer = L.polyline(coords, {color: 'red', weight: 5, opacity: 0.9});
    pathLayer.addTo(map);
    map.fitBounds(pathLayer.getBounds(), {padding: [40, 40]});
}
