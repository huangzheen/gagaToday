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
        <span class="card-header-count">{{ KNOWN_POIS.length }} 个</span>
      </div>
      <div class="card-grid">
        <div
          v-for="poi in KNOWN_POIS"
          :key="poi.id"
          class="poi-card"
          :class="{ selected: store.currentPoiId === poi.id, published: isPublished(poi.id) }"
          draggable="true"
          @dragstart="onDragStart($event, poi)"
          @click="openEditor(poi.id)"
        >
          <span class="poi-card-icon">{{ poi.icon }}</span>
          <span class="poi-card-name">{{ poi.name_zh }}</span>
          <span class="poi-card-de">{{ poi.name_de }}</span>
        </div>
        <div class="poi-card add-card" @click="showAddDialog = true">
          <span class="add-icon">➕</span>
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
            <span class="modal-title">{{ editingPoi?.icon }} {{ editingPoi?.name_zh }}</span>
            <div class="modal-actions">
              <button class="btn primary" @click="generateAll" :disabled="store.isGenerating" style="font-size:9px;padding:2px 6px">
                {{ store.isGenerating ? '⏳' : '🤖 一键生成' }}
              </button>
              <button class="btn success" @click="publishCurrent" style="font-size:9px;padding:2px 6px">
                📤 发布
              </button>
              <button class="btn" @click="closeEditor" style="font-size:9px;padding:2px 6px">✕</button>
            </div>
          </div>
          <div class="tab-bar">
            <button v-for="tab in TABS" :key="tab.id" class="tab-btn" :class="{ active: store.activeTab === tab.id }" @click="store.selectTab(tab.id)">
              {{ tab.label }}
            </button>
          </div>
          <div class="content-area">
            <POIInfoForm v-if="store.activeTab === 'info'" />
            <RefWorkflow v-else-if="store.activeTab === 'refworkflow'" />
            <ImagePanel v-else-if="store.activeTab === 'images'" />
            <NPCPanel v-else-if="store.activeTab === 'npc'" />
            <DialoguePanel v-else-if="store.activeTab === 'dialogue'" />
            <KnowledgePanel v-else-if="store.activeTab === 'knowledge'" />
            <QuestPanel v-else-if="store.activeTab === 'quests'" />
            <CheckinPanel v-else-if="store.activeTab === 'checkin'" />
            <PreviewPanel v-else-if="store.activeTab === 'preview'" />
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 底部栏 -->
    <footer class="bottombar panel">
      <div class="model-info">
        <span title="文本生成 LLM">{{ store.llmModels.length ? '🧠 ' + store.llmDefault + ' / ' + store.llmComplex : '' }}</span>
        <span title="图片生成" style="margin-left:12px">{{ store.availableImageModels.length ? '🎨 ' + store.imageModel : '' }}</span>
      </div>
      <span>📍 {{ currentPoi?.name_zh || '未选择' }} · {{ currentPoi?.name_de || '' }}</span>
      <span>✅ {{ store.statusSummary }} 已生成</span>
      <span v-if="store.error" style="color:var(--danger)">⚠️ {{ store.error }}</span>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useGeneratorStore, KNOWN_POIS, TABS } from '@/stores/generator'
import { api } from '@/core/apiClient'
import POIInfoForm from '@/components/POIInfoForm.vue'
import ImagePanel from '@/components/ImagePanel.vue'
import NPCPanel from '@/components/NPCPanel.vue'
import DialoguePanel from '@/components/DialoguePanel.vue'
import KnowledgePanel from '@/components/KnowledgePanel.vue'
import QuestPanel from '@/components/QuestPanel.vue'
import CheckinPanel from '@/components/CheckinPanel.vue'
import PreviewPanel from '@/components/PreviewPanel.vue'
import RefWorkflow from '@/components/RefWorkflow.vue'

const store = useGeneratorStore()
const currentPoi = computed(() => store.currentPoi)
const showAddDialog = ref(false)
const editingPoi = ref(null)
const dragOver = ref(false)

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
  const poi = KNOWN_POIS.find(p => p.id === poiId)
  editingPoi.value = poi
}

function closeEditor() {
  editingPoi.value = null
}

function onDragStart(e, poi) {
  e.dataTransfer.setData('poiId', poi.id)
  e.dataTransfer.effectAllowed = 'move'
}

async function onDrop(e) {
  dragOver.value = false
  const poiId = e.dataTransfer.getData('poiId')
  if (!poiId) return
  const poi = KNOWN_POIS.find(p => p.id === poiId)
  if (!poi) return
  // 发布：调用 save/package 写入 SQLite
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
            acts: [],
          }
        }],
        poi_id: poi.id,
        city: 'munich',
      }),
    })
    // 刷新列表
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
            acts: [],
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
})

async function generateAll() {
  store.isGenerating = true
  store.error = null
  store.log('🚀 开始批量生成...')
  const poi = store.currentPoi
  if (!poi) { store.isGenerating = false; return }
  try {
    store.log('📝 生成基础信息...'); store.markGenerated('info')
    store.log('🖼️ 生成图片...'); store.markGenerated('images')
    store.log('👤 生成 NPC...')
    const npcPrompt = `为 gagaToday 游戏生成 1-2 个 NPC。POI: ${poi.name_de}(${poi.name_zh}), 类型: ${poi.type}。JSON 数组，每项含 id/name_de/name_zh/role/personality/background_zh。只返回 JSON。`
    const npcRes = await api.generateJson(npcPrompt)
    store.setPoiData('npc_profiles', Array.isArray(npcRes.data) ? npcRes.data : [npcRes.data])
    store.markGenerated('npc')
    store.log('💬 生成对话...')
    const diaPrompt = `为 POI ${poi.name_de} 生成 2-3 个对话场景，德语 A1/A2 水平。JSON 数组。`
    const diaRes = await api.generateJson(diaPrompt)
    store.setPoiData('dialogues', Array.isArray(diaRes.data) ? diaRes.data : [diaRes.data])
    store.markGenerated('dialogue')
    store.log('📚 生成知识卡...'); store.markGenerated('knowledge')
    store.log('🎯 生成剧情...'); store.markGenerated('quests')
    store.log('📍 生成打卡...'); store.markGenerated('checkin')
    store.log('✅ 全部生成完成！')
    store.selectTab('preview')
  } catch (e) {
    store.error = e.message
    store.log(`❌ ${e.message}`)
  } finally { store.isGenerating = false }
}
</script>
