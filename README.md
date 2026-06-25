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

### 项目核心文档
- [PROPOSAL.md](docs/PROPOSAL.md) - 完整项目实施方案 v2.0
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计(Web→Desktop + 用户系统)
- [API_STACK.md](docs/API_STACK.md) - 阿里云 API 选型与对接
- [SCRIPT_METHODOLOGY.md](docs/SCRIPT_METHODOLOGY.md) - 教材剧本化方法 v2.0
- [ART_ASSETS.md](docs/ART_ASSETS.md) - 美术素材清单(画师指南)
- [MVP_TASKS.md](docs/MVP_TASKS.md) - 4-6 周 MVP 任务清单

### Curriculum 知识库(2026-06-21 新建)
- **[curriculum/README.md](docs/curriculum/README.md)** —— 三轨道课程知识库总览
- **[curriculum/KP_SCHEMA.md](docs/curriculum/KP_SCHEMA.md)** —— KP 详细规范
- **[curriculum/routes/apply-to-germany.md](docs/curriculum/routes/apply-to-germany.md)** —— 申请德国路线(主路线)
- **[curriculum/tracks/deutsch/00-overview.md](docs/curriculum/tracks/deutsch/00-overview.md)** —— 德语轨道
- **[curriculum/tracks/ielts/00-overview.md](docs/curriculum/tracks/ielts/00-overview.md)** —— 雅思 4 项
- **[curriculum/tracks/alevels/00-overview.md](docs/curriculum/tracks/alevels/00-overview.md)** —— A-levels 33 科
- **[curriculum/tracks/alevels/knowledge-points/mathematics/c1-algebra.md](docs/curriculum/tracks/alevels/knowledge-points/mathematics/c1-algebra.md)** —— 数学 C1 algebra 完整 25 KP 拆解(模板)

## 目录结构

```
GermanLearning/
├── docs/                # 项目文档(6 个)
├── scripts/             # 独立工具脚本
├── assets/              # 美术资源(像素图、立绘、UI)
│   ├── characters/      # 角色立绘
│   ├── scenes/          # 场景背景
│   ├── ui/              # UI 元素
│   ├── cities/          # 城市徽章
│   ├── map/             # 地图素材
│   └── fonts/           # 像素字体
├── backend/             # Python 后端(FastAPI)
├── frontend/            # Web 前端(Vite + React + Phaser)
│   ├── src/
│   │   ├── core/        # 业务层(可复用到 Godot)
│   │   ├── game/        # 渲染层(Phaser,后期可换 Godot)
│   │   ├── ui/          # UI 层(React)
│   │   ├── audio/       # 录音/播放
│   │   ├── api/         # API 客户端
│   │   └── store/       # 状态管理
└── README.md            # 本文件
```

## 关键设计原则

1. **回合制对话**而非实时流式 —— 避开实时发音纠错难点,延迟更宽松
2. **Core 与 Game 分离** —— 业务层(可复用到 Godot)和渲染层(Phaser)解耦
3. **MVP 用本地 stub,Phase 2 切云端** —— API Client 接口稳定,业务代码 0 改动
4. **内容(JSON)与代码分离** —— 美术/内容创作者不写代码也能更新关卡
5. **AI API 抽象** —— 后期可切换开源/自建方案,脱钩云服务

## 下一步

按 [MVP_TASKS.md](docs/MVP_TASKS.md) 的 Phase 0 推进:

1. 你注册阿里云账号,开通百炼服务
2. 我跑通 Python demo 脚本(录音→ASR→Qwen→TTS→播放)
3. 我写柏林第 1 关(火车站问路)完整 JSON 剧本
4. 你试画 1 个 NPC 立绘测试风格
5. Decision Gate:确认教学设计 + 技术栈 OK 后进入 Phase 1
