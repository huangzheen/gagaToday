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

    // 草稿保存时间(ISO 字符串,用于 UI 显示"已保存 HH:MM:SS")
    lastSavedAt: null,
  }),

  getters: {
    currentPoi: (state) => KNOWN_POIS.find(p => p.id === state.currentPoiId),
    isComplete: (state) => Object.keys(state.generated).length >= 8,
    statusSummary: (state) => {
      const sections = ['info', 'images', 'npc', 'dialogue', 'knowledge', 'quests', 'checkin', 'refworkflow']
      const done = sections.filter(s => state.generated[s]).length
      return `${done}/${sections.length}`
    },
    hasContent: (state) => {
      const d = state.poiData
      return Boolean(
        d.info ||
        d.npc_profiles?.length ||
        d.dialogues?.length ||
        d.dialogue_hooks?.length ||
        d.knowledge_cards?.length ||
        d.quests?.length ||
        d.checkin_targets?.length ||
        d.scene_events?.length
      )
    },
    lastSavedLabel: (state) => {
      if (!state.lastSavedAt) return ''
      const d = new Date(state.lastSavedAt)
      return d.toLocaleTimeString()
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

    /**
     * 把 store.poiData 里的全部生成内容保存到 filesystem drafts 目录 + poi_content 表
     * 不标记为已发布(register_published=False),仅作草稿
     * 返回 { saved_files: [...] } 或抛错
     */
    async saveDraft() {
      const poi = this.currentPoi
      if (!poi) throw new Error('未选择 POI')
      const files = this._buildDraftFiles()
      if (files.length === 0) {
        throw new Error('没有可保存的内容,先点"一键生成"')
      }
      // registerPublished=false:纯草稿,不动 pois.is_published
      const res = await api.savePackage(files, poi.id, 'munich', null, null, false)
      this.lastSavedAt = new Date().toISOString()
      this.log(`💾 已保存草稿 (${files.length} 个文件)`)
      return res
    },

    /**
     * 内部:构建所有 poiData 的文件清单
     * 顺序与 PreviewPanel.exportAll 保持一致
     */
    _buildDraftFiles() {
      const files = []
      const d = this.poiData
      const add = (key, path) => {
        if (d[key]) files.push({ relative_path: path, data: d[key] })
      }
      add('info',              'poi_info.draft.json')
      add('npc_profiles',      'npc_profiles.draft.json')
      add('dialogues',         'dialogues.draft.json')
      add('dialogue_hooks',    'npc_dialogue_hooks.draft.json')
      add('knowledge_cards',   'knowledge_cards.draft.json')
      add('quests',            'quests.draft.json')
      add('checkin_targets',   'checkin_targets.draft.json')
      add('scene_events',      'scene_events.draft.json')
      add('source_records',    'source_records.json')
      return files
    },

    /**
     * 打开弹窗时调用:从 drafts 目录加载已存在的文件到 store
     * 任何 section 加载成功都会 markGenerated
     */
    async loadDraft(poiId, city = 'munich') {
      try {
        const resp = await fetch(`/api/pois/${poiId}?city=${city}`)
        if (!resp.ok) return false
        const data = await resp.json()
        if (!data.success || !data.files) return false
        const fileMap = {
          'poi_info.draft.json':           { key: 'info',            mark: 'info' },
          'npc_profiles.draft.json':       { key: 'npc_profiles',    mark: 'npc' },
          'dialogues.draft.json':          { key: 'dialogues',       mark: 'dialogue' },
          'npc_dialogue_hooks.draft.json': { key: 'dialogue_hooks',  mark: 'dialogue' },
          'knowledge_cards.draft.json':    { key: 'knowledge_cards', mark: 'knowledge' },
          'quests.draft.json':             { key: 'quests',          mark: 'quests' },
          'checkin_targets.draft.json':    { key: 'checkin_targets', mark: 'checkin' },
          'scene_events.draft.json':       { key: 'scene_events',    mark: 'events' },
        }
        let loaded = 0
        for (const [filename, { key, mark }] of Object.entries(fileMap)) {
          if (data.files[filename] && !data.files[filename].error) {
            this.setPoiData(key, data.files[filename])
            this.markGenerated(mark)
            loaded++
          }
        }
        if (loaded > 0) {
          this.log(`📂 已加载 ${poiId} 的草稿 (${loaded} 个文件)`)
          return true
        }
        return false
      } catch {
        return false
      }
    },
  },
})
