"""
游戏数据 SQLite 数据库服务
管理所有 POI 数据、场景图片、导出内容的持久化存储和查询。

数据库位置: backend/poi-generator/game_data.db
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import DB_PATH

# ── Schema ──

SCHEMA_SQL = """
-- pois: POI 基础信息
CREATE TABLE IF NOT EXISTS pois (
    id          TEXT PRIMARY KEY,
    city        TEXT NOT NULL DEFAULT 'munich',
    name_de     TEXT,
    name_zh     TEXT,
    type        TEXT,              -- church, school, home, shop, market, castle, museum, park, library, landmark, etc.
    lat         REAL,
    lng         REAL,
    icon        TEXT,              -- emoji icon
    walk_minutes INTEGER,
    cost        TEXT,
    ubahn       TEXT,
    description TEXT,              -- 中文描述
    acts        TEXT,              -- JSON array of action buttons
    unlocked    INTEGER DEFAULT 0,
    is_published INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

-- poi_scenes: 场景图片路径（一对多）
CREATE TABLE IF NOT EXISTS poi_scenes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    poi_id      TEXT NOT NULL REFERENCES pois(id),
    city        TEXT NOT NULL DEFAULT 'munich',
    scene_type  TEXT,              -- exterior, interior, tower, _thumbnails
    variant     TEXT,              -- spring, summer, night, altar, etc.
    url_path    TEXT NOT NULL,     -- 浏览器可访问的 URL 路径
    file_path   TEXT,              -- 磁盘路径
    sort_order  INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- poi_content: 各模块导出内容，每次导出一个版本
CREATE TABLE IF NOT EXISTS poi_content (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    poi_id       TEXT NOT NULL REFERENCES pois(id),
    city         TEXT NOT NULL DEFAULT 'munich',
    content_type TEXT NOT NULL,    -- info, npc, dialogue, knowledge, quest, checkin
    data         TEXT,             -- JSON blob
    export_batch TEXT,             -- date suffix batch id
    file_path    TEXT,
    version      INTEGER DEFAULT 1,
    created_at   TEXT DEFAULT (datetime('now'))
);

-- export_logs: 导出历史
CREATE TABLE IF NOT EXISTS export_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    poi_id        TEXT NOT NULL,
    city          TEXT DEFAULT 'munich',
    batch_id      TEXT,
    file_count    INTEGER DEFAULT 0,
    content_types TEXT,            -- JSON array of ['npc','dialogue',...]
    created_at    TEXT DEFAULT (datetime('now'))
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_pois_city ON pois(city);
CREATE INDEX IF NOT EXISTS idx_pois_type ON pois(type);
CREATE INDEX IF NOT EXISTS idx_pois_published ON pois(is_published);
CREATE INDEX IF NOT EXISTS idx_poi_scenes_poi ON poi_scenes(poi_id);
CREATE INDEX IF NOT EXISTS idx_poi_content_poi ON poi_content(poi_id);
CREATE INDEX IF NOT EXISTS idx_poi_content_type ON poi_content(content_type);
"""


# ── 连接管理 ──

def get_conn() -> sqlite3.Connection:
    """获取数据库连接（每次调用创建新连接，线程安全）"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")    # 性能优化
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库 schema（幂等）"""
    conn = get_conn()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


# ── POI CRUD ──

def upsert_poi(
    poi_id: str,
    city: str = "munich",
    name_de: str = None,
    name_zh: str = None,
    type_: str = None,
    lat: float = None,
    lng: float = None,
    icon: str = None,
    walk_minutes: int = None,
    cost: str = None,
    ubahn: str = None,
    description: str = None,
    acts: list = None,
    unlocked: bool = False,
    is_published: bool = False,
) -> dict:
    """插入或更新一个 POI"""
    data = {
        "id": poi_id,
        "city": city,
        "name_de": name_de,
        "name_zh": name_zh,
        "type": type_,
        "lat": lat,
        "lng": lng,
        "icon": icon,
        "walk_minutes": walk_minutes,
        "cost": cost,
        "ubahn": ubahn,
        "description": description,
        "acts": json.dumps(acts, ensure_ascii=False) if acts else None,
        "unlocked": 1 if unlocked else 0,
        "is_published": 1 if is_published else 0,
        "updated_at": datetime.now().isoformat(),
    }

    sql = """
        INSERT INTO pois (id, city, name_de, name_zh, type, lat, lng, icon,
                          walk_minutes, cost, ubahn, description, acts,
                          unlocked, is_published, updated_at)
        VALUES (:id, :city, :name_de, :name_zh, :type, :lat, :lng, :icon,
                :walk_minutes, :cost, :ubahn, :description, :acts,
                :unlocked, :is_published, :updated_at)
        ON CONFLICT(id) DO UPDATE SET
            city=excluded.city, name_de=excluded.name_de, name_zh=excluded.name_zh,
            type=excluded.type, lat=excluded.lat, lng=excluded.lng,
            icon=excluded.icon, walk_minutes=excluded.walk_minutes,
            cost=excluded.cost, ubahn=excluded.ubahn,
            description=excluded.description, acts=excluded.acts,
            unlocked=excluded.unlocked, is_published=excluded.is_published,
            updated_at=excluded.updated_at
    """
    conn = get_conn()
    try:
        conn.execute(sql, data)
        conn.commit()
        return {"poi_id": poi_id, "action": "upserted"}
    finally:
        conn.close()


def list_pois(
    city: str = "munich",
    type_: str = None,
    published_only: bool = True,
) -> list[dict]:
    """列出 POI，支持按城市/类型过滤"""
    sql = "SELECT * FROM pois WHERE city = :city"
    params = {"city": city}

    if type_:
        sql += " AND type = :type"
        params["type"] = type_

    if published_only:
        sql += " AND is_published = 1"

    sql += " ORDER BY type, id"

    conn = get_conn()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_poi(r) for r in rows]
    finally:
        conn.close()


def get_poi(poi_id: str, city: str = "munich") -> Optional[dict]:
    """获取单个 POI"""
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM pois WHERE id = ? AND city = ?",
            (poi_id, city),
        ).fetchone()
        if not row:
            return None
        poi = _row_to_poi(row)
        # 附带场景图片和内容版本信息
        poi["scenes"] = list_scenes(poi_id, city)
        poi["content_types"] = list_content_types(poi_id, city)
        return poi
    finally:
        conn.close()


def delete_poi(poi_id: str, city: str = "munich"):
    """删除 POI 及其关联数据"""
    conn = get_conn()
    try:
        conn.execute("DELETE FROM poi_scenes WHERE poi_id = ? AND city = ?", (poi_id, city))
        conn.execute("DELETE FROM poi_content WHERE poi_id = ? AND city = ?", (poi_id, city))
        conn.execute("DELETE FROM export_logs WHERE poi_id = ? AND city = ?", (poi_id, city))
        conn.execute("DELETE FROM pois WHERE id = ? AND city = ?", (poi_id, city))
        conn.commit()
    finally:
        conn.close()


# ── 场景图片 ──

def add_scene(
    poi_id: str,
    city: str,
    url_path: str,
    scene_type: str = None,
    variant: str = None,
    file_path: str = None,
    sort_order: int = 0,
):
    """覆盖式写入场景图片(同 poi_id+scene_type+variant 只留最新)

    场景图重新生成时 URL 路径不变,只是覆盖;避免重复发布后 poi_scenes
    表里同一条图片有多行。
    """
    conn = get_conn()
    try:
        # 删同 (poi_id, city, scene_type, variant) 的旧行
        # 用 COALESCE 处理 NULL(NULL 在 SQLite unique 索引里视为不同)
        if scene_type is None and variant is None:
            conn.execute(
                "DELETE FROM poi_scenes WHERE poi_id=? AND city=? AND scene_type IS NULL AND variant IS NULL",
                (poi_id, city),
            )
        elif scene_type is None:
            conn.execute(
                "DELETE FROM poi_scenes WHERE poi_id=? AND city=? AND scene_type IS NULL AND variant=?",
                (poi_id, city, variant),
            )
        elif variant is None:
            conn.execute(
                "DELETE FROM poi_scenes WHERE poi_id=? AND city=? AND scene_type=? AND variant IS NULL",
                (poi_id, city, scene_type),
            )
        else:
            conn.execute(
                "DELETE FROM poi_scenes WHERE poi_id=? AND city=? AND scene_type=? AND variant=?",
                (poi_id, city, scene_type, variant),
            )
        conn.execute(
            """INSERT INTO poi_scenes (poi_id, city, scene_type, variant, url_path, file_path, sort_order)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (poi_id, city, scene_type, variant, url_path, file_path, sort_order),
        )
        conn.commit()
    finally:
        conn.close()


def list_scenes(poi_id: str, city: str = "munich") -> list[dict]:
    """列出 POI 的场景图片，按 type, sort_order 排序"""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM poi_scenes WHERE poi_id = ? AND city = ? ORDER BY scene_type, sort_order, id",
            (poi_id, city),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── 导出内容 ──

def add_content(
    poi_id: str,
    city: str,
    content_type: str,
    data: dict | list,
    export_batch: str = None,
    file_path: str = None,
):
    """覆盖式写入导出内容(同一 poi_id+content_type 只保留最新一份)

    之前用 INSERT + version+1,会导致每次发布都累积一行。
    改为 DELETE 旧的 + INSERT 新的(版本号重置 1),符合 '发布即覆盖' 语义。
    """
    conn = get_conn()
    try:
        # 同 (poi_id, city, content_type) 的旧记录全部删掉
        conn.execute(
            "DELETE FROM poi_content WHERE poi_id=? AND city=? AND content_type=?",
            (poi_id, city, content_type),
        )
        # 插新的,version=1
        conn.execute(
            """INSERT INTO poi_content (poi_id, city, content_type, data, export_batch, file_path, version)
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (poi_id, city, content_type, json.dumps(data, ensure_ascii=False),
             export_batch, file_path),
        )
        conn.commit()
    finally:
        conn.close()


def list_content_types(poi_id: str, city: str = "munich") -> list[str]:
    """列出 POI 已有的内容类型"""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT DISTINCT content_type FROM poi_content WHERE poi_id=? AND city=?",
            (poi_id, city),
        ).fetchall()
        return [r["content_type"] for r in rows]
    finally:
        conn.close()


def get_latest_content(poi_id: str, city: str = "munich") -> dict:
    """获取 POI 所有类型的最新版本内容"""
    types = list_content_types(poi_id, city)
    result = {}
    conn = get_conn()
    try:
        for ct in types:
            row = conn.execute(
                "SELECT data FROM poi_content WHERE poi_id=? AND city=? AND content_type=? ORDER BY version DESC LIMIT 1",
                (poi_id, city, ct),
            ).fetchone()
            if row:
                try:
                    result[ct] = json.loads(row["data"])
                except (json.JSONDecodeError, TypeError):
                    result[ct] = row["data"]
    finally:
        conn.close()
    return result


# ── 导出日志 ──

def log_export(
    poi_id: str,
    city: str,
    batch_id: str,
    file_count: int,
    content_types: list[str],
):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO export_logs (poi_id, city, batch_id, file_count, content_types)
               VALUES (?, ?, ?, ?, ?)""",
            (poi_id, city, batch_id, file_count, json.dumps(content_types)),
        )
        conn.commit()
    finally:
        conn.close()


# ── 辅助 ──

def _row_to_poi(row: sqlite3.Row) -> dict:
    """将 SQLite row 转为前端兼容的 POI dict"""
    d = dict(row)
    # 将 acts JSON 字符串解析回数组
    if isinstance(d.get("acts"), str):
        try:
            d["acts"] = json.loads(d["acts"])
        except (json.JSONDecodeError, TypeError):
            d["acts"] = []
    # 加前端友好别名
    d["name"] = d.pop("name_zh", "")
    d["t"] = d.pop("type", "")
    d["walk"] = d.pop("walk_minutes", None)
    d["d"] = d.pop("description", "")
    d["de"] = d.pop("name_de", "")
    # 只保留前端需要的字段
    frontend_fields = ["id", "name", "de", "t", "lat", "lng", "icon",
                       "walk", "cost", "ubahn", "d", "acts", "unlocked",
                       "is_published", "city"]
    filtered = {k: d.get(k) for k in frontend_fields if k in d}
    # 补充 imgs 字段（后续由 API 填充）
    filtered["imgs"] = []
    return filtered
