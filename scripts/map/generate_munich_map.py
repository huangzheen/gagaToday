#!/usr/bin/env python3
"""
从 OpenStreetMap 获取慕尼黑市中心真实地图数据 → 像素 tilemap
输出: frontend/public/assets/munich_map/tilemap.json

FF6 风格像素地图 (16x16 tiles)
"""

import json
import math
import sys
import urllib.request
import urllib.error

# ── 慕尼黑市中心范围 (~1.3km × 1.1km) ──
# 覆盖: Marienplatz · Rathaus · Frauenkirche · Viktualienmarkt · Hofbräuhaus · Residenz
BBOX = (48.132, 11.563, 48.143, 11.588)  # south, west, north, east

# 地图网格尺寸 (tiles) — 32px 瓦片
COLS, ROWS = 80, 70

# Tile types (对应 tileset_v2 索引)
# 0-2 草地 | 3 道路 | 4-8 建筑 | 9 人行道 | 10 水面
# 11-12 公园 | 13 广场 | 14-15 POI | 16 羊皮纸
T_GRASS     = 0    # 会被随机化为 0-2
T_ROAD      = 3
T_BUILDING  = 4    # 会被随机化为 4-8
T_SIDEWALK  = 9
T_WATER     = 10
T_PARK      = 11   # 会被随机化为 11-12
T_PLAZA     = 13
T_POI_MARK  = 14   # 会被随机化为 14-15

# ── POI 定义 (名称, lat, lng, 描述) ──
POIS = [
    ("Marienplatz",       48.1372, 11.5754, "玛利亚广场 · 市中心"),
    ("Rathaus",           48.1376, 11.5752, "新市政厅 · 哥特式建筑"),
    ("Frauenkirche",      48.1386, 11.5737, "圣母教堂 · 慕尼黑标志"),
    ("St. Peter",         48.1364, 11.5758, "圣彼得教堂 · Alter Peter"),
    ("Viktualienmarkt",   48.1352, 11.5763, "谷物市场 · 露天市集"),
    ("Hofbräuhaus",       48.1374, 11.5797, "皇家啤酒屋 ·  HB"),
    ("Residenz",          48.1404, 11.5781, "慕尼黑皇宫"),
    ("Odeonsplatz",       48.1424, 11.5774, "音乐厅广场"),
    ("Isar Tor",          48.1345, 11.5818, "伊萨尔门"),
    ("Karlsplatz",        48.1398, 11.5657, "卡尔广场 · Stachus"),
    ("Pinakothek Area",   48.1480, 11.5700, "艺术区"),
    ("Deutsches Museum",  48.1300, 11.5840, "德意志博物馆"),
]


def latlng_to_tile(lat, lng, cols, rows, bbox):
    """经纬度 → tile 网格坐标 (整数)"""
    s, w, n, e = bbox
    col = int((lng - w) / (e - w) * cols)
    row = int((n - lat) / (n - s) * rows)
    return col, row


def tile_to_latlng(col, row, cols, rows, bbox):
    """tile 网格坐标 → 经纬度 (中心点)"""
    s, w, n, e = bbox
    lng = w + (col + 0.5) / cols * (e - w)
    lat = n - (row + 0.5) / rows * (n - s)
    return lat, lng


def query_overpass(bbox):
    """调用 Overpass API 获取建筑/道路/水系/绿地数据"""
    s, w, n, e = bbox
    query = f"""
    [out:json][timeout:30];
    (
      way["building"]({s},{w},{n},{e});
      way["highway"]({s},{w},{n},{e});
      way["waterway"]({s},{w},{n},{e});
      way["natural"="water"]({s},{w},{n},{e});
      way["leisure"~"park|garden|common"]({s},{w},{n},{e});
      way["landuse"~"grass|forest|meadow"]({s},{w},{n},{e});
      way["place"="square"]({s},{w},{n},{e});
      relation["building"]({s},{w},{n},{e});
    );
    out body;
    >;
    out skel qt;
    """
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("User-Agent", "GermanLearningRPG/1.0 (map demo)")
    print(f"🌐 请求 Overpass API (bbox={bbox})...", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 错误: {e.code} {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        sys.exit(1)


def build_node_map(osm_json):
    """OSM JSON → {node_id: (lat, lng)} 字典"""
    nodes = {}
    for el in osm_json.get("elements", []):
        if el["type"] == "node":
            nodes[el["id"]] = (el["lat"], el["lon"])
    return nodes


def rasterize_ways(osm_json, nodes, cols, rows, bbox):
    """
    将 OSM ways 光栅化到 tile 网格
    返回: grid (cols x rows 的 2D list)
    """
    grid = [[T_GRASS for _ in range(rows)] for _ in range(cols)]

    categories = {
        "building": [],
        "highway": [],
        "water": [],
        "park": [],
        "square": [],
    }

    s, w, n, e = bbox

    for el in osm_json.get("elements", []):
        if el["type"] != "way":
            continue
        tags = el.get("tags", {})

        # 收集每个类别的 way
        if "building" in tags:
            categories["building"].append(el)
        if "highway" in tags:
            categories["highway"].append(el)
        if "waterway" in tags or tags.get("natural") == "water":
            categories["water"].append(el)
        if tags.get("leisure") in ("park", "garden", "common") or \
           tags.get("landuse") in ("grass", "forest", "meadow"):
            categories["park"].append(el)
        if tags.get("place") == "square":
            categories["square"].append(el)

    # 1. 水系 (优先级最高)
    print(f"  🏞️ 水系: {len(categories['water'])} ways", flush=True)
    for way in categories["water"]:
        fill_polygon(grid, way, nodes, cols, rows, bbox, T_WATER)

    # 2. 公园/绿地
    print(f"  🌳 绿地: {len(categories['park'])} ways", flush=True)
    for way in categories["park"]:
        fill_polygon(grid, way, nodes, cols, rows, bbox, T_PARK)

    # 3. 广场
    print(f"  ⬜ 广场: {len(categories['square'])} ways", flush=True)
    for way in categories["square"]:
        fill_polygon(grid, way, nodes, cols, rows, bbox, T_PLAZA)

    # 4. 道路
    print(f"  🛣️ 道路: {len(categories['highway'])} ways", flush=True)
    for way in categories["highway"]:
        draw_way_line(grid, way, nodes, cols, rows, bbox, T_ROAD)

    # 5. 建筑 (最上层)
    print(f"  🏠 建筑: {len(categories['building'])} ways", flush=True)
    for way in categories["building"]:
        fill_polygon(grid, way, nodes, cols, rows, bbox, T_BUILDING)

    return grid


def get_way_nodes(way, nodes):
    """从 way 提取节点坐标列表"""
    pts = []
    for ref in way.get("nodes", []):
        if ref in nodes:
            pts.append(nodes[ref])
    return pts


def latlng_to_grid(lat, lng, cols, rows, bbox):
    """经纬度 → (col, row) 网格坐标"""
    s, w, n, e = bbox
    c = int((lng - w) / (e - w) * cols)
    r = int((n - lat) / (n - s) * rows)
    return max(0, min(cols-1, c)), max(0, min(rows-1, r))


def point_in_polygon(lat, lng, poly):
    """
    射线法: 判断点是否在多边形内
    poly: [(lat, lng), ...]
    """
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        yi, xi = poly[i]
        yj, xj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
           (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def fill_polygon(grid, way, nodes, cols, rows, bbox, tile_type):
    """
    用扫描线法填充多边形区域
    """
    pts = get_way_nodes(way, nodes)
    if len(pts) < 3:
        return

    # 计算多边形边界框 (tile 坐标)
    min_c, min_r = cols, rows
    max_c, max_r = 0, 0
    tile_pts = []
    for lat, lng in pts:
        c, r = latlng_to_grid(lat, lng, cols, rows, bbox)
        tile_pts.append((c, r))
        min_c = min(min_c, c)
        max_c = max(max_c, c)
        min_r = min(min_r, r)
        max_r = max(max_r, r)

    # 裁剪到网格范围
    min_c = max(0, min_c)
    max_c = min(cols-1, max_c)
    min_r = max(0, min_r)
    max_r = min(rows-1, max_r)

    # 对 bbox 内的每个 tile, 将 tile 中心经纬度转回 latlng 做点面测试
    for c in range(min_c, max_c + 1):
        for r in range(min_r, max_r + 1):
            lat, lng = tile_to_latlng(c, r, cols, rows, bbox)
            if point_in_polygon(lat, lng, pts):
                grid[c][r] = tile_type


def draw_way_line(grid, way, nodes, cols, rows, bbox, tile_type):
    """
    Bresenham 线算法: 绘制线状元素(道路/河流)
    """
    pts = get_way_nodes(way, nodes)
    if len(pts) < 2:
        return

    for i in range(len(pts) - 1):
        c0, r0 = latlng_to_grid(pts[i][0], pts[i][1], cols, rows, bbox)
        c1, r1 = latlng_to_grid(pts[i+1][0], pts[i+1][1], cols, rows, bbox)
        for point in bresenham(c0, r0, c1, r1):
            c, r = point
            if 0 <= c < cols and 0 <= r < rows:
                grid[c][r] = tile_type

    # 道路加宽: 相邻 tile 也设为道路 (1 tile 宽)
    # 第二次 pass: 把紧邻道路的 grass 也标为 road
    new_road = []
    for c in range(1, cols-1):
        for r in range(1, rows-1):
            if grid[c][r] == T_GRASS:
                for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
                    if grid[c+dc][r+dr] == T_ROAD:
                        new_road.append((c, r))
                        break
    for c, r in new_road:
        grid[c][r] = T_ROAD


def bresenham(x0, y0, x1, y1):
    """Bresenham 直线算法"""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points


def place_pois(grid, cols, rows, bbox):
    """
    标记 POI 位置: 在 grid 上设置高亮 tile, 返回 pois 元数据
    """
    poi_list = []
    for name, lat, lng, desc in POIS:
        c, r = latlng_to_tile(lat, lng, cols, rows, bbox)
        if 0 <= c < cols and 0 <= r < rows:
            # 确保 POI 在建筑内或旁边
            if grid[c][r] == T_GRASS:
                grid[c][r] = T_PLAZA  # 落点设为广场
            grid[c][r] = T_POI_MARK  # 高亮

            # POI 周围的 8 邻域也设为 T_POI_MARK
            for dc in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    nc, nr = c + dc, r + dr
                    if 0 <= nc < cols and 0 <= nr < rows:
                        if grid[nc][nr] not in (T_WATER,):
                            grid[nc][nr] = T_POI_MARK

            poi_list.append({
                "name": name,
                "col": c,
                "row": r,
                "lat": lat,
                "lng": lng,
                "desc": desc,
            })

    return poi_list


def main():
    print("🗺️  = 慕尼黑像素地图生成器 =", flush=True)
    print(f"📐 网格: {COLS}×{ROWS} tile", flush=True)

    # 1. 拉取 OSM
    osm_data = query_overpass(BBOX)

    # 2. 构建节点索引
    nodes = build_node_map(osm_data)
    print(f"📍 节点数: {len(nodes)}", flush=True)

    # 3. 光栅化
    grid = rasterize_ways(osm_data, nodes, COLS, ROWS, BBOX)

    # 4. 统计
    counts = {}
    for row in grid:
        for val in row:
            counts[val] = counts.get(val, 0) + 1
    print(f"📊 Tile 分布: {dict(sorted(counts.items()))}", flush=True)
    total = COLS * ROWS
    built = counts.get(T_BUILDING, 0) + counts.get(T_POI_MARK, 0)
    print(f"🏠 建筑覆盖率: {built}/{total} ({built/total*100:.1f}%)", flush=True)

    # 5. POI
    pois = place_pois(grid, COLS, ROWS, BBOX)
    print(f"⭐ POI: {len(pois)} 个", flush=True)

    # 6. 随机化变体: 草地 0→0~2, 建筑 4→4~8, 公园 11→11~12, POI 14→14~15
    import random
    random.seed(2026)
    for c in range(COLS):
        for r in range(ROWS):
            v = grid[c][r]
            if v == T_GRASS:
                grid[c][r] = random.randint(0, 2)
            elif v == T_BUILDING:
                grid[c][r] = random.randint(4, 8)
            elif v == T_PARK:
                grid[c][r] = random.randint(11, 12)
            elif v == T_POI_MARK:
                grid[c][r] = random.randint(14, 15)

    # 7. 输出 JSON
    out_dir = "assets/munich_map"
    tilemap = {
        "cols": COLS,
        "rows": ROWS,
        "tileWidth": 32,
        "tileHeight": 32,
        "bbox": {"south": BBOX[0], "west": BBOX[1], "north": BBOX[2], "east": BBOX[3]},
        "layers": [{
            "name": "ground",
            "data": grid  # 列主序: data[col][row]
        }]
    }
    with open(f"{out_dir}/tilemap.json", "w") as f:
        json.dump(tilemap, f)
    print(f"💾 tilemap.json 已写入 {out_dir}/", flush=True)

    # POI 列表不再单独导出 pois.json (前端通过 /api/v2/pois 读取,不走静态文件)

    # 7. 输出文本版地图 (调试用)
    # chars = {T_GRASS: '.', T_ROAD: '#', T_BUILDING: '█', T_SIDEWALK: '░',
    #          T_WATER: '~', T_PARK: '&', T_PLAZA: '▒', T_POI_MARK: '★'}
    # with open(f"{out_dir}/map_ascii.txt", "w") as f:
    #     for r in range(ROWS):
    #         line = ''.join(chars[grid[c][r]] for c in range(COLS))
    #         f.write(line + '\n')

    print("✅ 完成!")


if __name__ == "__main__":
    main()
