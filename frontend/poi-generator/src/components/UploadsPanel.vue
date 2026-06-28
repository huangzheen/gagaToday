<template>
  <div>
    <h3 style="color:var(--gold2);margin-bottom:10px">📤 上传资源</h3>
    <p style="font-size:9px;color:var(--text-dim);margin-bottom:10px">
      上传即保存,无需其他操作。第一张场景图自动作为定妆照(与 RefWorkflow 兼容)。
    </p>

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- 1. 场景图(多张) -->
    <!-- ════════════════════════════════════════════════════════ -->
    <section class="upload-card">
      <div class="upload-card-header">
        <span class="upload-card-title">🖼️ 场景图</span>
        <span class="upload-card-target">
          已上传 <span style="color:var(--gold)">{{ sceneList.length }}</span> 张
        </span>
      </div>
      <p class="upload-card-hint">
        详情面板轮播 / 变体生成基础图。存入 <code>assets/scenes/munich/{{ poiId }}/_reference/</code>。
        第一张自动命名为 <code>ref_{{ poiId }}.png</code>,后续递增 <code>scene_{{ poiId }}_N.png</code>。
      </p>

      <!-- 场景图生成选项(比例 + 分辨率) -->
      <div class="scene-gen-options">
        <span class="scene-gen-label">🎛 场景图生成</span>
        <label>
          <span class="opt-label">比例</span>
          <select v-model="sceneAspect" class="opt-select">
            <option value="16:9">16:9 电影宽屏(剧情原画)</option>
            <option value="4:3">4:3 标准</option>
            <option value="1:1">1:1 方图(地点详情)</option>
            <option value="3:2">3:2 经典</option>
          </select>
        </label>
        <label>
          <span class="opt-label">色板</span>
          <select v-model="sceneBitDepth" class="opt-select">
            <option value="32bit">32-bit 高级(全色域,推荐)</option>
            <option value="16bit">16-bit 复古(SNES 色板)</option>
          </select>
        </label>
        <label>
          <span class="opt-label">分辨率</span>
          <select v-model="sceneResolution" class="opt-select" @change="onResolutionChange">
            <option value="720p">720p · 1280×720(快)</option>
            <option value="1080p">1080p · 1920×1080(推荐)</option>
            <option value="2K">2K · 2560×1440(高质)</option>
            <option value="4K">4K · 3840×2160(超清)</option>
          </select>
        </label>
      </div>

      <!-- AI 生成进度条(常驻指示器,弹窗外也看得到) -->
      <transition name="progress">
        <div v-if="aiGeneratingScene" class="ai-progress">
          <div class="ai-progress-spinner"></div>
          <div class="ai-progress-text">
            <div class="ai-progress-stage">🤖 {{ aiStage }} <span class="ai-progress-model">({{ store.imageModel }})</span></div>
            <div class="ai-progress-bar"><div class="ai-progress-bar-fill"></div></div>
          </div>
        </div>
      </transition>

      <!-- 缩略图网格 + 添加按钮 -->
      <div class="scene-grid">
        <div
          v-for="(img, i) in sceneList"
          :key="img.filename"
          class="scene-thumb"
          :class="{ 'is-primary': i === 0 }"
        >
          <div class="img-wrap">
            <img :src="img.src" :alt="img.filename" @load="onImgLoad($event)" @error="onImgError($event)" />
            <button class="del-btn" title="删除" @click.stop="deleteScene(img, i)">×</button>
            <span v-if="i === 0" class="scene-thumb-badge">主图</span>
          </div>
          <span class="scene-thumb-name">{{ img.filename }}</span>
          <span class="scene-thumb-size">
            {{ formatSize(img.size_bytes) }}
            <span v-if="img.width && img.height" class="scene-thumb-dims"> · {{ img.width }}×{{ img.height }}</span>
          </span>
        </div>

        <!-- 上传卡 → 弹窗选 AI 还是本地上传 -->
        <div class="scene-add" @click="showSceneAddMenu" :class="{ disabled: sceneUploading }">
          <span v-if="sceneUploading">⏳ 上传中...</span>
          <span v-else>＋<br/><small>添加场景图</small></span>
        </div>
        <!-- 隐藏的真实 file input(走本地上传分支) -->
        <input ref="sceneFileInput" type="file" accept="image/*" @change="onSceneUpload" multiple hidden />
      </div>

      <div v-if="sceneMsg" class="upload-msg" :class="{ ok: sceneMsg.startsWith('✅'), err: sceneMsg.startsWith('❌') }">
        {{ sceneMsg }}
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- 2. POI 图标(单张,固定文件名) -->
    <!-- ════════════════════════════════════════════════════════ -->
    <section class="upload-card">
      <div class="upload-card-header">
        <span class="upload-card-title">🎯 POI 图标</span>
        <span class="upload-card-target">→ {{ poiId }}_icon_64.png</span>
      </div>
      <p class="upload-card-hint">
        侧边栏 / 卡片 / 列表里的小图标。存入 <code>assets/icons/munich/</code>。推荐 64×64 PNG(带 alpha 通道)。
      </p>

      <!-- 横向小条:小缩略图 + 文件名 + 替换/删除 -->
      <div class="icon-strip">
        <div v-if="iconUrl" class="icon-thumb">
          <img :src="iconSrc" :alt="poiId + '_icon_64'" />
        </div>
        <div v-else class="icon-thumb icon-thumb-empty">🖼</div>
        <div class="icon-info">
          <div v-if="iconUrl" class="icon-info-name">✅ {{ iconFilename }}</div>
          <div v-else class="icon-info-name" style="color:var(--text-dim)">未上传图标</div>
          <div v-if="iconUrl" class="icon-info-size">{{ formatSize(iconSizeBytes) }}</div>
          <div v-else class="icon-info-size" style="color:var(--text-dim)">推荐 64×64 PNG (带 alpha)</div>
        </div>
        <div class="icon-actions">
          <label class="btn-mini">
            <input type="file" accept="image/*" @change="onIconUpload" hidden />
            <span v-if="iconUploading">⏳</span>
            <span v-else>📁 {{ iconUrl ? '替换' : '上传' }}</span>
          </label>
          <button v-if="iconUrl" class="btn-mini" @click="onIconDelete" style="color:#ff6b6b">🗑</button>
        </div>
      </div>

      <div v-if="iconMsg" class="upload-msg" :class="{ ok: iconMsg.startsWith('✅'), err: iconMsg.startsWith('❌') }">
        {{ iconMsg }}
      </div>
    </section>

    <!-- 日志 -->
    <div v-if="store.generationLog.length" style="margin-top:10px">
      <div class="json-viewer" style="max-height:100px;font-size:9px">
        <div v-for="(line, i) in store.generationLog.slice(-6)" :key="i">{{ line }}</div>
      </div>
    </div>

    <!-- 错误 -->
    <div v-if="store.error" style="margin-top:8px;padding:6px;background:#330000;border:1px solid #ff4444;color:#ff4444;font-size:10px">
      ⚠️ {{ store.error }}
    </div>

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- 场景图添加方式弹窗(AI 生成 vs 本地上传) -->
    <!-- ════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="sceneAddMenuOpen" class="modal-mask" @click.self="sceneAddMenuOpen = false">
        <div class="modal-box">
          <div class="modal-box-title">🎨 添加场景图</div>
          <div class="modal-box-sub">{{ poiId }} — 选一种方式</div>
          <div class="modal-box-actions">
            <button class="modal-choice" :disabled="aiGeneratingScene" @click="onPickAiScene">
              <div class="modal-choice-icon">🤖</div>
              <div class="modal-choice-title">AI 生成</div>
              <div class="modal-choice-desc">用 {{ store.imageModel }} 按视觉规范生成(~30s)</div>
            </button>
            <button class="modal-choice" :disabled="sceneUploading" @click="onPickLocalScene">
              <div class="modal-choice-icon">📁</div>
              <div class="modal-choice-title">本地上传</div>
              <div class="modal-choice-desc">从电脑选一张或多张图</div>
            </button>
          </div>
          <button class="modal-box-cancel" @click="sceneAddMenuOpen = false">取消</button>
        </div>
      </div>
    </Teleport>

    <!-- AI 生成前的"特殊需求"弹窗 -->
    <!-- ════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="sceneExtraPromptOpen" class="modal-mask" @click.self="sceneExtraPromptOpen = false">
        <div class="modal-box modal-box-wide">
          <div class="modal-box-title">✨ 特殊需求</div>
          <div class="modal-box-sub">
            {{ poiId }} — 可加入本次生成的特殊场景(空着就走默认)
          </div>

          <textarea
            ref="sceneExtraTextarea"
            v-model="sceneExtraPrompt"
            class="modal-extra-textarea"
            placeholder="例：狂风暴雨 / 夜晚霓虹灯 / 樱花季漫天飞舞 / 大雪纷飞的夜晚 / 黄昏金色时刻 / 浓雾笼罩 / 万圣节装饰..."
            rows="3"
          />

          <div class="modal-preset-row">
            <span class="modal-preset-label">快速预设:</span>
            <button
              v-for="p in SCENE_PRESETS"
              :key="p"
              type="button"
              class="modal-preset-chip"
              @click="applyPreset(p)"
            >{{ p }}</button>
          </div>

          <div class="modal-box-actions">
            <button class="modal-box-cancel" @click="sceneExtraPromptOpen = false">取消</button>
            <button
              class="modal-box-primary"
              :disabled="aiGeneratingScene"
              @click="onConfirmAiSceneWithExtra"
            >✨ 生成</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { api } from '@/core/apiClient'

const store = useGeneratorStore()
const poiId = computed(() => store.currentPoiId)
const cacheBust = ref(Date.now())

// ════════════════════════════════════════════════════════
// 场景图(多张)
// ════════════════════════════════════════════════════════
const sceneList = ref([])     // [{filename, src(dataURL or URL+cacheBust), size_bytes}]
const sceneUploading = ref(false)
const sceneMsg = ref('')
const aiGeneratingScene = ref(false)  // AI 生成场景图中(进度条 v-if 用)
const sceneAspect = ref('16:9')      // 场景图比例(默认 §5.12 剧情原画 16:9)
const sceneResolution = ref('1080p')  // 场景图分辨率(默认 1080p 1920×1080)
const sceneBitDepth = ref('32bit')   // 场景图色板:32bit(高级全色域) / 16bit(SNES 复古)

// 像素尺寸映射 — sceneResolution → (targetWidth, targetHeight, sourceResolution)
const sceneTargetSize = computed(() => {
  switch (sceneResolution.value) {
    case '720p':  return { w: 1280, h:  720, src: '1K' }
    case '1080p': return { w: 1920, h: 1080, src: '1K' }
    case '2K':    return { w: 2560, h: 1440, src: '2K' }
    case '4K':    return { w: 3840, h: 2160, src: '4K' }
    default:        return { w: 1920, h: 1080, src: '1K' }
  }
})

function onResolutionChange() {
  // 用户改了下拉,清空 aiStage(避免进度条还显示旧值)
  aiStage.value = ''
}
const sceneAddMenuOpen = ref(false)  // 弹窗:AI 生成 vs 本地上传
const sceneExtraPromptOpen = ref(false)  // 弹窗:特殊需求(空 = 走默认 prompt)
const sceneExtraPrompt = ref('')         // 弹窗里的 textarea 文本
const sceneExtraTextarea = ref(null)     // textarea DOM 引用,用于自动聚焦
const SCENE_PRESETS = ['狂风暴雨', '夜晚霓虹', '大雪纷飞', '黄昏金色']  // 一键预设
const sceneFileInput = ref(null)     // 隐藏 file input 引用
const aiStage = ref('')              // AI 生成当前阶段文字(给进度条显示)

// ════════════════════════════════════════════════════════
// AI 生成场景图(按 gagaToday_visual_style_guide.md §1-5)
// 用全局 store.imageModel(标题栏已选)
// ════════════════════════════════════════════════════════

// 场景图:按 gagaToday_visual_style_guide.md §5.12 剧情场景原画
// (16:9 完整场景,带天空/广场/行人,电影感构图)
// extraRequirements: 用户临时追加的特殊需求(如"狂风暴雨"),为空则不加段
function buildSceneImagePrompt(extraRequirements = '') {
  const poi = store.currentPoi
  const osm = store.osmData?.primary_poi

  // 1. 核心风格词(§2.1) — 按 sceneBitDepth 分支
  // 32-bit = PS1/Saturn 时代高级 RPG,全色域、丰富色阶、细腻几何
  // 16-bit = SNES 时代复古,克制色板(各 ~32 色),颗粒感更强
  const bitDepth = sceneBitDepth.value
  const style = bitDepth === '32bit'
    ? `premium 32-bit era pixel art, PlayStation 1 / Sega Saturn inspired high-fidelity game illustration, FULL COLOR GAMUT (millions of colors, NOT limited palette), VIVID HIGH-SATURATION palette (think Final Fantasy Tactics / Vagrant Story key visual — bold colors, deep chromatic richness, NOT muted nor pastel), high color depth, rich tonal gradients between adjacent pixels, painterly pixel shading with smooth hue transitions, refined detailed geometry, sharp readable silhouettes, sophisticated anti-aliased sub-pixel highlights at edges, dark navy outline, grounded German realism, Germany study-abroad life simulation RPG, cinematic and immersive first-year-abroad mood, handcrafted pixel-art texture, readable silhouette, blocky pixel highlights and shadows`
    : `16-bit era SNES / Sega Genesis inspired pixel art, LIMITED color palette (~32 colors per region), chunky visible pixels, no anti-aliasing, flat color regions, dithered shading, grounded German realism, Germany study-abroad life simulation RPG, retro European RPG atmosphere, warm nostalgic mood, dark navy outline, blocky pixel highlights and shadows`

  // 像素化处理(也按色板分支)
  const pixelCraft = bitDepth === '32bit'
    ? `32-bit pixel-art technique: visible pixel grid at high resolution, smooth color gradients between adjacent pixels (hundreds of micro-shades), NO washed-out airbrush, NO photorealistic texture, NO blurry edges, dark navy outline (#07152B) around all major shapes, subtle contact shadow blocks, fine architectural details readable (window frames, roof tiles, brick courses, sculptural reliefs). Output should feel like a high-budget PS1 RPG key visual.`
    : `16-bit pixel-art technique: chunky visible pixels, no anti-aliasing, flat color regions with crisp pixel boundaries, dithered shading where needed, dark navy outline (#07152B) around all major shapes, simple but iconic shape language. Output should feel like a SNES-era RPG key visual.`

  // 色板描述(也按色板分支)
  const paletteDesc = bitDepth === '32bit'
    ? `VIVID HIGHLY-SATURATED EXTENDED color palette anchored on: warm parchment beige #EFE2C2 (sunlit sandstone), rich Bavarian cream #E8D4A8 (golden hour glow), saturated terracotta roof red #C44A2C (oxidized clay), deep moss green #5E7A3A (forest shade), antique teal copper #4A7A6E (oxidized bronze), brilliant antique gold #F4C043 (gilded statue glow), dark navy shadow #07152B (deep crevices), vivid sapphire sky blue #2E6FB5 (sunny zenith) — enrich each anchor with 60+ vivid micro-shades per hue (NOT muted, NOT pastel, NOT poster-flat). Sky must be DEEPLY SATURATED cobalt-to-sapphire gradient, NOT pale washed-out blue. Foliage must be RICH forest green, NOT olive-gray. Shadows must be DEEP navy-black, NOT flat gray.`
    : `LIMITED color palette (SNES-era ~32 colors): warm parchment beige #EFE2C2, muted Bavarian cream #D8C39B, terracotta roof red #9C4331, moss green #6F8F4E, soft teal copper #4F7F73, antique gold #E8B85C, dark navy shadow #07152B, cool blue window glass #24354F`

  // 2. 构图(§5.12 电影感 16:9 完整场景)
  const composition = `full environmental scene composition, 16:9 cinematic wide aspect, eye-level player perspective as if walking into the place, deep foreground-middleground-background depth, the landmark fills the central 60% of the frame and the surrounding plaza/street/trees/sky extend to the edges, scene that a player can step into, explore, take photos at, and study`

  // 3. 色板(已并入 bitDepth 分支,见 paletteDesc)

  // 4. 大气/时间
  const atmosphere = `spring, late morning, BRIGHT sunny day, strong warm sunlight from upper-left at ~45° casting DEFINED hard-edged shadows, clean crisp air, hopeful new-start mood, golden warm daylight (NOT overcast, NOT flat-lit)`

  // 4b. 光影对比 — 单独段落强调,避免被吞
  const lighting = `Cinematic dramatic chiaroscuro lighting: strong directional sunlight creates HIGH CONTRAST between sunlit and shadowed surfaces. Sunlit stone glows with warm golden-amber tone. Shadowed stone falls into deep cool navy-black. NO flat even lighting, NO washed-out diffuse light, NO muddy mid-tones — every surface either catches bright warm light or recedes into rich cool shadow. Sky: DEEPLY SATURATED cobalt-to-sapphire gradient from horizon (lighter warm-tinted blue) up to zenith (rich saturated royal blue), with 3-5 large billowing volumetric cumulus clouds rendered with pink-gold sunlit tops and deep blue-violet shadowed undersides, NOT thin wispy streaks.`

  // 5. 场景元素(完整场景,而不是 1:1 居中资产)
  // 通用化:不绑定特定 POI,适用于任何 Munich landmark(plaza / church / museum / park 等)
  const elements = `Foreground: warm beige-and-grey cobblestone paving with VISIBLE mortar joints, one ornate wrought-iron lamp post with multi-globe lantern, one slatted wooden park bench, one bicycle leaning on rack. Middle: 4-6 small human figures (tourists/students in casual modern clothes, backpacks, varied clothing colors — denim, mustard, terracotta, olive, ivory), one or two café umbrellas in striped cream-and-red canvas, possibly a small wooden market stall or kiosk if appropriate to a plaza setting. Background: the landmark main structure filling center, surrounding authentic Munich/Bavarian townhouses on both sides with VARIED roof tile colors (terracotta red, weathered brick, moss-touched greenish copper accents), visible chimneys, dormer windows, ornate gables, painted window shutters. Distant trees: rich dark forest green with sunlit highlights. Sky above: deep saturated sapphire with 3-5 volumetric cumulus clouds.`

  // 6. Landmark 特定规范 — 通用化
  // - 主体用 ${poi.name_de} 驱动(变量)
  // - type 字段提示构图重心(church 偏建筑,square 偏广场, park 偏绿地)
  // - 如果 POI 配了 key_features(数据字段),附加进去增强细节
  // - 没有 key_features 时,让模型按 name_de 自行推断真实特征
  const landmarkName = poi?.name_de || 'this specific Munich landmark'
  const landmarkZh = poi?.name_zh ? ` (${poi.name_zh})` : ''
  const landmarkType = poi?.type || 'place'
  const typeHint = {
    church: 'Composition is BUILDING-DOMINANT — the church/cathedral occupies the central 60-70% of the frame, vertical emphasis on towers/spires/facade, plaza or courtyard in the foreground.',
    square: 'Composition is PLAZA-DOMINANT — the central monument or town hall building is framed by surrounding townhouses, the plaza floor occupies ~40% of the frame, multiple sightlines converge.',
    park: 'Composition is GREEN-DOMINANT — trees, lawns, and paths occupy most of the frame, the landmark (fountain / pavilion / monument) is the focal point within the greenery.',
    museum: 'Composition is FACADE-DOMINANT — symmetrical institutional facade as the main subject, plaza or steps in foreground.',
    monument: 'Composition is VERTICAL SINGLE-OBJECT — the monument/statue is the clear focal point with sky and minimal ground framing it.',
    // 交通枢纽(2026-06-28 新增,跟 POIInfoForm/AddPoiDialog 对齐)
    train_station: 'Composition is HUB-DOMINANT — a grand historic train station facade with arched train shed roof and prominent clock tower as focal point; visible train platforms with rail tracks and overhead catenary lines in mid-ground; travelers with luggage and DB signage; foreground plaza with taxis/buses/trams.',
    subway: 'Composition is UNDERGROUND-ENTRANCE-DOMINANT — the U-Bahn/S-Bahn entrance pillar with the iconic "U" or "S" roundel sign as focal point, stairs descending into ground, street context above.',
    tram: 'Composition is STREET-LEVEL — a vintage or modern tram at a tram stop with overhead electric wires, urban street context.',
    bus_stop: 'Composition is STREET-LEVEL — a city bus at a marked bus stop with Haltestelle sign, urban pavement context.',
    // 通用兜底
    attraction: 'Composition is LANDMARK-DOMINANT — the tourist attraction is the central focal point, recognizable architectural or scenic features clearly visible, foreground plaza or approach path.',
    historic: 'Composition is FACADE-DOMINANT — the historic building/structure occupies the central frame, classical or period architectural details emphasized.',
  }[landmarkType] || 'Composition frames the landmark as the clear focal point with appropriate surroundings.'
  const keyFeaturesClause = poi?.key_features
    ? ` KEY FEATURES (must include all of these): ${poi.key_features}`
    : ` Render with MAXIMUM architectural detail — every window frame, roof tile, ornamental detail, sculptural element, and material texture MUST be clearly visible and faithful to the real-world appearance of ${landmarkName}.`

  const landmarkClause = `The landmark MUST be ${landmarkName}${landmarkZh}, Munich, Germany — a real, identifiable Munich landmark. ${typeHint}${keyFeaturesClause} The result must be recognizably ${landmarkName}, NOT a generic European building, NOT a fictional place, NOT a fantasy castle.`

  // 7. 像素化处理(已在 bitDepth 分支里定义 pixelCraft)

  // 8. 负面
  const negative = `Negative: photorealistic photo, 3D render, anime, chibi, generic cartoon, fantasy castle, sci-fi, cyberpunk, neon, watercolor, oil painting, transparent background, checkerboard, gray platform, text, logo, watermark, UI frame, poster layout, blurry edges, low-detail, washed out, desaturated, muddy mid-tones, flat even lighting, pastel colors.`

  // 9. 用户临时追加的特殊需求(狂风暴雨 / 夜晚 / 雪天...),为空就不加这段
  const extraClause = extraRequirements && extraRequirements.trim()
    ? `=== User special requirements (HIGH PRIORITY — these OVERRIDE default atmosphere/lighting) ===\n${extraRequirements.trim()}\nIMPORTANT: the above user requirements take precedence over the default atmosphere/lighting sections above. Adapt the scene accordingly while keeping the overall style/composition/landmark identity intact.`
    : null

  const parts = [
    `=== Subject ===`,
    `${poi?.name_de || '?'} (${poi?.name_zh || '?'}), Munich, Germany.${osm ? ` OSM category: ${osm.class || '?'}.` : ''}`,
    ``,
    `=== Visual style (§2.1) ===`,
    style,
    ``,
    `=== Composition (§5.12 剧情场景原画) ===`,
    composition,
    ``,
    `=== Color palette (§3.2) ===`,
    paletteDesc,
    ``,
    `=== Atmosphere ===`,
    atmosphere,
    ``,
    `=== Lighting & contrast (chiaroscuro, push for richness) ===`,
    lighting,
    ``,
    `=== Scene elements (full scene, NOT isolated asset) ===`,
    elements,
    ``,
    `=== Landmark specifics ===`,
    landmarkClause,
    ``,
    `=== Pixel-art craft ===`,
    pixelCraft,
  ]
  if (extraClause) {
    parts.push(``)
    parts.push(extraClause)
  }
  parts.push(negative)
  return parts.join('\n')
}

async function aiGenerateScene(extraRequirements = '') {
  if (!poiId.value) { store.error = '请先选择 POI'; return }
  aiGeneratingScene.value = true
  aiStage.value = '拼提示词...'
  store.error = null
  const extraTag = extraRequirements && extraRequirements.trim() ? ` +特殊需求` : ''
  store.log(`✨ AI 生成场景图 (${store.imageModel}${extraTag})...`)
  try {
    const prompt = buildSceneImagePrompt(extraRequirements)
    const filename = `${poiId.value}_scene_ai.png`

    const target = sceneTargetSize.value
    aiStage.value = `调模型生成中...(${sceneBitDepth.value} / ${sceneResolution.value} ${target.w}×${target.h},~${target.src === '4K' ? '60-120s' : target.src === '2K' ? '25-45s' : '10-20s'})`
    const res = await api.generateImage(prompt, filename, {
      model: store.imageModel,
      promptType: 'scene',
      aspectRatio: sceneAspect.value,
      resolution: target.src,            // 源图档位(1K/2K/4K)
      targetWidth: target.w,             // 目标像素
      targetHeight: target.h,
    })

    aiStage.value = '下载图片...'
    const imgResp = await fetch(res.url)
    if (!imgResp.ok) throw new Error(`fetch 失败: ${res.url} → ${imgResp.status}`)
    const blob = await imgResp.blob()
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })

    aiStage.value = '上传到素材库...'
    const uploadRes = await api.uploadAsset({
      data: dataUrl,
      poiId: poiId.value,
      assetKind: 'scene_main',
    })

    // 立刻 push 到列表(append 到末尾),与后端最终顺序对齐,避免 flicker
    sceneList.value.push({
      filename: uploadRes.filename,
      size_bytes: uploadRes.size_bytes,
      src: dataUrl,
    })
    cacheBust.value = Date.now()
    aiStage.value = '完成 ✓'
    store.log(`✅ AI 场景图已上传 → ${uploadRes.filename}`)
    // 后台静默刷新一次列表(保证和其他来源同步),但不阻塞 UI
    loadScenes().catch(() => {})
    // 1.2s 后自动隐藏进度条,让用户看到"完成"那一刻
    setTimeout(() => { aiGeneratingScene.value = false; aiStage.value = '' }, 1200)
  } catch (e) {
    aiStage.value = `失败: ${e.message}`
    store.error = e.message
    store.log(`❌ AI 场景图失败: ${e.message}`)
    // 失败提示停留 3s 后收起,让用户看到错误
    setTimeout(() => { aiGeneratingScene.value = false; aiStage.value = '' }, 3000)
  }
}



// 打开添加方式弹窗
function showSceneAddMenu() {
  if (sceneUploading.value) return
  sceneAddMenuOpen.value = true
}

// 选 AI 生成 → 先关弹窗,再开"特殊需求"弹窗让用户填(可空)
async function onPickAiScene() {
  sceneAddMenuOpen.value = false
  // 等下个 tick 让第一个弹窗 v-if 卸掉,再开第二个,避免叠层视觉混乱
  setTimeout(() => {
    sceneExtraPrompt.value = ''         // 每次重置,避免上次的输入残留
    sceneExtraPromptOpen.value = true
    // 自动聚焦 textarea(下个 tick 等 modal 渲染完)
    setTimeout(() => sceneExtraTextarea.value?.focus(), 50)
  }, 80)
}

// 用户点 "生成" 按钮 → 读 extra,跑 aiGenerateScene
async function onConfirmAiSceneWithExtra() {
  const extra = sceneExtraPrompt.value.trim()
  sceneExtraPromptOpen.value = false
  try {
    await aiGenerateScene(extra)
  } catch (e) {
    console.error('[onConfirmAiSceneWithExtra] unhandled:', e)
    store.error = e.message
    store.log(`❌ 触发 AI 失败: ${e.message}`)
  }
}

// 预设 chip 一键填入
function applyPreset(preset) {
  sceneExtraPrompt.value = sceneExtraPrompt.value
    ? sceneExtraPrompt.value + ', ' + preset
    : preset
  sceneExtraTextarea.value?.focus()
}

// 选本地上传 → 弹窗关,触发隐藏 file input
function onPickLocalScene() {
  sceneAddMenuOpen.value = false
  // 走下一个 tick 等 v-if 卸掉弹窗后再 click,避免 iOS 弹窗残留
  setTimeout(() => sceneFileInput.value?.click(), 50)
}

// 删除图标(走 list-assets 拿 path + delete-asset)
async function onIconDelete() {
  if (!iconFilename.value) return
  if (!confirm(`确定删除图标 ${iconFilename.value}?`)) return
  try {
    await api.deleteAsset({
      poiId: poiId.value,
      assetKind: 'icon',
      filename: iconFilename.value,
    })
    iconUrl.value = ''
    iconFilename.value = ''
    iconSizeBytes.value = 0
    cacheBust.value = Date.now()
    store.log(`🗑 图标已删除: ${iconFilename.value}`)
  } catch (e) {
    store.error = e.message
    store.log(`❌ 删图标失败: ${e.message}`)
  }
}


// 初始化 + 切 POI 时刷
async function loadScenes() {
  sceneMsg.value = ''
  try {
    const res = await api.listAssets({ poiId: poiId.value, assetKind: 'scene_main' })
    sceneList.value = (res.files || []).map(f => ({
      filename: f.filename,
      size_bytes: f.size_bytes,
      src: f.url + '?t=' + cacheBust.value,
    }))
  } catch (e) {
    sceneList.value = []
  }
}

async function onSceneUpload(e) {
  const files = Array.from(e.target.files || [])
  if (files.length === 0) return
  sceneUploading.value = true
  sceneMsg.value = `⏳ 上传 ${files.length} 张中...`
  store.error = null

  let okCount = 0
  for (const file of files) {
    try {
      const dataUrl = await readAsDataURL(file)
      const res = await api.uploadAsset({
        data: dataUrl,
        poiId: poiId.value,
        assetKind: 'scene_main',
      })
      // 立即插入到列表(乐观 UI,append 到末尾 — 与后端顺序对齐,ref 在前,新图在后)
      sceneList.value.push({
        filename: res.filename,
        size_bytes: res.size_bytes,
        src: dataUrl,  // 先用 dataURL 显示,刷新后用 URL
      })
      store.log(`🖼️ 已上传 ${res.filename} (${res.size_bytes} bytes)`)
      okCount++
    } catch (err) {
      store.error = `${file.name}: ${err.message}`
    }
  }

  sceneMsg.value = okCount > 0 ? `✅ 已上传 ${okCount} 张` : `❌ 上传失败`
  cacheBust.value = Date.now()
  // 后台重新从服务器拉一次(同步真实状态)
  await loadScenes()
  store.markGenerated('uploads')
  sceneUploading.value = false
  e.target.value = ''
}

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function deleteScene(img, index) {
  const isPrimary = index === 0
  const msg = isPrimary
    ? `确认删除主图 "${img.filename}"?\n\n删除后,后续上传的图会自动成为新主图。`
    : `确认删除 "${img.filename}"?`
  if (!window.confirm(msg)) return
  try {
    await api.deleteAsset({
      filename: img.filename,
      poiId: poiId.value,
      assetKind: 'scene_main',
    })
    store.log(`🗑️ 已删除 ${img.filename}`)
    sceneMsg.value = `✅ 已删除 ${img.filename}`
    await loadScenes()   // 重新拉,自动提升新主图
  } catch (err) {
    sceneMsg.value = `❌ ${err.message}`
    store.error = err.message
  }
}


function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}


// 监听 <img> onload,把图片真实像素尺寸写到 sceneList 对应条目上,用于注释栏显示 "1920×1080"
function onImgLoad(ev) {
  const imgEl = ev.target
  const alt = imgEl.alt
  if (!alt) return
  const item = sceneList.value.find(s => s.filename === alt)
  if (item && imgEl.naturalWidth && imgEl.naturalHeight) {
    item.width = imgEl.naturalWidth
    item.height = imgEl.naturalHeight
  }
}
function onImgError(ev) {
  // 加载失败时不写尺寸(注释栏会自然不显示 dims)
  console.warn('[scene thumb] failed to load:', ev.target?.alt)
}


// ════════════════════════════════════════════════════════
// POI 图标(单张)
// ════════════════════════════════════════════════════════
const iconUrl = ref(null)
const iconFilename = ref('')
const iconSizeBytes = ref(0)
const iconUploading = ref(false)
const iconMsg = ref('')

const iconSrc = computed(() => {
  if (!iconUrl.value) return ''
  return iconUrl.value.startsWith('data:') ? iconUrl.value : iconUrl.value + '?t=' + cacheBust.value
})

async function loadIcon() {
  iconMsg.value = ''
  try {
    const res = await api.listAssets({ poiId: poiId.value, assetKind: 'icon' })
    if (res.files && res.files.length > 0) {
      const f = res.files[0]
      iconUrl.value = f.url
      iconFilename.value = f.filename
      iconSizeBytes.value = f.size_bytes
    } else {
      iconUrl.value = null
      iconFilename.value = ''
      iconSizeBytes.value = 0
    }
  } catch {
    iconUrl.value = null
  }
}

async function onIconUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  iconUploading.value = true
  iconMsg.value = '⏳ 上传中...'
  store.error = null

  try {
    const dataUrl = await readAsDataURL(file)
    iconUrl.value = dataUrl       // 立即显示
    const res = await api.uploadAsset({
      data: dataUrl,
      poiId: poiId.value,
      assetKind: 'icon',
    })
    iconFilename.value = res.filename
    iconSizeBytes.value = res.size_bytes
    iconMsg.value = `✅ ${res.filename}`
    store.log(`🎯 ${res.filename} (${res.size_bytes} bytes)`)
    cacheBust.value = Date.now()
    store.markGenerated('uploads')
  } catch (err) {
    iconMsg.value = `❌ ${err.message}`
    iconUrl.value = null
    store.error = err.message
  } finally {
    iconUploading.value = false
    e.target.value = ''
  }
}


// ── 切 POI 时刷两边 ──
watch(poiId, () => {
  sceneMsg.value = ''
  iconMsg.value = ''
  loadScenes()
  loadIcon()
}, { immediate: true })
</script>

<style scoped>
.upload-card {
  background: #12122a;
  border: 1px solid #333;
  padding: 10px 12px;
  margin-bottom: 10px;
}
.upload-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.upload-card-title {
  font-size: 11px;
  color: var(--gold2);
  font-weight: bold;
}
.upload-card-target {
  font-size: 9px;
  color: var(--text-dim);
  font-family: monospace;
}
.upload-card-hint {
  font-size: 9px;
  color: var(--text-dim);
  margin: 0 0 8px 0;
  line-height: 1.5;
}
.upload-card-hint code {
  color: var(--gold2);
  background: rgba(0,0,0,.3);
  padding: 0 3px;
  border-radius: 2px;
  font-size: 9px;
}
.upload-msg {
  margin-top: 6px;
  font-size: 10px;
  padding: 4px 6px;
}
.upload-msg.ok { color: #44ff88; }
.upload-msg.err { color: #ff6666; }

/* ── 场景图网格 ── */
.scene-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);   /* 一行四张 */
  gap: 8px;
  margin-top: 4px;
}
.scene-thumb {
  position: relative;
  background: #0a0a1a;
  border: 1px solid var(--border);
  padding: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.scene-thumb .img-wrap {
  position: relative;
  aspect-ratio: 16/9;
  overflow: hidden;
}
.scene-thumb .img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.scene-thumb .del-btn {
  position: absolute;
  top: 6px;
  left: 6px;       /* 左上角,跟右上角的主图徽章分开 */
  width: 22px;
  height: 22px;
  background: rgba(0,0,0,.75);
  color: #ff7777;
  border: 1px solid #ff4444;
  border-radius: 3px;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 0;
  z-index: 2;
}
.scene-thumb:hover .del-btn {
  display: flex;
}
.scene-thumb .del-btn:hover {
  background: #ff4444;
  color: #fff;
}
.scene-thumb.is-primary {
  border-color: var(--gold);
  box-shadow: 0 0 0 1px var(--gold);
}
.scene-thumb img {
  flex: 1;
  width: 100%;
  object-fit: cover;
  min-height: 0;
}
.scene-thumb-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: var(--gold);
  color: #000;
  font-size: 9px;
  padding: 1px 4px;
  font-weight: bold;
}
.scene-thumb-name {
  font-size: 8px;
  color: var(--gold2);
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}
.scene-thumb-size {
  font-size: 8px;
  color: var(--text-dim);
}
.scene-thumb-dims {
  color: var(--gold2);
  font-family: monospace;
}
.scene-add {
  background: #0a0a1a;
  border: 2px dashed var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  cursor: pointer;
  color: var(--text-dim);
  font-size: 14px;
  aspect-ratio: 16/9;
  transition: border-color .2s, color .2s;
}
.scene-add:hover {
  border-color: var(--gold);
  color: var(--gold2);
}
.scene-add small {
  font-size: 9px;
  display: block;
  margin-top: 4px;
}

/* ── 图标(横向小条,占位小) ── */
.icon-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  background: #0a0a1a;
  border: 1px solid var(--gold);
  min-height: 52px;
}
.icon-thumb {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border: 1px solid var(--border);
  background: repeating-conic-gradient(#222 0% 25%, #333 0% 50%) 0/8px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.icon-thumb img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  image-rendering: pixelated;
}
.icon-thumb-empty {
  font-size: 18px;
  color: var(--text-dim);
}
.icon-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.icon-info-name {
  font-size: 10px;
  color: var(--gold);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.icon-info-size {
  font-size: 8px;
  color: var(--text-dim);
}
.icon-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.btn-mini {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  font-size: 10px;
  background: var(--navy);
  color: var(--gold2);
  border: 1px solid var(--border);
  cursor: pointer;
  font-family: inherit;
  transition: border-color .15s, color .15s;
}
.btn-mini:hover {
  border-color: var(--gold);
  color: var(--gold);
}
.btn-mini:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── 场景图生成选项(比例/分辨率) ── */
.scene-gen-options {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 6px 10px;
  margin-bottom: 8px;
  background: var(--navy);
  border: 1px solid var(--border);
  font-size: 10px;
}
.scene-gen-label {
  color: var(--gold);
  font-weight: 500;
}
.scene-gen-options label {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-dim);
}
.opt-label {
  color: var(--text-dim);
  font-size: 9px;
}
.opt-select {
  font-size: 10px;
  padding: 3px 6px;
  background: #0a0a1a;
  color: var(--gold2);
  border: 1px solid var(--border);
  font-family: inherit;
  cursor: pointer;
  min-width: 80px;
}
.opt-select:hover {
  border-color: var(--gold);
}

/* ── AI 生成进度条(常驻指示器) ── */
.ai-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  margin-bottom: 8px;
  background: linear-gradient(90deg, #1a1530 0%, #0a1230 100%);
  border: 1px solid var(--gold);
  border-left: 3px solid var(--gold);
  box-shadow: 0 0 12px rgba(232, 184, 92, 0.15);
}
.ai-progress-spinner {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  border: 2px solid rgba(232, 184, 92, 0.25);
  border-top-color: var(--gold);
  border-radius: 50%;
  animation: ai-spin 0.8s linear infinite;
}
@keyframes ai-spin {
  to { transform: rotate(360deg); }
}
.ai-progress-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ai-progress-stage {
  font-size: 11px;
  color: var(--gold);
  font-weight: 500;
}
.ai-progress-model {
  color: var(--text-dim);
  font-size: 9px;
  margin-left: 4px;
}
.ai-progress-bar {
  height: 3px;
  background: rgba(232, 184, 92, 0.15);
  border-radius: 2px;
  overflow: hidden;
}
.ai-progress-bar-fill {
  height: 100%;
  width: 40%;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  animation: ai-progress-slide 1.5s ease-in-out infinite;
}
@keyframes ai-progress-slide {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}
/* 进度条进出场动画 */
.progress-enter-active, .progress-leave-active {
  transition: opacity .25s, transform .25s;
}
.progress-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}
.progress-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── 场景图添加卡(可能 disabled) ── */
.scene-add.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── 场景图添加方式弹窗 ── */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}
.modal-box {
  background: linear-gradient(180deg, #0a1230 0%, #060a1a 100%);
  border: 2px solid var(--gold);
  padding: 18px 20px 14px;
  min-width: 380px;
  max-width: 480px;
  box-shadow: 0 0 30px rgba(232, 184, 92, 0.3);
}
.modal-box-title {
  font-size: 14px;
  color: var(--gold);
  margin-bottom: 4px;
  text-align: center;
  letter-spacing: 1px;
}
.modal-box-sub {
  font-size: 10px;
  color: var(--text-dim);
  text-align: center;
  margin-bottom: 14px;
}
.modal-box-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}
.modal-choice {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background: #0a0a1a;
  border: 1px solid var(--border);
  cursor: pointer;
  font-family: inherit;
  transition: border-color .15s, transform .1s;
}
.modal-choice:hover:not(:disabled) {
  border-color: var(--gold);
  transform: translateY(-1px);
}
.modal-choice:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.modal-choice-icon {
  font-size: 28px;
  line-height: 1;
}
.modal-choice-title {
  font-size: 12px;
  color: var(--gold);
}
.modal-choice-desc {
  font-size: 9px;
  color: var(--text-dim);
  text-align: center;
  line-height: 1.3;
}
.modal-box-cancel {
  width: 100%;
  padding: 6px;
  font-size: 10px;
  background: transparent;
  color: var(--text-dim);
  border: 1px solid var(--border);
  cursor: pointer;
  font-family: inherit;
}
.modal-box-cancel:hover {
  border-color: var(--gold);
  color: var(--gold);
}

/* ── 特殊需求弹窗(textarea + presets) ── */
.modal-box-wide {
  width: 480px;
  max-width: 92vw;
}
.modal-extra-textarea {
  width: 100%;
  box-sizing: border-box;
  background: #0a0a1a;
  color: var(--text);
  border: 1px solid var(--border);
  padding: 8px 10px;
  font-family: inherit;
  font-size: 11px;
  line-height: 1.5;
  resize: vertical;
  min-height: 60px;
  margin-top: 10px;
}
.modal-extra-textarea:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 1px var(--gold);
}
.modal-extra-textarea::placeholder {
  color: var(--text-dim);
  font-style: italic;
}
.modal-preset-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  margin-bottom: 12px;
}
.modal-preset-label {
  font-size: 9px;
  color: var(--text-dim);
  margin-right: 2px;
}
.modal-preset-chip {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--gold2);
  font-size: 10px;
  padding: 3px 8px;
  cursor: pointer;
  font-family: inherit;
  transition: all .15s;
}
.modal-preset-chip:hover {
  border-color: var(--gold);
  background: rgba(232, 184, 92, 0.1);
  color: var(--gold);
}
.modal-box-primary {
  padding: 6px;
  font-size: 11px;
  font-weight: bold;
  background: var(--gold);
  color: #000;
  border: 1px solid var(--gold);
  cursor: pointer;
  font-family: inherit;
}
.modal-box-primary:hover:not(:disabled) {
  background: #ffd86b;
  border-color: #ffd86b;
}
.modal-box-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
