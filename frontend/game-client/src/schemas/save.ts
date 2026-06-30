/**
 * gagaToday 玩家存档 Schema
 *
 * ─────────────────────────────────────────────────
 * 与 content.ts 的区别:
 * - content.ts 是**只读内容** schema (从服务器来,版本由 contentVersion 管理)
 * - save.ts 是**玩家进度** schema (本地 localStorage 写入,跨刷新保留)
 *
 * 持久化规则:
 * - 主存档: `gagatoday.save.v1` (PlayerState)
 * - 损坏存档备份: `gagatoday.save.v1.invalid.<timestamp>` (出问题时保留)
 *
 * 迁移规则:
 * - schemaVersion 字段只增不减
 * - 旧存档通过 saveMigrations.ts 迁移到当前版本
 * - 迁移失败保留备份,不静默覆盖
 *
 * Phase 3 扩展:
 * - playerPosition: 玩家在地图上的经纬度(lng/lat)
 * - visionRadiusMeters: 视野半径(米),决定哪些 POI 算 discovered
 * - currentCity: 当前所在城市 ID(Phase 4+ 用于多城市切换)
 *
 * @module schemas/save
 */

import { z } from 'zod'

// ── 玩家状态 ──
export const PLAYER_STATE_SCHEMA_VERSION = 2 as const  // Phase 3 bump 1 → 2

// 经纬度(简化版,跟 content.ts 的 Position 字段一致)
export const PlayerPositionSchema = z.object({
  lng: z.number().min(-180).max(180),
  lat: z.number().min(-90).max(90),
})
export type PlayerPosition = z.infer<typeof PlayerPositionSchema>

export const PlayerStateSchema = z.object({
  schemaVersion: z.literal(PLAYER_STATE_SCHEMA_VERSION),
  playerId: z.string().min(1),
  // 时间维度
  day: z.number().int().nonnegative(),
  minuteOfDay: z.number().int().min(0).max(1439),  // 一天 1440 分钟
  // 资源
  moneyCents: z.number().int().nonnegative(),
  energy: z.number().int().min(0).max(100),
  germanXp: z.number().int().nonnegative(),
  // 进度
  completedQuestIds: z.array(z.string().min(1)),
  discoveredPoiIds: z.array(z.string().min(1)),
  inventory: z.record(z.string(), z.number().int().nonnegative()),
  // Phase 3: 地图位置 + 视野
  playerPosition: PlayerPositionSchema.nullable(),  // null = 还没开始移动
  visionRadiusMeters: z.number().int().positive().default(500),
  currentCity: z.string().min(1).nullable(),  // null = 未选择城市
  // 元数据
  lastContentVersion: z.string().optional(),  // 上次同步的 CityBundle.contentVersion
  savedAt: z.string().datetime({ offset: true }),
})
export type PlayerState = z.infer<typeof PlayerStateSchema>

// ── 默认新游戏 ──
export function createNewGameState(opts: {
  startPosition?: PlayerPosition
  city?: string
} = {}): PlayerState {
  return {
    schemaVersion: PLAYER_STATE_SCHEMA_VERSION,
    playerId: `player_${Date.now().toString(36)}`,
    day: 1,
    minuteOfDay: 480,  // 早上 8:00
    moneyCents: 2000,  // 20 欧
    energy: 100,
    germanXp: 0,
    completedQuestIds: [],
    discoveredPoiIds: [],
    inventory: {},
    playerPosition: opts.startPosition ?? null,
    visionRadiusMeters: 500,
    currentCity: opts.city ?? null,
    savedAt: new Date().toISOString(),
  }
}

// ── 升级:把 v1 存档迁移到 v2 ──
// 旧存档(Phase 2)没 playerPosition/visionRadius/currentCity,自动补 null/500/null
export function migrateV1ToV2(old: unknown): PlayerState | null {
  if (!old || typeof old !== 'object') return null
  const o = old as Record<string, unknown>
  if (o.schemaVersion !== 1) return null
  return {
    schemaVersion: PLAYER_STATE_SCHEMA_VERSION,
    playerId: String(o.playerId ?? `player_${Date.now().toString(36)}`),
    day: Number(o.day ?? 1),
    minuteOfDay: Number(o.minuteOfDay ?? 480),
    moneyCents: Number(o.moneyCents ?? 2000),
    energy: Number(o.energy ?? 100),
    germanXp: Number(o.germanXp ?? 0),
    completedQuestIds: Array.isArray(o.completedQuestIds) ? o.completedQuestIds as string[] : [],
    discoveredPoiIds: Array.isArray(o.discoveredPoiIds) ? o.discoveredPoiIds as string[] : [],
    inventory: (o.inventory && typeof o.inventory === 'object') ? o.inventory as Record<string, number> : {},
    // 新字段默认值
    playerPosition: null,
    visionRadiusMeters: 500,
    currentCity: null,
    // 元数据
    lastContentVersion: typeof o.lastContentVersion === 'string' ? o.lastContentVersion : undefined,
    savedAt: typeof o.savedAt === 'string' ? o.savedAt : new Date().toISOString(),
  }
}

// ── 奖励结构 (跟 content.ts 的 Quest.reward 对齐) ──
export const RewardSchema = z.object({
  moneyCents: z.number().int().optional(),
  energy: z.number().int().min(-100).max(100).optional(),
  germanXp: z.number().int().nonnegative().optional(),
  unlockPoiIds: z.array(z.string()).default([]),
  itemGrants: z.record(z.string(), z.number().int()).default({}),
})
export type Reward = z.infer<typeof RewardSchema>

// ── Quest 状态枚举 ──
// 跟 Python 端保持一致: locked / available / active / completed / failed
export const QUEST_STATUSES = ['locked', 'available', 'active', 'completed', 'failed'] as const
export const QuestStatusSchema = z.enum(QUEST_STATUSES)
export type QuestStatus = z.infer<typeof QuestStatusSchema>

// ── 持久化 key ──
export const SAVE_KEY = 'gagatoday.save.v1'
export const SAVE_BACKUP_PREFIX = 'gagatoday.save.v1.invalid.'

// ── 工具:Haversine 距离(米) ──
// 用于视野判定:player 与 POI 之间的球面距离
const EARTH_RADIUS_M = 6_371_000
export function haversineMeters(
  a: PlayerPosition,
  b: PlayerPosition,
): number {
  const toRad = (d: number) => (d * Math.PI) / 180
  const dLat = toRad(b.lat - a.lat)
  const dLng = toRad(b.lng - a.lng)
  const lat1 = toRad(a.lat)
  const lat2 = toRad(b.lat)
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2
  return 2 * EARTH_RADIUS_M * Math.asin(Math.min(1, Math.sqrt(h)))
}