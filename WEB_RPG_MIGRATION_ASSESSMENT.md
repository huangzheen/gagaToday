# gagaToday Web RPG 迁移实施手册

> 项目目录：`/Volumes/NewDisk/GermanLearning`  
> 文档日期：2026-06-28  
> 面向对象：接手本项目迁移工作的 Codex、Claude、Mavis、OpenClaw 或其他开发 Agent  
> 文档性质：执行规范（Runbook），不是愿景讨论稿  
> 硬约束：必须保留德国全境真实地图  

---

## 0. 这份文档的目的

这份文档用于指导 Agent 将当前 gagaToday 地图原型逐步升级为可维护、可测试、可发布的真实地图 Web RPG。

Agent 读完后，应当清楚知道：

1. 为什么要迁移；
2. 最终要交付什么；
3. 哪些现有模块必须保留；
4. 哪些代码需要替换或新增；
5. 应按什么顺序实施；
6. 每一步如何测试；
7. 出错时如何定位和纠正；
8. 达到什么标准才算验收通过。

### 0.1 一句话任务

> 保留现有 PMTiles、OSM、FastAPI、SQLite、内容生成器和美术语音资产，将手写 Vanilla JS 地图运行时迁移为 MapLibre GL JS + Vue 3 + TypeScript 客户端，并建立独立 Game Core，最终打通“真实地图 → POI → 德语任务 → 奖励 → 地图变化 → 存档”的完整闭环。

### 0.2 最终成功状态

迁移完成后，项目至少应满足：

- 德国全境真实地图可以加载、缩放和浏览；
- 慕尼黑游戏 POI 可以从正式运行时 API 加载；
- 玩家点击 POI 后可以进入一个确定性的学习任务；
- 完成任务后玩家获得奖励，POI 状态发生变化；
- 刷新或重启后进度仍然存在；
- 内容生产工具与玩家客户端彼此隔离；
- 地图、游戏规则、UI、后端数据均有自动化测试；
- 任一失败都能通过日志、错误状态或测试定位，而不是静默失效。

### 0.3 本次迁移不是做什么

本迁移不是：

- 将项目迁移到 Godot；
- 用 GDScript 重写 PMTiles 或 MVT；
- 立即实现德国所有城市；
- 立即实现全部德语、IELTS 和 A-levels 课程；
- 把 9.2GB 地图直接打进首版安装包；
- 让 AI 自动控制主线或自动发布未经审核的教学内容；
- 重写已经可用的 Vue 内容生成器和 FastAPI AI 服务。

---

## 1. Agent 开工规则

所有 Agent 在改代码前必须执行本节。不得跳过。

### 1.1 必读顺序

1. 本文档；
2. `README.md`；
3. `docs/ARCHITECTURE.md`；
4. `docs/POI_CONTENT_GENERATOR_PLAN.md`；
5. `gagaToday_visual_style_guide.md`；
6. 当前任务直接涉及的代码文件。

`archive/docs/` 只能作为历史参考，不得把其中的远期方案误当成当前实现。

### 1.2 开工前基线检查

```bash
cd /Volumes/NewDisk/GermanLearning
git status --short
git log -5 --oneline --decorate
rg --files -g '!node_modules/**' -g '!*.lock' | sed -n '1,240p'
```

Agent 必须在进度说明中记录：

- 当前分支和 HEAD；
- 工作区是否已有用户修改；
- 本任务会修改哪些文件；
- 哪些已有修改必须避开。

不得覆盖、回滚或整理不属于当前任务的用户改动。不得使用 `git reset --hard`、`git checkout --` 等破坏性命令。

### 1.3 密钥安全

- 不得 `cat`、打印或复制 `/Volumes/NewDisk/.agent-secrets/secrets.env`；
- 只有确实需要运行 AI/API 集成测试时才能在进程中 `source`；
- 日志、测试快照和错误信息不得包含密钥；
- 前端不得获得任何模型 API key；
- Admin API 与 Game API 必须隔离。

### 1.4 实施粒度

一次任务只完成一个可独立验收的阶段。每个阶段结束前必须：

1. 运行该阶段测试；
2. 检查 `git diff --check`；
3. 检查 `git status --short`；
4. 记录已完成、未完成、风险和下一步；
5. 未经用户要求，不自动 commit 或 push。

### 1.5 遇到以下情况应停止扩展范围

- PMTiles Range 请求仍不稳定；
- 运行时 schema 尚未冻结；
- 第一个任务闭环尚未通过；
- 自动化测试仍有失败；
- 必须覆盖用户未提交改动才能继续；
- 需要改变产品主线或引入新的付费服务。

停止扩展不代表停止排查。Agent 应先提供证据、最小复现和两个可选方案。

---

## 2. 当前项目事实与迁移边界

### 2.1 当前模块

| 模块 | 当前技术 | 处理方式 |
|---|---|---|
| 地图运行时 | Vanilla JS + Canvas + SVG + PMTiles | 替换为 MapLibre + Vue + TypeScript |
| POI 内容生成器 | Vue 3 + Pinia + Vite | 保留，只做接口适配 |
| 内容/AI 后端 | FastAPI | 保留，拆分 Admin/Game API |
| 内容数据库 | SQLite | 内容生产阶段保留 |
| OSM/PMTiles 工具 | Python、Node、Planetiler | 保留为离线生产工具 |
| 场景图与语音 | PNG/JPEG/MP3 | 复用，但需格式检查 |
| RPG 核心 | 尚未形成正式模块 | 新建纯 TypeScript Game Core |
| Phaser | 历史使用/依赖残留 | 只在 POI 内部场景按需启用 |

### 2.2 审计时的数据成熟度

审计时数据库约有：

- 3 个已发布 POI；
- 4 条场景记录；
- 3 条 `info` 内容；
- 尚无正式发布的 NPC、Dialogue、Quest、KnowledgeCard 游戏内容。

Agent 不得假设这些数量永远不变。实施前应重新运行只读查询：

```bash
sqlite3 backend/poi-generator/game_data.db \
  "select 'pois', count(*) from pois
   union all select 'published', count(*) from pois where is_published=1
   union all select 'scenes', count(*) from poi_scenes
   union all select 'content', count(*) from poi_content;"
```

### 2.3 保留与重建边界

必须保留：

- PMTiles 文件和生成链；
- OSM 真实坐标；
- FastAPI 的 LLM、图片、TTS、Wiki、OSM 服务；
- Vue POI 生成器；
- SQLite 内容数据；
- 现有场景图和音频；
- 视觉风格规范。

需要重建：

- 地图运行时；
- 正式玩家客户端；
- Game API；
- 运行时内容 schema；
- Game Core；
- 存档、任务和地图状态同步；
- 自动化测试与验收脚本。

---

## 3. 目标架构与目录

### 3.1 目标数据流

```text
Vue POI Generator
       │ 生成和编辑草稿
       ▼
FastAPI Admin API
       │ 人工审核并发布
       ▼
SQLite / Published Content
       │ 导出版本化城市内容包
       ▼
FastAPI Game API / CDN
       │
       ▼
Vue + TypeScript Game Client
├── MapLibre：德国真实地图
├── Game Core：任务和规则
├── Pinia：界面状态
├── Local Save：本地进度
└── Phaser：地点内部场景（后续）
```

### 3.2 推荐目录

```text
frontend/
├── game-client/                 # 新玩家客户端
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── core/
│   │   ├── map/
│   │   ├── scenes/
│   │   ├── schemas/
│   │   ├── stores/
│   │   └── test/
│   └── public/
├── poi-generator/               # 保留的内部 CMS
├── index.html                   # 旧原型，迁移期间只读对照
└── server.cjs                   # 迁移初期继续提供 Range

backend/poi-generator/
├── routers/
│   ├── admin_*.py               # 后续整理
│   └── game.py                  # 新增只读运行时 API
├── schemas/
│   └── game_content.py
└── services/
    └── runtime_export_service.py

packages/
└── content-schema/              # 可在第二阶段抽出
```

不要在第一天大规模移动旧文件。先新建 `frontend/game-client/` 完成垂直切片，验收通过后再决定删除或归档旧地图入口。

---

## 4. 总体实施顺序

必须按以下顺序执行：

1. Phase 0：冻结 MVP 与数据契约；
2. Phase 1：验证 MapLibre + 现有 PMTiles；
3. Phase 2：建立正式 Game API 和城市内容包；
4. Phase 3：迁移地图客户端；
5. Phase 4：建立 Game Core 和存档；
6. Phase 5：打通第一个学习闭环；
7. Phase 6：性能、离线与桌面包装验证；
8. Phase 7：扩大内容规模。

任何 Agent 不得在 Phase 5 通过前直接开始德国多城市批量生产。

---

## 5. Phase 0：冻结 MVP 与运行时数据契约

### 5.1 目标

让前端、后端和内容生成器对“运行时数据长什么样”达成唯一约定。

首个 MVP 固定为：

- 城市：慕尼黑；
- 时长：一个游戏日；
- POI：3–5 个；
- 黄金 POI：Marienplatz 或 Frauenkirche；
- 闭环：接任务 → 地图前往 → 对话/德语任务 → 奖励 → 地图状态变化 → 存档。

### 5.2 建议新增文件

```text
frontend/game-client/src/schemas/content.ts
frontend/game-client/src/schemas/save.ts
backend/poi-generator/schemas/game_content.py
docs/RUNTIME_CONTENT_SCHEMA.md
```

### 5.3 TypeScript schema 示例

推荐使用 Zod 做运行时边界验证。示例：

```ts
import { z } from 'zod'

export const LocalizedTextSchema = z.object({
  de: z.string().min(1),
  zh: z.string().min(1),
  en: z.string().optional(),
})

export const PoiSchema = z.object({
  id: z.string().min(1),
  city: z.string().min(1),
  type: z.string().min(1),
  name: LocalizedTextSchema,
  position: z.object({
    lat: z.number().gte(-90).lte(90),
    lng: z.number().gte(-180).lte(180),
  }),
  description: LocalizedTextSchema.partial(),
  iconUrl: z.string().optional(),
  sceneUrls: z.array(z.string()).default([]),
  questIds: z.array(z.string()).default([]),
  published: z.boolean(),
})

export const CityBundleSchema = z.object({
  schemaVersion: z.literal(1),
  contentVersion: z.string().min(1),
  city: z.string().min(1),
  generatedAt: z.string().datetime(),
  pois: z.array(PoiSchema),
  npcs: z.array(z.unknown()),
  dialogues: z.array(z.unknown()),
  quests: z.array(z.unknown()),
  knowledgeCards: z.array(z.unknown()),
})
```

示例中的 `unknown()` 只允许在 Phase 0 临时使用。进入对应功能开发前必须换成严格 schema。

### 5.4 Python DTO 示例

```py
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Position(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)

class LocalizedText(BaseModel):
    de: str
    zh: str
    en: Optional[str] = None

class RuntimePoi(BaseModel):
    id: str
    city: str
    type: str
    name: LocalizedText
    position: Position
    description: Dict[str, str] = Field(default_factory=dict)
    iconUrl: Optional[str] = None
    sceneUrls: List[str] = Field(default_factory=list)
    questIds: List[str] = Field(default_factory=list)
    published: bool = True

class CityBundle(BaseModel):
    schemaVersion: int = 1
    contentVersion: str
    city: str
    generatedAt: datetime
    pois: List[RuntimePoi]
    npcs: List[dict] = Field(default_factory=list)
    dialogues: List[dict] = Field(default_factory=list)
    quests: List[dict] = Field(default_factory=list)
    knowledgeCards: List[dict] = Field(default_factory=list)
```

该写法兼容项目审计时存在的 Python 3.9 环境，并避免可变默认值在实例之间共享。

### 5.5 测试

前端：

```ts
import { describe, expect, it } from 'vitest'
import { CityBundleSchema } from './content'
import fixture from '../test/fixtures/munich-bundle.json'

describe('CityBundleSchema', () => {
  it('accepts the approved Munich fixture', () => {
    expect(CityBundleSchema.parse(fixture).city).toBe('munich')
  })

  it('rejects invalid coordinates', () => {
    const bad = structuredClone(fixture)
    bad.pois[0].position.lat = 120
    expect(() => CityBundleSchema.parse(bad)).toThrow()
  })
})
```

后端：

```py
def test_city_bundle_rejects_invalid_latitude():
    payload = make_valid_bundle()
    payload["pois"][0]["position"]["lat"] = 120
    with pytest.raises(ValidationError):
        CityBundle.model_validate(payload)
```

### 5.6 常见错误与纠正

| 错误 | 原因 | 纠正 |
|---|---|---|
| 前端字段叫 `lng`，后端叫 `lon` | 无统一 DTO | 只在 exporter 做一次映射，运行时统一为 `lng` |
| 空字符串进入地图 | 草稿未审核 | schema 使用 `min(1)`，发布时拒绝 |
| `acts` 有时是字符串、有时是数组 | SQLite JSON blob 泄漏到客户端 | exporter 统一反序列化 |
| 旧内容突然无法加载 | schema 无版本 | 添加 `schemaVersion` 和迁移函数 |

### 5.7 验收标准

- 存在一份可验证的 Munich fixture；
- TypeScript 和 Pydantic 对同一 fixture 均通过；
- 非法坐标、缺名称、错误版本均会失败；
- schema 文档明确字段和版本策略；
- 生成器草稿不能直接冒充已发布运行时数据。

---

## 6. Phase 1：MapLibre + PMTiles 技术验证

### 6.1 目标

在不重写业务逻辑的情况下，证明 MapLibre 能稳定读取现有德国 PMTiles，并显示慕尼黑及当前 POI。

### 6.2 推荐依赖

```bash
cd frontend/game-client
npm install maplibre-gl pmtiles zod pinia
npm install -D vitest @vue/test-utils jsdom
```

首次创建 Vite 项目时选择 Vue + TypeScript。Agent 不得删除旧 `frontend/index.html`。

### 6.3 PMTiles Range 服务验证

先启动当前静态服务器：

```bash
cd /Volumes/NewDisk/GermanLearning/frontend
node server.cjs
```

再验证 Range：

```bash
curl -sS -r 0-16383 -o /dev/null -D - \
  http://127.0.0.1:8081/assets/munich_map/pmtiles/germany-zoom16.pmtiles
```

必须看到：

```text
HTTP/1.1 206 Partial Content
Accept-Ranges: bytes
Content-Range: bytes 0-16383/...
```

如果返回 200、404 或没有 `Content-Range`，先修 Range 服务，不要继续调 MapLibre。

### 6.4 MapLibre 初始化示例

`src/map/createMap.ts`：

```ts
import maplibregl, { type Map } from 'maplibre-gl'
import { PMTiles, Protocol } from 'pmtiles'
import 'maplibre-gl/dist/maplibre-gl.css'

const protocol = new Protocol()
maplibregl.addProtocol('pmtiles', protocol.tile)

export function createMap(container: HTMLElement): Map {
  const archiveUrl = import.meta.env.VITE_PMTILES_URL
  if (!archiveUrl) throw new Error('VITE_PMTILES_URL is required')

  const archive = new PMTiles(archiveUrl)
  protocol.add(archive)

  return new maplibregl.Map({
    container,
    center: [11.5761, 48.1372],
    zoom: 13,
    minZoom: 5,
    maxZoom: 16,
    attributionControl: true,
    style: {
      version: 8,
      sources: {
        germany: {
          type: 'vector',
          url: `pmtiles://${archiveUrl}`,
          attribution: '© OpenStreetMap contributors',
        },
      },
      layers: [
        { id: 'background', type: 'background', paint: { 'background-color': '#EFE2C2' } },
      ],
    },
  })
}
```

`.env.development` 只保存非敏感 URL：

```dotenv
VITE_PMTILES_URL=http://127.0.0.1:8081/assets/munich_map/pmtiles/germany-zoom16.pmtiles
VITE_GAME_API_URL=http://127.0.0.1:8000
```

### 6.5 确认 source-layer，禁止猜测

PMTiles 中的图层名由生成配置决定。不要直接假定为 `roads`、`building` 或 `water`。

定位方式：

1. 查看已有 `frontend/index.html` 如何遍历 `tile.layers`；
2. 使用 PMTiles/Planetiler 提供的 inspection 工具；
3. 在 MapLibre `sourcedata`/error 事件中记录加载状态；
4. 先只放 background，逐个加入经过确认的 source-layer。

示例日志：

```ts
map.on('error', event => {
  console.error('[maplibre]', event.error)
})

map.on('sourcedata', event => {
  if (event.sourceId === 'germany' && event.isSourceLoaded) {
    console.info('[map] Germany PMTiles source loaded')
  }
})
```

### 6.6 Vue 生命周期要求

Map 实例只能创建一次，组件卸载时必须释放：

```vue
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type { Map } from 'maplibre-gl'
import { createMap } from '@/map/createMap'

const container = ref<HTMLElement | null>(null)
let map: Map | undefined

onMounted(() => {
  if (!container.value) return
  map = createMap(container.value)
})

onBeforeUnmount(() => {
  map?.remove()
  map = undefined
})
</script>

<template><div ref="container" class="map-root" /></template>
```

不要把 Map 实例放进深度响应式对象；可使用普通变量或 `shallowRef`。

### 6.7 测试

自动化测试重点测试配置和模块边界，不在 jsdom 中假装测试 WebGL：

- 环境变量缺失时抛出清晰错误；
- style builder 输出合法结构；
- 经纬度转换和 GeoJSON 构造；
- Vue 组件卸载调用 `map.remove()`；
- Playwright 在真实浏览器中做地图冒烟测试。

Playwright 冒烟测试示例：

```ts
test('loads the Munich map', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByTestId('map-status')).toHaveText('ready')
  await expect(page.locator('.maplibregl-canvas')).toBeVisible()
  await expect(page.getByText('© OpenStreetMap contributors')).toBeVisible()
})
```

### 6.8 故障排查

| 症状 | 优先检查 | 纠正 |
|---|---|---|
| 空白地图 | 控制台 WebGL/Style 错误 | 先只保留 background，再逐层添加 |
| PMTiles 404 | URL 和 server 路径 | 用 curl 验证相同 URL |
| CORS 错误 | Range 响应头 | 确保 206 响应也有允许源头 |
| 地图只有背景 | source-layer 错误 | 检查 archive 实际图层名 |
| 页面切换后越来越卡 | 重复创建 Map | 卸载时 `map.remove()`，避免多实例 |
| 高 DPI 模糊 | Canvas/CSS 尺寸或图标资源 | 使用 MapLibre 图标和正确 pixel ratio |

### 6.9 验收标准

- 全国地图能从 zoom 5 浏览到现有最高层级；
- 慕尼黑道路、建筑或水系至少三类真实图层正确显示；
- Range 请求为 206；
- OSM 署名可见；
- 控制台没有未处理异常；
- 连续进入/退出地图 10 次不会创建残留实例；
- 桌面 Chrome 中平移缩放无明显卡顿。

---

## 7. Phase 2：Game API 与城市内容包

### 7.1 目标

让游戏客户端只读取稳定、已审核、版本化的数据，不直接理解 SQLite 内部结构或生成器草稿。

### 7.2 API 约定

建议新增：

```text
GET /api/game/v1/cities/{city}/bundle
GET /api/game/v1/cities/{city}/bundle?content_version=...
GET /api/game/v1/health
```

Admin 接口继续负责生成与发布：

```text
/api/admin/generate/*
/api/admin/pois/*
/api/admin/publish/*
```

旧接口可暂时保留兼容层，不要在同一阶段强制大规模改名。

### 7.3 FastAPI 示例

```py
from fastapi import APIRouter, HTTPException
from ..schemas.game_content import CityBundle
from ..services.runtime_export_service import build_city_bundle

router = APIRouter(prefix="/api/game/v1", tags=["game"])

@router.get("/cities/{city}/bundle", response_model=CityBundle)
def get_city_bundle(city: str) -> CityBundle:
    bundle = build_city_bundle(city)
    if bundle is None:
        raise HTTPException(status_code=404, detail="city_not_found")
    return bundle
```

### 7.4 Exporter 原则

Exporter 必须：

- 只包含 `is_published = 1` 数据；
- 将 SQLite JSON 字符串解析为数组/对象；
- 将数据库字段映射到运行时字段；
- 过滤磁盘绝对路径；
- 将资源路径转换为客户端可访问 URL；
- 生成稳定 `contentVersion`；
- 通过 Pydantic 验证后才返回。

不得把 `file_path`、内部 prompt、模型密钥、审核备注或生成日志发给玩家客户端。

### 7.5 后端测试

测试使用临时数据库或 fixture，不得写当前 `game_data.db`。

```py
def test_game_bundle_contains_only_published_pois(client, seeded_db):
    response = client.get('/api/game/v1/cities/munich/bundle')
    assert response.status_code == 200
    body = response.json()
    assert all(poi['published'] for poi in body['pois'])

def test_game_bundle_does_not_leak_file_paths(client, seeded_db):
    body = client.get('/api/game/v1/cities/munich/bundle').json()
    assert '/Volumes/' not in json.dumps(body)
    assert 'API_KEY' not in json.dumps(body)
```

### 7.6 纠错

如果客户端 schema 失败：

1. 保存脱敏后的失败响应；
2. 使用 Pydantic 在后端复现；
3. 判断是 exporter 映射错误还是内容数据不完整；
4. 不得在前端用大量 `??` 掩盖后端错误；
5. 修复 source of truth，并为该错误添加回归测试。

### 7.7 验收标准

- 一个请求返回慕尼黑完整运行时内容包；
- 响应通过前后端双重 schema 验证；
- 未发布 POI 不出现；
- 不泄漏绝对路径、密钥和内部 prompt；
- 同一数据版本产生稳定 `contentVersion`；
- 后端测试不修改生产数据库。

---

## 8. Phase 3：正式地图客户端

### 8.1 目标

将当前单文件地图原型迁移为模块化 Vue + TypeScript 应用。

### 8.2 模块边界

```text
src/map/createMap.ts             创建和销毁 MapLibre
src/map/style/buildStyle.ts      地图视觉样式
src/map/layers/poiLayer.ts       游戏 POI 图层
src/map/layers/routeLayer.ts     路线图层
src/api/gameClient.ts            Game API
src/stores/mapStore.ts           UI 选择状态
src/components/MapView.vue       地图容器
src/components/PoiPanel.vue      POI 详情
```

### 8.3 POI GeoJSON 示例

不要为大量 POI 创建独立 DOM Marker。使用 GeoJSON source + symbol layer：

```ts
import type { FeatureCollection, Point } from 'geojson'
import type { RuntimePoi } from '@/schemas/content'

export function poisToGeoJson(pois: RuntimePoi[]): FeatureCollection<Point> {
  return {
    type: 'FeatureCollection',
    features: pois.map(poi => ({
      type: 'Feature',
      id: poi.id,
      geometry: {
        type: 'Point',
        coordinates: [poi.position.lng, poi.position.lat],
      },
      properties: {
        id: poi.id,
        type: poi.type,
        nameZh: poi.name.zh,
        nameDe: poi.name.de,
      },
    })),
  }
}
```

```ts
map.addSource('game-pois', {
  type: 'geojson',
  data: poisToGeoJson(bundle.pois),
  cluster: true,
  clusterRadius: 40,
})

map.addLayer({
  id: 'game-pois-symbol',
  type: 'symbol',
  source: 'game-pois',
  filter: ['!', ['has', 'point_count']],
  layout: {
    'icon-image': ['concat', 'poi-', ['get', 'type']],
    'icon-size': 0.75,
    'icon-allow-overlap': false,
    'text-field': ['get', 'nameDe'],
    'text-offset': [0, 1.2],
    'text-size': 12,
  },
})
```

图标应在 map load 后通过 `map.loadImage()` / `map.addImage()` 注册，并为未知类型提供 fallback。

### 8.4 点击交互示例

```ts
map.on('click', 'game-pois-symbol', event => {
  const feature = event.features?.[0]
  const id = feature?.properties?.id
  if (typeof id === 'string') mapStore.selectPoi(id)
})

map.on('mouseenter', 'game-pois-symbol', () => {
  map.getCanvas().style.cursor = 'pointer'
})

map.on('mouseleave', 'game-pois-symbol', () => {
  map.getCanvas().style.cursor = ''
})
```

MapLibre 只上报 POI ID；详情数据从已验证 bundle/store 中读取。不要信任 feature properties 作为完整 POI 数据。

### 8.5 测试

- `poisToGeoJson()` 单元测试；
- 缺图标 fallback 测试；
- API 加载失败显示重试界面；
- 点击 POI 打开正确详情；
- zoom 较低时聚合显示；
- 语言切换只改变 UI，不重建 Map 实例；
- Playwright 完成“加载地图 → 点击 POI → 打开面板”。

### 8.6 验收标准

- 旧地图的核心功能已覆盖：浏览、POI、详情、场景图、语音入口；
- 页面不再依赖单文件内联业务脚本；
- 地图实例不会因 Vue 更新而重建；
- 1000 个测试 POI 仍使用一个 GeoJSON source，而非 1000 个 DOM 节点；
- API 不可用时有错误和重试，不是空白地图；
- 老入口仍保留，直到新入口验收完成。

---

## 9. Phase 4：Game Core 与存档

### 9.1 目标

建立不依赖 Vue、MapLibre、Phaser 的纯 TypeScript 游戏规则层。

### 9.2 建议模块

```text
src/core/gameState.ts
src/core/questEngine.ts
src/core/conditionEvaluator.ts
src/core/rewardEngine.ts
src/core/saveManager.ts
src/core/saveMigrations.ts
```

### 9.3 任务状态示例

```ts
export type QuestStatus = 'locked' | 'available' | 'active' | 'completed' | 'failed'

export interface PlayerState {
  schemaVersion: 1
  playerId: string
  day: number
  minuteOfDay: number
  moneyCents: number
  energy: number
  germanXp: number
  completedQuestIds: string[]
  discoveredPoiIds: string[]
  inventory: Record<string, number>
}

export interface Reward {
  moneyCents?: number
  energy?: number
  germanXp?: number
  unlockPoiIds?: string[]
  itemGrants?: Record<string, number>
}
```

### 9.4 奖励函数必须是纯函数

```ts
export function applyReward(state: PlayerState, reward: Reward): PlayerState {
  return {
    ...state,
    moneyCents: state.moneyCents + (reward.moneyCents ?? 0),
    energy: Math.max(0, Math.min(100, state.energy + (reward.energy ?? 0))),
    germanXp: state.germanXp + (reward.germanXp ?? 0),
    discoveredPoiIds: [
      ...new Set([...state.discoveredPoiIds, ...(reward.unlockPoiIds ?? [])]),
    ],
    inventory: mergeInventory(state.inventory, reward.itemGrants ?? {}),
  }
}
```

不要在 `applyReward()` 中操作 localStorage、Vue store、地图图层或播放音效。副作用由调用层处理。

### 9.5 存档示例

```ts
const SAVE_KEY = 'gagatoday.save.v1'

export function saveGame(state: PlayerState): void {
  const validated = PlayerStateSchema.parse(state)
  localStorage.setItem(SAVE_KEY, JSON.stringify(validated))
}

export function loadGame(): PlayerState {
  const raw = localStorage.getItem(SAVE_KEY)
  if (!raw) return createNewGame()

  try {
    return migrateAndValidateSave(JSON.parse(raw))
  } catch (error) {
    console.error('[save] invalid save, preserving backup', error)
    localStorage.setItem(`${SAVE_KEY}.invalid.${Date.now()}`, raw)
    return createNewGame()
  }
}
```

错误存档应保留备份，不能静默覆盖。

### 9.6 必测边界

- 金钱使用整数分，避免浮点误差；
- 体力始终限制在 0–100；
- 同一奖励重复提交不会重复解锁；
- 已完成任务不能重复领奖；
- 旧存档可以迁移；
- 损坏存档不会让游戏白屏；
- 地图选中状态不进入永久存档，除非产品明确需要。

### 9.7 验收标准

- Core 测试无需浏览器和后端即可运行；
- 任务完成、奖励、失败和存档均有单元测试；
- Core 文件中不 import Vue、MapLibre 或 Phaser；
- 刷新后玩家进度恢复；
- 损坏存档有备份与恢复路径；
- 相同任务结果具备确定性。

---

## 10. Phase 5：第一个完整学习闭环

### 10.1 目标

实现首个真正可玩的黄金路径：

```text
寄宿家庭接任务
  → 地图出现目标
  → 前往 Marienplatz/Frauenkirche
  → 打开地点场景
  → 与 NPC 完成 A1 德语任务
  → 获得 XP/知识卡/好感度
  → 返回地图，POI 状态改变
  → 自动存档
```

### 10.2 对话数据示例

```json
{
  "id": "dlg_marienplatz_greeting_01",
  "schemaVersion": 1,
  "npcId": "npc_tourist_info_anna",
  "startNodeId": "start",
  "nodes": [
    {
      "id": "start",
      "npcText": {
        "de": "Guten Tag! Kann ich dir helfen?",
        "zh": "你好！需要帮忙吗？"
      },
      "choices": [
        {
          "id": "ask_direction",
          "text": {
            "de": "Wo ist die Frauenkirche?",
            "zh": "圣母教堂在哪里？"
          },
          "nextNodeId": "success",
          "learningRefs": ["kp_deutsch_a1_wo_ist"]
        }
      ]
    },
    {
      "id": "success",
      "terminal": true,
      "result": "success"
    }
  ]
}
```

### 10.3 对话验证规则

发布前必须验证：

- `startNodeId` 存在；
- 所有 `nextNodeId` 均存在；
- 至少有一个 terminal 节点；
- 所有可达路径最终能够结束，或明确允许循环；
- `learningRefs` 均能解析；
- 奖励只绑定任务结果，不绑定任意 UI 点击。

### 10.4 E2E 测试示例

```ts
test('completes the first German-learning quest', async ({ page }) => {
  await page.goto('/?testMode=1')

  await page.getByRole('button', { name: '开始新游戏' }).click()
  await page.getByText('前往玛利亚广场').click()
  await page.getByTestId('poi-marienplatz').click()
  await page.getByRole('button', { name: '进入地点' }).click()
  await page.getByRole('button', { name: 'Wo ist die Frauenkirche?' }).click()

  await expect(page.getByText('任务完成')).toBeVisible()
  await expect(page.getByTestId('german-xp')).toHaveText('10')

  await page.reload()
  await expect(page.getByTestId('quest-first-arrival')).toHaveAttribute('data-status', 'completed')
})
```

测试模式应使用固定 fixture 和确定性结果，不调用付费 LLM。

### 10.5 人工试玩脚本

让未参与开发的人完成：

1. 打开游戏；
2. 找到当前任务；
3. 在地图找到目标地点；
4. 完成德语互动；
5. 说出自己学到了什么；
6. 关闭并重新打开，确认进度仍在。

记录：

- 完成耗时；
- 卡住位置；
- 是否理解奖励；
- 是否注意到地图变化；
- 是否愿意进入第二个 POI。

### 10.6 验收标准

- 新玩家能在 10–15 分钟完成；
- 没有开发者指导也知道下一步；
- 至少一个知识点在任务结束时被明确复述；
- 奖励和地图变化可见；
- 刷新后任务状态仍正确；
- E2E 测试不调用外部付费模型；
- 失败/答错有反馈和重试，不会卡死主线。

---

## 11. Phase 6：性能、离线与桌面验证

### 11.1 地图数据策略

推荐分层：

| 包 | 范围 | 用途 |
|---|---|---|
| Germany Base | zoom 0–12 | 全国道路、铁路、城市、水系、行政区 |
| State Pack | zoom 13–14 | 州级探索 |
| City Pack | zoom 13–16 | 已开放城市的街道、建筑、精细 POI |
| Game POI | Game API/GeoJSON | 策划过的任务地点 |

“全境真实”必须保留，但不等于首次下载包含每栋建筑。在线版可从对象存储/CDN使用 Range；离线版按州或城市缓存。

### 11.2 性能观测

开发构建和生产构建都要测：

- 首次地图可交互时间；
- 同屏瓦片请求数量；
- 内存增长；
- 平移缩放帧率；
- 100、1000、10000 个 POI 的表现；
- 进入/退出地图 10 次后的内存；
- 慢速网络和 API 失败状态。

建议验收基线（可根据设备调整，但调整必须记录理由）：

- 常规桌面设备地图交互接近 60 FPS；
- POI 点击反馈低于 100ms；
- 进入/退出地图 10 次后内存无持续线性增长；
- API 失败在 3 秒内显示可理解的错误或重试状态；
- 全国层级不会加载城市 zoom 16 瓦片。

### 11.3 Tauri 与 Electron 决策

先测试 Tauri，因为它可复用 Web 客户端且包体小；但系统 WebView 可能带来 MapLibre/WebGL 平台差异。

决策门槛：

- Windows、macOS、Linux 均能正确加载 PMTiles；
- Range、缓存、音频和 WebGL 表现一致；
- 没有平台特有的地图黑屏或严重字体问题。

若不满足，改用 Electron 的统一 Chromium。不要为了安装包更小而牺牲地图稳定性。

### 11.4 验收标准

- 生产构建通过；
- 目标浏览器冒烟测试通过；
- 大量 POI 不使用大量 DOM marker；
- 地图包没有重复进入应用产物；
- 离线/弱网有明确策略；
- 桌面包装方案有基于实测的决策记录。

---

## 12. 效率提升清单

按优先级执行。

### P0：立即做

1. 冻结 MVP，停止同时扩展多个愿景；
2. 建立严格运行时 schema；
3. 用 MapLibre 替代手写地图底层；
4. 建立黄金 POI；
5. Game Core 与 UI 分离；
6. 所有阶段都有 fixture 和回归测试；
7. Admin API 与 Game API 分离。

### P1：垂直切片后做

1. 城市内容包与 CDN；
2. 自动化素材格式检查；
3. 对话图可达性检查；
4. 任务死锁检查；
5. 存档迁移；
6. Playwright 关键路径；
7. PMTiles 分层构建。

### P2：有真实用户后做

1. Phaser 地点场景；
2. Tauri/Electron；
3. 多城市下载；
4. 账户与云同步；
5. 动态 AI 评价；
6. 成就、社交和长期生活模拟。

---

## 13. 内容与素材自动检查

建议建立 `scripts/qa/validate_runtime_content.py`，发布前检查：

- 经纬度合法且位于目标城市合理范围；
- 图片/音频 URL 可访问；
- 文件扩展名与真实 MIME 一致；
- 必填语言齐全；
- 对话节点可达；
- 任务能结束且无死锁；
- `kp_ref` 存在；
- OSM/Wiki/图片来源有记录；
- 内容状态为 reviewed/approved；
- 不含磁盘绝对路径和密钥模式。

伪代码：

```py
def validate_bundle(bundle: CityBundle) -> list[Issue]:
    issues = []
    issues += validate_coordinates(bundle)
    issues += validate_asset_urls(bundle)
    issues += validate_dialogue_graphs(bundle)
    issues += validate_quest_graphs(bundle)
    issues += validate_learning_refs(bundle)
    issues += detect_sensitive_paths(bundle)
    return issues
```

发布规则：

- Error：阻止发布；
- Warning：允许预览，不允许正式发布，除非人工记录豁免理由；
- Info：记录但不阻止。

---

## 14. 统一测试矩阵

| 层级 | 工具 | 测试内容 | 是否访问外网 |
|---|---|---|---|
| Schema | Vitest/Pytest | DTO、非法字段、版本 | 否 |
| Game Core | Vitest | 任务、奖励、时间、存档 | 否 |
| API | Pytest TestClient | bundle、发布过滤、脱敏 | 否 |
| Map Adapter | Vitest | GeoJSON、style、状态转换 | 否 |
| Browser E2E | Playwright | 地图、POI、任务闭环 | 默认否，使用本地 fixture |
| PMTiles | curl/浏览器 | Range、图层、加载 | 本地或测试对象存储 |
| AI Integration | 独立标记测试 | LLM/TTS/ASR | 是，非默认执行 |
| Manual QA | 人工 | 可理解性、学习效果 | 视场景而定 |

推荐命令约定：

```bash
npm run typecheck
npm run test
npm run test:e2e
npm run build
pytest -q
git diff --check
```

如果项目尚无这些 script，Agent 应在对应阶段建立；不要在文档中假装命令已经存在。

---

## 15. 统一纠错流程

任何 bug 按以下顺序处理：

1. **复现**：写清操作、输入、环境和预期；
2. **缩小**：判断属于地图、API、schema、Core、UI、资产还是外部服务；
3. **保存证据**：错误日志、HTTP 状态、脱敏响应、截图；
4. **最小修复**：优先修 source of truth，不在下游加掩盖性 fallback；
5. **补回归测试**：修复前失败、修复后通过；
6. **运行相邻测试**：避免只测一个点；
7. **记录影响**：是否需要内容重发、存档迁移或缓存失效。

### 15.1 快速归因表

| 现象 | 归属候选 |
|---|---|
| 地图黑屏 | WebGL、style、MapLibre 生命周期 |
| 地图有背景无道路 | source-layer、PMTiles URL/Range |
| POI 不出现 | Game API、schema、GeoJSON、图层 filter |
| POI 点击错位 | 经纬度顺序，应为 `[lng, lat]` |
| 刷新后任务丢失 | SaveManager、schema migration |
| 重复领奖 | Quest Engine 幂等性 |
| 内容生成器正常、游戏端报错 | exporter/运行时 schema |
| 音频本地正常、打包失败 | URL、MIME、CORS、资源路径 |
| 地图越用越卡 | Map 实例泄漏、重复 source/layer、监听器未解绑 |

### 15.2 禁止的“修复”方式

- 用空数组静默吞掉 API 错误；
- 对所有字段使用可选链掩盖数据问题；
- 在前端硬编码某个 POI 修复数据库问题；
- 删除损坏存档而不备份；
- 关闭 schema 验证；
- 关闭测试或注释断言让 CI 变绿；
- 把生产密钥写进 `.env` 并提交。

---

## 16. 每阶段交接模板

Agent 完成阶段后，应使用以下格式交接：

```md
## 完成内容
- ...

## 修改文件
- path/to/file：原因

## 测试结果
- `npm run test`：通过，X tests
- `pytest -q`：通过，X tests
- 手工验证：步骤与结果

## 已知问题
- ...

## 数据/存档影响
- 无 / 需要迁移说明

## 下一步
- ...
```

如果测试未运行，必须说明原因；不能只写“应该可以”。

---

## 17. 全项目最终验收清单

### 地图

- [ ] 德国全境真实地图可浏览；
- [ ] 全国、城市、街道缩放层级合理；
- [ ] PMTiles 使用 206 Range；
- [ ] OSM 署名始终可见；
- [ ] 地图无持续内存增长；
- [ ] POI 使用 GeoJSON 图层而非大量 DOM 节点。

### 数据

- [ ] CityBundle 有 schemaVersion/contentVersion；
- [ ] 前后端 schema 一致；
- [ ] 只发布 approved 数据；
- [ ] 不泄漏绝对路径、prompt 或密钥；
- [ ] 素材格式与扩展名一致。

### 游戏

- [ ] 第一个任务闭环可独立完成；
- [ ] 答错有反馈和重试；
- [ ] 奖励具备幂等性；
- [ ] 地图在任务后有可见变化；
- [ ] 刷新后存档恢复；
- [ ] 损坏存档可备份和恢复。

### 工程

- [ ] 地图、Core、UI、API 分层；
- [ ] TypeScript typecheck 通过；
- [ ] 前端单测通过；
- [ ] 后端单测通过；
- [ ] 浏览器 E2E 通过；
- [ ] 生产构建通过；
- [ ] `git diff --check` 通过；
- [ ] 没有覆盖用户无关修改。

### 产品

- [ ] 新玩家 10–15 分钟完成首个任务；
- [ ] 玩家能说出学到的德语知识点；
- [ ] 玩家理解下一步行动；
- [ ] 至少一次真实用户试玩已记录；
- [ ] 在首个闭环验证前未盲目扩张多城市。

只有以上关键项目全部通过，才能宣称“迁移完成”。地图能打开不等于迁移完成。

---

## 18. 工作量与里程碑

以单人全职、熟悉 Vue/TypeScript 为基准：

| 里程碑 | 时间估算 | 退出条件 |
|---|---:|---|
| Phase 0 数据契约 | 3–5 天 | 双端 schema + fixture 通过 |
| Phase 1 地图验证 | 3–5 天 | PMTiles/MapLibre/POI 冒烟通过 |
| Phase 2 Game API | 3–5 天 | bundle + 脱敏 + API 测试通过 |
| Phase 3 正式地图客户端 | 1–2 周 | 核心旧功能覆盖 |
| Phase 4 Game Core | 1–2 周 | 任务、奖励、存档单测通过 |
| Phase 5 首个闭环 | 1–2 周 | E2E + 人工试玩通过 |
| Phase 6 性能/包装验证 | 约 1 周 | 性能报告和包装决策 |

总体：

- 地图客户端迁移：约 2–3 周；
- 第一个完整可玩闭环：约 4–6 周；
- 慕尼黑 10 个高质量 POI 展示版：约 8–12 周；
- 德国多城市：垂直切片稳定后持续扩展。

以上估算不包含大规模内容创作、完整 ASR 发音评分、账户系统和全课程建设。

---

## 19. 最终技术决策

当前默认决策如下，除非用户明确批准变更：

| 问题 | 决策 |
|---|---|
| 是否迁移 Godot | 否 |
| 地图引擎 | MapLibre GL JS |
| 地图格式 | PMTiles/MVT |
| 玩家 UI | Vue 3 + TypeScript |
| 客户端状态 | Pinia |
| 游戏规则 | 纯 TypeScript Game Core |
| 地点内部玩法 | Phaser，延后按需引入 |
| 内容后端 | FastAPI + SQLite（当前阶段） |
| 内容传输 | 版本化 CityBundle JSON |
| 桌面发布 | 先测试 Tauri，不稳定则 Electron |
| 测试 | Vitest + Pytest + Playwright |

这套架构的核心思想是：

> MapLibre 是世界引擎，Game Core 是规则引擎，Vue 是界面层，Phaser 是地点场景引擎，FastAPI 是内容与 AI 服务层。

---

## 20. 参考资料

- MapLibre GL JS：https://maplibre.org/maplibre-gl-js/docs/
- MapLibre PMTiles 示例：https://maplibre.org/maplibre-gl-js/docs/examples/pmtiles/
- Protomaps PMTiles + MapLibre：https://docs.protomaps.com/pmtiles/maplibre
- Phaser Scenes：https://docs.phaser.io/phaser/concepts/scenes
- Tauri：https://v2.tauri.app/start/
- OpenStreetMap 版权与署名：https://www.openstreetmap.org/copyright/attribution-guide
