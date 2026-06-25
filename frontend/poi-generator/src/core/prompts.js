/**
 * 共享 LLM Prompt 库
 *
 * - PROJECT_CONTEXT: 每次调用都附带的项目背景/玩家画像/硬规则
 * - buildContext(poi, osm): POI 特定上下文(名字/类型/OSM 真实数据)
 * - 各 tab 的 prompt builder: NPC/Dialogue/Knowledge/Quest/Checkin
 * - buildAllInOnePrompt(poi, osm): App.vue "一键全量"按钮,1 次调用出 9 类内容
 * - IMAGE_PROMPT_CONTEXT + buildImagePrompt: 图片生成专用(16-bit 风格)
 */

// ============================================================
// 共享上下文
// ============================================================

/**
 * 项目背景 + 玩家画像 + 硬规则
 * 每次 LLM 调用都拼在 system prompt 位置
 * 精简到 UI 暴露的 9 个内容类型
 */
export const PROJECT_CONTEXT = `
# gagaToday — 德国留学模拟 RPG

**项目一句话**：基于真实 OpenStreetMap 数据的 16-bit 像素风德国城市 RPG,
从慕尼黑出发,用地图 + AI 对话体验德国留学日常。
**核心口号**：在德国,学会生活。Learn. Explore. Belong.

## 玩家画像
- 15-16 岁中国学生,初三毕业后赴德国(国际学校或普通中学)
- 德语水平从 A1 入门递进到 B2(TestDaF 目标)
- 年轻、有探索欲、对德国文化好奇但陌生
- 教学性内容(不是纯娱乐),每条语言材料标 A1/A2/B1 难度

## POI 内容产出(每个 POI 需 9 类)
1. **poi_info** — 基础信息(德中名/类型/坐标/游戏角色 1-2 句)
2. **scenes** — 场景图(由 IMAGE_PROMPT_CONTEXT 走图片生成,不走 LLM)
3. **npc_profiles** — 1-2 个 NPC(主理人 + 辅助)
4. **npcs_dialogue_hooks** — 6-8 个对话触发场景(LLM 自己根据 POI 类型推导)
5. **npcs_dialogue_trees** — 每 hook 3-5 轮对话 + 2 个分支选项,中/德/英三语
6. **knowledge_cards** — 5-7 张文化/历史/建筑/宗教知识卡
7. **quests** — 4-6 个任务(exploration/cultural/dialogue/seasonal/treasure_hunt)
8. **checkin_targets** — 3-5 个打卡目标(location/physical/photo/scheduled/discover)
9. **scene_events** — 2-3 个天气/时间相关的场景事件(雨天/圣诞/夜场等)

## 视觉风格(图 prompt 用,见 IMAGE_PROMPT_CONTEXT)
- 16-bit 像素艺术(SNES/GBA 时代)
- 慕尼黑主色:啤酒金 #D4A847 + 巴伐利亚蓝 + 阿尔卑斯白,暖色调
- 参考游戏:Coffee Talk / VA-11 Hall-A / Stardew Valley
- 角色 192×256、场景 1280×720、抗锯齿关、1px 硬阴影、≤24 色/城

## 硬规则(违反任意一条都算生成失败)
1. 不知道的真实信息(地址/电话/历史细节)留 null, **禁止编造**
2. 德国专有名词保留德文,附中/英文翻译
3. 数值合理: culture_xp 1-10、mood 1-5、energy 可负、任务奖励 5-15
4. 所有 JSON 字段填全, **不要空字符串**(不知道就 null)
5. 返回的 JSON 必须能被 JSON.parse 解析,不要 markdown \`\`\` 包裹
6. 对话三语(de/zh/en)都给, **不要只给德语**
7. NPC 性格用 2-3 个英文形容词(warm / patient / curious...)
`.trim()


/**
 * 图片生成专用上下文
 * 只在 generateImage / RefWorkflow 里拼,不在 LLM 文本生成里出现
 */
export const IMAGE_PROMPT_CONTEXT = `
**视觉风格**:
- 16-bit 像素艺术(SNES/GBA 时代),参考 Coffee Talk / VA-11 Hall-A / Stardew Valley
- 暖色调,慕尼黑:啤酒金 #D4A847 + 巴伐利亚蓝 + 阿尔卑斯白
- 抗锯齿关, 1 像素硬阴影, ≤24 色调色板
- 角色立绘 192×256 透明背景 PNG, 场景背景 1280×720 PNG
- 表情通过眼睛+嘴型+眉毛变化(4-5 个变体:neutral/smile/thinking/serious/blessing)
- 写实感场景要带轻微像素化处理, 不要完全写实
`.trim()


// ============================================================
// POI 上下文构建器
// ============================================================

/**
 * 拼 POI 特定上下文(每次 LLM 调用都附加)
 * @param {Object} poi - {id, name_de, name_zh, type, lat, lng, icon}
 * @param {Object|null} osm - OSM 提取数据,可能为 null
 */
export function buildContext(poi, osm) {
  if (!poi) return '(无 POI 上下文)'

  const parts = [
    '## 当前 POI',
    `- 中文名: ${poi.name_zh}`,
    `- 德文名: ${poi.name_de}`,
    `- 类型: ${poi.type}`,
    `- 坐标: ${poi.lat ?? '?'}, ${poi.lng ?? '?'}`,
    `- 英文: ${poi.name_en || '?'}`,
  ]

  if (osm) {
    parts.push('', '## OSM 提取的真实数据(必须基于这些)')
    if (osm.osm_id) parts.push(`- OSM ID: ${osm.osm_id}`)
    if (osm.name) parts.push(`- 标准名: ${osm.name}`)
    if (osm.category) parts.push(`- 分类: ${osm.category}`)
    if (osm.rank) parts.push(`- 重要度 rank: ${osm.rank}`)
    if (osm.walk_minutes != null) parts.push(`- 步行参考: ${osm.walk_minutes} 分钟`)
    if (osm.cost) parts.push(`- 费用参考: ${osm.cost}`)
    if (osm.ubahn) parts.push(`- 交通: ${osm.ubahn}`)
    if (osm.address) parts.push(`- 地址: ${osm.address}`)
    if (osm.wikipedia) parts.push(`- Wikipedia: ${osm.wikipedia}`)
    if (osm.description) parts.push(`- 描述: ${osm.description}`)
    if (osm.nearby_pois?.length) {
      parts.push(`- 邻近 POI: ${osm.nearby_pois.map(p => p.name).join(', ')}`)
    }
  } else {
    parts.push('', '(该 POI 尚未提取 OSM 真实数据,基于公开知识即可)')
  }

  return parts.join('\n')
}


// ============================================================
// App.vue "一键全量" prompt
// ============================================================

/**
 * 1 次调用产出 9 类内容中的 7 类文本(NPC + 对话 hook + 对话树 +
 *   知识卡 + 任务 + 打卡 + 场景事件;info 和 scenes 单独走)
 */
export function buildAllInOnePrompt(poi, osm) {
  return `${PROJECT_CONTEXT}

${buildContext(poi, osm)}

## 任务:为这个 POI 一次性产出以下 7 类内容

返回单个 JSON 对象,字段名严格按以下 schema。**所有数组至少给 1 个,不要空数组**。
如果某个类别不适用,给空数组。

\`\`\`json
{
  "npc_profiles": [
    {
      "id": "npc_${poi.id || 'x'}_main",
      "name_de": "德文姓名",
      "name_zh": "中文译名",
      "role": "主理人角色(如 Pfarrer / Kurator / Markthändler)",
      "role_zh": "中文角色",
      "age_band": "adult|teen|senior",
      "personality": ["warm", "patient"],
      "background_zh": "80-120 字背景故事,中文,体现德国 POI 的真实工作日常",
      "language_profile": {
        "default_language": "de",
        "lang_pref": { "de": 0.8, "en": 0.2 },
        "can_speak_english": true,
        "english_level": "B1",
        "patience_with_beginners": "high"
      },
      "relationship_defaults": { "friendship": 20, "trust": 30, "familiarity": 20, "conflict": 0 },
      "review_status": "draft"
    }
  ],
  "dialogue_hooks": [
    {
      "id": "hook_1",
      "label": "对话场景标题(中文)",
      "desc": "这个对话在什么情境下触发,1 句话",
      "difficulty": "A1|A2|B1",
      "trigger": "触发条件英文 ID,如 first_visit / ask_directions",
      "difficulty_rationale": "为什么是 A1/A2/B1,1 句话"
    }
  ],
  "dialogues": [
    {
      "hook_id": "对应 hook_1 的 id",
      "turns": [
        { "turn_id": "t1", "speaker": "npc", "de": "...", "zh": "...", "en": "...", "options_de": ["选项1德语 | 中文", "选项2德语 | 中文"] },
        { "turn_id": "t2", "speaker": "player", "de": "...", "zh": "...", "en": "...", "chosen_option_index": 0 },
        ...(3-5 轮)
      ]
    }
  ],
  "knowledge_cards": [
    {
      "id": "knowledge_${poi.id || 'x'}_1",
      "title_zh": "卡片标题(疑问句或名词短语)",
      "category": "Geschichte|Legende|Architektur|Kultur|Religion",
      "body_zh": "80-150 字中文,有教育意义和趣味性,基于真实文化历史(不知道就泛化,不要编造细节)",
      "gameplay_use": ["knowledge_card", "checkin_reward"]
    }
  ],
  "quests": [
    {
      "id": "quest_${poi.id || 'x'}_1",
      "title_zh": "任务标题(动宾结构)",
      "type": "exploration|cultural|dialogue|seasonal|treasure_hunt",
      "description_zh": "30-60 字任务描述",
      "trigger": { "type": "approach|talk|photo|schedule", "condition": "触发英文 ID" },
      "rewards": { "culture_xp": 5, "mood": 2, "german_xp": 3 },
      "steps": [
        { "step_id": "s1", "instruction_zh": "第一步做什么", "order": 1 }
      ],
      "review_status": "draft"
    }
  ],
  "checkin_targets": [
    {
      "id": "checkin_${poi.id || 'x'}_1",
      "name_zh": "打卡名(名词短语)",
      "type": "location|physical|photo|scheduled|discover",
      "trigger": { "type": "arrive|interact|time", "condition": "条件英文 ID" },
      "reward": { "culture_xp": 3, "mood": 2 },
      "review_status": "draft"
    }
  ],
  "scene_events": [
    {
      "id": "event_${poi.id || 'x'}_1",
      "name_zh": "场景事件名(如 雨夜独行 / 圣诞子夜)",
      "weather": "rainy|snowy|night|golden_hour|sunny",
      "season": "spring|summer|autumn|winter|any",
      "description_zh": "50-100 字,描述这个时刻的氛围和玩家感受",
      "trigger": { "type": "weather|time", "condition": "条件英文 ID" }
    }
  ]
}
\`\`\`

只返回 JSON,不要 markdown 包裹(我已用 \`\`\` 标 schema 不是要你加)。`.trim()
}


// ============================================================
// 单 tab prompt builder(给面板里 "📝 生成单个" 按钮用)
// ============================================================

export function buildNPCPrompt(poi, osm, roleZh = '主理人') {
  return `${PROJECT_CONTEXT}

${buildContext(poi, osm)}

## 任务:为这个 POI 生成 1 个 NPC(${roleZh})

根据 POI 类型推导合适的角色:
- 教堂 → Pfarrer(神父)/ Sakristan(管理员)
- 博物馆 → Kurator(馆长)/ Guide(导览员)
- 广场 → Straßenmusikant(街头艺人)/ Marktbesucher(游客)
- 公园 → Gärtner(园丁)/ Jogger(跑步者)
- 超市/商店 → Kassiererin(收银员)/ Verkäufer(店员)
- 城堡 → Schlosspächter(管理员)/ Guide

返回单个 JSON 对象:
{
  "id": "npc_${poi.id || 'x'}_${roleZh === '主理人' ? 'main' : 'helper'}",
  "name_de": "典型德国姓名",
  "name_zh": "中文译名",
  "role": "德文职业角色",
  "role_zh": "${roleZh}",
  "age_band": "adult|teen|senior",
  "personality": ["形容词1", "形容词2"],
  "background_zh": "80-120 字背景,中文,具体生动",
  "language_profile": {
    "default_language": "de",
    "lang_pref": { "de": 0.8, "en": 0.2 },
    "can_speak_english": true,
    "english_level": "B1",
    "patience_with_beginners": "high"
  },
  "relationship_defaults": { "friendship": 20, "trust": 30, "familiarity": 20, "conflict": 0 },
  "review_status": "draft"
}

只返回 JSON。`.trim()
}


export function buildDialoguePrompt(poi, osm, hook) {
  // hook: { label, desc, difficulty?, trigger? }
  return `${PROJECT_CONTEXT}

${buildContext(poi, osm)}

## 任务:为这个对话场景生成 1 个完整对话树

场景: ${hook.label}
描述: ${hook.desc}
触发条件: ${hook.trigger || '未指定'}

**对话难度 (A1/A2/B1) 你自己决定**,根据场景复杂度(简单问候 = A1,深入文化讨论 = B1)。
在返回的 dialogue 对象里加 difficulty 字段说明选择理由。

返回 JSON 数组,3-5 轮对话 + 2 个分支选项,中/德/英三语:
[
  {
    "hook_id": "${hook.id || 'hook_x'}",
    "difficulty": "A1|A2|B1",
    "difficulty_rationale": "为什么选这个难度",
    "turns": [
      { "turn_id": "t1", "speaker": "npc", "de": "德语", "zh": "中文", "en": "English", "options_de": ["选项1德语 | 中文", "选项2德语 | 中文"] },
      { "turn_id": "t2", "speaker": "player", "de": "德语回应", "zh": "中文", "en": "English", "chosen_option_index": 0 },
      ...(3-5 轮)
    ]
  }
]

只返回 JSON 数组。`.trim()
}


export function buildKnowledgePrompt(poi, osm, card) {
  // card: { title, category, gameplay_use? }
  return `${PROJECT_CONTEXT}

${buildContext(poi, osm)}

## 任务:为这个知识卡题目生成内容

题目: ${card.title}
类别: ${card.category || 'Geschichte'}
游戏用途: ${(card.gameplay_use || ['knowledge_card']).join(', ')}

返回单个 JSON:
{
  "id": "knowledge_${poi.id || 'x'}_${(card.title || '').replace(/[^\w]/g, '').slice(0, 12)}",
  "location_id": "explore_munich_${poi.id || 'x'}",
  "category": "${card.category || 'Geschichte'}",
  "title_zh": "${card.title || ''}",
  "body_zh": "80-150 字中文,基于 POI 真实文化历史(不知道就泛化)。有教育意义和趣味性。",
  "gameplay_use": ${JSON.stringify(card.gameplay_use || ['knowledge_card'])},
  "review_status": "draft"
}

只返回 JSON。`.trim()
}


export function buildQuestPrompt(poi, osm, quest) {
  // quest: { title, type, desc? }
  return `${PROJECT_CONTEXT}

${buildContext(poi, osm)}

## 任务:为这个任务题目生成完整任务

题目: ${quest.title}
类型: ${quest.type}
简述: ${quest.desc || '未指定'}

返回单个 JSON:
{
  "id": "quest_${poi.id || 'x'}_${quest.id || 'q1'}",
  "title_zh": "${quest.title || ''}",
  "type": "${quest.type || 'exploration'}",
  "description_zh": "30-60 字任务描述,告诉玩家要做什么",
  "location_id": "explore_munich_${poi.id || 'x'}",
  "trigger": { "type": "approach|talk|photo|schedule", "condition": "${quest.trigger || 'first_visit'}" },
  "rewards": { "culture_xp": 5, "mood": 2, "german_xp": 3 },
  "steps": [
    { "step_id": "s1", "instruction_zh": "第一步做什么", "order": 1 }
  ],
  "review_status": "draft"
}

只返回 JSON。`.trim()
}


export function buildCheckinPrompt(poi, osm, item) {
  // item: { title, type, rewardDesc? }
  return `${PROJECT_CONTEXT}

${buildContext(poi, osm)}

## 任务:为这个打卡目标生成完整配置

目标: ${item.title}
类型: ${item.type}
奖励描述: ${item.rewardDesc || 'culture_xp:3, mood:1'}

返回单个 JSON:
{
  "id": "checkin_${poi.id || 'x'}_${item.id || 'c1'}",
  "location_id": "explore_munich_${poi.id || 'x'}",
  "name_zh": "${item.title || ''}",
  "type": "${item.type || 'location'}",
  "trigger": { "type": "arrive|interact|time", "condition": "${item.trigger || 'first_visit'}" },
  "reward": { "culture_xp": 3, "mood": 1 },
  "review_status": "draft"
}

只返回 JSON。`.trim()
}


// ============================================================
// 图片 prompt builder
// ============================================================

/**
 * 场景图 prompt
 * @param {Object} opts - { season, weather, interior|exterior, time, description }
 */
export function buildSceneImagePrompt(poi, opts = {}) {
  const { season = 'spring', weather = 'sunny', time = 'day', view = 'exterior', extra = '' } = opts
  return `${IMAGE_PROMPT_CONTEXT}

POI: ${poi.name_de} (${poi.name_zh}), 慕尼黑
场景类型: ${view === 'interior' ? '内部' : '外部'}
季节: ${season}
天气: ${weather}
时间: ${time}
${extra ? `额外描述: ${extra}` : ''}

生成一张 16-bit 像素艺术风格场景图,1280×720。
${view === 'interior' ? '展示内部空间氛围(座位/装饰/光影)' : '展示建筑外观、周围环境、天空和地标关系'}。`
}


/**
 * NPC 立绘 prompt
 */
export function buildCharacterImagePrompt(npc, expression = 'neutral') {
  return `${IMAGE_PROMPT_CONTEXT}

NPC: ${npc.name_de} (${npc.name_zh}), ${npc.role_zh}
年龄: ${npc.age_band}
性格: ${(npc.personality || []).join(', ')}
当前表情: ${expression}

生成 192×256 PNG 透明背景的角色立绘。
表情通过眼睛+嘴型+眉毛变化实现(不是全身动作)。
视线略微朝左(看着对话气泡)。`
}
