"""
数据保存路由 — 将生成内容写入文件系统 + SQLite
"""

import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..services.file_service import save_json, save_image, save_source_record, save_poi_package, list_draft_pois, save_upload_asset, list_uploaded_assets, delete_uploaded_asset
from ..services.db_service import (
    upsert_poi, add_scene, add_content, log_export, list_scenes,
)
from ..config import CONTENT_DRAFTS_ROOT

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


class UploadAssetRequest(BaseModel):
    """前端 base64 上传直存 game assets。文件名由后端自动决定。"""
    data: str                  # base64 encoded image data
    poi_id: str
    asset_kind: str            # "scene_main" | "icon"
    city: str = "munich"


class SavePackageRequest(BaseModel):
    files: list[dict]  # [{"relative_path": "xxx.draft.json", "data": {...}}, ...]
    poi_id: str
    city: str = "munich"
    date_suffix: str = None
    source_records: list[dict] = None
    is_draft: bool = True
    register_published: bool = True  # False = 纯草稿保存,不动 pois.is_published


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


@router.get("/save/json")
async def api_load_json(
    relative_path: str = Query(..., description="相对路径,如 'poi_info.draft.json'"),
    poi_id: str = Query(None),
    city: str = Query("munich"),
    is_draft: bool = Query(True),
):
    """读取已保存的 JSON 文件(draft 目录或正式目录)"""
    import json as _json
    from pathlib import Path

    if is_draft:
        if poi_id:
            base_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}"
        else:
            base_dir = CONTENT_DRAFTS_ROOT / city
    else:
        base_dir = CONTENT_DRAFTS_ROOT / city

    file_path = base_dir / relative_path
    if not file_path.exists():
        # 404 表示没有这个 draft,前端用 fallback(KNOWN_POIS)
        raise HTTPException(status_code=404, detail=f"文件不存在: {relative_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = _json.load(f)
        return {"success": True, "data": data, "path": str(file_path)}
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


class DeleteAssetRequest(BaseModel):
    """删除某个 POI 的某个已上传资源。"""
    filename: str
    poi_id: str
    asset_kind: str            # "scene_main" | "icon" | "npc_head" | "npc_half"
    city: str = "munich"


class NpcContentRequest(BaseModel):
    """保存/覆盖 NPC 列表(JSON)到 poi_content 表 content_type='npc'"""
    poi_id: str
    data: list[dict]           # NPC 数组
    city: str = "munich"


class TransparentRequest(BaseModel):
    """把已上传的白底 PNG 转成透明底(覆盖原文件,备份到 .bak-white.png)"""
    filename: str
    poi_id: str
    asset_kind: str            # scene_main / icon / npc_head / npc_half
    city: str = "munich"


@router.post("/save/npc-content")
async def api_save_npc_content(req: NpcContentRequest):
    """覆盖式写入 NPC 列表(JSON)到 poi_content 表"""
    from ..services.db_service import add_content
    add_content(
        poi_id=req.poi_id,
        city=req.city,
        content_type='npc',
        data=req.data,
        file_path=None,
    )
    return {"success": True, "count": len(req.data)}


@router.post("/white-to-transparent")
async def api_white_to_transparent(req: TransparentRequest):
    """把 game assets 下的某张白底 PNG 转成透明底(复用 scripts/white_to_transparent.py)"""
    import sys, asyncio
    from pathlib import Path as _Path
    from ..config import PROJECT_ROOT
    script = PROJECT_ROOT / "scripts" / "white_to_transparent.py"
    if not script.exists():
        raise HTTPException(status_code=500, detail="scripts/white_to_transparent.py not found")

    # 计算目标文件路径(复用 file_service 的路径规则)
    from ..services.file_service import ASSETS_ROOT
    if req.asset_kind == "scene_main":
        target_dir = ASSETS_ROOT / "scenes" / req.city / req.poi_id / "_reference"
    elif req.asset_kind == "icon":
        target_dir = ASSETS_ROOT / "icons" / req.city
    elif req.asset_kind in ("npc_head", "npc_half"):
        target_dir = ASSETS_ROOT / "characters" / req.city / f"npc_{req.poi_id}"
    else:
        raise HTTPException(status_code=400, detail=f"unsupported asset_kind: {req.asset_kind}")
    target = target_dir / req.filename
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"{req.filename} 不存在")

    # 跑脚本(子进程同步执行,简单可靠)
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(script), str(target),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f"脚本失败: {stderr.decode()[:300]}")

    return {
        "success": True,
        "path": str(target),
        "filename": req.filename,
        "log": stdout.decode().strip(),
    }


@router.get("/list-assets")
async def api_list_assets(
    poi_id: str,
    asset_kind: str,
    city: str = "munich",
):
    """列出某 POI 的某类已上传资源。返回 [{filename, url, size_bytes}]"""
    from ..services.file_service import list_uploaded_assets
    try:
        files = list_uploaded_assets(poi_id=poi_id, asset_kind=asset_kind, city=city)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "files": files}


@router.post("/upload-asset")
async def api_upload_asset(req: UploadAssetRequest):
    """接收 base64 图片直存 game assets(scene_main → _reference/ | icon → assets/icons/)"""
    import base64 as b64
    try:
        # 兼容 data:image/png;base64,XXX 格式
        payload = req.data.split(",", 1)[-1] if req.data.startswith("data:") else req.data
        raw = b64.b64decode(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid base64 image data")

    try:
        result = save_upload_asset(
            data=raw,
            poi_id=req.poi_id,
            asset_kind=req.asset_kind,
            city=req.city,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"success": True, **result}


@router.delete("/upload-asset")
async def api_delete_asset(req: DeleteAssetRequest):
    """删除某个 POI 的某个已上传资源文件(scene 图 / 图标)"""
    try:
        result = delete_uploaded_asset(
            filename=req.filename,
            poi_id=req.poi_id,
            asset_kind=req.asset_kind,
            city=req.city,
        )
        return {"success": True, **result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            # 仅在 register_published=True 时才标记为已发布,纯草稿保存不动 pois 表
            if req.register_published and ct == "info" and isinstance(data, dict):
                upsert_poi(
                    poi_id=poi_id,
                    city=city,
                    name_de=data.get("name_de"),
                    name_zh=data.get("name_zh"),
                    type_=data.get("type"),
                    lat=data.get("lat"),
                    lng=data.get("lng"),
                    icon=data.get("icon"),
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
