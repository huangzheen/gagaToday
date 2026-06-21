<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const dateLabel = computed(() => {
  const months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  return `Y${store.stats.date.year} · ${months[store.stats.date.month - 1]} ${store.stats.date.day}`;
});

const moodIcon = computed(() => {
  if (store.stats.mood >= 70) return '😊';
  if (store.stats.mood >= 40) return '😐';
  return '😔';
});

const energyColor = computed(() => {
  if (store.stats.energy >= 60) return '#7dcf6f';
  if (store.stats.energy >= 30) return '#e8a83a';
  return '#d94545';
});
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
        <span class="icon">⚡</span>
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
        <span class="flag">🇩🇪</span>
        <span class="level">{{ store.stats.language.german }}</span>
      </div>
      <div class="lang en">
        <span class="flag">🇬🇧</span>
        <span class="level">{{ store.stats.language.english }}</span>
      </div>
    </div>

    <!-- 当前位置 -->
    <div class="cell right">
      <div class="loc-icon">📍</div>
      <div class="loc-text">{{ store.stats.location.toUpperCase() }}</div>
    </div>
  </header>
</template>

<style scoped>
.status-bar {
  display: grid;
  grid-template-columns: 1fr 1.2fr 0.6fr 0.8fr 0.7fr;
  gap: 12px;
  align-items: center;
  padding: 10px 16px;
  background: linear-gradient(180deg, #3a2f23 0%, #2d261d 100%);
  font-family: 'Courier New', monospace;
  height: 72px;
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

.stat .icon {
  font-size: 14px;
}

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
</style>