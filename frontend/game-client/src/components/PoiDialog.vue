<script setup lang="ts">
/**
 * Phase 3 POI Dialog — 点击 POI marker 后弹出的详情面板
 *
 * 设计:
 * - 右下角 panel(不覆盖地图中心,留视野)
 * - 显示:POI 名字(de/zh)+ type + icon + 主图 + description + audio
 * - 按钮:关闭(默认) + 开始对话(Phase 4 接)
 * - 打开时自动 markDiscovered(由 store.openPoi 完成)
 */

import { computed, ref, watch } from 'vue'

import { usePlayerStore } from '../store/player'
import type { Poi as RuntimePoi } from '../schemas/content'

const props = defineProps<{
  poi: RuntimePoi | null
  /** 玩家离 POI 距离(米)— 用于显示「走近了 / 走远了」 */
  distanceMeters?: number | null
}>()

const emit = defineEmits<{
  close: []
  'start-dialog': [poi: RuntimePoi]
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

function onClose() {
  player.closePoi()
  emit('close')
}

function onStartDialog() {
  if (!props.poi) return
  emit('start-dialog', props.poi)
}
</script>

<template>
  <Transition name="gaga-poi-dialog">
    <div
      v-if="poi"
      class="gaga-poi-dialog"
      role="dialog"
      aria-modal="false"
      :aria-label="`POI: ${poi.name.zh}`"
      data-testid="poi-dialog"
    >
      <!-- 关闭按钮 -->
      <button
        type="button"
        class="gaga-dialog-close"
        aria-label="关闭"
        @click="onClose"
      >✕</button>

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
          type="button"
          class="gaga-dialog-btn gaga-dialog-btn--primary"
          data-testid="poi-start-dialog"
          @click="onStartDialog"
        >
          💬 开始对话 (Phase 4)
        </button>
        <button
          type="button"
          class="gaga-dialog-btn gaga-dialog-btn--secondary"
          @click="onClose"
        >
          离开
        </button>
      </div>
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
.gaga-dialog-btn--primary {
  background: #e8b85c;
  color: #14305c;
  box-shadow: 2px 2px 0 #06142a, inset 0 0 0 1px #ffcf72;
}
.gaga-dialog-btn--primary:hover {
  background: #ffcf72;
}
.gaga-dialog-btn--primary:active {
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