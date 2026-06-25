<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <h3 style="color:var(--gold2)">📍 打卡目标生成</h3>
      <button class="btn primary" @click="generateAll" :disabled="store.isGenerating" style="padding:5px 12px">
        {{ store.isGenerating ? '⏳ 生成中…' : '🤖 一键生成全部打卡' }}
      </button>
    </div>

    <div class="card-grid">
      <div v-for="(item, i) in checkinItems" :key="i" class="card">
        <h4>{{ item.title }}</h4>
        <p style="font-size:9px">
          类型: {{ item.type }} · 奖励: {{ item.rewardDesc }}
        </p>
        <div class="card-actions">
          <button class="btn" @click="generateItem(item)">📝 生成</button>
          <span v-if="item.done" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <div style="margin-top:12px">
      <button class="btn primary" @click="generateAll">🤖 一键生成全部打卡</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'
import { buildCheckinPrompt } from '@/core/prompts'

const store = useGeneratorStore()

const poiId = computed(() => store.currentPoiId)

const checkinItems = ref([
  { id: 'c1', title: '?', type: 'location', rewardDesc: 'culture_xp:3, mood:1', done: false },
  { id: 'c2', title: '?', type: 'physical', rewardDesc: 'culture_xp:5, energy:-5', done: false },
  { id: 'c3', title: '?', type: 'photo',    rewardDesc: 'mood:3', done: false },
])

async function generateItem(item) {
  const poi = store.currentPoi
  const prompt = buildCheckinPrompt(poi, store.osmData, item)

  try {
    const res = await api.generateJson(prompt)
    item.data = res.data
    item.done = true
    // 存入 store
    store.appendPoiData('checkin_targets', res.data)
    store.log(`✅ 已生成打卡: ${item.title}`)
  } catch (e) {
    store.error = e.message
  }
}

async function generateAll() {
  store.isGenerating = true
  for (const item of checkinItems.value) {
    if (item.done) continue
    await generateItem(item)
  }
  store.isGenerating = false
  store.markGenerated('checkin')
}
</script>
