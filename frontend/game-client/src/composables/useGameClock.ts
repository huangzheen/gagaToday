/**
 * Phase 3: 游戏内时钟
 *
 * 设计:
 * - setInterval 每 REAL_INTERVAL_MS 触发一次
 * - 每次推进 GAME_MINUTES_PER_TICK 个游戏内分钟
 * - 真实 1 秒 = 游戏内 MINUTES_PER_SECOND 分钟(默认 1:1,1 秒 = 1 分钟 → 24 分钟 = 1 天)
 * - 暂停时不推进(player store 的 isPaused 标志)
 *
 * 用法:
 *   const { start, stop, isRunning } = useGameClock()
 *   onMounted(start)
 *   onBeforeUnmount(stop)
 */

import { onBeforeUnmount, ref } from 'vue'

import { usePlayerStore } from '../store/player'

/** 默认速率:每真实秒 = 1 游戏分钟 → 现实 24 分钟 = 游戏 1 天 */
const DEFAULT_MINUTES_PER_SECOND = 1

/** setInterval 周期(毫秒) */
const DEFAULT_REAL_INTERVAL_MS = 1000

export interface UseGameClockOptions {
  minutesPerSecond?: number
  intervalMs?: number
}

export function useGameClock(opts: UseGameClockOptions = {}) {
  const minutesPerSecond = opts.minutesPerSecond ?? DEFAULT_MINUTES_PER_SECOND
  const intervalMs = opts.intervalMs ?? DEFAULT_REAL_INTERVAL_MS

  const isRunning = ref(false)
  const player = usePlayerStore()

  let timer: number | null = null

  function start() {
    if (isRunning.value) return
    const tickMinutes = Math.max(1, Math.round(minutesPerSecond * (intervalMs / 1000)))
    timer = window.setInterval(() => {
      // player store 内部会判断 isPaused
      player.tickTime(tickMinutes)
    }, intervalMs)
    isRunning.value = true
  }

  function stop() {
    if (timer !== null) {
      window.clearInterval(timer)
      timer = null
    }
    isRunning.value = false
  }

  onBeforeUnmount(stop)

  return { start, stop, isRunning }
}