#!/usr/bin/env node
/**
 * Phase 1+2 smoke test · dev server + FastAPI backend
 *
 * 不依赖浏览器,只验证:
 *   1. dev server 起来
 *   2. index.html 200
 *   3. main.ts 200
 *   4. main.ts 引用的模块都能加载(从 vite client 拉)
 *   5. .env.development 配置的 PMTiles URL 走 8081 老 server
 *   6. Phase 2 FastAPI 后端可达(通过 vite proxy 转发)
 *   7. ETag 协商:200 + ETag header,带 If-None-Match 后 304
 *
 * 真实地图渲染需要 chromium(用 playwright/chrome headless),留给用户浏览器手测。
 *
 * 用法:
 *   node scripts/phase1-smoke.mjs
 */

import http from 'node:http'
import { readFileSync, existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

const DEV_URL = process.env.SMOKE_DEV_URL ?? 'http://127.0.0.1:5185'
const ENV_FILE = resolve(ROOT, '.env.development')

let pass = 0
let fail = 0
const failures = []

function ok(msg) { pass++; console.log(`  \x1b[32m✓\x1b[0m ${msg}`) }
function bad(msg) { fail++; failures.push(msg); console.log(`  \x1b[31m✗\x1b[0m ${msg}`) }

function get(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = ''
      res.on('data', (c) => (data += c))
      res.on('end', () => resolve({ status: res.statusCode ?? 0, headers: res.headers, body: data }))
    }).on('error', reject)
  })
}

function getRaw(url, headers = {}) {
  return new Promise((resolve, reject) => {
    http.get(url, { headers }, (res) => {
      let data = ''
      res.on('data', (c) => (data += c))
      res.on('end', () => resolve({ status: res.statusCode ?? 0, headers: res.headers, body: data }))
    }).on('error', reject)
  })
}

function head(url) {
  return new Promise((resolve, reject) => {
    http.get(url, { method: 'HEAD' }, (res) => {
      res.resume()
      resolve({ status: res.statusCode ?? 0, headers: res.headers })
    }).on('error', reject)
  })
}

async function main() {
  console.log(`\n[smoke] Phase 1+2 dev server + FastAPI smoke test`)
  console.log(`[smoke] target: ${DEV_URL}\n`)

  // ── 1. .env.development 配置存在且可解析 ──
  if (!existsSync(ENV_FILE)) {
    bad(`.env.development 不存在: ${ENV_FILE}`)
  } else {
    const env = readFileSync(ENV_FILE, 'utf-8')
    const pmtilesMatch = env.match(/^VITE_PMTILES_URL=(.+)$/m)
    if (!pmtilesMatch) {
      bad('VITE_PMTILES_URL 未配置')
    } else {
      ok(`VITE_PMTILES_URL = ${pmtilesMatch[1].trim()}`)
    }
  }

  // ── 2. dev server 起来 ──
  let index
  try {
    index = await get(DEV_URL + '/')
    if (index.status === 200) ok(`GET / → 200 (${index.body.length} bytes)`)
    else bad(`GET / → ${index.status}`)
  } catch (e) {
    bad(`dev server 不可达: ${e.message}`)
    console.log(`\n  提示: 在另一个终端跑 \`cd frontend/game-client && npx vite\``)
    return finish()
  }

  // ── 3. index.html 含 #app 挂载点 ──
  if (index.body.includes('<div id="app">') && index.body.includes('main.ts')) {
    ok('index.html 含 #app 挂载点 + main.ts 入口')
  } else {
    bad('index.html 缺关键节点')
  }

  // ── 4. main.ts 自身可加载 ──
  const mainTs = await get(DEV_URL + '/src/main.ts')
  if (mainTs.status === 200 && mainTs.body.includes('createApp')) {
    ok(`GET /src/main.ts → 200 (${mainTs.body.length} bytes)`)
  } else {
    bad(`GET /src/main.ts → ${mainTs.status}`)
  }

  // ── 5. 关键模块能加载(vite 转译后的 ESM) ──
  // 注: types.ts 只有 export type,转译后 0 bytes — 这是正常的
  const modules = [
    { path: '/src/App.vue', allowEmpty: false },
    { path: '/src/components/MapView.vue', allowEmpty: false },
    { path: '/src/components/HUD.vue', allowEmpty: false },  // Phase 3
    { path: '/src/components/PoiDialog.vue', allowEmpty: false },  // Phase 3 / Phase 4 dialogue
    { path: '/src/store/player.ts', allowEmpty: false },  // Phase 3 / Phase 4 dialogue state
    { path: '/src/composables/useGameClock.ts', allowEmpty: false },  // Phase 3
    { path: '/src/api/bundle.ts', allowEmpty: false },
    { path: '/src/map/createMap.ts', allowEmpty: false },
    { path: '/src/map/mapStyle.ts', allowEmpty: false },
    { path: '/src/map/types.ts', allowEmpty: true },
    { path: '/src/schemas/content.ts', allowEmpty: false },
    { path: '/src/schemas/save.ts', allowEmpty: false },  // Phase 3 扩展
    { path: '/src/data/munich-bundle.json', allowEmpty: false },
    { path: '/src/data/phase4-fixture.ts', allowEmpty: false },  // Phase 4 fixture
    { path: '/src/core/dialogueEngine.ts', allowEmpty: false },  // Phase 4
    { path: '/src/core/rewardEngine.ts', allowEmpty: false },  // Phase 4
    { path: '/src/core/questEngine.ts', allowEmpty: false },  // Phase 4
  ]
  for (const { path: m, allowEmpty } of modules) {
    const r = await get(DEV_URL + m)
    if (r.status === 200 && (allowEmpty || r.body.length > 0)) {
      ok(`GET ${m} → 200 (${r.body.length} bytes${allowEmpty ? ', 纯类型' : ''})`)
    } else {
      bad(`GET ${m} → ${r.status} (${r.body.length} bytes)`)
    }
  }

  // ── 5b. MapView.vue 含自定义控件按钮的 6 个 data-testid ──
  const mapViewSrc = await get(DEV_URL + '/src/components/MapView.vue')
  if (mapViewSrc.status === 200) {
    const expectedTestids = [
      'zoom-in', 'zoom-out',
      'pan-up', 'pan-down', 'pan-left', 'pan-right',
    ]
    let missing = []
    for (const tid of expectedTestids) {
      // vue-tsc 把模板编译成 JS 对象,属性是 "data-testid": "xxx"
      if (!mapViewSrc.body.includes(`"data-testid": "${tid}"`)) missing.push(tid)
    }
    if (missing.length === 0) {
      ok(`MapView 含 6 个控件按钮 (zoom×2 + pan×4)`)
    } else {
      bad(`MapView 缺控件按钮: ${missing.join(', ')}`)
    }
    // 也验证 panBy / zoomBy / easeTo 函数在编译后的代码里出现
    const fnsPresent = ['panBy', 'zoomBy', 'easeTo'].every((fn) => mapViewSrc.body.includes(fn))
    if (fnsPresent) ok('MapView 含 panBy / zoomBy / easeTo 函数')
    else bad('MapView 缺关键函数 (panBy/zoomBy/easeTo)')
  } else {
    bad(`MapView 源码不可读: ${mapViewSrc.status}`)
  }

  // ── 5c. App.vue 含 Phase 2 fetch 调用 + contentVersion 显示 ──
  const appSrc = await get(DEV_URL + '/src/App.vue')
  if (appSrc.status === 200) {
    const hasFetch = appSrc.body.includes('fetchCityBundle')
    const hasCv = appSrc.body.includes('contentVersion')
    const hasFallback = appSrc.body.includes('fallback')
    const hasPlayerStore = appSrc.body.includes('usePlayerStore')
    const hasHud = appSrc.body.includes('HUD')
    const hasDialog = appSrc.body.includes('PoiDialog')
    const hasQuestCompleted = appSrc.body.includes('onQuestCompleted')
    if (hasFetch && hasCv && hasFallback && hasPlayerStore && hasHud && hasDialog && hasQuestCompleted) {
      ok('App.vue 含 fetchCityBundle + contentVersion + fallback + player store + HUD + PoiDialog + quest-completed')
    } else {
      const missing = []
      if (!hasFetch) missing.push('fetchCityBundle')
      if (!hasCv) missing.push('contentVersion')
      if (!hasFallback) missing.push('fallback')
      if (!hasPlayerStore) missing.push('usePlayerStore')
      if (!hasHud) missing.push('HUD')
      if (!hasDialog) missing.push('PoiDialog')
      if (!hasQuestCompleted) missing.push('quest-completed')
      bad(`App.vue 缺关键标记: ${missing.join(', ')}`)
    }
  } else {
    bad(`App.vue 源码不可读: ${appSrc.status}`)
  }

  // ── 5d. Phase 4: PoiDialog 含 dialogue mode + dialogueEngine 调用 ──
  const poiDialogSrc = await get(DEV_URL + '/src/components/PoiDialog.vue')
  if (poiDialogSrc.status === 200) {
    const hasDialogueMode = poiDialogSrc.body.includes('currentDialogue') && poiDialogSrc.body.includes('dialogue-header')
    const hasChooseNode = poiDialogSrc.body.includes('chooseNode') && poiDialogSrc.body.includes('onChoose')
    const hasQuestHook = poiDialogSrc.body.includes('tryCompleteQuest')
    const hasExpose = poiDialogSrc.body.includes('openDialogueForCurrentPoi')
    if (hasDialogueMode && hasChooseNode && hasQuestHook && hasExpose) {
      ok('PoiDialog 含 dialogue mode + chooseNode + tryCompleteQuest + exposed ref')
    } else {
      const missing = []
      if (!hasDialogueMode) missing.push('dialogue mode')
      if (!hasChooseNode) missing.push('chooseNode')
      if (!hasQuestHook) missing.push('tryCompleteQuest')
      if (!hasExpose) missing.push('openDialogueForCurrentPoi')
      bad(`PoiDialog 缺 Phase 4 标记: ${missing.join(', ')}`)
    }
  } else {
    bad(`PoiDialog 源码不可读: ${poiDialogSrc.status}`)
  }

  // ── 6. PMTiles server (8081) 仍可达 + Range 206 ──
  // .env.development 里写的 URL
  const envContent = readFileSync(ENV_FILE, 'utf-8')
  const pmtilesUrl = envContent.match(/^VITE_PMTILES_URL=(.+)$/m)?.[1].trim()
  if (pmtilesUrl) {
    try {
      const u = new URL(pmtilesUrl)
      // 验证 server 在
      const live = await head(`${u.protocol}//${u.host}/`)
      if (live.status === 200 || live.status === 206) {
        ok(`PMTiles server 活着: ${u.host}`)
      } else {
        bad(`PMTiles server 异常: ${u.host} → ${live.status}`)
      }
      // Range 请求
      const range = await new Promise((resolve, reject) => {
        http.get(pmtilesUrl, { headers: { Range: 'bytes=0-1023' } }, (res) => {
          res.resume()
          resolve({ status: res.statusCode ?? 0, headers: res.headers })
        }).on('error', reject)
      })
      if (range.status === 206 && range.headers['content-range']) {
        ok(`PMTiles Range 206: ${range.headers['content-range']}`)
      } else {
        bad(`PMTiles Range → ${range.status}`)
      }
    } catch (e) {
      bad(`PMTiles URL 解析失败: ${e.message}`)
    }
  }

  // ── 7. Phase 2: FastAPI 后端(via vite proxy)──
  // GET /api/game/v1/cities
  const citiesRes = await getRaw(DEV_URL + '/api/game/v1/cities')
  if (citiesRes.status === 200) {
    try {
      const data = JSON.parse(citiesRes.body)
      const hasMunich = data.cities?.some((c) => c.id === 'munich')
      if (hasMunich) {
        ok('Phase 2: /api/game/v1/cities 返回 munich(经 vite proxy → 8000)')
      } else {
        bad(`Phase 2: cities 缺 munich: ${citiesRes.body.slice(0, 100)}`)
      }
    } catch (e) {
      bad(`Phase 2: cities JSON parse: ${e.message}`)
    }
  } else {
    bad(`Phase 2: cities → ${citiesRes.status}(后端可能没启,uivcorn 8000)`)
  }

  // ── 7b. Phase 2: GET /api/game/v1/cities/munich/bundle + ETag ──
  const bundleRes = await getRaw(DEV_URL + '/api/game/v1/cities/munich/bundle')
  if (bundleRes.status === 200) {
    const etag = bundleRes.headers['etag']
    const cv = bundleRes.headers['x-content-version']
    if (etag && cv) {
      ok(`Phase 2: bundle → 200 + ETag=${etag} + cv=${cv}`)
    } else {
      bad(`Phase 2: bundle 200 但缺 headers(etag=${etag}, cv=${cv})`)
    }

    // ── 7c. Phase 2: If-None-Match → 304 ──
    const notModified = await getRaw(
      DEV_URL + '/api/game/v1/cities/munich/bundle',
      { 'If-None-Match': etag ?? '' },
    )
    if (notModified.status === 304) {
      ok(`Phase 2: If-None-Match 匹配 → 304(0 bytes body)`)
    } else {
      bad(`Phase 2: If-None-Match → ${notModified.status}(期望 304)`)
    }
  } else {
    bad(`Phase 2: bundle → ${bundleRes.status}`)
  }

  // ── 8. Phase 3: /assets 静态资源(vite proxy → FastAPI StaticFiles)──
  // PoiDialog 加载 scene 图 + audio,必须能正常拿到 image/png 和 audio/mpeg
  // 如果 vite dev fallback 到 SPA HTML,Content-Type 会是 text/html → 图片显示不出来
  const assetChecks = [
    { path: '/assets/scenes/munich/frauenkirche/_reference/ref_frauenkirche.png', expectType: 'image/png', label: 'frauenkirche 主图' },
    { path: '/assets/scenes/munich/marienplatz/_reference/ref_marienplatz.png', expectType: 'image/png', label: 'marienplatz 主图' },
    { path: '/assets/scenes/munich/munchen_hauptbahnhof/audio/intro_de.mp3', expectType: 'audio/mpeg', label: '中央火车站 de 音频' },
  ]
  for (const { path: p, expectType, label } of assetChecks) {
    const r = await new Promise((resolve, reject) => {
      http.get(DEV_URL + p, (res) => {
        res.resume()
        resolve({ status: res.statusCode ?? 0, headers: res.headers })
      }).on('error', reject)
    })
    const ct = (r.headers['content-type'] ?? '').toLowerCase()
    if (r.status === 200 && ct.startsWith(expectType)) {
      ok(`Phase 3: ${label} → 200 ${expectType}`)
    } else if (r.status === 200 && ct.startsWith('text/html')) {
      bad(`Phase 3: ${label} → 200 text/html(vite SPA fallback!需修 vite.config.ts proxy)`)
    } else {
      bad(`Phase 3: ${label} → ${r.status} ${ct}(期望 ${expectType})`)
    }
  }

  finish()
}

function finish() {
  console.log(`\n[smoke] 结果: ${pass} 通过, ${fail} 失败`)
  if (fail > 0) {
    console.log('\n失败项:')
    for (const f of failures) console.log('  - ' + f)
    process.exit(1)
  }
  console.log('\n✅ Phase 1+2 smoke 通过')
  console.log('   真实地图渲染请打开浏览器访问 ' + DEV_URL)
  console.log('   (PMTiles 9GB 首次加载需 10-30s,请耐心等地图出现)')
  process.exit(0)
}

main().catch((e) => {
  console.error('[smoke] 未捕获异常:', e)
  process.exit(2)
})