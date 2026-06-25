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

    import shutil
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
    保存一组 POI 相关 JSON 文件到草稿目录

    Args:
        files: [{"relative_path": "poi_info.draft.json", "data": {...}}, ...]
        city: 城市名
        poi_id: POI ID
        date_suffix: 可选日期后缀，用于避免覆盖并体现批次
        source_records: optional list of source records
        is_draft: 是否保存为草稿

    Returns:
        {"saved_files": [...], "source_path": ...}
    """
    if not poi_id:
        raise ValueError("poi_id is required for save_poi_package")

    if date_suffix is None:
        date_suffix = datetime.now().strftime("%Y%m%d")

    package_dir = CONTENT_DRAFTS_ROOT / f"{city}_{poi_id}_{date_suffix}"
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
