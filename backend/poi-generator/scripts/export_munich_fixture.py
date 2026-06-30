"""
Phase 0 一次性工具: 从现有 SQLite 数据导出 Munich fixture

用法:
    cd /Volumes/NewDisk/GermanLearning/backend
    python -m poi-generator.scripts.export_munich_fixture

输出:
    frontend/game-client/src/test/fixtures/munich-bundle.json

注意:
- 这是 **Phase 0 的临时脚手架**,只用于生成测试 fixture
- **生产环境必须用 runtime_export_service.py** (Phase 2),包含脱敏、URL 转换、稳定性版本号
- 当前 fixture 还很薄(npcs/dialogues/quests/knowledgeCards 都空,因为数据库里没有)
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path("/Volumes/NewDisk/GermanLearning")
DB_PATH = PROJECT_ROOT / "backend/poi-generator/game_data.db"
FIXTURE_PATH = PROJECT_ROOT / "frontend/game-client/src/test/fixtures/munich-bundle.json"

CONTENT_VERSION = "0.1.0"  # Phase 0 初始版本,任何 schema 变更 + minor


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # ── 1. POIs (只取已发布) ──
    pois = []
    poi_id_to_icon = {}  # BUILTIN_POIS emoji 备份(数据库 icon 字段是 emoji)
    for r in conn.execute(
        "SELECT id, name_de, name_zh, type, lat, lng, icon FROM pois "
        "WHERE is_published = 1 ORDER BY id"
    ):
        poi = {
            "id": r["id"],
            "city": "munich",
            "type": r["type"],
            "name": {"de": r["name_de"], "zh": r["name_zh"]},
            "position": {"lat": r["lat"], "lng": r["lng"]},
            "icon": r["icon"] or "📍",
            "sceneUrls": [],
            "audioUrls": {},
            "questIds": [],
            "npcIds": [],
        }
        poi_id_to_icon[r["id"]] = r["icon"] or "📍"
        pois.append(poi)

    # ── 2. 场景图 (按 POI 聚合) ──
    for r in conn.execute(
        "SELECT poi_id, scene_type, variant, url_path, sort_order "
        "FROM poi_scenes ORDER BY poi_id, sort_order"
    ):
        poi = next((p for p in pois if p["id"] == r["poi_id"]), None)
        if poi is None:
            continue
        # 只把 _reference 当作主场景图加入 sceneUrls(完整 exterior/interior 等 Phase 3+ 加入)
        if r["scene_type"] == "_reference":
            url = r["url_path"]
            # 兼容 /assets/... 路径(已是 runtime URL,直接用)
            if not url.startswith("/"):
                url = "/" + url
            poi["sceneUrls"].append(url)

    # ── 3. audio URLs (从 poi_content.data 提取) ──
    for r in conn.execute(
        "SELECT poi_id, data FROM poi_content WHERE content_type = 'info'"
    ):
        poi = next((p for p in pois if p["id"] == r["poi_id"]), None)
        if poi is None:
            continue
        try:
            data = json.loads(r["data"])
        except (json.JSONDecodeError, TypeError):
            continue
        audio = data.get("audio") or {}
        for lang in ("de", "zh", "en"):
            url = audio.get(lang, {}).get("url")
            if url:
                # 验证文件存在,不存在则不发
                rel = url.lstrip("/")
                if (PROJECT_ROOT / rel).exists():
                    poi["audioUrls"][lang] = url

    # ── 4. published: true 必填字段 ──
    for p in pois:
        p["published"] = True

    bundle = {
        "schemaVersion": 1,
        "contentVersion": CONTENT_VERSION,
        "city": "munich",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "pois": pois,
        "npcs": [],            # 数据库里暂无
        "dialogues": [],       # 数据库里暂无
        "quests": [],          # 数据库里暂无
        "knowledgeCards": [],  # 数据库里暂无
    }

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)
    print(f"✓ 已生成 {FIXTURE_PATH}")
    print(f"  POIs: {len(pois)}")
    print(f"  总大小: {FIXTURE_PATH.stat().st_size:,} 字节")


if __name__ == "__main__":
    main()