<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">📚 知识卡生成</h3>

    <div class="card-grid">
      <div v-for="(card, i) in knowledgeCards" :key="i" class="card">
        <h4>{{ card.title }}</h4>
        <p style="font-size:9px">类别: {{ card.category }} · {{ card.gameplay_use?.join(', ') }}</p>
        <div class="card-actions">
          <button class="btn" @click="generateCard(card)">📝 生成</button>
          <span v-if="card.done" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <div style="margin-top:12px">
      <button class="btn primary" @click="generateAll">🤖 一键生成全部知识卡</button>
      <button class="btn" style="margin-left:8px" @click="addCard">＋ 添加知识卡</button>
    </div>

    <div v-if="selectedCard?.body" style="margin-top:12px">
      <div style="background:var(--navy);border:2px solid var(--gold);padding:10px">
        <h4 style="color:var(--gold2)">{{ selectedCard.title }}</h4>
        <p style="font-size:11px;margin-top:6px;line-height:1.6">{{ selectedCard.body }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'
import { buildKnowledgePrompt } from '@/core/prompts'

const store = useGeneratorStore()
const selectedCard = ref(null)

const poiId = computed(() => store.currentPoiId)

// 5 张通用知识卡(LLM 根据 POI 类型填充标题和内容)
const knowledgeCards = ref([
  { id: 'k1', title: '?', category: 'Geschichte', gameplay_use: ['knowledge_card'], done: false, body: '' },
  { id: 'k2', title: '?', category: 'Geschichte', gameplay_use: ['knowledge_card'], done: false, body: '' },
  { id: 'k3', title: '?', category: 'Architektur', gameplay_use: ['knowledge_card'], done: false, body: '' },
  { id: 'k4', title: '?', category: 'Legende',    gameplay_use: ['history_qa'], done: false, body: '' },
  { id: 'k5', title: '?', category: 'Kultur',     gameplay_use: ['knowledge_card'], done: false, body: '' },
])

function addCard() {
  knowledgeCards.value.push({ title: '新知识卡', category: 'Kultur', gameplay_use: ['knowledge_card'], done: false, body: '' })
}

async function generateCard(card) {
  const poi = store.currentPoi
  const prompt = buildKnowledgePrompt(poi, store.osmData, card)

  try {
    const res = await api.generateJson(prompt)
    card.body = res.data.body_zh
    card.done = true
    card.data = res.data
    selectedCard.value = card
    // 存入 store
    store.appendPoiData('knowledge_cards', res.data)
    store.log(`✅ 已生成知识卡: ${card.title}`)
  } catch (e) {
    store.error = e.message
  }
}

async function generateAll() {
  store.isGenerating = true
  for (const card of knowledgeCards.value) {
    if (card.done) continue
    await generateCard(card)
  }
  store.isGenerating = false
  store.markGenerated('knowledge')
}
</script>
