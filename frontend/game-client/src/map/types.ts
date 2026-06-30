/**
 * Phase 1 地图配置类型
 *
 * 故意保持小:Phase 1 只关心"能不能渲染出地图 + POI 标记",不引入游戏状态/玩家进度等概念。
 * 后续 Phase 在此基础上扩展(Marker 交互、视野雾、保存进度等)。
 */

/** 创建地图的核心配置(从环境变量 + 调用方参数合并) */
export interface CreateMapOptions {
  /** 容器 DOM 元素 */
  container: HTMLElement
  /** PMTiles 文件的 http(s) URL,会被包装成 pmtiles:// 协议 */
  pmtilesUrl: string
  /** 初始中心 [lng, lat] — 注意 GeoJSON 顺序 */
  center: [number, number]
  /** 初始缩放(0-16) */
  zoom: number
  /** 是否启用键盘/鼠标交互 — Phase 1 默认开,debug 截图时关 */
  interactive?: boolean
}

/** MapLibre 'load' 事件后,POI 加载层需要的输入 */
export interface PoiMarker {
  /** POI id(对应 CityBundle.pois[].id) */
  id: string
  /** 显示名称(玩家语言,默认中文) */
  label: string
  /** emoji 图标 */
  icon: string
  /** 坐标 [lng, lat] */
  position: [number, number]
}
