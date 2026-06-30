/**
 * Phase 1 地图初始化
 *
 * 职责:
 *   1. 注册 pmtiles 协议到 maplibre(全局副作用,只调一次)
 *   2. 创建 maplibre Map 实例
 *   3. 暴露 Promise<Map> 等到 'load' 事件触发
 *
 * 反模式警告(Phase 3+ 注意):
 *   - 不要在多个组件里都调 createMap,否则会注册多份 pmtiles protocol
 *   - 不要在 component unmount 后还持有 map 引用
 */

import maplibregl, { Map as MlMap } from 'maplibre-gl'
import { Protocol } from 'pmtiles'

import { buildMapStyle } from './mapStyle'
import type { CreateMapOptions } from './types'

// 全局单例,避免重复注册(pmtiles 4.x 重复注册会抛错)
let protocolRegistered = false
function ensurePmtilesProtocol(): void {
  if (protocolRegistered) return
  const protocol = new Protocol()
  // maplibre 4.x 的 addProtocol: (customProtocol, loadFn) => this
  // pmtiles 4.x 提供 protocol.tile 作为 loadFn
  maplibregl.addProtocol('pmtiles', protocol.tile)
  protocolRegistered = true
}

export interface CreateMapResult {
  /** 同步返回的 map 实例(可以立刻 addControl 等) */
  map: MlMap
  /** resolve 时 maplibre 已完成首次 'load'(样式 + 初始瓦片就绪) */
  whenReady: Promise<MlMap>
}

/**
 * 创建并初始化 maplibre 地图
 *
 * 调用方负责:onUnmounted 时调 map.remove() — MapView.vue 已经处理
 */
export function createMap(opts: CreateMapOptions): CreateMapResult {
  ensurePmtilesProtocol()

  // pmtiles://<http url> 形式,MapLibre 会用 addProtocol 路由
  const pmtilesUrl = `pmtiles://${opts.pmtilesUrl}`

  const map = new maplibregl.Map({
    container: opts.container,
    style: buildMapStyle({ pmtilesUrl }),
    center: opts.center,
    zoom: opts.zoom,
    interactive: opts.interactive ?? true,
    attributionControl: { compact: true },
    // Phase 1 关闭不必要的特性加速首屏
    fadeDuration: 100,
  })

  // 不再加 maplibre 默认 NavigationControl — MapView.vue 用 16-bit RPG 风自定义控件
  // Scale 控件(左下角)留着,跟自定义控件不冲突
  map.addControl(new maplibregl.ScaleControl({ maxWidth: 100, unit: 'metric' }), 'bottom-left')

  const whenReady = new Promise<MlMap>((resolve, reject) => {
    const onLoad = () => {
      map.off('error', onError)
      resolve(map)
    }
    const onError = (e: unknown) => {
      // 静默 tile 404(zoom 16 边界瓦片偶尔缺),其他错误 reject
      const err = e as { error?: { status?: number } }
      const status = err?.error?.status
      if (status === 404) return
      map.off('load', onLoad)
      reject(e instanceof Error ? e : new Error(String(e)))
    }
    map.on('load', onLoad)
    map.on('error', onError)
  })

  return { map, whenReady }
}
