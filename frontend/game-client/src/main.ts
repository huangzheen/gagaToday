/**
 * gagaToday Game Client 入口
 *
 * Phase 1: 接入 MapLibre + PMTiles,渲染慕尼黑 basemap + POI 标记
 *   - 静态加载 Phase 0 fixture(开发期)
 *   - 真实 PMTiles 数据从 8081 静态服务拉(本地 dev)
 *   - Phase 2 替换 fixture 为运行时 API
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')

console.info('[gagaToday] Game Client booted (Phase 1: MapLibre + PMTiles)')
