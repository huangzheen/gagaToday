# POI 内容生成器 — 设计与开发计划

> 版本：v0.1 · 2026-06-22  
> 用途：为慕尼黑 MVP 及后续所有城市提供 **兴趣点(POI)全量内容生成** 的独立 Web 工具  
> 消费方：游戏客户端 (`frontend/src/content/` + `assets/`)

---

## 1. 为什么需要这个生成器

当前内容生产流程：

```
Agent 手动写 JSON → 存入 drafts/ → 人工审查 → 移入 content/munich/
```

痛点：
- 每个 POI 需要手动编写 10+ 个 JSON 文件
- 图片需要单独用 AI 工具生成 + 手动下载 + 归档
- NPC 对话树需要反复修改格式
- 跨文件关联（location ↔ NPC ↔ dialogue ↔ knowledge_card）容易断裂

**生成器目标**：一个 Web 界面，输入 POI 名称/地址/坐标 → 一键生成全套内容。

---

## 2. 生成器产出总表

对于**每个 POI**，生成器产出以下内容（均按现有 schema）：

| # | 产出类型 | 文件名后缀 | 现有参考文件 | 生成方式 |
|---|---------|-----------|-------------|---------|
| 1 | POI 基础信息 | `exploration_locations.draft.json` | `drafts/exploration/...` | LLM + 手动输入 |
| 2 | 场景图片(多版本) | `assets/scenes/munich/{poi_id}/*.png` | `docs/ART_ASSETS.md` | AI 图片生成 |
| 3 | NPC 档案(主理人+辅助) | `npc_profiles.draft.json` | `drafts/npcs/...` | LLM 生成 |
| 4 | NPC 立绘(多表情) | `assets/characters/{npc_id}/*.png` | `assets/characters/anna/` | AI 图片生成 |
| 5 | 对话树(多场景) | `npc_dialogue_hooks.draft.json` | `drafts/npcs/...` | LLM 生成 |
| 6 | 完整对话脚本(多轮) | `dialogues.draft.json` | `content/munich/dialogues.json` | LLM 生成 |
| 7 | 知识卡(文化/历史) | `knowledge_cards.draft.json` | `drafts/exploration/...` | LLM 生成 |
| 8 | 历史故事/传说 | `history_stories.draft.json` | `drafts/exploration/...` | LLM 生成 |
| 9 | 打卡目标 | `checkin_targets.draft.json` | `drafts/exploration/...` | LLM 生成 |
| 10 | 隐藏彩蛋/珍奇点 | `treasure_items.draft.json` | `drafts/exploration/...` | LLM 生成 |
| 11 | 营业时间 | `opening_hours.draft.json` | `drafts/exploration/...` | LLM + 默认模板 |
| 12 | 门票价格 | `ticket_prices.draft.json` | `drafts/exploration/...` | LLM + 默认模板 |
| 13 | 剧情/任务链 | `quests.draft.json` | 新建 | LLM 生成 |
| 14 | 场景事件(天气/时间) | `scene_events.draft.json` | 新建 | LLM 生成 |
| 15 | 来源记录 | `source_records.json` | `drafts/.../source_records.json` | 自动生成 |

---

## 3. 以 Frauenkirche（慕尼黑圣母教堂）为例

### 3.1 需要生成的图片

按 `assets/` 目录约定，每个 POI 的场景图按用途分文件夹：

```
assets/scenes/munich/frauenkirche/
├── exterior/
│   ├── spring.png              # 春天 · 樱花/新绿
│   ├── summer.png              # 夏天 · 蓝天/阳光
│   ├── autumn.png              # 秋天 · 金叶
│   ├── winter.png              # 冬天 · 积雪
│   ├── rainy.png               # 暴雨
│   ├── snowy.png               # 大雪纷飞
│   ├── night.png               # 夜景 · 灯光
│   └── golden_hour.png         # 黄昏/日出
├── interior/
│   ├── empty.png               # 空无一人的教堂
│   ├── faithful.png            # 满是信徒(弥撒时间)
│   ├── tourists.png            # 满是游客(旺季)
│   ├── choir.png               # 唱诗班演唱
│   ├── altar_closeup.png       # 祭坛特写
│   └── teufelstritt.png        # 魔鬼脚印特写
├── tower/
│   ├── view_over_munich.png    # 塔顶俯瞰慕尼黑
│   └── tower_stairs.png        # 旋转楼梯
└── _thumbnails/
    ├── exterior_thumb.png       # 缩略图(地图 POI 气泡用)
    └── interior_thumb.png
```

- **分辨率**: 1280×720 (16:9) 场景背景 / 192×256 立绘
- **风格**: 像素艺术 16-bit 或 写实水彩风格(可配置)
- **生成工具**: `matrix_generate_image`（通过 `generate_art.py` 统一调用）

### 3.2 需要生成的 NPC

#### 主理人 NPC: Pfarrer (教父)

```
npc_id: npc_pater_johann_frauenkirche
name_de: Pater Johann
name_zh: 约翰神父
role: 圣母教堂助理神父
age_band: adult (45)
personality: ["warm", "thoughtful", "patient", "good_humored"]
background_zh: |
  在 Frauenkirche 服务 18 年,负责日常弥撒、游客导览、学校团体接待。
  曾在罗马学习神学,能说流利的英语和基础法语。
  特别喜欢和年轻人聊天,经常在教堂中殿主动搭讪看起来迷茫的游客。
  每周三下午在教堂侧厅提供免费心理咨询(Seelsorge)。
lang_pref: de 0.8 / en 0.2
can_speak_english: true (C1)
```

#### 辅助 NPC（可选）:

- **npc_frau_weber_sakristanin**: 教堂管理员/sakristanin,负责开放/关闭教堂,卖纪念品
- **npc_herr_ Mueller_organist**: 管风琴师,周末弥撒演奏

#### NPC 肖像(多表情):

```
assets/characters/pater_johann/
├── neutral.png       # 默认
├── smile.png         # 微笑/欢迎
├── thinking.png      # 思考/讲解
├── serious.png       # 严肃/重要话题
└── blessing.png      # 祝福/告别
```

### 3.3 需要生成的对话场景

按 `dialogue_type` 分类，每个场景一个完整对话树：

| hook_id | 场景 | 时间 | 语言难度 | 触发条件 |
|---------|------|------|---------|---------|
| `hook_frauenkirche_first_visit` | 第一次进入教堂 | 任意 | A1 | `first_visit` |
| `hook_frauenkirche_tower_question` | 询问塔楼开放 | 白天 | A1 | `approach_tower` |
| `hook_frauenkirche_history_tour` | 神父亲自导览 | 下午 | A2 | `ask_for_tour` (好感度>20) |
| `hook_frauenkirche_teufelstritt` | 魔鬼脚印传说 | 任意 | A2 | `notice_teufelstritt` |
| `hook_frauenkirche_mass_invite` | 邀请参加弥撒 | 周日上午 | A1 | `weekend_morning` |
| `hook_frauenkirche_confession_intro` | 介绍告解/倾诉 | 周三下午 | B1 | `seelsorge_available` |
| `hook_frauenkirche_organ_music` | 管风琴演奏欣赏 | 周末 | A2 | `organ_playing` |
| `hook_frauenkirche_christmas` | 圣诞特别对话 | 12月 | A2 | `december_visit` |

每个对话树 3-5 轮，含选项分支和中德英三语。

### 3.4 需要生成的知识卡

| card_id | 标题 | 类别 |
|---------|------|------|
| `knowledge_frauenkirche_arch` | 为什么 Frauenkirche 屋顶是绿色的? | Geschichte |
| `knowledge_frauenkirche_teufelstritt` | 魔鬼脚印的传说 | Legende |
| `knowledge_frauenkirche_gothic_brick` | 德国最大的砖砌哥特式教堂 | Architektur |
| `knowledge_frauenkirche_wittelsbach` | Wittelsbach 家族与 Frauenkirche | Geschichte |
| `knowledge_frauenkirche_ww2` | 二战中的 Frauenkirche | Geschichte |
| `knowledge_frauenkirche_renovation` | 1990 年代大修缮 | Kultur |
| `knowledge_frauenkirche_domes` | 为什么叫"Frauenkirche" | Religion |

### 3.5 需要生成的剧情/任务

| quest_id | 类型 | 标题 | 简述 |
|---------|------|------|------|
| `quest_frauenkirche_tower_climb` | exploration | 登顶圣母教堂 | 爬 99 阶到塔顶,拍摄慕尼黑全景 |
| `quest_frauenkirche_teufelstritt_find` | treasure_hunt | 寻找魔鬼脚印 | 在教堂入口找到魔鬼脚印,学习传说 |
| `quest_frauenkirche_organ_listen` | cultural | 聆听管风琴 | 在周末弥撒时聆听管风琴演奏 |
| `quest_frauenkirche_pater_interview` | dialogue | 与神父对话 | 用德语与 Pater Johann 完成一次完整对话 |
| `quest_frauenkirche_mass_experience` | cultural | 体验弥撒 | 参加一次周日弥撒(10:00) |
| `quest_frauenkirche_christmas_eve` | seasonal | 圣诞子夜弥撒 | 12 月 24 日参加 Christmas 弥撒(限时) |

### 3.6 打卡目标

| checkin_id | 类型 | 名称 | 奖励 |
|-----------|------|------|------|
| `checkin_frauenkirche_first_enter` | location | 第一次走进圣母教堂 | culture_xp:3, mood:2 |
| `checkin_frauenkirche_tower_top` | physical | 登顶北塔 | culture_xp:8, energy:-8 |
| `checkin_frauenkirche_mass_sun` | scheduled | 周日弥撒参与 | culture_xp:6, mood:4 |
| `checkin_frauenkirche_teufelstritt` | discover | 找到魔鬼脚印 | culture_xp:5 |
| `checkin_frauenkirche_photo_sunset` | photo | 拍摄日落教堂 | mood:5, photo_unlock:true |

---

## 4. 生成器架构

### 4.1 整体结构

```
frontend/poi-generator/                    # 独立 Web 生成器
├── index.html                             # 入口
├── package.json                           # 依赖
├── vite.config.js                         # 构建配置
└── src/
    ├── main.js
    ├── App.vue                            # 主布局
    ├── style.css
    ├── components/
    │   ├── POISelector.vue                # POI 列表 / 新建 POI
    │   ├── POIInfoForm.vue                # POI 基础信息编辑
    │   ├── ImageGenerator.vue             # 图片生成面板
    │   ├── NPCGenerator.vue               # NPC 生成面板
    │   ├── DialogueEditor.vue             # 对话树编辑/预览
    │   ├── KnowledgePanel.vue             # 知识卡管理
    │   ├── QuestPanel.vue                 # 剧情/任务管理
    │   ├── CheckinPanel.vue               # 打卡目标管理
    │   ├── DataViewer.vue                 # 数据预览/检查
    │   └── OutputPanel.vue                # 导出/保存面板
    ├── stores/
    │   └── generator.js                   # Pinia store
    ├── core/
    │   ├── schema.js                      # 所有 schema 定义
    │   ├── templates.js                   # 各类型默认模板
    │   ├── apiClient.js                   # 调用后端 AI API
    │   └── fileSaver.js                   # 归档到正确目录
    └── assets/                            # 生成器自身 UI 资源

backend/poi-generator/                     # Python FastAPI 后端
├── main.py                                # FastAPI 入口
├── requirements.txt                       # 依赖
├── config.py                              # 配置(API key 等)
├── routers/
│   ├── text.py                            # LLM 文本生成路由
│   ├── image.py                           # 图片生成路由
│   └── save.py                            # 文件保存路由
└── services/
    ├── llm_service.py                     # DashScope LLM 调用封装
    ├── image_service.py                   # matrix 图片生成封装
    └── file_service.py                    # 文件系统操作
```

### 4.2 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 前端框架 | Vue 3 + Vite | 与主项目保持一致 |
| 状态管理 | Pinia | 与主项目保持一致 |
| UI 组件 | 自建(16-bit 像素风格) | 与游戏视觉风格统一 |
| 后端代理 | Python FastAPI | 与 DashScope SDK 原生集成 |
| AI 文本 | Qwen-Plus / Qwen3-Max | 通过 DashScope Python SDK |
| AI 图片 | matrix_generate_image | 通过 `mavis mcp call` |
| 存储 | 本地文件系统 | 直接写入 `assets/` + `content/drafts/` |

### 4.3 数据流

```
用户输入 POI 名称/坐标
    ↓
[基础信息面板] → 手动填写/LLM 辅助
    ↓
[生成图片] → AI 图片 API → 预览 → 确认 → 保存到 assets/scenes/munich/{poi_id}/
    ↓
[生成 NPC] → LLM → NPC 档案 + 立绘 → 预览 → 保存到 content/drafts/npcs/
    ↓
[生成对话] → LLM → 对话树(中/德/英) → 编辑 → 保存
    ↓
[生成知识卡] → LLM → 知识卡片列表 → 编辑 → 保存
    ↓
[生成剧情/任务] → LLM → 任务链 → 编辑 → 保存
    ↓
[生成打卡/门票/时间] → LLM + 模板 → 预览 → 保存
    ↓
[预览所有数据] → 树形结构查看器 → 检查完整性
    ↓
[导出] → 写入 drafts/ 对应目录 + source_records.json
```

### 4.4 后端 API 设计 (FastAPI)

```
POST /api/generate/text              # 调用 LLM 生成文本
  body: { prompt, system_prompt, model: "qwen-plus"|"qwen3-max" }
  response: { text, model_used, tokens }

POST /api/generate/image             # 调用 AI 生成图片
  body: { prompt, aspect_ratio, style, reference_image? }
  response: { url, local_path }

POST /api/generate/batch             # 批量生成(一个POI所有内容)
  body: { poi_id, poi_name, address, lat, lng, type, city }
  response: { job_id, items: [...] }

GET  /api/generate/batch/{job_id}    # 查询批量任务进度
  response: { status, progress, results }

POST /api/save                       # 保存生成的数据到本地文件
  body: { file_path, content, is_draft: true }
  response: { success, path }

GET  /api/pois                       # 获取现有 POI 列表(从 drafts 读取)
GET  /api/pois/{poi_id}              # 获取某个 POI 的现有数据
```

---

## 5. UI 设计概览

### 5.1 布局

```
┌──────────────────────────────────────────────────────────┐
│  🏗️ POI 内容生成器 · gagaToday         [保存] [导出]    │
├──────────────────┬───────────────────────────────────────┤
│  📍 POI 选择     │  [当前 POI: Frauenkirche]            │
│  ┌────────────┐  ├───────────────────────────────────────┤
│  │ ○ Marienpl.│  │  Tab: [基础信息] [图片] [NPC] [对话]  │
│  │ ● Frauenk. │  │       [知识卡] [剧情] [打卡] [预览]  │
│  │ ○ Viktual. │  │                                       │
│  │ ○ Museum   │  │  ┌───────────────────────────────┐   │
│  │ ○ Garten   │  │  │  当前标签页内容              │   │
│  │ ○ Nymphen. │  │  │  (表单/预览/编辑)            │   │
│  │ ○ BMW Welt │  │  │                               │   │
│  │ ○ Olympia  │  │  │                               │   │
│  │ ○ Allianz  │  │  └───────────────────────────────┘   │
│  │ + 新建 POI  │  │                                       │
│  └────────────┘  │  [🤖 一键生成全部] [✅ 完整性检查]    │
├──────────────────┴───────────────────────────────────────┤
│  状态栏: 已生成 3/15 项 · 最后保存: 刚才                │
└──────────────────────────────────────────────────────────┘
```

### 5.2 关键交互

1. **图片生成面板**: 展示所有需要生成的图片列表，每个带"生成"按钮和预览缩略图
2. **对话编辑器**: 树形结构展示多轮对话，支持增删改节点
3. **批量生成**: 点击"一键生成全部"→ 按顺序依次调用 AI → 实时显示进度
4. **完整性检查**: 检查是否所有必要字段都已填充，显示缺失项

---

## 6. 实施计划

### Phase 1: 基础框架 + Frauenkirche 完整示范 (3-5 天)

| 天数 | 任务 |
|------|------|
| Day 1 | 搭建 FastAPI 后端骨架 (DashScope LLM + matrix 图片服务) |
| Day 2 | 搭建 Vite + Vue 3 前端骨架, Pinia store, POI 选择器 |
| Day 3 | 实现基础信息表单 + AI 文本生成 + 图片生成面板 |
| Day 4 | 实现 NPC 生成 + 对话树生成 + 知识卡生成 |
| Day 5 | 实现导出系统(写入 drafts/ + assets/) + Frauenkirche 端到端验证 |

### Phase 2: 功能完善 (2-3 天)

| 天数 | 任务 |
|------|------|
| Day 6 | 实现打卡目标 + 剧情任务 + 门票/时间生成 |
| Day 7 | 对话树编辑器(可视化增删改) + 预览检查器 |
| Day 8 | 完整性检查 + 数据校验 + 批量生成流水线 |

### Phase 3: 批量生产 (2 天)

| 天数 | 任务 |
|------|------|
| Day 9 | UI 润色(16-bit 像素风格) + 错误处理 + 进度提示 |
| Day 10 | 批量生成 Marienplatz / Viktualienmarkt / Deutsches Museum / Englischer Garten / Schloss Nymphenburg + MVP 5 POI |

---

## 7. 已确认决策

| 问题 | 决策 |
|------|------|
| 图片风格 | **16-bit 像素风格**,与 ART_ASSETS.md 规范一致 |
| 图片生成工具 | `matrix_generate_image`（通过 `generate_art.py` 方案） |
| 后端代理 | **Python FastAPI**，与 DashScope SDK 原生集成 |
| AI 文本模型 | Qwen-Plus / Qwen3-Max (按任务复杂度选择) |
| 对话树复杂度 | 3-5 轮，含分支选项 |
| 首批 POI | **全部**：先做 **Frauenkirche 示范** → Marienplatz / Viktualienmarkt / Deutsches Museum / Englischer Garten / Schloss Nymphenburg + 现有 MVP 5 个 POI |

---

## 8. 与现有系统的集成

```
生成器输出目录结构:

frontend/src/content/drafts/
└── poi_generator/                    # 生成器专属 drafts
    └── {city}_{poi_id}_{date}/
        ├── poi_info.draft.json
        ├── npc_profiles.draft.json
        ├── dialogues.draft.json
        ├── dialogue_hooks.draft.json
        ├── knowledge_cards.draft.json
        ├── history_stories.draft.json
        ├── checkin_targets.draft.json
        ├── treasure_items.draft.json
        ├── opening_hours.draft.json
        ├── ticket_prices.draft.json
        ├── quests.draft.json
        ├── scene_events.draft.json
        ├── source_records.json
        └── validation_report.json   # 自动生成的校验报告

assets/
└── scenes/
    └── munich/
        └── {poi_id}/                # 与 POI ID 对应
            ├── exterior/
            ├── interior/
            ├── tower/               # (可选)
            └── _thumbnails/
```

生成内容 → 人工审查 → 批准后移入 `content/munich/` + `assets/` 对应位置。
