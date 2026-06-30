# gagaToday — 德国留学模拟 RPG

> 基于真实 OpenStreetMap 数据的 16-bit 像素风德国城市 RPG
> 从慕尼黑出发,用地图 + AI 对话体验德国留学日常

---

## 当前状态 (2026-06-30,Phase 1+2+3 已完成)

**已完成的核心功能:**

- 🗺️ **MapLibre + PMTiles 矢量地图** — 16-bit RPG 配色样式,zoom 0-16 全德国瓦片,HTTP Range 按需加载
- 🎮 **玩家状态机** — Pinia store 持 PlayerState(位置/视野/时间/能量/金钱/XP),HUD 实时显示
- 👁️ **视野雾机制** — 进入视野的 POI 自动 discovered,未发现 POI 灰色半透明
- 🪟 **POI 详情面板** — 点 marker 弹 dialog(scene 图 + 三语 audio + 距离 + 进入对话)
- ⏰ **游戏内时钟** — 真实 1 秒 = 游戏 1 分钟,POI dialog 打开时自动暂停
- 🔌 **运行时 API** — `/api/game/v1/cities` + `/api/game/v1/cities/{id}/bundle`,ETag/304 协商
- 🗄️ **生产级导出器** — SQLite → CityBundle,脱敏(file_path 防泄漏)+ 跨字段一致性校验 + contentVersion hash
- 💾 **存档持久化** — PlayerState 写 localStorage(500ms debounce),v1→v2 schema 自动迁移,损坏存档备份
- 🛠️ **自定义地图控件** — 16-bit RPG 风格 `+`/`−` 缩放 + ↑↓←→ 方向键平移,整数 zoom 档

**Phase 0(已完成,Phase 1 的基础):**

- 🏛️ **运行时内容契约** — Python Pydantic v2 + TS Zod 双端 schema(POI / NPC / Dialogue / Quest / KnowledgeCard)
- 🧪 **测试矩阵** — 后端 59/59 pytest + 前端 17/17 vitest + 28/28 dev server smoke
- 📊 **DB schema** — `pois` / `poi_scenes` / `poi_content` / `export_logs` / `poi_scenes`

**Phase 4+ 待实现(已设计但未做):**

- NPC 对话系统(Dialogue engine 接 Quest 触发)
- 玩家自由移动(点击地图 / 拖动玩家 marker)
- 视野半径可视化(玩家周围画半透明圆)
- 多城市切换 UI(顶部 Tab + 独立 PMTiles)
- 时间倍率切换(1x / 2x / 4x)

---

## 快速启动

### 完整启动(3 个服务)

```bash
# 0. 一次性:加载密钥 + 装依赖
source /Volumes/NewDisk/.agent-secrets/secrets.env

# 1. 后端 API + 静态资源 (http://127.0.0.1:8000)
cd /Volumes/NewDisk/GermanLearning
.venv/bin/python -m uvicorn backend.poi-generator.main:app --host 127.0.0.1 --port 8000
# 暴露:
#   /api/game/v1/cities
#   /api/game/v1/cities/{city_id}/bundle  (ETag/304)
#   /assets/*  (scene 图 / audio)

# 2. 玩家客户端 (http://127.0.0.1:5185) — 推荐用这个看 Phase 3 效果
cd frontend/game-client
npm run dev
# 内部代理:
#   /api → 8000 (FastAPI bundle API)
#   /assets → 8000 (scene 图 / audio)

# 3. 老的 PMTiles Range server (http://127.0.0.1:8081) — 给 Phase 1 地图拉瓦片用
cd frontend && node server.cjs
# 暴露:
#   /assets/munich_map/pmtiles/*.pmtiles (Range 206)

# 4. 素材生成器 (http://127.0.0.1:5174) — 可选,做新 POI 时才需要
cd frontend/poi-generator
npx vite
```

**访问 http://127.0.0.1:5185/ 看 Phase 3 效果**(HUD + POI dialog + 玩家 marker)

### 最小启动(只看地图)

```bash
# 后端(必需)
cd /Volumes/NewDisk/GermanLearning
.venv/bin/python -m uvicorn backend.poi-generator.main:app --port 8000

# 玩家客户端(必需,会代理到 8000)
cd frontend/game-client && npm run dev

# PMTiles 老 server(必需,地图瓦片源)
cd frontend && node server.cjs
```

如果只起后端,玩家客户端会自动 fallback 到静态 fixture (`src/data/munich-bundle.json`)。

---

## 架构 (Phase 3 当前状态)

```
┌───────────────────────────────────────────────────────────────┐
│  玩家客户端 (Vue 3 + MapLibre + Pinia :5185)                  │
│  src/                                                         │
│  ├─ App.vue                  顶层:加载 bundle + 启动 clock    │
│  ├─ components/                                              │
│  │  ├─ MapView.vue           MapLibre 地图 + 控件 + 玩家 marker│
│  │  ├─ HUD.vue               右下角状态栏                    │
│  │  └─ PoiDialog.vue         POI 详情面板                     │
│  ├─ store/player.ts          Pinia store:state + actions      │
│  ├─ composables/useGameClock.ts  游戏时钟(1秒=1分钟)         │
│  ├─ api/bundle.ts            fetch + ETag/304 + localStorage  │
│  ├─ map/                     MapLibre + pmtiles Protocol + 样式│
│  ├─ schemas/                 Zod schema(content + save)       │
│  └─ data/munich-bundle.json  静态 fixture(后端 fallback)      │
└───────────────────────┬───────────────────────────────────────┘
                        │  /api/* /assets/*  (vite proxy)
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  后端 API + 静态资源 (FastAPI :8000)                           │
│  backend/poi-generator/                                       │
│  ├─ main.py                 FastAPI + CORS + /assets Static   │
│  ├─ routers/                                                 │
│  │  ├─ game_content.py      /api/game/v1/cities[/{id}/bundle]│
│  │  ├─ text/image/save/pois_v2/osm/wiki  Phase 0 老路由       │
│  ├─ services/                                                 │
│  │  ├─ runtime_export_service.py  SQLite → CityBundle 导出    │
│  │  ├─ db_service.py        SQLite 连接 + CRUD                │
│  │  ├─ llm_service.py       Qwen-Plus / Qwen3-Max             │
│  │  ├─ image_service.py     MiniMax / ARK / OpenRouter        │
│  │  └─ ...                                                     │
│  ├─ schemas/                                                  │
│  │  ├─ game_content.py      Pydantic v2: CityBundle 契约     │
│  │  └─ save.py              Pydantic v2: PlayerState          │
│  └─ game_data.db            SQLite (WAL)                       │
└───────────────────────┬───────────────────────────────────────┘
                        │  Range 206
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  老 PMTiles 服务器 (Node.js :8081)                            │
│  frontend/server.cjs                                           │
│  - 暴露 /assets/munich_map/pmtiles/*.pmtiles (9.2 GB)         │
│  - Range 206 支持,无 gzip / 无缓存                            │
└───────────────────────────────────────────────────────────────┘
```

**辅助模块(独立,不参与主流程):**

```
┌───────────────────────────────────────────────────────────────┐
│  素材生成器 (Vue 3 :5174) — 做新 POI 内容用                   │
│  frontend/poi-generator/                                      │
│  ├─ 卡片网格 + 编辑弹窗                                       │
│  ├─ LLM 生成 NPC / 对话 / 知识卡 / 剧情                       │
│  └─ 拖拽发布 → 写 SQLite → Phase 2 runtime_export 自动出现   │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  assets/scenes/munich/  — AI 生成的 16-bit RPG 场景图 + audio │
│  - /assets/scenes/munich/{poi_id}/_reference/ref_*.png         │
│  - /assets/scenes/munich/{poi_id}/audio/intro_{de,zh,en}.mp3 │
└───────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```
GermanLearning/
├── frontend/
│   ├── game-client/          ← Phase 1+2+3 玩家客户端(Vue 3 + MapLibre)
│   │   ├── src/
│   │   │   ├── App.vue
│   │   │   ├── main.ts
│   │   │   ├── components/         MapView / HUD / PoiDialog
│   │   │   ├── composables/        useGameClock
│   │   │   ├── store/              Pinia: player
│   │   │   ├── api/                bundle.ts (fetch + ETag)
│   │   │   ├── map/                createMap / mapStyle / types
│   │   │   ├── schemas/            content.ts / save.ts (Zod)
│   │   │   └── data/               munich-bundle.json (fixture)
│   │   ├── scripts/phase1-smoke.mjs   28 项 dev server smoke
│   │   └── vite.config.ts         + /api + /assets proxy
│   ├── poi-generator/         ← 素材生成器(独立 UI,Phase 0 沿用)
│   ├── index.html             ← 老的 vanilla 地图主页(已弃用)
│   └── server.cjs             ← 老 PMTiles Range server
│
├── backend/
│   └── poi-generator/         ← FastAPI 后端
│       ├── main.py            ← 入口(注册 game_content router + /assets mount)
│       ├── config.py          ← 配置
│       ├── routers/
│       │   ├── game_content.py    ← Phase 2 新增
│       │   ├── text.py / image.py / save.py / pois_v2.py / osm.py / wiki.py
│       ├── services/
│       │   ├── runtime_export_service.py    ← Phase 2 新增
│       │   ├── db_service.py / llm_service.py / ...
│       ├── schemas/
│       │   ├── game_content.py      ← Phase 0 Pydantic v2(Phase 2 修复)
│       │   └── save.py              ← PlayerState
│       ├── tests/
│       │   └── test_runtime_export.py   ← Phase 2 新增(40 测试)
│       ├── scripts/
│       │   └── export_munich_fixture.py ← Phase 0 工具(导出 fixture)
│       └── game_data.db        ← SQLite
│
├── assets/
│   └── scenes/munich/         ← AI 生成的场景图 + audio
│       ├── frauenkirche/_reference/ref_frauenkirche.png
│       ├── marienplatz/_reference/{ref,scene_*}.png
│       └── munchen_hauptbahnhof/
│           ├── _reference/*.png
│           └── audio/intro_{de,zh,en}.mp3
│
├── docs/
│   ├── README.md                ← 你正在看
│   ├── ARCHITECTURE.md          ← 详细架构 + Phase 状态
│   ├── PHASE1_MAP_INTEGRATION.md    ← Phase 1 详情
│   ├── PHASE2_RUNTIME_API.md        ← Phase 2 详情
│   ├── PHASE3_GAMEPLAY.md           ← Phase 3 详情
│   ├── RUNTIME_CONTENT_SCHEMA.md    ← Phase 0 schema 契约
│   └── curriculum/                  ← 三轨道知识库(未接入)
│
└── scripts/
    └── map/                     ← PMTiles 提取工具
```

---

## 核心工作流

### 制作新 POI → 玩家客户端显示

```
1. 在素材生成器(:5174) 选 POI → 编辑/生成 NPC/对话/知识卡/剧情
2. 拖拽发布 → 写 SQLite (is_published = 1)
3. 玩家客户端(:5185) 打开页面 → fetch /api/game/v1/cities/munich/bundle
4. FastAPI runtime_export_service 读 SQLite → 校验 → 生成 contentVersion
5. 返回 CityBundle JSON + ETag header
6. 浏览器解析 → Zod 校验 → 渲染 POI marker(已发现的会显示)
```

### 多用户协作:数据流

```
素材生成器 ──写──> SQLite ──读──> runtime_export ──JSON──> 玩家客户端
                                                  ↑
                                              ETag/304
                                              本地缓存
```

---

## 接入的大模型

| 类型 | 模型 | 提供商 |
|------|------|--------|
| LLM 日常 | `qwen-plus` | 阿里云 DashScope (通义千问) |
| LLM 复杂 | `qwen3-max` | 阿里云 DashScope |
| 图像 默认 | `minimax` | MiniMax/海螺 AI |
| 图像 备选 | `doubao-seedream` | 火山引擎 ARK |
| 图像 备选 | `openai/gpt-5.4-image-2` | OpenRouter |
| 图像 备选 | `qwen-image-edit-plus` | 阿里云 DashScope |

---

## 技术栈

| 层级 | 技术 | 备注 |
|------|------|------|
| 玩家客户端 UI | Vue 3 + Pinia + MapLibre GL JS | Phase 1-3 |
| 状态管理 | Pinia (setup store 风格) | Phase 3 |
| 客户端 schema | Zod | content.ts + save.ts |
| 客户端构建 | Vite + vue-tsc | TypeScript strict |
| 客户端测试 | Vitest (jsdom) | 17 测试 |
| 客户端 smoke | 自写 node http 脚本 | 28 项 |
| 后端 | FastAPI (Python 3.9) | |
| 后端 schema | Pydantic v2(Phase 2 修复兼容) | |
| 后端静态 | FastAPI StaticFiles mount /assets | Phase 3 |
| 后端测试 | Pytest | 59 测试 |
| 数据库 | SQLite (WAL 模式) | |
| 地图数据 | PMTiles 9.2GB (germany-zoom16) | Phase 3 评估抠 Munich bbox |
| 地图渲染 | MapLibre GL JS + pmtiles Protocol | Phase 1 |
| LLM | Qwen-Plus / Qwen3-Max | |
| 图像 | MiniMax / ARK / OpenRouter / DashScope | |
| 场景图 | 16-bit RPG 风 PNG(AI 生成) | |
| Audio | MP3(三语 intro) | |

---

## 文档索引

### 当前架构(A 方案:慕尼黑 POI 探索 + Phase 1-3 增量)

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 详细架构 + Phase 状态
- [docs/PHASE1_MAP_INTEGRATION.md](docs/PHASE1_MAP_INTEGRATION.md) — Phase 1:MapLibre + PMTiles
- [docs/PHASE2_RUNTIME_API.md](docs/PHASE2_RUNTIME_API.md) — Phase 2:后端 API + ETag
- [docs/PHASE3_GAMEPLAY.md](docs/PHASE3_GAMEPLAY.md) — Phase 3:玩家状态机 + POI 交互
- [docs/RUNTIME_CONTENT_SCHEMA.md](docs/RUNTIME_CONTENT_SCHEMA.md) — Phase 0 契约(Pydantic + Zod)
- [docs/POI_CONTENT_GENERATOR_PLAN.md](docs/POI_CONTENT_GENERATOR_PLAN.md) — 素材生成器设计
- [docs/AGENT_WORKFLOW.md](docs/AGENT_WORKFLOW.md) — 多 agent 协作约定

### 已弃用 / 远景参考(B 方案:30 天生活模拟)

> 以下文档描述的"30 天慕尼黑生活模拟"架构(React + Phaser + 时间/金钱/体力/日历系统)
> **未在当前实现中跟进**。当前实现是上面 A 方案 + Phase 1-3 增量。
> 这些文档保留作为远景参考,请勿按其路线规划开发。

- `docs/PROPOSAL.md` / `docs/PROJECT_FRAMEWORK.md` / `docs/MVP_IMPLEMENTATION_PLAN.md` — v2.0 远景
- `docs/CONTENT_SCHEMA.md` / `docs/API_STACK.md` / `docs/SCRIPT_METHODOLOGY.md` / `docs/ART_ASSETS.md`
- `docs/archive/MVP_TASKS_BERLIN_2026-06-21.md`
- `docs/ARCHITECTURE_MUNICH_MVP.md` / `docs/ARCHITECTURE_v2.0_ASPIRATIONAL.md`
- `docs/GAME_DESIGN_MUNICH_MVP.md`

### Curriculum 知识库

- [docs/curriculum/README.md](docs/curriculum/README.md) — 三轨道课程知识库(德语/雅思/A-levels)

> **状态**:Curriculum 知识库已建立但**未接入**当前代码。下一阶段再决定是接入 POI 生成器还是重新定位。

---

## Phase 进度表

| Phase | 状态 | 文档 | 主要交付 |
|-------|------|------|----------|
| Phase 0 | ✅ | [RUNTIME_CONTENT_SCHEMA.md](docs/RUNTIME_CONTENT_SCHEMA.md) | Schema 契约 + SQLite + 素材生成器 |
| Phase 1 | ✅ | [PHASE1_MAP_INTEGRATION.md](docs/PHASE1_MAP_INTEGRATION.md) | MapLibre + PMTiles + 自定义控件 |
| Phase 2 | ✅ | [PHASE2_RUNTIME_API.md](docs/PHASE2_RUNTIME_API.md) | runtime_export_service + /api/game/v1 + ETag |
| Phase 3 | ✅ | [PHASE3_GAMEPLAY.md](docs/PHASE3_GAMEPLAY.md) | Pinia store + HUD + PoiDialog + 玩家 marker |
| Phase 4 | 📅 | 待写 | NPC 对话 + Quest 触发 + reward |
| Phase 5+ | 💭 | 待讨论 | 多城市切换 / 玩家移动 / 视野可视化 / 时间倍率 |

---

## 已知限制 & 未来优化

### 性能

- PMTiles 9.2GB 仍是全国数据,首屏 30s;Phase 3+ 抠 Munich bbox 可降至 3-5s
- 客户端 bundle 980KB,maplibre 占大头;Phase 4+ code-split

### 数据

- 只有慕尼黑 3 个 POI 有数据(数据库里);其他城市需生成
- NPCs/Dialogues/Quests/KnowledgeCards 暂未填充
- 无玩家自由移动(只能通过代码 setPosition)

### 架构

- 多城市架构(独立 PMTiles + 城市 Tab)已设计但用户决定暂缓
- 没有 WebSocket / SSE 推送 contentVersion 变化
- localStorage 缓存没有 TTL