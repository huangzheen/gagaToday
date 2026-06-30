<script setup lang="ts">
/**
 * Phase 3 HUD — 右下角游戏状态栏
 *
 * 显示:
 * - Day N · HH:MM(夜晚用月亮图标,白天用太阳)
 * - Energy bar(10 格)
 * - Money (€X.XX)
 * - German XP
 * - Player position(可选)
 */

import { computed } from 'vue'

import { usePlayerStore } from '../store/player'

const player = usePlayerStore()

const energyDots = computed(() => {
  // 10 个格子,每格代表 10 体力
  return Array.from({ length: 10 }, (_, i) => i < Math.floor(player.player.energy / 10))
})

const moneyEuro = computed(() => {
  return (player.player.moneyCents / 100).toFixed(2)
})

const timeIcon = computed(() => {
  return player.isDaytime ? '☀' : '🌙'
})
</script>

<template>
  <div class="gaga-hud" data-testid="hud">
    <!-- 顶行:Day + 时间 -->
    <div class="hud-row hud-row--top">
      <span class="hud-day" data-testid="hud-day">Day {{ player.player.day }}</span>
      <span class="hud-time" :class="{ 'hud-time--night': !player.isDaytime }" data-testid="hud-time">
        {{ timeIcon }} {{ player.timeOfDay }}
      </span>
    </div>

    <!-- 中行:能量 -->
    <div class="hud-row hud-row--energy">
      <span class="hud-label">EP</span>
      <span class="hud-energy-bar" data-testid="hud-energy">
        <span
          v-for="(filled, i) in energyDots"
          :key="i"
          class="hud-energy-cell"
          :class="{ 'hud-energy-cell--filled': filled }"
        />
      </span>
      <span class="hud-value">{{ player.player.energy }}/100</span>
    </div>

    <!-- 底行:金钱 + XP -->
    <div class="hud-row hud-row--stats">
      <span class="hud-stat" data-testid="hud-money">
        <span class="hud-stat-icon">€</span>{{ moneyEuro }}
      </span>
      <span class="hud-stat" data-testid="hud-xp">
        <span class="hud-stat-icon">★</span>{{ player.player.germanXp }} XP
      </span>
    </div>

    <!-- 调试:玩家位置 -->
    <div v-if="player.player.playerPosition" class="hud-row hud-row--debug" data-testid="hud-position">
      📍 {{ player.player.playerPosition.lat.toFixed(4) }}, {{ player.player.playerPosition.lng.toFixed(4) }}
    </div>

    <!-- 暂停指示 -->
    <div v-if="player.isPaused" class="hud-paused" data-testid="hud-paused">⏸ Paused</div>
  </div>
</template>

<style>
.gaga-hud {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 10;
  background: #14305c;
  border: 3px solid #06142a;
  border-radius: 6px;
  box-shadow: 3px 3px 0 #06142a;
  padding: 10px 14px;
  min-width: 220px;
  font-family: 'Courier New', 'VT323', monospace;
  color: #ffcf72;
  font-size: 13px;
  user-select: none;
}

.hud-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}
.hud-row:last-child {
  margin-bottom: 0;
}

.hud-row--top {
  font-size: 15px;
  font-weight: bold;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(255, 207, 114, 0.3);
}
.hud-day { color: #ffcf72; }
.hud-time { color: #ffcf72; }
.hud-time--night { color: #6a8aaa; }

.hud-label {
  font-size: 11px;
  color: #8aaac8;
  width: 24px;
}
.hud-energy-bar {
  display: flex;
  gap: 2px;
  flex: 1;
}
.hud-energy-cell {
  width: 12px;
  height: 12px;
  border: 1px solid #06142a;
  background: rgba(6, 20, 42, 0.6);
}
.hud-energy-cell--filled {
  background: linear-gradient(180deg, #ffcf72, #e8b85c);
  box-shadow: inset 0 0 0 1px #ffcf72;
}
.hud-value {
  font-size: 10px;
  color: #8aaac8;
  min-width: 36px;
  text-align: right;
}

.hud-row--stats {
  font-size: 12px;
}
.hud-stat {
  display: flex;
  align-items: center;
  gap: 4px;
}
.hud-stat-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: #e8b85c;
  color: #14305c;
  border-radius: 3px;
  font-weight: bold;
  font-size: 11px;
  border: 1px solid #06142a;
}

.hud-row--debug {
  font-size: 9px;
  color: #6a8aaa;
  border-top: 1px dashed rgba(106, 138, 170, 0.3);
  padding-top: 4px;
}

.hud-paused {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff6b6b;
  color: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: bold;
  border: 1px solid #06142a;
}
</style>