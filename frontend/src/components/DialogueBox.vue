<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const currentTurn = computed(() => {
  if (!store.currentNpc) return null;
  return store.currentNpc.turns[store.dialogueState.turnIndex];
});

const npcName = computed(() => store.currentNpc?.npc_name_de || '...');
const npcRole = computed(() => store.currentNpc?.npc_role || '');

const activeLanguage = computed(() => store.dialogueState.useEnglish ? 'en' : 'de');
const mainText = computed(() => {
  if (!currentTurn.value) return '';
  return activeLanguage.value === 'en' ? currentTurn.value.en : currentTurn.value.de;
});
const zhHint = computed(() => currentTurn.value?.zh || '');

const hasOptions = computed(() => Array.isArray(currentTurn.value?.options_de) && currentTurn.value.options_de.length > 0);
const isLastTurn = computed(() => {
  if (!store.currentNpc) return true;
  return store.dialogueState.turnIndex >= store.currentNpc.turns.length - 1;
});

// 闪烁"继续"指示器 ▼
const showCursor = ref(true);
let cursorInterval = null;
onMounted(() => {
  cursorInterval = setInterval(() => { showCursor.value = !showCursor.value; }, 500);
});
onUnmounted(() => {
  if (cursorInterval) clearInterval(cursorInterval);
});

function handleNext() {
  if (!hasOptions.value) {
    // 无选项时点击直接 nextTurn(最后一轮会自动关闭)
    store.nextTurn();
  }
}

function handleOption(optionText, optionIndex) {
  store.selectOption(optionIndex);
  store.nextTurn();
}

function handleBackToCity() {
  store.returnToCity();
}

function handleBackToHome() {
  store.returnToHome();
}

function handleToggleLang() {
  store.toggleLanguage();
}

const isAtHome = computed(() => store.currentScene === 'host_home');
const isOpen = computed(() => store.dialogueState.open && !!store.currentNpc);
</script>

<template>
  <Transition name="dialogue">
    <div v-if="isOpen" class="dialogue-root">
      <!-- 左上角名字标签(RPG Maker 风格) -->
      <div class="name-tag pixel-panel-name">
        <span class="name-text">{{ npcName }}</span>
        <span v-if="npcRole" class="name-role">{{ npcRole }}</span>
      </div>

      <!-- 主体对话条 -->
      <div class="dialogue-box pixel-panel-box" @click="handleNext">
        <!-- 顶部小工具栏(语言切换) -->
        <div class="toolbar" @click.stop>
          <button
            class="lang-btn"
            :class="{ active: !store.dialogueState.useEnglish }"
            @click="handleToggleLang"
          >🇩🇪 DE</button>
          <button
            class="lang-btn"
            :class="{ active: store.dialogueState.useEnglish }"
            @click="handleToggleLang"
          >🇬🇧 EN</button>
          <span class="toolbar-hint">
            {{ store.dialogueState.useEnglish ? 'English mode' : 'Deutsch mode' }}
          </span>
          <button v-if="isAtHome" class="back-btn" @click.stop="handleBackToHome">← Nach Hause</button>
          <button v-else class="back-btn" @click.stop="handleBackToCity">← Karte</button>
        </div>

        <!-- 主对话内容 -->
        <div class="main-text">
          {{ mainText }}
        </div>

        <!-- 中文提示 -->
        <div v-if="zhHint" class="zh-hint">💡 {{ zhHint }}</div>

        <!-- 选项(可选) -->
        <div v-if="hasOptions" class="options" @click.stop>
          <div class="options-label">▼ 回复选项:</div>
          <div class="options-list">
            <button
              v-for="(opt, idx) in currentTurn.options_de"
              :key="idx"
              class="option-btn"
              @click="handleOption(opt, idx)"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- 继续指示(右下角闪烁) -->
        <div v-if="!hasOptions" class="continue-indicator" :class="{ visible: showCursor }">
          ▼
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.dialogue-root {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  pointer-events: none;
}

/* 名字标签 - 浮在对话条上方 */
.name-tag {
  position: absolute;
  left: 24px;
  top: -32px;
  padding: 6px 14px 6px 12px;
  background: #1a2a5a;
  border: 3px solid #fff;
  box-shadow:
    inset 0 0 0 1px #1a2a5a,
    0 0 0 1px #0a1428;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
  font-family: 'Courier New', monospace;
  image-rendering: pixelated;
}

.name-text {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 1px;
  text-shadow: 1px 1px 0 #000;
}

.name-role {
  color: #b8c8e8;
  font-size: 10px;
  font-style: italic;
  letter-spacing: 0.5px;
}

/* 主对话条 */
.dialogue-box {
  position: relative;
  margin: 0 16px 16px 16px;
  padding: 12px 16px 14px 16px;
  min-height: 140px;
  background: #1a2a5a;
  border: 4px solid #fff;
  box-shadow:
    inset 0 0 0 2px #1a2a5a,
    0 0 0 2px #0a1428,
    0 -4px 0 rgba(10, 20, 40, 0.4);
  pointer-events: auto;
  cursor: pointer;
  font-family: 'Courier New', monospace;
  color: #fff;
  image-rendering: pixelated;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.3);
}

.lang-btn {
  padding: 2px 8px;
  background: rgba(10, 20, 40, 0.6);
  border: 1px solid #4a6a9a;
  color: #b8c8e8;
  font-family: 'Courier New', monospace;
  font-size: 10px;
  cursor: pointer;
  letter-spacing: 0.5px;
  border-radius: 0;
}

.lang-btn.active {
  background: #4a6a9a;
  color: #fff;
  border-color: #fff;
}

.toolbar-hint {
  color: #8a9aba;
  font-size: 10px;
  font-style: italic;
  margin-left: auto;
  margin-right: 8px;
}

.back-btn {
  padding: 2px 8px;
  background: rgba(244, 211, 94, 0.15);
  border: 1px solid #c9956b;
  color: #f4d35e;
  font-family: 'Courier New', monospace;
  font-size: 10px;
  cursor: pointer;
  letter-spacing: 0.5px;
}

.back-btn:hover {
  background: rgba(244, 211, 94, 0.3);
}

/* 主对话文字 */
.main-text {
  color: #fff;
  font-size: 18px;
  line-height: 1.4;
  letter-spacing: 0.5px;
  padding: 4px 0;
  text-shadow: 1px 1px 0 #000;
}

/* 中文提示 */
.zh-hint {
  margin-top: 6px;
  padding: 4px 8px;
  background: rgba(10, 20, 40, 0.5);
  border-left: 2px solid #c9956b;
  color: #b8c8e8;
  font-size: 12px;
  font-style: italic;
}

/* 选项 */
.options {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed rgba(255, 255, 255, 0.3);
}

.options-label {
  color: #f4d35e;
  font-size: 11px;
  margin-bottom: 6px;
  letter-spacing: 1px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-btn {
  padding: 6px 10px;
  background: rgba(10, 20, 40, 0.5);
  border: 2px solid #4a6a9a;
  color: #fff;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: all 0.1s;
  letter-spacing: 0.5px;
}

.option-btn:hover {
  background: #2a4a8a;
  border-color: #fff;
  transform: translateX(2px);
}

/* 继续指示(右下角闪烁 ▼) */
.continue-indicator {
  position: absolute;
  right: 16px;
  bottom: 10px;
  color: #f4d35e;
  font-size: 16px;
  font-weight: bold;
  text-shadow: 1px 1px 0 #000;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

.continue-indicator.visible {
  opacity: 1;
}

/* Transition */
.dialogue-enter-active, .dialogue-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.dialogue-enter-from, .dialogue-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>