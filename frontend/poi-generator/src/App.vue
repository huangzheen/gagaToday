<template>
  <div id="app">
    <!-- 顶部栏 -->
    <header class="topbar panel">
      <div>
        <span class="title">🏗️ POI GENERATOR</span>
        <span class="subtitle"> · gagaToday</span>
      </div>
      <div class="actions">
        <span class="status-dot" :class="store.backendConnected ? 'ok' : 'missing'" />
        <span style="font-size:10px;color:var(--text-dim)">
          {{ store.backendConnected ? 'API 已连接' : 'API 未连接' }}
        </span>
      </div>
    </header>

    <!-- 卡片网格 -->
    <div class="card-container panel">
      <div class="card-header">
        <span class="card-header-title">📍 慕尼黑 POI</span>
        <span class="card-header-count">{{ store.knownPois.length }} 个</span>
      </div>
      <div class="card-grid">
        <div
          v-for="poi in store.knownPois"
          :key="poi.id"
          class="poi-card"
          :class="{ selected: store.currentPoiId === poi.id, published: isPublished(poi.id) }"
          draggable="true"
          @dragstart="onDragStart($event, poi)"
          @click="openEditor(poi.id)"
        >
          <!-- 场景主图(16:9) -->
          <div class="poi-card-img-wrap">
            <img
              v-if="primaryImageExists(poi.id)"
              :src="`/assets/scenes/munich/${poi.id}/_reference/ref_${poi.id}.png?t=${cardCacheBust}`"
              :alt="poi.name_zh"
              @error="onCardImgError(poi.id)"
            />
            <span v-else class="placeholder-icon">{{ poi.icon || '📍' }}</span>
          </div>
          <!-- 名称 -->
          <div class="poi-card-name">{{ poi.name_zh }}</div>
          <div class="poi-card-de">{{ poi.name_de }}</div>
          <!-- 信息(国家 · 城市 · 类型) -->
          <div class="poi-card-info">
            <span class="info-flag">🇩🇪</span>
            <span>慕尼黑</span>
            <span class="info-sep">·</span>
            <span>{{ poi.type }}</span>
          </div>
        </div>
        <div class="poi-card add-card" @click="showAddDialog = true">
          <div class="poi-card-img-wrap">
            <span class="add-icon">＋</span>
          </div>
          <span class="poi-card-name" style="text-align:center;opacity:.6">添加新 POI</span>
        </div>
      </div>
    </div>

    <!-- 右侧发布栏 -->
    <div
      class="publish-bar panel"
      @dragover.prevent
      @drop="onDrop"
      @dragenter="dragOver = true"
      @dragleave="dragOver = false"
      :class="{ 'drag-over': dragOver }"
    >
      <div class="publish-header">📤 已发布</div>
      <div class="publish-list" v-if="publishedPois.length">
        <div
          v-for="p in publishedPois"
          :key="p.id"
          class="publish-item"
          :class="{ 'is-new': p.isNew }"
        >
          <span class="pi-city">MUC</span>
          <span class="pi-type">{{ p.type }}</span>
          <span class="pi-name">{{ p.name_zh }}</span>
        </div>
      </div>
      <div class="publish-empty" v-else>
        <span class="drop-hint">拖入卡片<br/>发布到地图</span>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="editingPoi" @click.self="closeEditor">
        <div class="modal-panel panel">
          <div class="modal-header">
            <span class="modal-title">
              {{ editingPoi?.icon }} {{ editingPoi?.name_zh }}
            </span>

            <!-- 全局模型选择器(整个弹窗内的 AI 调用都读这两个) -->
            <div class="modal-models">
              <label class="model-select">
                <span class="model-label">🎨 图像</span>
                <select v-model="store.imageModel" :disabled="!store.availableImageModels.length">
                  <option v-for="m in store.availableImageModels" :key="m.id" :value="m.id">
                    {{ m.name || m.id }}
                  </option>
                </select>
              </label>
              <label class="model-select">
                <span class="model-label">📝 文本</span>
                <select v-model="store.textModel" :disabled="!store.availableTextModels.length">
                  <option v-for="m in store.availableTextModels" :key="m.id" :value="m.id">
                    {{ m.name || m.id }}
                  </option>
                </select>
              </label>
            </div>

            <div class="modal-actions">
              <button class="btn success" @click="publishCurrent" style="padding:4px 10px">
                📤 发布
              </button>
              <button class="btn" @click="closeEditor" style="padding:4px 10px">✕</button>
            </div>
          </div>
          <div class="tab-bar">
            <button v-for="tab in TABS" :key="tab.id" class="tab-btn" :class="{ active: store.activeTab === tab.id }" @click="store.selectTab(tab.id)">
              {{ tab.label }}
            </button>
          </div>
          <div class="content-area">
            <POIInfoForm v-if="store.activeTab === 'info'" ref="poiInfoFormRef" @auto-fill-done="onAutoFillDone" />
            <RefWorkflow v-else-if="store.activeTab === 'refworkflow'" />
            <UploadsPanel v-else-if="store.activeTab === 'uploads'" />
            <NPCPanel v-else-if="store.activeTab === 'npc'" />
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 添加新 POI 弹窗 (2026-06-27 新增) -->
    <AddPoiDialog
      v-if="showAddDialog"
      @close="showAddDialog = false"
      @created="onPoiCreated"
    />

    <!-- 底部栏 -->
    <footer class="bottombar panel">
      <div class="model-info">
        <span title="图片生成">{{ store.availableImageModels.length ? '🎨 ' + store.imageModel : '' }}</span>
      </div>
      <span>📍 {{ currentPoi?.name_zh || '未选择' }} · {{ currentPoi?.name_de || '' }}</span>
      <span>✅ {{ store.statusSummary }} 已生成</span>
      <span v-if="store.error" style="color:var(--danger)">⚠️ {{ store.error }}</span>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref, nextTick } from 'vue'
import { useGeneratorStore, TABS } from '@/stores/generator'
import { api } from '@/core/apiClient'
import POIInfoForm from '@/components/POIInfoForm.vue'
import RefWorkflow from '@/components/RefWorkflow.vue'
import UploadsPanel from '@/components/UploadsPanel.vue'
import NPCPanel from '@/components/NPCPanel.vue'
import AddPoiDialog from '@/components/AddPoiDialog.vue'

const store = useGeneratorStore()
const currentPoi = computed(() => store.currentPoi)
const showAddDialog = ref(false)
const editingPoi = ref(null)
const dragOver = ref(false)
const poiInfoFormRef = ref(null)  // 弹窗关闭前调 saveInfo() 自动保存

// 卡片场景图缓存破坏
const cardCacheBust = ref(Date.now())
const cardBrokenImgs = ref(new Set())  // 加载失败的 poi_id 集合(用 emoji 占位)

function primaryImageExists(poiId) {
  if (cardBrokenImgs.value.has(poiId)) return false
  return true
}

function onCardImgError(poiId) {
  cardBrokenImgs.value.add(poiId)
}

// 已发布的 POI 列表（从 SQLite 拉取）
const publishedPois = ref([])

function isPublished(poiId) {
  return publishedPois.value.some(p => p.id === poiId)
}

async function loadPublished() {
  try {
    const resp = await fetch('http://127.0.0.1:8000/api/v2/pois?city=munich')
    const data = await resp.json()
    if (data.success) {
      publishedPois.value = data.pois.map(p => ({
        id: p.id,
        name_zh: p.name || p.id,
        type: p.t || '?',
        isNew: false,
      }))
    }
  } catch(e) { /* backend off */ }
}

function openEditor(poiId) {
  store.selectPoi(poiId)
  const poi = store.knownPois.find(p => p.id === poiId)
  editingPoi.value = poi
}

async function closeEditor() {
  // 弹窗任何方式关闭前,自动保存 info tab 里的基础信息(如果用户在那个 tab)
  if (poiInfoFormRef.value && typeof poiInfoFormRef.value.saveInfo === 'function') {
    try {
      await poiInfoFormRef.value.saveInfo()
    } catch (e) {
      console.warn('[closeEditor] 自动保存失败:', e)
    }
  }
  editingPoi.value = null
}

// 创建新 POI 后(从 AddPoiDialog emit): 自动打开编辑器 + 触发 AI 流程
async function onPoiCreated(poi) {
  // 编辑器已经 store.selectPoi(poi.id),activeTab='info'
  editingPoi.value = poi
  // 等 POIInfoForm mount 完
  await nextTick()
  await nextTick()
  // 触发自动 AI 填第一页(场景介绍 + 周边 OSM)
  if (poiInfoFormRef.value && typeof poiInfoFormRef.value.aiGenerateIntro === 'function') {
    store.log('🤖 自动触发 AI 场景介绍生成...')
    poiInfoFormRef.value.aiGenerateIntro().catch(e => {
      store.error = 'AI 自动填充失败: ' + e.message
    })
  }
}

// AI 填充完成事件 (POIInfoForm emit)
function onAutoFillDone() {
  store.log('✅ AI 自动填充完成,可以查看第一页')
}

// ESC 键关闭弹窗
function onGlobalKeydown(e) {
  if (e.key === 'Escape') {
    if (showAddDialog.value) {
      showAddDialog.value = false
    } else if (editingPoi.value) {
      closeEditor()
    }
  }
}

function onDragStart(e, poi) {
  e.dataTransfer.setData('poiId', poi.id)
  e.dataTransfer.effectAllowed = 'move'
}

async function onDrop(e) {
  dragOver.value = false
  const poiId = e.dataTransfer.getData('poiId')
  if (!poiId) return
  const poi = store.knownPois.find(p => p.id === poiId)
  if (!poi) return
  try {
    await fetch('http://127.0.0.1:8000/api/save/package', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        files: [{
          relative_path: 'poi_info.draft.json',
          data: {
            id: poi.id,
            name_de: poi.name_de,
            name_zh: poi.name_zh,
            type: poi.type,
            lat: poi.lat,
            lng: poi.lng,
            icon: poi.icon,
            description: poi.description || '',
            acts: poi.acts || [],
          }
        }],
        poi_id: poi.id,
        city: 'munich',
      }),
    })
    await loadPublished()
    store.log(`📤 已发布 ${poi.name_zh}`)
    store.markGenerated('info')
  } catch(e) {
    store.error = '发布失败: ' + e.message
  }
}

async function publishCurrent() {
  if (!editingPoi.value) return
  const poi = editingPoi.value
  try {
    await fetch('http://127.0.0.1:8000/api/save/package', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        files: [{
          relative_path: 'poi_info.draft.json',
          data: {
            id: poi.id,
            name_de: poi.name_de,
            name_zh: poi.name_zh,
            type: poi.type,
            lat: poi.lat,
            lng: poi.lng,
            icon: poi.icon,
            description: poi.description || '',
            acts: poi.acts || [],
          }
        }],
        poi_id: poi.id,
        city: 'munich',
      }),
    })
    await loadPublished()
    store.log(`📤 已发布 ${poi.name_zh}`)
    store.markGenerated('info')
  } catch(e) {
    store.error = '发布失败: ' + e.message
  }
}

onMounted(() => {
  store.checkBackend()
  loadPublished()
  window.addEventListener('keydown', onGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<style scoped>
</style>