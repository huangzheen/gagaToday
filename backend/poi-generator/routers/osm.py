"""
OSM 数据提取 API
为素材生成器提供真实地图数据的查询接口
"""

from fastapi import APIRouter, Query, HTTPException
from ..services.osm_extractor import extract_osm_data

router = APIRouter(prefix="/api/osm", tags=["osm"])


@router.get("/extract")
async def api_osm_extract(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    tile_url: str = Query(None, description="PMTiles URL（可选）"),
):
    """
    查询指定坐标的 OSM 地图数据

    返回该位置附近的所有有用信息：
    - primary_poi: 主 POI（名称、类型、多语言翻译）
    - building: 建筑信息（高度、颜色）
    - address: 地址/门牌号
    - transport: 附近交通（U-Bahn、电车）
    - roads: 道路名称
    - nearby_pois: 附近兴趣点
    """
    try:
        result = extract_osm_data(lat, lng, tile_url)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
