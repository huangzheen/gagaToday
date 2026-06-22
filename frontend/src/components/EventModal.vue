<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const showModal = computed(() => store.currentEvent !== null);
const event = computed(() => store.currentEvent);

const actionSummary = computed(() => {
  const e = event.value;
  if (!e) return [];
  return (e.actions || []).map((a) => {
    if (a.type === 'unlock_task') return `🔓 任务解锁: ${a.task_id}`;
    if (a.type === 'open_dialogue') return `💬 触发对话: ${a.dialogue_id}`;
    return `• ${a.type}`;
  });
});

function handleContinue() {
  store.dismissEvent();
}
</script>

<template>
  <Transition name="event-modal">
    <div v-if="showModal" class="event-modal-overlay" @click.self="handleContinue">
      <div class="event-modal pixel-border">
        <div class="event-header">
          <span class="event-time-tag">{{ event.time_block }} · {{ event.location_id }}</span>
          <span class="event-id">#{{ event.id }}</span>
        </div>
        <h2 class="event-title">{{ event.title_zh }}</h2>
        <p class="event-summary">{{ event.summary_zh }}</p>

        <div v-if="actionSummary.length" class="event-actions">
          <div class="actions-label">即将发生:</div>
          <ul>
            <li v-for="(line, idx) in actionSummary" :key="idx">{{ line }}</li>
          </ul>
        </div>

        <button class="event-continue-btn" @click="handleContinue">
          继续 →
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.event-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.event-modal {
  width: min(90vw, 520px);
  background: linear-gradient(180deg, #3a2f23 0%, #2d261d 100%);
  border: 3px solid #c9956b;
  border-radius: 4px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: 'Courier New', monospace;
  box-shadow: 0 0 32px rgba(244, 211, 94, 0.15);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #8a7a60;
}

.event-time-tag {
  background: #1a1410;
  padding: 2px 8px;
  border: 1px solid #4a3a2a;
  border-radius: 2px;
  letter-spacing: 1px;
}

.event-id {
  font-style: italic;
}

.event-title {
  color: #f4d35e;
  font-size: 22px;
  margin: 0;
  text-shadow: 1px 1px 0 #000;
  font-weight: bold;
}

.event-summary {
  color: #e8d5b0;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  padding: 12px;
  background: #1a1410;
  border-left: 3px solid #c9956b;
  border-radius: 2px;
}

.event-actions {
  background: #1a1410;
  border: 1px dashed #4a3a2a;
  border-radius: 3px;
  padding: 10px 14px;
}

.actions-label {
  color: #8a7a60;
  font-size: 11px;
  margin-bottom: 6px;
  letter-spacing: 1px;
}

.event-actions ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-actions li {
  color: #c9956b;
  font-size: 13px;
}

.event-continue-btn {
  margin-top: 8px;
  padding: 10px 20px;
  background: #5a4a3a;
  border: 2px solid #c9956b;
  border-radius: 3px;
  color: #f4d35e;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.15s;
  align-self: flex-end;
}

.event-continue-btn:hover {
  background: #6a5a4a;
  border-color: #f4d35e;
  transform: translateX(2px);
}

/* Transition */
.event-modal-enter-active, .event-modal-leave-active {
  transition: opacity 0.2s;
}
.event-modal-enter-active .event-modal,
.event-modal-leave-active .event-modal {
  transition: transform 0.25s ease-out;
}
.event-modal-enter-from, .event-modal-leave-to {
  opacity: 0;
}
.event-modal-enter-from .event-modal, .event-modal-leave-to .event-modal {
  transform: scale(0.95) translateY(-8px);
}
</style>