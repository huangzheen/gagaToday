<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">🖼️ 场景图片生成</h3>
    <p style="font-size:10px;color:var(--text-dim);margin-bottom:10px">
      16-bit 像素风格 · 分辨率 1280×720
    </p>

    <!-- 模型选择器 -->
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;background:var(--navy);padding:8px;border:1px solid var(--gold);">
      <label style="font-size:10px;color:var(--gold);white-space:nowrap">🎨 生图模型:</label>
      <select v-model="store.imageModel" style="flex:1;font-size:10px;padding:4px;background:#0a0a1a;color:var(--gold2);border:1px solid var(--border)">
        <option v-for="m in store.availableImageModels" :key="m.id" :value="m.id" :disabled="m.status === 'no_key'">
          {{ m.status === 'no_key' ? '🔒' : '✅' }} {{ m.provider }} · {{ m.name }}
        </option>
      </select>
    </div>

    <div class="card-grid">
      <!-- 外观图 -->
      <div v-for="img in exteriorImages" :key="img.id" class="card">
        <h4>{{ img.label }}</h4>
        <div class="img-preview">
          <span v-if="!img.url">{{ img.desc }}</span>
          <img v-else :src="img.url" :alt="img.label" />
        </div>
        <div class="card-actions">
          <button class="btn" @click="generateExterior(img)" :disabled="store.isGenerating">
            🎨 生成
          </button>
          <span v-if="img.url" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <hr style="border-color:var(--border);margin:14px 0" />

    <div class="card-grid">
      <!-- 内部图 -->
      <div v-for="img in interiorImages" :key="img.id" class="card">
        <h4>{{ img.label }}</h4>
        <div class="img-preview">
          <span v-if="!img.url">{{ img.desc }}</span>
          <img v-else :src="img.url" :alt="img.label" />
        </div>
        <div class="card-actions">
          <button class="btn" @click="generateInterior(img)" :disabled="store.isGenerating">
            🎨 生成
          </button>
          <span v-if="img.url" class="status-dot ok" style="align-self:center;margin-left:auto" />
        </div>
      </div>
    </div>

    <div style="margin-top:12px">
      <button class="btn primary" @click="generateAllImages">🤖 一键生成所有图片</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'
import { buildSceneImagePrompt } from '@/core/prompts'

const store = useGeneratorStore()
const poiId = computed(() => store.currentPoiId)
import { computed } from 'vue'

const exteriorImages = ref([
  { id: 'spring', label: '🌷 春天', desc: 'Frühling · 樱花/新绿', path: null },
  { id: 'summer', label: '☀️ 夏天', desc: 'Sommer · 蓝天/阳光', path: null },
  { id: 'autumn', label: '🍂 秋天', desc: 'Herbst · 金叶', path: null },
  { id: 'winter', label: '❄️ 冬天', desc: 'Winter · 积雪', path: null },
  { id: 'rainy', label: '🌧️ 暴雨', desc: 'Regen · 阴雨', path: null },
  { id: 'snowy', label: '🌨️ 大雪', desc: 'Schneefall · 大雪纷飞', path: null },
  { id: 'night', label: '🌙 夜景', desc: 'Nacht · 灯光', path: null },
  { id: 'golden_hour', label: '🌅 黄昏', desc: 'Goldene Stunde · 日落', path: null },
])

const interiorImages = ref([
  { id: 'empty', label: '⛪ 空无一人的教堂', desc: 'Leer · 无人', path: null },
  { id: 'faithful', label: '🙏 满是信徒', desc: 'Gläubige · 弥撒时间', path: null },
  { id: 'tourists', label: '📸 满是游客', desc: 'Touristen · 旺季', path: null },
  { id: 'choir', label: '🎵 唱诗班', desc: 'Chor · 演唱', path: null },
  { id: 'altar', label: '✨ 祭坛特写', desc: 'Altar · 近景', path: null },
  { id: 'teufelstritt', label: '👣 魔鬼脚印', desc: 'Teufelstritt · 传说', path: null },
])

const allImages = computed(() => [...exteriorImages.value, ...interiorImages.value])

async function generateExterior(img) {
  const poi = store.currentPoi
  if (!poi) return
  const filename = `exterior_${img.id}.png`
  const desc = buildSceneImagePrompt(poi, { view: 'exterior', extra: img.desc })
  try {
    const res = await api.generateImage(desc, filename, { promptType: 'scene', model: store.imageModel })
    img.url = res.url
    img.path = res.path
    store.log(`✅ 已生成: ${filename} (模型: ${res.model_used || store.imageModel})`)
    // 保存到 assets
    await api.saveImage(res.path, poiId.value, 'exterior', filename)
  } catch (e) {
    store.error = e.message
  }
}

async function generateInterior(img) {
  const poi = store.currentPoi
  if (!poi) return
  const filename = `interior_${img.id}.png`
  const desc = buildSceneImagePrompt(poi, { view: 'interior', extra: img.desc })
  try {
    const res = await api.generateImage(desc, filename, { promptType: 'scene', model: store.imageModel })
    img.url = res.url
    img.path = res.path
    store.log(`✅ 已生成: ${filename} (模型: ${res.model_used || store.imageModel})`)
    await api.saveImage(res.path, poiId.value, 'interior', filename)
  } catch (e) {
    store.error = e.message
  }
}

async function generateAllImages() {
  store.isGenerating = true
  for (const img of allImages.value) {
    if (img.url) continue
    if (exteriorImages.value.includes(img)) {
      await generateExterior(img)
    } else {
      await generateInterior(img)
    }
  }
  store.isGenerating = false
  store.markGenerated('images')
}
</script>
