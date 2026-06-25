/**
 * Pinia Store — 管理 POI 生成器状态
 */

import { defineStore } from 'pinia'
import { api } from '@/core/apiClient'

// 已发布的慕尼黑 POI 列表（含坐标和类型）
// 2026-06-25 收敛：只保留已发布到地图的 2 个 POI
export const KNOWN_POIS = [
  { id: 'frauenkirche', name_de: 'Frauenkirche', name_zh: '圣母教堂', type: 'church', lat: 48.1385, lng: 11.5737, icon: '⛪' },
  { id: 'marienplatz', name_de: 'Marienplatz', name_zh: '玛利亚广场', type: 'square', lat: 48.1374, lng: 11.5755, icon: '🏛️' },
]


export const TABS = [
  { id: 'info', label: '基础信息' },
  { id: 'refworkflow', label: '📸 定妆照 → 变体' },
  { id: 'images', label: '图片' },
  { id: 'npc', label: 'NPC' },
  { id: 'dialogue', label: '对话' },
  { id: 'knowledge', label: '知识卡' },
  { id: 'quests', label: '剧情' },
  { id: 'checkin', label: '打卡' },
  { id: 'preview', label: '预览' },
]

export const useGeneratorStore = defineStore('generator', {
  state: () => ({
    // POI 选择
    currentPoiId: 'frauenkirche',
    activeTab: 'info',

    // 图片模型
    imageModel: 'minimax',
    availableImageModels: [],

    // LLM 模型
    llmModels: [],
    llmDefault: '',
    llmComplex: '',

    // 生成状态跟踪
    generated: {},  // { "images": true, "npc": false, ... }
    isGenerating: false,
    generationLog: [],

    // 缓存数据
    poiData: {},    // { "npc_profiles": [...], "dialogues": [...], ... }

    // 后端状态
    backendConnected: false,

    // OSM 提取的真实数据(POIInfoForm 写入,其他 tab 共享)
    osmData: null,

    // 错误
    error: null,
  }),

  getters: {
    currentPoi: (state) => KNOWN_POIS.find(p => p.id === state.currentPoiId),
    isComplete: (state) => Object.keys(state.generated).length >= 8,
    statusSummary: (state) => {
      const sections = ['info', 'images', 'npc', 'dialogue', 'knowledge', 'quests', 'checkin', 'refworkflow']
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

    appendPoiData(section, item) {
      if (!Array.isArray(this.poiData[section])) {
        this.poiData[section] = []
      }
      this.poiData[section].push(item)
    },

    clearPoiData() {
      this.poiData = {}
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
          // 拉取可用的图片模型列表
          try {
            const m = await (await fetch('/api/generate/models')).json()
            if (m.success) this.availableImageModels = m.models
          } catch {}
          // 拉取 LLM 模型信息
          try {
            const l = await (await fetch('/api/generate/llm-models')).json()
            if (l.success) {
              this.llmModels = l.models
              this.llmDefault = l.default
              this.llmComplex = l.complex
            }
          } catch {}
        }
      } catch {
        this.backendConnected = false
      }
    },

    setImageModel(modelId) {
      this.imageModel = modelId
    },

    setOsmData(data) {
      this.osmData = data
      this.error = null
    },
  },
})
