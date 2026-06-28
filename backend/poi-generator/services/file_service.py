"""
文件保存服务
管理生成内容归档到正确目录
"""

import json
from datetime import datetime
from pathlib import Path
from ..config import ASSETS_ROOT, CONTENT_DRAFTS_ROOT


def _ensure_dir(path: Path) -> Path:
    """确保目录存在"""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_json(
    data: dict | list,
    relative_path: str,
    city: str = "munich",
    poi_id: str = None,
    is_draft: bool = True,
) -> dict:
    """
    保存 JSON 数据到 content 目录

    Args:
        data: 要保存的数据
        relative_path: 相对路径 (如 "npc_profiles.draft.json")
        city: 城市名
        poi_id: POI ID（可选，用于分组）
        is_draft: 是否保存到 drafts 目录

    Returns:
        {"path": "...", "size_bytes": N}
    """
    if is_draft:
        if poi_id:
            base_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}"
        else:
            base_dir = CONTENT_DRAFTS_ROOT / city
    else:
        base_dir = Path("/Volumes/NewDisk/GermanLearning/frontend/src/content") / city

    file_path = base_dir / relative_path
    _ensure_dir(file_path)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    size = file_path.stat().st_size
    return {"path": str(file_path), "size_bytes": size}


def save_image(
    source_path: Path,
    poi_id: str,
    subfolder: str = "exterior",
    filename: str = None,
    city: str = "munich",
) -> dict:
    """
    将生成的图片复制到 assets 目录

    Args:
        source_path: 源文件路径
        poi_id: POI ID
        subfolder: 子文件夹 (exterior / interior / tower / _thumbnails)
        filename: 文件名（可选，默认用源文件名）
        city: 城市名

    Returns:
        {"path": "...", "size_bytes": N}
    """
    if filename is None:
        filename = source_path.name

    target_dir = ASSETS_ROOT / "scenes" / city / poi_id / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / filename

    # 文件已在目标位置(源=目标),跳过 copy,直接复用。
    # 这样 RefWorkflow/UploadsPanel 已经把图放在 _reference/ 后,再调 save/image
    # 注册到 poi_scenes 表也不会报 "are the same file"。
    import shutil
    if source_path.resolve() != target_path.resolve():
        shutil.copy2(str(source_path), str(target_path))

    return {"path": str(target_path), "size_bytes": target_path.stat().st_size}


def save_source_record(
    records: list[dict],
    city: str = "munich",
    poi_id: str = None,
) -> dict:
    """
    保存 source_records.json

    Args:
        records: 来源记录列表
        city: 城市名
        poi_id: POI ID

    Returns:
        {"path": "..."}
    """
    if poi_id:
        base_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}"
    else:
        base_dir = CONTENT_DRAFTS_ROOT / city

    file_path = base_dir / "source_records.json"
    _ensure_dir(file_path)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    return {"path": str(file_path)}


def list_draft_pois(city: str = "munich") -> list[dict]:
    """
    列出所有已有 draft 的 POI

    Returns:
        [{"poi_id": "...", "files": [...], "updated_at": "..."}, ...]
    """
    if not CONTENT_DRAFTS_ROOT.exists():
        return []

    pois = []
    for poi_dir in sorted(CONTENT_DRAFTS_ROOT.iterdir()):
        if not poi_dir.is_dir():
            continue
        # 目录名格式: {city}_{poi_id} 或 {city}
        name = poi_dir.name
        if name.startswith(f"{city}_"):
            poi_id = name[len(city) + 1:]
        else:
            poi_id = name

        files = [f.name for f in poi_dir.iterdir() if f.is_file() and f.suffix == ".json"]
        mtime = datetime.fromtimestamp(
            max(f.stat().st_mtime for f in poi_dir.iterdir() if f.is_file())
        ).isoformat() if files else None

        pois.append({
            "poi_id": poi_id,
            "files": files,
            "updated_at": mtime,
        })

    return pois


def save_poi_package(
    files: list[dict],
    city: str = "munich",
    poi_id: str = None,
    date_suffix: str = None,
    source_records: list[dict] = None,
    is_draft: bool = True,
) -> dict:
    """
    保存一组 POI 相关 JSON 文件到草稿目录(覆盖式)

    同一 POI 多次发布 → 写入同一个目录,文件 in-place 覆盖。
    如果之前有过带 date_suffix 的旧目录,会自动清掉,避免累积。

    Args:
        files: [{"relative_path": "poi_info.draft.json", "data": {...}}, ...]
        city: 城市名
        poi_id: POI ID
        date_suffix: 可选。传了就用 (例如导出历史快照);不传就用稳定目录
        source_records: optional list of source records
        is_draft: 是否保存为草稿

    Returns:
        {"saved_files": [...], "source_path": ...}
    """
    import shutil
    if not poi_id:
        raise ValueError("poi_id is required for save_poi_package")

    if date_suffix:
        package_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}_{date_suffix}"
    else:
        # 稳定目录:同一 POI 永远写到 munich_{poi_id}/
        package_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}"
        # 清掉之前累积的 {city}_{poi_id}_* 旧目录(发布日期版本)
        for old_dir in CONTENT_DRAFTS_ROOT.glob(f"{city}_{poi_id}_*"):
            if old_dir.is_dir() and old_dir != package_dir:
                shutil.rmtree(old_dir, ignore_errors=True)

    package_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for file_item in files:
        relative_path = file_item.get("relative_path")
        data = file_item.get("data")
        if not relative_path or data is None:
            continue

        file_path = package_dir / relative_path
        _ensure_dir(file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        saved_files.append(str(file_path))

    source_path = None
    if source_records is not None:
        source_file = package_dir / "source_records.json"
        _ensure_dir(source_file)
        with open(source_file, "w", encoding="utf-8") as f:
            json.dump(source_records, f, ensure_ascii=False, indent=2)
        saved_files.append(str(source_file))
        source_path = str(source_file)

    return {"saved_files": saved_files, "source_path": source_path}

def save_upload_asset(
    data: bytes,
    poi_id: str,
    asset_kind: str,
    city: str = "munich",
) -> dict:
    """
    直接写上传的图片到 game assets 目录(base64 解码后的 bytes)。

    文件名自动决定,前端不需要传:
        - scene_main:
            - 第一个上传 → ref_{poi_id}.png  (跟 RefWorkflow 的定妆照同名,可互替)
            - 之后上传   → scene_{poi_id}_{N}.png  (N 递增,跳过已存在的序号)
        - icon:
            - {poi_id}_icon_64.png  (单文件,覆盖)

    Args:
        data: 已解码的图片 bytes
        poi_id: POI ID
        asset_kind: "scene_main" | "icon"
        city: 城市名

    Returns:
        {"path": ..., "filename": ..., "url": ..., "size_bytes": ...}
    """
    import re

    if asset_kind == "scene_main":
        target_dir = ASSETS_ROOT / "scenes" / city / poi_id / "_reference"
    elif asset_kind == "icon":
        target_dir = ASSETS_ROOT / "icons" / city
    elif asset_kind in ("npc_head", "npc_half"):
        if not poi_id:
            raise ValueError(f"{asset_kind} 需要 poi_id(=npc_id)")
        target_dir = ASSETS_ROOT / "characters" / city / f"npc_{poi_id}"
    else:
        raise ValueError(f"unsupported asset_kind: {asset_kind}")

    target_dir.mkdir(parents=True, exist_ok=True)

    # ── 自动命名 ──
    if asset_kind == "npc_head":
        filename = f"npc_{poi_id}_head.png"
    elif asset_kind == "npc_half":
        filename = f"npc_{poi_id}_half.png"
    elif asset_kind == "scene_main":
        primary = f"ref_{poi_id}.png"
        if not (target_dir / primary).exists():
            filename = primary
        else:
            # 找当前最大 N,生成 scene_{poi_id}_{N+1}.png
            existing = sorted(
                int(m.group(1))
                for f in target_dir.iterdir()
                if (m := re.match(rf"scene_{re.escape(poi_id)}_(\d+)\.png$", f.name))
            )
            next_n = (existing[-1] + 1) if existing else 1
            filename = f"scene_{poi_id}_{next_n}.png"
    else:  # icon
        filename = f"{poi_id}_icon_64.png"

    target_path = target_dir / filename
    target_path.write_bytes(data)

    url = "/" + str(target_path.relative_to(ASSETS_ROOT.parent))  # /assets/...
    return {
        "path": str(target_path),
        "filename": filename,
        "url": url,
        "size_bytes": len(data),
    }

def list_uploaded_assets(
    poi_id: str,
    asset_kind: str,
    city: str = "munich",
) -> list[dict]:
    """
    列出某 POI 的某类已上传资源。

    Args:
        poi_id: POI ID
        asset_kind: "scene_main" | "icon"
        city: 城市名

    Returns:
        [{"filename": "ref_X.png", "url": "/assets/...", "size_bytes": N, "mtime": iso}, ...]
    """
    from datetime import datetime
    if asset_kind == "scene_main":
        target_dir = ASSETS_ROOT / "scenes" / city / poi_id / "_reference"
    elif asset_kind == "icon":
        # icon 是扁平目录(assets/icons/<city>/<poi_id>_icon_64.png),
        # 不同 POI 的 icon 文件放在同一目录,必须按 poi_id 过滤文件名
        target_dir = ASSETS_ROOT / "icons" / city
    elif asset_kind in ("npc_head", "npc_half"):
        target_dir = ASSETS_ROOT / "characters" / city / f"npc_{poi_id}"
    else:
        raise ValueError(f"unsupported asset_kind: {asset_kind}")

    if not target_dir.exists():
        return []

    # 按 asset_kind 过滤文件名后缀(npc_head/npc_half 共用目录,只过滤文件名区分)
    suffix_filter = None
    if asset_kind == "npc_head":
        suffix_filter = "_head"
    elif asset_kind == "npc_half":
        suffix_filter = "_half"
    # icon 按 poi_id 前缀过滤(2026-06-28 修复:之前不过滤导致新 POI 误读 marienplatz 的图标)
    # 文件名约定: <poi_id>_icon_64.png,所以前缀就是 "<poi_id>_icon"
    icon_prefix = f"{poi_id}_icon" if asset_kind == "icon" else None

    files = []
    for f in target_dir.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        if suffix_filter and suffix_filter not in f.stem:
            continue
        # icon: 严格按 poi_id 前缀过滤(防止新 POI 误读其他 POI 的 icon)
        if icon_prefix and not f.stem.startswith(icon_prefix):
            continue
        files.append({
            "filename": f.name,
            "url": "/assets/" + str(f.relative_to(ASSETS_ROOT.parent / "assets")),
            "size_bytes": f.stat().st_size,
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    # 主图优先(ref_* 在前,作为定妆照锚定),其余按 mtime 正序(老 → 新,新生成的追加到末尾)
    # 这样文件名编号(scene_X_1, _2, _3)和视觉顺序一致,不会"夹"在中间
    files.sort(key=lambda x: (not x["filename"].startswith("ref_"), __import__("os").stat(target_dir / x["filename"]).st_mtime))
    return files

def delete_uploaded_asset(
    filename: str,
    poi_id: str,
    asset_kind: str,
    city: str = "munich",
) -> dict:
    """
    删除某个 POI 的某类已上传资源文件。

    Args:
        filename: 要删除的文件名(如 ref_X.png 或 scene_X_1.png)
        poi_id: POI ID
        asset_kind: "scene_main" | "icon"
        city: 城市名

    Returns:
        {"deleted": True, "filename": "..."}
    """
    if asset_kind == "scene_main":
        target_dir = ASSETS_ROOT / "scenes" / city / poi_id / "_reference"
    elif asset_kind == "icon":
        target_dir = ASSETS_ROOT / "icons" / city
    elif asset_kind in ("npc_head", "npc_half"):
        target_dir = ASSETS_ROOT / "characters" / city / f"npc_{poi_id}"
    else:
        raise ValueError(f"unsupported asset_kind: {asset_kind}")

    target = target_dir / filename
    if not target.exists():
        raise FileNotFoundError(f"{filename} 不存在")

    # 安全检查:filename 不能包含路径分隔符(防止 ../ 越权)
    if "/" in filename or "\\" in filename or filename.startswith("."):
        raise ValueError("invalid filename")

    target.unlink()
    return {"deleted": True, "filename": filename}
