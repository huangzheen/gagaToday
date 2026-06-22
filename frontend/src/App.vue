<script setup>
import StatusBar from './components/StatusBar.vue';
import GameCanvas from './components/GameCanvas.vue';
import DialogueBox from './components/DialogueBox.vue';
import EventModal from './components/EventModal.vue';
import DaySummaryModal from './components/DaySummaryModal.vue';
import MvpHud from './components/MvpHud.vue';
import { useGameStore } from '@/stores/game';
import { computed } from 'vue';

const store = useGameStore();

// 当前场景图缩略名(footer 提示)
const locationHint = computed(() => {
  if (store.currentView === 'home') return '🏠 Gastfamilie';
  if (store.currentView === 'city') return '🗺️ München Karte';
  return '📍 ' + (store.currentScene || '—');
});
</script>

<template>
  <div class="game-root">
    <!-- Phaser 全屏像素艺术场景 -->
    <GameCanvas />

    <!-- 左上角紧凑状态卡 -->
    <StatusBar />

    <!-- 右侧 MVP 操作与任务面板 -->
    <MvpHud />

    <!-- 右下角场景提示 + 推进时间 -->
    <div class="scene-hint">
      <span class="hint-loc">{{ locationHint }}</span>
      <button
        v-if="store.currentView !== 'scene' && !store.dialogueState?.open"
        class="hint-advance"
        :class="{ night: store.currentTimeBlock === 'night' }"
        @click="store.currentTimeBlock === 'night' ? store.endDay() : store.advanceTime()"
        :title="store.currentTimeBlock === 'night' ? '睡觉结算' : `推进到 ${store.nextTimeBlock}`"
      >
        <span v-if="store.currentTimeBlock === 'night'">💤 Schlafen</span>
        <span v-else>▶ {{ store.nextTimeBlock || '—' }}</span>
      </button>
    </div>

    <!-- RPG Maker MV 风格底部对话条 -->
    <DialogueBox />

    <!-- 居中浮层 -->
    <EventModal />
    <DaySummaryModal />
  </div>
</template>

<style scoped>
.game-root {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #000;
}

/* 全屏 Phaser 场景(GameCanvas absolute inset:0) */
.game-root > :deep(.game-canvas) {
  position: absolute !important;
  inset: 0;
  z-index: 1;
}

/* 场景提示(右下角) */
.scene-hint {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: none;
}

.hint-loc {
  background: rgba(20, 30, 50, 0.85);
  border: 2px solid #4a6a9a;
  padding: 4px 10px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #f4d35e;
  border-radius: 4px;
  letter-spacing: 0;
}

.hint-advance {
  pointer-events: auto;
  padding: 6px 12px;
  background: rgba(60, 80, 120, 0.92);
  border: 2px solid #c9956b;
  border-radius: 2px;
  color: #f4d35e;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.15s;
  letter-spacing: 0;
}

.hint-advance:hover {
  background: rgba(80, 100, 150, 1);
  border-color: #fff;
  transform: translateY(-1px);
}

.hint-advance.night {
  background: rgba(40, 30, 60, 0.92);
  border-color: #8a7aaa;
  color: #d8c8f8;
}

@media (max-width: 820px) {
  .scene-hint {
    left: 12px;
    right: 12px;
    bottom: 8px;
    justify-content: space-between;
  }

  .hint-loc {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
