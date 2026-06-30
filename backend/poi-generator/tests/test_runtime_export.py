"""
Phase 2 测试 · runtime_export_service + game_content router

覆盖:
- exporter: city_id 校验 / 脱敏 / contentVersion / etag / stability / 跨字段校验
- router: list_cities / get_bundle 200/304/400/404 / response shape

运行:
    cd /Volumes/NewDisk/GermanLearning
    .venv/bin/python -m pytest backend/poi-generator/tests/test_runtime_export.py -v
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from poi_generator.config import CORS_ORIGINS
from poi_generator.routers import game_content
from poi_generator.services.runtime_export_service import (
    CITY_ID_PATTERN,
    ExportError,
    _file_path_to_url,
    export_city,
)


def _build_test_app() -> FastAPI:
    """测试专用 app: 只挂载 game_content router,避免拉 openai/dashscope 等重型依赖

    生产 app 在 backend/poi-generator/main.py,这里只测 Phase 2 新加的部分。
    """
    app = FastAPI(title="gagaToday Phase2 test app")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(game_content.router)
    return app


ROOT = Path(__file__).resolve().parents[3]  # tests → poi-generator → backend → ROOT
DB_PATH = ROOT / "backend" / "poi-generator" / "game_data.db"


# ── 夹具 ──
@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient(同步,基于 requests)"""
    return TestClient(_build_test_app())


@pytest.fixture(scope="module")
def conn():
    """共享一个 DB 连接,read-only 视角"""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


# ── exporter 测试 ──
class TestCityIdValidation:
    """export_city 拒绝任何非 ^[a-z][a-z0-9_]*$ 的 city_id"""

    @pytest.mark.parametrize("bad", [
        "", "munich-1", "MUNICH", "../etc", "1munich",
        "munich city", "munich.city", "münchen", "munich/path",
    ])
    def test_rejects_invalid_city_id(self, conn, bad):
        with pytest.raises(ExportError, match="city_id 不合法"):
            export_city(bad, conn)

    @pytest.mark.parametrize("good", ["munich", "berlin", "m", "a1", "abc_def"])
    def test_accepts_valid_city_id(self, conn, good):
        # 不抛错即可(可能空,但合法)
        export_city(good, conn)


class TestFilePathToUrl:
    """_file_path_to_url 脱敏"""

    def test_none_returns_none(self):
        assert _file_path_to_url(None) is None

    def test_empty_returns_none(self):
        assert _file_path_to_url("") is None

    def test_absolute_assets_url_passes_through(self):
        assert _file_path_to_url("/assets/maps/foo.png") == "/assets/maps/foo.png"

    def test_https_url_passes_through(self):
        url = "https://cdn.example.com/img.png"
        assert _file_path_to_url(url) == url

    def test_relative_path_gets_slash_prefix(self):
        assert _file_path_to_url("assets/img.png") == "/assets/img.png"

    @pytest.mark.parametrize("leak", [
        "/Users/hzone/leak.png",
        "/Volumes/NewDisk/leak.png",
        "/tmp/leak.png",
        "/private/var/leak.png",
    ])
    def test_disk_path_rejected(self, leak):
        with pytest.raises(ExportError, match="磁盘路径"):
            _file_path_to_url(leak)


class TestExportMunich:
    def test_returns_three_published_pois(self, conn):
        r = export_city("munich", conn)
        assert len(r.bundle.pois) == 3
        ids = {p.id for p in r.bundle.pois}
        assert ids == {"frauenkirche", "marienplatz", "munchen_hauptbahnhof"}

    def test_content_version_is_semver(self, conn):
        r = export_city("munich", conn)
        assert re.match(r"^\d+\.\d+\.\d+$", r.content_version), \
            f"contentVersion 不是 semver: {r.content_version}"

    def test_etag_is_weak_with_quote(self, conn):
        r = export_city("munich", conn)
        # 弱 ETag 格式 W/"<hex>"
        assert r.etag.startswith('W/"')
        assert r.etag.endswith('"')
        inner = r.etag[3:-1]
        assert re.match(r"^[a-f0-9]{8,32}$", inner)

    def test_etag_stable_for_same_data(self, conn):
        r1 = export_city("munich", conn)
        r2 = export_city("munich", conn)
        assert r1.etag == r2.etag

    def test_content_version_stable_for_same_data(self, conn):
        r1 = export_city("munich", conn)
        r2 = export_city("munich", conn)
        assert r1.content_version == r2.content_version

    def test_bundle_passes_pydantic_validation(self, conn):
        """导出的 bundle 必须能被自己的 CityBundle schema 重新验证"""
        r = export_city("munich", conn)
        # to_runtime_json 已经经过 Pydantic,这里再次 model_validate 应该不报错
        from poi_generator.schemas.game_content import CityBundle
        rebuilt = CityBundle.model_validate(r.bundle.to_runtime_json())
        assert rebuilt.city == "munich"
        assert len(rebuilt.pois) == 3

    def test_bundle_has_no_absolute_disk_paths(self, conn):
        """Exporte r 必须脱敏:不泄漏磁盘路径"""
        r = export_city("munich", conn)
        dumped = json.dumps(r.bundle.to_runtime_json(), ensure_ascii=False)
        for leak in ["/Users/", "/Volumes/", "/tmp/", "/private/"]:
            assert leak not in dumped, f"bundle 泄漏磁盘路径: {leak}"

    def test_stats_accurate(self, conn):
        r = export_city("munich", conn)
        assert r.stats["pois"] == 3
        assert r.stats["npcs"] == 0
        assert r.stats["dialogues"] == 0
        assert r.stats["quests"] == 0
        assert r.stats["knowledgeCards"] == 0


class TestExportUnknownCity:
    """未知城市但合法 id(为未来占位用)→ 空 bundle,但 schema 合法"""

    def test_empty_bundle_passes_validation(self, conn):
        r = export_city("berlin", conn)
        assert len(r.bundle.pois) == 0
        assert r.bundle.city == "berlin"
        assert r.stats["pois"] == 0


# ── router 测试 ──
class TestListCities:
    def test_returns_200(self, client):
        r = client.get("/api/game/v1/cities")
        assert r.status_code == 200

    def test_includes_munich(self, client):
        r = client.get("/api/game/v1/cities")
        data = r.json()
        ids = [c["id"] for c in data["cities"]]
        assert "munich" in ids

    def test_city_has_required_metadata(self, client):
        r = client.get("/api/game/v1/cities")
        munich = next(c for c in r.json()["cities"] if c["id"] == "munich")
        # 必备字段
        for key in ("id", "displayName", "country", "center", "zoom", "bbox", "pmtilesUrl", "available"):
            assert key in munich, f"munich 缺字段: {key}"
        assert munich["country"] == "DE"
        assert len(munich["center"]) == 2
        assert len(munich["bbox"]) == 4


class TestGetCityBundle:
    def test_200_with_etag_and_content_version_header(self, client):
        r = client.get("/api/game/v1/cities/munich/bundle")
        assert r.status_code == 200
        assert "etag" in r.headers
        assert "x-content-version" in r.headers
        # body 是 CityBundle
        data = r.json()
        assert data["schemaVersion"] == 1
        assert data["city"] == "munich"
        assert len(data["pois"]) == 3

    def test_304_on_if_none_match_match(self, client):
        """带匹配的 If-None-Match → 304 空 body"""
        r1 = client.get("/api/game/v1/cities/munich/bundle")
        etag = r1.headers["etag"]
        r2 = client.get(
            "/api/game/v1/cities/munich/bundle",
            headers={"If-None-Match": etag},
        )
        assert r2.status_code == 304
        # 304 body 必须空
        assert r2.content == b""

    def test_400_on_invalid_city_id(self, client):
        r = client.get("/api/game/v1/cities/MUNICH/bundle")
        assert r.status_code == 400
        assert "city_id 不合法" in r.text or "不合法" in r.text

    def test_404_on_unknown_city(self, client):
        # 合法 id 但不在 registry
        r = client.get("/api/game/v1/cities/berlin/bundle")
        assert r.status_code == 404

    def test_response_matches_zod_schema_fields(self, client):
        """返回的字段名必须是前端 Zod 期望的 camelCase"""
        r = client.get("/api/game/v1/cities/munich/bundle")
        data = r.json()
        # CityBundle 顶层
        for key in ("schemaVersion", "contentVersion", "city", "generatedAt", "pois"):
            assert key in data, f"CityBundle 缺字段: {key}"
        # POI
        poi = data["pois"][0]
        for key in ("id", "city", "type", "name", "position", "icon", "sceneUrls", "audioUrls"):
            assert key in poi, f"POI 缺字段: {key}"
        # audioUrls 三语
        for lang in ("de", "zh", "en"):
            assert lang in poi["audioUrls"]