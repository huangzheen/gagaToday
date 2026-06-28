"""
OSM POI 反向地理编码 — 按名字搜 PMTiles 找坐标

调用 osm_geocode.mjs (Node.js) 扫描 PMTiles 的 Munich bbox,
按字符串匹配返回候选 POI 列表。
"""

import json
import subprocess
from pathlib import Path

_SCRIPT = Path(__file__).parent / "osm_geocode.mjs"


def geocode_osm_poi(
    query: str,
    lat_min: float = 48.06,
    lat_max: float = 48.25,
    lng_min: float = 11.36,
    lng_max: float = 11.75,
    tile_url: str = None,
    timeout: int = 30,
) -> dict:
    """
    按名字反向地理编码: 搜 PMTiles 找候选 POI

    Args:
        query: 用户输入的名字(任意语言: 中/英/德 等)
        lat_min/lat_max/lng_min/lng_max: 搜索 bbox(默认 Munich 主城区 + 紧邻郊区)
        tile_url: PMTiles URL (可选)
        timeout: Node 脚本超时(秒)

    Returns:
        {
            "success": True,
            "query": "...",
            "best_match": {name, name_de, name_en, lat, lng, class, subclass, ...} or None,
            "results": [...top 20],
            "tiles_scanned": N,
            "matches_found": N,
        }
    """
    cmd = ["node", str(_SCRIPT), query, str(lat_min), str(lat_max), str(lng_min), str(lng_max)]
    if tile_url:
        cmd.append(tile_url)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {
            "success": False,
            "query": query,
            "error": f"OSM geocoder timeout (> {timeout}s)",
        }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": f"OSM geocoder spawn failed: {e}",
        }

    if proc.returncode != 0:
        return {
            "success": False,
            "query": query,
            "error": f"OSM geocoder exit {proc.returncode}: {(stderr or stdout).strip()[:500]}",
        }

    if not stdout or not stdout.strip():
        return {
            "success": False,
            "query": query,
            "error": f"OSM geocoder empty stdout. stderr: {stderr.strip()[:300]}",
        }

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "query": query,
            "error": f"OSM geocoder output not JSON: {e}\nOutput: {stdout[:500]}",
        }

    return data