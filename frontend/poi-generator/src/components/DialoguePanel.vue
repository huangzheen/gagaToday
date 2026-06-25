<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <h3 style="color:var(--gold2)">💬 对话树生成</h3>
      <button class="btn primary" @click="generateAll" :disabled="store.isGenerating" style="padding:5px 12px">
        {{ store.isGenerating ? '⏳ 生成中…' : '🤖 一键生成全部对话' }}
      </button>
    </div>

    <div class="card-grid">
      <div v-for="(hook, i) in dialogueHooks" :key="i" class="card">
        <h4>{{ hook.label }}</h4>
        <p style="font-size:9px">{{ hook.desc }}</p>
        <p style="font-size:9px;color:var(--gold)">
          难度: {{ hook.difficulty }} · {{ hook.trigger }}
        </p>
        <div class="card-actions">
          <button class="btn" @click="generateDialogue(hook)">📝 生成对话</button>
          <span v-if="hook.done" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <div style="margin-top:12px">
      <button class="btn primary" @click="generateAll">🤖 一键生成全部对话</button>
    </div>

    <div v-if="previewDialogue" style="margin-top:12px">
      <h4 style="color:var(--gold);font-size:10px;margin-bottom:4px">对话预览</h4>
      <div class="json-viewer">{{ previewDialogue }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'
import { buildDialoguePrompt } from '@/core/prompts'

const store = useGeneratorStore()
const previewDialogue = ref('')

const poiId = computed(() => store.currentPoiId)

// 6 个通用对话触发场景(LLM 根据 POI 类型填充 label/desc/trigger)
const dialogueHooks = ref([
  { id: 'first_visit',     label: '?', desc: '首次到访时的招呼/简单对话',      trigger: 'first_visit',     done: false },
  { id: 'ask_info',        label: '?', desc: '询问基本信息(时间/价格/方向等)', trigger: 'ask_for_info',     done: false },
  { id: 'ask_directions',  label: '?', desc: '问路/找其他地方',                trigger: 'ask_directions',  done: false },
  { id: 'seasonal_event',  label: '?', desc: '季节性事件(圣诞/啤酒节/特殊展)',  trigger: 'seasonal_event',  done: false },
  { id: 'deep_conversation', label: '?', desc: '深入交流(历史/文化/个人故事)',  trigger: 'deep_talk',        done: false },
  { id: 'special_request', label: '?', desc: '特殊请求(拍照/导览/帮助)',         trigger: 'special_request', done: false },
])

async function generateDialogue(hook) {
  const poi = store.currentPoi
  const prompt = buildDialoguePrompt(poi, store.osmData, hook)
  try {
    const res = await api.generateJson(prompt)
    // LLM 返回的是带 hook_id 的对象数组,可能包了一层 {turns: [...], difficulty: '...'}
    const data = Array.isArray(res.data) ? res.data[0] : res.data
    hook.data = data
    hook.label = data.hook_label || hook.label  // LLM 可能回填
    hook.difficulty = data.difficulty || '?'
    hook.done = true
    previewDialogue.value = JSON.stringify(data, null, 2)
    // 替换 store 里同 hook_id 的
    const existing = store.poiData.dialogues || []
    const idx = existing.findIndex(d => d.hook_id === hook.id)
    const entry = { hook_id: hook.id, label: hook.label, difficulty: hook.difficulty, turns: data.turns || data }
    if (idx >= 0) existing[idx] = entry
    else store.appendPoiData('dialogues', entry)
    store.log(`✅ 已生成对话: ${hook.label} (${hook.difficulty})`)
  } catch (e) {
    store.error = e.message
  }
}

async function generateAll() {
  store.isGenerating = true
  for (const hook of dialogueHooks.value) {
    if (hook.done) continue
    await generateDialogue(hook)
  }
  store.isGenerating = false
  store.markGenerated('dialogue')
}
</script>
