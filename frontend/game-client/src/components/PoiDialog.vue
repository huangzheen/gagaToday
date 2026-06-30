<script setup lang="ts">
/**
 * Phase 4 POI Dialog — 点击 POI marker 后弹出的详情面板
 *
 * 两种模式:
 * 1. POI 模式(props.poi 存在,不在对话中):显示 POI 详情 + "开始对话"按钮
 * 2. 对话模式(player.currentDialogueId 存在):显示 NPC + 对话节点 + 选项
 *
 * 设计:
 * - 右下角 panel(不覆盖地图中心,留视野)
 * - POI 模式:icon + 名字(de/zh) + type + 主图 + 描述 + audio + 开始对话
 * - 对话模式:替换上面大部分区域,显示 NPC 名 + 节点文本 + 选择按钮
 */

import { computed, ref, watch } from 'vue'

import { usePlayerStore } from '../store/player'
import type { Poi as RuntimePoi } from '../schemas/content'

import {
  PHASE4_FIXTURE,
} from '../data/phase4-fixture'
import {
  chooseNode,
  isTerminal,
} from '../core/dialogueEngine'

const props = defineProps<{
  poi: RuntimePoi | null
  /** 玩家离 POI 距离(米)— 用于显示「走近了 / 走远了」 */
  distanceMeters?: number | null
}>()

const emit = defineEmits<{
  close: []
  'start-dialog': [poi: RuntimePoi]
  'quest-completed': [questId: string, xpDelta: number]
}>()

const player = usePlayerStore()

const mainSceneUrl = computed<string | null>(() => {
  if (!props.poi) return null
  return props.poi.sceneUrls?.[0] ?? null
})

const availableAudio = computed<Array<{ lang: 'de' | 'zh' | 'en'; url: string }>>(() => {
  if (!props.poi) return []
  const result: Array<{ lang: 'de' | 'zh' | 'en'; url: string }> = []
  const audio = props.poi.audioUrls
  if (audio.de) result.push({ lang: 'de', url: audio.de })
  if (audio.zh) result.push({ lang: 'zh', url: audio.zh })
  if (audio.en) result.push({ lang: 'en', url: audio.en })
  return result
})

const distanceLabel = computed<string | null>(() => {
  if (props.distanceMeters == null) return null
  if (props.distanceMeters < 1000) {
    return `${Math.round(props.distanceMeters)} m`
  }
  return `${(props.distanceMeters / 1000).toFixed(1)} km`
})

const imageErrored = ref(false)
watch(() => props.poi?.id, () => {
  imageErrored.value = false
})

// ── Phase 4:对话数据 ──
// 这个 POI 的 NPC(Phase 4.1 应从后端 bundle 读,目前用 fixture)
const currentNpc = computed(() => {
  if (!props.poi) return null
  return PHASE4_FIXTURE.npcs.find((n) => n.poiId === props.poi!.id) ?? null
})

const currentDialogue = computed(() => {
  if (!player.currentDialogueId) return null
  return PHASE4_FIXTURE.dialogues.find((d) => d.id === player.currentDialogueId) ?? null
})

const currentNode = computed(() => {
  if (!currentDialogue.value || !player.currentNodeId) return null
  return currentDialogue.value.nodes.find((n) => n.id === player.currentNodeId) ?? null
})

const dialogueQuest = computed(() => {
  if (!currentDialogue.value) return null
  return PHASE4_FIXTURE.quests.find(
    (q) => q.dialogueIds?.includes(currentDialogue.value!.id),
  ) ?? null
})

const dialogueEnded = computed(() => {
  if (!currentNode.value) return true
  return isTerminal(currentNode.value)
})

function onClose() {
  player.closePoi()
  player.closeDialogue()  // 同步关闭任何进行中的对话
  emit('close')
}

function onStartDialog() {
  if (!props.poi) return
  emit('start-dialog', props.poi)
}

/** 由 App.vue 调用的对话启动入口(从 NPC 的 dialogueIds 取第一个) */
function openDialogueForCurrentPoi() {
  if (!currentNpc.value) return
  const dialogue = PHASE4_FIXTURE.dialogues.find((d) => d.npcId === currentNpc.value!.id)
  if (!dialogue) return
  player.startDialogue(dialogue.id, dialogue.startNodeId)
}

/** 玩家选了对话选项 */
function onChoose(choiceId: string) {
  if (!currentDialogue.value || !currentNode.value) return
  const next = chooseNode(currentDialogue.value, currentNode.value, choiceId)
  if (next === null) {
    player.closeDialogue()
    tryCompleteQuest()
  } else {
    player.chooseDialogue(choiceId, () => next.id)
    // 检查是否到达 success 节点 + 自动完成 quest
    if (next.result === 'success') {
      tryCompleteQuest()
    }
  }
}

/** 触发 quest 完成 */
function tryCompleteQuest() {
  if (!dialogueQuest.value) return
  const xpBefore = player.player.germanXp
  const result = player.completeQuestById(
    dialogueQuest.value,
    new Set(player.visitedNodeIds),
    (visited) => {
      // 简单判定:dialogue 至少有一个 success 节点被走到
      const dialogue = currentDialogue.value
      if (!dialogue) return false
      return dialogue.nodes
        .filter((n) => n.result === 'success')
        .some((n) => visited.has(n.id))
    },
  )
  if (result.ok && result.rewarded) {
    const xpDelta = player.player.germanXp - xpBefore
    emit('quest-completed', dialogueQuest.value.id, xpDelta)
    console.info(
      `[PoiDialog] quest 完成: ${dialogueQuest.value.id} (+${xpDelta} XP)`,
    )
  }
}

// 暴露给 App.vue
defineExpose({ openDialogueForCurrentPoi })
</script>

<template>
  <Transition name="gaga-poi-dialog">
    <div
      v-if="poi"
      class="gaga-poi-dialog"
      role="dialog"
      aria-modal="false"
      :aria-label="currentDialogue
        ? `对话: ${currentNpc?.name.zh}`
        : `POI: ${poi.name.zh}`"
      data-testid="poi-dialog"
    >
      <!-- 关闭按钮 -->
      <button
        type="button"
        class="gaga-dialog-close"
        aria-label="关闭"
        @click="onClose"
      >✕</button>

      <!-- ── 对话模式 ── -->
      <template v-if="currentDialogue && currentNode && !dialogueEnded">
        <div class="gaga-dialog-header" data-testid="dialogue-header">
          <span class="gaga-dialog-icon">
            {{ currentNpc?.name?.de?.[0] ?? '👤' }}
          </span>
          <div class="gaga-dialog-titles">
            <div class="gaga-dialog-title-zh">
              {{ currentNpc?.name?.zh }}
            </div>
            <div class="gaga-dialog-title-de">
              {{ currentNpc?.name?.de }}
              <span v-if="currentNpc?.role?.zh" class="gaga-dialog-role">
                · {{ currentNpc.role.zh }}
              </span>
            </div>
          </div>
        </div>

        <!-- NPC 说话内容(德语优先,中文为翻译) -->
        <div class="gaga-dialogue-bubble" data-testid="dialogue-npc-text">
          <div class="gaga-dialogue-lang-de">
            <span class="gaga-dialogue-lang-tag">DE</span>
            {{ currentNode.npcText.de }}
          </div>
          <div class="gaga-dialogue-lang-zh">
            <span class="gaga-dialogue-lang-tag">ZH</span>
            {{ currentNode.npcText.zh }}
          </div>
        </div>

        <!-- 选项 -->
        <div class="gaga-dialogue-choices" data-testid="dialogue-choices">
          <button
            v-for="choice in currentNode.choices"
            :key="choice.id"
            type="button"
            class="gaga-dialogue-choice"
            :data-testid="`dialogue-choice-${choice.id}`"
            @click="onChoose(choice.id)"
          >
            <span class="gaga-choice-de">{{ choice.text.de }}</span>
            <span class="gaga-choice-zh">{{ choice.text.zh }}</span>
          </button>
        </div>
      </template>

      <!-- 对话结束(terminal 节点)— 显示知识卡 + 完成反馈 -->
      <template v-else-if="currentDialogue && dialogueEnded">
        <div class="gaga-dialog-header" data-testid="dialogue-end">
          <span class="gaga-dialog-icon">🎉</span>
          <div class="gaga-dialog-titles">
            <div class="gaga-dialog-title-zh">对话完成</div>
            <div class="gaga-dialog-title-de">Dialogue abgeschlossen</div>
          </div>
        </div>
        <div class="gaga-dialogue-end-msg">
          感谢与 {{ currentNpc?.name?.zh }} 的对话!
        </div>
        <div class="gaga-dialog-actions">
          <button
            type="button"
            class="gaga-dialog-btn gaga-dialog-btn--primary"
            data-testid="dialogue-close"
            @click="onClose"
          >
            继续旅程
          </button>
        </div>
      </template>

      <!-- ── POI 模式 ── -->
      <template v-else>
        <!-- 标题 -->
        <div class="gaga-dialog-header">
          <span class="gaga-dialog-icon">{{ poi.icon }}</span>
          <div class="gaga-dialog-titles">
            <div class="gaga-dialog-title-zh">{{ poi.name.zh }}</div>
            <div class="gaga-dialog-title-de">{{ poi.name.de }}</div>
          </div>
        </div>

        <!-- 元信息:type + 距离 -->
        <div class="gaga-dialog-meta">
          <span class="gaga-dialog-type" data-testid="poi-type">{{ poi.type }}</span>
          <span v-if="distanceLabel" class="gaga-dialog-distance" data-testid="poi-distance">
            📏 {{ distanceLabel }}
          </span>
        </div>

        <!-- 主图 -->
        <div v-if="mainSceneUrl && !imageErrored" class="gaga-dialog-image">
          <img
            :src="mainSceneUrl"
            :alt="poi.name.zh"
            @error="imageErrored = true"
          />
        </div>
        <div v-else class="gaga-dialog-image-placeholder">
          <span class="gaga-dialog-placeholder-icon">{{ poi.icon }}</span>
          <span class="gaga-dialog-placeholder-text">场景图暂缺</span>
        </div>

        <!-- 描述(如果有) -->
        <div v-if="poi.description" class="gaga-dialog-description">
          <p
            v-for="(text, lang) in poi.description"
            :key="lang"
            class="gaga-dialog-desc-line"
            :class="`gaga-dialog-desc-${lang}`"
          >
            <span class="gaga-dialog-desc-lang">{{ lang }}</span>
            <span>{{ text }}</span>
          </p>
        </div>

        <!-- 音频 -->
        <div v-if="availableAudio.length > 0" class="gaga-dialog-audio">
          <span class="gaga-dialog-audio-label">🔊 Audio</span>
          <audio
            v-for="audio in availableAudio"
            :key="audio.lang"
            controls
            preload="none"
            :src="audio.url"
          >
            <track kind="captions" />
          </audio>
        </div>

        <!-- 操作按钮 -->
        <div class="gaga-dialog-actions">
          <button
            v-if="currentNpc"
            type="button"
            class="gaga-dialog-btn gaga-dialog-btn--primary"
            data-testid="poi-start-dialog"
            @click="onStartDialog"
          >
            💬 与 {{ currentNpc.name.zh }} 对话
          </button>
          <button
            v-else
            type="button"
            class="gaga-dialog-btn gaga-dialog-btn--primary"
            disabled
            data-testid="poi-start-dialog-disabled"
            title="此 POI 暂无可用 NPC"
          >
            💬 暂无可对话 NPC
          </button>
          <button
            type="button"
            class="gaga-dialog-btn gaga-dialog-btn--secondary"
            @click="onClose"
          >
            离开
          </button>
        </div>
      </template>
    </div>
  </Transition>
</template>

<style>
.gaga-poi-dialog {
  position: absolute;
  right: 12px;
  bottom: 220px;  /* 在 HUD 上方 */
  z-index: 20;
  width: 320px;
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  background: #14305c;
  border: 3px solid #06142a;
  border-radius: 8px;
  box-shadow: 4px 4px 0 #06142a, inset 0 0 0 2px #1f4576;
  padding: 14px 16px 16px;
  color: #ffcf72;
  font-family: 'Courier New', 'VT323', monospace;
  font-size: 13px;
  user-select: none;
}

.gaga-dialog-close {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  background: #ff6b6b;
  color: #fff;
  border: 2px solid #06142a;
  border-radius: 4px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}
.gaga-dialog-close:hover {
  background: #ff8585;
}

.gaga-dialog-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  padding-right: 30px;
}
.gaga-dialog-icon {
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #e8b85c;
  border: 2px solid #06142a;
  border-radius: 4px;
  box-shadow: inset 0 0 0 2px #ffcf72;
  color: #14305c;
}
.gaga-dialog-titles {
  flex: 1;
  min-width: 0;
}
.gaga-dialog-title-zh {
  font-size: 16px;
  font-weight: bold;
  color: #ffcf72;
  letter-spacing: 1px;
}
.gaga-dialog-title-de {
  font-size: 11px;
  color: #8aaac8;
  font-style: italic;
}
.gaga-dialog-role {
  color: #e8b85c;
  font-style: normal;
}

/* Phase 4 对话气泡 */
.gaga-dialogue-bubble {
  background: rgba(6, 20, 42, 0.6);
  border-left: 3px solid #e8b85c;
  border-radius: 4px;
  padding: 10px 12px;
  margin-bottom: 12px;
  line-height: 1.5;
}
.gaga-dialogue-lang-de {
  font-size: 13px;
  color: #ffcf72;
  margin-bottom: 6px;
}
.gaga-dialogue-lang-zh {
  font-size: 11px;
  color: #8aaac8;
}
.gaga-dialogue-lang-tag {
  display: inline-block;
  width: 24px;
  font-size: 9px;
  font-weight: bold;
  padding: 1px 4px;
  margin-right: 6px;
  background: #e8b85c;
  color: #14305c;
  border-radius: 3px;
  letter-spacing: 1px;
  vertical-align: middle;
}

/* 选项 */
.gaga-dialogue-choices {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.gaga-dialogue-choice {
  background: #1f4576;
  border: 2px solid #06142a;
  border-radius: 4px;
  padding: 8px 10px;
  color: #ffcf72;
  font-family: inherit;
  font-size: 11px;
  text-align: left;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.gaga-dialogue-choice:hover {
  background: #2a578a;
  transform: translateX(2px);
}
.gaga-dialogue-choice:active {
  transform: translateX(2px) translateY(1px);
}
.gaga-choice-de {
  font-size: 12px;
  color: #ffcf72;
}
.gaga-choice-zh {
  font-size: 10px;
  color: #8aaac8;
}

.gaga-dialogue-end-msg {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.4);
  border-radius: 4px;
  padding: 12px;
  color: #4ade80;
  font-size: 12px;
  text-align: center;
  margin-bottom: 12px;
}

.gaga-dialog-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: #8aaac8;
  margin-bottom: 8px;
}
.gaga-dialog-type {
  background: rgba(232, 184, 92, 0.2);
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.gaga-dialog-distance {
  color: #6a8aaa;
}

.gaga-dialog-image {
  width: 100%;
  height: 160px;
  background: #06142a;
  border: 2px solid #06142a;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gaga-dialog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  image-rendering: pixelated;
}
.gaga-dialog-image-placeholder {
  width: 100%;
  height: 100px;
  background: linear-gradient(135deg, #06142a 0%, #14305c 100%);
  border: 2px solid #06142a;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.gaga-dialog-placeholder-icon {
  font-size: 32px;
  opacity: 0.5;
}
.gaga-dialog-placeholder-text {
  font-size: 10px;
  color: #6a8aaa;
}

.gaga-dialog-description {
  background: rgba(6, 20, 42, 0.4);
  border-radius: 4px;
  padding: 8px 10px;
  margin-bottom: 10px;
  font-size: 11px;
  line-height: 1.5;
}
.gaga-dialog-desc-line {
  display: flex;
  gap: 6px;
  margin: 0 0 4px 0;
}
.gaga-dialog-desc-line:last-child { margin-bottom: 0; }
.gaga-dialog-desc-lang {
  flex-shrink: 0;
  width: 18px;
  font-weight: bold;
  text-transform: uppercase;
  color: #e8b85c;
  font-size: 10px;
  padding-top: 1px;
}
.gaga-dialog-desc-zh .gaga-dialog-desc-lang { color: #ffcf72; }

.gaga-dialog-audio {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}
.gaga-dialog-audio-label {
  font-size: 10px;
  color: #8aaac8;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.gaga-dialog-audio audio {
  width: 100%;
  height: 32px;
}

.gaga-dialog-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(255, 207, 114, 0.3);
}
.gaga-dialog-btn {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #06142a;
  border-radius: 4px;
  font-family: inherit;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  letter-spacing: 1px;
}
.gaga-dialog-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
.gaga-dialog-btn--primary {
  background: #e8b85c;
  color: #14305c;
  box-shadow: 2px 2px 0 #06142a, inset 0 0 0 1px #ffcf72;
}
.gaga-dialog-btn--primary:hover:not(:disabled) {
  background: #ffcf72;
}
.gaga-dialog-btn--primary:active:not(:disabled) {
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0 #06142a, inset 0 0 0 1px #ffcf72;
}
.gaga-dialog-btn--secondary {
  background: #14305c;
  color: #ffcf72;
  box-shadow: inset 0 0 0 1px #ffcf72;
}
.gaga-dialog-btn--secondary:hover {
  background: #1f4576;
}

/* transition */
.gaga-poi-dialog-enter-active, .gaga-poi-dialog-leave-active {
  transition: all 0.2s ease;
}
.gaga-poi-dialog-enter-from, .gaga-poi-dialog-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>