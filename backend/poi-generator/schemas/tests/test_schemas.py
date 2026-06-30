"""
Phase 0 schema 验证测试 — Python 端

测试 PoI / Bundle / 跨字段一致性 / 边界情况
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_PATH = (
    PROJECT_ROOT
    / "frontend"
    / "game-client"
    / "src"
    / "test"
    / "fixtures"
    / "munich-bundle.json"
)

from poi_generator.schemas.game_content import (  # noqa: E402
    CityBundle,
    LocalizedText,
    POI_TYPE_VALUES,
    Position,
    RuntimePoi,
)
from poi_generator.schemas.save import PlayerState, PLAYER_STATE_SCHEMA_VERSION  # noqa: E402


def load_fixture() -> dict:
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate_bundle(bundle_dict: dict):
    """pydantic v1/v2 兼容的校验入口"""
    if hasattr(CityBundle, "model_validate"):
        return CityBundle.model_validate(bundle_dict)
    return CityBundle(**bundle_dict)


# ── 基础 DTO ──
class TestLocalizedText:
    def test_requires_de_and_zh(self):
        with pytest.raises(Exception):
            LocalizedText(de="", zh="中")
        with pytest.raises(Exception):
            LocalizedText(de="de")  # type: ignore[call-arg]
        ok = LocalizedText(de="de", zh="中", en="en")
        assert ok.en == "en"


class TestPosition:
    def test_valid_position(self):
        p = Position(lat=48.1374, lng=11.5755)
        assert p.lat == 48.1374

    def test_rejects_invalid_latitude(self):
        with pytest.raises(Exception):
            Position(lat=120, lng=11)
        with pytest.raises(Exception):
            Position(lat=-91, lng=11)

    def test_rejects_invalid_longitude(self):
        with pytest.raises(Exception):
            Position(lat=48, lng=200)


class TestRuntimePoi:
    @pytest.fixture
    def valid_poi(self):
        return {
            "id": "frauenkirche",
            "city": "munich",
            "type": "church",
            "name": {"de": "Frauenkirche", "zh": "圣母教堂"},
            "position": {"lat": 48.1385, "lng": 11.5737},
            "icon": "⛪",
        }

    def test_valid_poi(self, valid_poi):
        p = RuntimePoi(**valid_poi)
        assert p.id == "frauenkirche"
        assert p.published is True  # 默认值

    def test_rejects_uppercase_id(self, valid_poi):
        valid_poi["id"] = "Frauenkirche"
        with pytest.raises(Exception):
            RuntimePoi(**valid_poi)

    def test_rejects_unknown_type(self, valid_poi):
        valid_poi["type"] = "unknown_type_xyz"
        with pytest.raises(Exception):
            RuntimePoi(**valid_poi)

    def test_accepts_all_poi_types(self, valid_poi):
        for t in POI_TYPE_VALUES:
            valid_poi["type"] = t
            p = RuntimePoi(**valid_poi)
            assert p.type == t


# ── City Bundle (核心) ──
class TestCityBundle:
    def test_accepts_fixture(self):
        """Phase 0 验收:fixture 必须通过 Pydantic 验证"""
        bundle_dict = load_fixture()
        bundle = validate_bundle(bundle_dict)
        assert bundle.city == "munich"
        assert len(bundle.pois) >= 3
        assert bundle.schemaVersion == 1

    def test_rejects_invalid_latitude_in_poi(self):
        bundle_dict = load_fixture()
        bundle_dict["pois"][0]["position"]["lat"] = 120
        with pytest.raises(Exception):
            validate_bundle(bundle_dict)

    def test_rejects_wrong_schema_version(self):
        bundle_dict = load_fixture()
        bundle_dict["schemaVersion"] = 999
        with pytest.raises(Exception):
            validate_bundle(bundle_dict)

    def test_rejects_bad_content_version(self):
        bundle_dict = load_fixture()
        bundle_dict["contentVersion"] = "not-semver"
        with pytest.raises(Exception):
            validate_bundle(bundle_dict)

    def test_rejects_quest_referencing_missing_poi(self):
        bundle_dict = load_fixture()
        bundle_dict["quests"] = [{
            "id": "q_test",
            "title": {"de": "Test", "zh": "测试"},
            "poiId": "nonexistent_poi",
            "dialogueIds": [],
            "prerequisites": [],
            "reward": {},
            "published": True,
        }]
        with pytest.raises(Exception, match="Quest q_test"):
            validate_bundle(bundle_dict)

    def test_rejects_dialogue_referencing_missing_npc(self):
        bundle_dict = load_fixture()
        bundle_dict["dialogues"] = [{
            "id": "d_test",
            "npcId": "nonexistent_npc",
            "startNodeId": "start",
            "nodes": [{
                "id": "start",
                "npcText": {"de": "Hallo", "zh": "你好"},
                "choices": [],
                "terminal": True,
                "result": "success",
            }],
            "published": True,
        }]
        with pytest.raises(Exception, match="Dialogue d_test"):
            validate_bundle(bundle_dict)

    def test_rejects_dialogue_with_unresolvable_start_node(self):
        bundle_dict = load_fixture()
        bundle_dict["dialogues"] = [{
            "id": "d_test",
            "npcId": "npc_test",
            "startNodeId": "ghost_start",  # 不存在
            "nodes": [{
                "id": "start",
                "npcText": {"de": "Hallo", "zh": "你好"},
                "choices": [],
                "terminal": True,
            }],
            "published": True,
        }]
        bundle_dict["npcs"] = [{
            "id": "npc_test",
            "poiId": bundle_dict["pois"][0]["id"],
            "name": {"de": "NPC", "zh": "NPC"},
            "published": True,
        }]
        with pytest.raises(Exception, match="startNodeId"):
            validate_bundle(bundle_dict)

    def test_fixture_has_no_absolute_paths_or_keys(self):
        """Exporte r 必须脱敏:不泄漏磁盘路径 / 密钥"""
        bundle_dict = load_fixture()
        dumped = json.dumps(bundle_dict, ensure_ascii=False)
        assert "/Volumes/" not in dumped
        assert "sk-" not in dumped or dumped.count("sk-") == 0  # no api key pattern


# ── PlayerState ──
class TestPlayerState:
    def test_new_game_state(self):
        state = PlayerState.new_game()
        assert state.schemaVersion == PLAYER_STATE_SCHEMA_VERSION
        assert state.energy == 100
        assert state.moneyCents == 2000
        assert state.day == 1
        assert state.minuteOfDay == 480  # 8:00

    def test_energy_bounds(self):
        with pytest.raises(Exception):
            PlayerState(
                schemaVersion=1,
                playerId="p1",
                day=1,
                minuteOfDay=0,
                moneyCents=0,
                energy=200,  # 越界
                germanXp=0,
                completedQuestIds=[],
                discoveredPoiIds=[],
                inventory={},
                savedAt=datetime.now(timezone.utc),
            )

    def test_minute_of_day_bounds(self):
        with pytest.raises(Exception):
            PlayerState(
                schemaVersion=1,
                playerId="p1",
                day=1,
                minuteOfDay=1500,  # 越界
                moneyCents=0,
                energy=100,
                germanXp=0,
                completedQuestIds=[],
                discoveredPoiIds=[],
                inventory={},
                savedAt=datetime.now(timezone.utc),
            )