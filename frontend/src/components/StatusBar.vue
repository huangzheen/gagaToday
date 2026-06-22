<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const dateLabel = computed(() => {
  const months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  return `Y${store.stats.date.year} · ${months[store.stats.date.month - 1]} ${store.stats.date.day}`;
});

const moodIcon = computed(() => {
  if (store.stats.mood >= 70) return ':)';
  if (store.stats.mood >= 40) return ':|';
  return ':(';
});

const energyColor = computed(() => {
  if (store.stats.energy >= 60) return '#7dcf6f';
  if (store.stats.energy >= 30) return '#e8a83a';
  return '#d94545';
});

const canAdvance = computed(() => {
  return store.nextTimeBlock !== null && !store.dialogueState.open;
});

const isNight = computed(() => store.currentTimeBlock === 'night');

function handleAdvance() {
  if (isNight.value) {
    store.endDay();
  } else {
    store.advanceTime();
  }
}
</script>

<template>
  <header class="status-bar pixel-border">
    <!-- 主角名 + 日期 -->
    <div class="cell left">
      <div class="name">{{ store.stats.name }}, {{ store.stats.age }}</div>
      <div class="date">{{ dateLabel }}</div>
    </div>

    <!-- 心情 + 体力 -->
    <div class="cell">
      <div class="stat">
        <span class="icon">{{ moodIcon }}</span>
        <div class="bar">
          <div class="fill" :style="{ width: store.stats.mood + '%' }"></div>
        </div>
        <span class="value">{{ store.stats.mood }}</span>
      </div>
      <div class="stat">
        <span class="icon">EN</span>
        <div class="bar">
          <div class="fill" :style="{ width: store.stats.energy + '%', background: energyColor }"></div>
        </div>
        <span class="value">{{ store.stats.energy }}</span>
      </div>
    </div>

    <!-- 资金 -->
    <div class="cell money">
      <span class="icon">€</span>
      <span class="value">{{ store.stats.money }}</span>
    </div>

    <!-- 语言能力 -->
    <div class="cell languages">
      <div class="lang de">
        <span class="flag">DE</span>
        <span class="level">{{ store.stats.language.german }}</span>
      </div>
      <div class="lang en">
        <span class="flag">EN</span>
        <span class="level">{{ store.stats.language.english }}</span>
      </div>
    </div>

    <!-- 当前位置 -->
    <div class="cell right">
      <div class="loc-icon">LOC</div>
      <div class="loc-text">{{ store.stats.location.toUpperCase() }}</div>
    </div>

    <!-- 时间块 + 推进按钮 -->
    <div class="time-strip">
      <div class="time-info">
        <span class="time-label">UHRZEIT</span>
        <span class="time-value">{{ store.currentTimeLabel }}</span>
      </div>
      <button
        class="advance-btn"
        :class="{ night: isNight }"
        :disabled="!canAdvance"
        @click="handleAdvance"
        :title="isNight ? '结束今天,睡觉结算' : `推进到下一时段: ${store.nextTimeBlock}`"
      >
        {{ isNight ? '💤 Schlafen · 睡觉' : `▶ ${store.nextTimeBlock || '—'}` }}
      </button>
    </div>

    <!-- 当前任务 -->
    <div class="task-strip">
      <span class="task-label">AKTIV</span>
      <span class="task-title">{{ store.activeTasks[0]?.title_zh || '自由探索' }}</span>
      <span v-if="store.activeTasks.length > 1" class="task-more">+{{ store.activeTasks.length - 1 }}</span>
    </div>
  </header>
</template>

<style scoped>
.status-bar {
  display: grid;
  grid-template-columns: 1fr 1.2fr 0.6fr 0.8fr 0.7fr;
  grid-template-rows: auto auto auto;
  gap: 8px 12px;
  align-items: center;
  padding: 8px 16px;
  background: linear-gradient(180deg, #3a2f23 0%, #2d261d 100%);
  font-family: 'Courier New', monospace;
  min-height: 96px;
  position: relative;
}

.cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.cell.left { align-items: flex-start; }
.cell.right { align-items: flex-end; text-align: right; }

.name {
  color: #f4d35e;
  font-size: 16px;
  font-weight: bold;
  text-shadow: 1px 1px 0 #000;
}

.date {
  color: #8a7a60;
  font-size: 11px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat .icon { font-size: 14px; }

.bar {
  width: 80px;
  height: 8px;
  background: #1a1410;
  border: 1px solid #4a3a2a;
  border-radius: 2px;
  overflow: hidden;
}

.bar .fill {
  height: 100%;
  background: #7dcf6f;
  transition: width 0.3s;
}

.value {
  font-size: 11px;
  color: #c9956b;
  min-width: 24px;
}

.money {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.money .icon {
  font-size: 20px;
  color: #f4d35e;
  font-weight: bold;
}

.money .value {
  font-size: 18px;
  color: #f4d35e;
  font-weight: bold;
}

.languages {
  flex-direction: row;
  gap: 12px;
  align-items: center;
}

.lang {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #1a1410;
  border: 1px solid #4a3a2a;
  border-radius: 3px;
}

.lang.de { border-color: #5a7a8a; }
.lang.en { border-color: #8a5a5a; }

.flag { font-size: 14px; }

.level {
  font-size: 11px;
  color: #c9956b;
  font-weight: bold;
}

.loc-icon { font-size: 16px; }
.loc-text {
  font-size: 13px;
  color: #f4d35e;
  font-weight: bold;
  letter-spacing: 2px;
}

/* 时间块 strip */
.time-strip {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 0;
  border-top: 1px solid #4a3a2a;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-label {
  color: #8a7a60;
  font-size: 10px;
  letter-spacing: 1px;
}

.time-value {
  color: #e8d5b0;
  font-size: 13px;
  font-weight: bold;
}

.advance-btn {
  padding: 6px 14px;
  background: #5a4a3a;
  border: 2px solid #c9956b;
  border-radius: 3px;
  color: #f4d35e;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.15s;
}

.advance-btn:hover:not(:disabled) {
  background: #6a5a4a;
  border-color: #f4d35e;
  transform: translateX(2px);
}

.advance-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.advance-btn.night {
  background: #2a2a4a;
  border-color: #7a7aaa;
  color: #b8b8d8;
}

.advance-btn.night:hover:not(:disabled) {
  background: #3a3a5a;
  border-color: #d8d8f8;
}

/* 任务 strip */
.task-strip {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 20px;
  padding-top: 4px;
  border-top: 1px solid #4a3a2a;
}

.task-label {
  color: #8a7a60;
  font-size: 10px;
  letter-spacing: 1px;
}

.task-title {
  color: #e8d5b0;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-more {
  background: #c9956b;
  color: #1a1410;
  font-size: 10px;
  font-weight: bold;
  padding: 1px 6px;
  border-radius: 8px;
}
</style>