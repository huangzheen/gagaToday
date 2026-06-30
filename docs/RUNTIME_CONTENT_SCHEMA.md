# Runtime Content Schema (运行时内容契约)

> Phase 0 冻结的运行时数据契约,所有后续 Phase 必须基于此文档

## 为什么需要这个

旧架构里,玩家地图 (`frontend/index.html`) 直接通过 `/api/v2/pois?city=munich&published_only=true` 读后端 SQLite。这导致:

- 数据库字段直接泄漏给客户端(比如 `file_path`、`acts` 字段名混乱)
- 草稿(未发布)和正式内容走同一路径,前端无法区分
- 没有版本号,schema 一变客户端就静默崩溃

本文件定义的 `CityBundle` 是**新的 source of truth**:
- 玩家客户端**只解析 CityBundle,绝不直接读 SQLite**
- 后端 `runtime_export_service.py` (Phase 2) 负责 SQLite → CityBundle 转换 + 脱敏
- 双端 schema (`frontend/game-client/src/schemas/content.ts` + `backend/poi-generator/schemas/game_content.py`) 严格对齐

## 双端文件对应表

| 概念 | TypeScript (Zod) | Python (Pydantic) |
|---|---|---|
| CityBundle | `schemas/content.ts` | `schemas/game_content.py::CityBundle` |
| RuntimePoi | `schemas/content.ts::PoiSchema` | `schemas/game_content.py::RuntimePoi` |
| LocalizedText | `schemas/content.ts::LocalizedTextSchema` | `schemas/game_content.py::LocalizedText` |
| Position | `schemas/content.ts::PositionSchema` | `schemas/game_content.py::Position` |
| NPC/Dialogue/Quest | 同上(用 `.passthrough()` 暂未严格化) | 同上 |
| PlayerState | `schemas/save.ts` | `schemas/save.py::PlayerState` |

**任何字段如果只在一端有,都视为 bug。**

## 顶层结构

```ts
interface CityBundle {
  schemaVersion: 1              // 格式版本,只增不减
  contentVersion: 'x.y.z'      // 内容数据版本,发布时生成
  city: 'munich'                // 城市 ID (lowercase)
  generatedAt: ISO8601          // 服务端导出时间
  pois: RuntimePoi[]            // POI 列表
  npcs: RuntimeNpc[]            // NPC 列表
  dialogues: RuntimeDialogue[]  // 对话脚本
  quests: RuntimeQuest[]        // 任务列表
  knowledgeCards: KnowledgeCard[]  // 学习卡片
}
```

## 关键字段语义

### `schemaVersion` vs `contentVersion`

- `schemaVersion`: 字段集/类型本身改变了 → 客户端必须升级
  - 当前固定为 `1`
  - 升级方式:写新 `CityBundleV2Schema`,旧数据经 `migrateV1ToV2(bundle)` 转换
- `contentVersion`: 同一个 schema 下,内容数据更新了(比如新增了 1 个 POI) → 客户端可以热更新
  - 格式: `x.y.z` semver
  - 由 exporter 生成(基于 `pois.updated_at` 等字段 hash,Phase 2 实现)

### `published`

POI/NPC/Dialogue/Quest 的 `published` 在 bundle 里**必须是字面量 `true`** (`z.literal(true)`):
- 草稿不能直接冒充已发布运行时数据
- 客户端如果看到 `published !== true`,视为严重错误

### `position`

```ts
{ lat: number; lng: number }  // 顺序严格,GeoJSON 标准
```

- 范围: `lat ∈ [-90, 90]`, `lng ∈ [-180, 180]`
- 服务端导出前必须校验(防 OSM 抓取异常)
- 客户端不需要做范围校验,但测试会跑

### `sceneUrls` / `audioUrls` / `iconUrl`

全部是 **浏览器可访问的 URL**,**不能是磁盘绝对路径**:

```
✅ /assets/scenes/munich/frauenkirche/_reference/ref_frauenkirche.png
✅ https://cdn.example.com/...
❌ /Volumes/NewDisk/GermanLearning/assets/...
❌ /Users/.../foo.png
```

服务端 exporter 负责路径转换(`file_path` → URL)。

### 跨字段一致性(必须)

由 Pydantic `root_validator` 和 Zod `superRefine` 强制:

- `Quest.poiId` 必须在 `pois[].id` 集合里
- `Dialogue.npcId` 必须在 `npcs[].id` 集合里
- `Dialogue.startNodeId` 必须在 `nodes[].id` 集合里
- 所有 `nextNodeId` 必须能解析(或为 `null`)

测试用例覆盖在 `schemas/tests/test_schemas.py` 和 `frontend/game-client/src/test/content.test.ts`。

## Player State (本地存档)

跟 content schema 完全独立 — content 是从服务器来的,save 是 localStorage 写入:

```ts
interface PlayerState {
  schemaVersion: 1
  playerId: string
  day: number
  minuteOfDay: number  // 0-1439
  moneyCents: number   // 整数分
  energy: number       // 0-100
  germanXp: number
  completedQuestIds: string[]
  discoveredPoiIds: string[]
  inventory: Record<string, number>
  lastContentVersion?: string
  savedAt: ISO8601
}
```

存档 key: `gagatoday.save.v1`

损坏存档处理:不静默覆盖,先备份到 `gagatoday.save.v1.invalid.<timestamp>`。

## 不在 schema 里的东西

下列字段**绝对不出现**在 bundle 里,exporter 必须脱敏:

- `file_path` (磁盘绝对路径)
- `created_at` / `updated_at` (内部元数据,玩家用不到)
- 内部审核备注、生成日志
- 任何 API key / model 凭证
- 任何 LLM prompt

如果客户端需要看到时间戳,只能看到 `generatedAt`(导出时间),不能看到数据库行级时间。

## 当前状态 (2026-06-28)

- ✅ TypeScript Zod schema (Phase 0.2)
- ✅ Python Pydantic schema (Phase 0.3)
- ✅ Munich fixture 从 SQLite 导出 (Phase 0.4)
- ✅ Vitest + Pytest 测试 (Phase 0.5)
- ⚠️  fixture 还很薄:`npcs / dialogues / quests / knowledgeCards` 全空 — 因为数据库里没数据
- ⚠️  `runtime_export_service.py` (Phase 2) 还没建 — 当前 fixture 是 `scripts/export_munich_fixture.py` 临时导的

## 下一步

- ✅ **Phase 1** (2026-06-30): MapLibre + PMTiles 渲染慕尼黑 + POI 标记,见 `docs/PHASE1_MAP_INTEGRATION.md`
- **Phase 2**: 建 `runtime_export_service.py`,用本 schema 替换临时 fixture 脚本;建 `/api/game/v1/cities/{city}/bundle` 端点
- **Phase 5**: 当 NPC/Dialogue/Quest 内容真正写进 SQLite,本 schema 的 `.passthrough()` 要收紧成严格 schema

## 如何测试

### 前端

```bash
cd frontend/game-client
npm install
npm run test          # Vitest,验证 schema + fixture
npm run typecheck     # TypeScript 编译检查
```

### 后端

```bash
cd backend
PYTHONPATH=. python3 -m pytest poi_generator/schemas/tests/ -v
```

### Fixture 重新生成

```bash
cd /Volumes/NewDisk/GermanLearning
python3 backend/poi-generator/scripts/export_munich_fixture.py
```