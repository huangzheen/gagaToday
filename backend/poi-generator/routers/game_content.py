"""
Phase 2: 玩家端运行时内容 API

端点:
  GET /api/game/v1/cities                       → 列出所有可用城市
  GET /api/game/v1/cities/{city_id}/bundle      → 取 CityBundle(支持 ETag/304)

设计原则:
- city_id 路径参数化(即使现在只服务 munich,接口契约已支持多城市)
- 返回的 CityBundle 已经过 Pydantic 校验,客户端 Zod 解析必通过
- ETag 来自 runtime_export_service 的 _compute_etag(基于 content)
- 304 协商:客户端带 If-None-Match,服务匹配则返回 304 空 body
- CORS 由 main.py 的 CORSMiddleware 统一处理
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Response

from ..config import DB_PATH
from ..services.runtime_export_service import (
    CITY_ID_PATTERN,
    ExportError,
    export_city,
)

router = APIRouter(prefix="/api/game/v1", tags=["game-content"])

# 城市元数据(Phase 2:hardcoded,Phase 3 改成 DB 表)
# 字段:
#   id: 路由参数
#   displayName: zh 显示名
#   country: 国家(目前都是 DE)
#   center: 地图初始中心 [lng, lat]
#   zoom: 地图初始 zoom
#   bbox: 地图边界 [west, south, east, north]
#   pmtilesUrl: 浏览器可访问的 PMTiles URL
#   available: True=有 published POI 数据,False=仅占位
_CITIES = {
    "munich": {
        "id": "munich",
        "displayName": {"de": "München", "zh": "慕尼黑", "en": "Munich"},
        "country": "DE",
        "center": [11.5755, 48.1374],
        "zoom": 12.5,
        "bbox": [11.3608, 48.0610, 11.7229, 48.2482],
        "pmtilesUrl": "/assets/munich_map/pmtiles/germany-zoom16.pmtiles",
        "available": True,
    },
    # 后续 Phase 2.x / Phase 3 加 berlin / hamburg / koeln / frankfurt
}


def _open_db() -> sqlite3.Connection:
    """打开 DB 连接(单连接 / 短生命周期,FastAPI Depends 也行但这里更直接)"""
    db_path = Path(DB_PATH)
    if not db_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"DB 不存在: {db_path}",
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/cities")
def list_cities() -> dict:
    """列出所有可用城市

    Response:
      {
        "schemaVersion": 1,
        "cities": [
          {id, displayName, country, center, zoom, bbox, pmtilesUrl, available},
          ...
        ]
      }
    """
    return {
        "schemaVersion": 1,
        "cities": list(_CITIES.values()),
    }


@router.get("/cities/{city_id}/bundle")
def get_city_bundle(
    city_id: str,
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
) -> Response:
    """取 CityBundle(支持 ETag/304)

    Headers:
      If-None-Match: 客户端缓存的 ETag(来自上一次响应)

    Response:
      200: CityBundle JSON + ETag header
      304: 空 body(If-None-Match 匹配)
      400: city_id 非法
      404: 城市不存在 / 无 published 数据
      500: 导出失败
    """
    # 1. city_id 格式校验
    if not CITY_ID_PATTERN.match(city_id):
        raise HTTPException(
            status_code=400,
            detail=f"city_id 不合法: {city_id!r}",
        )

    # 2. 城市是否在 registry
    if city_id not in _CITIES:
        raise HTTPException(
            status_code=404,
            detail=f"未知城市: {city_id!r}",
        )

    # 3. 导出
    conn = _open_db()
    try:
        try:
            result = export_city(city_id, conn)
        except ExportError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        conn.close()

    # 4. ETag 协商(304)
    if if_none_match and if_none_match.strip() == result.etag:
        # 注意:某些客户端会带 W/"xxx" 弱 ETag 前缀,这里我们生成的就是 W/"xxx" 格式
        return Response(
            status_code=304,
            headers={
                "ETag": result.etag,
                "X-Content-Version": result.content_version,
                "Cache-Control": "private, max-age=0, must-revalidate",
            },
        )

    # 5. 200 with JSON body
    import json
    body = json.dumps(
        result.bundle.to_runtime_json(),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return Response(
        content=body,
        status_code=200,
        media_type="application/json; charset=utf-8",
        headers={
            "ETag": result.etag,
            "X-Content-Version": result.content_version,
            # ETag 已够强,这里告诉浏览器:必须 revalidate,但允许短期缓存
            "Cache-Control": "private, max-age=60, must-revalidate",
        },
    )