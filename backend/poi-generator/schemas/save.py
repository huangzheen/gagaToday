"""
玩家存档 schema (Player State) — Python 端

与 frontend/game-client/src/schemas/save.ts 严格对齐。

Phase 3 / 审计 P1-03 修复:
- 升 v1 → v2(前端早已是 v2,Python 一直是 v1)
- 加 playerPosition / visionRadiusMeters / currentCity 三个地图相关字段
- 可变默认值改用 Field(default_factory=...)(避免共享 mutable default bug)
- Optional 显式标注,避免 str = None 这种隐式 optional

持久化规则:
- 主存档: `gagatoday.save.v1` (PlayerState dict,localStorage key 不变)
- 损坏存档备份: `gagatoday.save.v1.invalid.<timestamp>`

迁移规则:
- schemaVersion 字段只增不减
- 旧存档通过 save_migrations.py 迁移到当前版本
- 迁移失败保留备份,不静默覆盖

v1 → v2 字段变化:
- 新增 playerPosition: {lng, lat} | null
- 新增 visionRadiusMeters: int (默认 500)
- 新增 currentCity: str | null
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ── 固定值 ──
PLAYER_STATE_SCHEMA_VERSION = 2  # 审计 P1-03:升 v1 → v2
SAVE_KEY = "gagatoday.save.v1"
SAVE_BACKUP_PREFIX = "gagatoday.save.v1.invalid."


# ── 经纬度(跟 content.py.Position 等价,单独定义避免循环依赖) ──
class PlayerPosition(BaseModel):
    lng: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)


# ── 玩家状态 ──
class PlayerState(BaseModel):
    # schemaVersion 必须是字面量 2(Zod 端用 z.literal(2) 校验)
    schemaVersion: int = PLAYER_STATE_SCHEMA_VERSION
    playerId: str = Field(..., min_length=1)

    # 时间维度
    day: int = Field(..., ge=0)
    minuteOfDay: int = Field(..., ge=0, le=1439)  # 一天 1440 分钟

    # 资源
    moneyCents: int = Field(..., ge=0)
    energy: int = Field(..., ge=0, le=100)
    germanXp: int = Field(..., ge=0)

    # 进度(可变 list/dict 必须用 default_factory,避免共享 mutable default)
    completedQuestIds: List[str] = Field(default_factory=list)
    discoveredPoiIds: List[str] = Field(default_factory=list)
    inventory: Dict[str, int] = Field(default_factory=dict)

    # Phase 3 地图字段(新增)
    playerPosition: Optional[PlayerPosition] = None
    visionRadiusMeters: int = Field(default=500, gt=0)
    currentCity: Optional[str] = None

    # 元数据
    lastContentVersion: Optional[str] = None
    savedAt: datetime

    @classmethod
    def new_game(cls, start_position: Optional[PlayerPosition] = None, city: Optional[str] = None) -> "PlayerState":
        """工厂:创建一份新游戏状态(8:00 早上, 20 欧, 100 体力)

        Args:
            start_position: 玩家起始坐标(None = 还没移动)
            city: 起始城市 ID(None = 未选择)
        """
        import time
        return cls(
            schemaVersion=PLAYER_STATE_SCHEMA_VERSION,
            playerId=f"player_{int(time.time() * 1000):x}",
            day=1,
            minuteOfDay=480,  # 8:00
            moneyCents=2000,
            energy=100,
            germanXp=0,
            completedQuestIds=[],
            discoveredPoiIds=[],
            inventory={},
            playerPosition=start_position,
            visionRadiusMeters=500,
            currentCity=city,
            savedAt=datetime.now(),
        )


# ── v1 → v2 迁移 ──
def migrate_v1_to_v2(old: dict) -> Optional[PlayerState]:
    """
    把 v1 存档升级到 v2(补 3 个地图字段)

    Returns:
        - PlayerState: 迁移成功
        - None: 输入不是合法 v1 存档(schemaVersion != 1)
    """
    if not isinstance(old, dict):
        return None
    if old.get("schemaVersion") != 1:
        return None

    # v1 缺这几个字段,补默认值
    migrated = dict(old)
    migrated["schemaVersion"] = PLAYER_STATE_SCHEMA_VERSION
    migrated.setdefault("playerPosition", None)
    migrated.setdefault("visionRadiusMeters", 500)
    migrated.setdefault("currentCity", None)

    try:
        return PlayerState(**migrated)
    except Exception:
        return None


class QuestReward(BaseModel):
    """跟 game_content.py.QuestReward 对齐"""
    moneyCents: Optional[int] = None
    energy: Optional[int] = Field(None, ge=-100, le=100)
    germanXp: Optional[int] = Field(None, ge=0)
    unlockPoiIds: List[str] = Field(default_factory=list)
    itemGrants: Dict[str, int] = Field(default_factory=dict)


# Quest 状态枚举
QUEST_STATUSES = ("locked", "available", "active", "completed", "failed")