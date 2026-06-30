/**
 * Phase 3 / P1-01: Player Store 单元测试
 *
 * 审计 P1-01 关键修复:
 *   - 未发现 + 视野外 → openPoi 拒绝(discoveredPoiIds 不变)
 *   - 未发现 + 视野内 → 自动 discover + 打开
 *   - 已发现 → 任何位置都允许打开
 *   - moveTo(pos, pois) 同时改坐标 + 触发视野发现
 *
 * 这些是直接关系到"灰色 POI 仍可点"这个 bug 的回归测试。
 */

import { describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { usePlayerStore } from '../store/player'
import type { Poi } from '../schemas/content'

// 真实坐标:慕尼黑火车总站 lat 48.1407 lng 11.5569
const HAUPTBAHNHOF: Poi = {
  id: 'munchen_hauptbahnhof',
  city: 'munich',
  type: 'train_station',
  name: { de: 'München Hauptbahnhof', zh: '慕尼黑中央火车站' },
  position: { lat: 48.1407, lng: 11.5569 },
  icon: '🚉',
  sceneUrls: [],
  audioUrls: {},
  questIds: [],
  npcIds: [],
  published: true,
}

// 玛丽安广场:距离火车总站 ~2km,远超 500m 视野
const MARIENPLATZ: Poi = {
  id: 'marienplatz',
  city: 'munich',
  type: 'square',
  name: { de: 'Marienplatz', zh: '玛利亚广场' },
  position: { lat: 48.1374, lng: 11.5755 },
  icon: '🏛',
  sceneUrls: [],
  audioUrls: {},
  questIds: [],
  npcIds: [],
  published: true,
}

function freshPlayer() {
  setActivePinia(createPinia())
  return usePlayerStore()
}

describe('P1-01:openPoi 视野规则', () => {
  it('未发现 + 视野外 → 拒绝,不进 discoveredPoiIds', () => {
    const p = freshPlayer()
    p.setPosition({ lat: 48.1374, lng: 11.5755 })  // Marienplatz
    expect(p.isInVision(HAUPTBAHNHOF)).toBe(false)

    const initial = p.player.discoveredPoiIds.length
    const result = p.openPoi(HAUPTBAHNHOF)

    expect(result).toEqual({ ok: false, reason: 'out-of-vision' })
    expect(p.player.discoveredPoiIds.length).toBe(initial)
    expect(p.currentPoiId).toBeNull()
    expect(p.isPaused).toBe(false)
  })

  it('未发现 + 视野内 → 自动 discover + 打开', () => {
    const p = freshPlayer()
    p.setPosition({ lat: 48.1407, lng: 11.5569 })  // 就在火车总站
    expect(p.isInVision(HAUPTBAHNHOF)).toBe(true)

    const result = p.openPoi(HAUPTBAHNHOF)

    expect(result).toEqual({ ok: true })
    expect(p.player.discoveredPoiIds).toContain('munchen_hauptbahnhof')
    expect(p.currentPoiId).toBe('munchen_hauptbahnhof')
    expect(p.isPaused).toBe(true)
  })

  it('已发现 → 任何位置都允许', () => {
    const p = freshPlayer()
    // 第一次在视野内发现
    p.setPosition({ lat: 48.1407, lng: 11.5569 })
    p.openPoi(HAUPTBAHNHOF)
    p.closePoi()

    // 移动到视野外
    p.setPosition({ lat: 48.1374, lng: 11.5755 })  // Marienplatz
    expect(p.isInVision(HAUPTBAHNHOF)).toBe(false)

    // 应该仍能打开(已发现不受视野限制)
    const result = p.openPoi(HAUPTBAHNHOF)
    expect(result).toEqual({ ok: true })
    expect(p.currentPoiId).toBe('munchen_hauptbahnhof')
  })

  it('已发现 POI 不会被重复加入 discoveredPoiIds', () => {
    const p = freshPlayer()
    p.setPosition({ lat: 48.1407, lng: 11.5569 })
    p.openPoi(HAUPTBAHNHOF)
    p.closePoi()
    p.openPoi(HAUPTBAHNHOF)  // 第二次

    const matches = p.player.discoveredPoiIds.filter(
      (id) => id === 'munchen_hauptbahnhof',
    )
    expect(matches.length).toBe(1)
  })
})

describe('P1-01:moveTo 高阶 action', () => {
  it('moveTo 同时改坐标 + 触发视野发现', () => {
    const p = freshPlayer()
    p.setPosition({ lat: 0, lng: 0 })  // 远离所有 POI

    const r = p.moveTo({ lat: 48.1407, lng: 11.5569 }, [HAUPTBAHNHOF, MARIENPLATZ])

    expect(p.player.playerPosition).toEqual({ lat: 48.1407, lng: 11.5569 })
    expect(r.added).toContain('munchen_hauptbahnhof')
    expect(p.player.discoveredPoiIds).toContain('munchen_hauptbahnhof')
  })

  it('moveTo 到 POI 视野外:不发现任何', () => {
    const p = freshPlayer()
    p.setPosition({ lat: 0, lng: 0 })

    const r = p.moveTo({ lat: 48.20, lng: 11.60 }, [HAUPTBAHNHOF, MARIENPLATZ])

    expect(r.added).toEqual([])
    expect(p.player.discoveredPoiIds).toEqual([])
  })
})