# gagaToday — Munich MVP Architecture

> 当前第一版实际架构 · v0.1.0 · 2026-06-22

## 版本说明

| 项 | 内容 |
|---|---|
| **状态** | 当前主线 |
| **对应设计** | [GAME_DESIGN_MUNICH_MVP.md](./GAME_DESIGN_MUNICH_MVP.md) |
| **工程分层原则** | [PROJECT_FRAMEWORK.md](./PROJECT_FRAMEWORK.md) |
| **实施计划** | [MVP_IMPLEMENTATION_PLAN.md](./MVP_IMPLEMENTATION_PLAN.md) |
| **长期架构(冻结)** | [ARCHITECTURE_v2.0_ASPIRATIONAL.md](./ARCHITECTURE_v2.0_ASPIRATIONAL.md) |

---

## 1. 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                    Game Client (Vue + Phaser)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  App.vue     │  │ Phaser       │  │  Vue Components       │  │
│  │  - 布局      │  │  - BootScene │  │  - StatusBar          │  │
│  │  - 路由      │  │  - CityScene │  │  - DialogueBox        │  │
│  └──────┬───────┘  └──────┬───────┘  │  - GameCanvas         │  │
│         │                 │          └───────────┬───────────┘  │
│         └─────────┬───────┘                      │              │
│                   ▼                              │              │
│         ┌─────────────────────┐                  │              │
│         │  Pinia Store        │◄─────────────────┘              │
│         │  stores/game.js     │                                 │
│         └─────────┬───────────┘                                 │
└───────────────────┼─────────────────────────────────────────────┘
                    ▼ import { ... } from '@/core'
┌─────────────────────────────────────────────────────────────────┐
│              Game Core (纯业务逻辑, 无 Vue/Phaser)              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ player/state │  │ economy/     │  │ tasks/tasks           │  │
│  │ createPlayer │  │   wallet     │  │ getActiveTasks        │  │
│  │ toStatusBar  │  │ spendMoney   │  │ unlockTask            │  │
│  └──────────────┘  │              │  │ completeTask          │  │
│  ┌──────────────┐  └──────────────┘  └───────────────────────┘  │
│  │ calendar/    │  ┌──────────────┐  ┌───────────────────────┐  │
│  │   time       │  │ travel/      │  │ events/effects        │  │
│  │ TIME_BLOCKS  │  │   routes     │  │ applyEffects          │  │
│  │ advanceTime  │  │ travelTo     │  └───────────────────────┘  │
│  └──────────────┘  │ findRoute    │  ┌───────────────────────┐  │
│                    └──────────────┘  │ save/localSave        │  │
│                                     │ loadPlayerState       │  │
│                                     │ savePlayerState       │  │
│                                     │ clearPlayerState      │  │
│                                     └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    ▼ import from json
┌─────────────────────────────────────────────────────────────────┐
│                Content System (JSON 数据, 不可 import .vue)      │
│  content/munich/                                                │
│  ├── player_start.json     PlayerState 工厂输入                 │
│  ├── locations.json        5 POI 坐标 + 元数据                  │
│  ├── dialogues.json        NPC 对话脚本                        │
│  ├── routes.json           路线成本 + 时间                      │
│  ├── tasks.json            Day 1 任务定义                       │
│  └── daily_events.json     每日事件(待接入)                     │
│                                                                 │
│  content/drafts/         (Phase 2/3 候选, 不可直接 import)      │
│  ├── transport/           慕尼黑 U-Bahn/S-Bahn/DB               │
│  ├── art/                 美术审计                              │
│  ├── restaurants/         Hofbräuhaus 详细                      │
│  ├── npcs/                NPC 完整档案                          │
│  ├── exploration/         11 景点 + 知识卡                      │
│  └── food/                食谱 + 食材 + 价格                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 目录结构(实际)

```
GermanLearning/
├── frontend/                          # MVP 单机 Web Demo
│   ├── package.json                   # vue/pinia/phaser/vite
│   ├── vite.config.js                 # @ → src, @assets → ../assets
│   ├── index.html                     # mount #app
│   ├── public/
│   │   └── assets/                    # 软链或复制 assets/
│   └── src/
│       ├── main.js                    # Vue + Pinia mount
│       ├── style.css                  # 全局样式
│       ├── App.vue                    # 三段布局: StatusBar + GameCanvas + DialogueBox
│       ├── components/
│       │   ├── StatusBar.vue          # 玩家状态栏
│       │   ├── GameCanvas.vue         # Phaser 挂载点
│       │   └── DialogueBox.vue        # 对话 UI
│       ├── phaser/
│       │   ├── BootScene.js           # 加载场景图 + NPC 立绘 + UI
│       │   └── CityScene.js           # 慕尼黑顶视图 + 5 POI
│       ├── core/
│       │   ├── index.js               # 统一导出 8 个模块
│       │   ├── player/state.js        # createPlayerState / toStatusBarStats
│       │   ├── economy/wallet.js      # spendMoney
│       │   ├── tasks/tasks.js         # getActiveTasks / completeTask
│       │   ├── calendar/time.js       # TIME_BLOCKS / advanceTimeBlock
│       │   ├── travel/routes.js       # travelTo / findRoute
│       │   ├── events/effects.js      # applyEffects
│       │   └── save/localSave.js      # loadPlayerState / savePlayerState
│       ├── stores/
│       │   └── game.js                # Pinia 主 store
│       └── content/
│           ├── munich/                # 已批准内容(MVP 使用)
│           │   ├── player_start.json
│           │   ├── locations.json
│           │   ├── dialogues.json
│           │   ├── routes.json
│           │   ├── tasks.json
│           │   └── daily_events.json
│           └── drafts/                # 待审核内容(不可直接 import)
│               ├── transport/
│               ├── art/
│               ├── restaurants/
│               ├── npcs/
│               ├── exploration/
│               └── food/
├── assets/
│   ├── characters/
│   │   ├── anna/                      # 4 表情: neutral/smile/surprise/thinking
│   │   └── peter/                     # 4 表情: 同上
│   ├── scenes/
│   │   └── berlin/                    # 占位图(MVP 暂用)
│   │       ├── cafe_einstein.png
│   │       ├── hauptbahnhof_interior.png
│   │       └── street_kreuzberg.png
│   ├── ui/                            # dialogue_box / button / mic / badge
│   └── references/                    # 用户参考图(供 AI 生图用)
├── docs/                              # 设计 + 架构 + Agent 文档
│   ├── GAME_DESIGN_MUNICH_MVP.md      # ← 当前设计基线
│   ├── ARCHITECTURE_MUNICH_MVP.md     # ← 当前架构基线(本文件)
│   ├── PROJECT_FRAMEWORK.md           # 工程分层原则
│   ├── MVP_IMPLEMENTATION_PLAN.md     # 12 周计划
│   ├── MVP_TASKS.md                   # Phase 0-5 任务清单
│   ├── AGENT_WORKFLOW.md              # 多 Agent 协作规范
│   ├── CONTENT_SCHEMA.md              # JSON 数据规范
│   ├── API_STACK.md                   # AI 服务栈(Phase 2 用)
│   ├── ART_ASSETS.md                  # 美术规范
│   ├── SCRIPT_METHODOLOGY.md          # 剧本方法论
│   ├── PROPOSAL.md                    # 早期提案
│   ├── GAME_DESIGN_v2.0_ASPIRATIONAL.md        # ← 长期愿景(冻结)
│   ├── ARCHITECTURE_v2.0_ASPIRATIONAL.md       # ← 长期架构(冻结)
│   ├── ACHIEVEMENT_SYSTEM_v2.0_ASPIRATIONAL.md # ← 长期成就系统(冻结)
│   ├── agents/                        # 16 个 Agent 角色定义
│   ├── agent_runs/                    # Agent 历史轨迹
│   ├── curriculum/                    # A-levels KP(Phase 2 用)
│   └── archive/                       # 归档
└── scripts/
    ├── generate_art.py                # 美术生成脚本
    └── curriculum/                    # 课程数据生成脚本
```

---

## 3. 核心模块接口(已实现)

### 3.1 `core/index.js`(统一导出)

```js
export { createPlayerState, toStatusBarStats } from '@/core/player/state';
export { applyEffects } from '@/core/events/effects';
export { spendMoney } from '@/core/economy/wallet';
export { travelTo, findRoute } from '@/core/travel/routes';
export { getActiveTasks, unlockTask, completeTask } from '@/core/tasks/tasks';
export { advanceTimeBlock, TIME_BLOCKS } from '@/core/calendar/time';
export { loadPlayerState, savePlayerState, clearPlayerState } from '@/core/save/localSave';
```

### 3.2 模块职责

| 模块 | 输入 | 输出 | 副作用 |
|---|---|---|---|
| `player/state.createPlayerState` | `player_start.json` | 完整 PlayerState | 无(纯函数) |
| `player/state.toStatusBarStats` | PlayerState | {energy, mood, stress, health, ...} | 无 |
| `economy/wallet.spendMoney` | PlayerState, amount, reason | 新 PlayerState | 写 transactions 数组 |
| `travel/routes.travelTo` | PlayerState, routes, locationId | {playerState, route, costEur, timeMin} | 写 transactions |
| `travel/routes.findRoute` | routes, fromId, toId | Route \| null | 无 |
| `tasks/tasks.getActiveTasks` | PlayerState, taskCatalog | Task[] | 无 |
| `tasks/tasks.unlockTask` | PlayerState, taskCatalog, taskId | 新 PlayerState | 写 active_task_ids |
| `tasks/tasks.completeTask` | PlayerState, taskCatalog, taskId | 新 PlayerState | 移 completed + apply rewards |
| `calendar/time.advanceTimeBlock` | PlayerState | 新 PlayerState | 写 time_block + 时间副作用 |
| `calendar/time.TIME_BLOCKS` | — | 枚举 | — |
| `events/effects.applyEffects` | PlayerState, effects | 新 PlayerState | 写 status 子字段 |
| `save/localSave.loadPlayerState` | — | PlayerState \| null | 读 localStorage |
| `save/localSave.savePlayerState` | PlayerState | void | 写 localStorage |
| `save/localSave.clearPlayerState` | — | void | 清 localStorage |

**约束**(强制):
- Core 模块**不**依赖 Vue / Phaser / DOM
- Core 模块**不**加载图片资源
- Core 模块**不**写 UI 文案
- Core 模块**不**编造真实世界数据
- 所有 mutator 返回**新 PlayerState**(immutable)

---

## 4. 数据流

### 4.1 启动流程

```
index.html → main.js
  ↓
  createApp(App) + createPinia()
  ↓
  App.vue 挂载 → StatusBar / GameCanvas / DialogueBox
  ↓
  GameCanvas 初始化 Phaser
  ↓
  BootScene 加载 assets/*(柏林占位图)
  ↓ scene.start('CityScene')
  CityScene 从 @/content/munich/locations.json 读 5 POI
  ↓
  渲染慕尼黑地图 + 5 场景点 + 连线
  ↓
  用户点击 POI → 触发 'scenePointClicked' 事件
  ↓
  Pinia game.enterScene(locationId)
  ↓
  travelTo() → 结算路线成本 + 时间 → 更新 playerState
  ↓
  currentScene = locationId / currentNpc = dialogueScripts[id]
  ↓
  DialogueBox 打开对话
```

### 4.2 任务完成流程

```
玩家选择对话选项 → nextTurn() → 最后一 turn
  ↓
  completeCurrentDialogueTask()
  ↓
  find matching task (type === 'dialogue' && target_location_id === currentScene)
  ↓
  completeTask(playerState, taskCatalog, taskId)
  ↓
  apply rewards (german_xp / life_xp / mood / cash_eur)
  ↓
  move task from active_task_ids to completed_task_ids
  ↓
  watch(playerState, deep) → savePlayerState() → localStorage
  ↓
  returnToCity() → 关闭 DialogueBox
```

### 4.3 存档恢复流程

```
浏览器加载
  ↓
  Pinia store 初始化
  ↓
  loadPlayerState() ← localStorage['player_state']
  ↓
  命中 → 恢复 playerState
  ↓
  未命中 → createPlayerState(player_start.json)
```

---

## 5. 关键设计决策

### 5.1 为什么 Vue + Canvas + SVG 分工

| 关注点 | Vue | Canvas | SVG |
|---|---|---|---|
| 状态栏 / 任务面板 | ✓ | | |
| 对话框 UI / 详情面板 | ✓ | | |
| 地图底图渲染(道路/建筑/水/公园/地铁) | | ✓ | |
| 游戏 POI 标记(大头针) | | | ✓ |
| 路线动画(红色虚线) | | | ✓ |
| Tooltip | ✓ | | |
| 全屏布局 Grid | ✓ | | |

**原则**:
- **Canvas**(pixel rendering) → 渲染 OSM 地图底图:道路/建筑/水系/公园/地铁/真实 POI,使用 pixelSnap + 16-bit 色板
- **SVG**(overlay) → 叠加可交互的游戏 POI 大头针 + 路线动画,独立于 Canvas 层
- **Vue**(DOM) → 所有 UI 面板:顶栏/左侧任务/右侧详情/底部操控

### 5.2 为什么 Core 独立

- 可单元测试(无 DOM 依赖)
- 可未来迁移到 Tauri / Electron(只搬 Client 层)
- 可未来迁移到 Godot(只搬 Core 逻辑 + 重写 Client)
- 内容 Agent 可直接读 PlayerState 校验 JSON

### 5.3 为什么 Drafts 不可直接 import

`@/content/munich/*` 是已批准的运行时数据。
`@/content/drafts/*` 是 Agent 输出,需要 review → approved 后才能移入。

**编译期防护**:Drafts 目录结构与人手 / Agent 工作目录分离,前端代码 import 路径不允许穿越。

### 5.4 为什么地图改用 OSM 真实数据

当前地图系统(`munich-map-demo.html`)已从 Phaser 手绘场景图升级为 **OSM GeoJSON 数据驱动 Canvas 像素渲染**:

| 对比 | 旧版(Phaser) | 新版(Canvas+SVG) |
|---|---|---|
| 数据来源 | 手绘占位图 | OpenStreetMap Overpass API |
| 地图要素 | 5 个固定场景图片 | 42,878 GeoJSON features |
| 道路 | 无 | 17,178 条(primary/tertiary/residential...) |
| 建筑 | 无 | 14,597 栋(Polygon 轮廓) |
| 水系 | 无 | 86 条(Isar/溪流/湖) |
| 公园 | 无 | 1,183 块(英国花园等) |
| 地铁/铁路 | 无 | 6,715 条(station/rail/subway/tram) |
| 真实 POI | 无 | 2,427 个(餐厅/咖啡馆/超市/博物馆…) |
| 渲染方式 | Phaser 图片 | Canvas 像素绘制 + pixelSnap |

---

## 6. 当前可跑通的验证

```bash
cd /Volumes/NewDisk/GermanLearning/frontend

# 启动 dev(已在 PID 19882 监听 5173)
npm run dev

# 验证模块编译
curl http://127.0.0.1:5173/src/main.js                # ✓
curl http://127.0.0.1:5173/src/App.vue               # ✓
curl http://127.0.0.1:5173/src/phaser/BootScene.js   # ✓
curl http://127.0.0.1:5173/src/content/munich/locations.json  # ✓

# 浏览器访问
open http://127.0.0.1:5173/
# → 顶部 StatusBar / 中部 Phaser CityScene / 底部 DialogueBox
```

---

## 7. 范围外(本架构不做)

| 项 | 不做的原因 | 何时做 |
|---|---|---|
| 用户系统(注册/登录) | MVP 用本地 UUID | Phase 3 |
| 云存档 | MVP 用 localStorage | Phase 3 |
| 后端 AI Gateway | MVP 用固定剧本 | Phase 2 |
| 实时路线 API | MVP 用 routes.json 预设 | Phase 3 |
| 全德国地图 | MVP 只慕尼黑 | Phase 2 |
| Godot 迁移 | 等玩法验证 | Phase 3+ |
| A-levels 全量 | Phase 2 用 drafts/curriculum 部分 | Phase 2 |
| 移动端 App | MVP 只 Web | Phase 4 |

---

## 8. 跟 v2.0 长期架构的关系

[ARCHITECTURE_v2.0_ASPIRATIONAL.md](./ARCHITECTURE_v2.0_ASPIRATIONAL.md) 描述的是:
- Track 系统 + NPC lang_pref + RPG stats(EN/D/DEX/...)
- LearningUnit + 结局 + ~250 L/XP 路径
- Track A/B/C + event bus + Service 接口

这些是**长期架构演进方向**,不在 MVP 范围。当前 MVP 架构**不**引入这些 — 等玩法闭环跑通后再讨论是否升级。

---

## 9. 地图渲染管线(2026-06-22 新增)

### 9.1 数据来源

```
OpenStreetMap (Overpass API)
  ↓ osm_to_geojson.py (6 层分步查询)
assets/munich_map/munich.geojson (42,878 features, 12 MB)
  ↓ HTTP fetch (或 munich_fallback.geojson 3,000 featured)
mapGeoJSON (内存中的 FeatureCollection)
```

**GeoJSON 结构**完全兼容 OSM 标准,后续只需重新运行脚本即可拉取最新数据。

### 9.2 渲染层级

```
L1: 羊皮纸底色 (#efe2c2)
L2: 水系 (Polygon, #5aa5c6 / 描边 #2d6f94)
L3: 公园/绿地 (Polygon, #8fb96c / 描边 #547d40)
L4: 地铁/铁路 (LineString, U3 橙/U6 蓝, dash)
L5: 道路 (按 highway 类型: primary 7px → footway 2.5px)
L6: 真实 POI (z16+, 按类型分色小点)
L7: 建筑 (z15+, Polygon, 统一 #b96f4d / 描边 #523225)
──────────── Canvas ↑  SVG ↓ ────────────
L8: 游戏 POI (大头针, z16+, 脉动光环, 可点击)
L9: 路线动画 (红色虚线, stroke-dasharray)
L10: UI 面板 (Vue DOM 层: 顶栏/左面板/右面板/底栏)
```

### 9.3 Web Mercator 投影

```js
function lngLatToWorld(lng, lat, zoom) {
  const scale = 256 * Math.pow(2, zoom);
  const x = (lng + 180) / 360 * scale;
  const sinLat = Math.sin(lat * Math.PI / 180);
  const y = (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale;
  return { x, y };
}
```

所有坐标通过 `pixelSnap` 取整,Canvas `imageSmoothingEnabled = false`。

### 9.4 Zoom 分级

| Zoom | 显示内容 |
|------|---------|
| 11 | 主干道 + 公园 + 河流 + 地铁线 |
| 12 | 次级道路 |
| 13 | 三级道路 + 地铁站 |
| 14 | 详细道路 + 标注 |
| 15 | 建筑轮廓 + 住宅道路 |
| 16 | 步行道 + 真实 POI 小点 + 游戏 POI 标记 |
| 17 | 最高细节 |

### 9.5 操作方式

| 操作 | 触发 | 说明 |
|------|------|------|
| 平移 | 鼠标拖拽 / ←↑↓→ 方向键 | 步长 20px |
| 缩放 | 鼠标滚轮 / `-` `=` 键 / `+` `−` 按钮 | 范围 11-17 |
| 点击 POI | 点击大头针标记 | 右侧弹出详情面板 |
| 显示路线 | 详情面板 → "显示路线" | 红色虚线动画 |
| 重置视角 | "🎯 重置" 按钮 | 回到 Marienplatz zoom 15 |

### 9.6 16-bit RPG 色板

| 要素 | 颜色 |
|------|------|
| 背景 | `#efe2c2` (羊皮纸) |
| 水面 | `#5aa5c6` / 描边 `#2d6f94` |
| 公园 | `#8fb96c` / 描边 `#547d40` |
| 主路 | `#d89a45` / 描边 `#76512b` |
| 住宅路 | `#f4e7c3` / 描边 `#bba574` |
| 建筑 | `#b96f4d` / 描边 `#523225` |
| UI 面板 | `#07152b` (深蓝) / `#e8b85c` (金色) |
| 游戏 POI | 按类型: 蓝(home) / 绿(school) / 橙(shop) / 红(landmark) / 紫(museum) |

### 9.7 文件位置

| 文件 | 作用 |
|------|------|
| `frontend/munich-map-demo.html` | 单文件 Demo: HTML + CSS + JS (异步加载 GeoJSON) |
| `scripts/map/osm_to_geojson.py` | OSM 数据拉取脚本 (6 层 Overpass query) |
| `assets/munich_map/munich.geojson` | 完整 GeoJSON (42,878 features, 12 MB, 不入 git) |
| `assets/munich_map/munich_fallback.geojson` | 精简版 fallback (3,000 features, ~1 MB, 入 git) |
| `copilot-instructions.md` | 项目工作规则(语言/Git/Docker/限制) |

### 9.8 与 Phaser 老系统的关系

Phaser 场景(`BootScene.js` / `CityScene.js` / `HomeScene.js`)在 `src/` 中保留,供 Vue 主应用 (`App.vue`) 使用。

新地图 Demo (`munich-map-demo.html`) 是完全独立的单文件,不依赖 Phaser/Vue/Pinia,纯 HTML+CSS+JS 即可运行:

```bash
cd frontend && python3 -m http.server 8081
# 打开 http://127.0.0.1:8081/munich-map-demo.html
```

---

## 10. 变更日志

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-06-22 | v0.1.1 | 新增 §9: OSM GeoJSON Canvas+SVG 地图渲染管线 |
| 2026-06-22 | v0.1.0 | 新建 — 基于实际跑通的 Vue/Phaser/Core 三层架构 |