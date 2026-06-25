<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">📍 POI 基础信息</h3>

    <!-- ── 加载/错误状态 ── -->
    <div v-if="loading" style="color:#6a8aaa;font-size:10px;padding:20px;text-align:center">
      🔍 正在从地图提取 OSM 数据...
    </div>
    <div v-else-if="error" style="color:var(--danger);font-size:10px;padding:10px;background:rgba(200,50,50,.15);border:1px solid rgba(200,50,50,.3);margin-bottom:10px">
      ⚠️ {{ error }}
    </div>

    <!-- ── OSM 主 POI 摘要 ── -->
    <div v-if="osm?.primary_poi" class="osm-bar">
      <span class="osm-icon">📍</span>
      <span class="osm-name">{{ osm.primary_poi.name_de }}</span>
      <span class="osm-meta">{{ osm.primary_poi.class }}<span v-if="osm.primary_poi.subclass"> / {{ osm.primary_poi.subclass }}</span></span>
      <span class="osm-dist">{{ osm.primary_poi.distance_m }}m</span>
    </div>

    <!-- ── 游戏内容编辑区 ── -->
    <div style="margin-top:12px">
      <div class="field">
        <label>POI ID</label>
        <input v-model="poiId" disabled />
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="field">
          <label>德语名</label>
          <input v-model="nameDe" :placeholder="osm?.primary_poi?.name_de || ''" />
        </div>
        <div class="field">
          <label>中文名</label>
          <input v-model="nameZh" :placeholder="osm?.primary_poi?.name_zh || ''" />
        </div>
      </div>

      <div class="field">
        <label>类型</label>
        <select v-model="type">
          <option value="church">教堂</option>
          <option value="square">广场</option>
          <option value="museum">博物馆</option>
          <option value="park">公园</option>
          <option value="market">市场</option>
          <option value="castle">城堡/宫殿</option>
          <option value="stadium">体育场</option>
          <option value="school">学校</option>
          <option value="shop">商店</option>
          <option value="library">图书馆</option>
          <option value="home">住所</option>
        </select>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="field">
          <label>纬度</label>
          <input v-model="lat" type="number" step="0.0001" />
        </div>
        <div class="field">
          <label>经度</label>
          <input v-model="lng" type="number" step="0.0001" />
        </div>
      </div>

      <div class="field">
        <label>游戏内角色描述</label>
        <textarea v-model="gameRole" rows="3" placeholder="这个 POI 在游戏中扮演什么角色？"></textarea>
      </div>

      <button class="btn primary" @click="saveInfo" :disabled="saving">
        {{ saving ? '⏳ 保存中...' : '💾 保存基础信息' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'

const store = useGeneratorStore()

const poiId = ref('')
const nameDe = ref('')
const nameZh = ref('')
const type = ref('church')
const lat = ref(0)
const lng = ref(0)
const gameRole = ref('')
const saving = ref(false)

// OSM 数据
const osm = ref(null)
const loading = ref(false)
const error = ref(null)

async function fetchOsmData(latVal, lngVal) {
  if (!latVal || !lngVal) return
  loading.value = true
  error.value = null
  try {
    const resp = await fetch(`/api/osm/extract?lat=${latVal}&lng=${lngVal}`)
    const data = await resp.json()
    if (data.success) {
      osm.value = data
      store.setOsmData(data)  // 共享给其他 tab
      // 自动填入 OSM 数据到游戏字段
      if (!nameDe.value && data.primary_poi?.name_de) nameDe.value = data.primary_poi.name_de
      if (!nameZh.value && data.primary_poi?.name_zh) nameZh.value = data.primary_poi.name_zh
    } else {
      error.value = '地图数据提取失败'
    }
  } catch (e) {
    error.value = `OSM 提取器不可用: ${e.message}`
    // 如果 PMTiles 或后端未运行，仍允许手动编辑
  } finally {
    loading.value = false
  }
}

watch(() => store.currentPoiId, (id) => {
  const poi = store.currentPoi
  if (!poi) return
  poiId.value = poi.id
  nameDe.value = poi.name_de
  nameZh.value = poi.name_zh
  type.value = poi.type
  const newLat = poi.lat || 0
  const newLng = poi.lng || 0
  lat.value = newLat
  lng.value = newLng
  gameRole.value = ''
  osm.value = null
  store.setOsmData(null)
  if (newLat && newLng) {
    fetchOsmData(newLat, newLng)
  }
}, { immediate: true })

async function saveInfo() {
  saving.value = true
  store.error = null
  const data = {
    id: `explore_munich_${poiId.value}`,
    name_de: nameDe.value,
    name_zh: nameZh.value,
    name_en: nameDe.value,
    type: type.value,
    city: 'munich',
    coordinates: { lat: lat.value, lng: lng.value, source: 'manual' },
    visit_duration_minutes: 30,
    student_fit: 'high',
    game_role: gameRole.value,
    osm_data: osm.value ? {
      name_de: osm.value.primary_poi?.name_de,
      name_zh: osm.value.primary_poi?.name_zh,
      class: osm.value.primary_poi?.class,
      subclass: osm.value.primary_poi?.subclass,
      rank: osm.value.primary_poi?.rank,
      building_height: osm.value.building?.render_height,
      building_colour: osm.value.building?.colour,
      transport: osm.value.transport?.slice(0, 3).map(t => t.name),
      roads: osm.value.roads?.slice(0, 3).map(r => r.name),
      all_layers: osm.value.all_layers,
    } : null,
    review_status: 'draft',
  }

  try {
    await api.saveJson(data, 'poi_info.draft.json', poiId.value)
    store.setPoiData('info', data)
    store.log(`✅ 已保存 ${poiId.value} 基础信息`)
    store.markGenerated('info')
  } catch (e) {
    store.error = e.message
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.osm-panel {
  background: rgba(0,0,0,.25);
  border: 1px solid var(--navy3);
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 8px;
}
.osm-header {
  color: var(--gold);
  font-size: 9px;
  letter-spacing: 1px;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--navy3);
}
.osm-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}
.osm-card {
  background: rgba(0,0,0,.2);
  border: 1px solid var(--navy2);
  border-radius: 3px;
  padding: 8px;
}
.osm-card-title {
  color: var(--gold2);
  font-size: 8px;
  letter-spacing: 1px;
  margin-bottom: 4px;
  padding-bottom: 2px;
  border-bottom: 1px solid var(--navy2);
}
.osm-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 0;
  font-size: 9px;
}
.osm-label {
  color: #6a8aaa;
  font-size: 8px;
}
.osm-val {
  color: #aab8bf;
  font-family: monospace;
}
.osm-section {
  margin-bottom: 8px;
}
.osm-section-title {
  color: var(--gold2);
  font-size: 8px;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.osm-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.osm-badge {
  background: rgba(0,0,0,.2);
  border: 1px solid var(--navy2);
  padding: 2px 6px;
  font-size: 8px;
  color: #aab8bf;
  border-radius: 2px;
}
.osm-nearby-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 4px;
  font-size: 8px;
  color: #aab8bf;
  background: rgba(0,0,0,.15);
  border-radius: 2px;
}
</style>
