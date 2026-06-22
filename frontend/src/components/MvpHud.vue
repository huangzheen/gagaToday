<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const locationName = computed(() => {
  const location = store.currentLocation;
  if (!location) return 'München';
  return `${location.name_de} · ${location.name_zh}`;
});

const progressText = computed(() => `${store.completion.done}/${store.completion.total}`);
const mapDestinations = computed(() => store.scenePoints.filter((location) => location.id !== store.playerState.location_id));

function taskState(task) {
  if (store.completedTaskIds.has(task.id)) return 'done';
  if (store.playerState.active_task_ids.includes(task.id)) return 'active';
  return 'locked';
}

function taskLabel(task) {
  const state = taskState(task);
  if (state === 'done') return '完成';
  if (state === 'active') return '进行中';
  return '未触发';
}
</script>

<template>
  <aside class="mvp-hud">
    <section class="panel location-panel">
      <div class="title-row">
        <div class="kicker">Day 1 MVP</div>
        <button class="mini-reset" @click="store.resetGame()">重开</button>
      </div>
      <h1>{{ locationName }}</h1>
      <p>{{ store.currentTimeLabel }}</p>
      <div class="progress-row">
        <span>任务闭环</span>
        <strong>{{ progressText }}</strong>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${(store.completion.done / store.completion.total) * 100}%` }"></div>
      </div>
    </section>

    <section class="panel actions-panel">
      <div class="panel-title">当前行动</div>
      <div v-if="store.suggestedActions.length" class="action-list">
        <button
          v-for="action in store.suggestedActions"
          :key="action.id"
          class="action-button"
          :data-action-id="action.id"
          :class="{ primary: action.primary }"
          @click="store.runLocationAction(action.id)"
        >
          <span class="action-copy">
            <strong>{{ action.label }}</strong>
            <small>{{ action.de }} · {{ action.detail }}</small>
          </span>
          <span class="action-arrow">›</span>
        </button>
      </div>
      <div v-else class="empty-note">
        点击地图上的 POI，或推进时间寻找下一段事件。
      </div>
      <div v-if="store.currentView === 'city'" class="destination-grid">
        <button
          v-for="location in mapDestinations"
          :key="location.id"
          class="destination-button"
          :data-location-id="location.id"
          @click="store.enterScene(location.id)"
        >
          {{ location.name_zh }}
        </button>
      </div>
      <button
        v-if="store.playerState.location_id !== 'host_home' && ['after_school', 'evening', 'night'].includes(store.currentTimeBlock)"
        class="secondary-button"
        @click="store.goHome()"
      >
        回寄宿家庭 · Nach Hause
      </button>
    </section>

    <section class="panel tasks-panel">
      <div class="panel-title">Day 1 任务</div>
      <div class="task-list">
        <div
          v-for="task in store.taskCatalog"
          :key="task.id"
          class="task-item"
          :class="taskState(task)"
        >
          <span class="task-dot"></span>
          <div>
            <strong>{{ task.title_zh }}</strong>
            <small>{{ task.description_zh }}</small>
          </div>
          <em>{{ taskLabel(task) }}</em>
        </div>
      </div>
    </section>

    <section v-if="store.recentNotices.length || store.latestTransactions.length" class="panel log-panel">
      <div class="panel-title">最近反馈</div>
      <div v-for="notice in store.recentNotices" :key="notice.id" class="notice">
        <strong>{{ notice.title }}</strong>
        <span>{{ notice.body }}</span>
      </div>
      <div v-for="tx in store.latestTransactions" :key="tx.id" class="transaction">
        <span>{{ tx.reason }}</span>
        <strong>€{{ Math.abs(tx.amount_eur).toFixed(2) }}</strong>
      </div>
    </section>

    <button class="reset-button" @click="store.resetGame()">重新开始 MVP</button>
  </aside>
</template>

<style scoped>
.mvp-hud {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 12;
  width: min(360px, calc(100vw - 320px));
  max-height: calc(100vh - 24px);
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.panel,
.reset-button {
  pointer-events: auto;
}

.panel {
  background: rgba(13, 18, 26, 0.9);
  border: 1px solid rgba(232, 213, 176, 0.18);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
  padding: 14px;
  color: #f4ecd8;
}

.kicker,
.panel-title {
  color: #7fd1b9;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.mini-reset {
  min-width: 44px;
  padding: 4px 8px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.08);
  color: #beb398;
  font-size: 11px;
}

.location-panel h1 {
  margin: 4px 0 3px;
  font-size: 22px;
  line-height: 1.15;
  letter-spacing: 0;
}

.location-panel p {
  margin: 0 0 12px;
  color: #cbbf9f;
  font-size: 13px;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  color: #d9cfb5;
  font-size: 12px;
}

.progress-row strong {
  color: #f6d36d;
}

.progress-track {
  height: 7px;
  margin-top: 7px;
  background: rgba(255, 255, 255, 0.12);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7fd1b9, #f6d36d);
  transition: width 0.25s ease;
}

.action-list,
.task-list,
.log-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-button,
.secondary-button,
.destination-button,
.reset-button {
  width: 100%;
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.08);
  color: #f8f1dd;
  text-align: left;
  transition: transform 0.12s ease, border-color 0.12s ease, background 0.12s ease;
}

.action-button.primary {
  background: rgba(127, 209, 185, 0.16);
  border-color: rgba(127, 209, 185, 0.48);
}

.action-button:hover,
.secondary-button:hover,
.reset-button:hover {
  transform: translateY(-1px);
  border-color: rgba(246, 211, 109, 0.7);
  background: rgba(246, 211, 109, 0.14);
}

.action-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.action-copy strong,
.task-item strong,
.notice strong {
  font-size: 13px;
  line-height: 1.25;
}

.action-copy small,
.task-item small,
.notice span,
.empty-note {
  color: #beb398;
  font-size: 11px;
  line-height: 1.35;
}

.action-arrow {
  color: #f6d36d;
  font-size: 24px;
}

.secondary-button {
  margin-top: 8px;
  justify-content: center;
  color: #f6d36d;
  min-height: 38px;
  text-align: center;
}

.destination-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  margin-top: 8px;
}

.destination-button {
  min-height: 34px;
  justify-content: center;
  padding: 8px;
  color: #d9cfb5;
  font-size: 12px;
  text-align: center;
}

.task-item {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  gap: 8px;
  align-items: start;
  padding: 9px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.task-item em {
  color: #897f69;
  font-size: 11px;
  font-style: normal;
  white-space: nowrap;
}

.task-item.active em {
  color: #f6d36d;
}

.task-item.done em {
  color: #7fd1b9;
}

.task-dot {
  width: 8px;
  height: 8px;
  margin-top: 4px;
  border-radius: 50%;
  background: #4b4650;
}

.task-item.active .task-dot {
  background: #f6d36d;
}

.task-item.done .task-dot {
  background: #7fd1b9;
}

.notice,
.transaction {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.notice {
  flex-direction: column;
  gap: 2px;
}

.transaction {
  color: #d9cfb5;
  font-size: 12px;
}

.transaction strong {
  color: #f6d36d;
}

.reset-button {
  justify-content: center;
  min-height: 36px;
  background: rgba(0, 0, 0, 0.34);
  color: #beb398;
  font-size: 12px;
}

@media (max-width: 820px) {
  .mvp-hud {
    left: 12px;
    right: 12px;
    top: auto;
    bottom: 176px;
    width: auto;
    max-height: 42vh;
    overflow: auto;
  }

  .tasks-panel,
  .log-panel {
    display: none;
  }
}
</style>
