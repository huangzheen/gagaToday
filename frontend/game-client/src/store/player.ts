/**
 * Phase 3: Pinia player store
 *
 * 职责:
 * - 持有 PlayerState(reactive)
 * - 提供 actions: move / discover / openPoi / closePoi / tickTime
 * - 提供 getters: timeOfDay, isInVision, discoveredPOIs
 * - 自动持久化到 localStorage(SAVE_KEY),损坏存档备份
 * - 自动迁移 v1 → v2 schema
 */

import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

import {
  PLAYER_STATE_SCHEMA_VERSION,
  PlayerStateSchema,
  SAVE_BACKUP_PREFIX,
  SAVE_KEY,
  createNewGameState,
  haversineMeters,
  migrateV1ToV2,
  type PlayerPosition,
  type PlayerState,
} from '../schemas/save'
import type { Poi as RuntimePoi } from '../schemas/content'

/** 安全 localStorage 访问(Safari 隐私模式 / SSR 会抛) */
function getStorage(): Storage | null {
  try {
    if (typeof localStorage === 'undefined') return null
    // touch test
    const k = '__test__'
    localStorage.setItem(k, k)
    localStorage.removeItem(k)
    return localStorage
  } catch {
    return null
  }
}

/** P1-01:打开 POI dialog 的结果(用于 App.vue 反馈) */
export type OpenPoiResult =
  | { ok: true }
  | { ok: false; reason: 'out-of-vision' }

export const usePlayerStore = defineStore('player', () => {
  // ── state ──
  const player = ref<PlayerState>(createNewGameState())
  /** 当前打开的 POI id(null = 没有 dialog) */
  const currentPoiId = ref<string | null>(null)
  /** 暂停时间推进(POI dialog 打开时,或开发者调) */
  const isPaused = ref<boolean>(false)

  // ── getters ──
  /** 格式化 HH:MM */
  const timeOfDay = computed<string>(() => {
    const h = Math.floor(player.value.minuteOfDay / 60)
    const m = player.value.minuteOfDay % 60
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
  })

  /** 是否在白天(6:00-22:00) */
  const isDaytime = computed<boolean>(() => {
    const m = player.value.minuteOfDay
    return m >= 360 && m < 1320
  })

  /** 已知 POI(进入过视野) */
  const discoveredPoiIds = computed<Set<string>>(() => new Set(player.value.discoveredPoiIds))

  /** 给定 POI,判断是否在视野内 */
  function isInVision(poi: RuntimePoi | { position: { lng: number; lat: number } }): boolean {
    const pos = player.value.playerPosition
    if (!pos) return false
    const dist = haversineMeters(pos, poi.position)
    return dist <= player.value.visionRadiusMeters
  }

  /** 计算 POI 距离(米)— 给 HUD / POI marker label 用 */
  function distanceTo(poi: RuntimePoi | { position: { lng: number; lat: number } }): number | null {
    const pos = player.value.playerPosition
    if (!pos) return null
    return haversineMeters(pos, poi.position)
  }

  // ── actions ──
  /** 移动玩家(地图拖动 / 自动巡游 / 调试用) */
  function setPosition(pos: PlayerPosition | null): void {
    player.value.playerPosition = pos
    player.value.savedAt = new Date().toISOString()
  }

  /** 进入新城市(Phase 4 多城市时用,Phase 3 简化版:只设值不切 bundle) */
  function setCurrentCity(cityId: string | null): void {
    player.value.currentCity = cityId
  }

  /** 视野自动发现:把 POI 列表里所有在视野内的加进 discoveredPoiIds */
  function discoverInVision(pois: RuntimePoi[]): { added: string[]; total: number } {
    const before = new Set(player.value.discoveredPoiIds)
    const added: string[] = []
    for (const p of pois) {
      if (!before.has(p.id) && isInVision(p)) {
        added.push(p.id)
      }
    }
    if (added.length > 0) {
      player.value.discoveredPoiIds = [...player.value.discoveredPoiIds, ...added]
      player.value.savedAt = new Date().toISOString()
    }
    return { added, total: player.value.discoveredPoiIds.length }
  }

  /** 手动标记 POI 为已发现(Phase 4 接 quest 触发) */
  function markDiscovered(poiId: string): void {
    if (!player.value.discoveredPoiIds.includes(poiId)) {
      player.value.discoveredPoiIds = [...player.value.discoveredPoiIds, poiId]
      player.value.savedAt = new Date().toISOString()
    }
  }

  /**
   * 打开 POI dialog
   *
   * 审计 P1-01 修复:
   * - 未发现 + 视野外 → 拒绝(不打开 dialog,不改 discoveredPoiIds)
   * - 未发现 + 视野内 → 自动 discover + 打开
   * - 已发现 → 直接打开
   *
   * 注意:必须传整个 poi 对象,因为 store 需要 position 判断视野。
   * 旧签名 openPoi(poiId: string) 已移除,避免误用。
   */
  function openPoi(poi: RuntimePoi): OpenPoiResult {
    const discovered = player.value.discoveredPoiIds.includes(poi.id)
    if (!discovered && !isInVision(poi)) {
      return { ok: false, reason: 'out-of-vision' }
    }
    if (!discovered) {
      markDiscovered(poi.id)
    }
    currentPoiId.value = poi.id
    isPaused.value = true
    return { ok: true }
  }

  /**
   * 高阶 action:移动玩家 + 触发视野发现
   *
   * 审计 P1-01 推荐:不要让调用者记住额外调 discoverInVision。
   * setPosition() 只改坐标;moveTo() 改坐标 + 自动发现。
   */
  function moveTo(
    pos: PlayerPosition,
    pois: RuntimePoi[],
  ): { added: string[]; total: number } {
    setPosition(pos)
    return discoverInVision(pois)
  }

  /** 关闭 POI dialog */
  function closePoi(): void {
    currentPoiId.value = null
    isPaused.value = false
  }

  /** 推进游戏内时间(由 useGameClock 每秒调一次) */
  function tickTime(deltaMinutes: number): void {
    if (isPaused.value) return
    let m = player.value.minuteOfDay + deltaMinutes
    let d = player.value.day
    while (m >= 1440) {
      m -= 1440
      d += 1
    }
    player.value.minuteOfDay = m
    player.value.day = d
  }

  /** 增加 XP(quest 完成后) */
  function addXp(amount: number): void {
    player.value.germanXp = Math.max(0, player.value.germanXp + amount)
  }

  /** 改变金钱(cent) */
  function spendMoney(cents: number): boolean {
    if (player.value.moneyCents < cents) return false
    player.value.moneyCents -= cents
    return true
  }

  function earnMoney(cents: number): void {
    player.value.moneyCents += cents
  }

  /** 消耗体力 */
  function spendEnergy(amount: number): boolean {
    if (player.value.energy < amount) return false
    player.value.energy -= amount
    return true
  }

  function restEnergy(amount: number): void {
    player.value.energy = Math.min(100, player.value.energy + amount)
  }

  // ── 持久化 ──
  function saveToStorage(): boolean {
    const storage = getStorage()
    if (!storage) return false
    try {
      player.value.savedAt = new Date().toISOString()
      storage.setItem(SAVE_KEY, JSON.stringify(player.value))
      return true
    } catch (e) {
      console.warn('[player] save failed:', e)
      return false
    }
  }

  function loadFromStorage(): boolean {
    const storage = getStorage()
    if (!storage) return false
    const raw = storage.getItem(SAVE_KEY)
    if (!raw) return false
    let parsed: unknown
    try {
      parsed = JSON.parse(raw)
    } catch (e) {
      // 备份 + 清掉
      console.warn('[player] save JSON 损坏,备份:', e)
      storage.setItem(`${SAVE_BACKUP_PREFIX}${Date.now()}`, raw)
      storage.removeItem(SAVE_KEY)
      return false
    }
    // 已经是 v2
    if (
      parsed &&
      typeof parsed === 'object' &&
      (parsed as Record<string, unknown>).schemaVersion === PLAYER_STATE_SCHEMA_VERSION
    ) {
      const r = PlayerStateSchema.safeParse(parsed)
      if (r.success) {
        player.value = r.data
        return true
      }
      console.warn('[player] save Zod 失败,备份:', r.error.issues)
      storage.setItem(`${SAVE_BACKUP_PREFIX}${Date.now()}`, raw)
      storage.removeItem(SAVE_KEY)
      return false
    }
    // v1 尝试迁移
    if (
      parsed &&
      typeof parsed === 'object' &&
      (parsed as Record<string, unknown>).schemaVersion === 1
    ) {
      const migrated = migrateV1ToV2(parsed)
      if (migrated) {
        player.value = migrated
        console.info('[player] 从 v1 迁移到 v2 成功')
        saveToStorage()  // 写回新版本
        return true
      }
    }
    // 不可识别,备份
    storage.setItem(`${SAVE_BACKUP_PREFIX}${Date.now()}`, raw)
    storage.removeItem(SAVE_KEY)
    return false
  }

  /** 重置(测试 / 调试) */
  function reset(): void {
    player.value = createNewGameState()
    currentPoiId.value = null
    isPaused.value = false
  }

  // ── 自动持久化 ──
  // 任何 player state 变化 → 节流写 localStorage(500ms debounce)
  let saveTimer: number | null = null
  watch(
    player,
    () => {
      if (saveTimer !== null) window.clearTimeout(saveTimer)
      saveTimer = window.setTimeout(() => {
        saveToStorage()
        saveTimer = null
      }, 500)
    },
    { deep: true },
  )

  return {
    // state
    player,
    currentPoiId,
    isPaused,
    // getters
    timeOfDay,
    isDaytime,
    discoveredPoiIds,
    isInVision,
    distanceTo,
    // actions
    setPosition,
    setCurrentCity,
    moveTo,
    discoverInVision,
    markDiscovered,
    openPoi,
    closePoi,
    tickTime,
    addXp,
    spendMoney,
    earnMoney,
    spendEnergy,
    restEnergy,
    saveToStorage,
    loadFromStorage,
    reset,
  }
})