<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">🎯 剧情/任务生成</h3>

    <div class="card-grid">
      <div v-for="(quest, i) in quests" :key="i" class="card">
        <h4>{{ quest.title }}</h4>
        <p style="font-size:9px">
          类型: {{ quest.type }} · {{ quest.desc?.slice(0, 60) }}
        </p>
        <div class="card-actions">
          <button class="btn" @click="generateQuest(quest)">📝 生成</button>
          <span v-if="quest.done" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <div style="margin-top:12px">
      <button class="btn primary" @click="generateAll">🤖 一键生成全部任务</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'
import { buildQuestPrompt } from '@/core/prompts'

const store = useGeneratorStore()

const poiId = computed(() => store.currentPoiId)

const quests = ref([
  { id: 'q1', title: '?', type: 'exploration', desc: '?', done: false },
  { id: 'q2', title: '?', type: 'cultural',    desc: '?', done: false },
  { id: 'q3', title: '?', type: 'dialogue',    desc: '?', done: false },
  { id: 'q4', title: '?', type: 'seasonal',    desc: '?', done: false },
])

async function generateQuest(quest) {
  const poi = store.currentPoi
  const prompt = buildQuestPrompt(poi, store.osmData, quest)

  try {
    const res = await api.generateJson(prompt)
    quest.data = res.data
    quest.done = true
    // 存入 store
    store.appendPoiData('quests', res.data)
    store.log(`✅ 已生成任务: ${quest.title}`)
  } catch (e) {
    store.error = e.message
  }
}

async function generateAll() {
  store.isGenerating = true
  for (const quest of quests.value) {
    if (quest.done) continue
    await generateQuest(quest)
  }
  store.isGenerating = false
  store.markGenerated('quests')
}
</script>
