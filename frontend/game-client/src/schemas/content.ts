/**
 * gagaToday 运行时内容契约 (Runtime Content Contract)
 *
 * ─────────────────────────────────────────────────
 * 谁负责什么
 * ─────────────────────────────────────────────────
 * - 内容生产端 (Vue POI Generator + FastAPI Admin) → 写 SQLite / draft JSON
 * - 内容审核员 → 决定 is_published
 * - **运行时导出端** (runtime_export_service.py) → SQLite → CityBundle JSON
 * - **玩家客户端** (game-client,这里) → 只解析 CityBundle,绝不直接读 SQLite
 *
 * 任何字段如果"看起来合理但客户端没有 schema 验证",就属于错误。
 * 本文件是 single source of truth,Python 端 schemas/game_content.py 必须对齐。
 *
 * 版本策略:
 * - schemaVersion: CityBundle JSON 自身的格式版本,只增不减
 * - contentVersion: 同一份内容数据的版本号(发布时由导出器生成)
 * - 玩家存档用 schemaVersion + 独立 save.ts 的 schema
 *
 * @module schemas/content
 */

import { z } from 'zod'

// ── 三语本地化文本 ──
// 中文必填(慕尼黑游戏面向中文玩家),德语必填(游戏语言),英语选填
export const LocalizedTextSchema = z.object({
  de: z.string().min(1, '德语必填'),
  zh: z.string().min(1, '中文必填'),
  en: z.string().optional(),
})
export type LocalizedText = z.infer<typeof LocalizedTextSchema>

// ── 经纬度 (必须是 [lng, lat] 顺序,这是 GeoJSON 标准) ──
export const PositionSchema = z.object({
  lat: z.number().gte(-90).lte(90),
  lng: z.number().gte(-180).lte(180),
})
export type Position = z.infer<typeof PositionSchema>

// ── POI ──
// 一座城市场景图清单(运行时拼图用,顺序即显示顺序)
const SceneUrlSchema = z.string().url().or(z.string().regex(/^\/assets\//, '本地资源必须以 /assets/ 开头'))

// ── 图标 emoji(暂时用,后续可换 sprite 图标) ──
const IconSchema = z.string().min(1).max(8)  // emoji 通常 ≤ 4 字节

// ── POI 类型枚举 ──
// 与 frontend/poi-generator/src/stores/generator.js BUILTIN_POIS 对齐
export const POI_TYPE_VALUES = [
  'church', 'square', 'museum', 'park', 'market',
  'castle', 'stadium', 'school', 'shop', 'library',
  'home', 'train_station', 'subway', 'tram', 'bus_stop',
  'historic', 'attraction', 'landmark',
] as const
export const PoiTypeSchema = z.enum(POI_TYPE_VALUES)
export type PoiType = z.infer<typeof PoiTypeSchema>

export const PoiSchema = z.object({
  id: z.string().min(1, 'POI id 必填').regex(/^[a-z][a-z0-9_]*$/, 'POI id 只能含小写字母数字下划线,且以字母开头'),
  city: z.string().min(1),
  type: PoiTypeSchema,
  name: LocalizedTextSchema,
  position: PositionSchema,
  description: LocalizedTextSchema.partial().optional(),  // 可选,可只填 de/zh
  icon: IconSchema,
  iconUrl: SceneUrlSchema.optional(),
  sceneUrls: z.array(SceneUrlSchema).default([]),
  audioUrls: z.object({
    de: SceneUrlSchema.optional(),
    zh: SceneUrlSchema.optional(),
    en: SceneUrlSchema.optional(),
  }).default({}),
  questIds: z.array(z.string().min(1)).default([]),
  npcIds: z.array(z.string().min(1)).default([]),
  published: z.literal(true),  // 运行时 bundle 里只可能 published=true
})
export type Poi = z.infer<typeof PoiSchema>

// ── NPC (Phase 0 占位,Phase 4+ 严格化) ──
// 文档要求: unknown() 只在 Phase 0 临时使用,Phase 5 前换成严格 schema
export const NpcSchema = z.object({
  id: z.string().min(1),
  poiId: z.string().min(1),
  name: LocalizedTextSchema,
  role: LocalizedTextSchema.partial(),
  imageUrls: z.object({
    head: SceneUrlSchema.optional(),
    half: SceneUrlSchema.optional(),
  }).default({}),
  published: z.literal(true),
}).passthrough()  // Phase 0 允许额外字段,Phase 5 前收紧
export type Npc = z.infer<typeof NpcSchema>

// ── Dialogue 节点 ──
// nextNodeId 接受 string | null | undefined(后端 audit P0-01 用 exclude_none
// 会让 None 字段省略,所以这里同时接受 missing)
export const DialogueChoiceSchema = z.object({
  id: z.string().min(1),
  text: LocalizedTextSchema,
  nextNodeId: z.string().min(1).nullable().optional(),
  learningRefs: z.array(z.string()).default([]),
})
export type DialogueChoice = z.infer<typeof DialogueChoiceSchema>

// terminal / result 同理
export const DialogueNodeSchema = z.object({
  id: z.string().min(1),
  npcText: LocalizedTextSchema,
  choices: z.array(DialogueChoiceSchema).default([]),
  terminal: z.boolean().optional(),
  result: z.enum(['success', 'failure', 'neutral']).optional(),
})
export type DialogueNode = z.infer<typeof DialogueNodeSchema>

export const DialogueSchema = z.object({
  id: z.string().min(1),
  npcId: z.string().min(1),
  startNodeId: z.string().min(1),
  nodes: z.array(DialogueNodeSchema).min(1),
  published: z.literal(true),
}).passthrough()
export type Dialogue = z.infer<typeof DialogueSchema>

// ── Quest ──
export const QuestSchema = z.object({
  id: z.string().min(1),
  title: LocalizedTextSchema,
  description: LocalizedTextSchema.partial(),
  poiId: z.string().min(1),
  dialogueIds: z.array(z.string()).default([]),
  prerequisites: z.array(z.string()).default([]),  // questIds
  reward: z.object({
    moneyCents: z.number().int().optional(),
    energy: z.number().int().min(-100).max(100).optional(),
    germanXp: z.number().int().nonnegative().optional(),
    unlockPoiIds: z.array(z.string()).default([]),
    itemGrants: z.record(z.string(), z.number().int()).default({}),
  }).default({}),
  published: z.literal(true),
}).passthrough()
export type Quest = z.infer<typeof QuestSchema>

// ── Knowledge Card ──
export const KnowledgeCardSchema = z.object({
  id: z.string().min(1),
  title: LocalizedTextSchema,
  body: LocalizedTextSchema,
  refs: z.array(z.string()).default([]),  // 学习点 id
  published: z.literal(true),
}).passthrough()
export type KnowledgeCard = z.infer<typeof KnowledgeCardSchema>

// ── City Bundle ──
// 一次 API 调用返回一整个城市的内容,客户端拿到后缓存到内存,直到 schemaVersion/contentVersion 变化
export const CityBundleSchema = z.object({
  schemaVersion: z.literal(1),
  contentVersion: z.string().min(1).regex(/^\d+\.\d+\.\d+$/, 'contentVersion 必须 x.y.z 格式'),
  city: z.string().min(1),
  generatedAt: z.string().datetime({ offset: true }),  // ISO 8601,带时区
  pois: z.array(PoiSchema).default([]),
  npcs: z.array(NpcSchema).default([]),
  dialogues: z.array(DialogueSchema).default([]),
  quests: z.array(QuestSchema).default([]),
  knowledgeCards: z.array(KnowledgeCardSchema).default([]),
}).superRefine((bundle, ctx) => {
  // 跨字段一致性:Quest 引用的 POI 必须存在
  const poiIds = new Set(bundle.pois.map(p => p.id))
  for (const q of bundle.quests) {
    if (!poiIds.has(q.poiId)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Quest ${q.id} 引用的 POI ${q.poiId} 不存在`,
        path: ['quests'],
      })
    }
  }
  // Dialogue 引用的 NPC 必须存在
  const npcIds = new Set(bundle.npcs.map(n => n.id))
  for (const d of bundle.dialogues) {
    if (!npcIds.has(d.npcId)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Dialogue ${d.id} 引用的 NPC ${d.npcId} 不存在`,
        path: ['dialogues'],
      })
    }
  }
})
export type CityBundle = z.infer<typeof CityBundleSchema>

// ── 辅助函数 ──
export function safeParseBundle(json: unknown):
  | { ok: true; data: CityBundle }
  | { ok: false; issues: z.ZodIssue[] } {
  const result = CityBundleSchema.safeParse(json)
  if (result.success) return { ok: true, data: result.data }
  return { ok: false, issues: result.error.issues }
}