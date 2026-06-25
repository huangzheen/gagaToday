<template>
  <div>
    <!-- ═══ Stage 1: 定妆照 ═══ -->
    <h3 style="color:var(--gold2);margin-bottom:4px">📸 Stage 1 — 定妆照</h3>
    <p style="font-size:9px;color:var(--text-dim);margin-bottom:8px">
      生成或上传一张高质量参考图。后续所有变体都以它为基础，保持建筑结构和构图完全一致。
      <br/><span style="color:var(--gold)">💡 定妆照用 photorealistic 实景 → 变体自动转 16-bit 像素艺术。</span>
    </p>

    <!-- 已有定妆照 → 快速进入 -->
    <div v-if="existingRefUrl" class="stage-box" style="border-color:var(--gold)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <span style="font-size:11px;color:var(--gold);font-weight:bold">✅ 发现已有定妆照</span>
        <button class="btn primary" @click="useExisting" style="padding:4px 10px;font-size:9px">
          📸 使用 → 进入 Stage 2
        </button>
      </div>
      <img :src="existingRefUrl" style="width:100%;max-height:200px;object-fit:contain;border:1px solid var(--gold)" />
    </div>

    <div class="stage-box" v-if="!referenceUrl">
      <!-- 生成方式 -->
      <div style="margin-bottom:8px">
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">
          <input v-model="refDescription" :placeholder="'例：' + (currentPoi?.name_de || '') +' with its main facade, sunny day, photorealistic architecture photo, wide angle'"
                 style="flex:1;font-size:10px;padding:6px;background:#0a0a1a;color:var(--gold2);border:1px solid var(--border)" />
          <button class="btn primary" @click="generateReference" :disabled="isGenerating">
            {{ isGenerating ? '⏳' : '🎨 生成定妆照' }}
          </button>
        </div>
        <div style="font-size:9px;color:var(--text-dim)">
          模型: <span style="color:var(--gold)">OpenRouter · GPT-5.4 Image 2</span>
        </div>
      </div>
      <div class="divider">或</div>
      <div>
        <label class="upload-label">📁 拖放或点击上传定妆照
          <input type="file" accept="image/*" @change="handleUpload" style="display:none" />
        </label>
        <div v-if="uploadMsg" style="font-size:9px;margin-top:4px" :style="{color: uploadMsg.startsWith('✅')?'#44ff88':'#ff4444'}">{{ uploadMsg }}</div>
      </div>
    </div>

    <!-- 刚生成/上传的预览 -->
    <div v-if="referenceUrl && !referenceLocked" class="ref-preview">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
        <span style="font-size:10px;color:var(--gold)">📷 定妆照预览</span>
        <div style="display:flex;gap:6px">
          <button class="btn success" @click="lockReference" style="font-size:9px;padding:4px 10px">🔒 锁定 → 生成变体</button>
          <button class="btn" @click="saveReference" style="font-size:9px;padding:4px 8px">💾 存档</button>
        </div>
      </div>
      <img :src="referenceUrl" @error="onRefImgError"
           style="width:100%;max-height:260px;object-fit:contain;border:2px solid var(--gold)" />
      <div v-if="refImgFailed" style="font-size:9px;color:#ff4444;margin-top:4px">
        ⚠️ 加载失败 — <a @click="retryRefImg" style="color:var(--gold);cursor:pointer">重试</a>
      </div>
    </div>

    <!-- ═══ Stage 2: 变体 ═══ -->
    <div v-if="referenceLocked">
      <h3 style="color:var(--gold2);margin-bottom:2px">🎮 Stage 2 — 像素化变体</h3>
      <p style="font-size:9px;color:var(--text-dim);margin-bottom:4px">
        基于定妆照生成不同天气/季节/时间的 16-bit 像素化版本。仅改变氛围，建筑不变。
      </p>

      <!-- 锁定后的参考图缩略 -->
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;background:var(--navy);padding:4px 8px">
        <img :src="referenceUrl" style="width:60px;height:45px;object-fit:cover;border:1px solid var(--gold)" />
        <span style="font-size:9px;color:var(--gold)">🔒 已锁定 · 变体模型:</span>
        <select v-model="variantModel" style="font-size:9px;padding:3px;background:#0a0a1a;color:var(--gold2);border:1px solid var(--border)">
          <option value="doubao-seedream-4-5-251128">火山 · Seedream 4.5</option>
          <option value="openai/gpt-5.4-image-2">OpenRouter · Image 2</option>
        </select>
        <button class="btn" @click="resetReference" style="font-size:8px;padding:3px 6px;margin-left:auto">🔄 换定妆照</button>
      </div>

      <div class="card-grid">
        <div v-for="v in variants" :key="v.id" class="card">
          <h4>{{ v.icon }} {{ v.label }}</h4>
          <p style="font-size:8px;color:var(--text-dim)">{{ v.desc }}</p>
          <div v-if="v.url" class="img-preview" style="height:100px">
            <img :src="v.url" :alt="v.label" style="width:100%;height:100%;object-fit:cover" />
          </div>
          <div v-else class="img-preview" style="height:40px">
            <span style="font-size:9px;color:var(--text-dim)">{{ v.generating ? '⏳ 生成中...' : '未生成' }}</span>
          </div>
          <div class="card-actions">
            <button class="btn" @click="generateVariant(v)" :disabled="v.generating || isGenerating">
              {{ v.generating ? '⏳' : (v.url ? '🔄' : '🎨 生成') }}
            </button>
            <span v-if="v.url" class="status-dot ok" />
          </div>
        </div>
      </div>

      <div style="margin-top:10px;display:flex;gap:8px">
        <button class="btn primary" @click="generateAllVariants" :disabled="isGenerating">
          🤖 一键生成全部变体
        </button>
        <button class="btn success" @click="exportVariants" :disabled="doneCount === 0">
          💾 导出到游戏 assets
        </button>
      </div>
      <div style="font-size:9px;color:var(--text-dim);margin-top:4px">
        已生成 {{ doneCount }}/{{ variants.length }} 个变体
      </div>
    </div>

    <!-- 日志 -->
    <div v-if="store.generationLog.length" style="margin-top:8px">
      <div class="json-viewer" style="max-height:100px;font-size:9px">
        <div v-for="(line, i) in store.generationLog.slice(-8)" :key="i">{{ line }}</div>
      </div>
    </div>

    <!-- 错误 -->
    <div v-if="store.error" style="margin-top:8px;padding:6px;background:#330000;border:1px solid #ff4444;color:#ff4444;font-size:10px">⚠️ {{ store.error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'

const store = useGeneratorStore()
const poiId = computed(() => store.currentPoiId)
const currentPoi = computed(() => store.currentPoi)

// ── Stage 1 state ──
const refDescription = ref('')
const referenceUrl = ref(null)
const referencePath = ref(null)
const referenceLocked = ref(false)
const isGenerating = ref(false)
const uploadMsg = ref('')
const refImgFailed = ref(false)
const existingRefUrl = ref(null)   // auto-detected

// ── Stage 2 variants ──
const variantModel = ref('doubao-seedream-4-5-251128')

const variants = ref([
  { id: 'spring', icon: '🌷', label: '春天', desc: '新绿嫩叶，粉色花绽，柔暖阳光', url: null, path: null, generating: false },
  { id: 'summer', icon: '☀️', label: '夏天', desc: '深绿树冠，烈日短影，空气微热', url: null, path: null, generating: false },
  { id: 'autumn', icon: '🍂', label: '秋天', desc: '金红落叶，斜阳长影，暖金光晕', url: null, path: null, generating: false },
  { id: 'winter', icon: '❄️', label: '冬天', desc: '薄雪屋顶，苍白阳光，清冷寂静', url: null, path: null, generating: false },
  { id: 'night', icon: '🌙', label: '夜景', desc: '窗内暖灯，街灯光晕，月光银影', url: null, path: null, generating: false },
  { id: 'rain', icon: '🌧️', label: '雨天', desc: '灰天雨丝，潮湿反光，蓝灰调子', url: null, path: null, generating: false },
  { id: 'snow', icon: '🌨️', label: '大雪', desc: '厚雪覆盖，雪花纷飞，灰白柔光', url: null, path: null, generating: false },
  { id: 'golden', icon: '🌅', label: '黄昏', desc: '金色直射，橙红天空，极长影子', url: null, path: null, generating: false },
])

const doneCount = computed(() => variants.value.filter(v => v.url).length)

// ── Auto-detect existing reference on POI switch ──
watch(poiId, async (newId) => {
  // reset
  referenceUrl.value = null; referencePath.value = null; referenceLocked.value = false
  variants.value.forEach(v => { v.url = null; v.path = null; v.generating = false })
  existingRefUrl.value = null

  // probe existence
  const probeUrl = `/generated/ref_${newId}.png`
  // 用 Image 对象探测（比 HEAD 更可靠）
  const probeImg = new Image()
  probeImg.onload = () => {
    existingRefUrl.value = probeUrl
    store.log(`📸 发现已有定妆照: ${probeUrl}`)
  }
  probeImg.onerror = () => { existingRefUrl.value = null }
  probeImg.src = probeUrl
}, { immediate: true })

// ── Use existing ──
function useExisting() {
  referenceUrl.value = existingRefUrl.value
  // derive absolute path
  referencePath.value = `/Volumes/NewDisk/GermanLearning/frontend/poi-generator/public/generated/ref_${poiId.value}.png`
  existingRefUrl.value = null
  lockReference()
}

// ── Stage 1: 生成定妆照 ──
async function generateReference() {
  if (!refDescription.value.trim()) { store.error = '请输入地点描述'; return }
  isGenerating.value = true; store.error = null; store.log('📸 生成定妆照 (OpenRouter)...')

  const poi = store.currentPoi
  const desc = [
    `Architectural photography: ${refDescription.value.trim()}, ${poi?.name_de || ''}, Munich Germany.`,
    `Wide-angle lens, centered composition, professional real-estate photo quality,`,
    `clear sunny day, natural daylight, sharp focus, vibrant colors, no people or minimal,`,
    `16:9 horizontal framing from a flattering public vantage point.`,
  ].join(' ')

  try {
    const res = await api.generateImage(desc, `ref_${poiId.value}.png`, {
      model: 'openai/gpt-5.4-image-2', promptType: 'scene',
    })
    referenceUrl.value = res.url; referencePath.value = res.path; refImgFailed.value = false
    await new Promise(r => setTimeout(r, 800))
    store.log('✅ 定妆照已生成 — 点击「🔒 锁定 → 生成变体」进入 Stage 2')
  } catch (e) {
    store.error = e.message; store.log(`❌ ${e.message}`)
  } finally { isGenerating.value = false }
}

// ── Stage 1: 上传 ──
async function handleUpload(e) {
  const file = e.target.files[0]; if (!file) return
  uploadMsg.value = '⏳ 上传中...'
  const reader = new FileReader()
  reader.onload = async () => {
    try {
      const res = await fetch('/api/generate/upload-reference', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: `ref_${poiId.value}_upload.jpg`, data: reader.result }),
      })
      const d = await res.json()
      if (d.success) {
        referenceUrl.value = d.url; referencePath.value = d.path
        uploadMsg.value = '✅ 上传成功！点锁定进入 Stage 2'
        store.log('📁 定妆照已上传')
      } else { uploadMsg.value = `❌ ${d.detail}` }
    } catch (err) { uploadMsg.value = `❌ ${err.message}` }
  }
  reader.readAsDataURL(file)
}

// ── Save reference to archive ──
async function saveReference() {
  if (!referencePath.value) return
  store.log('💾 存档定妆照...')
  // Copy into game assets
  try {
    const res = await api.saveImage(referencePath.value, poiId.value, '_reference', `ref_${poiId.value}.png`)
    store.log(`✅ 已存档: ${res.path || 'assets'}`)
  } catch (e) { store.error = e.message }
}

// ── Lock ──
function lockReference() {
  referenceLocked.value = true
  store.log('🔒 定妆照已锁定 — 可生成变体')
}

function resetReference() {
  referenceLocked.value = false
  referenceUrl.value = null; referencePath.value = null
  variants.value.forEach(v => { v.url = null; v.path = null; v.generating = false })
}

// ═══════════════════════════════════════════
// Stage 2: Variant prompts & generation
// ═══════════════════════════════════════════

const VARIANT_PROMPTS = {
  spring: { cn:'春季，浅绿新叶点缀，粉色花盛放，柔和暖阳，清澈蓝天', en:'spring, fresh green leaves, pink blossoms, soft warm sun, clear blue sky' },
  summer: { cn:'盛夏，茂密深绿树冠，强烈正午阳光投短影，亮白蓝天，建筑表面明亮', en:'high summer, dense green canopy, strong midday sun, short shadows, bright sky' },
  autumn: { cn:'深秋，金黄橙红落叶覆盖地面，低斜阳投长影，暖金光晕笼罩建筑', en:'late autumn, golden orange fallen leaves, slanting sun, long shadows, amber glow' },
  winter: { cn:'冬季晴日，薄雪覆盖屋顶窗台，光秃树枝，浅蓝冷色天空，苍白阳光', en:'clear winter day, thin snow on roof, bare branches, pale blue sky, cold light' },
  night:  { cn:'晴朗夜晚，窗户透暖黄灯光，街灯点亮，深蓝夜空，月光银影', en:'clear night, warm yellow windows, street lamps lit, dark blue sky, moonlight' },
  rain:   { cn:'雨天，深灰天空，细密雨丝可见，潮湿反光地面映建筑倒影，蓝灰调', en:'rainy, dark grey sky, visible rain, wet reflective ground, grey-blue tone' },
  snow:   { cn:'大雪纷飞，厚积雪覆屋顶地面，密集白色雪花可见，灰白天空，柔光', en:'heavy snowfall, thick snow layer, visible white snowflakes, grey-white sky, soft light' },
  golden: { cn:'日落黄金时刻，低角金色阳光直射建筑正面，橙红天空渐层，极长影', en:'golden hour sunset, low golden sun hitting facade, orange-red sky, very long shadows' },
}

async function generateVariant(v) {
  if (!referencePath.value) return
  v.generating = true; store.error = null; store.log(`🎨 生成 ${v.label}...`)

  const vp = VARIANT_PROMPTS[v.id] || VARIANT_PROMPTS.spring
  const prompt = [
    `STRICT: Keep the building, composition, camera angle, and all structures IDENTICAL to the reference image.`,
    `ONLY change atmosphere: ${vp.cn}. ${vp.en}.`,
    `STYLE: 16-bit pixel art game background, hard blocky pixel edges, no anti-aliasing, limited 16-color palette, retro JRPG aesthetic.`,
  ].join('\n')

  try {
    const res = await fetch('/api/generate/with-reference', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reference_path: referencePath.value,
        description: prompt,
        output_name: `${poiId.value}_${v.id}.png`,
        model: variantModel.value,
      }),
    })
    const d = await res.json()
    if (!d.success) throw new Error(d.detail || 'failed')
    v.url = d.url; v.path = d.path
    await new Promise(r => setTimeout(r, 600))
    store.log(`✅ ${v.label}`)
  } catch (e) {
    store.error = e.message; store.log(`❌ ${v.label}: ${e.message}`)
  } finally { v.generating = false }
}

async function generateAllVariants() {
  isGenerating.value = true; store.error = null
  for (const v of variants.value) {
    if (!v.url && !v.generating) await generateVariant(v)
  }
  isGenerating.value = false; store.markGenerated('refworkflow')
}

async function exportVariants() {
  store.log('💾 导出变体到游戏 assets...')
  for (const v of variants.value) {
    if (v.path) {
      try { await api.saveImage(v.path, poiId.value, 'exterior', `${poiId.value}_${v.id}.png`) }
      catch (e) { store.log(`  ⚠️ ${v.label}: ${e.message}`) }
    }
  }
  store.log(`✅ 已导出到 assets/scenes/munich/${poiId.value}/exterior/`)
}

function onRefImgError() { refImgFailed.value = true }
function retryRefImg() {
  refImgFailed.value = false
  const u = referenceUrl.value; referenceUrl.value = ''
  setTimeout(() => { referenceUrl.value = u + '?t=' + Date.now() }, 100)
}
</script>

<style scoped>
.stage-box {
  background: #12122a;
  border: 1px solid #333;
  padding: 10px;
  margin-bottom: 8px;
}
.ref-preview {
  background: #0a0a1a;
  padding: 6px;
  border: 1px solid #333;
}
.upload-label {
  display: block;
  padding: 12px;
  border: 2px dashed var(--border);
  text-align: center;
  cursor: pointer;
  color: var(--text-dim);
  font-size: 10px;
  transition: border-color 0.2s;
}
.upload-label:hover {
  border-color: var(--gold);
  color: var(--gold2);
}
.divider {
  text-align: center;
  color: #444;
  font-size: 9px;
  margin: 6px 0;
  position: relative;
}
.divider::before, .divider::after {
  content: '';
  display: inline-block;
  width: 40%;
  height: 1px;
  background: #333;
  vertical-align: middle;
  margin: 0 8px;
}
.error-msg {
  margin-top: 8px;
  padding: 6px;
  background: #330000;
  border: 1px solid #ff4444;
  color: #ff4444;
  font-size: 10px;
}
</style>