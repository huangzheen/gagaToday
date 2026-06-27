/**
 * API 客户端 — 调用后端 FastAPI
 *
 * 当前只暴露 RefWorkflow + POIInfoForm 实际用到的接口:
 * - generateImage: RefWorkflow 定妆照/变体
 * - getImageModels: store.checkBackend 拉模型列表
 * - saveImage: RefWorkflow 保存变体到 game assets
 * - saveJson: POIInfoForm 保存基础信息到 drafts
 */

const API_BASE = '/api'

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) {
    // 去掉 null/undefined 字段，避免 Pydantic 422
    const clean = {}
    for (const [k, v] of Object.entries(body)) {
      if (v !== null && v !== undefined) clean[k] = v
    }
    opts.body = JSON.stringify(clean)
  }

  const res = await fetch(`${API_BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    let msg = err.detail || `HTTP ${res.status}`
    if (Array.isArray(msg)) msg = msg.map(e => e.msg || JSON.stringify(e)).join('; ')
    const e = new Error(msg)
    e.status = res.status
    throw e
  }
  // DELETE 可能返回 204 No Content
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  // ── 文本生成 (LLM JSON, NPC 一键生成等) ──
  generateJson(prompt, systemPrompt = null, model = 'qwen3-max') {
    return request('POST', '/generate/json', { prompt, system_prompt: systemPrompt, model })
  },

  // ── 文本生成 (LLM 自由文本,场景介绍/NPC 描述等) ──
  generateText(prompt, systemPrompt = null, model = null) {
    return request('POST', '/generate/text', {
      prompt,
      system_prompt: systemPrompt,
      model: model || 'qwen-plus',
    })
  },

  // ── 场景介绍抓取 (Wikipedia → Wikidata → Brave Search → LLM) ──
  fetchWikiIntro(nameDe, nameZh = null) {
    return request('POST', '/wiki/intro', {
      name_de: nameDe,
      name_zh: nameZh,
    })
  },

  // ── 图片生成 (RefWorkflow) ──
  generateImage(description, outputName, opts = {}) {
    return request('POST', '/generate/image', {
      description,
      output_name: outputName,
      model: opts.model || 'minimax',
      aspect_ratio: opts.aspectRatio || '16:9',
      resolution: opts.resolution || '1K',
      target_dir: opts.targetDir || null,
      prompt_type: opts.promptType || 'scene',
    })
  },

  // ── 模型列表 (store.checkBackend) ──
  getImageModels() {
    return request('GET', '/generate/models')
  },

  // ── 保存 (POIInfoForm: drafts JSON / RefWorkflow: game assets) ──
  saveJson(data, relativePath, poiId = null, city = 'munich') {
    return request('POST', '/save/json', { data, relative_path: relativePath, poi_id: poiId, city })
  },

  // ── 读取已保存的 JSON(draft 优先,fallback 正式目录) ──
  loadJson(relativePath, poiId = null, city = 'munich', isDraft = true) {
    const qs = new URLSearchParams({ relative_path: relativePath, city, is_draft: String(isDraft) })
    if (poiId) qs.set('poi_id', poiId)
    return request('GET', `/save/json?${qs}`)
  },

  saveImage(sourcePath, poiId, subfolder = 'exterior', filename = null, city = 'munich') {
    return request('POST', '/save/image', { source_path: sourcePath, poi_id: poiId, subfolder, filename, city })
  },

  // ── 上传(直存 game assets,文件名由后端自动决定) ──
  // assetKind: "scene_main"(多张) | "icon"(单张) | "npc_head" | "npc_half"
  // 对 npc_*: poiId 传 npc_id 主体(如 "frauenkirche_pfarrer"),后端自动拼 npc_{poiId}_head.png
  uploadAsset({ data, poiId, assetKind, city = 'munich' }) {
    return request('POST', '/upload-asset', {
      data, poi_id: poiId, asset_kind: assetKind, city,
    })
  },

  // ── 列出已上传资源(用于刷新/初次加载) ──
  listAssets({ poiId, assetKind, city = 'munich' }) {
    return request('GET', `/list-assets?poi_id=${poiId}&asset_kind=${assetKind}&city=${city}`)
  },

  // ── 删除已上传资源 ──
  deleteAsset({ filename, poiId, assetKind, city = 'munich' }) {
    return request('DELETE', '/upload-asset', { filename, poi_id: poiId, asset_kind: assetKind, city })
  },

  // ── POI 内容读写(NPC 等) ──
  // getPoi(poiId, { includeContent: true }) → 后端返回 poi.content.npc 等
  getPoi(poiId, { includeContent = false, city = 'munich' } = {}) {
    const qs = new URLSearchParams({ city, include_content: String(includeContent) })
    return request('GET', `/v2/pois/${poiId}?${qs}`)
  },

  // 写入 NPC 列表(JSON 数组)到 poi_content 表
  saveNpcContent(poiId, data, city = 'munich') {
    return request('POST', '/save/npc-content', { poi_id: poiId, data, city })
  },

  // ── 把白底 PNG 转透明底(走 scripts/white_to_transparent.py) ──
  whiteToTransparent({ filename, poiId, assetKind, city = 'munich' }) {
    return request('POST', '/white-to-transparent', {
      filename, poi_id: poiId, asset_kind: assetKind, city,
    })
  },
}
