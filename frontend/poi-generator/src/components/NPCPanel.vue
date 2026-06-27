<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">🧑 NPC 管理</h3>
    <p style="font-size:9px;color:var(--text-dim);margin-bottom:6px">
      头像 / 半身像可手动上传,也可 ✨ AI 一键生成(遵守 gagaToday 视觉规范)。
      姓名与介绍可手动填或 🤖 一键生成。
    </p>



    <!-- ═══ 双列布局:左 NPC 列表 / 右 编辑表单 ═══ -->
    <div class="npc-layout">

      <!-- ── 左:NPC 列表 ── -->
      <aside class="npc-sidebar">
        <div class="npc-sidebar-header">
          <span class="npc-sidebar-title">NPC 列表</span>
          <span class="npc-sidebar-count">{{ npcs.length }}</span>
        </div>

        <div class="npc-list">
          <div
            v-for="(npc, i) in npcs"
            :key="npc.id"
            class="npc-card"
            :class="{ active: editing?.id === npc.id }"
            @click="editExisting(npc)"
          >
            <div class="npc-thumb">
              <img v-if="npc.head_image" :src="npc.head_image + '?t=' + cacheBust" :alt="npc.name_zh || npc.id" />
              <span v-else style="color:var(--text-dim);font-size:20px">👤</span>
            </div>
            <div class="npc-info">
              <div class="npc-name">
                {{ npc.name_zh || '(未命名)' }}
              </div>
              <div class="npc-name-de">{{ npc.name_de || '—' }}</div>
              <div class="npc-role">{{ npc.role_zh || npc.role_de || '未指定角色' }}</div>
              <div class="npc-meta">
                <span v-if="npc.head_image" style="color:var(--gold)">✓头</span>
                <span v-if="npc.half_image" style="color:var(--gold)">✓半身</span>
                <span v-if="!npc.head_image && !npc.half_image" style="color:var(--text-dim)">无图</span>
              </div>
            </div>
            <button class="npc-del" title="删除 NPC" @click.stop="deleteNpc(i)">×</button>
          </div>

          <div v-if="!npcs.length" class="npc-empty">
            <div style="font-size:32px;opacity:.4;margin-bottom:6px">🧑</div>
            <div style="font-size:10px;color:var(--text-dim)">还没有 NPC</div>
            <div style="font-size:9px;color:var(--text-dim)">点下方按钮添加</div>
          </div>
        </div>

        <button class="btn primary" @click="startNew" style="width:100%;margin-top:8px">
          ＋ 添加 NPC
        </button>
      </aside>

      <!-- ── 右:编辑表单 ── -->
      <main class="npc-main">
        <!-- 空状态 -->
        <div v-if="!editing" class="npc-form-empty">
          <div style="font-size:48px;opacity:.3;margin-bottom:10px">👈</div>
          <div style="font-size:11px;color:var(--text-dim)">从左侧选择 NPC 编辑</div>
          <div style="font-size:9px;color:var(--text-dim);margin-top:4px">或点 ＋ 添加 NPC 开始新建</div>
        </div>

        <!-- 表单 -->
        <section v-else class="npc-form">
      <div class="npc-form-header">
        <span>{{ npcs.find(n => n.id === editing.id) ? '✏️ 编辑 NPC' : '➕ 新增 NPC' }}</span>
        <div class="npc-form-actions">
          <button
            class="btn primary"
            @click="generateAll"
            :disabled="llmLoading || aiGenerating"
            style="padding:3px 8px;font-size:9px"
            title="一键全包:LLM 文字 + 头像 + 半身像"
          >{{ (llmLoading || aiGenerating) ? '⏳' : '生成' }}</button>
          <button
            class="btn success"
            @click="saveNpc"
            :disabled="saving"
            style="padding:3px 8px;font-size:9px"
            title="保存 NPC 数据(图已自动存)"
          >{{ saving ? '⏳' : '保存' }}</button>
          <button class="btn" @click="cancelEdit" style="padding:3px 8px;font-size:9px">取消</button>
        </div>
      </div>

      <!-- NPC ID + 头像 + 半身像 — 同一行(节省垂直空间) -->
      <div class="npc-id-portraits">
        <!-- NPC ID -->
        <div class="npc-id-wrap">
          <label>NPC ID <span class="hint">(英文+下划线)</span></label>
          <input v-model="editing.id" :disabled="!!npcs.find(n => n.id === editing.id)" placeholder="frauenkirche_pfarrer" />
        </div>

        <!-- 头像 -->
        <div class="npc-portrait-cell">
          <label style="font-size:9px;color:var(--gold2);text-align:center;display:block;margin-bottom:4px">头像<br/><span style="color:var(--text-dim)">64×64 · 1:1</span></label>
          <div class="npc-portrait" :class="{ filled: editing.head_image }">
            <img v-if="editing.head_image" :src="editing.head_image" alt="head" />
            <span v-else style="color:var(--text-dim);font-size:20px">👤</span>
          </div>
          <div style="display:flex;gap:3px;margin-top:4px;justify-content:center">
            <label class="btn mini">
              <input type="file" accept="image/*" @change="onPortraitUpload($event, 'head')" hidden />
              {{ editing.head_image ? '🔄' : '📁' }}
            </label>
            <button class="btn mini" v-if="editing.head_image" @click="whiteToTransparent('head')" :disabled="transparentizing" title="白底转透明(自动备份)">
              {{ transparentizing === 'head' ? '⏳' : '🪄' }}
            </button>
            <button v-if="editing.head_image" class="btn mini danger" @click="editing.head_image = ''">🗑️</button>
          </div>
        </div>

        <!-- 半身像 -->
        <div class="npc-portrait-cell">
          <label style="font-size:9px;color:var(--gold2);text-align:center;display:block;margin-bottom:4px">半身像<br/><span style="color:var(--text-dim)">192×256 · 3:4</span></label>
          <div class="npc-portrait half" :class="{ filled: editing.half_image }">
            <img v-if="editing.half_image" :src="editing.half_image" alt="half" />
            <span v-else style="color:var(--text-dim);font-size:20px">🧍</span>
          </div>
          <div style="display:flex;gap:3px;margin-top:4px;justify-content:center">
            <label class="btn mini">
              <input type="file" accept="image/*" @change="onPortraitUpload($event, 'half')" hidden />
              {{ editing.half_image ? '🔄' : '📁' }}
            </label>
            <button class="btn mini" v-if="editing.half_image" @click="whiteToTransparent('half')" :disabled="transparentizing" title="白底转透明(自动备份)">
              {{ transparentizing === 'half' ? '⏳' : '🪄' }}
            </button>
            <button v-if="editing.half_image" class="btn mini danger" @click="editing.half_image = ''">🗑️</button>
          </div>
        </div>
      </div>

      <!-- 姓名 -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div class="field">
          <label>中文姓名</label>
          <input v-model="editing.name_zh" placeholder="约翰神父" />
        </div>
        <div class="field">
          <label>德文姓名</label>
          <input v-model="editing.name_de" placeholder="Pater Johann Schmidt" />
        </div>
      </div>

      <!-- 角色 -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div class="field">
          <label>角色(中)</label>
          <input v-model="editing.role_zh" placeholder="神父" />
        </div>
        <div class="field">
          <label>角色(德)</label>
          <input v-model="editing.role_de" placeholder="Pfarrer" />
        </div>
      </div>

      <!-- 年龄段 + 性格 -->
      <div style="display:grid;grid-template-columns:1fr 2fr;gap:8px">
        <div class="field">
          <label>年龄段</label>
          <select v-model="editing.age_band">
            <option value="teen">少年(teen)</option>
            <option value="adult">成年(adult)</option>
            <option value="senior">长者(senior)</option>
          </select>
        </div>
        <div class="field">
          <label>性格(逗号分隔)</label>
          <input v-model="editing.personalityStr" placeholder="warm, patient, thoughtful" />
        </div>
      </div>

      <!-- 介绍 -->
      <div class="field">
        <label>介绍(中文,250-350 字,6 段成长经历)</label>
        <textarea v-model="editing.background_zh" rows="6" placeholder="在 Frauenkirche 服务 18 年..."></textarea>
      </div>
        </section>
      </main>
    </div>

    <!-- 日志 -->
    <div v-if="store.generationLog.length" style="margin-top:10px">
      <div class="json-viewer" style="max-height:100px;font-size:9px">
        <div v-for="(line, i) in store.generationLog.slice(-6)" :key="i">{{ line }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'

const store = useGeneratorStore()
const poiId = computed(() => store.currentPoiId)
const cacheBust = ref(Date.now())

// ── 状态 ──
const npcs = ref([])
const editing = ref(null)
const saving = ref(false)
const llmLoading = ref(false)
const llmError = ref('')

// AI 图像相关 — 用全局 store.imageModel(标题栏已选)
const aiGenerating = ref(null)  // null | 'head' | 'half'
const transparentizing = ref(null)  // null | 'head' | 'half'  去白底中

// ── 默认 NPC schema(空白) ──
function blankNpc(id = '') {
  return {
    id,
    name_de: '',
    name_zh: '',
    role_de: '',
    role_zh: '',
    age_band: 'adult',
    personalityStr: '',   // 表单临时字段,逗号分隔
    background_zh: '',
    head_image: '',
    half_image: '',
    review_status: 'draft',
  }
}

// ── 从后端加载 NPC 列表 ──
async function loadNpcs() {
  try {
    const res = await api.getPoi(poiId.value, { includeContent: true })
    const raw = res.poi?.content?.npc
    npcs.value = Array.isArray(raw) ? raw.map(n => ({
      ...n,
      personalityStr: Array.isArray(n.personality) ? n.personality.join(', ') : '',
    })) : []
    store.log(`📂 已加载 ${npcs.value.length} 个 NPC`)
  } catch (e) {
    npcs.value = []
  }
}

// ── 切 POI 时 reload ──
watch(poiId, () => {
  editing.value = null
  loadNpcs()
}, { immediate: true })

// ── 新增 ──
function startNew() {
  const id = `${poiId.value}_npc${npcs.value.length + 1}`
  editing.value = blankNpc(id)
}

// ── 编辑已有 ──
function editExisting(npc) {
  editing.value = { ...npc, personalityStr: Array.isArray(npc.personality) ? npc.personality.join(', ') : '' }
}

// ── 取消 ──
function cancelEdit() {
  editing.value = null
}

// ── 删除 ──
async function deleteNpc(i) {
  const n = npcs.value[i]
  if (!window.confirm(`确认删除 NPC "${n.name_zh || n.id}"?\\n(不会删除已上传的头像/半身像文件)`)) return
  npcs.value.splice(i, 1)
  if (editing.value?.id === n.id) editing.value = null
  await persist()
}

// ── 保存(写入 poi_content 表) ──
async function persist() {
  saving.value = true
  try {
    // 把 personalityStr 还原为 array
    const payload = npcs.value.map(n => {
      const { personalityStr, ...rest } = n
      return { ...rest, personality: personalityStr.split(',').map(s => s.trim()).filter(Boolean) }
    })
    await api.saveNpcContent(poiId.value, payload)
    store.log(`💾 已保存 ${payload.length} 个 NPC`)
    store.markGenerated('npc')
  } catch (e) {
    store.error = e.message
  } finally {
    saving.value = false
  }
}

async function saveNpc() {
  // 把当前 editing 合并到 npcs
  const idx = npcs.value.findIndex(n => n.id === editing.value.id)
  if (idx >= 0) npcs.value[idx] = { ...editing.value }
  else npcs.value.push({ ...editing.value })
  editing.value = null
  await persist()
}

// ════════════════════════════════════════════════════════
// 🤖 一键全量生成(2026-06-27 升级)
// 串行 3 步:LLM 文字 → 头像 AI → 半身像 AI
// ════════════════════════════════════════════════════════
async function generateAll() {
  if (!editing.value) return
  if (!editing.value.id) { store.error = '请先填 NPC ID'; return }

  store.error = null
  llmError.value = ''

  // 步骤 1:LLM 文字生成
  llmLoading.value = true
  store.log('🤖 LLM 生成文字中...')
  try {
    await runLLMGenerate()
  } catch (e) {
    llmError.value = e.message
    store.error = `LLM 生成失败: ${e.message}`
    llmLoading.value = false
    return
  }
  llmLoading.value = false
  store.log(`🤖 LLM 完成: ${editing.value.name_zh || editing.value.id}`)

  // 步骤 2:头像 AI(只在没图时生成)
  if (!editing.value.head_image) {
    store.log('🎨 生成头像...')
    aiGenerating.value = 'head'
    try { await runPortraitGenerate('head') }
    catch (e) { store.log(`❌ 头像: ${e.message}`) }
    aiGenerating.value = null
  }

  // 步骤 3:半身像 AI(只在没图时生成)
  if (!editing.value.half_image) {
    store.log('🎨 生成半身像...')
    aiGenerating.value = 'half'
    try { await runPortraitGenerate('half') }
    catch (e) { store.log(`❌ 半身像: ${e.message}`) }
    aiGenerating.value = null
  }

  store.log('✅ 全部生成完成!点 保存 写入 SQLite')
}

// ── 🤖 LLM 一键生成(只被 generateAll 调用) ──
async function runLLMGenerate() {
  if (!editing.value) return
  llmLoading.value = true
  llmError.value = ''
  store.error = null
  try {
    const poi = store.currentPoi
    const partial = editing.value
    // 拼 prompt:把当前已填的字段(role_zh, role_de)也带过去作为 hint
    const roleHint = partial.role_zh || partial.role_de || ''
    // 拼 OSM 真实上下文(POIInfoForm 写入 store.osmData,可能是 null)
    const osm = store.osmData?.primary_poi
    const building = store.osmData?.building
    const osmCtx = osm ? `
OSM 真实数据(必须基于这些,不要编造):
- 标准名: ${osm.name || '?'}
- 类别: ${osm.class || '?'} / ${osm.subclass || '?'}
- 距离: ${osm.distance_m || '?'}m
- 别名: ${(osm.all_names || []).join('、') || '无'}
${building ? `- 建筑高度: ${building.render_height || '?'}m` : ''}
- 邻近 POI: ${(store.osmData?.nearby_pois || []).slice(0, 5).map(p => p.name).join('、') || '无'}
- 周边交通: ${(store.osmData?.transport || []).slice(0, 3).map(t => t.name).join('、') || '无'}` : '(该 POI 暂无 OSM 真实数据)'

    const prompt = `你是 gagaToday 项目的 NPC 生成助手。

# 项目背景 — gagaToday
- **类型**: 16-bit 像素艺术风格德国留学模拟 RPG(参考 Stardew Valley / Coffee Talk)
- **平台**: 玩家通过地图探索 + AI 对话体验德国留学日常
- **技术**: Vue 3 前端 + PMTiles 真实地图 + LLM 对话生成 + SQLite 数据持久化
- **核心口号**: 在德国,学会生活。Learn. Explore. Belong.

# 玩家画像(重要,NPC 必须适配)
- 15-16 岁中国初三毕业生,刚到德国(国际学校或文理中学)
- 德语水平 A1 入门递进到 B2,目标 TestDaF 4×4
- 年轻、有探索欲、对德国文化好奇但陌生
- 可能第一次离家,需要情感支持 + 实用信息
- 教学性优先于纯娱乐 — NPC 对话是隐性德语学习场景

# 当前 POI(这是 NPC 工作/生活的地点)
- 中文名: ${poi?.name_zh || '?'}
- 德文名: ${poi?.name_de || '?'}
- 城市: ${poi?.city || 'munich'}(德国巴伐利亚州首府)
- 类型: ${poi?.type || '?'}
- 坐标: ${poi?.lat?.toFixed(4) || '?'}, ${poi?.lng?.toFixed(4) || '?'}
${osmCtx}

${roleHint ? `# 用户已指定角色: ${roleHint}
(基于 POI 类型 "${poi?.type}" 选定。请让 NPC 的工作日常与该角色 + POI 类型强相关)` : `# 角色自推导
请根据 POI 类型 "${poi?.type}" 自动推导合适 NPC 职业,参考映射:
- 教堂/宗教场所 → Pfarrer(神父) / Sakristan(教堂管理员)
- 博物馆 → Kurator(馆长) / Guide(导览员) / Aufsicht(看护员)
- 广场 → Straßenmusikant(街头艺人) / Marktbesucher(游客) / Polizist
- 公园/城堡 → Gärtner(园丁) / Schlosspächter(管理员) / Jogger
- 商店/超市 → Kassiererin(收银员) / Verkäuferin(店员) / Bäcker
- 餐厅/咖啡 → Wirt(店主) / Kellner(服务员) / Koch(厨师)`}

# NPC 背景要求(本 prompt 最关键,2026-06-27 升级:6 段完整成长经历)
"background_zh" 字段必须是 **250-350 字中文,6 段式完整成长故事**,每段 1-3 句,6 段用换行分隔:

1. **【童年背景】** 在哪里出生/成长?家庭背景/父母职业?什么性格底色?
   例:"1962 年生于巴伐利亚小城 Landsberg am Lech,父亲是面包师,母亲在幼儿园工作。童年在面包房后厨帮工,养成了勤劳和面团般的耐心"

2. **【教育经历】** 学校/学位/重要学习阶段?哪些人或事影响了你?
   例:"1981 年慕尼黑大学神学系本科,1988 年在罗马格里高利大学进修获硕士学位。导师 Pater Schmidt 的严谨治学影响至今"

3. **【职业路径】** 之前做过什么工作?如何一步步进入现在的领域?
   例:"毕业后在雷根斯堡教区做助理神父 5 年,1995 年调回慕尼黑,先后在 St. Peter 和 Frauenkirche 服务。2008 年获高级神父职称"

4. **【为何在此景点】** 为什么选择 / 被分配到这个具体的 POI?具体动机是什么?
   例:"主动申请到 Frauenkirche,因为这里能接触到最多国际游客和留学生,想在退休前把'跨文化交流'做成自己的事工方向"

5. **【现状与日常】** 现在的典型工作日是什么样?有什么小习惯?
   例:"每天 7 点开教堂侧门,8 点晨祷,9 点和 17 点敲钟。上午在告解室接待,下午处理邮件和教区文件。周三下午专门接听 Seelsorge 倾诉电话"

6. **【与中国学生】** 你怎么跟中国留学生互动?展示什么性格特点?愿意聊什么?
   例:"对中文母语学生会主动放慢语速,准备英文版教堂历史册。曾在春节带 5 个中国学生看管风琴内部构造,还请他们吃了慕尼黑白香肠"

# 输出 Schema(严格遵守,只返回合法 JSON,不要 markdown 包裹)

{
  "id": "npc_${poi?.id || 'x'}_${(partial.id?.split('_').pop()) || '1'}",
  "name_de": "典型德国姓名(名+姓,反映年龄段的常见姓氏)",
  "name_zh": "中文译名(音译为主,不意译)",
  "role_de": "德文职业(如 Pfarrer / Kurator)",
  "role_zh": "中文职业",
  "age_band": "adult 或 teen 或 senior(根据角色推导合理年龄)",
  "personality": ["2-3 个英文形容词,如 warm / patient / thoughtful / playful / gruff"],
  "background_zh": "按上述 6 段式完整成长故事,250-350 字,6 段用换行分隔",
  "language_profile": {
    "default_language": "de",
    "lang_pref": { "de": 0.8, "en": 0.2 },
    "can_speak_english": true,
    "english_level": "B1(神父/馆长) 或 A2(店员/园丁)",
    "patience_with_beginners": "high 或 medium(根据角色)"
  }
}

# 硬规则(违反任何一条都算生成失败)
1. **绝不编造**:不确定的地址、电话、具体历史年份、家人姓名 — 一律不写或泛化
2. **基于 OSM 真实数据**:上面的 OSM 字段如果存在,必须用作背景细节来源
3. **德国文化准确性**:德文姓名/职业/场所名称必须用标准德语(注意大小写、变音 ä ö ü ß)
4. **POI 类型一致性**:NPC 工作内容必须跟 POI 类型强相关(教堂 NPC 不能讲咖啡)
5. **不要空洞形容词**:背景里禁止"热情友好专业"等套话 — 必须给具体场景、具体动作
6. **personality 2-3 个**:多一个词 LLM 就开始凑数,严控数量
7. **language_profile.english_level**:根据角色推断(教堂/博物馆/酒店 = B1,商店/超市 = A2)
8. **只返回 JSON**:不要任何 markdown 包裹(我已用 schema 标结构)`

    const res = await api.generateJson(prompt, null, 'qwen3-max')
    const d = res.data
    // 合并到 editing(保留 id / head_image / half_image)
    editing.value = {
      ...editing.value,
      name_de: d.name_de || editing.value.name_de,
      name_zh: d.name_zh || editing.value.name_zh,
      role_de: d.role_de || editing.value.role_de,
      role_zh: d.role_zh || editing.value.role_zh,
      age_band: d.age_band || editing.value.age_band,
      personalityStr: Array.isArray(d.personality) ? d.personality.join(', ') : editing.value.personalityStr,
      background_zh: d.background_zh || editing.value.background_zh,
    }
    store.log(`🤖 LLM 已生成: ${d.name_zh} (${d.role_zh})`)
  } catch (e) {
    llmError.value = e.message
    store.error = e.message
  } finally {
    llmLoading.value = false
  }
}

// ════════════════════════════════════════════════════════
// AI 生成头像 / 半身像(遵守 gagaToday 视觉规范)
// ════════════════════════════════════════════════════════

/**
 * 拼 NPC portrait prompt(基于 gagaToday_visual_style_guide.md §2/3/5/8/15)
 *
 * @param {Object} npc - 当前 editing NPC
 * @param {'head'|'half'} kind - 头像(1:1 半身) 或 半身像(3:4 上身)
 */
function buildNpcPortraitPrompt(npc, kind) {
  const subject = [
    `${npc.name_de || 'NPC'} (${npc.name_zh || '?'}), ${npc.role_de || '?'} (${npc.role_zh || '?'})`,
    `${npc.age_band || 'adult'} age`,
    `personality: ${(npc.personality || []).slice(0, 3).join(', ') || 'warm, patient'}`,
    'German study-abroad life simulation RPG character',
  ].join(', ')

  // 视觉风格核心(§2.1 英文 16 条)
  const style = `premium low-resolution pixel art, refined 16-bit / 32-bit inspired game illustration, grounded German realism, retro European study-abroad RPG atmosphere, warm nostalgic but not childish, slightly lonely first-year-abroad mood, handcrafted pixel-art texture, crisp pixel edges, readable silhouette, limited color palette, dark navy outline, blocky pixel highlights and shadows`

  // 构图(§5.6 半身头像 vs §5.7 全身立绘 — 这里半身像 = 上身至腰)
  const composition = kind === 'head'
    ? `centered isolated headshot on a clean white background, front view, half-body or chest-up portrait, facial expression clearly visible, clear readable silhouette, designed for a small 64x64 portrait icon`
    : `centered isolated half-body portrait on a clean white background, front or slight 3/4 view, upper body from waist up, clear clothing details, readable silhouette, designed for a 192x256 character portrait`

  // 服装(§8.4 真实德国留学,不幻想)
  const clothing = `casual jacket or hoodie or simple coat, muted colors, age-appropriate (${npc.age_band || 'adult'}), non-sexualized, no fantasy costume, no anime uniform`

  // 颜色(§3.1 + §3.2 色板)
  const palette = `color palette: warm parchment beige #EFE2C2, muted Bavarian cream #D8C39B, terracotta roof red #9C4331, moss green #6F8F4E, soft teal copper #4F7F73, antique gold #E8B85C, dark navy shadow #07152B, cool blue window glass #24354F`

  // 表情(§8.5)
  const expression = `expression reflects personality: ${(npc.personality || []).slice(0, 1).join('') || 'warm'} — use eyes, eyebrows, mouth, posture`

  // 背景(§4 白底规则)
  const background = `background: clean white, no gray platform, no checkerboard, no full scene, no text, no UI frame, no poster layout`

  // 负面提示词(§2.3 + §15.1)
  const negative = `Negative: photorealistic photo, 3D render, anime, chibi, generic cartoon, mobile game cartoon, fantasy, sci-fi, cyberpunk, neon, watercolor, oil painting, smooth vector illustration, plastic toy look, transparent background, checkerboard, gray platform, text, logo, watermark, UI frame, poster layout, blurry edges, soft anti-aliased look, sexy outfit, exaggerated expression, fantasy costume`

  return [
    `Subject: ${subject}`,
    ``,
    `Visual style: ${style}`,
    ``,
    `Composition: ${composition}`,
    ``,
    `Clothing: ${clothing}`,
    ``,
    `Expression: ${expression}`,
    ``,
    `${palette}`,
    ``,
    `Background: ${background}`,
    ``,
    negative,
  ].join('\n')
}



/**
 * AI 生成头像或半身像:
 *   1. 调 /api/generate/image → 写到 staging 目录
 *   2. fetch 图片转 dataURL
 *   3. 上传到 game assets(npc_head / npc_half)
 *   4. 立即用 URL 显示在 editing 里
 */
async function runPortraitGenerate(kind) {
  if (!editing.value) return
  if (!editing.value.id) { store.error = '请先填 NPC ID'; return }

  // 检查必要字段
  if (!editing.value.name_de && !editing.value.name_zh) {
    store.error = '请先填姓名(中/德)再生成,或先点 🤖 LLM 生成 NPC 信息'
    return
  }

  aiGenerating.value = kind
  store.error = null
  store.log(`✨ AI 生成 ${kind === 'head' ? '头像' : '半身像'} (${store.imageModel})...`)

  try {
    const prompt = buildNpcPortraitPrompt(editing.value, kind)
    const filename = `${editing.value.id}_${kind}_gen.png`
    const res = await api.generateImage(prompt, filename, {
      model: store.imageModel,
      promptType: 'npc',
    })

    // fetch staging 图片,转 dataURL
    const imgResp = await fetch(res.url)
    if (!imgResp.ok) throw new Error(`fetch 失败: ${res.url} → ${imgResp.status}`)
    const blob = await imgResp.blob()
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })

    // 上传到 game assets
    const uploadRes = await api.uploadAsset({
      data: dataUrl,
      poiId: editing.value.id,
      assetKind: kind === 'head' ? 'npc_head' : 'npc_half',
    })

    // 更新 editing 显示
    if (kind === 'head') editing.value.head_image = uploadRes.url + '?t=' + cacheBust.value
    else editing.value.half_image = uploadRes.url + '?t=' + cacheBust.value

    store.log(`✅ AI 生成 ${kind} 成功 → ${uploadRes.filename}`)
  } catch (e) {
    store.error = e.message
    store.log(`❌ AI 生成 ${kind} 失败: ${e.message}`)
  } finally {
    aiGenerating.value = null
  }
}


// ── 白底转透明(走 /api/white-to-transparent → scripts/white_to_transparent.py) ──
async function whiteToTransparent(kind) {
  if (!editing.value?.id) return
  transparentizing.value = kind
  store.error = null
  store.log(`🪄 ${kind === 'head' ? '头像' : '半身像'} 去白底中...`)
  try {
    // 从 URL 提取文件名(去掉 ?t=cacheBust)
    const url = kind === 'head' ? editing.value.head_image : editing.value.half_image
    if (!url) return
    const filename = url.split('?')[0].split('/').pop()
    await api.whiteToTransparent({
      filename,
      poiId: editing.value.id,
      assetKind: kind === 'head' ? 'npc_head' : 'npc_half',
    })
    // 强制刷新图(加新 cacheBust)
    cacheBust.value = Date.now()
    const newUrl = `/assets/characters/munich/npc_${editing.value.id}/${filename}?t=${cacheBust.value}`
    if (kind === 'head') editing.value.head_image = newUrl
    else editing.value.half_image = newUrl
    store.log(`✅ ${kind} 已转透明`)
  } catch (e) {
    store.error = e.message
    store.log(`❌ 去白底失败: ${e.message}`)
  } finally {
    transparentizing.value = null
  }
}


// ── 头像/半身像上传 ──
async function onPortraitUpload(e, kind) {
  const file = e.target.files[0]
  if (!file) return
  const dataUrl = await readAsDataURL(file)
  // 立即用 dataURL 显示
  if (kind === 'head') editing.value.head_image = dataUrl
  else editing.value.half_image = dataUrl
  store.error = null
  try {
    const res = await api.uploadAsset({
      data: dataUrl,
      poiId: editing.value.id,  // 后端会拼 npc_{id}_head.png
      assetKind: kind === 'head' ? 'npc_head' : 'npc_half',
    })
    // 上传成功后用 URL 替换 dataURL(节省内存)
    if (kind === 'head') editing.value.head_image = res.url + '?t=' + cacheBust.value
    else editing.value.half_image = res.url + '?t=' + cacheBust.value
    store.log(`📷 ${kind === 'head' ? '头像' : '半身像'}已上传 → ${res.filename}`)
  } catch (err) {
    store.error = err.message
  } finally {
    e.target.value = ''
  }
}

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
</script>

<style scoped>
/* ════════════════════════════════════════════════════════
   NPC 双列布局(2026-06-27 重设计)
   - 左侧 NPC 列表(垂直堆叠)
   - 右侧 编辑表单(宽)
   ════════════════════════════════════════════════════════ */
.npc-layout {
  display: grid;
  grid-template-columns: minmax(180px, 240px) 1fr;
  gap: 10px;
  min-height: 320px;
}

/* ── 左侧栏 ── */
.npc-sidebar {
  display: flex;
  flex-direction: column;
  background: #12122a;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 6px;
  max-height: 70vh;
}
.npc-sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px 6px;
  border-bottom: 1px solid #1a2a3a;
  margin-bottom: 6px;
}
.npc-sidebar-title {
  font-size: 10px;
  color: var(--gold2);
  font-weight: bold;
  letter-spacing: 0.5px;
}
.npc-sidebar-count {
  font-size: 10px;
  color: var(--text-dim);
  background: var(--navy);
  padding: 1px 6px;
  border-radius: 8px;
}

/* NPC 列表(垂直堆叠) */
.npc-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.npc-card {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 6px;
  cursor: pointer;
  position: relative;
  transition: border-color .15s, background .15s;
  min-width: 0;
}
.npc-card:hover { border-color: var(--gold2); }
.npc-card.active {
  border-color: var(--gold);
  background: var(--navy3);
  box-shadow: inset 2px 0 0 var(--gold);
}

.npc-thumb {
  width: 36px;
  height: 36px;
  background: #0a0a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  border-radius: 2px;
}
.npc-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.npc-info {
  flex: 1;
  min-width: 0;
}
.npc-name {
  font-size: 11px;
  color: var(--gold2);
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}
.npc-name-de {
  font-size: 9px;
  color: var(--text-dim);
  font-style: italic;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}
.npc-role {
  font-size: 9px;
  color: var(--text-dim);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.npc-meta {
  font-size: 8px;
  margin-top: 2px;
  display: flex;
  gap: 6px;
  white-space: nowrap;
}
.npc-del {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  background: rgba(0,0,0,.7);
  color: #ff7777;
  border: 1px solid #ff4444;
  border-radius: 3px;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  display: none;
}
.npc-card:hover .npc-del { display: flex; align-items: center; justify-content: center; }
.npc-del:hover { background: #ff4444; color: #fff; }

/* 空状态(NPC 列表空) */
.npc-empty {
  text-align: center;
  padding: 30px 12px;
}

/* ── 右侧主区 ── */
.npc-main {
  display: flex;
  flex-direction: column;
  background: #12122a;
  border: 1px solid var(--border);
  border-radius: 3px;
  min-width: 0;
}

/* 表单空状态(没选中 NPC) */
.npc-form-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* ── 表单 ── */
.npc-form {
  background: #12122a;
  border: 1px solid var(--gold);
  padding: 10px 12px;
  margin-top: 8px;
}

/* ── NPC ID + 头像 + 半身像 — 同一行 ── */
.npc-id-portraits {
  display: grid;
  grid-template-columns: 1fr auto auto;   /* NPC ID 占剩余,头像/半身像固定宽 */
  gap: 12px;
  align-items: start;
  margin-bottom: 8px;
}
.npc-id-wrap {
  display: flex;
  flex-direction: column;
}
.npc-id-wrap label {
  font-size: 9px;
  color: var(--gold2);
  margin-bottom: 4px;
}
.npc-id-wrap input {
  padding: 6px 8px;
  background: #0a0a1a;
  color: var(--gold2);
  border: 1px solid var(--border);
  font-size: 11px;
  font-family: inherit;
  width: 100%;
}
.npc-id-wrap input:focus {
  outline: none;
  border-color: var(--gold);
}
.npc-id-wrap input:disabled {
  opacity: 0.5;
}
.npc-portrait-cell {
  display: flex;
  flex-direction: column;
}
.npc-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  color: var(--gold2);
  font-size: 11px;
  font-weight: bold;
}
.npc-form-actions {
  display: flex;
  gap: 4px;       /* 按钮之间 4px */
  align-items: center;
}
.field {
  margin-bottom: 6px;
}
.field label {
  display: block;
  font-size: 9px;
  color: var(--gold2);
  margin-bottom: 2px;
}
.field label .hint {
  color: var(--text-dim);
  font-weight: normal;
  margin-left: 4px;
}
.field input, .field textarea, .field select {
  width: 100%;
  padding: 5px 7px;
  background: #0a0a1a;
  color: var(--gold2);
  border: 1px solid var(--border);
  font-size: 10px;
  font-family: inherit;
}
.field input:focus, .field textarea:focus, .field select:focus {
  outline: none;
  border-color: var(--gold);
}
.field input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.field textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.4;
}

.btn.mini {
  padding: 3px 8px;
  font-size: 9px;
  display: inline-block;
}

/* AI 图像模型选择条 */
.model-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #12122a;
  border: 1px solid var(--border);
  padding: 4px 8px;
  margin-bottom: 10px;
}
.btn.danger {
  background: #4a1f1f;
  color: #ff8888;
  border-color: #ff4444;
}

/* ── 头像/半身像预览 ── */
/* 固定像素 + aspect-ratio,跟生成目标 64×64 / 192×256 一致 */
/* 96×96 是 64×64 的 1.5x 预览,96×128 是 192×256 的 0.5x 预览 */
.npc-portrait {
  width: 96px;
  height: 96px;                    /* 头像 1:1 → 对应 64×64 生成目标 */
  background: #0a0a1a;
  border: 1px dashed var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin: 0 auto;                  /* 居中 */
}
.npc-portrait.half {
  width: 96px;
  height: 128px;                   /* 半身像 3:4 → 对应 192×256 生成目标 */
}
.npc-portrait.filled {
  border-style: solid;
  border-color: var(--gold);
}
.npc-portrait img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  image-rendering: pixelated;      /* 像素图近看用 nearest-neighbor */
}
</style>
