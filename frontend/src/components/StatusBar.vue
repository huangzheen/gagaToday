<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const dateLabel = computed(() => {
  const months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  return `${months[store.stats.date.month - 1]} ${store.stats.date.day}`;
});

const moodIcon = computed(() => {
  if (store.stats.mood >= 70) return '😊';
  if (store.stats.mood >= 40) return '😐';
  return '😟';
});

const energyColor = computed(() => {
  if (store.stats.energy >= 60) return '#7dcf6f';
  if (store.stats.energy >= 30) return '#e8a83a';
  return '#d94545';
});

const moneyColor = computed(() => {
  if (store.stats.money >= 300) return '#f4d35e';
  if (store.stats.money >= 100) return '#e8a83a';
  return '#d94545';
});
</script>

<template>
  <div class="status-card pixel-panel">
    <!-- 角色 + 日期 + 时段 -->
    <div class="row top">
      <div class="char">
        <span class="avatar">👧</span>
        <div class="char-info">
          <div class="name">{{ store.stats.name }} · {{ store.stats.age }}</div>
          <div class="date">{{ dateLabel }}</div>
        </div>
      </div>
      <div class="time">
        <div class="time-label">UHR</div>
        <div class="time-value">{{ store.currentTimeLabel }}</div>
      </div>
    </div>

    <!-- 体力 + 心情 -->
    <div class="row stats">
      <div class="stat">
        <span class="icon">{{ moodIcon }}</span>
        <div class="bar">
          <div class="fill" :style="{ width: store.stats.mood + '%' }"></div>
        </div>
        <span class="value">{{ store.stats.mood }}</span>
      </div>
      <div class="stat">
        <span class="icon">⚡</span>
        <div class="bar">
          <div class="fill" :style="{ width: store.stats.energy + '%', background: energyColor }"></div>
        </div>
        <span class="value">{{ store.stats.energy }}</span>
      </div>
    </div>

    <!-- 资金 + 语言 -->
    <div class="row bottom">
      <div class="money">
        <span class="money-icon">€</span>
        <span class="money-value" :style="{ color: moneyColor }">{{ store.stats.money.toFixed(0) }}</span>
      </div>
      <div class="langs">
        <span class="lang de">
          <span class="flag">🇩🇪</span>
          <span class="level">{{ store.stats.language.german }}</span>
        </span>
        <span class="lang en">
          <span class="flag">🇬🇧</span>
          <span class="level">{{ store.stats.language.english }}</span>
        </span>
      </div>
    </div>

    <!-- 当前任务 -->
    <div v-if="store.activeTasks.length" class="row task">
      <span class="task-label">▸ {{ store.activeTasks[0].title_zh }}</span>
      <span v-if="store.activeTasks.length > 1" class="task-more">+{{ store.activeTasks.length - 1 }}</span>
    </div>
  </div>
</template>

<style scoped>
.status-card {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 10;
  width: 280px;
  padding: 8px 10px;
  background: rgba(15, 22, 42, 0.92);
  border: 3px solid #fff;
  box-shadow:
    inset 0 0 0 1px #1a2a5a,
    0 0 0 1px #1a2a5a,
    0 2px 8px rgba(0, 0, 0, 0.4);
  font-family: 'Courier New', monospace;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-radius: 0;
  image-rendering: pixelated;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.top {
  border-bottom: 1px dashed #4a6a9a;
  padding-bottom: 4px;
}

.char {
  display: flex;
  align-items: center;
  gap: 6px;
}

.avatar {
  font-size: 22px;
  filter: drop-shadow(0 1px 0 #000);
}

.char-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.name {
  color: #f4d35e;
  font-size: 12px;
  font-weight: bold;
  text-shadow: 1px 1px 0 #000;
}

.date {
  color: #8a9aba;
  font-size: 10px;
  letter-spacing: 1px;
}

.time {
  text-align: right;
}

.time-label {
  color: #6a7a9a;
  font-size: 9px;
  letter-spacing: 1px;
}

.time-value {
  color: #c9956b;
  font-size: 11px;
  font-weight: bold;
  letter-spacing: 0.5px;
}

.stats {
  padding: 2px 0;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.stat .icon {
  font-size: 12px;
}

.bar {
  flex: 1;
  height: 6px;
  background: #0a1428;
  border: 1px solid #2a3a5a;
  border-radius: 0;
}

.bar .fill {
  height: 100%;
  background: #7dcf6f;
  transition: width 0.3s;
}

.value {
  color: #c9956b;
  font-size: 10px;
  font-weight: bold;
  min-width: 18px;
  text-align: right;
}

.bottom {
  border-top: 1px dashed #4a6a9a;
  padding-top: 4px;
}

.money {
  display: flex;
  align-items: center;
  gap: 4px;
}

.money-icon {
  color: #f4d35e;
  font-size: 14px;
  font-weight: bold;
}

.money-value {
  font-size: 14px;
  font-weight: bold;
  text-shadow: 1px 1px 0 #000;
}

.langs {
  display: flex;
  gap: 6px;
}

.lang {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  background: #0a1428;
  border: 1px solid #2a3a5a;
  border-radius: 0;
}

.lang.de { border-color: #4a6a8a; }
.lang.en { border-color: #8a5a5a; }

.flag { font-size: 11px; }

.level {
  color: #c9956b;
  font-size: 10px;
  font-weight: bold;
}

.task {
  border-top: 1px dashed #4a6a9a;
  padding-top: 4px;
  background: rgba(244, 211, 94, 0.08);
  margin: 2px -10px -8px -10px;
  padding: 4px 10px;
}

.task-label {
  color: #f4d35e;
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 0.5px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-more {
  background: #c9956b;
  color: #1a1410;
  font-size: 9px;
  font-weight: bold;
  padding: 0 5px;
  border-radius: 6px;
}
</style>