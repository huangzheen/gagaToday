"""
玩家存档 schema (Player State)

与 frontend/game-client/src/schemas/save.ts 严格对齐。

持久化规则:
- 主存档: `gagatoday.save.v1` (PlayerState dict)
- 损坏存档备份: `gagatoday.save.v1.invalid.<timestamp>`

迁移规则:
- schemaVersion 字段只增不减
- 旧存档通过 save_migrations.py 迁移到当前版本
- 迁移失败保留备份,不静默覆盖
"""

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field

PLAYER_STATE_SCHEMA_VERSION = 1
SAVE_KEY = "gagatoday.save.v1"
SAVE_BACKUP_PREFIX = "gagatoday.save.v1.invalid."


class PlayerState(BaseModel):
    schemaVersion: int = PLAYER_STATE_SCHEMA_VERSION
    playerId: str = Field(..., min_length=1)

    # 时间维度
    day: int = Field(..., ge=0)
    minuteOfDay: int = Field(..., ge=0, le=1439)  # 一天 1440 分钟

    # 资源
    moneyCents: int = Field(..., ge=0)
    energy: int = Field(..., ge=0, le=100)
    germanXp: int = Field(..., ge=0)

    # 进度
    completedQuestIds: List[str]
    discoveredPoiIds: List[str]
    inventory: Dict[str, int]

    # 元数据
    lastContentVersion: str = None
    savedAt: datetime

    @classmethod
    def new_game(cls) -> "PlayerState":
        """工厂:创建一份新游戏状态(8:00 早上, 20 欧, 100 体力)"""
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
            savedAt=datetime.now(),
        )


class QuestReward(BaseModel):
    """跟 game_content.py.QuestReward 对齐"""
    moneyCents: int = None
    energy: int = Field(None, ge=-100, le=100)
    germanXp: int = Field(None, ge=0)
    unlockPoiIds: List[str] = []
    itemGrants: Dict[str, int] = {}


# Quest 状态枚举
QUEST_STATUSES = ("locked", "available", "active", "completed", "failed")