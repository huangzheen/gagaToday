# GermanLearning 项目实施方案 v2.0

> 一款游戏化 + AI 语音 + 地图 RPG 的德福备考应用
> 文档版本: v2.0  ·  2026-06-21  ·  v2 主要变化:德福定位 + "走遍德国"地图玩法 + Web→Desktop 迁移 + 用户系统预留

---

## 1. 项目定位

**一句话**: 玩家用德语"走遍德国"——通过完成各地的生活任务解锁城市地图,在沉浸式 AI 语音对话中备考德福,同时学习德国文化、饮食、工商业、旅游知识。

**三大核心体验**:
1. **德语学习** —— 沉浸式对话,练听说(德福 4 项中的"听"+"说")
2. **文化认知** —— 解锁城市百科卡(文化/经济/饮食/旅游)
3. **RPG 体验** —— 地图点亮、关卡解锁、角色养成

**目标用户**:
- 主要: 准备去德国留学的中国学生(德福 TDN 3-5,目标 B2-C1)
- 次要: 在德华人、移民、欧标学习者

**目标考试**: TestDaF(德福),对齐 B2-C1 水平
**德福 4 项对齐**:
- 阅读 → 城市百科的"信息检索"任务(后期)
- 听力 → NPC 语音(已经在做)
- 口语 → 玩家语音对话(核心)
- 写作 → 反馈卡的"书面表达"任务(后期)

---

## 2. 产品形态

### 2.1 用户场景(主流程)

```
玩家打开游戏
  ↓
看到德国地图(2D 像素手绘风)
  - 已解锁城市亮起
  - 当前位置有光标
  - 当前任务显示气泡
  ↓
点击城市 → 进入城市章节
  ↓
看到该城市的关卡列表
  ↓
选择关卡(例:在柏林咖啡馆点咖啡)
  ↓
开始和 NPC 语音对话
  ↓
每回合:用户录音 → AI 评判 + NPC 语音回复
  ↓
完成关卡 → 反馈卡 + 城市百科卡 + 解锁下一关
  ↓
返回地图 → 点亮新区域
  ↓
可以自由探索其他已解锁城市
```

### 2.2 三个层级的内容

**第一层: 地图(主界面)**
- 德国 16 州 + 主要城市(Phase 1-4 逐步点亮)
- 显示玩家当前位置、已解锁城市
- 点击城市进入章节

**第二层: 城市章节**
- 一个城市 = 1 章节 = 3-5 个关卡
- 城市介绍(历史、人口、特色)
- 关卡列表(完成度)
- 城市百科(文化/经济/饮食/旅游/教育)

**第三层: 关卡(具体生活场景)**
- 1 个场景 = 1 个 NPC + 5-15 回合对话
- 完成解锁下一关 + 城市百科更新

### 2.3 回合制对话(核心技术)

每回合交互流程(非实时流式):

```
玩家点击"说话"按钮
  ↓
浏览器录音 (Web Audio API, 16kHz mono PCM)
  ↓
录音上传后端
  ↓
后端 3 件事:
  1. Fun-ASR 1.5 → 文字转写
  2. Qwen2-Audio-7B → 发音+语法评估(直接吃音频)
  3. Qwen-Plus → 基于剧本生成 NPC 回复
  ↓
NPC 回复文字 → CosyVoice 3.5 → 流式 TTS 音频
  ↓
返回前端:
  - 玩家说的话(转写)
  - 评估反馈
  - NPC 回复文字
  - NPC 语音音频
  ↓
前端播放 NPC 音频 + 显示反馈 + 显示对话
  ↓
玩家继续(下一回合,直到关卡完成)
```

**关键决策**: 回合制(turn-based)而非实时(streaming)——避开实时发音纠错的技术难点,降低延迟敏感度,工程更简单。

---

## 3. 技术架构

### 3.1 全栈图

```
┌─────────────────────────────────────────────────────────┐
│  客户端(浏览器 → 后期 Tauri Desktop)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Phaser 3    │  │  React UI    │  │  Web Audio   │  │
│  │  (游戏画面)  │  │  (对话框)    │  │  (录音)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│       ↑                   ↑                  ↑           │
│       └───────────────────┴──────────────────┘           │
│                          ↓                                │
│              ┌──────────────────────┐                    │
│              │  Core (业务逻辑层)   │ ← 后期 Godot 复用  │
│              │  - 对话状态机        │                    │
│              │  - 剧本加载器        │                    │
│              │  - 用户进度          │                    │
│              └──────────────────────┘                    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / WebSocket
                       ↓
┌─────────────────────────────────────────────────────────┐
│  后端 FastAPI (Python)                                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │
│  │ API 层 │  │ 对话   │  │ 用户   │  │ 剧本   │         │
│  │ (REST) │  │ 引擎   │  │ 系统   │  │ 存储   │         │
│  └────────┘  └────────┘  └────────┘  └────────┘         │
│       ↓                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ IndexedDB   │  │ (Phase 2+)  │  │             │    │
│  │ (MVP 存)    │  │ PostgreSQL  │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │ DashScope SDK
                       ↓
┌─────────────────────────────────────────────────────────┐
│  阿里云百炼(DashScope)                                   │
│  ├─ LLM: Qwen-Plus / Qwen3-Max(对话+反馈)              │
│  ├─ TTS: CosyVoice 3.5 Plus(流式,德语,150ms 首包)     │
│  ├─ ASR: Fun-ASR 1.5(德语,30 语种)                    │
│  └─ 发音评估: Qwen2-Audio-7B(直接吃音频+文字评估)     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 关键架构决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 前端游戏引擎 | **Phaser 3** | 2D 像素友好,Web 调试方便,后期 Tauri 打包 |
| 前端 UI 框架 | **React + TypeScript** | 生态最大,后期可换 SolidJS/Vue 几乎无成本 |
| 后端 | **FastAPI (Python)** | 对接 DashScope SDK 方便 |
| MVP 数据存储 | **IndexedDB** (浏览器) | 单机够用,无需后端 |
| 后期数据存储 | **PostgreSQL** (云端) | 多用户、跨设备 |
| 后期 Desktop 打包 | **Tauri** | 同一份 TypeScript 代码,几乎 0 改动 |
| 终极 Desktop | **Godot 4** (可选) | 重写游戏渲染层,后端不动 |
| 美术工具 | **Aseprite / LibreSprite** | 像素动画标准 |

### 3.3 业务层与渲染层分离(为后期迁移准备)

```typescript
// frontend/src/core/  ← 业务逻辑(可复用到 Godot)
//   ├── dialogue-state.ts      // 对话状态机
//   ├── scenario-loader.ts     // 剧本加载
//   ├── progress-tracker.ts    // 进度追踪
//   ├── error-collector.ts     // 错题收集
//   ├── vocabulary-tracker.ts  // 词汇管理
//   └── api-client.ts          // API 客户端

// frontend/src/game/  ← 渲染层(Phaser,后期换 Godot 时只重写这里)
//   ├── scenes/  (map-scene, city-scene, dialogue-scene)
//   ├── sprites/  (角色、场景)
//   └── animations/

// frontend/src/ui/  ← UI 层(React)
//   ├── dialogue-box.tsx
//   ├── feedback-card.tsx
//   ├── city-encyclopedia.tsx
//   └── map-overlay.tsx
```

**为什么这样分**: 后期从 Phaser 切 Godot,只需要重写 `game/`,业务逻辑和 API 客户端**一行不改**。

---

## 4. 用户系统设计(框架预留,MVP 不实现)

### MVP 状态
- 用户无感知,用本地 UUID
- 所有"API 调用"实际写到 IndexedDB
- 单机游戏

### Phase 2 升级
- 加入注册/登录(邮箱/Google/Apple)
- 数据同步到 PostgreSQL
- 跨设备进度

### 数据库 Schema(从一开始就这么设计)

```sql
-- 用户表
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  name VARCHAR,
  cefr_level VARCHAR,  -- A1/A2/B1/B2/C1
  target_test VARCHAR,  -- TestDaF/Goethe/DSH
  created_at TIMESTAMP,
  last_active_at TIMESTAMP
)

-- 关卡进度
user_progress (
  user_id UUID REFERENCES users(id),
  scenario_id VARCHAR,
  status VARCHAR,  -- not_started/in_progress/completed
  score INTEGER,
  attempts INTEGER,
  first_completed_at TIMESTAMP,
  last_attempted_at TIMESTAMP,
  PRIMARY KEY (user_id, scenario_id)
)

-- 错题本
user_errors (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  scenario_id VARCHAR,
  error_type VARCHAR,  -- grammar/vocabulary/pronunciation
  user_input TEXT,
  suggested_fix TEXT,
  explanation TEXT,
  created_at TIMESTAMP
)

-- 词汇本
user_vocabulary (
  user_id UUID REFERENCES users(id),
  word VARCHAR,
  translation JSON,  -- {zh, en, de_def}
  learned_at TIMESTAMP,
  review_count INTEGER,
  next_review_at TIMESTAMP,  -- 间隔重复算法
  PRIMARY KEY (user_id, word)
)

-- 学习统计
user_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  scenario_id VARCHAR,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  rounds_count INTEGER,
  errors_count INTEGER
)
```

### API 设计(从一开始就这样,MVP 用本地 stub)

```
GET    /api/v1/users/{user_id}
GET    /api/v1/users/{user_id}/progress
POST   /api/v1/users/{user_id}/progress
GET    /api/v1/users/{user_id}/errors
POST   /api/v1/users/{user_id}/errors
GET    /api/v1/users/{user_id}/vocabulary
POST   /api/v1/users/{user_id}/vocabulary
```

**MVP 实现**: `api-client.ts` 内部根据环境变量决定调用真实 API 还是 IndexedDB。**业务代码完全不知道差别**。

---

## 5. "走遍德国"地图内容设计

### 5.1 城市内容布局(全景)

| 联邦州 | 代表城市 | 主题 | 难度 | 文化卡片类别 |
|--------|---------|------|------|------------|
| Berlin | 柏林 | 政治/文化/街区 | A1-B1 | 历史/文化/艺术 |
| Bayern | 慕尼黑 | 工业/啤酒/阿尔卑斯 | A2-B1 | 工业/饮食/旅游 |
| Hamburg | 汉堡 | 港口/媒体/音乐 | A2-B1 | 经济/媒体/海事 |
| NRW | 科隆/杜塞尔多夫 | 商业/艺术/工业 | B1-B2 | 商业/艺术/工业 |
| Hessen | 法兰克福 | 金融/交通 | B1-B2 | 金融/交通/会展 |
| Baden-W. | 海德堡/斯图加特 | 学术/汽车 | B1-B2 | 教育/工业/科研 |
| Sachsen | 莱比锡/德累斯顿 | 历史/音乐 | B2 | 历史/艺术/建筑 |
| Nieders. | 汉诺威/沃尔夫斯堡 | 工业/汽车 | B2 | 工业/会展 |
| ... | ... | ... | ... | ... |

### 5.2 每城市内容包(3-5 关)

**Phase 1 (柏林 5 关)**:
1. 火车站初到(A1): 问路、买票
2. 咖啡馆点单(A1): 本文档示例
3. 超市购物(A2): 找商品、付款
4. 看医生(B1): 预约、描述症状
5. 朋友家做客(B1): 自我介绍、聊爱好

**Phase 2 (柏林 + 慕尼黑 + 汉堡 各 5 关)**: 15 关

**Phase 3 (5 个城市各 5 关)**: 25 关

**Phase 4 (10 个城市各 5 关)**: 50 关

**Phase 5 (完整版 16 州 60-100 关)**: 德福 TDN 4-5

### 5.3 关卡内容结构

```yaml
场景基本信息:
  scenario_id: "berlin_cafe_01"
  scenario_name: "在柏林咖啡馆点单"
  city: Berlin
  cefr_level: A1
  textbook_ref: "Menschen A1, Lektion 3"

学习目标:
  德语: 5 个核心表达 + 2 个语法点
  文化: 1 个德国咖啡馆文化点
  城市知识: 柏林咖啡馆文化(独立小店 vs 连锁)

NPC:
  name: "Anna (Kellnerin)"
  性格: freundlich, geduldig
  语速: langsam (A1)
  立绘: anna_neutral.png, anna_smile.png, ...

对话流程:
  Round 1-6: 主对话
  Round 7: 自由延伸(可选)

完成后:
  反馈卡: 语法错误 + 发音问题 + 5 个新表达
  城市百科卡: 柏林咖啡馆文化
  解锁: 下一关
```

### 5.4 城市百科卡(文化融入)

**结构化数据 + 视觉卡片**:
```yaml
encyclopedia_card:
  city: "Berlin"
  category: "Kultur"  # Kultur/Wirtschaft/Essen/Tourismus/Bildung
  title: "Berliner Kaffeekultur"
  image: berlin_cafe_history.png
  
  content:
    sections:
      - heading: "历史"
        text: "柏林的咖啡馆文化起源于 17 世纪..."
      - heading: "特色"
        text: "柏林咖啡馆以独立小店为主,和维也纳、巴黎不同..."
      - heading: "推荐"
        text: "Café Einstein, Bonanza Coffee Roasters..."
  
  keywords:  # 德语新词
    - "die Kaffeekultur"
    - "unabhängig"
    - "die Röstung"
```

**LLM 辅助生成**: 文化卡片初稿用 LLM 生成,你审校——能省 50% 时间。

---

## 6. 阿里云 API 选型(详见 API_STACK.md)

| 用途 | 模型 | 用途场景 | 价格(估算) |
|------|------|---------|------------|
| LLM 对话 | Qwen-Plus | NPC 角色对话 | ¥0.0004/千 token |
| LLM 高级 | Qwen3-Max | 反馈卡生成 | ¥0.003/千 token |
| TTS | CosyVoice 3.5 Plus | NPC 语音(流式) | ~¥0.0001/字 |
| ASR | Fun-ASR 1.5 | 用户语音转写 | ~¥0.006/15秒 |
| 发音评估 | Qwen2-Audio-7B | 直接吃音频评估 | 暂未公开,免费额度够用 |
| 城市百科生成 | Qwen-Plus | 文化卡片初稿 | 边际成本极低 |

**单关成本**: ¥0.08-0.15
**完整玩 1 城市(5 关)**: ¥0.4-0.75
**完整 A1(柏林 5 关)**: ¥0.4-0.75
**Phase 2(3 城市 15 关)**: ¥1.2-2.3

**几乎可忽略**,无需优化。

---

## 7. 开发路线图

### Phase 0: 技术验证(1-2 周)

**目标**: 跑通所有阿里云 API,确认效果

- [ ] 阿里云账号 + DashScope API Key
- [ ] Python 脚本: 录音 → ASR → Qwen → CosyVoice → 播放
- [ ] Qwen2-Audio 德语评估实测(5 段不同水平德语)
- [ ] 选第一本教材(*Menschen A1*),拆第 1 关剧本
- [ ] **Decision Gate**: 决定是否进入 Phase 1

### Phase 1: MVP 柏林 1 关(4-6 周)

**目标**: 1 个完整关卡可玩,2D 像素风,基础反馈

- [ ] 前端框架: Vite + React + TypeScript + Phaser 3
- [ ] 后端: FastAPI + 阿里云 API 封装
- [ ] 美术: 柏林咖啡馆场景 + Anna 立绘(6 张) + UI 元素
- [ ] 业务层: 对话状态机 + 剧本加载器 + 进度追踪
- [ ] **验收**: 1 个关卡(5-6 回合),完整反馈卡,愿意再玩

### Phase 2: 柏林 5 关 + 慕尼黑/汉堡 5 关(6-8 周)

**目标**: 3 城市 15 关,城市百科卡

- [ ] 柏林补全(4 关)
- [ ] 慕尼黑 5 关(工业/啤酒节)
- [ ] 汉堡 5 关(港口/媒体)
- [ ] 城市百科系统(LLM 生成初稿,人工审校)
- [ ] 错题本 + 词汇本
- [ ] **验收**: 完整 1 个州(Berlin)的体验

### Phase 3: 用户系统 + 完整地图(8-12 周)

**目标**: 注册/登录,跨设备,5-10 个城市

- [ ] 后端 PostgreSQL + 阿里云 ECS 部署
- [ ] 用户系统(注册/登录/同步)
- [ ] Tauri Desktop 打包(可选)
- [ ] 5-10 个城市
- [ ] **验收**: 完整学习闭环,跨设备进度

### Phase 4: 德福备考专题(8-12 周)

**目标**: B2-C1 难度,德福 TDN 4-5 准备

- [ ] 留学场景关卡(大学注册、租房、银行开户)
- [ ] 阅读/写作训练(城市百科扩展)
- [ ] 德福模拟题(对话式而非纸质)
- [ ] **验收**: 用户实测德福能到 TDN 4

### Phase 5: 完整版(6-12 个月)

- [ ] 全 16 州 60-100 关
- [ ] Godot 4 重写(可选,更好的游戏体验)
- [ ] 移动端(iOS/Android via Capacitor 或 Tauri)
- [ ] 商业化(订阅?一次性买断?)

---

## 8. 美术资源(详见 ART_ASSETS.md)

**MVP 第 1 关需要**:
- 角色立绘 6 张
- 场景背景 1 张
- UI 元素 15-20 个
- 像素字体 1 套

**预估工作量**:
- 熟练画师: 3-5 天
- 新手: 1-2 周学习 Aseprite

---

## 9. 关键风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Qwen2-Audio 德语评估不准 | 反馈差 | 改用 wav2vec2-xlsr-53-german + LLM 组合 |
| LLM 跳出剧本 | 教学失控 | 严格 system prompt + 输出 token 限制 + 输出 schema |
| 城市百科工作量爆炸 | 进度慢 | LLM 生成初稿 + 模板填充,80% 结构化 |
| 美术跟不上 | 视觉差 | 留 placeholder,1 关做 1 城市背景慢慢补 |
| 德福内容专业度高 | 需要专业审校 | 找德语专业朋友做内容审校(0 成本友情价) |
| 单人维护成本高 | 项目烂尾 | 设定每 4 周一个 milestone,达不到就缩小范围 |

---

## 10. 我希望和用户核对的几个点

✅ 已确认:
- 目标:德福备考
- 客户端:Web 先,后期 Tauri Desktop
- 用户系统:框架预留,MVP 不做
- 美术:用户自画
- 目标用户:准备去德国留学
- 核心玩法:"走遍德国"地图 + 文化融入

⏳ 待确认:
1. 教材确认:用 *Menschen A1* 起步?
2. 城市选择:第 1 个城市锁定柏林(政治/文化主题),同意?
3. 美术学习成本:你是否熟悉 Aseprite?不熟的话需要 1-2 周学习
4. 内容工作量:你预计每周能投入多少小时到剧本创作?(我推荐 5-10 小时/周)
5. 是否需要找德语专业朋友做内容审校?
6. 是否要"加好友 / 看其他玩家进度"这种社交功能?(影响 MVP 范围)

---

## 11. 下一步(本周)

1. **今天-明天**: 我跑通 Phase 0 的 Python demo 脚本
2. **本周内**: 拆 *Menschen A1* 第 1 关(柏林咖啡馆)完整 JSON 剧本
3. **等你审校**: 剧本 + 美术清单(我会单独发一个文档给你画)
4. **决策 Gate**: 你 review 后决定是否进入 Phase 1

**先按 Phase 0 走,跑通 demo 再说。** 我现在开始写 demo 脚本,你有空确认上面的待确认点。

要不要我现在就开干 Phase 0?
