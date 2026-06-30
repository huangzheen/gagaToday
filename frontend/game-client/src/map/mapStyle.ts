/**
 * Phase 1 地图样式
 *
 * 16-bit RPG 配色,跟 gagaToday 视觉指南保持一致:
 *   --navy  深蓝(0d2344)   --gold  金色(e8b85c)  --warm  米色(efe2c2)
 *
 * 数据源: protomaps v3/v4 basemap(MVT vector)
 *   PMTiles header 已确认有 16 个 layer:water/landuse/park/transportation/building/poi/...
 *   我们只展示 4 个(water/landuse/park/transportation) + 1 个 POI label,
 *   其余 layer 在 maplibre source 里保留但不绘 — Phase 3 再细化。
 *
 * 注意: protomaps basemap 里 POI 是底图原生的 OSM 兴趣点,跟我们的 CityBundle POI 无关;
 *       我们自己的 POI 在 MapView.vue 用 Marker 渲染。
 */

import type { StyleSpecification } from 'maplibre-gl'

export interface BuildMapStyleOptions {
  /** pmtiles:// 协议的 PMTiles URL(注意是 pmtiles:// 前缀) */
  pmtilesUrl: string
}

const COLORS = {
  bg: '#efe2c2',          // 背景米色
  water: '#5aa5c6',
  waterShadow: '#2d6f94',
  park: '#8fb96c',
  parkShadow: '#547d40',
  landuse: '#e9d8a8',     // 居民/工业等 — 比 bg 略深
  residential: '#e6d4a0',
  roadMinor: '#d6c090',
  roadMajor: '#d89a45',
  roadHighway: '#b85a2a',
  building: '#b96f4d',
  buildingShadow: '#523225',
  placeLabel: '#14305c',
  poiLabel: '#7a3e1c',
} as const

export function buildMapStyle({ pmtilesUrl }: BuildMapStyleOptions): StyleSpecification {
  return {
    version: 8,
    glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
    // 单一数据源: 整套德国 basemap
    sources: {
      basemap: {
        type: 'vector',
        url: pmtilesUrl,         // pmtiles:// 前缀的 URL
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a> · <a href="https://protomaps.com">Protomaps</a>',
      },
    },
    layers: [
      // ── 背景色(瓦片未加载时显示) ──
      {
        id: 'bg',
        type: 'background',
        paint: { 'background-color': COLORS.bg },
      },

      // ── 水系 (zoom 0+) ──
      {
        id: 'water',
        type: 'fill',
        source: 'basemap',
        'source-layer': 'water',
        paint: { 'fill-color': COLORS.water },
      },
      {
        id: 'water-shadow',
        type: 'line',
        source: 'basemap',
        'source-layer': 'water',
        paint: {
          'line-color': COLORS.waterShadow,
          'line-width': 0.5,
          'line-translate': [0, 1],
        },
      },

      // ── 公园/绿地 (zoom 4+) ──
      {
        id: 'park',
        type: 'fill',
        source: 'basemap',
        'source-layer': 'park',
        paint: { 'fill-color': COLORS.park },
      },

      // ── 土地利用 (zoom 4+) ──
      {
        id: 'landuse',
        type: 'fill',
        source: 'basemap',
        'source-layer': 'landuse',
        paint: { 'fill-color': COLORS.landuse, 'fill-opacity': 0.5 },
      },

      // ── 道路 (zoom 4+) ──
      {
        id: 'road-minor',
        type: 'line',
        source: 'basemap',
        'source-layer': 'transportation',
        filter: ['in', 'class', 'minor', 'service', 'path', 'footway'],
        minzoom: 13,
        paint: {
          'line-color': COLORS.roadMinor,
          'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.5, 16, 2],
        },
      },
      {
        id: 'road-secondary',
        type: 'line',
        source: 'basemap',
        'source-layer': 'transportation',
        filter: ['in', 'class', 'secondary', 'tertiary'],
        minzoom: 10,
        paint: {
          'line-color': COLORS.roadMajor,
          'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 16, 3],
        },
      },
      {
        id: 'road-primary',
        type: 'line',
        source: 'basemap',
        'source-layer': 'transportation',
        filter: ['in', 'class', 'primary', 'trunk'],
        minzoom: 7,
        paint: {
          'line-color': COLORS.roadHighway,
          'line-width': ['interpolate', ['linear'], ['zoom'], 7, 0.5, 16, 4],
        },
      },
      {
        id: 'road-motorway',
        type: 'line',
        source: 'basemap',
        'source-layer': 'transportation',
        filter: ['==', 'class', 'motorway'],
        minzoom: 5,
        paint: {
          'line-color': COLORS.roadHighway,
          'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.8, 16, 5],
        },
      },

      // ── 建筑物(zoom 13+) ──
      {
        id: 'building',
        type: 'fill',
        source: 'basemap',
        'source-layer': 'building',
        minzoom: 13,
        paint: {
          'fill-color': COLORS.building,
          'fill-opacity': 0.7,
        },
      },

      // ── 城市/地名标签(zoom 8+) — 只显示城市/镇 ──
      {
        id: 'place-city',
        type: 'symbol',
        source: 'basemap',
        'source-layer': 'place',
        filter: ['in', 'class', 'city', 'town'],
        minzoom: 8,
        layout: {
          'text-field': ['coalesce', ['get', 'name:de'], ['get', 'name'], ['get', 'name_en']],
          'text-font': ['Noto Sans Regular'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 8, 10, 14, 16],
          'text-anchor': 'center',
          'text-max-width': 8,
        },
        paint: {
          'text-color': COLORS.placeLabel,
          'text-halo-color': COLORS.bg,
          'text-halo-width': 1.5,
        },
      },
    ],
  }
}

/** 暴露给测试用 */
export const __TESTING__ = { COLORS }
