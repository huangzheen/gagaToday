/**
 * Phase 4: Quest Engine
 *
 * 审计 P0-02 推荐:"任务完成必须幂等"。
 * completeQuest 检查 completedQuestIds,已完成直接返回原 state(不发奖励)。
 *
 * 规则:
 * - prerequisites 全部完成才能接(返回 'prereq-not-met')
 * - 已完成 → 'already-completed',不发奖励
 * - prerequisites 缺失 → 'prereq-not-met'
 * - 成功 → 返回新 state + reward
 */

import type { PlayerState } from '../schemas/save'
import type { Quest } from '../schemas/content'

import { applyReward } from './rewardEngine'

export type CompleteQuestResult =
  | { ok: true; state: PlayerState; rewarded: boolean }
  | { ok: false; reason: 'prereq-not-met' | 'already-completed' }

export function completeQuest(state: PlayerState, quest: Quest): CompleteQuestResult {
  // 幂等:已完成不发奖励
  if (state.completedQuestIds.includes(quest.id)) {
    return { ok: true, state, rewarded: false }
  }

  // 前置检查
  if (quest.prerequisites.length > 0) {
    const allMet = quest.prerequisites.every((id) =>
      state.completedQuestIds.includes(id),
    )
    if (!allMet) {
      return { ok: false, reason: 'prereq-not-met' }
    }
  }

  // 发奖励 + 标记完成
  const rewarded = applyReward(state, quest.reward)
  return {
    ok: true,
    state: {
      ...rewarded,
      completedQuestIds: [...rewarded.completedQuestIds, quest.id],
    },
    rewarded: true,
  }
}

/**
 * 检查 quest 是否可接(纯函数)
 */
export function canAcceptQuest(state: PlayerState, quest: Quest): boolean {
  if (state.completedQuestIds.includes(quest.id)) return false
  return quest.prerequisites.every((id) =>
    state.completedQuestIds.includes(id),
  )
}