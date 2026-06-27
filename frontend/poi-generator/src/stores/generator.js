/**
 * Pinia Store — 管理 POI 生成器状态
 *
 * 当前职责(2026-06-27 重构):
 * - POI 选择 / Tab 切换
 * - 图像模型选择 (RefWorkflow 用)
 * - 基础信息编辑 (POIInfoForm 用)
 * - 定妆照→变体工作流 (RefWorkflow 用)
 */

import { defineStore } from 'pinia'
import { api } from '@/core/apiClient'

// 已发布的慕尼黑 POI 列表(含坐标和类型)
// key_features: 可选,该 POI 的关键建筑特征(用于场景图 prompt 强化细节)。
//   新加 POI 时,如果不写,prompt 会用通用"按 name_de 自行推断真实特征"指令,模型也会给出合理结果。
// description/acts: 用于地图端 POI 详情卡片(右栏)显示
export const KNOWN_POIS = [
  {
    id: 'frauenkirche',
    name_de: 'Frauenkirche',
    name_zh: '圣母教堂',
    type: 'church',
    lat: 48.1385,
    lng: 11.5737,
    icon: '⛪',
    description: '慕尼黑最著名的地标——圣母教堂。两座绿色铜洋葱顶双塔俯瞰全城,是游戏中新手剧情的起点。',
    acts: ['参观', '登塔观景', '拍照打卡'],
    key_features: 'two tall symmetrical towers with iconic green copper onion domes, pale Bavarian limestone facade, red terracotta tile roof, large Gothic arched windows, central nave body. NOT a generic cathedral, NOT a fantasy castle, NOT a single tower, MUST have both onion domes.',
  },
  {
    id: 'marienplatz',
    name_de: 'Marienplatz',
    name_zh: '玛利亚广场',
    type: 'square',
    lat: 48.1374,
    lng: 11.5755,
    icon: '🏛️',
    description: '慕尼黑市中心广场和换乘枢纽。新市政厅(Neues Rathaus)及其著名的钟琴(Glockenspiel)是必打卡点,玛利亚金柱是城市的精神中心。',
    acts: ['看钟琴表演', '逛市集摊位', '参观新市政厅'],
    key_features: 'the central tall New Town Hall (Neues Rathaus) with its iconic Gothic Revival tower, the famous Glockenspiel carillon balcony with tiny painted wooden figures, the gilded golden Mariensäule column with a radiant Virgin Mary statue on a dark marble Corinthian base. Surrounding: red-roofed Munich townhouses with dormer windows and painted facades (warm cream, ochre, terracotta, ivory). Distant background: Fraunhofer church tower or Frauenkirche onion-dome twin towers visible behind. NOT a generic European plaza.',
  },
]


export const TABS = [
  { id: 'info', label: '基础信息' },
  { id: 'refworkflow', label: '📸 定妆照 → 变体' },
  { id: 'uploads', label: '📤 上传资源' },
  { id: 'npc', label: '🧑 NPC' },
]


export const useGeneratorStore = defineStore('generator', {
  state: () => ({
    // POI 选择
    currentPoiId: 'frauenkirche',
    activeTab: 'info',

    // 全局模型(供整个弹窗使用:App.vue 标题栏下拉)
    imageModel: 'minimax',            // 默认图像模型
    textModel: 'deepseek-v4-flash',   // 默认文本模型(DeepSeek V4 Flash,快+质量好)
    availableImageModels: [],
    availableTextModels: [],

    // 状态跟踪 (POIInfoForm/RefWorkflow mark)
    generated: {},
    poiData: {},

    // 后端状态
    backendConnected: false,

    // OSM 提取的真实数据 (POIInfoForm 写入,RefWorkflow 读)
    osmData: null,

    // 错误 + 日志
    error: null,
    generationLog: [],
  }),

  getters: {
    currentPoi: (state) => KNOWN_POIS.find(p => p.id === state.currentPoiId),
    isComplete: (state) => Object.keys(state.generated).length >= 4,
    statusSummary: (state) => {
      const sections = ['info', 'refworkflow', 'uploads', 'npc']
      const done = sections.filter(s => state.generated[s]).length
      return `${done}/${sections.length}`
    },
  },

  actions: {
    selectPoi(poiId) {
      this.currentPoiId = poiId
      this.activeTab = 'info'
      this.generated = {}
      this.poiData = {}
      this.error = null
      this.generationLog = []
    },

    selectTab(tabId) {
      this.activeTab = tabId
    },

    markGenerated(section) {
      this.generated[section] = true
    },

    setPoiData(section, data) {
      this.poiData[section] = data
    },

    log(msg) {
      const ts = new Date().toLocaleTimeString()
      this.generationLog.push(`[${ts}] ${msg}`)
    },

    async checkBackend() {
      try {
        const res = await fetch('/api/health')
        const data = await res.json()
        this.backendConnected = data.status === 'ok'
        if (this.backendConnected) {
          // 并行拉图像和文本模型列表
          await Promise.all([
            fetch('/api/generate/models').then(r => r.json()).then(m => {
              if (m.success) this.availableImageModels = m.models
            }).catch(() => {}),
            fetch('/api/generate/llm-models').then(r => r.json()).then(m => {
              if (m.success) {
                this.availableTextModels = m.models
                if (m.default && !this.textModel) this.textModel = m.default
                if (m.complex && !this.textModel) this.textModel = m.complex
              }
            }).catch(() => {}),
          ])
        }
      } catch {
        this.backendConnected = false
      }
    },

    setImageModel(modelId) {
      this.imageModel = modelId
    },

    setTextModel(modelId) {
      this.textModel = modelId
    },

    setOsmData(data) {
      this.osmData = data
      this.error = null
    },
  },
})
