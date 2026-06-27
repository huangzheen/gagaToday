<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">📍 POI 基础信息</h3>

    <!-- ── 加载/错误状态 ── -->
    <div v-if="loading" style="color:#6a8aaa;font-size:10px;padding:20px;text-align:center">
      🔍 正在从地图提取 OSM 数据...
    </div>
    <div v-else-if="error" style="color:var(--danger);font-size:10px;padding:10px;background:rgba(200,50,50,.15);border:1px solid rgba(200,50,50,.3);margin-bottom:10px">
      ⚠️ {{ error }}
    </div>

    <!-- ── OSM 主 POI 摘要 ── -->
    <div v-if="osm?.primary_poi" class="osm-bar">
      <span class="osm-icon">📍</span>
      <span class="osm-name">{{ osm.primary_poi.name_de }}</span>
      <span class="osm-meta">{{ osm.primary_poi.class }}<span v-if="osm.primary_poi.subclass"> / {{ osm.primary_poi.subclass }}</span></span>
      <span class="osm-dist">{{ osm.primary_poi.distance_m }}m</span>
    </div>

    <!-- ── 游戏内容编辑区 ── -->
    <div style="margin-top:12px">
      <div class="field">
        <label>POI ID</label>
        <input v-model="poiId" disabled />
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="field">
          <label>德语名</label>
          <input v-model="nameDe" :placeholder="osm?.primary_poi?.name_de || ''" />
        </div>
        <div class="field">
          <label>中文名</label>
          <input v-model="nameZh" :placeholder="osm?.primary_poi?.name_zh || ''" />
        </div>
      </div>

      <div class="field">
        <label>类型</label>
        <select v-model="type">
          <option value="church">教堂</option>
          <option value="square">广场</option>
          <option value="museum">博物馆</option>
          <option value="park">公园</option>
          <option value="market">市场</option>
          <option value="castle">城堡/宫殿</option>
          <option value="stadium">体育场</option>
          <option value="school">学校</option>
          <option value="shop">商店</option>
          <option value="library">图书馆</option>
          <option value="home">住所</option>
        </select>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="field">
          <label>纬度</label>
          <input v-model="lat" type="number" step="0.0001" />
        </div>
        <div class="field">
          <label>经度</label>
          <input v-model="lng" type="number" step="0.0001" />
        </div>
      </div>

      <div class="field">
        <label>
          场景介绍
          <button
            type="button"
            class="btn-ai"
            @click="aiGenerateIntro"
            :disabled="aiGenerating"
          >{{ aiGenerating ? '⏳ 生成中...' : '✨ AI 生成' }}</button>
        </label>

        <!-- 语言 tab 切换 -->
        <div class="lang-tabs">
          <button
            type="button"
            :class="['lang-tab', { active: introLang === 'de' }]"
            @click="introLang = 'de'"
          >🇩🇪 Deutsch</button>
          <button
            type="button"
            :class="['lang-tab', { active: introLang === 'zh' }]"
            @click="introLang = 'zh'"
          >🇨🇳 中文</button>
          <button
            type="button"
            :class="['lang-tab', { active: introLang === 'en' }]"
            @click="introLang = 'en'"
          >🇬🇧 English</button>
        </div>

        <!-- 当前语言的 textarea -->
        <textarea
          v-model="intro[introLang]"
          rows="6"
          :placeholder="introPlaceholder[introLang]"
        />

        <!-- 字数统计 + 状态 + 音频 -->
        <div class="intro-meta">
          <span>{{ introWordCount }} 词</span>
          <span class="intro-meta-sep">·</span>
          <span class="intro-meta-hint">
            {{ introLang === 'de' ? '维基百科原文' : '维基百科原文 / AI 忠实翻译' }}
          </span>
          <span v-if="aiGenerating" class="intro-meta-spin">⟳ 正在生成 {{ aiStage }}</span>
          <span v-if="audioUrls[introLang]" class="audio-badge" :title="`音频约 ${audioUrls[introLang].duration_estimate}s`">
            🔊 音频就绪
          </span>
        </div>
      </div>

      <button class="btn primary" @click="saveInfo" :disabled="saving">
        {{ saving ? '⏳ 保存中...' : '💾 保存基础信息' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'

const store = useGeneratorStore()

const poiId = ref('')
const nameDe = ref('')
const nameZh = ref('')
const type = ref('church')
const lat = ref(0)
const lng = ref(0)
const gameRole = ref('')
// ── 场景介绍:三语言,以德语为原文 ──
const intro = ref({ de: '', zh: '', en: '' })
const introLang = ref('zh')   // 默认显示中文
const aiGenerating = ref(false)
const aiStage = ref('')        // '生成德语原文...' / '翻译中英...'
const saving = ref(false)
const audioUrls = ref({})       // TTS 预生成的 {de: {url, duration_estimate}, ...}

const introPlaceholder = {
  de: '场景介绍(德语,维基百科原文)…',
  zh: '场景介绍(中文,维基百科原文 / AI 翻译)…',
  en: 'Scene introduction (English, Wikipedia original)…',
}
// 字数统计:中英文按"非空白 token 数",德语按"空格分词数"
// 简单起见统一按空格分词,中文 char-only 显示 word count 偏低但够用
const introWordCount = computed(() => {
  const text = intro.value[introLang.value] || ''
  if (!text.trim()) return 0
  return text.trim().split(/\s+/).filter(Boolean).length
})

// OSM 数据
const osm = ref(null)
const loading = ref(false)
const error = ref(null)

async function fetchOsmData(latVal, lngVal) {
  if (!latVal || !lngVal) return
  loading.value = true
  error.value = null
  try {
    const resp = await fetch(`/api/osm/extract?lat=${latVal}&lng=${lngVal}`)
    const data = await resp.json()
    if (data.success) {
      osm.value = data
      store.setOsmData(data)  // 共享给其他 tab
      // 自动填入 OSM 数据到游戏字段
      if (!nameDe.value && data.primary_poi?.name_de) nameDe.value = data.primary_poi.name_de
      if (!nameZh.value && data.primary_poi?.name_zh) nameZh.value = data.primary_poi.name_zh
    } else {
      error.value = '地图数据提取失败'
    }
  } catch (e) {
    error.value = `OSM 提取器不可用: ${e.message}`
    // 如果 PMTiles 或后端未运行，仍允许手动编辑
  } finally {
    loading.value = false
  }
}

// ── 加载已保存的 draft(覆盖 KNOWN_POIS 默认值) ──
async function loadDraftIfExists(poiId) {
  try {
    const resp = await api.loadJson('poi_info.draft.json', poiId, 'munich', true)
    if (resp.success && resp.data) {
      const d = resp.data
      if (d.name_de) nameDe.value = d.name_de
      if (d.name_zh) nameZh.value = d.name_zh
      if (d.type) type.value = d.type
      if (d.coordinates) {
        if (d.coordinates.lat != null) lat.value = d.coordinates.lat
        if (d.coordinates.lng != null) lng.value = d.coordinates.lng
      }
      if (d.intro_de || d.intro_zh || d.intro_en) {
        intro.value = {
          de: d.intro_de || '',
          zh: d.intro_zh || '',
          en: d.intro_en || '',
        }
      }
      if (d.game_role) gameRole.value = d.game_role
      if (d.audio && typeof d.audio === 'object') audioUrls.value = d.audio
      if (d.osm_data) {
        osm.value = { primary_poi: d.osm_data, building: {}, transport: [], roads: [], all_layers: d.osm_data.all_layers }
      }
      return true
    }
  } catch (e) {
    // 404 = 没有 draft,正常情况
    if (e?.status !== 404) console.warn(`[loadDraft] ${poiId} 失败:`, e?.message || e)
  }
  return false
}

watch(() => store.currentPoiId, async (id) => {
  const poi = store.currentPoi
  if (!poi) return
  poiId.value = poi.id
  // 先用 KNOWN_POIS 默认值初始化
  nameDe.value = poi.name_de
  nameZh.value = poi.name_zh
  type.value = poi.type
  const newLat = poi.lat || 0
  const newLng = poi.lng || 0
  lat.value = newLat
  lng.value = newLng
  gameRole.value = ''
  intro.value = { de: '', zh: '', en: '' }
  introLang.value = 'zh'
  osm.value = null
  store.setOsmData(null)
  // 异步加载已保存的 draft,如果有就覆盖默认值
  await loadDraftIfExists(poi.id)
  if (newLat && newLng) {
    fetchOsmData(newLat, newLng)
  }
}, { immediate: true })


// ── AI 生成场景介绍 ──
// 流程(走 /api/wiki/intro 后端编排):
//   1) Wikipedia DE 拿摘要(主要来源)
//   2) 查 Wikidata QID → 拿 ZH/EN sitelink → 各拉摘要
//   3) 缺失语言 → LLM 翻译 DE 补齐
//   4) DE Wikipedia 无 → Brave Search 搜德语内容
//   5) 每种语言 LLM 改写成 ~100 词 RPG 风
async function aiGenerateIntro() {
  if (!poiId.value || !nameDe.value) {
    store.error = '请先填写德语名称'
    return
  }
  aiGenerating.value = true
  store.error = null
  try {
    aiStage.value = '查 Wikipedia + Wikidata...'
    store.log(`✨ AI 生成场景介绍 (${store.textModel})...`)
    const resp = await api.fetchWikiIntro(nameDe.value, nameZh.value || null)
    if (!resp.success) throw new Error(resp.detail || 'wiki/intro 失败')

    // 填回三语言 textarea
    intro.value.de = resp.de || ''
    intro.value.zh = resp.zh || ''
    intro.value.en = resp.en || ''

    // 来源摘要显示在日志
    const rawSources = []
    if (resp.sources?.de_raw === 'wikipedia') rawSources.push('🇩🇪 维基')
    else if (resp.sources?.de_raw === 'brave_search') rawSources.push('🇩🇪 Brave')
    if (resp.sources?.zh_raw === 'wikipedia') rawSources.push('🇨🇳 维基')
    if (resp.sources?.en_raw === 'wikipedia') rawSources.push('🇬🇧 维基')
    const generated = []
    if (resp.sources?.de === 'llm_rewrite') generated.push('🇩🇪 改写')
    if (resp.sources?.zh === 'llm_translate') generated.push('🇨🇳 翻译')
    if (resp.sources?.zh === 'llm_rewrite') generated.push('🇨🇳 改写')
    if (resp.sources?.en === 'llm_translate') generated.push('🇬🇧 翻译')
    if (resp.sources?.en === 'llm_rewrite') generated.push('🇬🇧 改写')
    const qid = resp.wikidata_qid ? ` · QID=${resp.wikidata_qid}` : ''
    store.log(`✅ 来源: ${rawSources.join(' + ') || '无'}; LLM: ${generated.join(' / ')}${qid}`)
    if (resp.urls?.de) store.log(`  DE: ${resp.urls.de}`)

    // 切到中文 tab 让用户立刻看到结果
    introLang.value = 'zh'

    // 音频就绪状态(后端在生成三语维基百科内容时同步跑 TTS 预生成 MP3)
    if (resp.audio && Object.keys(resp.audio).length > 0) {
      const langs = Object.keys(resp.audio).map(l => l.toUpperCase()).join(' ')
      store.log(`🔊 TTS 已就绪: ${langs} · 时长约 ${Object.values(resp.audio)[0].duration_estimate}s`)
      audioUrls.value = resp.audio  // 暂存,saveInfo 时落盘
    } else {
      audioUrls.value = {}
    }

    aiStage.value = '完成 ✓'
    setTimeout(() => { aiStage.value = '' }, 1500)
  } catch (e) {
    store.error = e.message
    store.log(`❌ AI 场景介绍失败: ${e.message}`)
    aiStage.value = `失败: ${e.message}`
    setTimeout(() => { aiStage.value = '' }, 3000)
  } finally {
    aiGenerating.value = false
  }
}

async function saveInfo() {
  saving.value = true
  store.error = null
  const data = {
    id: `explore_munich_${poiId.value}`,
    name_de: nameDe.value,
    name_zh: nameZh.value,
    name_en: nameDe.value,
    type: type.value,
    city: 'munich',
    coordinates: { lat: lat.value, lng: lng.value, source: 'manual' },
    visit_duration_minutes: 30,
    student_fit: 'high',
    game_role: gameRole.value,
    // 新版:三语言场景介绍
    intro_de: intro.value.de,
    intro_zh: intro.value.zh,
    intro_en: intro.value.en,
    // TTS 预生成音频(地图页 🔊 播放按钮用)
    audio: Object.keys(audioUrls.value).length > 0 ? audioUrls.value : null,
    osm_data: osm.value ? {
      name_de: osm.value.primary_poi?.name_de,
      name_zh: osm.value.primary_poi?.name_zh,
      class: osm.value.primary_poi?.class,
      subclass: osm.value.primary_poi?.subclass,
      rank: osm.value.primary_poi?.rank,
      building_height: osm.value.building?.render_height,
      building_colour: osm.value.building?.colour,
      transport: osm.value.transport?.slice(0, 3).map(t => t.name),
      roads: osm.value.roads?.slice(0, 3).map(r => r.name),
      all_layers: osm.value.all_layers,
    } : null,
    review_status: 'draft',
  }

  try {
    await api.saveJson(data, 'poi_info.draft.json', poiId.value)
    store.setPoiData('info', data)
    store.log(`✅ 已保存 ${poiId.value} 基础信息`)
    store.markGenerated('info')
  } catch (e) {
    store.error = e.message
  } finally {
    saving.value = false
  }
}

// 暴露给父组件(App.vue)在弹窗关闭前调用
defineExpose({ saveInfo })
</script>

<style scoped>
.osm-panel {
  background: rgba(0,0,0,.25);
  border: 1px solid var(--navy3);
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 8px;
}
.osm-header {
  color: var(--gold);
  font-size: 9px;
  letter-spacing: 1px;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--navy3);
}
.osm-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}
.osm-card {
  background: rgba(0,0,0,.2);
  border: 1px solid var(--navy2);
  border-radius: 3px;
  padding: 8px;
}
.osm-card-title {
  color: var(--gold2);
  font-size: 8px;
  letter-spacing: 1px;
  margin-bottom: 4px;
  padding-bottom: 2px;
  border-bottom: 1px solid var(--navy2);
}
.osm-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 0;
  font-size: 9px;
}
.osm-label {
  color: #6a8aaa;
  font-size: 8px;
}
.osm-val {
  color: #aab8bf;
  font-family: monospace;
}
.osm-section {
  margin-bottom: 8px;
}
.osm-section-title {
  color: var(--gold2);
  font-size: 8px;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.osm-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.osm-badge {
  background: rgba(0,0,0,.2);
  border: 1px solid var(--navy2);
  padding: 2px 6px;
  font-size: 8px;
  color: #aab8bf;
  border-radius: 2px;
}
.osm-nearby-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 4px;
  font-size: 8px;
  color: #aab8bf;
  background: rgba(0,0,0,.15);
  border-radius: 2px;
}

/* ── 场景介绍 (三语言 tab + AI 生成) ── */
.field label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.btn-ai {
  background: var(--gold);
  color: #000;
  border: 1px solid var(--gold);
  font-size: 9px;
  padding: 3px 10px;
  cursor: pointer;
  font-family: inherit;
  font-weight: bold;
  letter-spacing: 0.5px;
}
.btn-ai:hover:not(:disabled) {
  background: #ffd86b;
  border-color: #ffd86b;
}
.btn-ai:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.lang-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--navy3);
}
.lang-tab {
  flex: 1;
  background: transparent;
  border: 1px solid var(--navy2);
  border-bottom: none;
  color: var(--text-dim);
  font-size: 10px;
  padding: 5px 4px;
  cursor: pointer;
  font-family: inherit;
  transition: all .15s;
  border-radius: 2px 2px 0 0;
  margin-right: 2px;
}
.lang-tab:last-child {
  margin-right: 0;
}
.lang-tab:hover {
  color: var(--gold2);
  border-color: var(--navy3);
}
.lang-tab.active {
  background: var(--gold);
  color: #000;
  border-color: var(--gold);
  font-weight: bold;
}
.intro-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 9px;
  color: var(--text-dim);
  margin-top: 4px;
  font-family: monospace;
}
.intro-meta .over-limit {
  color: var(--danger);
  font-weight: bold;
}
.intro-meta-sep {
  opacity: 0.5;
}
.intro-meta-hint {
  flex: 1;
  font-family: inherit;
  font-style: italic;
}
.intro-meta-spin {
  color: var(--gold);
  animation: blink 1s infinite;
}
.audio-badge {
  background: rgba(232, 184, 92, 0.15);
  border: 1px solid var(--gold);
  color: var(--gold2);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 9px;
}
@keyframes blink {
  50% { opacity: 0.4; }
}
</style>
