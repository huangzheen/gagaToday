/**
 * Phase 4: Reward Engine
 *
 * 审计 P0-02 推荐:"奖励必须是纯函数"。
 * applyReward 接收 PlayerState + Reward,返回新 PlayerState,不修改入参。
 * 这样可在测试里反复调用,Game Core 不 import Vue/Pinia/localStorage。
 *
 * 规则:
 * - moneyCents + reward.moneyCents:可负(扣费),最低 0
 * - energy + reward.energy:范围 [-100, 100],最终 clamp 到 [0, 100]
 * - germanXp + reward.germanXp:可加,不可减
 * - unlockedPoiIds:合并去重
 * - itemGrants:合并累加
 */

import type { PlayerState } from '../schemas/save'
// Reward 在 save.ts 导出(questEngine / game content 复用)
import type { Reward } from '../schemas/save'

export function applyReward(state: PlayerState, reward: Reward): PlayerState {
  const moneyDelta = reward.moneyCents ?? 0
  const energyDelta = reward.energy ?? 0
  const xpDelta = reward.germanXp ?? 0

  return {
    ...state,
    moneyCents: Math.max(0, state.moneyCents + moneyDelta),
    energy: clamp(state.energy + energyDelta, 0, 100),
    germanXp: Math.max(0, state.germanXp + xpDelta),
    discoveredPoiIds: mergeUnique(state.discoveredPoiIds, reward.unlockPoiIds ?? []),
    inventory: mergeInventory(state.inventory, reward.itemGrants ?? {}),
    savedAt: new Date().toISOString(),
  }
}

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n))
}

function mergeUnique(a: readonly string[], b: readonly string[]): string[] {
  const seen = new Set<string>(a)
  for (const id of b) seen.add(id)
  return [...seen]
}

function mergeInventory(a: Record<string, number>, b: Record<string, number>): Record<string, number> {
  return { ...a, ...b, ...addDuplicates(a, b) }
}

function addDuplicates(a: Record<string, number>, b: Record<string, number>): Record<string, number> {
  const result: Record<string, number> = {}
  for (const [k, v] of Object.entries(b)) {
    if (k in a) {
      result[k] = (a[k] ?? 0) + v
    }
  }
  return result
}