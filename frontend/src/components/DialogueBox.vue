<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';

const store = useGameStore();

const currentTurn = computed(() => {
  if (!store.currentNpc) return null;
  return store.currentNpc.turns[store.dialogueState.turnIndex];
});

const npcPortrait = computed(() => store.currentNpc?.npc_portrait);

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

const isAtHome = computed(() => store.currentScene === 'host_home');

function handleToggleLanguage() {
  store.toggleLanguage();
}

function handleMicRecord() {
  // 演示:录音按钮(后续接 Fun-ASR + Qwen2-Audio)
  alert('🎤 录音功能(Phase 0 步骤 2-5 完成后接入)\n\n当前对话:\n' +
        (store.dialogueState.useEnglish ? currentTurn.value?.en : currentTurn.value?.de));
}
</script>

<template>
  <Transition name="dialogue">
    <div v-if="store.dialogueState.open && store.currentNpc" class="dialogue-overlay">
      <div class="dialogue-container pixel-border">
        <!-- 左侧: NPC 立绘 + 信息 -->
        <div class="npc-panel">
          <div class="portrait-frame">
            <img v-if="npcPortrait" :src="npcPortrait" :alt="store.currentNpc.npc_name_de" class="portrait" />
          </div>
          <div class="npc-info">
            <div class="npc-name-de">{{ store.currentNpc.npc_name_de }}</div>
            <div class="npc-name-zh">{{ store.currentNpc.npc_name_zh }}</div>
            <div class="npc-role">{{ store.currentNpc.npc_role }}</div>
          </div>
        </div>

        <!-- 右侧: 对话内容 -->
        <div class="dialogue-content">
          <!-- 语言切换栏 -->
          <div class="lang-toggle-bar">
            <button
              :class="['lang-btn', { active: !store.dialogueState.useEnglish }]"
              @click="store.dialogueState.useEnglish && handleToggleLanguage()"
            >
              🇩🇪 Deutsch
            </button>
            <button
              :class="['lang-btn', { active: store.dialogueState.useEnglish }]"
              @click="!store.dialogueState.useEnglish && handleToggleLanguage()"
            >
              🇬🇧 English
            </button>
            <span class="lang-hint">
              {{ store.dialogueState.useEnglish ? '已切换到英文 (德语 XP -50%)' : '德语模式 (建议)' }}
            </span>
          </div>

          <!-- 当前台词 -->
          <div v-if="currentTurn" class="turn">
            <div v-if="!store.dialogueState.useEnglish" class="lang-section de">
              <div class="lang-label">🇩🇪 Deutsch</div>
              <div class="text de">{{ currentTurn.de }}</div>
            </div>
            <div v-else class="lang-section en">
              <div class="lang-label">🇬🇧 English</div>
              <div class="text en">{{ currentTurn.en }}</div>
            </div>

            <div class="translation">
              <span class="zh-label">中文提示:</span>
              {{ currentTurn.zh }}
            </div>
          </div>

          <!-- 选项 -->
          <div v-if="currentTurn?.options_de" class="options">
            <div class="options-label">▼ 回复选项 (德语尝试):</div>
            <button
              v-for="(opt, idx) in currentTurn.options_de"
              :key="idx"
              class="option-btn"
              @click="handleOption(opt, idx)"
            >
              <span class="option-text">{{ opt }}</span>
              <button class="mic-mini" @click.stop="handleMicRecord" title="用麦克风说出这句话">
                🎤
              </button>
            </button>
          </div>

          <!-- 底部操作 -->
          <div class="actions">
            <button v-if="isAtHome" class="action-btn back" @click="handleBackToHome">
              ← 回家
            </button>
            <button v-else class="action-btn back" @click="handleBackToCity">
              ← 返回城市地图
            </button>
            <button class="action-btn mic" @click="handleMicRecord">
              🎤 长按录音 (Phase 0 接入)
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.dialogue-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.dialogue-container {
  display: grid;
  grid-template-columns: 320px 1fr;
  width: min(95vw, 1100px);
  height: min(85vh, 600px);
  background: #2d261d;
  border-radius: 4px;
  overflow: hidden;
}

.npc-panel {
  background: linear-gradient(180deg, #3a2f23 0%, #2d261d 100%);
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  border-right: 2px solid #4a3a2a;
}

.portrait-frame {
  width: 240px;
  height: 320px;
  background: #1a1410;
  border: 3px solid #c9956b;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.portrait {
  width: 100%;
  height: 100%;
  object-fit: cover;
  image-rendering: pixelated;
}

.npc-info {
  text-align: center;
}

.npc-name-de {
  font-family: 'Courier New', monospace;
  color: #f4d35e;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 2px;
}

.npc-name-zh {
  color: #c9956b;
  font-size: 13px;
  margin-bottom: 4px;
}

.npc-role {
  color: #8a7a60;
  font-size: 11px;
  font-style: italic;
}

.dialogue-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.lang-toggle-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #1a1410;
  border: 1px solid #4a3a2a;
  border-radius: 3px;
}

.lang-btn {
  padding: 6px 12px;
  background: #2d261d;
  border: 1px solid #4a3a2a;
  border-radius: 3px;
  color: #8a7a60;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  transition: all 0.2s;
}

.lang-btn.active {
  background: #4a3a2a;
  border-color: #c9956b;
  color: #f4d35e;
  font-weight: bold;
}

.lang-hint {
  margin-left: auto;
  font-size: 11px;
  color: #8a7a60;
  font-style: italic;
}

.turn {
  background: #1a1410;
  border: 2px solid #4a3a2a;
  border-radius: 4px;
  padding: 16px;
}

.lang-section {
  margin-bottom: 12px;
}

.lang-label {
  font-size: 11px;
  color: #8a7a60;
  margin-bottom: 6px;
  font-family: 'Courier New', monospace;
}

.text.de {
  font-size: 20px;
  color: #e8d5b0;
  font-weight: bold;
  line-height: 1.4;
  font-family: 'Courier New', monospace;
}

.text.en {
  font-size: 18px;
  color: #c9956b;
  line-height: 1.4;
}

.translation {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #4a3a2a;
  color: #8a7a60;
  font-size: 13px;
}

.zh-label {
  color: #f4d35e;
  font-weight: bold;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.options-label {
  color: #f4d35e;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  margin-bottom: 4px;
}

.option-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #2d261d;
  border: 2px solid #4a3a2a;
  border-radius: 3px;
  color: #e8d5b0;
  font-size: 14px;
  text-align: left;
  transition: all 0.15s;
}

.option-btn:hover {
  background: #3a2f23;
  border-color: #c9956b;
  transform: translateX(4px);
}

.mic-mini {
  padding: 4px 8px;
  background: #1a1410;
  border-radius: 50%;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 8px;
}

.action-btn {
  padding: 10px 16px;
  background: #2d261d;
  border: 2px solid #4a3a2a;
  border-radius: 3px;
  color: #e8d5b0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  transition: all 0.15s;
}

.action-btn:hover {
  background: #3a2f23;
  border-color: #c9956b;
}

.action-btn.back { color: #8a7a60; }
.action-btn.mic { color: #d94545; }

/* Transition */
.dialogue-enter-active, .dialogue-leave-active {
  transition: opacity 0.2s;
}
.dialogue-enter-from, .dialogue-leave-to {
  opacity: 0;
}
</style>
