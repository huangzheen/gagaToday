"""
数据保存路由 — 将生成内容写入文件系统 + SQLite
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.file_service import save_json, save_image, save_source_record, save_poi_package, list_draft_pois
from ..services.db_service import (
    upsert_poi, add_scene, add_content, log_export, list_scenes,
)

router = APIRouter(prefix="/api", tags=["save"])


class SaveJsonRequest(BaseModel):
    data: dict | list
    relative_path: str
    city: str = "munich"
    poi_id: str = None
    is_draft: bool = True


class SaveImageRequest(BaseModel):
    source_path: str
    poi_id: str
    subfolder: str = "exterior"
    filename: str = None
    city: str = "munich"


class SaveSourceRequest(BaseModel):
    records: list[dict]
    city: str = "munich"
    poi_id: str = None


class SavePackageRequest(BaseModel):
    files: list[dict]  # [{"relative_path": "xxx.draft.json", "data": {...}}, ...]
    poi_id: str
    city: str = "munich"
    date_suffix: str = None
    source_records: list[dict] = None
    is_draft: bool = True


@router.post("/save/json")
async def api_save_json(req: SaveJsonRequest):
    """保存 JSON 数据"""
    try:
        result = save_json(
            data=req.data,
            relative_path=req.relative_path,
            city=req.city,
            poi_id=req.poi_id,
            is_draft=req.is_draft,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save/image")
async def api_save_image(req: SaveImageRequest):
    """保存图片到 assets 目录，并记录到 SQLite"""
    try:
        from pathlib import Path
        result = save_image(
            source_path=Path(req.source_path),
            poi_id=req.poi_id,
            subfolder=req.subfolder,
            filename=req.filename,
            city=req.city,
        )
        target_path = result.get("path", "")

        # 构造浏览器可访问的 URL 路径
        url_path = target_path
        # 如果路径包含 /assets/，用它作 URL
        if "/assets/" in target_path:
            url_path = "/" + target_path[target_path.index("assets/"):]
        else:
            # fallback: /generated/
            url_path = f"/generated/{Path(target_path).name}"

        # 从 subfolder/filename 推断 scene_type 和 variant
        scene_type = req.subfolder  # exterior / interior / tower
        variant = req.filename
        if variant:
            variant = Path(variant).stem  # 去掉 .png
            # 去掉 poi_id_ 前缀（如果有）
            prefix = f"{req.poi_id}_"
            if variant.startswith(prefix):
                variant = variant[len(prefix):]

        # 写入 SQLite
        add_scene(
            poi_id=req.poi_id,
            city=req.city,
            url_path=url_path,
            scene_type=scene_type,
            variant=variant,
            file_path=target_path,
            sort_order=0,
        )

        return {"success": True, **result, "synced_to_db": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save/source")
async def api_save_source(req: SaveSourceRequest):
    """保存来源记录"""
    try:
        result = save_source_record(
            records=req.records,
            city=req.city,
            poi_id=req.poi_id,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save/package")
async def api_save_package(req: SavePackageRequest):
    """批量保存 POI 全套内容到 drafts 目录，并同步到 SQLite"""
    try:
        # 1. 写入文件系统
        result = save_poi_package(
            files=req.files,
            city=req.city,
            poi_id=req.poi_id,
            date_suffix=req.date_suffix,
            source_records=req.source_records,
            is_draft=req.is_draft,
        )

        # 2. 同步到 SQLite
        poi_id = req.poi_id
        city = req.city
        batch = req.date_suffix
        content_types = []

        for file_item in req.files:
            relative_path = file_item.get("relative_path", "")
            data = file_item.get("data")
            if not relative_path or data is None:
                continue

            # 从文件名推断 content_type
            ct = relative_path.replace(".draft.json", "").replace(".json", "")
            # 特殊情况
            ct_map = {
                "poi_info": "info",
                "npc_profiles": "npc",
                "dialogues": "dialogue",
                "npc_dialogue_hooks": "dialogue_hooks",
                "knowledge_cards": "knowledge",
                "quests": "quest",
                "checkin_targets": "checkin",
            }
            ct = ct_map.get(ct, ct)
            content_types.append(ct)

            # 如果是 poi_info，先 upsert POI（外键约束要求 pois 表先有记录）
            if ct == "info" and isinstance(data, dict):
                upsert_poi(
                    poi_id=poi_id,
                    city=city,
                    name_de=data.get("name_de"),
                    name_zh=data.get("name_zh"),
                    type_=data.get("type"),
                    lat=data.get("lat"),
                    lng=data.get("lng"),
                    icon=data.get("icon"),
                    walk_minutes=data.get("walk_minutes") or data.get("walk"),
                    cost=data.get("cost"),
                    ubahn=data.get("ubahn"),
                    description=data.get("description") or data.get("d"),
                    acts=data.get("acts"),
                    unlocked=True,
                    is_published=True,
                )

            # 写入 db
            add_content(
                poi_id=poi_id,
                city=city,
                content_type=ct,
                data=data,
                export_batch=batch,
                file_path=relative_path,
            )

        # 3. 记录导出日志
        log_export(
            poi_id=poi_id,
            city=city,
            batch_id=batch or "",
            file_count=len(req.files),
            content_types=content_types,
        )

        return {"success": True, **result, "synced_to_db": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pois")
async def api_list_pois(city: str = "munich"):
    """列出已有 draft 的 POI"""
    pois = list_draft_pois(city)
    return {"success": True, "pois": pois}


@router.get("/pois/{poi_id}")
async def api_get_poi(poi_id: str, city: str = "munich"):
    """获取某个 POI 的现有数据"""
    from ..services.file_service import CONTENT_DRAFTS_ROOT
    poi_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}"
    if not poi_dir.exists():
        raise HTTPException(status_code=404, detail=f"POI {poi_id} 没有 draft 数据")

    files = {}
    for f in sorted(poi_dir.iterdir()):
        if f.is_file() and f.suffix == ".json":
            import json
            with open(f, "r", encoding="utf-8") as fh:
                try:
                    files[f.name] = json.load(fh)
                except json.JSONDecodeError:
                    files[f.name] = {"error": "解析失败"}

    return {"success": True, "poi_id": poi_id, "files": files}
