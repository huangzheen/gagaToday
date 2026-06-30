# gagaToday 架构文档

> 最后更新: 2026-06-30(Phase 3 完成)

---

## 当前架构(Phase 1+2+3 状态)

### 服务拓扑

```
┌─────────────────────────────────────────────────────────────────────┐
│  玩家客户端 game-client (Vue 3 + MapLibre + Pinia :5185)            │
│                                                                     │
│  src/                                                               │
│  ├─ App.vue                  顶层:加载 bundle + 启动 clock           │
│  ├─ components/                                                       │
│  │  ├─ MapView.vue          MapLibre 地图 + 控件 + 玩家 marker        │
│  │  ├─ HUD.vue              右下角状态栏(Day/时间/能量/钱/XP)        │
│  │  └─ PoiDialog.vue        POI 详情(图 + 描述 + audio)              │
│  ├─ store/player.ts         Pinia store:state + actions + 持久化     │
│  ├─ composables/                                                      │
│  │  └─ useGameClock.ts      游戏时钟(1秒=1分钟,可暂停)              │
│  ├─ api/bundle.ts           fetch + ETag/304 + localStorage          │
│  ├─ map/                    createMap + mapStyle + types              │
│  ├─ schemas/                                                          │
│  │  ├─ content.ts          Zod:CityBundle 契约                       │
│  │  └─ save.ts             Zod:PlayerState + Haversine              │
│  └─ data/munich-bundle.json 静态 fixture (fallback)                  │
│                                                                     │
│  vite.config.ts proxy:                                              │
│    /api    → 127.0.0.1:8000                                         │
│    /assets → 127.0.0.1:8000                                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  后端 API + 静态资源 backend/poi-generator (FastAPI :8000)          │
│                                                                     │
│  main.py                                                            │
│  ├─ CORS (Vite dev origins)                                          │
│  ├─ /assets → StaticFiles(ASSETS_ROOT)                             │
│  └─ routers:                                                         │
│     ├─ game_content.py    /api/game/v1/cities[/{id}/bundle]  Phase 2│
│     ├─ text/image/save/pois_v2/osm/wiki   Phase 0 旧路由             │
│                                                                     │
│  services/                                                          │
│  ├─ runtime_export_service.py   SQLite → CityBundle 导出  Phase 2 │
│  ├─ db_service.py        SQLite 连接 + CRUD                         │
│  ├─ llm_service.py       Qwen-Plus / Qwen3-Max                     │
│  ├─ image_service.py     MiniMax / ARK / OpenRouter                │
│  └─ file_service.py      文件系统存取                              │
│                                                                     │
│  schemas/                                                            │
│  ├─ game_content.py      Pydantic v2:CityBundle 契约               │
│  └─ save.py              Pydantic v2:PlayerState                    │
│                                                                     │
│  game_data.db (SQLite WAL)                                          │
│  ├─ pois                 POI 基础信息                                │
│  ├─ poi_scenes           场景图路径                                  │
│  ├─ poi_content          NPC / 对话 / 知识卡 (JSON blob)            │
│  └─ export_logs          导出历史                                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ Range 206
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  老 PMTiles 服务器 frontend/server.cjs (:8081)                      │
│  - 暴露 /assets/munich_map/pmtiles/*.pmtiles (9.2 GB)              │
│  - Range 206 支持,无 gzip / 无缓存                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 增量小结

| Phase | 新增 | 关键文件 |
|-------|------|----------|
| Phase 1 | MapLibre 地图 + 自定义控件 | `game-client/src/map/`, `MapView.vue` |
| Phase 2 | runtime_export_service + /api/game/v1 + ETag | `services/runtime_export_service.py`, `routers/game_content.py`, `api/bundle.ts` |
| Phase 3 | Pinia store + HUD + PoiDialog + /assets mount | `store/player.ts`, `components/HUD.vue`, `components/PoiDialog.vue`, `composables/useGameClock.ts`, `schemas/save.ts` (v1→v2) |

---

## 关键数据流(Phase 2+3)

### Bundle 加载

```
玩家打开 :5185
  ↓ App.onMounted
  ↓ fetchCityBundle('munich')
  ↓
  GET /api/game/v1/cities/munich/bundle
    (带 If-None-Match: <缓存 etag>)
  ↓ vite proxy → 8000
  ↓
  FastAPI game_content.get_city_bundle
    ├─ _open_db()
    ├─ runtime_export_service.export_city('munich')
    │   ├─ _load_pois (聚合 scenes + audio)
    │   ├─ _compute_content_version (semver 1.YYYYMMDD.{hash})
    │   ├─ CityBundle(...) Pydantic 校验
    │   └─ _compute_etag (弱 ETag W/"<hex>")
    ├─ 检查 If-None-Match
    │   ├─ 匹配 → 304 (空 body)
    │   └─ 不匹配 → 200 + JSON body + ETag header
  ↓
  fetchCityBundle 解析 body
    ├─ Zod safeParseBundle 校验
    ├─ 写 localStorage 缓存
    └─ 返回 { bundle, contentVersion, source: 'network' | 'cache' }
  ↓
  App 用 bundle.pois → MapView
  ↓
  MapView 渲染 POI markers + 玩家 marker
```

### POI 点击 → Dialog

```
玩家点 POI marker
  ↓ MapView onPoiClick → emit('poi-click', poi)
  ↓ App onPoiClick
  ↓ player.openPoi(poi.id)
    ├─ markDiscovered(poi.id)  → discoveredPoiIds
    ├─ currentPoiId.value = id
    └─ isPaused.value = true   → game clock 暂停
  ↓
  App 派生 currentPoi = bundle.pois.find(p => p.id === currentPoiId)
  ↓
  PoiDialog 渲染:名字 + 图 + 描述 + audio + 距离
  ↓
  玩家点 "关闭" → player.closePoi() → isPaused = false → 时间恢复
```

### 玩家视野 → 发现 POI

```
玩家 setPosition({lng, lat})
  ↓
  MapView watch(player.player.playerPosition)
  ↓
  renderPlayerMarker() 更新 marker
  ↓
  player.discoverInVision(bundle.pois)
    ├─ 对每个 POI: haversineMeters(playerPos, poi.position)
    └─ 距离 ≤ visionRadiusMeters(500m)→ 加进 discoveredPoiIds
  ↓
  MapView watch(discoveredSet) → toggle CSS class(.gaga-poi-marker--undiscovered)
```

---

## 关键技术决策

### Phase 1

| 决策 | 理由 |
|------|------|
| **MapLibre GL JS 而非 OpenLayers / Leaflet** | WebGL 矢量瓦片渲染,性能比 Canvas DOM 高 10× |
| **PMTiles 协议单例注册** | 避免 maplibre 重复 addProtocol 抛错 |
| **自定义 16-bit RPG 控件** | maplibre 自带控件风格不一致 |
| **POI 用 DOM element marker 而非 sprite** | 一张图 = 一个 emoji,零资源成本 |
| **vite 端口 5185** | 跟 5174 / 5175 / 8081 都错开 |

### Phase 2

| 决策 | 理由 |
|------|------|
| **runtime_export_service.py 作为生产级 exporter** | 替换 Phase 0 一次性 `export_munich_fixture.py` |
| **路径参数化 `{city_id}`** | 即使只服务 munich,接口契约已支持多城市 |
| **contentVersion 用严格 semver `1.YYYYMMDD.{hash}`** | 符合 Pydantic/Zod schema `^\d+\.\d+\.\d+$` |
| **ETag 排除 generatedAt** | 重新导出不应让客户端缓存失效 |
| **脱敏:disk path 抛错而非返回** | 防止泄漏 `/Users/` `/Volumes/` 等绝对路径 |
| **三层 fallback** | 后端 304 → 200 → 静态 fixture |

### Phase 3

| 决策 | 理由 |
|------|------|
| **Pinia setup store 风格** | 类型自动推断,直接用 ref/computed/watch |
| **PlayerState schema v1→v2 自动迁移** | 旧存档不丢,自动补新字段 |
| **500ms debounce 持久化** | 避免每帧写 localStorage |
| **POI 视野过滤用 CSS class toggle** | 不重建 marker,只切 undiscovered 样式 |
| **游戏时间 1秒=1分钟** | 现实 24 分钟 = 游戏 1 天,体验合理 |
| **POI dialog 自动 discover + 暂停时间** | 玩家点开 dialog 就是"真正看到"了 |

---

## 端口分配

| 端口 | 服务 | 启动命令 | 状态 |
|------|------|---------|------|
| **5185** | 玩家客户端 game-client | `cd frontend/game-client && npm run dev` | **Phase 1+ 主入口** |
| **8000** | 后端 API + /assets 静态 | `cd /Volumes/NewDisk/GermanLearning && .venv/bin/python -m uvicorn backend.poi-generator.main:app --port 8000` | Phase 2 主后端 |
| **8081** | 老 PMTiles Range server | `cd frontend && node server.cjs` | Phase 1 沿用 |
| **5174** | 素材生成器 | `cd frontend/poi-generator && npx vite` | Phase 0 沿用(可选) |

---

## 环境变量

密钥统一从 `/Volumes/NewDisk/.agent-secrets/secrets.env` 加载:

| 变量 | 用途 |
|------|------|
| `DASHSCOPE_API_KEY` | 阿里云通义千问 (LLM + 图像编辑) |
| `ARK_API_KEY` | 火山引擎 (豆包 Seedream 图像) |
| `OPENROUTER_API_KEY` | OpenRouter (GPT-5.4 图像) |
| `MINIMAX_API_KEY` | MiniMax/海螺 AI (默认图像) |
| `VITE_PMTILES_URL` | 前端 PMTiles URL(相对 :8081 老 server) |

---

## 历史架构(Phase 0,保留作参考)

### 老地图前端 vanilla JS(:8081 单文件)

```
┌─────────────────────────────────────────────────────────────────┐
│                  老地图前端 (:8081)                                │
│  Node.js + Vanilla JS                                            │
│                                                                  │
│  index.html (单文件应用)                                           │
│  ├─ 三栏布局: 左侧面板 | 地图 | 右侧详情                         │
│  ├─ 16-bit RPG 风格 UI (暗蓝/金 CSS)                              │
│  └─ <script type="module"> 内联 JS (~17KB)                        │
│                                                                  │
│  渲染管线:                                                        │
│  ├─ PMTiles → HTTP Range 请求瓦片                                │
│  ├─ MVT 解码 (@mapbox/vector-tile + pbf)                          │
│  ├─ Canvas 绘制: 道路 / 建筑 / 水系 / 公园                         │
│  └─ SVG 叠加: POI 标记 + 路线动画                                 │
└─────────────────────────────────────────────────────────────────┘
```

**保留原因:** Phase 1 game-client 仍依赖 :8081 拉 PMTiles 瓦片(暂未替换为独立 Munich bbox)。Phase 3 评估是否切换到 Munich bbox PMTiles。

---

## 文档索引

- [README.md](README.md) — 项目入口,Phase 进度,快速启动
- [PHASE1_MAP_INTEGRATION.md](PHASE1_MAP_INTEGRATION.md) — Phase 1 详情
- [PHASE2_RUNTIME_API.md](PHASE2_RUNTIME_API.md) — Phase 2 详情
- [PHASE3_GAMEPLAY.md](PHASE3_GAMEPLAY.md) — Phase 3 详情
- [RUNTIME_CONTENT_SCHEMA.md](RUNTIME_CONTENT_SCHEMA.md) — Phase 0 schema 契约