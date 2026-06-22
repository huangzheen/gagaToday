#!/usr/bin/env python3
"""
从 OpenStreetMap Overpass API 获取慕尼黑市中心真实数据 → GeoJSON

输出: assets/munich_map/munich.geojson (FeatureCollection)
兼容 gagaToday Canvas 渲染器

Usage: python3 scripts/map/osm_to_geojson.py
"""

import json
import sys
import urllib.request
import urllib.parse

# ── 慕尼黑市中心 (~3km × 2.5km) ──
# Schwabing → Altstadt → Deutsches Museum
BBOX = (48.125, 11.555, 48.165, 11.605)  # south, west, north, east


def query_overpass(query_str, description=""):
    """调用 Overpass API"""
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({"data": query_str}).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("User-Agent", "GermanLearningRPG/2.0 (GeoJSON export)")
    print(f"🌐 {description}...", flush=True, end=" ")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            result = json.loads(raw)
            print(f"OK ({len(result.get('elements',[]))} elements)", flush=True)
            return result
    except Exception as e:
        print(f"❌ {e}", flush=True)
        sys.exit(1)


def build_node_map(osm_data):
    """{node_id: (lat, lng)}"""
    nodes = {}
    for el in osm_data.get("elements", []):
        if el["type"] == "node":
            nodes[el["id"]] = (el["lat"], el["lon"])
    return nodes


def way_to_coords(way, nodes):
    """way → [[lng, lat], ...] (GeoJSON 顺序)"""
    coords = []
    for ref in way.get("nodes", []):
        if ref in nodes:
            lat, lng = nodes[ref]
            coords.append([lng, lat])
    return coords if len(coords) >= 2 else None


# ── 主流程 ──
def main():
    south, west, north, east = BBOX
    bbox_str = f"({south},{west},{north},{east})"

    features = []

    # ─────────────────────────────
    # 1. 道路 (highway)
    # ─────────────────────────────
    q1 = f"""
    [out:json][timeout:60];
    (
      way["highway"]{bbox_str};
    );
    out body;
    >;
    out skel qt;
    """
    osm1 = query_overpass(q1, "道路 highway")
    nodes1 = build_node_map(osm1)
    for el in osm1["elements"]:
        if el["type"] != "way":
            continue
        coords = way_to_coords(el, nodes1)
        if not coords:
            continue
        tags = el.get("tags", {})
        features.append({
            "type": "Feature",
            "properties": {
                "highway": tags.get("highway", "road"),
                "name": tags.get("name", ""),
                "osm_id": str(el["id"]),
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            },
        })

    # ─────────────────────────────
    # 2. 建筑 (building)
    # ─────────────────────────────
    q2 = f"""
    [out:json][timeout:60];
    (
      way["building"]{bbox_str};
      relation["building"]{bbox_str};
    );
    out body;
    >;
    out skel qt;
    """
    osm2 = query_overpass(q2, "建筑 building")
    nodes2 = build_node_map(osm2)
    for el in osm2["elements"]:
        if el["type"] != "way":
            continue
        coords = way_to_coords(el, nodes2)
        if not coords or len(coords) < 3:
            continue
        # 闭合 polygon
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        tags = el.get("tags", {})
        features.append({
            "type": "Feature",
            "properties": {
                "building": "yes",
                "name": tags.get("name", ""),
                "osm_id": str(el["id"]),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
        })

    # ─────────────────────────────
    # 3. 水系 (water / waterway)
    # ─────────────────────────────
    q3 = f"""
    [out:json][timeout:60];
    (
      way["waterway"="river"]{bbox_str};
      way["waterway"="canal"]{bbox_str};
      way["waterway"="stream"]{bbox_str};
      way["natural"="water"]{bbox_str};
    );
    out body;
    >;
    out skel qt;
    """
    osm3 = query_overpass(q3, "水系 water")
    nodes3 = build_node_map(osm3)
    for el in osm3["elements"]:
        if el["type"] != "way":
            continue
        coords = way_to_coords(el, nodes3)
        if not coords or len(coords) < 3:
            continue
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        tags = el.get("tags", {})
        features.append({
            "type": "Feature",
            "properties": {
                "waterway": tags.get("waterway", ""),
                "natural": tags.get("natural", ""),
                "name": tags.get("name", ""),
                "osm_id": str(el["id"]),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
        })

    # ─────────────────────────────
    # 4. 公园 / 绿地
    # ─────────────────────────────
    q4 = f"""
    [out:json][timeout:60];
    (
      way["leisure"]["leisure"~"park|garden|common"]{bbox_str};
      way["landuse"]["landuse"~"grass|forest|meadow"]{bbox_str};
      way["natural"="wood"]{bbox_str};
    );
    out body;
    >;
    out skel qt;
    """
    osm4 = query_overpass(q4, "公园/绿地")
    nodes4 = build_node_map(osm4)
    for el in osm4["elements"]:
        if el["type"] != "way":
            continue
        coords = way_to_coords(el, nodes4)
        if not coords or len(coords) < 3:
            continue
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        tags = el.get("tags", {})
        features.append({
            "type": "Feature",
            "properties": {
                "leisure": tags.get("leisure", ""),
                "landuse": tags.get("landuse", ""),
                "name": tags.get("name", ""),
                "osm_id": str(el["id"]),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
        })

    # ─────────────────────────────
    # 5. 铁路 / 地铁
    # ─────────────────────────────
    q5 = f"""
    [out:json][timeout:60];
    (
      way["railway"]["railway"~"rail|subway|tram"]{bbox_str};
      node["railway"="station"]{bbox_str};
      node["railway"="subway_entrance"]{bbox_str};
      node["public_transport"="station"]{bbox_str};
    );
    out body;
    >;
    out skel qt;
    """
    osm5 = query_overpass(q5, "铁路/地铁")
    nodes5 = build_node_map(osm5)
    for el in osm5["elements"]:
        tags = el.get("tags", {})
        if el["type"] == "way":
            coords = way_to_coords(el, nodes5)
            if not coords or len(coords) < 2:
                continue
            features.append({
                "type": "Feature",
                "properties": {
                    "railway": tags.get("railway", ""),
                    "name": tags.get("name", ""),
                    "osm_id": str(el["id"]),
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords,
                },
            })
        elif el["type"] == "node":
            features.append({
                "type": "Feature",
                "properties": {
                    "railway": "station",
                    "name": tags.get("name", ""),
                    "osm_id": str(el["id"]),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [el["lon"], el["lat"]],
                },
            })

    # ─────────────────────────────
    # 6. POI (amenity / shop / tourism)
    # ─────────────────────────────
    q6 = f"""
    [out:json][timeout:60];
    (
      node["amenity"]["amenity"~"restaurant|cafe|school|university|library|pharmacy|hospital|place_of_worship|bank|atm|post_office"]{bbox_str};
      node["shop"]["shop"~"bakery|supermarket|convenience|mall|books|clothes"]{bbox_str};
      node["tourism"]["tourism"~"museum|attraction|hotel|hostel|gallery"]{bbox_str};
    );
    out body;
    """
    osm6 = query_overpass(q6, "POI")
    for el in osm6["elements"]:
        if el["type"] != "node":
            continue
        tags = el.get("tags", {})
        cat = tags.get("amenity") or tags.get("shop") or tags.get("tourism") or "poi"
        feat = {
            "type": "Feature",
            "properties": {
                "amenity": tags.get("amenity", ""),
                "shop": tags.get("shop", ""),
                "tourism": tags.get("tourism", ""),
                "name": tags.get("name", ""),
                "osm_id": str(el["id"]),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [el["lon"], el["lat"]],
            },
        }
        features.append(feat)

    # ─────────────────────────────
    # 输出
    # ─────────────────────────────
    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    out_path = "assets/munich_map/munich.geojson"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    # 统计
    counts = {}
    for feat in features:
        p = feat["properties"]
        key = p.get("highway") or p.get("waterway") or p.get("railway") or \
              p.get("amenity") or p.get("shop") or p.get("tourism") or \
              p.get("building") or p.get("leisure") or p.get("landuse") or \
              p.get("natural") or "other"
        counts[key] = counts.get(key, 0) + 1

    print(f"\n{'='*50}")
    print(f"📦 GeoJSON: {len(features)} features")
    print(f"💾 {out_path}")
    print(f"\n📊 类型分布:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k:20s} {v:5d}")
    print(f"\n✅ 完成！可直接替换 demo 中的 sampleGeoJSON")


if __name__ == "__main__":
    main()
