/**
 * Phase 0 schema 验证测试
 *
 * - 必须接受已批准的 Munich fixture
 * - 非法坐标、缺名称、错误版本必须拒绝
 */

import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import {
  PoiSchema,
  PositionSchema,
  LocalizedTextSchema,
  safeParseBundle,
} from '../schemas/content'

const fixturePath = resolve(__dirname, 'fixtures/munich-bundle.json')

function loadFixture() {
  const raw = readFileSync(fixturePath, 'utf-8')
  return JSON.parse(raw)
}

describe('LocalizedTextSchema', () => {
  it('要求 de 和 zh 必填', () => {
    expect(() => LocalizedTextSchema.parse({ de: '', zh: '中' })).toThrow()
    expect(() => LocalizedTextSchema.parse({ de: 'de' })).toThrow()  // 缺 zh
    const ok = LocalizedTextSchema.parse({ de: 'de', zh: '中', en: 'en' })
    expect(ok.de).toBe('de')
    expect(ok.en).toBe('en')
  })
})

describe('PositionSchema', () => {
  it('接受合法坐标', () => {
    const p = PositionSchema.parse({ lat: 48.1374, lng: 11.5755 })
    expect(p.lat).toBe(48.1374)
  })

  it('拒绝超出范围的纬度', () => {
    expect(() => PositionSchema.parse({ lat: 120, lng: 11 })).toThrow()
    expect(() => PositionSchema.parse({ lat: -91, lng: 11 })).toThrow()
  })

  it('拒绝超出范围的经度', () => {
    expect(() => PositionSchema.parse({ lat: 48, lng: 200 })).toThrow()
  })
})

describe('PoiSchema', () => {
  const validPoi = {
    id: 'frauenkirche',
    city: 'munich',
    type: 'church',
    name: { de: 'Frauenkirche', zh: '圣母教堂' },
    position: { lat: 48.1385, lng: 11.5737 },
    icon: '⛪',
    sceneUrls: [],
    audioUrls: {},
    questIds: [],
    npcIds: [],
    published: true as const,
  }

  it('接受标准 POI', () => {
    expect(() => PoiSchema.parse(validPoi)).not.toThrow()
  })

  it('拒绝非法 id(大写)', () => {
    expect(() => PoiSchema.parse({ ...validPoi, id: 'Frauenkirche' })).toThrow()
  })

  it('拒绝非法 type', () => {
    expect(() => PoiSchema.parse({ ...validPoi, type: 'unknown_type' })).toThrow()
  })

  it('拒绝 published=false(运行时 bundle 不允许)', () => {
    expect(() => PoiSchema.parse({ ...validPoi, published: false })).toThrow()
  })
})

describe('CityBundleSchema · Munich fixture', () => {
  it('接受已批准的 fixture', () => {
    const fixture = loadFixture()
    const result = safeParseBundle(fixture)
    if (!result.ok) {
      console.error('Zod issues:', result.issues)
    }
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.data.city).toBe('munich')
      expect(result.data.pois.length).toBeGreaterThanOrEqual(3)
    }
  })

  it('拒绝非法坐标', () => {
    const fixture = loadFixture()
    fixture.pois[0].position.lat = 120  // 非法
    const result = safeParseBundle(fixture)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.issues.some(i => i.path.includes('lat'))).toBe(true)
    }
  })

  it('拒绝错误 schemaVersion', () => {
    const fixture = loadFixture()
    ;(fixture as any).schemaVersion = 999
    expect(safeParseBundle(fixture).ok).toBe(false)
  })

  it('拒绝错误 contentVersion 格式', () => {
    const fixture = loadFixture()
    ;(fixture as any).contentVersion = 'not-semver'
    expect(safeParseBundle(fixture).ok).toBe(false)
  })

  it('拒绝引用不存在的 POI 的 quest', () => {
    const fixture = loadFixture()
    fixture.quests = [{
      id: 'q_test',
      title: { de: 'Test', zh: '测试' },
      poiId: 'nonexistent_poi',
      dialogueIds: [],
      prerequisites: [],
      reward: {},
      published: true,
    }]
    expect(safeParseBundle(fixture).ok).toBe(false)
  })

  it('拒绝引用不存在的 NPC 的 dialogue', () => {
    const fixture = loadFixture()
    fixture.dialogues = [{
      id: 'd_test',
      npcId: 'nonexistent_npc',
      startNodeId: 'start',
      nodes: [{
        id: 'start',
        npcText: { de: 'Hallo', zh: '你好' },
        choices: [],
        terminal: true,
        result: 'success',
      }],
      published: true,
    }]
    expect(safeParseBundle(fixture).ok).toBe(false)
  })

  it('不泄漏内部绝对路径(本 fixture 是 clean 的)', () => {
    const fixture = loadFixture()
    const json = JSON.stringify(fixture)
    expect(json).not.toMatch(/\/Volumes\//)  // 不应有 macOS 绝对路径
    expect(json).not.toMatch(/sk-[a-zA-Z0-9]{20,}/)  // 不应有 OpenAI/DashScope key
  })
})

describe('Phase 0 验收清单', () => {
  it('fixture 文件存在', () => {
    expect(() => loadFixture()).not.toThrow()
  })

  it('fixture 是合法 JSON', () => {
    const fixture = loadFixture()
    expect(fixture.schemaVersion).toBe(1)
    expect(fixture.city).toBe('munich')
  })
})