<script setup>
import StatusBar from './components/StatusBar.vue';
import GameCanvas from './components/GameCanvas.vue';
import DialogueBox from './components/DialogueBox.vue';
import EventModal from './components/EventModal.vue';
import DaySummaryModal from './components/DaySummaryModal.vue';
</script>

<template>
  <div class="game-root">
    <StatusBar />
    <main class="game-main">
      <GameCanvas />
    </main>
    <footer class="game-footer">
      <span class="footer-text pixel-text">
        Auf nach Deutschland! | 慕尼黑 30 天德国留学生活 RPG
      </span>
      <span class="footer-version">v0.1.0 · Skeleton</span>
    </footer>
    <DialogueBox />
    <EventModal />
    <DaySummaryModal />
  </div>
</template>

<style scoped>
.game-root {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100vh;
  background: #0a0805;
}

.game-main {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #1a1410;
}

.game-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #1a1410;
  border-top: 2px solid #4a3a2a;
  font-size: 12px;
}

.footer-text { color: #f4d35e; }
.footer-version {
  color: #6a5a40;
  font-family: 'Courier New', monospace;
}
</style>