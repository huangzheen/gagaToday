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

    <!-- 卡片网格 + 编辑面板 -->
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
          :class="{ selected: store.currentPoiId === poi.id }"
          @click="selectAndGenerate(poi.id)"
        >
          <span class="poi-card-icon">{{ poi.icon }}</span>
          <span class="poi-card-name">{{ poi.name_zh }}</span>
          <span class="poi-card-type">{{ poi.type }}</span>
          <span class="poi-card-de">{{ poi.name_de }}</span>
          <div class="poi-card-stats">
            <span class="stat" :class="poi.lat ? 'ok' : 'missing'">📍</span>
            <span class="stat missing">📄</span>
            <span class="stat missing">🖼️</span>
            <span class="stat missing">👤</span>
          </div>
        </div>
        <!-- 新增卡片 -->
        <div class="poi-card add-card" @click="showAddDialog = true">
          <span class="add-icon">➕</span>
          <span class="add-text">新建 POI</span>
        </div>
      </div>
    </div>

    <!-- 右侧编辑面板 -->
    <div class="editor-panel panel" v-if="store.currentPoiId">
      <div class="editor-header">
        <span class="editor-poi-name">{{ store.currentPoi?.icon }} {{ store.currentPoi?.name_zh }}</span>
        <div class="editor-actions">
          <button class="btn primary" @click="generateAll" :disabled="store.isGenerating" style="font-size:9px;padding:2px 6px">
            {{ store.isGenerating ? '⏳' : '🤖 一键生成' }}
          </button>
          <button class="btn success" @click="saveAll" :disabled="Object.keys(store.generated).length === 0" style="font-size:9px;padding:2px 6px">
            💾 导出
          </button>
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

    <!-- 未选中时的占位提示 -->
    <div class="editor-panel panel empty-editor" v-else>
      <div class="empty-hint">
        <p style="font-size:32px;margin-bottom:8px">📇</p>
        <p>点击左侧卡片<br/>开始编辑 POI</p>
      </div>
    </div>

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

function selectAndGenerate(poiId) {
  store.selectPoi(poiId)
}

onMounted(() => {
  store.checkBackend()
})

async function generateAll() {
  store.isGenerating = true
  store.error = null
  store.log('🚀 开始批量生成...')

  const poi = store.currentPoi
  try {
    // Step 1: 生成基础信息
    store.log('📝 生成基础信息...')
    await generateInfo(poi)
    store.markGenerated('info')

    // Step 2: 生成图片
    store.log('🖼️ 生成图片...')
    await generateImages(poi)
    store.markGenerated('images')

    // Step 3: 生成 NPC
    store.log('👤 生成 NPC...')
    await generateNPC(poi)
    store.markGenerated('npc')

    // Step 4: 生成对话
    store.log('💬 生成对话...')
    await generateDialogue(poi)
    store.markGenerated('dialogue')

    // Step 5: 生成知识卡
    store.log('📚 生成知识卡...')
    await generateKnowledge(poi)
    store.markGenerated('knowledge')

    // Step 6: 生成剧情
    store.log('🎯 生成剧情任务...')
    await generateQuests(poi)
    store.markGenerated('quests')

    // Step 7: 生成打卡
    store.log('📍 生成打卡目标...')
    await generateCheckin(poi)
    store.markGenerated('checkin')

    store.log('✅ 全部生成完成！')
    store.selectTab('preview')
  } catch (e) {
    store.error = e.message
    store.log(`❌ 错误: ${e.message}`)
  } finally {
    store.isGenerating = false
  }
}

async function saveAll() {
  store.log('💾 导出数据到 drafts...')
  const files = []
  if (store.poiData.info) files.push({ relative_path: 'poi_info.draft.json', data: store.poiData.info })
  if (store.poiData.npc_profiles) files.push({ relative_path: 'npc_profiles.draft.json', data: store.poiData.npc_profiles })
  if (store.poiData.dialogues) files.push({ relative_path: 'dialogues.draft.json', data: store.poiData.dialogues })
  if (store.poiData.dialogue_hooks) files.push({ relative_path: 'npc_dialogue_hooks.draft.json', data: store.poiData.dialogue_hooks })
  if (store.poiData.knowledge_cards) files.push({ relative_path: 'knowledge_cards.draft.json', data: store.poiData.knowledge_cards })
  if (store.poiData.quests) files.push({ relative_path: 'quests.draft.json', data: store.poiData.quests })
  if (store.poiData.checkin_targets) files.push({ relative_path: 'checkin_targets.draft.json', data: store.poiData.checkin_targets })

  if (files.length === 0) {
    store.log('⚠️ 没有可导出的数据，请先生成内容')
    return
  }

  try {
    const res = await api.savePackage(files, store.currentPoiId, 'munich')
    const saved = res.saved_files || []
    store.log(`✅ 导出完成: ${saved.length} 个文件已写入 drafts`)
    for (const p of saved) store.log(`   📄 ${p}`)
  } catch (e) {
    store.error = e.message
    store.log(`❌ 导出失败: ${e.message}`)
  }
}

// ── 各模块生成函数（直接调用后端 LLM）──

async function generateInfo(poi) {
  const data = {
    id: `explore_munich_${poi.id}`,
    name_de: poi.name_de,
    name_zh: poi.name_zh,
    name_en: poi.name_de,
    type: poi.type,
    city: 'munich',
    coordinates: { lat: poi.lat, lng: poi.lng, source: 'manual' },
    visit_duration_minutes: 30,
    student_fit: 'high',
    review_status: 'draft',
  }
  store.setPoiData('info', data)
}

async function generateImages(poi) {
  store.log('🖼️ 图片生成需手动在「图片」标签操作（调用 matrix MCP）')
}

async function generateNPC(poi) {
  const prompt = `为 gagaToday 德国留学模拟 RPG 生成 NPC 档案。POI: ${poi.name_de} (${poi.name_zh}), 类型: ${poi.type}。生成 1-2 个 NPC，JSON 数组格式，每个包含 id/name_de/name_zh/role/age_band/personality/background_zh/language_profile/review_status:"draft"。只返回 JSON 数组。`
  try {
    const res = await api.generateJson(prompt)
    const npcs = Array.isArray(res.data) ? res.data : [res.data]
    store.setPoiData('npc_profiles', npcs)
    store.log(`✅ 已生成 ${npcs.length} 个 NPC`)
  } catch (e) { store.log(`⚠️ NPC 生成失败: ${e.message}`) }
}

async function generateDialogue(poi) {
  const prompt = `为 gagaToday 游戏生成 3 个对话场景。POI: ${poi.name_de}。每场景 4-6 轮对话，含 2 个分支选项，中/德/英三语。JSON 数组，每个含 hook_id/label/turns/[{"turn_id","speaker","de","zh","en"}]。只返回 JSON 数组。`
  try {
    const res = await api.generateJson(prompt)
    const dialogues = Array.isArray(res.data) ? res.data : [res.data]
    store.setPoiData('dialogues', dialogues)
    store.log(`✅ 已生成 ${dialogues.length} 个对话场景`)
  } catch (e) { store.log(`⚠️ 对话生成失败: ${e.message}`) }
}

async function generateKnowledge(poi) {
  const prompt = `为 gagaToday 生成 5 张德国文化历史知识卡。POI: ${poi.name_de} (${poi.name_zh})。类别涵盖 Geschichte/Architektur/Legende/Kultur。JSON 数组，每张含 id/category/title_zh/body_zh(80-150字)/gameplay_use/review_status:"draft"。只返回 JSON 数组。`
  try {
    const res = await api.generateJson(prompt)
    const cards = Array.isArray(res.data) ? res.data : [res.data]
    store.setPoiData('knowledge_cards', cards)
    store.log(`✅ 已生成 ${cards.length} 张知识卡`)
  } catch (e) { store.log(`⚠️ 知识卡生成失败: ${e.message}`) }
}

async function generateQuests(poi) {
  const prompt = `为 gagaToday 游戏生成 4 个剧情任务。POI: ${poi.name_de}。类型含 exploration/dialogue/cultural/treasure_hunt。JSON 数组，每任务含 id/type/title_zh/description_zh/steps/rewards/review_status:"draft"。只返回 JSON 数组。`
  try {
    const res = await api.generateJson(prompt)
    const quests = Array.isArray(res.data) ? res.data : [res.data]
    store.setPoiData('quests', quests)
    store.log(`✅ 已生成 ${quests.length} 个任务`)
  } catch (e) { store.log(`⚠️ 任务生成失败: ${e.message}`) }
}

async function generateCheckin(poi) {
  const prompt = `为 gagaToday 生成 5 个打卡目标。POI: ${poi.name_de}。类型含 location/physical/photo/discover/scheduled。JSON 数组，每目标含 id/name_zh/type/trigger/reward/review_status:"draft"。只返回 JSON 数组。`
  try {
    const res = await api.generateJson(prompt)
    const checkins = Array.isArray(res.data) ? res.data : [res.data]
    store.setPoiData('checkin_targets', checkins)
    store.log(`✅ 已生成 ${checkins.length} 个打卡目标`)
  } catch (e) { store.log(`⚠️ 打卡生成失败: ${e.message}`) }
}
</script>
