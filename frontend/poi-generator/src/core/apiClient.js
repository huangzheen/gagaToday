/**
 * API 客户端 — 调用后端 FastAPI
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
    throw new Error(msg)
  }
  return res.json()
}

export const api = {
  // ── 文本生成 ──
  generateText(prompt, systemPrompt = null, model = 'qwen-plus') {
    return request('POST', '/generate/text', { prompt, system_prompt: systemPrompt, model })
  },

  generateJson(prompt, systemPrompt = null, model = 'qwen3-max') {
    return request('POST', '/generate/json', { prompt, system_prompt: systemPrompt, model })
  },

  // ── 图片生成 ──
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

  // ── 模型列表 ──
  getImageModels() {
    return request('GET', '/generate/models')
  },

  // ── 保存 ──
  saveJson(data, relativePath, poiId = null, city = 'munich') {
    return request('POST', '/save/json', { data, relative_path: relativePath, poi_id: poiId, city })
  },

  saveImage(sourcePath, poiId, subfolder = 'exterior', filename = null, city = 'munich') {
    return request('POST', '/save/image', { source_path: sourcePath, poi_id: poiId, subfolder, filename, city })
  },

  saveSource(records, poiId = null, city = 'munich') {
    return request('POST', '/save/source', { records, poi_id: poiId, city })
  },

  // ── 批量保存 ──
  savePackage(files, poiId, city = 'munich', dateSuffix = null, sourceRecords = null) {
    return request('POST', '/save/package', {
      files,
      poi_id: poiId,
      city,
      date_suffix: dateSuffix,
      source_records: sourceRecords,
    })
  },

  // ── POI 查询 ──
  listPois(city = 'munich') {
    return request('GET', `/pois?city=${city}`)
  },

  getPoi(poiId, city = 'munich') {
    return request('GET', `/pois/${poiId}?city=${city}`)
  },
}
