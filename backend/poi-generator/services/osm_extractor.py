"""
OSM 数据提取服务
从 PMTiles 提取 OpenStreetMap 特征数据，供生成器前端使用
"""

import json
import subprocess
from pathlib import Path

_SCRIPT = Path(__file__).parent / "osm_extractor.mjs"


def extract_osm_data(lat: float, lng: float, tile_url: str = None) -> dict:
    """
    提取指定坐标的 OSM 数据

    Args:
        lat: 纬度
        lng: 经度
        tile_url: PMTiles URL（可选，默认通过 frontend server 的 HTTP Range）

    Returns:
        dict: 结构化 OSM 数据（与 osm_extractor.mjs 输出一致）
    """
    cmd = ["node", str(_SCRIPT), str(lat), str(lng)]
    if tile_url:
        cmd.append(tile_url)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"OSM extractor failed: {stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"OSM extractor output not JSON: {e}\n{result.stdout[:500]}")
