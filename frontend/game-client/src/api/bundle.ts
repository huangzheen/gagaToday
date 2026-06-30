/**
 * Phase 2: CityBundle fetcher + ETag/304 协商 + localStorage 缓存
 *
 * 设计目标:
 * - 后端返回 304 时不下载 body,用本地缓存(避免重复反序列化)
 * - 任何错误降级到静态 fallback(开发体验优先)
 * - contentVersion 暴露给上层,UI 可显示"v1.20260630.69050521"
 *
 * 用法:
 *   const result = await fetchCityBundle('munich')
 *   if (result.bundle) { ... } else { use static fallback }
 */

import type { CityBundle } from '../schemas/content'
import { safeParseBundle } from '../schemas/content'

export interface FetchResult {
  bundle: CityBundle | null
  contentVersion: string
  source: 'network' | 'cache' | 'fallback' | 'error'
  errorMessage?: string
}

const LS_PREFIX = 'gagaToday.bundle.'
const LS_ETAG_PREFIX = 'gagaToday.etag.'

function lsKey(cityId: string): { bundle: string; etag: string } {
  return {
    bundle: LS_PREFIX + cityId,
    etag: LS_ETAG_PREFIX + cityId,
  }
}

/** 降级用的静态 fixture(开发环境后端未启动时) */
export interface FallbackBundle {
  bundle: CityBundle
  reason: 'no-backend' | 'http-error' | 'parse-error'
  message: string
}

/**
 * 从 FastAPI fetch 一个城市的 CityBundle
 *
 * @param cityId    例如 'munich'
 * @param fetcher   可选:测试时注入 mock fetch(默认用全局 fetch)
 * @param storage   可选:测试时注入 mock localStorage(默认用全局 localStorage)
 */
export async function fetchCityBundle(
  cityId: string,
  fetcher: typeof fetch = fetch,
  storage: Storage | null = typeof localStorage !== 'undefined' ? localStorage : null,
): Promise<FetchResult> {
  const { bundle: bundleKey, etag: etagKey } = lsKey(cityId)
  const cachedEtag = storage?.getItem(etagKey) ?? null
  const cachedJson = storage?.getItem(bundleKey) ?? null

  const headers: Record<string, string> = {
    Accept: 'application/json',
  }
  if (cachedEtag) {
    headers['If-None-Match'] = cachedEtag
  }

  let res: Response
  try {
    res = await fetcher(`/api/game/v1/cities/${encodeURIComponent(cityId)}/bundle`, { headers })
  } catch (e) {
    // 网络层错误(后端没启、CORS、DNS...)
    const msg = e instanceof Error ? e.message : String(e)
    return { bundle: null, contentVersion: '', source: 'error', errorMessage: msg }
  }

  // ── 304:本地缓存有效 ──
  if (res.status === 304) {
    if (cachedJson) {
      try {
        const parsed = safeParseBundle(JSON.parse(cachedJson))
        if (parsed.ok) {
          return {
            bundle: parsed.data,
            contentVersion: res.headers.get('x-content-version') ?? '',
            source: 'cache',
          }
        }
      } catch {
        // 缓存损坏,继续走全量请求
      }
    }
    // 缓存丢了 / 损坏 → 强制全量
    storage?.removeItem(etagKey)
    return fetchCityBundle(cityId, fetcher, storage)
  }

  // ── 非 2xx:错误 ──
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try {
      const body = await res.text()
      msg += `: ${body.slice(0, 200)}`
    } catch {
      // ignore
    }
    return { bundle: null, contentVersion: '', source: 'error', errorMessage: msg }
  }

  // ── 200:正常 ──
  const etag = res.headers.get('etag') ?? ''
  const cv = res.headers.get('x-content-version') ?? ''
  let body: unknown
  try {
    body = await res.json()
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e)
    return { bundle: null, contentVersion: cv, source: 'error', errorMessage: `JSON parse: ${msg}` }
  }

  const parsed = safeParseBundle(body)
  if (!parsed.ok) {
    const msg = parsed.issues.map((i) => `${i.path.join('.')}: ${i.message}`).join('; ')
    return { bundle: null, contentVersion: cv, source: 'error', errorMessage: `Zod: ${msg}` }
  }

  // 缓存(成功才存)
  try {
    storage?.setItem(bundleKey, JSON.stringify(body))
    if (etag) storage?.setItem(etagKey, etag)
  } catch {
    // localStorage 满 / 隐私模式 → 不影响功能,只是没缓存
  }

  return { bundle: parsed.data, contentVersion: cv, source: 'network' }
}

/** 测试用:清掉某城市的本地缓存 */
export function clearBundleCache(cityId: string, storage: Storage | null = typeof localStorage !== 'undefined' ? localStorage : null): void {
  const { bundle, etag } = lsKey(cityId)
  storage?.removeItem(bundle)
  storage?.removeItem(etag)
}