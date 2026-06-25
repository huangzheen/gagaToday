<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">📋 数据预览 & 完整性检查</h3>

    <!-- 完整性检查 -->
    <div style="display:flex;gap:10px;margin-bottom:12px">
      <div v-for="(cnt, section) in completeness" :key="section" class="card" style="flex:1">
        <h4>{{ sectionLabels[section] }}</h4>
        <p style="font-size:20px;color:var(--gold2)">
          {{ cnt.done }}/{{ cnt.total }}
        </p>
        <div class="progress-bar">
          <div class="fill" :style="{ width: (cnt.total > 0 ? (cnt.done / cnt.total * 100) : 0) + '%' }" />
        </div>
      </div>
    </div>

    <!-- 生成日志 -->
    <div style="margin-bottom:10px">
      <h4 style="color:var(--gold);font-size:10px;margin-bottom:4px">📜 生成日志</h4>
      <div class="json-viewer" style="max-height:150px">
        <div v-for="(line, i) in store.generationLog" :key="i">{{ line }}</div>
        <div v-if="store.generationLog.length === 0" style="color:var(--text-dim)">暂无日志</div>
      </div>
    </div>

    <!-- JSON 数据预览 -->
    <div v-for="(data, key) in store.poiData" :key="key" style="margin-bottom:8px">
      <h4 style="color:var(--gold);font-size:10px;margin-bottom:4px">{{ key }}</h4>
      <div class="json-viewer">{{ JSON.stringify(data, null, 2).slice(0, 500) }}...</div>
    </div>

    <div v-if="Object.keys(store.poiData).length === 0" style="text-align:center;padding:30px;color:var(--text-dim)">
      ⭐ 点击"一键生成全部"开始内容生产
    </div>

    <!-- 导出按钮 -->
    <div style="margin-top:12px;display:flex;gap:8px">
      <button class="btn primary" @click="exportAll">💾 导出所有数据</button>
      <button class="btn success" @click="exportToGame">🎮 导出到游戏 content</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'

const store = useGeneratorStore()

const sectionLabels = {
  info: '基础信息',
  images: '图片',
  npc: 'NPC',
  dialogue: '对话',
  knowledge: '知识卡',
  quests: '剧情',
  checkin: '打卡',
  refworkflow: '定妆照→变体',
}

const completeness = computed(() => {
  const sections = ['info', 'images', 'npc', 'dialogue', 'knowledge', 'quests', 'checkin', 'refworkflow']
  const result = {}
  for (const s of sections) {
    result[s] = {
      done: store.generated[s] ? 1 : 0,
      total: 1,
    }
  }
  return result
})

async function exportAll() {
  const poi = store.currentPoi
  store.log(`💾 导出 ${poi.name_zh} 所有数据到 drafts...`)
  const files = []

  if (store.poiData.info) {
    files.push({ relative_path: 'poi_info.draft.json', data: store.poiData.info })
  }
  if (store.poiData.npc_profiles) {
    files.push({ relative_path: 'npc_profiles.draft.json', data: store.poiData.npc_profiles })
  }
  if (store.poiData.dialogues) {
    files.push({ relative_path: 'dialogues.draft.json', data: store.poiData.dialogues })
  }
  if (store.poiData.dialogue_hooks) {
    files.push({ relative_path: 'npc_dialogue_hooks.draft.json', data: store.poiData.dialogue_hooks })
  }
  if (store.poiData.knowledge_cards) {
    files.push({ relative_path: 'knowledge_cards.draft.json', data: store.poiData.knowledge_cards })
  }
  if (store.poiData.quests) {
    files.push({ relative_path: 'quests.draft.json', data: store.poiData.quests })
  }
  if (store.poiData.checkin_targets) {
      files.push({ relative_path: 'checkin_targets.draft.json', data: store.poiData.checkin_targets })
    }
    if (store.poiData.scene_events) {
      files.push({ relative_path: 'scene_events.draft.json', data: store.poiData.scene_events })
  }
  if (store.poiData.source_records) {
    files.push({ relative_path: 'source_records.json', data: store.poiData.source_records })
  }

  if (files.length === 0) {
    store.log('⚠️ 没有可导出的数据')
    return
  }

  try {
    const res = await api.savePackage(files, store.currentPoiId, 'munich')
    const saved = res.saved_files || []
    store.log(`✅ 导出完成: ${saved.length} 个文件已写入 drafts 目录`)
    for (const p of saved) {
      store.log(`   📄 ${p}`)
    }
  } catch (e) {
    store.error = e.message
    store.log(`❌ 导出失败: ${e.message}`)
  }
}

async function exportToGame() {
  store.log('🎮 导出到游戏 content 目录（需要人工审核）')
  store.log('💡 请手动将 drafts 文件移到 content/munich/')
}
</script>
