# Phase 1 — MapLibre + PMTiles 集成

> **完成日期**: 2026-06-30
> **目标**: 验证 MapLibre 能读现有德国 PMTiles、显示慕尼黑 + POI,不改业务逻辑
> **状态**: ✅ 完成(13/13 smoke 通过 + 17/17 vitest 通过 + typecheck clean + build 成功)

---

## 一句话总结

`game-client` 用 **MapLibre GL JS 4.x** 读 `germany-zoom16.pmtiles` 渲染慕尼黑底图,用 **protomaps pmtiles 4.x** 协议解决 HTTP Range 切片。Phase 0 的 Munich fixture 通过 Vite 静态 import,经 Zod 校验后渲染为金色圆形 emoji 标记。

## 验证矩阵

| 项目 | 命令 | 结果 |
|------|------|------|
| 类型检查 | `npm run typecheck` | ✓ 0 errors |
| 单元测试 | `npm run test` | ✓ 17/17 (Phase 0 schema) |
| 生产 build | `npm run build` | ✓ 1.45s, 932KB JS / 68KB CSS |
| Dev server | `npx vite` | ✓ http://127.0.0.1:5185/ |
| Dev smoke | `node scripts/phase1-smoke.mjs` | ✓ 13/13 |
| PMTiles Range | `curl -H Range: 0-1023` | ✓ 206 / bytes 0-1023/9908259563 |
| 真实地图渲染 | 浏览器打开 5185 | 🟡 需人工确认(见下方"如何验证") |

## 架构总览

```
┌────────────────────────────────────────────────────────┐
│               frontend/game-client                     │
│                                                        │
│   index.html                                           │
│     └─ src/main.ts                                     │
│         └─ src/App.vue  ←─ import Zod 解析 fixture    │
│             └─ src/components/MapView.vue              │
│                 ├─ src/map/createMap.ts                │
│                 │   ├─ maplibre-gl 4.7                 │
│                 │   └─ pmtiles 4.0 (Protocol)          │
│                 └─ src/map/mapStyle.ts (inline style)  │
│                                                        │
│   数据流:                                              │
│   fixture.json → Zod 校验 → POI[] → MapView            │
│                                              ↓         │
│              createMap → pmtiles://VITE_PMTILES_URL    │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP Range 206
                           ▼
┌────────────────────────────────────────────────────────┐
│   老的 Node server.cjs (frontend/, :8081)              │
│   /assets/munich_map/pmtiles/germany-zoom16.pmtiles    │
│   9.2 GB, 16 vector layers, MVT                        │
└────────────────────────────────────────────────────────┘
```

## 关键文件

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/main.ts` | 17 | Vue 入口 |
| `src/App.vue` | 220 | 顶层布局 + 静态加载 fixture + Zod 解析 |
| `src/components/MapView.vue` | 144 | Vue 组件,挂载 maplibre + 渲染 POI 标记 |
| `src/map/createMap.ts` | 86 | 创建 maplibre Map + 注册 pmtiles Protocol |
| `src/map/mapStyle.ts` | 145 | 16-bit RPG 配色 inline style(6 个 layer) |
| `src/map/types.ts` | 35 | CreateMapOptions / PoiMarker 类型 |
| `src/data/munich-bundle.json` | 81 | 从 `test/fixtures/` 复制,生产构建用 |
| `scripts/phase1-smoke.mjs` | 145 | Dev server smoke test(13 项) |

## 关键决策记录

### 1. PMTiles 协议注册(单例)

```ts
// src/map/createMap.ts
let protocolRegistered = false
function ensurePmtilesProtocol(): void {
  if (protocolRegistered) return
  const protocol = new Protocol()
  maplibregl.addProtocol('pmtiles', protocol.tile)
  protocolRegistered = true
}
```

- `maplibre.addProtocol` 不能重复注册(pmtiles 4.x 抛错)
- 用模块级 flag 保证整个 app 只注册一次
- `createMap` 被调用多次也安全

### 2. PMTiles URL 来源

```ts
// .env.development
VITE_PMTILES_URL=http://127.0.0.1:8081/assets/munich_map/pmtiles/germany-zoom16.pmtiles
```

- 绝对 URL + 8081 老 server(已支持 CORS `Access-Control-Allow-Origin: *`)
- 用 `pmtiles://${url}` 形式让 MapLibre 路由到 pmtiles Protocol
- Phase 2 改为 `bayern.pmtiles` 或后端代理(减小体积)

### 3. POI 数据源 = Phase 0 fixture(静态 import)

```vue
// App.vue
import bundleJson from './data/munich-bundle.json'
const parseResult = safeParseBundle(bundleJson)
if (!parseResult.ok) { state.value = { status: 'error', ... } }
```

- Vite 静态 import + Zod 校验(双层防线)
- Phase 2 替换为 `fetch('/api/game/v1/cities/munich/bundle')` + contentVersion 比较

### 4. POI 标记 = DOM 元素(不用 sprite)

```vue
<div class="gaga-poi-marker">⛪</div>
```

- 简单 32×32 圆形 + 金色 + 深蓝边,16-bit RPG 风格
- 不用 MapLibre sprite 机制 — Phase 1 简化,emoji 已够
- 不用 cluster — Phase 1 慕尼黑只有 3 个 POI

### 5. Style 层(6 个,不全用 protomaps 16 个)

```ts
layers: [
  'background',          // 兜底米色
  'water', 'water-shadow',
  'park', 'landuse',
  'road-minor/secondary/primary/motorway',  // 4 阶道路
  'building',            // zoom 13+
  'place-city',          // 城市名
]
```

- 不画: `poi`/`aerodrome_label`/`housenumber`/`transportation_name`/`boundary` 等
- 理由: 我们自己的 POI 标记已经够清晰,原生的 OSM POI label 反而干扰
- Phase 3 可加 `poi` layer 互补(原生便利店、餐厅等),玩家到哪儿都能看到完整 POI 网络

### 6. 16-bit RPG 配色

跟 `gagaToday_visual_style_guide.md` 对齐:

```
--navy     #07152b / #0d2344 / #14305c
--gold     #e8b85c / #ffcf72
--warm     #efe2c2 (背景米色)
water      #5aa5c6
park       #8fb96c
road       #d89a45 (主) / #d6c090 (次) / #b85a2a (高速)
building   #b96f4d
place label #14305c
```

### 7. Vite 端口 = 5185

```ts
server: { port: 5185, host: '127.0.0.1', strictPort: true }
```

- 5174: poi-generator(老生成器)
- 5175: hermes-agent(其他项目)
- 5181: 老 vite(归档)
- 5185: gagaToday game-client(本项目)
- 8081: 老 server.cjs(PMTiles + 静态资源)

`strictPort: true` + `host: '127.0.0.1'` — 避免冲突,macOS Node 默认 IPv6-only 要显式写 IPv4。

## 怎么验证(本地手测)

```bash
# 1. 启动老 server (8081) — 已经在跑(已有进程)
cd /Volumes/NewDisk/GermanLearning/frontend
node server.cjs

# 2. 启动新 game-client dev server
cd /Volumes/NewDisk/GermanLearning/frontend/game-client
npx vite
# → http://127.0.0.1:5185/

# 3. 浏览器打开
open http://127.0.0.1:5185/

# 4. 期待效果
# - 顶部 "gagaToday · München" 标题
# - 状态栏: "✓ 地图就绪 · 城市 munich · 3 个 POI"
# - 主区域: 慕尼黑米色背景 + 蓝色水系 + 红色道路 + 金色圆形 POI 标记(⛪ 🏛 等)
# - PMTiles 首次加载 10-30s(9.2GB,Range 请求多个 tile)
```

如果地图不显示:
1. 看浏览器 Console,有红色 error 贴回来
2. 看 Network → 找 `germany-zoom16.pmtiles` 请求,看 206 / 404 / CORS
3. `curl -I http://127.0.0.1:8081/` 确认老 server 还在
4. 重新跑 `node scripts/phase1-smoke.mjs` 看 13/13 是否还过

## 自动化烟测 (不依赖浏览器)

`scripts/phase1-smoke.mjs` 验证:

1. `.env.development` 含 `VITE_PMTILES_URL`
2. Dev server 起来
3. `index.html` 含 `#app` + `main.ts`
4. `main.ts` 200
5. 7 个关键模块(App.vue / MapView.vue / createMap.ts / mapStyle.ts / types.ts / schemas / fixture)都能 200 加载
6. PMTiles server (8081) 活着
7. PMTiles Range 206

```bash
cd /Volumes/NewDisk/GermanLearning/frontend/game-client
node scripts/phase1-smoke.mjs
# → 13/13 ✓
```

**为什么没有 Playwright 截图?**
需要先 `playwright install chromium`(~150MB 下载)。在 Phase 2/3 必然要做自动截图测试时一并装,Phase 1 先用 dev server smoke 顶一下。Phase 1.5 决定延后到 Phase 2 一起做。

## 已知限制 (Phase 1 范围内的)

| 限制 | 原因 | Phase 解决 |
|------|------|-----------|
| POI 只有 3 个 (Frauenkirche/Marienplatz/BMW Welt) | fixture 里就这么些 | Phase 4 (内容批量) |
| NPCs/Dialogues/Quests 全空 | fixture 里全空数组 | Phase 4 |
| Bundle 是静态 import,不是 API | Phase 1 验证地图,不需要后端 | Phase 2 (runtime_export_service.py + /api/game/v1/cities/...) |
| 每次冷加载都下载整套 bundle | Vite 没做缓存策略 | Phase 3 (localStorage 缓存 + contentVersion 增量) |
| PMTiles 用 9.2GB 的 germany-zoom16.pmtiles | 慕尼黑细节最好 | Phase 3 评估切到 bayern.pmtiles (547MB) |
| 没有 POI 视角雾(已发现 vs 未发现) | Phase 1 不动游戏状态 | Phase 3 (playerState.discoveredPoiIds) |
| 没有玩家位置 marker | Phase 1 还不引入玩家移动 | Phase 3 |
| 1MB JS bundle (含 maplibre) | maplibre 4.x 体积 | Phase 3 code-split |

## Phase 2 衔接点(本 Phase 不做)

1. **runtime_export_service.py** — SQLite → CityBundle 生产级导出
2. **`/api/game/v1/cities/{city}/bundle` 端点** — FastAPI 路由
3. **contentVersion 缓存** — 客户端拿 `lastContentVersion`,服务端 304 协商
4. **错误降级** — API 5xx 时用本地缓存 bundle,而不是空白地图
5. **POI 资源 URL 转换** — `file_path` → `/assets/scenes/...`(由 exporter)

## Phase 3 衔接点

1. POI 点击 → scene 切换(dialogue / image / quest)
2. 玩家位置 marker(蓝色箭头)
3. 视野雾(未发现 POI 半透明显现)
4. 任务路径(从 home 到目标 POI 的 SVG 路径)
5. 时间系统(白天/夜晚 palette 切换)
6. localStorage 存档(`gagatoday.save.v1`)

---

## 如何回滚

Phase 1 没动老代码,只新增 `frontend/game-client/` + `docs/PHASE1_MAP_INTEGRATION.md`。

```bash
# 看新文件
git status --short frontend/game-client/

# 不想要的话,直接:
rm -rf frontend/game-client/
rm docs/PHASE1_MAP_INTEGRATION.md
```

老 server.cjs / 老 index.html 一行没动。
