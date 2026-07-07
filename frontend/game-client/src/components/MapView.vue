<script setup lang="ts">
/**
 * Phase 3 地图视图组件
 *
 * 职责:
 *   - onMounted: 创建 maplibre 地图实例
 *   - map 'load' 完成后,接收 POI 列表渲染为 marker
 *   - 自定义缩放 + 方向键控件(整数档 zoom + panBy)
 *   - Phase 3 新增:玩家 marker、视野过滤(已发现 vs 未发现 POI 不同样式)
 *   - onUnmounted: map.remove() 释放 GL context
 *
 * Phase 3 POI 视觉规则:
 *   - discoveredPoiIds 内的 POI → 标准金色圆形
 *   - 视野外的 POI → 灰色半透明(discovered=false 但发现不了因为没走到)
 *   - 玩家当前位置 → 蓝色方形 marker
 */

import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import maplibregl from 'maplibre-gl'

import { createMap } from '../map/createMap'
import type { PoiMarker } from '../map/types'
import { usePlayerStore } from '../store/player'

import 'maplibre-gl/dist/maplibre-gl.css'

const props = defineProps<{
  pmtilesUrl: string
  center: [number, number]
  zoom: number
  pois: PoiMarker[]
  /** POI id → 是否已发现(由 App.vue 根据 store 派生) */
  discoveredSet?: Set<string>
}>()

const emit = defineEmits<{
  ready: []
  'poi-click': [poi: PoiMarker]
  error: [message: string]
}>()

const containerRef = ref<HTMLDivElement | null>(null)
// shallowRef: maplibre Map/Marker 都是不可变外部资源,深响应没意义还耗性能
const mapRef = shallowRef<maplibregl.Map | null>(null)
const markersRef = shallowRef<maplibregl.Marker[]>([])
const playerMarkerRef = shallowRef<maplibregl.Marker | null>(null)

const player = usePlayerStore()

// 缩放档位配置
const ZOOM_STEP = 1.0        // 整数档(±1)
const PAN_STEP_PX = 100      // 方向键一次平移的像素
const PAN_ANIM_MS = 200      // 平移动画时长
const ZOOM_ANIM_MS = 200     // 缩放动画时长

function clearMarkers() {
  for (const m of markersRef.value) m.remove()
  markersRef.value = []
  if (playerMarkerRef.value) {
    playerMarkerRef.value.remove()
    playerMarkerRef.value = null
  }
}

function makeMarkerElement(poi: PoiMarker, isDiscovered: boolean): HTMLDivElement {
  const el = document.createElement('div')
  el.className = 'gaga-poi-marker'
  if (!isDiscovered) el.classList.add('gaga-poi-marker--undiscovered')
  el.title = poi.label
  el.dataset.poiId = poi.id
  el.textContent = poi.icon
  return el
}

function renderPois() {
  clearMarkers()
  if (!mapRef.value) return
  const discovered = props.discoveredSet ?? new Set<string>()
  const next: maplibregl.Marker[] = []
  for (const poi of props.pois) {
    const el = makeMarkerElement(poi, discovered.has(poi.id))
    const marker = new maplibregl.Marker({ element: el, anchor: 'bottom' })
      .setLngLat(poi.position)
      .addTo(mapRef.value)

    el.addEventListener('click', (ev) => {
      ev.stopPropagation()
      emit('poi-click', poi)
    })

    next.push(marker)
  }
  markersRef.value = next
  renderPlayerMarker()
}

function renderPlayerMarker() {
  if (!mapRef.value) return
  if (playerMarkerRef.value) {
    playerMarkerRef.value.remove()
    playerMarkerRef.value = null
  }
  const pos = player.player.playerPosition
  if (!pos) return

  const el = document.createElement('div')
  el.className = 'gaga-player-marker'
  el.title = '你'
  el.textContent = '🧑'
  playerMarkerRef.value = new maplibregl.Marker({ element: el, anchor: 'bottom' })
    .setLngLat([pos.lng, pos.lat])
    .addTo(mapRef.value)
}

/** 缩放一档(+1 / -1),动画过渡到整数 zoom */
function zoomBy(delta: number) {
  const map = mapRef.value
  if (!map) return
  const next = Math.max(0, Math.min(22, map.getZoom() + delta))
  map.easeTo({ zoom: next, duration: ZOOM_ANIM_MS })
}

/** 平移一定像素(方向键) */
function panBy(dx: number, dy: number) {
  const map = mapRef.value
  if (!map) return
  map.panBy([dx, dy], { duration: PAN_ANIM_MS })
}

/** 键盘事件:方向键 pan,+/- 缩放 */
function onKeydown(ev: KeyboardEvent) {
  // 输入框/textarea 里输入时不要拦截
  const target = ev.target as HTMLElement | null
  if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
    return
  }
  const map = mapRef.value
  if (!map) return

  switch (ev.key) {
    case 'ArrowUp':
    case 'w':
    case 'W':
      ev.preventDefault()
      panBy(0, -PAN_STEP_PX)
      break
    case 'ArrowDown':
    case 's':
    case 'S':
      ev.preventDefault()
      panBy(0, PAN_STEP_PX)
      break
    case 'ArrowLeft':
    case 'a':
    case 'A':
      ev.preventDefault()
      panBy(-PAN_STEP_PX, 0)
      break
    case 'ArrowRight':
    case 'd':
    case 'D':
      ev.preventDefault()
      panBy(PAN_STEP_PX, 0)
      break
    case '+':
    case '=':
      ev.preventDefault()
      zoomBy(ZOOM_STEP)
      break
    case '-':
    case '_':
      ev.preventDefault()
      zoomBy(-ZOOM_STEP)
      break
  }
}

onMounted(() => {
  if (!containerRef.value) return
  const { map, whenReady } = createMap({
    container: containerRef.value,
    pmtilesUrl: props.pmtilesUrl,
    center: props.center,
    zoom: props.zoom,
  })
  mapRef.value = map

  window.addEventListener('keydown', onKeydown)

  whenReady
    .then(() => {
      renderPois()
      emit('ready')
    })
    .catch((e: unknown) => {
      const msg = e instanceof Error ? e.message : String(e)
      console.error('[MapView] map load failed:', msg)
      emit('error', msg)
    })
})

// 监听 POI 列表变化(由 App.vue 切换城市时触发)
watch(
  () => props.pois,
  () => {
    if (mapRef.value) renderPois()
  },
  { deep: false },
)

// 监听发现集合变化(只重渲染已发现/未发现的样式,不重建整个 marker)
watch(
  () => props.discoveredSet,
  (next) => {
    if (!mapRef.value || !next) return
    for (const marker of markersRef.value) {
      const el = marker.getElement()
      const id = el.dataset.poiId
      if (!id) continue
      if (next.has(id)) {
        el.classList.remove('gaga-poi-marker--undiscovered')
      } else {
        el.classList.add('gaga-poi-marker--undiscovered')
      }
    }
  },
  { deep: false },
)

// 监听玩家位置变化 → 更新 player marker
watch(
  () => player.player.playerPosition,
  () => {
    renderPlayerMarker()
  },
  { deep: false },
)

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  clearMarkers()
  if (mapRef.value) {
    mapRef.value.remove()
    mapRef.value = null
  }
})
</script>

<template>
  <div class="map-view-wrapper">
    <div ref="containerRef" class="map-view" data-testid="map-container" />

    <!-- 自定义 16-bit RPG 风控件: 缩放档位 + 方向键 -->
    <div class="gaga-map-controls" data-testid="map-controls">
      <button
        type="button"
        class="gaga-ctrl-btn"
        data-testid="zoom-in"
        aria-label="放大"
        @click="zoomBy(ZOOM_STEP)"
      >+</button>
      <button
        type="button"
        class="gaga-ctrl-btn gaga-ctrl-btn--arrow"
        data-testid="pan-up"
        aria-label="向上"
        @click="panBy(0, -PAN_STEP_PX)"
      >↑</button>
      <button
        type="button"
        class="gaga-ctrl-btn"
        data-testid="zoom-out"
        aria-label="缩小"
        @click="zoomBy(-ZOOM_STEP)"
      >−</button>
      <button
        type="button"
        class="gaga-ctrl-btn gaga-ctrl-btn--arrow"
        data-testid="pan-left"
        aria-label="向左"
        @click="panBy(-PAN_STEP_PX, 0)"
      >←</button>
      <button
        type="button"
        class="gaga-ctrl-btn gaga-ctrl-btn--arrow"
        data-testid="pan-down"
        aria-label="向下"
        @click="panBy(0, PAN_STEP_PX)"
      >↓</button>
      <button
        type="button"
        class="gaga-ctrl-btn gaga-ctrl-btn--arrow"
        data-testid="pan-right"
        aria-label="向右"
        @click="panBy(PAN_STEP_PX, 0)"
      >→</button>
    </div>
  </div>
</template>

<style>
.map-view-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}
.map-view {
  width: 100%;
  height: 100%;
  background: #efe2c2;
}

/* POI 标记样式: 圆形 + 阴影,16-bit RPG 风 */
.gaga-poi-marker {
  width: 32px;
  height: 32px;
  background: #e8b85c;
  border: 3px solid #14305c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  box-shadow:
    2px 2px 0 #06142a,
    inset 0 0 0 2px #ffcf72;
  user-select: none;
  transition: transform 0.1s ease, opacity 0.2s ease, filter 0.2s ease;
}
.gaga-poi-marker:hover {
  transform: translateY(-2px) scale(1.08);
  background: #ffcf72;
}
.gaga-poi-marker:active {
  transform: translateY(0) scale(0.96);
}

/* Phase 3: 未发现的 POI(视野外 / 没走到)— 灰色半透明,不可点 */
.gaga-poi-marker--undiscovered {
  background: #4a5a72;
  border-color: #1f2c3e;
  opacity: 0.5;
  filter: grayscale(70%);
  box-shadow: 1px 1px 0 #06142a;
  cursor: not-allowed;
}
.gaga-poi-marker--undiscovered:hover {
  transform: none;
  background: #4a5a72;
}

/* Phase 3: 玩家 marker — 蓝色方块 + emoji,跟 POI 区分 */
.gaga-player-marker {
  width: 36px;
  height: 36px;
  background: #4a8fdc;
  border: 3px solid #06142a;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  cursor: default;
  box-shadow:
    2px 2px 0 #06142a,
    inset 0 0 0 2px #8ac0ff;
  user-select: none;
  z-index: 5;
}

/* 自定义控件面板: 右上角 3x2 网格 */
.gaga-map-controls {
  position: absolute;
  top: 12px;
  right: 12px;
  display: grid;
  grid-template-columns: repeat(3, 36px);
  grid-template-rows: repeat(2, 36px);
  gap: 4px;
  padding: 4px;
  background: #14305c;
  border: 3px solid #06142a;
  border-radius: 6px;
  box-shadow: 3px 3px 0 #06142a;
  z-index: 10;
}

.gaga-ctrl-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  background: #e8b85c;
  color: #14305c;
  border: 2px solid #06142a;
  border-radius: 4px;
  font-family: 'Courier New', 'VT323', monospace;
  font-size: 20px;
  font-weight: bold;
  line-height: 1;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    inset 0 0 0 2px #ffcf72,
    1px 1px 0 #06142a;
  transition: transform 0.05s ease, background 0.1s ease;
}

.gaga-ctrl-btn:hover {
  background: #ffcf72;
}
.gaga-ctrl-btn:active {
  transform: translate(1px, 1px);
  box-shadow:
    inset 0 0 0 2px #ffcf72,
    0 0 0 #06142a;
}

/* 让方向键按钮字体小一点(箭头比 +/- 占空间) */
.gaga-ctrl-btn--arrow {
  font-size: 18px;
}

/* ── B5:focus-visible ── */
.gaga-ctrl-btn:focus-visible,
.gaga-poi-marker:focus-visible {
  outline: 2px solid #ffcf72;
  outline-offset: 2px;
}

/* ── A2:移动端控件加大(< 640px) — 触控目标 >= 44px ── */
@media (max-width: 640px) {
  .gaga-map-controls {
    top: 8px;
    right: 8px;
    grid-template-columns: repeat(3, 44px);
    grid-template-rows: repeat(2, 44px);
    gap: 6px;
    padding: 6px;
  }
  .gaga-ctrl-btn {
    width: 44px;
    height: 44px;
    font-size: 22px;
  }
  .gaga-ctrl-btn--arrow {
    font-size: 20px;
  }
}

@supports (padding: max(0px)) {
  @media (max-width: 640px) {
    .gaga-map-controls {
      top: max(8px, env(safe-area-inset-top));
      right: max(8px, env(safe-area-inset-right));
    }
  }
}

/* ── B1:prefers-reduced-motion ── */
@media (prefers-reduced-motion: reduce) {
  .gaga-poi-marker,
  .gaga-ctrl-btn {
    transition: none;
  }
  .gaga-poi-marker:hover {
    transform: none;
  }
  .gaga-ctrl-btn:active {
    transform: none;
  }
}
</style>
