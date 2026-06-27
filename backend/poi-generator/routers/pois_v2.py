"""
地图端 POI 数据 API (v2)
供前端地图 (frontend/index.html) 通过 fetch() 调用，替代硬编码的 gamePois
"""

import json
from fastapi import APIRouter, HTTPException, Query
from ..services.db_service import (
    list_pois, get_poi, list_scenes, get_latest_content,
    upsert_poi, delete_poi,
)

router = APIRouter(prefix="/api/v2", tags=["pois-v2"])


@router.get("/pois")
async def api_v2_list_pois(
    city: str = Query("munich", description="城市"),
    type_: str = Query(None, alias="type", description="按类型过滤"),
    published_only: bool = Query(True, description="只列出已发布的 POI"),
):
    """
    获取 POI 列表（地图渲染用）

    返回格式与前端 gamePois 结构兼容。
    """
    pois = list_pois(city=city, type_=type_, published_only=published_only)

    # 为每个 POI 填充 imgs
    for p in pois:
        scenes = list_scenes(p["id"], city)
        p["imgs"] = [s["url_path"] for s in scenes]

    return {"success": True, "pois": pois, "total": len(pois)}


@router.get("/pois/{poi_id}")
async def api_v2_get_poi(
    poi_id: str,
    city: str = Query("munich"),
    include_content: bool = Query(False, description="是否包含导出内容（NPC、对话等）"),
):
    """获取单个 POI 详情"""
    poi = get_poi(poi_id, city)
    if not poi:
        raise HTTPException(status_code=404, detail=f"POI '{poi_id}' 不存在")

    # 场景图片
    scenes = list_scenes(poi_id, city)
    poi["imgs"] = [s["url_path"] for s in scenes]
    poi["scenes_detail"] = scenes

    # 可选：附带导出内容
    if include_content:
        poi["content"] = get_latest_content(poi_id, city)

    return {"success": True, "poi": poi}


@router.post("/pois")
async def api_v2_create_poi(data: dict):
    """手动创建/更新一个 POI（供生成器或管理工具调用）"""
    result = upsert_poi(
        poi_id=data.get("id"),
        city=data.get("city", "munich"),
        name_de=data.get("name_de"),
        name_zh=data.get("name_zh"),
        type_=data.get("type"),
        lat=data.get("lat"),
        lng=data.get("lng"),
        icon=data.get("icon"),
        description=data.get("description"),
        acts=data.get("acts"),
        unlocked=data.get("unlocked", False),
        is_published=data.get("is_published", False),
    )
    return {"success": True, **result}


@router.delete("/pois/{poi_id}")
async def api_v2_delete_poi(
    poi_id: str,
    city: str = Query("munich"),
):
    """删除一个 POI"""
    delete_poi(poi_id, city)
    return {"success": True, "poi_id": poi_id}
