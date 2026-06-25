# gagaToday 架构文档

> 最后更新: 2026-06-25

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    素材生成器 (:5174)                        │
│  Vue 3 + Pinia + Vite                                       │
│  ├─ 卡片网格 (11 张 POI)                                    │
│  ├─ 弹窗编辑 (基础信息 / NPC / 对话 / 知识卡 / 剧情)        │
│  ├─ LLM 生成 → POST /api/generate/json                     │
│  └─ 拖拽发布 → POST /api/save/package                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                    后端 API (:8000)                           │
│  FastAPI (Python)                                            │
│  ├─ routers/text.py      /api/generate/text | json           │
│  ├─ routers/image.py     /api/generate/image | models        │
│  ├─ routers/save.py      /api/save/json | image | package    │
│  ├─ routers/pois_v2.py   /api/v2/pois | pois/:id             │
│  └─ routers/osm.py       /api/osm/extract                    │
│                                                              │
│  services/                                                   │
│  ├─ llm_service.py       Qwen-Plus / Qwen3-Max               │
│  ├─ multi_image_service  MiniMax / ARK / OpenRouter / DashScope│
│  ├─ db_service.py        SQLite 四表 (WAL)                   │
│  ├─ file_service.py      文件系统存取                        │
│  └─ osm_extractor.py/mjs Node.js 读 PMTiles 提取 OSM 数据   │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                    SQLite (game_data.db)                      │
│                                                              │
│  pois               POI 基础信息                             │
│  ├─ id, city, name_de, name_zh, type, lat, lng, icon        │
│  ├─ walk_minutes, cost, ubahn, description, acts             │
│  ├─ unlocked, is_published, created_at, updated_at           │
│  └─ INDEX: city, type, is_published                          │
│                                                              │
│  poi_scenes          场景图片路径                            │
│  ├─ poi_id → pois, scene_type, variant, url_path, file_path  │
│  └─ INDEX: poi_id                                            │
│                                                              │
│  poi_content         导出内容（多版本）                      │
│  ├─ poi_id → pois, content_type, data (JSON blob)            │
│  ├─ export_batch, file_path, version                         │
│  └─ INDEX: poi_id, content_type                              │
│                                                              │
│  export_logs         导出历史记录                            │
│  └─ poi_id, city, batch_id, file_count, content_types        │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                    地图前端 (:8081)                            │
│  Node.js + Vanilla JS                                        │
│                                                              │
│  index.html (单文件应用)                                      │
│  ├─ 三栏布局: 左侧面板 | 地图 | 右侧详情                     │
│  ├─ 16-bit RPG 风格 UI (暗蓝/金 CSS)                         │
│  └─ <script type="module"> 内联 JS (~17KB)                   │
│                                                              │
│  渲染管线:                                                    │
│  ├─ PMTiles → HTTP Range 请求瓦片                            │
│  ├─ MVT 解码 (@mapbox/vector-tile + pbf)                     │
│  ├─ Canvas 绘制: 道路 (自适应宽度) / 建筑 / 水系 / 公园      │
│  ├─ 建筑颜色: POI 附近用 OSM colour，其余统一 PAL.b1        │
│  └─ SVG 叠加: POI 标记 (脉冲动画) + 路线 (贝塞尔曲线)       │
│                                                              │
│  POI 数据源:                                                  │
│  └─ loadPoisFromApi() → GET /api/v2/pois → SQLite → 动态渲染│
│     (API 不可用时 gamePois = []，地图无 POI)                 │
│                                                              │
│  交互:                                                        │
│  ├─ 拖拽/方向键移动 + 滚轮缩放                               │
│  ├─ 点击 POI 标记 → 右侧详情面板 (图片/描述/动作)            │
│  └─ 显示路线 → 从 home 到目标 POI 的 SVG 路径               │
└──────────────────────────────────────────────────────────────┘
```

---

## 数据流

### POI 制作流程

```
1. 生成器选中 POI 卡片
2. 弹窗内编辑基础信息 → 自动 OSM 提取真实名称/坐标
3. 🤖 一键生成 → LLM 生成 NPC / 对话 / 知识卡 / 剧情
4. 拖拽卡片到「已发布」栏 / 弹窗点 📤 发布
   → POST /api/save/package
   → 写入文件系统 (drafts/) + SQLite
5. 地图刷新 → GET /api/v2/pois → 渲染新 POI 标记
```

### OSM 数据提取流程

```
1. 生成器「基础信息」标签加载
2. Vue 组件 fetch → GET /api/osm/extract?lat=48.1385&lng=11.5737
3. Python 调 subprocess → node osm_extractor.mjs
4. Node.js 读 PMTiles (HTTP Range) → 搜索 5×5 瓦片网格
5. 返回: primary_poi, building, address, transport, roads, nearby_pois
6. 前端自动填入德语名/中文名 placeholder
```

---

## 关键技术决策

| 决策 | 理由 |
|------|------|
| **SQLite 而非 PostgreSQL** | 零部署，Python 内置，10k+ 条轻松 |
| **PMTiles 而非 tile server** | 单文件 9.2GB，HTTP Range 零配置 |
| **Vanilla JS 地图而非框架** | 单文件 <20KB，无构建步骤，直接改 |
| **Vue 生成器而非统一框架** | 编辑面板需要响应式，地图需要性能 |
| **WAL 模式** | 并发读写不阻塞 |
| **OSM colour 仅 POI 附近** | 保持地图风格统一，突出 POI 建筑 |

---

## 端口分配

| 端口 | 服务 | 启动命令 |
|------|------|---------|
| 8081 | 地图前端 | `cd frontend && node server.cjs` |
| 8000 | 后端 API | `uvicorn backend.poi-generator.main:app --reload --port 8000` |
| 5174 | 素材生成器 | `cd frontend/poi-generator && npx vite` |

---

## 环境变量

密钥统一从 `/Volumes/NewDisk/.agent-secrets/secrets.env` 加载：

| 变量 | 用途 |
|------|------|
| `DASHSCOPE_API_KEY` | 阿里云通义千问 (LLM + 图像编辑) |
| `ARK_API_KEY` | 火山引擎 (豆包 Seedream 图像) |
| `OPENROUTER_API_KEY` | OpenRouter (GPT-5.4 图像) |