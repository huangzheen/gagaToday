# Phase 3: 玩家状态机 + POI 交互

> 完成日期: 2026-06-30
> 范围: A(状态机) + B(POI 交互)
> 结果: 地图从「静态背景」升级为「可玩游戏」

## 一句话总结

Pinia player store 落地 PlayerState(playerPosition + visionRadius + day/time/energy/money/xp),HUD 显示实时状态,点击 POI marker 弹出详情面板(图 + 描述 + 音频 + 进入对话),未发现 POI 自动变灰,游戏时钟每秒推进 1 分钟。

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│  App.vue (orchestrator)                                          │
│  - 启动时 load player store (localStorage) + fetch bundle       │
│  - 渲染 HUD + PoiDialog + MapView                                │
│  - 启动 useGameClock (每秒 tick)                                 │
└───────┬───────────────────┬───────────────────┬──────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌─────────────────┐
│  HUD.vue     │    │  PoiDialog   │    │  MapView.vue    │
│  右下角      │    │  右下角上方  │    │  全屏 + 控件     │
│  Day/HH:MM   │    │  POI 详情    │    │  POI markers    │
│  Energy/€XP  │    │  Scene 图    │    │  + 玩家 marker  │
│  Position    │    │  Audio       │    │  + 视野过滤     │
└──────┬───────┘    └──────┬───────┘    └────────┬────────┘
       │                   │                     │
       └───────────────────┴─────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  store/player.ts        │
              │  Pinia store            │
              │  - state: PlayerState   │
              │  - actions: openPoi     │
              │              move       │
              │              tickTime   │
              │  - persist: localStorage│
              └─────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌────────────────────┐   ┌────────────────────────┐
   │  composables/      │   │  schemas/save.ts       │
   │  useGameClock      │   │  - PlayerStateSchema   │
   │  - setInterval     │   │  - PlayerPositionSchema│
   │  - 1秒 = 1分钟     │   │  - haversineMeters()   │
   │  - isPaused 尊重   │   │  - migrateV1ToV2()     │
   └────────────────────┘   └────────────────────────┘
```

## 文件清单

| 文件 | 角色 | 行数 |
|------|------|------|
| `frontend/game-client/src/schemas/save.ts` | PlayerState schema v1 → v2(加 playerPosition/visionRadius/currentCity) | 165 |
| `frontend/game-client/src/store/player.ts` | Pinia store:state + actions + 自动持久化 + v1→v2 迁移 | 245 |
| `frontend/game-client/src/composables/useGameClock.ts` | 游戏内时钟,每秒 = 1 分钟,可暂停 | 60 |
| `frontend/game-client/src/components/HUD.vue` | 右下角 HUD(Day/HH:MM/Energy/Money/XP/Position) | 175 |
| `frontend/game-client/src/components/PoiDialog.vue` | POI 详情面板(图 + 描述 + 音频 + 进入对话) | 280 |
| `frontend/game-client/src/components/MapView.vue` | 加 player marker + undiscovered POI 样式过滤 | 380 |
| `frontend/game-client/src/App.vue` | 串联:load player + fetch bundle + start clock + 渲染 HUD/dialog | 245 |
| `frontend/game-client/scripts/phase1-smoke.mjs` | 扩到 25 项(原 20 + Phase 3 5 项) | 230 |

## 关键设计

### 1. PlayerState schema v1 → v2 迁移

```typescript
// v1 (Phase 2): 只有 day/time/energy/xp 等资源维度
// v2 (Phase 3): 加地图相关字段
playerPosition: { lng, lat } | null  // null = 还没开始移动
visionRadiusMeters: 500               // 默认 500m 视野
currentCity: string | null            // null = 未选择城市
```

**自动迁移**:打开页面时,如果 localStorage 是 v1,自动用 `migrateV1ToV2()` 补默认值,迁移完写回 v2。v1 损坏或不可识别时备份到 `gagatoday.save.v1.invalid.<timestamp>` 然后清掉。

### 2. Pinia store 模式 — setup style

用 `defineStore('player', () => { ... })` setup 写法,而非 Options API 写法:
- 自动推断 types
- 直接用 `ref` / `computed` / `watch`
- `return` 出去的全是公开的(state + actions + getters)

### 3. 自动持久化

```typescript
watch(player, () => {
  if (saveTimer !== null) window.clearTimeout(saveTimer)
  saveTimer = window.setTimeout(() => {
    saveToStorage()  // 500ms debounce 写 localStorage
  }, 500)
}, { deep: true })
```

任何 player 字段变化(energy 减了、POI discovered、位置改了)→ 500ms 后写一次 localStorage,避免每帧写。

### 4. 视野自动发现(discoverInVision)

```typescript
function discoverInVision(pois: RuntimePoi[]) {
  const before = new Set(player.discoveredPoiIds)
  const added = pois.filter(p => !before.has(p.id) && isInVision(p))
  if (added.length > 0) {
    player.discoveredPoiIds = [...player.discoveredPoiIds, ...added.map(p => p.id)]
  }
}
```

进入新城市 / 移动玩家 / bundle 加载 → 自动发现视野内 POI。Phase 3 默认玩家在城市中心(慕尼黑 [11.5755, 48.1374]),3 个 POI 都在 1km 内,所以打开页面就能发现全部。

### 5. 时间推进策略

- **真实 1 秒 = 游戏内 1 分钟**(可在 `useGameClock` 调)
- 现实 24 分钟 = 游戏 1 天
- `tickTime` 由 setInterval 每 1000ms 触发
- POI dialog 打开时 `isPaused = true`,时间暂停(让玩家细看场景)
- `day` 自动 +1 当 `minuteOfDay >= 1440`

### 6. POI 视觉二态

| 状态 | 样式 | 数据来源 |
|------|------|---------|
| 已发现 | 金色圆形 + emoji + 内嵌高光 | `player.discoveredPoiIds.includes(id)` |
| 未发现 | 灰色半透明 + grayscale(70%) + cursor not-allowed | 不在 discovered 集合 |

切换不重建 marker,只 toggle CSS class(`watch(discoveredSet)`)。

### 7. 玩家 marker

🧑 emoji + 蓝色方形 + 内嵌高光,`anchor: bottom`(脚在坐标点上)。位置变化时只 `renderPlayerMarker()`,不重建 POI markers。

### 8. POI Dialog 布局

- **右下角,320px 宽**(不覆盖地图中心)
- **位置**:`bottom: 220px` 在 HUD 上方
- **内容**:icon + 名字(de/zh) + type + 距离 + 主图 + 描述 + audio + 按钮
- **transition**:scale + translateY 200ms 进入/退出

## 验证矩阵

| 验证项 | 结果 |
|--------|------|
| typecheck (vue-tsc) | ✓ 0 errors |
| vitest | ✓ 17/17(原 + 没回归) |
| vite build | ✓ 1.86s, 979KB JS / 74KB CSS(+24KB JS / +6KB CSS,Pinia+HUD+Dialog) |
| dev server smoke | ✓ **25/25**(原 20 + Phase 3 5 项) |
| Backend 回归 | ✓ 59/59 |
| Hot reload | ✓ HMR 自动应用,无 console error |

### Smoke 新增 5 项 Phase 3

- `GET /src/components/HUD.vue` → 200
- `GET /src/components/PoiDialog.vue` → 200
- `GET /src/store/player.ts` → 200
- `GET /src/composables/useGameClock.ts` → 200
- `App.vue` 含 `usePlayerStore` + `HUD` + `PoiDialog`

## 端到端操作流程

1. **打开 http://127.0.0.1:5185/**
2. 看到:
   - 顶部蓝金 bar:gagaToday · München · v1.20260630.69050521 · [network] · 已发现 3
   - 地图:3 个金色 emoji POI(已发现,因为玩家在城市中心)+ 蓝色 🧑 玩家 marker
   - 右下角 HUD:`Day 1 · ☀ 08:00 · EP ▮▮▮▮▮▮▮▮▮▮ · €20.00 · ★0 XP · 📍 48.1374, 11.5755`
3. **点击任一 POI**(比如 Frauenkirche ⛪)
   - 右下角上方弹出 dialog,显示场景图 + 名字 + type + 距离 + audio
   - 顶部 bar 显示 `[paused]`(时间暂停)
   - 玩家可以放 audio,看 description
4. **点"离开"**
   - dialog 消失,时间恢复推进
   - minuteOfDay 开始 +1(观察 HUD 时间在变)
5. **刷新页面**
   - player state 持久化:day / energy / discovered 都在(除非能量被消耗,Phase 4 接 quest 后才有消耗场景)
   - HUD 显示旧的位置 / 时间

## 已知限制

- **玩家不能自由移动** — 当前 setPosition 只能由代码调,用户不能拖玩家 marker
  - 解决方案:Phase 3.1 加点击地图 setPosition,或拖动玩家 marker
- **POI 视野固定 500m** — 玩家移远了所有 POI 都会变灰
  - 解决方案:Phase 3.1 加 zoom-aware vision(zoom in = vision 缩小,zoom out = vision 扩大)
- **Audio 没真正测试** — 浏览器 autoplay policy 可能阻止,需要用户先交互
- **时间暂停只 POI dialog 触发** — 没暂停按钮
- **没有 save 按钮** — 自动持久化,但没"导出存档 JSON"功能
- **没有玩家图片 sprite** — 用 emoji 🧑,Phase 5+ 换真 sprite

## 衔接点(Phase 4+)

1. **NPC + 对话** — exporter 加载 NPC 数据,点 POI 后选 "开始对话" 进入对话 UI(Dialogue engine)
2. **Quest 触发** — POI dialog 显示 quest 列表,完成后给 reward(XP + 金钱 + energy)
3. **玩家自由移动** — 地图上点击 → setPosition(直接传 lng/lat) 或拖动玩家 marker
4. **暂停按钮 + 时间倍率** — HUD 加 ⏸ / ▶ / ⏩ 按钮,支持 1x / 2x / 4x
5. **视野半径可视化** — 玩家周围画一个半透明圆,直观看到视野范围
6. **声音** — 加背景音乐 + 脚步声 + 公交到站声

## 决策回顾

| 决策 | 选项 | 选了 | 为什么 |
|------|------|------|--------|
| 时间倍率 | 1秒=1分钟 vs 1秒=10分钟 | 1秒=1分钟 | 24分钟现实 = 1天游戏,体验合理 |
| 暂停触发 | POI dialog / 全局 | POI dialog | 玩游戏的人不需要全局暂停,细节查看用 |
| 持久化时机 | 立即写 / debounce | 500ms debounce | 防止高频变化每帧写 IO |
| vision radius | 100m / 500m / 1km | 500m | 慕尼黑老城 POI 都覆盖,初始能 discover 全部 |
| 玩家 marker | emoji / SVG / sprite | emoji 🧑 | 16-bit RPG 风格 + 零素材成本,Phase 5 换 sprite |
| POI 未发现样式 | 隐藏 / 灰显 / 迷雾 | 灰显 | 留位置感(玩家知道去哪),不剧透名字 |