<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <h3 style="color:var(--gold2)">👤 NPC 生成</h3>
      <button class="btn primary" @click="generateAllNPC" :disabled="store.isGenerating" style="padding:5px 12px">
        {{ store.isGenerating ? '⏳ 生成中…' : '🤖 一键生成全部 NPC' }}
      </button>
    </div>

    <div class="card-grid">
      <div v-for="npc in npcList" :key="npc.id" class="card">
        <h4>{{ npc.role_zh }}</h4>
        <p><strong>{{ npc.name_de }}</strong> · {{ npc.name_zh }}</p>
        <p style="font-size:9px;margin-top:4px">{{ npc.background_zh?.slice(0, 80) }}...</p>
        <div class="card-actions">
          <button class="btn" @click="generateNPCProfile(npc)">📝 生成档案</button>
          <button class="btn" @click="generateNPCPortrait(npc)">🎨 生成立绘</button>
          <span v-if="npc.done" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <div style="margin-top:12px">
      <button class="btn primary" @click="generateAllNPC">🤖 一键生成全部 NPC</button>
    </div>

    <div v-if="rawOutput" style="margin-top:12px">
      <h4 style="color:var(--gold);font-size:10px;margin-bottom:4px">LLM 原始输出</h4>
      <div class="json-viewer">{{ rawOutput }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'
import { buildNPCPrompt } from '@/core/prompts'

const store = useGeneratorStore()
const rawOutput = ref('')

const poiId = computed(() => store.currentPoiId)

// 根据 POI 类型生成对应的 NPC 模板
// 通用骨架:2 个空位 (主理人 + 辅助),名字等字段由 LLM 根据 POI 类型生成
const npcList = ref([
  { id: 'main',    role_zh: '主理人', name_de: '?', name_zh: '?', background_zh: '', done: false },
  { id: 'helper',  role_zh: '辅助 NPC', name_de: '?', name_zh: '?', background_zh: '', done: false },
])

watch(() => store.currentPoiId, () => {
  // 切 POI 时重置 NPC 状态,等用户重新生成
  npcList.value = [
    { id: 'main',   role_zh: '主理人', name_de: '?', name_zh: '?', background_zh: '', done: false },
    { id: 'helper', role_zh: '辅助 NPC', name_de: '?', name_zh: '?', background_zh: '', done: false },
  ]
})

async function generateNPCProfile(npc) {
  const poi = store.currentPoi
  const prompt = buildNPCPrompt(poi, store.osmData, npc.role_zh)
  try {
    const res = await api.generateJson(prompt)
    npc.profile = res.data
    npc.name_de = res.data.name_de
    npc.name_zh = res.data.name_zh
    npc.background_zh = res.data.background_zh
    npc.done = true
    rawOutput.value = JSON.stringify(res.data, null, 2)
    // 替换 store 里同 id 的(避免重复)
    const existing = store.poiData.npc_profiles || []
    const idx = existing.findIndex(n => n.id === res.data.id)
    if (idx >= 0) existing[idx] = res.data
    else store.appendPoiData('npc_profiles', res.data)
    store.log(`✅ 已生成 NPC: ${res.data.name_de} (${res.data.role_zh})`)
  } catch (e) {
    store.error = e.message
  }
}

async function generateNPCPortrait(npc) {
  const desc = `${npc.name_de}, ${npc.role_zh}, 16-bit pixel art character portrait`
  // 暂未实现 — 后续通过 image service 调用
  store.log(`🖼️ 立绘生成待实现: ${npc.name_de}`)
}

async function generateAllNPC() {
  store.isGenerating = true
  for (const npc of npcList.value) {
    if (npc.done) continue
    await generateNPCProfile(npc)
  }
  store.isGenerating = false
  store.markGenerated('npc')
}
</script>
