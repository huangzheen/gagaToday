<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const showSummary = computed(() => store.daySummary !== null);
const summary = computed(() => store.daySummary);

const germanLevel = computed(() => {
  const xp = summary.value?.skills.german_xp || 0;
  if (xp >= 100) return 'A1';
  if (xp >= 50) return 'A0+';
  return 'A0';
});

function handleStartNextDay() {
  store.startNextDay();
}
</script>

<template>
  <Transition name="summary">
    <div v-if="showSummary" class="summary-overlay">
      <div class="summary-card pixel-border">
        <div class="summary-header">
          <h2>🌙 Tag {{ summary.day }} Zusammenfassung</h2>
          <p class="summary-date">
            Y{{ summary.date.year }} · {{ summary.date.month }}/{{ summary.date.day }}
          </p>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-label">体力</div>
            <div class="stat-value">{{ summary.energy }}<span class="unit">/100</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">😊</div>
            <div class="stat-label">心情</div>
            <div class="stat-value">{{ summary.mood }}<span class="unit">/100</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">😰</div>
            <div class="stat-label">压力</div>
            <div class="stat-value">{{ summary.stress }}<span class="unit">/100</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💶</div>
            <div class="stat-label">现金</div>
            <div class="stat-value">€{{ summary.money.toFixed(2) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👨‍👩‍👧</div>
            <div class="stat-label">父母信任</div>
            <div class="stat-value">{{ summary.parent_trust }}<span class="unit">/100</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🇩🇪</div>
            <div class="stat-label">德语水平</div>
            <div class="stat-value">{{ germanLevel }}</div>
          </div>
        </div>

        <div class="achievements">
          <div class="ach-row">
            <span class="ach-icon">✅</span>
            <span class="ach-text">完成任务: <b>{{ summary.completed_tasks }}</b> 个</span>
          </div>
          <div class="ach-row">
            <span class="ach-icon">💸</span>
            <span class="ach-text">交易笔数: <b>{{ summary.transactions_count }}</b></span>
          </div>
          <div class="ach-row">
            <span class="ach-icon">📚</span>
            <span class="ach-text">
              经验:
              DE <b>+{{ summary.skills.german_xp }}</b> ·
              EN <b>+{{ summary.skills.english_xp }}</b> ·
              Life <b>+{{ summary.skills.life_xp }}</b>
            </span>
          </div>
        </div>

        <button class="next-day-btn" @click="handleStartNextDay">
          ☀️ Neuer Tag · 开始下一天 ({{ summary.day + 1 }})
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.summary-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
}

.summary-card {
  width: min(90vw, 600px);
  background: linear-gradient(180deg, #2d261d 0%, #1a1410 100%);
  border: 3px solid #c9956b;
  border-radius: 6px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  font-family: 'Courier New', monospace;
  box-shadow: 0 0 48px rgba(244, 211, 94, 0.2);
}

.summary-header {
  text-align: center;
  border-bottom: 1px dashed #4a3a2a;
  padding-bottom: 16px;
}

.summary-header h2 {
  color: #f4d35e;
  font-size: 22px;
  margin: 0 0 4px;
  text-shadow: 1px 1px 0 #000;
}

.summary-date {
  color: #8a7a60;
  font-size: 12px;
  margin: 0;
  letter-spacing: 1px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-card {
  background: #1a1410;
  border: 1px solid #4a3a2a;
  border-radius: 4px;
  padding: 12px 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-icon { font-size: 24px; }

.stat-label {
  color: #8a7a60;
  font-size: 11px;
  letter-spacing: 1px;
}

.stat-value {
  color: #f4d35e;
  font-size: 20px;
  font-weight: bold;
}

.stat-value .unit {
  color: #8a7a60;
  font-size: 12px;
  font-weight: normal;
}

.achievements {
  background: #1a1410;
  border: 1px dashed #4a3a2a;
  border-radius: 4px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ach-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e8d5b0;
  font-size: 13px;
}

.ach-icon { font-size: 16px; }
.ach-text b { color: #f4d35e; }

.next-day-btn {
  margin-top: 8px;
  padding: 12px 24px;
  background: #4a3a2a;
  border: 2px solid #f4d35e;
  border-radius: 4px;
  color: #f4d35e;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.15s;
}

.next-day-btn:hover {
  background: #6a5a3a;
  border-color: #fff5c5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(244, 211, 94, 0.2);
}

/* Transition */
.summary-enter-active, .summary-leave-active {
  transition: opacity 0.3s;
}
.summary-enter-active .summary-card,
.summary-leave-active .summary-card {
  transition: transform 0.3s ease-out;
}
.summary-enter-from, .summary-leave-to {
  opacity: 0;
}
.summary-enter-from .summary-card, .summary-leave-to .summary-card {
  transform: scale(0.92) translateY(20px);
}
</style>