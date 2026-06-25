# gagaToday — 德国留学模拟 RPG

> 基于真实 OpenStreetMap 数据的 16-bit 像素风德国城市 RPG
> 从慕尼黑出发，用地图 + AI 对话体验德国留学日常

---

## 当前状态 (2026-06-25)

**已实现的核心功能：**

- 🗺️ **PMTiles 矢量地图** — 德国全境 zoom 0–16，9.2GB 数据，HTTP Range 按需加载，实时渲染道路/建筑/水系/公园
- 📍 **POI 系统** — 从 OpenStreetMap 提取真实坐标和属性，SQLite 存储，素材生成器导出后地图自动显示
- 🏗️ **素材生成器** — Vue 3 卡片式 UI，LLM 自动生成 NPC/对话/知识卡/剧情，拖拽发布到地图
- 🎨 **16-bit 像素渲染** — Canvas + SVG 叠加，建筑用 OSM 真实颜色，像素化处理，暗蓝/金 RPG UI 面板
- 🧠 **多模型接入** — Qwen-Plus/Qwen3-Max (LLM) + MiniMax/ARK/OpenRouter/DashScope (图像)

---

## 快速启动

```bash
# 1. 地图前端（http://localhost:8081）
cd frontend && node server.cjs

# 2. 后端 API（http://127.0.0.1:8000）
cd /Volumes/NewDisk/GermanLearning
source /Volumes/NewDisk/.agent-secrets/secrets.env
uvicorn backend.poi-generator.main:app --reload --port 8000

# 3. 素材生成器（http://localhost:5174）
cd frontend/poi-generator && npx vite
```

**三个服务必须同时运行**，地图才能从 SQLite 加载 POI 数据。

---

## 架构

```
┌──────────────────────────────────────────────────┐
│  素材生成器 (Vue 3 + Vite :5174)                   │
│  ├─ 卡片网格 (11 张 POI)                          │
│  ├─ 弹窗编辑 (基础信息/NPC/对话/知识卡/剧情)        │
│  ├─ LLM 生成 (Qwen-Plus/Qwen3-Max)                │
│  └─ 拖拽发布 → POST /api/save/package              │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  后端 API (FastAPI :8000)                         │
│  ├─ /api/generate/*    LLM/图片生成               │
│  ├─ /api/save/package  写入 drafts + SQLite       │
│  ├─ /api/v2/pois       地图 POI 数据查询          │
│  └─ /api/osm/extract   OSM 地图数据提取           │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  SQLite (game_data.db)                            │
│  ├─ pois             POI 基础信息                 │
│  ├─ poi_scenes       场景图片路径                 │
│  ├─ poi_content      导出内容 (NPC/对话/知识卡)   │
│  └─ export_logs      导出历史                     │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  地图前端 (Node.js :8081)                         │
│  ├─ Canvas 渲染 (PMTiles → MVT → 道路/建筑/水系) │
│  ├─ SVG 叠加 (POI 标记 + 路线动画)                │
│  └─ fetch API → 动态加载 SQLite POI 数据          │
└──────────────────────────────────────────────────┘
```

---

## 目录结构

```
project/
├── frontend/
│   ├── index.html         # 地图主页（Canvas + SVG + 三栏 UI）
│   ├── server.cjs         # 静态文件服务器 (Range 支持)
│   └── poi-generator/     # 素材生成器 (Vue 3 + Vite)
│       └── src/
│           ├── App.vue           # 卡片网格 + 拖拽发布 + 弹窗编辑
│           ├── stores/           # Pinia 状态管理
│           └── components/       # POIInfoForm, ImagePanel, NPCPanel 等
├── backend/
│   └── poi-generator/
│       ├── main.py              # FastAPI 入口
│       ├── config.py            # 配置 (模型、路径、CORS)
│       ├── routers/             # text, image, save, pois_v2, osm
│       └── services/            # db_service, file_service, llm_service, ...
├── assets/
│   └── scenes/munich/           # AI 生成的场景图 (frauenkirche 等)
├── docs/
│   ├── ARCHITECTURE.md          # 架构文档
│   ├── GAME_DESIGN.md           # 游戏设计
│   ├── MVP_TASKS.md             # MVP 任务清单
│   └── curriculum/              # 教学大纲
└── scripts/
    └── map/                     # PMTiles 生成脚本 (planetiler)
```

---

## 核心工作流

### 制作 POI → 地图显示

```
1. 在生成器卡片网格选中 POI → 弹出编辑弹窗
2. 🤖 一键生成 NPC/对话/知识卡/剧情
3. 拖拽卡片到右侧「已发布」栏（或弹窗内点 📤 发布）
   → POST /api/save/package → 写入 SQLite
4. 刷新地图 → 自动从 API 拉取新 POI → 地图上出现新标记
```

### OSM 数据提取

```
生成器「基础信息」标签 → 自动 GET /api/osm/extract
→ Node.js 脚本读取 PMTiles 瓦片
→ 提取 5x5 瓦片网格内的所有特征
→ 返回主 POI（名称/多语言/分类/rank/距离）
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

| 层级 | 技术 |
|------|------|
| 前端地图 | Vanilla JS (Canvas + SVG + PMTiles) |
| 生成器 UI | Vue 3 + Pinia + Vite |
| 后端 | FastAPI (Python) |
| 数据库 | SQLite (WAL 模式) |
| 地图数据 | PMTiles (zoom 5–16, 9.2GB, Planetiler 生成) |
| 矢量渲染 | @mapbox/vector-tile + pbf |
| LLM | Qwen-Plus / Qwen3-Max |
| 图像 | MiniMax / ARK / OpenRouter / DashScope |

几乎可忽略,无需优化成本。
## 文档

### 当前架构（A 方案：慕尼黑 POI 探索 + 素材生成器）

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 当前实现的架构图、模块边界、端口分配
- [docs/POI_CONTENT_GENERATOR_PLAN.md](docs/POI_CONTENT_GENERATOR_PLAN.md) — POI 内容生成器设计（2026-06-22 立项）
- [docs/AGENT_WORKFLOW.md](docs/AGENT_WORKFLOW.md) — 多 agent 协作约定（中性）

### 已弃用 / 远景参考（B 方案：30 天生活模拟）

> 以下文档描述的"30 天慕尼黑生活模拟"架构（React + Phaser + 时间/金钱/体力/日历系统）
> **未在当前实现中跟进**。当前实现是上面 A 方案的"POI 探索 + 素材生成器"。
> 这些文档保留作为远景参考，请勿按其路线规划开发。

- [docs/PROPOSAL.md](docs/PROPOSAL.md) — v2.0 远景提案（走遍德国 + 用户系统）
- [docs/PROJECT_FRAMEWORK.md](docs/PROJECT_FRAMEWORK.md) — 框架分层（**未跟进**）
- [docs/MVP_IMPLEMENTATION_PLAN.md](docs/MVP_IMPLEMENTATION_PLAN.md) — 12 周实施计划（**未跟进**）
- [docs/CONTENT_SCHEMA.md](docs/CONTENT_SCHEMA.md) — 30 天内容 JSON schema（**未跟进**）
- [docs/API_STACK.md](docs/API_STACK.md) / [docs/SCRIPT_METHODOLOGY.md](docs/SCRIPT_METHODOLOGY.md) / [docs/ART_ASSETS.md](docs/ART_ASSETS.md) — v2.0 时期附属
- [docs/archive/MVP_TASKS_BERLIN_2026-06-21.md](docs/archive/) — 柏林第 1 关 MVP 任务（**已弃用**）
- [docs/ARCHITECTURE_MUNICH_MVP.md](docs/ARCHITECTURE_MUNICH_MVP.md) / [docs/ARCHITECTURE_v2.0_ASPIRATIONAL.md](docs/ARCHITECTURE_v2.0_ASPIRATIONAL.md) — 历史架构文档
- [docs/GAME_DESIGN_MUNICH_MVP.md](docs/GAME_DESIGN_MUNICH_MVP.md) — 历史游戏设计

### Curriculum 知识库

- [docs/curriculum/README.md](docs/curriculum/README.md) — 三轨道课程知识库（德语/雅思/A-levels）

> **状态**：Curriculum 知识库已建立但**未接入**当前代码。下一阶段再决定是接入 POI 生成器还是重新定位。

### 智能体说明（未实现）

- [docs/agents/](docs/agents/) — 17 个角色化智能体说明（NPC 智能体 / 美食智能体 / ...）

> **状态**：这些是 B 方案时代的角色定义文档，**未在当前实现中跟进**。保留以备未来参考。
