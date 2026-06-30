<script setup lang="ts">
/**
 * Phase 3 App 顶层组件
 *
 * 职责:
 *   - onMounted:
 *     1. 加载 PlayerState(localStorage,失败则新游戏)
 *     2. fetch CityBundle(后端 → 304 → 静态 fallback)
 *     3. 把玩家位置初始到城市中心
 *     4. 启动游戏时钟
 *   - 把 POI + discoveredSet 传给 MapView(Phase 3 视野过滤)
 *   - 渲染 HUD + PoiDialog
 *   - 把 POI click 转发给 store.openPoi(自动 discover + 暂停时间)
 */

import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import HUD from './components/HUD.vue'
import MapView from './components/MapView.vue'
import PoiDialog from './components/PoiDialog.vue'
import { fetchCityBundle } from './api/bundle'
import { useGameClock } from './composables/useGameClock'
import type { PoiMarker } from './map/types'
import type { CityBundle, Poi as RuntimePoi } from './schemas/content'
import { usePlayerStore } from './store/player'

// 静态 fixture 兜底(后端不可用时用)
import fallbackJson from './data/munich-bundle.json'

const envUrl = (import.meta.env.VITE_PMTILES_URL as string | undefined) ?? ''

interface AppState {
  status: 'loading' | 'ready' | 'error'
  message?: string
  cityLabel: string
  poiCount: number
  contentVersion?: string
  dataSource?: 'network' | 'cache' | 'fallback' | 'error'
}

const state = ref<AppState>({ status: 'loading', cityLabel: '…', poiCount: 0 })
const bundle = ref<CityBundle | null>(null)
/** P1-01 反馈:玩家点击视野外 POI 时的 toast(临时横幅) */
const feedback = ref<string | null>(null)

const player = usePlayerStore()

// POI → PoiMarker(简化:中文 label + emoji)
const pois = computed<PoiMarker[]>(() => {
  if (!bundle.value) return []
  return bundle.value.pois.map((p) => ({
    id: p.id,
    label: `${p.name.zh} · ${p.name.de}`,
    icon: p.icon,
    position: [p.position.lng, p.position.lat],
  }))
})

// 给 MapView 的 discovered Set(避免每次 watcher 触发都新建一个 Set 引用导致全量重渲染)
const discoveredSet = computed(() => player.discoveredPoiIds)

// 当前打开的 POI(给 PoiDialog 用)
const currentPoi = computed<RuntimePoi | null>(() => {
  if (!bundle.value || !player.currentPoiId) return null
  return bundle.value.pois.find((p) => p.id === player.currentPoiId) ?? null
})

// 距离(米)— 给 PoiDialog 显示「离你 X 米」
const currentPoiDistance = computed<number | null>(() => {
  if (!currentPoi.value) return null
  return player.distanceTo(currentPoi.value)
})

// 慕尼黑中心 + zoom 11(覆盖老城 + POI 范围)
const CENTER: [number, number] = [11.5755, 48.1374]
const ZOOM = 11

async function loadBundle() {
  // 1. 尝试 fetch 后端
  const result = await fetchCityBundle('munich')

  if (result.bundle) {
    bundle.value = result.bundle
    state.value = {
      status: 'ready',
      cityLabel: result.bundle.city,
      poiCount: result.bundle.pois.length,
      contentVersion: result.contentVersion || result.bundle.contentVersion,
      dataSource: result.source,
    }
  } else {
    // 2. 后端失败 → fallback 到静态
    console.warn('[App] backend fetch failed, using static fallback:', result.errorMessage)
    bundle.value = fallbackJson as CityBundle
    state.value = {
      status: 'ready',
      cityLabel: fallbackJson.city,
      poiCount: fallbackJson.pois.length,
      contentVersion: `${fallbackJson.contentVersion} (fallback)`,
      dataSource: 'fallback',
      message: `后端不可达: ${result.errorMessage ?? 'unknown'},已用静态 fixture`,
    }
  }

  console.info(
    `[App] bundle loaded: source=${state.value.dataSource} cv=${state.value.contentVersion}`,
  )

  // 3. 初始化玩家位置(若还没有)— 城市中心
  if (!player.player.playerPosition) {
    player.setPosition({ lng: CENTER[0], lat: CENTER[1] })
  }

  // 4. 标记当前城市
  player.setCurrentCity('munich')

  // 5. 视野内 POI 自动发现
  if (bundle.value) {
    const r = player.discoverInVision(bundle.value.pois)
    if (r.added.length > 0) {
      console.info(`[App] auto-discovered ${r.added.length} POIs in initial vision`)
    }
  }
}

// 启动游戏时钟(每秒 = 1 游戏分钟)
const { start: startClock, stop: stopClock } = useGameClock()

onMounted(async () => {
  // 先尝试从 localStorage 加载 PlayerState,失败则保留新游戏
  player.loadFromStorage()
  await loadBundle()
  startClock()
})

// 监听 bundle 加载完毕 → 重新触发视野发现(因为 vision POI 跟 bundle.pois 有关)
watch(bundle, (b) => {
  if (b) player.discoverInVision(b.pois)
})

onBeforeUnmount(() => {
  stopClock()
})

function onMapReady() {
  console.info('[App] map ready')
}
function onMapError(msg: string) {
  state.value = { ...state.value, status: 'error', message: msg }
}

function onPoiClick(poi: PoiMarker) {
  console.info('[App] POI clicked:', poi)
  // 审计 P1-01 修复:openPoi 接收完整 POI,store 判断视野
  const fullPoi = bundle.value?.pois.find((p) => p.id === poi.id)
  if (!fullPoi) {
    console.warn('[App] POI not in bundle:', poi.id)
    return
  }
  const result = player.openPoi(fullPoi)
  if (!result.ok) {
    // 视野外未发现 — 给用户明确反馈
    feedback.value = `📍 ${fullPoi.name.zh} 距离太远,先移动到附近吧`
    console.info('[App] out-of-vision:', fullPoi.id)
    // 5 秒后清掉
    window.setTimeout(() => {
      if (feedback.value?.startsWith(`📍 ${fullPoi.name.zh}`)) {
        feedback.value = null
      }
    }, 5000)
  }
}

function onPoiDialogClose() {
  console.info('[App] POI dialog closed')
}

function onPoiStartDialog(poi: RuntimePoi) {
  console.info('[App] start dialog:', poi.id)
  alert(`Phase 4 实现对话系统: 与 ${poi.name.zh} 对话\n(Phase 3 仅占位,Phase 4 接 Dialogue engine)`)
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="ttl">
        <span class="game-name">gagaToday</span>
        <span class="city">München</span>
        <span v-if="state.contentVersion" class="cv" :title="`dataSource: ${state.dataSource}`">
          v{{ state.contentVersion }}
        </span>
      </div>
      <div class="status" :class="`status-${state.status}`">
        <template v-if="state.status === 'loading'">⏳ 加载中…</template>
        <template v-else-if="state.status === 'ready'">
          ✓ 地图就绪 · 城市 <b>{{ state.cityLabel }}</b> · {{ state.poiCount }} 个 POI
          <span class="data-source" :class="`ds-${state.dataSource}`">[{{ state.dataSource }}]</span>
          <span v-if="envUrl" class="pmtiles-hint">({{ envUrl.split('/').pop() }})</span>
          <span v-if="player.discoveredPoiIds.size > 0" class="discovered-hint" data-testid="discovered-count">
            · 已发现 {{ player.discoveredPoiIds.size }}
          </span>
        </template>
        <template v-else>
          ✗ {{ state.message }}
        </template>
      </div>
    </header>
    <main class="map-wrap">
      <!-- P1-01:反馈 toast(视野外 POI 点击) -->
      <Transition name="gaga-feedback">
        <div v-if="feedback" class="gaga-feedback" data-testid="poi-feedback" role="status">
          {{ feedback }}
        </div>
      </Transition>

      <MapView
        v-if="state.status !== 'error' && envUrl"
        :pmtiles-url="envUrl"
        :center="CENTER"
        :zoom="ZOOM"
        :pois="pois"
        :discovered-set="discoveredSet"
        @ready="onMapReady"
        @error="onMapError"
        @poi-click="onPoiClick"
      />
      <div v-else class="error-pane">
        <pre>{{ state.message ?? 'VITE_PMTILES_URL 未配置' }}</pre>
      </div>

      <!-- Phase 3: HUD + PoiDialog(在地图之上) -->
      <HUD v-if="state.status === 'ready'" />
      <PoiDialog
        :poi="currentPoi"
        :distance-meters="currentPoiDistance"
        @close="onPoiDialogClose"
        @start-dialog="onPoiStartDialog"
      />
    </main>
  </div>
</template>

<style>
:root {
  --navy: #07152b;
  --navy2: #0d2344;
  --navy3: #14305c;
  --gold: #e8b85c;
  --gold2: #ffcf72;
}
* { box-sizing: border-box; }
html, body, #app { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }
body { background: var(--navy); color: #fff; font-family: 'Courier New', monospace; }

.app-shell {
  display: grid;
  grid-template-rows: 64px 1fr;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle at 50% 0%, #183b67, #06101f 60%, #030812);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px;
  background: linear-gradient(180deg, #173d72, #07152b 82%);
  border-bottom: 3px solid var(--gold);
  box-shadow: 0 4px 0 rgba(0, 0, 0, 0.6);
}
.ttl { display: flex; align-items: baseline; gap: 14px; }
.game-name {
  font-size: 22px;
  font-weight: bold;
  color: var(--gold2);
  letter-spacing: 4px;
  text-shadow: 2px 2px 0 #000;
}
.city {
  font-size: 14px;
  color: #8aaac8;
  letter-spacing: 2px;
}
.cv {
  font-size: 10px;
  color: #6a8aaa;
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 6px;
  border-radius: 3px;
  letter-spacing: 1px;
}
.data-source {
  font-size: 10px;
  margin-left: 6px;
  padding: 1px 5px;
  border-radius: 3px;
  letter-spacing: 1px;
}
.ds-network { background: rgba(74, 222, 128, 0.2); color: #4ade80; }
.ds-cache   { background: rgba(96, 165, 250, 0.2); color: #60a5fa; }
.ds-fallback { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.ds-error   { background: rgba(248, 113, 113, 0.2); color: #f87171; }
.discovered-hint {
  color: #ffcf72;
  font-weight: bold;
}
.status {
  font-size: 11px;
  color: #8aaac8;
}
.status-ready b { color: var(--gold2); }
.status-error { color: #ff6b6b; max-width: 60%; text-align: right; }
.pmtiles-hint { color: #6a8aaa; margin-left: 8px; font-size: 10px; }

.map-wrap { position: relative; overflow: hidden; }

.error-pane {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.error-pane pre {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid #ff6b6b;
  padding: 14px 18px;
  color: #ffb0b0;
  font-size: 11px;
  line-height: 1.5;
  max-width: 80%;
  white-space: pre-wrap;
}

/* P1-01:POI 反馈 toast */
.gaga-feedback {
  position: absolute;
  top: 76px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 30;
  background: #14305c;
  border: 2px solid #ff6b6b;
  border-radius: 6px;
  box-shadow: 3px 3px 0 #06142a;
  padding: 10px 18px;
  color: #ffcf72;
  font-family: 'Courier New', 'VT323', monospace;
  font-size: 13px;
  font-weight: bold;
  letter-spacing: 1px;
  white-space: nowrap;
}
.gaga-feedback-enter-active, .gaga-feedback-leave-active {
  transition: all 0.2s ease;
}
.gaga-feedback-enter-from, .gaga-feedback-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
