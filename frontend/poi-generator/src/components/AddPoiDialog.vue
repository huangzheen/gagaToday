<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="close">
      <div class="modal-panel panel add-poi-dialog">
        <div class="modal-header">
          <span class="modal-title">🏗️ 添加新 POI</span>
          <button class="btn" @click="close" style="padding:4px 10px">✕</button>
        </div>

        <!-- Step 1: 输入地点名 -->
        <div class="content-area">
          <div v-if="step === 'input'">
            <div class="step-hint">
              📝 输入一个地点名称（中文/德语/英语均可）。<br/>
              🤖 LLM 会推断你的意图,并在本地 9G 地图数据中搜索候选 POI。
            </div>

            <div class="field">
              <label>地点名称</label>
              <input
                v-model="userQuery"
                type="text"
                placeholder="例如: 慕尼黑中央火车站 / BMW Welt / 安联球场"
                @keydown.enter="runSearch"
                autofocus
              />
            </div>

            <div class="field" style="margin-top:14px">
              <label>城市上下文 (决定 LLM 用什么语料推断)</label>
              <select v-model="cityContext">
                <option value="munich">🇩🇪 慕尼黑 (Munich)</option>
              </select>
            </div>

            <div v-if="error" class="error-box">
              ⚠️ {{ error }}
            </div>

            <div class="dialog-actions">
              <button class="btn" @click="close">取消</button>
              <button
                class="btn primary"
                :disabled="!userQuery.trim() || loading"
                @click="runSearch"
              >
                {{ loading ? '🔍 LLM 推断中...' : '🔍 搜索' }}
              </button>
            </div>

            <div v-if="loading" class="loading-detail">
              <span class="step-dot active"></span>
              <span>LLM 推断意图 + 生成搜索 query</span>
              <span class="step-sep">→</span>
              <span :class="['step-dot', { active: phase >= 2 }]"></span>
              <span>扫描本地 PMTiles 地图数据</span>
              <span class="step-sep">→</span>
              <span :class="['step-dot', { active: phase >= 3 }]"></span>
              <span>合并候选</span>
            </div>
          </div>

          <!-- Step 2: 候选列表 + 用户确认 -->
          <div v-else-if="step === 'confirm'">
            <div class="intent-box">
              <div class="intent-row">
                <span class="intent-label">你的输入:</span>
                <span class="intent-val">{{ resolveResult.user_query }}</span>
              </div>
              <div class="intent-row" v-if="resolveResult.intent_zh">
                <span class="intent-label">LLM 推断意图:</span>
                <span class="intent-val">{{ resolveResult.intent_zh }}</span>
              </div>
              <div class="intent-row" v-if="resolveResult.intent_de">
                <span class="intent-label">德语表达:</span>
                <span class="intent-val-de">{{ resolveResult.intent_de }}</span>
              </div>
              <div class="intent-row" v-if="resolveResult.rationale">
                <span class="intent-label">决策依据:</span>
                <span class="intent-rationale">{{ resolveResult.rationale }}</span>
              </div>
              <div class="intent-row" v-if="resolveResult.search_queries?.length">
                <span class="intent-label">搜索 query:</span>
                <span class="intent-queries">
                  <code v-for="q in resolveResult.search_queries" :key="q" class="q-chip">{{ q }}</code>
                </span>
              </div>
            </div>

            <div class="candidates-title">
              候选 POI <span class="candidates-count">{{ resolveResult.candidates?.length || 0 }} 个</span>
              <span class="candidates-hint">点击选择一个,然后继续</span>
            </div>

            <div v-if="!resolveResult.candidates?.length" class="no-candidates">
              <div style="font-size:32px;opacity:.3">😕</div>
              <div>未找到候选 POI</div>
              <div class="no-candidates-hint">
                可能该地点不在慕尼黑主城区,或名称差异较大。<br/>
                试试用更短/更通用的名字,或换种语言输入。
              </div>
              <button class="btn" @click="step = 'input'" style="margin-top:12px">↩ 返回修改</button>
            </div>

            <div v-else class="candidate-list">
              <div
                v-for="(cand, i) in resolveResult.candidates"
                :key="i"
                class="candidate-item"
                :class="{
                  selected: selectedIdx === i,
                  recommended: i === 0 && resolveResult.recommended?.display_name === cand.display_name,
                }"
                @click="selectedIdx = i"
              >
                <div class="cand-radio">{{ selectedIdx === i ? '●' : '○' }}</div>
                <div class="cand-main">
                  <div class="cand-name">
                    {{ cand.display_name }}
                    <span v-if="cand.name_zh" class="cand-name-zh">· {{ cand.name_zh }}</span>
                    <span v-if="i === 0 && resolveResult.recommended?.display_name === cand.display_name" class="rec-badge">
                      ★ 推荐
                    </span>
                  </div>
                  <div class="cand-meta">
                    <span class="cand-class" :class="`cls-${cand.class}`">
                      {{ formatClass(cand.class, cand.subclass) }}
                    </span>
                    <span class="cand-coord">{{ formatCoord(cand.lat, cand.lng) }}</span>
                    <span v-if="cand.rank" class="cand-rank">rank {{ cand.rank }}</span>
                  </div>
                  <div v-if="cand.all_names && Object.keys(cand.all_names).length > 1" class="cand-all-names">
                    <span v-for="(name, lang) in cand.all_names" :key="lang" class="alt-name" :title="lang">
                      {{ name }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="error" class="error-box">⚠️ {{ error }}</div>

            <div class="dialog-actions">
              <button class="btn" @click="step = 'input'" :disabled="creating">↩ 返回修改</button>
              <button class="btn primary"
                :disabled="selectedIdx === null || creating"
                @click="confirmCreate"
              >
                {{ creating ? '⏳ 创建中...' : '✅ 创建并打开编辑器' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGeneratorStore } from '@/stores/generator'

const emit = defineEmits(['close', 'created'])

const store = useGeneratorStore()

const step = ref('input')  // 'input' | 'confirm'
const userQuery = ref('')
const cityContext = ref('munich')
const loading = ref(false)
const phase = ref(0)
const error = ref(null)
const resolveResult = ref(null)
const selectedIdx = ref(0)  // 默认选中第一个(LLM 推荐)
const creating = ref(false)

function close() {
  emit('close')
}

function formatClass(cls, sub) {
  const map = {
    'railway/station': '🚉 火车站',
    'railway/subway': '🚇 地铁站',
    'railway/tram_stop': '🚊 电车站',
    'bus/bus_stop': '🚌 公交站',
    'place_of_worship/christian': '⛪ 教堂',
    'place_of_worship': '🛕 宗教场所',
    'place/square': '🏛️ 广场',
    'place/locality': '📍 地名',
    'tourism/museum': '🏛️ 博物馆',
    'tourism/attraction': '🎡 景点',
    'historic': '🏛️ 历史建筑',
    'leisure/park': '🌳 公园',
    'amenity': '🏢 公共设施',
    'shop': '🛒 商店',
    'building': '🏢 建筑',
    'attraction/attraction': '🎡 景点',
    'fuel/charging_station': '⚡ 充电站',
    'lodging/hostel': '🏨 旅馆',
    'restaurant/restaurant': '🍽️ 餐厅',
  }
  const key = `${cls}/${sub}`
  return map[key] || map[cls] || `${cls}/${sub}`
}

function formatCoord(lat, lng) {
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
}

async function runSearch() {
  if (!userQuery.value.trim()) return
  loading.value = true
  phase.value = 1
  error.value = null
  try {
    // Phase 1: LLM 推断
    store.log(`🔍 搜索 "${userQuery.value}"...`)
    // Phase 2: 搜索 (后端会并行调 LLM + PMTiles)
    phase.value = 2
    const resp = await fetch(`/api/osm/agent-resolve?q=${encodeURIComponent(userQuery.value)}`)
    const data = await resp.json()
    if (!data.success) throw new Error(data.error || '搜索失败')

    phase.value = 3
    resolveResult.value = data
    selectedIdx.value = 0  // 默认选第一个
    step.value = 'confirm'
    store.log(`✅ 找到 ${data.candidates?.length || 0} 个候选,推荐: ${data.recommended?.display_name || '(无)'}`)
  } catch (e) {
    error.value = e.message
    store.error = e.message
  } finally {
    loading.value = false
    phase.value = 0
  }
}

async function confirmCreate() {
  if (selectedIdx.value === null || !resolveResult.value) return
  const cand = resolveResult.value.candidates[selectedIdx.value]
  creating.value = true
  error.value = null
  try {
    const finalType = mapOsmClassToPoiType(cand.class, cand.subclass, cand.display_name)
    const poi = await store.createNewPoi({
      name_de: cand.display_name,
      name_zh: cand.name_zh || resolveResult.value.intent_zh || cand.display_name,
      lat: cand.lat,
      lng: cand.lng,
      type: finalType,
      icon: pickIconByType(finalType),
      osm_class: cand.class,
      osm_subclass: cand.subclass,
      osm_rank: cand.rank,
      osm_all_names: cand.all_names,
    })
    store.log(`✅ POI "${poi.name_zh}" 已创建,自动打开编辑器`)
    emit('created', poi)
    close()
  } catch (e) {
    error.value = '创建失败: ' + e.message
  } finally {
    creating.value = false
  }
}

// OSM class/subclass → POI 类型
// 2026-06-28 加 displayName 二次校准:OSM 把有 S-Bahn/U-Bahn 站的广场(如 Marienplatz)
// 也标成 railway/station,所以按名称关键词做最后兜底判断
function mapOsmClassToPoiType(cls, sub, displayName = '') {
  const m = {
    'railway/station': 'train_station',
    'railway/subway': 'subway',
    'railway/tram_stop': 'tram',
    'bus/bus_stop': 'bus_stop',
    'place_of_worship/christian': 'church',
    'place_of_worship': 'church',
    'place/square': 'square',
    'tourism/museum': 'museum',
    'tourism/attraction': 'attraction',
    'leisure/park': 'park',
    'historic': 'historic',
  }
  let type = m[`${cls}/${sub}`] || m[cls] || 'attraction'

  // ── 名称关键词校准(优先级高于 OSM class) ──
  const name = (displayName || '').toLowerCase()
  const has = (kw) => name.includes(kw)
  // 广场/集市关键词(覆盖 railway/station 的 Marienplatz 这种 case)
  if (has('platz') || has('markt') || has('square')) {
    type = has('markt') ? 'market' : 'square'
  }
  // 教堂关键词(覆盖任何误分类)
  else if (has('kirche') || has('dom ') || has('dom,') || has('münster') || has('minster') || has('kathedrale') || has('cathedral') || has('basilika') || has('pfarrkirche')) {
    type = 'church'
  }
  // 城堡/宫殿关键词
  else if (has('schloss') || has('burg ') || has('palais') || has('palace') || has('residenz')) {
    type = 'castle'
  }
  // 博物馆关键词
  else if (has('museum')) {
    type = 'museum'
  }
  // 公园/花园关键词
  else if (has('park') || has('garten') || has('garden')) {
    type = 'park'
  }
  // 火车站关键词(显式包含 bahnhof / hbf 时才明确是火车站,否则保留默认 train_station)
  // 注意:不强制,因为 railway/station 默认就是 train_station
  else if (has('bahnhof') || has(' hbf')) {
    type = 'train_station'
  }
  return type
}

// 按最终 type 取 emoji(2026-06-28 改为跟 type 而非 cls/sub,跟 mapOsmClassToPoiType 对齐)
function pickIconByType(type) {
  const m = {
    church: '⛪',
    square: '🏛️',
    market: '🛒',
    museum: '🏛️',
    attraction: '🎡',
    park: '🌳',
    castle: '🏰',
    stadium: '🏟️',
    school: '🏫',
    shop: '🛍️',
    library: '📚',
    home: '🏠',
    train_station: '🚉',
    subway: '🚇',
    tram: '🚊',
    bus_stop: '🚌',
    historic: '🏛️',
  }
  return m[type] || '📍'
}

// ESC 键关闭
function onKey(e) {
  if (e.key === 'Escape' && !creating.value) close()
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.add-poi-dialog {
  width: 720px;
  max-width: 96vw;
  height: auto;
  max-height: 90vh;
}

.modal-header {
  background: var(--navy2);
}

.content-area {
  padding: 16px;
  overflow-y: auto;
}

.step-hint {
  font-size: 11px;
  color: var(--text-dim);
  line-height: 1.7;
  padding: 10px 12px;
  background: rgba(232, 184, 92, 0.08);
  border: 1px solid rgba(232, 184, 92, 0.2);
  border-radius: 3px;
  margin-bottom: 14px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--navy3);
}

.error-box {
  color: var(--danger);
  font-size: 10px;
  padding: 8px 10px;
  background: rgba(200,90,90,.12);
  border: 1px solid rgba(200,90,90,.3);
  margin: 10px 0;
  border-radius: 2px;
}

.loading-detail {
  margin-top: 12px;
  padding: 10px;
  background: rgba(0,0,0,.15);
  border: 1px solid var(--navy2);
  border-radius: 2px;
  font-size: 9px;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.step-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--navy3);
}
.step-dot.active { background: var(--gold); animation: pulse 1s infinite; }
.step-sep { color: var(--text-dim); opacity: .4; }
@keyframes pulse { 50% { opacity: 0.4; } }

/* ── Intent box ── */
.intent-box {
  background: rgba(0,0,0,.2);
  border: 1px solid var(--navy2);
  padding: 10px 12px;
  margin-bottom: 14px;
  border-radius: 3px;
}
.intent-row {
  display: flex;
  gap: 8px;
  padding: 3px 0;
  font-size: 11px;
  line-height: 1.4;
}
.intent-label {
  color: var(--gold);
  font-size: 9px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  min-width: 80px;
  padding-top: 1px;
}
.intent-val { color: var(--text); }
.intent-val-de { color: var(--gold2); font-style: italic; }
.intent-rationale { color: var(--text-dim); font-style: italic; font-size: 10px; }
.intent-queries { display: inline-flex; flex-wrap: wrap; gap: 4px; }
.q-chip {
  background: var(--navy3);
  color: var(--gold2);
  padding: 1px 6px;
  border-radius: 2px;
  font-size: 10px;
  font-family: inherit;
}

/* ── Candidates ── */
.candidates-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 11px;
  color: var(--gold);
  letter-spacing: 1px;
}
.candidates-count {
  background: var(--navy3);
  color: var(--gold2);
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 9px;
}
.candidates-hint {
  color: var(--text-dim);
  font-size: 9px;
  font-weight: normal;
  letter-spacing: 0;
  margin-left: auto;
}

.candidate-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.candidate-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 8px 10px;
  background: var(--navy2);
  border: 2px solid var(--border);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.1s;
}
.candidate-item:hover {
  border-color: var(--gold);
  background: var(--navy3);
}
.candidate-item.selected {
  border-color: var(--gold2);
  background: rgba(232, 184, 92, 0.08);
}
.candidate-item.recommended {
  border-color: rgba(232, 184, 92, 0.5);
}
.candidate-item.recommended.selected {
  border-color: var(--gold2);
}

.cand-radio {
  font-size: 18px;
  color: var(--gold);
  padding-top: 2px;
}
.cand-main { flex: 1; min-width: 0; }
.cand-name {
  font-size: 12px;
  color: var(--gold2);
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.cand-name-zh { color: var(--text); font-weight: normal; font-size: 11px; }
.rec-badge {
  background: var(--gold);
  color: var(--navy);
  font-size: 8px;
  padding: 1px 5px;
  border-radius: 2px;
  font-weight: bold;
}
.cand-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 9px;
  color: var(--text-dim);
  align-items: center;
}
.cand-class {
  background: var(--navy3);
  padding: 1px 6px;
  border-radius: 2px;
  color: var(--gold2);
}
.cand-coord { font-family: monospace; color: #8ab8d8; }
.cand-rank { opacity: 0.6; }
.cand-all-names {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}
.alt-name {
  background: rgba(0,0,0,.2);
  padding: 1px 5px;
  font-size: 9px;
  color: #8ab8d8;
  border-radius: 2px;
}

.no-candidates {
  text-align: center;
  padding: 30px 20px;
  color: var(--text-dim);
}
.no-candidates-hint {
  font-size: 10px;
  margin-top: 6px;
  opacity: 0.8;
}
</style>