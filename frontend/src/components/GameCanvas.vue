<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import Phaser from 'phaser';
import { useGameStore } from '@/stores/game';
import BootScene from '@/phaser/BootScene';
import HomeScene from '@/phaser/HomeScene';
import CityScene from '@/phaser/CityScene';

const gameStore = useGameStore();
const containerRef = ref(null);
let game = null;
let lastView = null;

onMounted(() => {
  game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: containerRef.value,
    width: 1024,
    height: 576,
    backgroundColor: '#1a1410',
    pixelArt: true,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    scene: [BootScene, HomeScene, CityScene],
  });

  // Phaser 点击事件 → 通知 Vue store
  game.events.on('scenePointClicked', (sceneId) => {
    gameStore.enterScene(sceneId);
  });

  game.events.on('returnToCity', () => {
    gameStore.returnToCity();
  });

  // 寄宿家庭内部事件
  game.events.on('homeAction', (action) => {
    if (action === 'eat_breakfast') gameStore.eatBreakfast();
    if (action === 'greet_host') gameStore.greetHost();
    if (action === 'leave_home') gameStore.leaveHome();
  });
});

// 监听 Vue store 的 currentView 切换 Phaser scene
watch(() => gameStore.currentView, (newView) => {
  if (!game || newView === lastView) return;
  lastView = newView;
  if (newView === 'home') {
    game.scene.start('HomeScene');
  } else if (newView === 'city') {
    game.scene.start('CityScene');
  }
});

onUnmounted(() => {
  if (game) game.destroy(true);
});
</script>

<template>
  <div ref="containerRef" class="game-canvas"></div>
</template>

<style scoped>
.game-canvas {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>