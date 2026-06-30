# Phase 2: 运行时 CityBundle API

> 完成日期: 2026-06-30
> 范围: 后端 SQLite → FastAPI → 前端 fetch 的端到端管线

## 一句话总结

`runtime_export_service.py` 把 SQLite 里的 published POI 数据生产化成符合 Zod schema 的 CityBundle,通过 FastAPI 暴露给前端;前端从静态 `import` 改成 `fetch`,自动 ETag/304 协商。

## 架构

```
┌────────────────┐    SQLite     ┌────────────────────────┐
│  content       │   读/写       │  runtime_export_       │
│  producer      │ ───────────► │  service.py            │
│  (POI admin)   │               │  (脱敏 + 校验 + hash)   │
└────────────────┘               └─────────┬──────────────┘
                                           │ ExportResult
                                           ▼
                                ┌────────────────────────┐
                                │  FastAPI               │
                                │  routers/game_content  │
                                │  - /api/game/v1/cities │
                                │  - /api/.../{id}/bundle│
                                │  ETag/304 协商          │
                                └─────────┬──────────────┘
                                          │ JSON + ETag
                                          │ (经 vite proxy)
                                          ▼
                                ┌────────────────────────┐
                                │  frontend/game-client  │
                                │  api/bundle.ts         │
                                │  fetchCityBundle()     │
                                │  + localStorage 缓存   │
                                └────────────────────────┘
```

## 后端

### 文件清单

| 文件 | 角色 | 行数 |
|------|------|------|
| `backend/poi-generator/schemas/game_content.py` | Pydantic v2 兼容(修复 `regex→pattern` / `validator→field_validator`) | 221 |
| `backend/poi-generator/services/runtime_export_service.py` | 核心:SQLite → CityBundle 导出器 | 327 |
| `backend/poi-generator/routers/game_content.py` | FastAPI 路由(cities + bundle + ETag) | 156 |
| `backend/poi-generator/tests/test_runtime_export.py` | 40 个测试(exporter + router) | 247 |
| `backend/poi-generator/main.py` | 注册 game_content router,Phase 0 旧 router 用 try/except 包裹(避免 openai 缺依赖阻塞启动) | 90 |

### 关键设计

**1. contentVersion — 严格 semver `1.YYYYMMDD.{hash}`**
- 反映 published POIs + scenes + content 的 SHA256
- 同一份数据 → 同一 contentVersion(浏览器可缓存)
- 任何数据变更 → contentVersion 变化(强制客户端重新拉)
- `1.{8-digit-date}.{8-digit-hash-decimal}` 三段,符合 Zod schema 的 `^\d+\.\d+\.\d+$`

**2. ETag — 弱 ETag `W/"<16hex>"`**
- 基于 (canonical JSON 排除 generatedAt) 的 SHA256
- 排除 `generatedAt` 是关键 — 重新导出不应让客户端缓存失效

**3. 脱敏 — `_file_path_to_url()`**
- `/Users/`, `/Volumes/`, `/tmp/`, `/private/`, `/home/` 开头的磁盘路径 → **抛错**(绝不返回)
- `/assets/...` 保留,`https://...` 保留,相对路径补 `/`
- 测试覆盖 5 种 leak 路径,全部拒绝

**4. 接口路径参数化**
- `/api/game/v1/cities/{city_id}/bundle` — 即使现在只服务 `munich`,接口契约已支持多城市
- 未来 `--city=berlin` 零代码改动直接跑

**5. router 容错 — Phase 0 旧代码不挡 Phase 2**
- `text/image/save/pois_v2/osm/wiki` 用 try/except import(依赖 openai/dashscope,缺时不挂)
- `db_service.init_db()` 同理(用 Python 3.10+ 语法,3.9 不兼容)
- Phase 2 game_content router 不依赖这些,独立可启

### CLI 用法

```bash
cd /Volumes/NewDisk/GermanLearning
.venv/bin/python -m poi_generator.services.runtime_export_service munich
# stdout: 完整 bundle JSON
# stderr: meta=city=munich contentVersion=... etag=...
```

## 前端

### 文件清单

| 文件 | 角色 | 行数 |
|------|------|------|
| `frontend/game-client/src/api/bundle.ts` | fetcher + ETag/304 + localStorage 缓存 | 154 |
| `frontend/game-client/src/App.vue` | 从静态 import 改成 fetchCityBundle + fallback | 244 |
| `frontend/game-client/vite.config.ts` | 加 proxy `/api` → `127.0.0.1:8000` | 35 |
| `frontend/game-client/scripts/phase1-smoke.mjs` | 扩到 20 项(原 15 + Phase 2 5 项) | 215 |

### 关键设计

**1. fetchCityBundle() — 单文件统一处理**
- 优先 fetch(`/api/game/v1/cities/{city_id}/bundle`)
- 带 `If-None-Match` 请求 → 304 直接读 localStorage
- 200 响应 → Zod 校验 → 写 localStorage
- 任何错误 → 返回 `{source: 'error', errorMessage}`,由 App 决定是否降级

**2. 三层 fallback 链**
```
1. 后端 + 304   → 用 localStorage 缓存(source='cache')
2. 后端 + 200   → 用新数据 + 写缓存(source='network')
3. 后端失败     → 用静态 fixture munich-bundle.json(source='fallback')
4. 静态都失败   → Zod 报错,UI 红色错误面板
```

**3. Vite proxy — `/api` 自动转发 8000**
- 避免 CORS 配置(虽然 backend 已配,但更干净)
- dev server 单端口 5185 调试

**4. UI 显示**
- topbar 顶部: `gagaToday · München · v1.20260630.69050521`
- 状态栏: `✓ 地图就绪 · 城市 munich · 3 个 POI · [network]` (或 cache/fallback/error)
- 鼠标 hover v 显示 `dataSource: network`

## 验证矩阵

### 后端

| 验证项 | 结果 |
|--------|------|
| schemas/test_schemas.py | ✓ 19/19(修复前 pydantic v2 不兼容直接挂) |
| tests/test_runtime_export.py | ✓ 40/40(exporter + router) |
| FastAPI 启动(`uvicorn backend.poi-generator.main:app --port 8000`) | ✓ |
| `GET /api/game/v1/cities` | ✓ 200 + munich metadata |
| `GET /api/game/v1/cities/munich/bundle` | ✓ 200 + ETag + x-content-version + body |
| `If-None-Match: <etag>` → 304 | ✓ 0 bytes body |
| `GET /api/game/v1/cities/MUNICH/bundle` | ✓ 400 |
| `GET /api/game/v1/cities/berlin/bundle` | ✓ 404 |
| Vite proxy 转发 5185 → 8000 | ✓ headers + body 完整保留 |

### 前端

| 验证项 | 结果 |
|--------|------|
| typecheck (vue-tsc) | ✓ 0 errors |
| vitest | ✓ 17/17 |
| vite build | ✓ 1.49s, 955KB JS / 68KB CSS |
| dev server smoke | ✓ **20/20**(原 15 + Phase 2 5 项) |

### 端到端

```bash
# 后端启动
cd /Volumes/NewDisk/GermanLearning
.venv/bin/python -m uvicorn backend.poi-generator.main:app --port 8000

# 前端启动(另一终端)
cd frontend/game-client
npm run dev
# → http://127.0.0.1:5185

# 实测流:
# 1. 浏览器打开 5185
# 2. DevTools Network → /api/game/v1/cities/munich/bundle
#    第一次: 200 (1800 bytes), ETag W/"5760571cc447ddc6"
# 3. 刷新页面 → 304 (0 bytes), source='cache'
# 4. 停掉 uvicorn → 刷新 → source='fallback'(用静态 fixture)
```

## 已知限制

- **NPCs/Dialogues/Quests/KnowledgeCards 都为空** — DB 还没数据,exporter 返回空列表,前端不渲染(Phase 4+ 加内容)
- **城市 registry hardcoded 在 router 里** — 未来 Phase 3 改成 DB 表 + admin UI
- **PMTiles 仍是全国 9.2GB** — 跟 Phase 2 无关,Phase 3 抠独立 pmtiles
- **没有 WebSocket / 长连接** — 客户端不知 DB 何时变化,只能定时轮询或用户主动刷新
- **localStorage 缓存没有 TTL** — 服务端数据过期不会自动失效,需要 ETag 强制 200

## 衔接点(Phase 3+)

1. **城市切换 UI** — 顶部加 Tab(慕尼黑/柏林/汉堡...),调 `fetchCityBundle(<新 city>)` + `map.jumpTo(center, zoom)`
2. **每个城市独立 PMTiles** — `pmtiles extract germany.pmtiles munich.pmtiles --bbox=... --minzoom=12 --maxzoom=16`
3. **NPCs/Dialogues/Quests/KnowledgeCards 数据** — 走 `runtime_export_service._load_*` 现在是 stub,接 DB + Zod 校验
4. **contentVersion 推送到客户端** — WebSocket 或 SSE,数据变更时推 `{city, contentVersion}` 让客户端 invalidate cache
5. **Admin UI** — 直接调 `runtime_export_service` 生成 bundle 写到 `frontend/game-client/src/data/{city}-bundle.json`(用作静态 fallback 的"金本")