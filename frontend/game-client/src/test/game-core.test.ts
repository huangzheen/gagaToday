/**
 * Phase 4: Game Core 单元测试
 *
 * 审计 P0-02 推荐测试:
 * - Dialogue 从 startNode 到 terminal
 * - 不存在的 nextNodeId 被拒绝
 * - 完成任务只奖励一次
 * - 失败不会发成功奖励
 * - XP/体力/金钱边界正确
 *
 * Game Core 不依赖 Vue/Pinia/MapLibre — 纯函数,可独立测试。
 */

import { describe, expect, it } from 'vitest'

import { canAcceptQuest, completeQuest } from '../core/questEngine'
import { applyReward } from '../core/rewardEngine'
import {
  DialogueReferenceError,
  chooseNode,
  getStartNode,
  isTerminal,
  reachedSuccessNode,
} from '../core/dialogueEngine'

import {
  DIALOGUE_HANS_FRAUENKIRCHE,
  QUEST_LEARN_FRAUENKIRCHE,
} from '../data/phase4-fixture'

import type { PlayerState, Reward } from '../schemas/save'

function freshPlayer(): PlayerState {
  return {
    schemaVersion: 2,
    playerId: 'p_test',
    day: 1,
    minuteOfDay: 480,
    moneyCents: 2000,
    energy: 100,
    germanXp: 0,
    completedQuestIds: [],
    discoveredPoiIds: [],
    inventory: {},
    playerPosition: null,
    visionRadiusMeters: 500,
    currentCity: 'munich',
    savedAt: new Date().toISOString(),
  }
}

// ── rewardEngine ──
describe('rewardEngine.applyReward', () => {
  // 测试里频繁写 reward,Partial<Reward> 让缺省字段更短
  const r = (over: Partial<Reward>): Reward => ({
    unlockPoiIds: [],
    itemGrants: {},
    ...over,
  } as Reward)

  it('moneyCents + reward 不溢出 0 下限', () => {
    const s = freshPlayer()
    const out = applyReward(s, r({ moneyCents: -9999 }))
    expect(out.moneyCents).toBe(0)
  })

  it('energy clamp 到 [0, 100]', () => {
    let s = applyReward(freshPlayer(), r({ energy: -200 }))
    expect(s.energy).toBe(0)
    s = applyReward(freshPlayer(), r({ energy: 200 }))
    expect(s.energy).toBe(100)
  })

  it('germanXp 只能加不减', () => {
    const s = applyReward(freshPlayer(), r({ germanXp: 10 }))
    expect(s.germanXp).toBe(10)
    const s2 = applyReward(s, r({ germanXp: -5 }))
    expect(s2.germanXp).toBe(5)
  })

  it('discoveredPoiIds 合并去重', () => {
    const s = applyReward(freshPlayer(), r({ unlockPoiIds: ['a', 'b', 'a'] }))
    expect(s.discoveredPoiIds).toEqual(['a', 'b'])
  })

  it('itemGrants 合并累加', () => {
    const base = applyReward(freshPlayer(), r({ itemGrants: { map: 1, key: 1 } }))
    const more = applyReward(base, r({ itemGrants: { map: 1, key: 2 } }))
    expect(more.inventory).toEqual({ map: 2, key: 3 })
  })

  it('空 reward 不改 state(只更新 savedAt)', () => {
    const s = freshPlayer()
    const out = applyReward(s, r({}))
    expect(out.moneyCents).toBe(s.moneyCents)
    expect(out.energy).toBe(s.energy)
    expect(out.germanXp).toBe(s.germanXp)
  })
})

// ── questEngine ──
describe('questEngine.completeQuest', () => {
  it('首次完成:发奖励 + completedQuestIds 加进去', () => {
    const s = freshPlayer()
    const r = completeQuest(s, QUEST_LEARN_FRAUENKIRCHE)
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.rewarded).toBe(true)
    expect(r.state.germanXp).toBe(10)
    expect(r.state.completedQuestIds).toContain('quest_learn_frauenkirche')
  })

  it('幂等:已完成再调一次不发奖励', () => {
    const s = freshPlayer()
    const r1 = completeQuest(s, QUEST_LEARN_FRAUENKIRCHE)
    expect(r1.ok).toBe(true)
    if (!r1.ok) return
    const r2 = completeQuest(r1.state, QUEST_LEARN_FRAUENKIRCHE)
    expect(r2.ok).toBe(true)
    if (!r2.ok) return
    expect(r2.rewarded).toBe(false)
    // XP 还是 10(没加)
    expect(r2.state.germanXp).toBe(10)
    // completedQuestIds 仍只有 1 个
    expect(
      r2.state.completedQuestIds.filter((id) => id === 'quest_learn_frauenkirche'),
    ).toHaveLength(1)
  })

  it('前置任务未完成:拒绝', () => {
    const s = freshPlayer()
    const questWithPrereq = {
      ...QUEST_LEARN_FRAUENKIRCHE,
      id: 'q_advanced',
      prerequisites: ['q_missing'],
    }
    const r = completeQuest(s, questWithPrereq)
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.reason).toBe('prereq-not-met')
  })

  it('前置任务已完成:接受', () => {
    const s = freshPlayer()
    s.completedQuestIds = ['q_prereq_done']
    const questWithPrereq = {
      ...QUEST_LEARN_FRAUENKIRCHE,
      id: 'q_advanced',
      prerequisites: ['q_prereq_done'],
    }
    const r = completeQuest(s, questWithPrereq)
    expect(r.ok).toBe(true)
  })

  it('canAcceptQuest:已完成的不能接', () => {
    const s = freshPlayer()
    s.completedQuestIds = ['quest_learn_frauenkirche']
    expect(canAcceptQuest(s, QUEST_LEARN_FRAUENKIRCHE)).toBe(false)
  })
})

// ── dialogueEngine ──
describe('dialogueEngine', () => {
  it('getStartNode:返回 startNodeId 对应节点', () => {
    const node = getStartNode(DIALOGUE_HANS_FRAUENKIRCHE)
    expect(node.id).toBe('start')
  })

  it('getStartNode:startNodeId 不存在时抛 DialogueReferenceError', () => {
    const broken = {
      ...DIALOGUE_HANS_FRAUENKIRCHE,
      startNodeId: 'nonexistent',
    }
    expect(() => getStartNode(broken)).toThrow(DialogueReferenceError)
  })

  it('chooseNode:选 c_yes 走到 q_ask', () => {
    const start = getStartNode(DIALOGUE_HANS_FRAUENKIRCHE)
    const next = chooseNode(DIALOGUE_HANS_FRAUENKIRCHE, start, 'c_yes')
    expect(next?.id).toBe('q_ask')
  })

  it('chooseNode:选正确答案走到 q_done', () => {
    const qAsk = DIALOGUE_HANS_FRAUENKIRCHE.nodes.find((n) => n.id === 'q_ask')!
    const next = chooseNode(DIALOGUE_HANS_FRAUENKIRCHE, qAsk, 'c_correct_15')
    expect(next?.id).toBe('q_done')
  })

  it('chooseNode:选错误答案走到 q_retry', () => {
    const qAsk = DIALOGUE_HANS_FRAUENKIRCHE.nodes.find((n) => n.id === 'q_ask')!
    const next = chooseNode(DIALOGUE_HANS_FRAUENKIRCHE, qAsk, 'c_wrong_18')
    expect(next?.id).toBe('q_retry')
  })

  it('chooseNode:非法 choice id 返回 null(终止)', () => {
    const start = getStartNode(DIALOGUE_HANS_FRAUENKIRCHE)
    const next = chooseNode(DIALOGUE_HANS_FRAUENKIRCHE, start, 'c_invalid')
    expect(next).toBeNull()
  })

  it('chooseNode:nextNodeId 不存在抛 DialogueReferenceError', () => {
    const broken = {
      ...DIALOGUE_HANS_FRAUENKIRCHE,
      nodes: [
        {
          id: 'start',
          npcText: { de: 'x', zh: 'x' },
          choices: [{
            id: 'c',
            text: { de: 'x', zh: 'x' },
            nextNodeId: 'ghost',
            learningRefs: [],
          }],
        },
      ],
      startNodeId: 'start',
    }
    const start = broken.nodes[0]!
    expect(() => chooseNode(broken, start, 'c')).toThrow(DialogueReferenceError)
  })

  it('isTerminal:terminal=true 或 choices=[]', () => {
    const end = DIALOGUE_HANS_FRAUENKIRCHE.nodes.find((n) => n.id === 'end')!
    expect(isTerminal(end)).toBe(true)
    const qAsk = DIALOGUE_HANS_FRAUENKIRCHE.nodes.find((n) => n.id === 'q_ask')!
    expect(isTerminal(qAsk)).toBe(false)
  })

  it('reachedSuccessNode:走完一个 success 节点返回 true', () => {
    expect(reachedSuccessNode(DIALOGUE_HANS_FRAUENKIRCHE, new Set())).toBe(false)
    expect(
      reachedSuccessNode(DIALOGUE_HANS_FRAUENKIRCHE, new Set(['q_done'])),
    ).toBe(true)
  })
})

// ── 黄金路径 E2E(纯函数模拟) ──
describe('golden path: Hans 对话 → Quest 完成', () => {
  it('玩家正确回答 → 走到 success 节点 → 触发 quest reward', () => {
    const dialogue = DIALOGUE_HANS_FRAUENKIRCHE
    const quest = QUEST_LEARN_FRAUENKIRCHE

    // 起点
    let node = getStartNode(dialogue)
    let visited = new Set<string>([node.id])

    // 选 c_yes → q_ask
    node = chooseNode(dialogue, node, 'c_yes')!
    visited.add(node.id)
    expect(node.id).toBe('q_ask')

    // 选正确答案 c_correct_15 → q_done
    node = chooseNode(dialogue, node, 'c_correct_15')!
    visited.add(node.id)
    expect(node.id).toBe('q_done')
    expect(node.result).toBe('success')

    // 走到 success 节点 → 触发 quest 完成
    expect(reachedSuccessNode(dialogue, visited)).toBe(true)
    const player = freshPlayer()
    const r = completeQuest(player, quest)
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.state.germanXp).toBe(10)  // 10 XP
    expect(r.state.moneyCents).toBe(1900)  // 2000 - 100
    expect(r.state.energy).toBe(95)  // 100 - 5
    expect(r.state.completedQuestIds).toContain('quest_learn_frauenkirche')
  })

  it('错误路径走两步重试 → 最终成功 → quest 完成', () => {
    const dialogue = DIALOGUE_HANS_FRAUENKIRCHE
    let node = getStartNode(dialogue)
    node = chooseNode(dialogue, node, 'c_yes')!
    node = chooseNode(dialogue, node, 'c_wrong_18')!  // 错
    expect(node.id).toBe('q_retry')
    node = chooseNode(dialogue, node, 'c_retry_correct')!
    expect(node.id).toBe('q_done')

    const r = completeQuest(freshPlayer(), QUEST_LEARN_FRAUENKIRCHE)
    expect(r.ok).toBe(true)
  })
})