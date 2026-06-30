"""
Phase 2: 运行时 CityBundle 导出器

职责:
- 从 SQLite 读 POIs/NPCs/Dialogues/Quests/KnowledgeCards
- 把 file_path 转换成浏览器可访问的 URL(/assets/...)
- Pydantic 校验(单字段 + 跨字段一致性)
- 生成稳定的 contentVersion(基于 DB 数据的 SHA256)
- 生成 ETag(供 HTTP 304 协商)

设计原则:
- 单 city_id 为单位,支持未来多城市
- 不写文件 — 返回 ExportResult,让调用方(router / CLI)决定怎么持久化
- 失败抛 ExportError(router 转 HTTP 500)
- 复用 schemas/game_content.py 的 CityBundle 作为 single source of truth

CLI 用法:
    python -m poi_generator.services.runtime_export_service munich
    # 输出: JSON to stdout, contentVersion + ETag 到 stderr
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ..schemas.game_content import (
    CITY_BUNDLE_SCHEMA_VERSION,
    CityBundle,
    DialogueChoice,
    DialogueNode,
    LocalizedText,
    PoiAudioUrls,
    Position,
    QuestReward,
    RuntimeDialogue,
    RuntimeKnowledgeCard,
    RuntimeNpc,
    RuntimePoi,
    RuntimeQuest,
)

# ── 常量 ──
CITY_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
ETAG_PATTERN = re.compile(r"^[a-f0-9]{8,64}$")


class ExportError(Exception):
    """导出过程中任何不可恢复错误 → router 转 HTTP 500"""


# ── 结果 ──
@dataclass
class ExportResult:
    """一次完整导出"""
    bundle: CityBundle
    """已 Pydantic 验证的 CityBundle"""
    content_version: str
    """semver '1.YYYY.MMDD-{short_hash}',稳定 + 时间相关"""
    etag: str
    """基于 (contentVersion + canonical_json) 的 SHA256,用于 HTTP 304"""
    generated_at: datetime
    """导出时间,UTC"""
    stats: Dict[str, int]
    """导出统计:{pois: 3, npcs: 0, ...},便于日志 + 调试"""


# ── 内部辅助 ──
def _validate_city_id(city_id: str) -> str:
    """防注入 + 路径穿越"""
    if not city_id or not CITY_ID_PATTERN.match(city_id):
        raise ExportError(
            f"city_id 不合法: {city_id!r}(必须 ^[a-z][a-z0-9_]*$)"
        )
    return city_id


def _file_path_to_url(file_path: Optional[str]) -> Optional[str]:
    """磁盘路径 → 浏览器可访问 URL
    规则:
      - 空 → 空
      - 已经是 /assets/... 开头 → 保留
      - 已经是绝对 URL(http/https)→ 保留
      - 包含磁盘路径(/Users/... 或 /Volumes/...)→ 拒绝(防止泄漏)
      - 相对路径 → 补前缀 '/'
    """
    if not file_path:
        return None
    s = file_path.strip()
    if not s:
        return None
    # 已合法 URL / 路径
    if s.startswith("/assets/"):
        return s
    if s.startswith("http://") or s.startswith("https://"):
        return s
    # 磁盘路径(脱敏失败 → 抛错而不是返回)
    if (
        s.startswith("/Users/")
        or s.startswith("/Volumes/")
        or s.startswith("/tmp/")
        or s.startswith("/private/")
        or s.startswith("/home/")
    ):
        raise ExportError(
            f"file_path 是磁盘路径,不允许出现在 runtime bundle: {s!r}"
        )
    # 相对路径 → 加 /
    if not s.startswith("/"):
        s = "/" + s
    return s


def _compute_content_version(
    conn: sqlite3.Connection, city_id: str
) -> str:
    """
    稳定 + 时间相关的版本号

    策略:
      - 取所有 published 内容的 (id, updated_at) 拼接(去掉时间秒级精度)
      - sha256 → 取前 8 hex
      - 格式: "1.YYYY.MMDD-{short_hash}"
        - "1." 是 schemaVersion(CityBundle JSON 格式版本,不变)
        - "YYYY.MMDD" 让运维/QA 一眼看出发布日
        - "-{short_hash}" 让内容微变也能感知

    优点:
      - 同一份数据 → 同一 contentVersion(浏览器可缓存)
      - 任何 published 内容变更 → contentVersion 变化(强制客户端重新拉)
      - 不需要单独的 "versions" 表
    """
    rows: List[str] = []

    # pois
    for r in conn.execute(
        "SELECT id, updated_at FROM pois "
        "WHERE is_published = 1 AND city = ? ORDER BY id",
        (city_id,),
    ):
        # 截到分钟级(秒级更新会让 cache 失效太频繁)
        ts = (r["updated_at"] or "")[:16]
        rows.append(f"poi:{r['id']}@{ts}")

    # poi_scenes
    for r in conn.execute(
        "SELECT poi_id, id, created_at FROM poi_scenes "
        "WHERE city = ? ORDER BY poi_id, id",
        (city_id,),
    ):
        ts = (r["created_at"] or "")[:16]
        rows.append(f"scene:{r['id']}@{ts}")

    # poi_content (任意 content_type)
    for r in conn.execute(
        "SELECT id, poi_id, content_type, version, created_at FROM poi_content "
        "WHERE city = ? ORDER BY id",
        (city_id,),
    ):
        ts = (r["created_at"] or "")[:16]
        rows.append(
            f"content:{r['id']}@{r['content_type']}v{r['version']}@{ts}"
        )

    if not rows:
        # 空城市也要给一个 contentVersion(基于 city_id)
        rows = [f"empty:{city_id}"]

    blob = "\n".join(rows).encode("utf-8")
    # 严格 semver "X.Y.Z" 格式(三个 . 分隔的数字段),Z 段用 hash 转十进制
    # 这样符合 schemas/game_content.py CityBundle.contentVersion 的 pattern=^\d+\.\d+\.\d+$
    digest_int = int(hashlib.sha256(blob).hexdigest()[:8], 16) % 100_000_000
    today_int = int(datetime.now(timezone.utc).strftime("%Y%m%d"))  # e.g. 20260630
    return f"1.{today_int}.{digest_int:08d}"


def _compute_etag(bundle_dict: Dict) -> str:
    """基于 (contentVersion + canonical JSON,排除 generatedAt) 的 SHA256,带 W/ 前缀

    排除 generatedAt:它是导出时刻的时间戳,每次重导都会变,但不应该让客户端缓存失效。
    ETag 应该反映"内容是否变了" — contentVersion 已经是内容的稳定标识,这里再冗余校验一次。
    """
    # sort_keys + ensure_ascii=False + separators 让 hash 稳定
    payload = {k: v for k, v in bundle_dict.items() if k != "generatedAt"}
    canonical = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f'W/"{digest}"'


# ── 核心:从 SQLite 读 POIs ──
def _load_pois(
    conn: sqlite3.Connection, city_id: str
) -> List[RuntimePoi]:
    """读 published POIs + 聚合 sceneUrls / audioUrls"""
    pois: List[RuntimePoi] = []
    for r in conn.execute(
        "SELECT id, name_de, name_zh, type, lat, lng, icon "
        "FROM pois WHERE is_published = 1 AND city = ? ORDER BY id",
        (city_id,),
    ):
        if not r["name_de"] or not r["name_zh"]:
            # 必有 de/zh,name 缺一不可
            raise ExportError(
                f"POI {r['id']!r} 缺 name_de 或 name_zh,无法导出"
            )
        poi = RuntimePoi(
            id=r["id"],
            city=city_id,
            type=r["type"],
            name=LocalizedText(de=r["name_de"], zh=r["name_zh"]),
            position=Position(lat=r["lat"], lng=r["lng"]),
            icon=r["icon"] or "📍",
        )
        pois.append(poi)

    # 聚合 sceneUrls (只取 _reference 当主图)
    for r in conn.execute(
        "SELECT poi_id, scene_type, url_path FROM poi_scenes "
        "WHERE city = ? AND scene_type = '_reference' ORDER BY poi_id, sort_order",
        (city_id,),
    ):
        poi = next((p for p in pois if p.id == r["poi_id"]), None)
        if poi is None:
            continue
        url = _file_path_to_url(r["url_path"])
        if url and url not in poi.sceneUrls:
            poi.sceneUrls.append(url)

    # 聚合 audioUrls (从 poi_content.data 提取)
    for r in conn.execute(
        "SELECT poi_id, data FROM poi_content "
        "WHERE city = ? AND content_type = 'info'",
        (city_id,),
    ):
        poi = next((p for p in pois if p.id == r["poi_id"]), None)
        if poi is None:
            continue
        try:
            data = json.loads(r["data"]) if r["data"] else {}
        except json.JSONDecodeError:
            continue
        audio = data.get("audio") or {}
        for lang in ("de", "zh", "en"):
            url = audio.get(lang, {}).get("url")
            url = _file_path_to_url(url) if url else None
            if url:
                setattr(poi.audioUrls, lang, url)

    return pois


def _load_npcs(
    conn: sqlite3.Connection, city_id: str, valid_poi_ids: set
) -> List[RuntimeNpc]:
    """读 NPCs(Phase 2 数据库还没建,返回空列表)"""
    # 未来实现:从 poi_content WHERE content_type='npc' 读 JSON
    return []


def _load_dialogues(
    conn: sqlite3.Connection, city_id: str, valid_npc_ids: set
) -> List[RuntimeDialogue]:
    """读 Dialogues(Phase 2 数据库还没建,返回空列表)"""
    return []


def _load_quests(
    conn: sqlite3.Connection, city_id: str, valid_poi_ids: set
) -> List[RuntimeQuest]:
    """读 Quests(Phase 2 数据库还没建,返回空列表)"""
    return []


def _load_knowledge_cards(
    conn: sqlite3.Connection, city_id: str
) -> List[RuntimeKnowledgeCard]:
    """读 KnowledgeCards(Phase 2 数据库还没建,返回空列表)"""
    return []


# ── 主入口 ──
def export_city(city_id: str, conn: sqlite3.Connection) -> ExportResult:
    """
    从 SQLite 导出 CityBundle(完整流程)

    Raises:
        ExportError: city_id 非法 / 数据损坏 / 校验失败
    """
    city_id = _validate_city_id(city_id)

    # 1. 读 POIs
    pois = _load_pois(conn, city_id)
    valid_poi_ids = {p.id for p in pois}

    # 2. 读 NPCs/Dialogues/Quests/KnowledgeCards
    npcs = _load_npcs(conn, city_id, valid_poi_ids)
    valid_npc_ids = {n.id for n in npcs}
    dialogues = _load_dialogues(conn, city_id, valid_npc_ids)
    quests = _load_quests(conn, city_id, valid_poi_ids)
    knowledge_cards = _load_knowledge_cards(conn, city_id)

    # 3. 算 contentVersion(在打包前,这样 hash 反映"原始数据状态")
    content_version = _compute_content_version(conn, city_id)

    # 4. 组装 CityBundle(Pydantic 校验 + 跨字段一致性)
    now = datetime.now(timezone.utc)
    try:
        bundle = CityBundle(
            schemaVersion=CITY_BUNDLE_SCHEMA_VERSION,
            contentVersion=content_version,
            city=city_id,
            generatedAt=now,
            pois=pois,
            npcs=npcs,
            dialogues=dialogues,
            quests=quests,
            knowledgeCards=knowledge_cards,
        )
    except ValueError as e:
        raise ExportError(f"CityBundle Pydantic 校验失败: {e}") from e

    # 5. 算 ETag
    bundle_dict = bundle.to_runtime_json()
    etag = _compute_etag(bundle_dict)

    return ExportResult(
        bundle=bundle,
        content_version=content_version,
        etag=etag,
        generated_at=now,
        stats={
            "pois": len(pois),
            "npcs": len(npcs),
            "dialogues": len(dialogues),
            "quests": len(quests),
            "knowledgeCards": len(knowledge_cards),
        },
    )


# ── CLI ──
def main() -> int:
    """CLI: python -m poi_generator.services.runtime_export_service <city_id>"""
    if len(sys.argv) != 2:
        print(
            "用法: python -m poi_generator.services.runtime_export_service <city_id>",
            file=sys.stderr,
        )
        return 2

    city_id = sys.argv[1]

    # 默认 DB 路径(可在 POI_DB_PATH 环境变量覆盖)
    db_path = Path(
        Path(__file__).resolve().parents[2] / "game_data.db"
    )
    if not db_path.exists():
        print(f"DB 不存在: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        result = export_city(city_id, conn)
    except ExportError as e:
        print(f"导出失败: {e}", file=sys.stderr)
        return 1

    # stdout: 完整 bundle JSON(便于 jq 处理 / 重定向到文件)
    bundle_dict = result.bundle.to_runtime_json()
    print(json.dumps(bundle_dict, ensure_ascii=False, indent=2))

    # stderr: 元信息(便于日志追踪)
    print(
        f"\n--- meta: city={city_id} contentVersion={result.content_version} "
        f"etag={result.etag} stats={result.stats}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())