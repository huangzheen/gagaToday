"""
gagaToday 运行时内容契约 (Runtime Content Contract) — Python 端

必须与 frontend/game-client/src/schemas/content.ts 保持完全一致。

谁负责什么:
- 内容生产端 (Vue POI Generator + FastAPI Admin) → 写 SQLite / draft JSON
- 内容审核员 → 决定 is_published
- **运行时导出端** (runtime_export_service.py) → SQLite → CityBundle JSON
- **玩家客户端** (game-client, Zod 端) → 只解析 CityBundle,绝不直接读 SQLite

任何字段如果"看起来合理但客户端没有 schema 验证",就属于错误。
本文件是 Python 端的 single source of truth,TS 端 schemas/content.ts 必须对齐。

版本策略:
- schemaVersion: CityBundle JSON 自身的格式版本,只增不减
- contentVersion: 同一份内容数据的版本号(发布时由导出器生成)
- 玩家存档用 schemaVersion + 独立 save.py 的 schema

兼容性:
- Python 3.9+
- pydantic v2(用 field_validator / model_validator 模式)
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal

# ── 固定值 ──
CITY_BUNDLE_SCHEMA_VERSION = 1
PLAYER_STATE_SCHEMA_VERSION = 1

# POI 类型枚举(与 TS 端 POI_TYPE_VALUES 严格对齐)
POI_TYPE_VALUES = (
    "church", "square", "museum", "park", "market",
    "castle", "stadium", "school", "shop", "library",
    "home", "train_station", "subway", "tram", "bus_stop",
    "historic", "attraction", "landmark",
)


# ── 三语本地化文本 ──
class LocalizedText(BaseModel):
    de: str = Field(..., min_length=1)
    zh: str = Field(..., min_length=1)
    en: Optional[str] = None


# ── 经纬度 ──
class Position(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


# ── POI ──
class PoiAudioUrls(BaseModel):
    de: Optional[str] = None
    zh: Optional[str] = None
    en: Optional[str] = None


class RuntimePoi(BaseModel):
    id: str = Field(..., min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    city: str = Field(..., min_length=1)
    type: str
    name: LocalizedText
    position: Position
    description: Optional[Dict[str, str]] = None  # 可选,可只填 de/zh
    icon: str = Field(..., min_length=1, max_length=8)
    iconUrl: Optional[str] = None
    sceneUrls: List[str] = Field(default_factory=list)
    audioUrls: PoiAudioUrls = Field(default_factory=PoiAudioUrls)
    questIds: List[str] = Field(default_factory=list)
    npcIds: List[str] = Field(default_factory=list)
    published: bool = True  # 运行时 bundle 里只可能 published=true

    @field_validator("type")
    @classmethod
    def _validate_type(cls, v: str) -> str:
        if v not in POI_TYPE_VALUES:
            raise ValueError(
                f"POI type {v!r} 不在允许列表 ({POI_TYPE_VALUES[:5]}...)"
            )
        return v


# ── NPC (Phase 0 占位,Phase 4+ 严格化) ──
class NpcImages(BaseModel):
    head: Optional[str] = None
    half: Optional[str] = None


class RuntimeNpc(BaseModel):
    id: str = Field(..., min_length=1)
    poiId: str = Field(..., min_length=1)
    name: LocalizedText
    role: Dict[str, str] = Field(default_factory=dict)
    imageUrls: NpcImages = Field(default_factory=NpcImages)
    published: bool = True


# ── Dialogue ──
class DialogueChoice(BaseModel):
    id: str = Field(..., min_length=1)
    text: LocalizedText
    nextNodeId: Optional[str] = None
    learningRefs: List[str] = Field(default_factory=list)


class DialogueNode(BaseModel):
    id: str = Field(..., min_length=1)
    npcText: LocalizedText
    choices: List[DialogueChoice] = Field(default_factory=list)
    terminal: Optional[bool] = None
    result: Optional[str] = None  # success / failure / neutral

    @field_validator("result")
    @classmethod
    def _validate_result(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("success", "failure", "neutral"):
            raise ValueError(f"DialogueNode.result 必须是 success/failure/neutral,实际 {v!r}")
        return v


class RuntimeDialogue(BaseModel):
    id: str = Field(..., min_length=1)
    npcId: str = Field(..., min_length=1)
    startNodeId: str = Field(..., min_length=1)
    nodes: List[DialogueNode] = Field(..., min_length=1)
    published: bool = True


# ── Quest ──
class QuestReward(BaseModel):
    moneyCents: Optional[int] = None
    energy: Optional[int] = Field(None, ge=-100, le=100)
    germanXp: Optional[int] = Field(None, ge=0)
    unlockPoiIds: List[str] = Field(default_factory=list)
    itemGrants: Dict[str, int] = Field(default_factory=dict)


class RuntimeQuest(BaseModel):
    id: str = Field(..., min_length=1)
    title: LocalizedText
    description: Dict[str, str] = Field(default_factory=dict)
    poiId: str = Field(..., min_length=1)
    dialogueIds: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    reward: QuestReward = Field(default_factory=QuestReward)
    published: bool = True


# ── Knowledge Card ──
class RuntimeKnowledgeCard(BaseModel):
    id: str = Field(..., min_length=1)
    title: LocalizedText
    body: LocalizedText
    refs: List[str] = Field(default_factory=list)
    published: bool = True


# ── City Bundle ──
class CityBundle(BaseModel):
    schemaVersion: Literal[CITY_BUNDLE_SCHEMA_VERSION] = CITY_BUNDLE_SCHEMA_VERSION
    contentVersion: str = Field(..., min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    city: str = Field(..., min_length=1)
    generatedAt: datetime
    pois: List[RuntimePoi] = Field(default_factory=list)
    npcs: List[RuntimeNpc] = Field(default_factory=list)
    dialogues: List[RuntimeDialogue] = Field(default_factory=list)
    quests: List[RuntimeQuest] = Field(default_factory=list)
    knowledgeCards: List[RuntimeKnowledgeCard] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_cross_references(self) -> "CityBundle":
        """跨字段一致性:Quest.poiId / Dialogue.npcId 必须能解析"""
        poi_ids = {p.id for p in self.pois}
        npc_ids = {n.id for n in self.npcs}

        for q in self.quests:
            if q.poiId not in poi_ids:
                raise ValueError(f"Quest {q.id} 引用不存在的 POI {q.poiId!r}")

        for d in self.dialogues:
            if d.npcId not in npc_ids:
                raise ValueError(f"Dialogue {d.id} 引用不存在的 NPC {d.npcId!r}")

            # 额外检查:startNodeId 必须在 nodes 里
            node_ids = {n.id for n in d.nodes}
            if d.startNodeId not in node_ids:
                raise ValueError(
                    f"Dialogue {d.id} 的 startNodeId {d.startNodeId!r} 不在 nodes 中"
                )
            # 所有 nextNodeId 必须能解析(或为 None)
            for n in d.nodes:
                for c in n.choices:
                    if c.nextNodeId is not None and c.nextNodeId not in node_ids:
                        raise ValueError(
                            f"Dialogue {d.id} 节点 {n.id} 的 choice {c.id} "
                            f"nextNodeId={c.nextNodeId!r} 解析不到"
                        )

        return self

    def to_runtime_json(self) -> Dict:
        """导出成可直接发给客户端的 dict(JSON 序列化友好)"""
        return self.model_dump(mode="json")