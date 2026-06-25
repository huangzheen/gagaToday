> ⚠️ **本文档为历史参考，未反映当前实现**（标记于 2026-06-25 文档收敛）
>
> 当前架构见 [README.md](../../README.md) 和 [docs/ARCHITECTURE.md](../ARCHITECTURE.md)。
>
# 架构设计(ARCHITECTURE)

> Web → Desktop 迁移设计 + 用户系统预留 + 业务层与渲染层分离
> 版本: v2.0  ·  2026-06-21(新增:三轨并行学习 + 双语切换机制 + RPG 顶视图)

---

## 0. v2.0 修订说明

**相对 v1.0(TestDaF 备考)的核心变化**:
- 主角定位:从"成年人 TestDaF 备考者" → **15-16 岁中考毕业生,德国国际高中留学**
- 学习内容:从"单一德语 B2-C1" → **三轨并行**(德语 + A-levels + 雅思)
- 双语机制:新增 **NPC 语言偏好 + 玩家语言切换**(德语为主、英文兜底)
- 游戏类型:从"对话 app" → **RPG**(顶视图探索 + 角色属性 + 任务系统 + 多结局)
- 学习路径:从"我方写" → **统一 LearningUnit 接口 + 另一个 agent 填内容**

**本文档核心架构(三层 + 抽象 API + Web→Desktop 路径)仍然适用**,新设计细节见 `docs/GAME_DESIGN.md`。

| 新设计模块 | 对应章节 |
|----------|---------|
| 三轨并行学习(德语 / A-levels / 雅思) | §13 新增 |
| 双语切换机制(NPC lang_pref + 玩家选择) | §14 新增 |
| RPG 角色属性系统 | §15 新增 |
| 走遍德国地图 + 文化百科 | §16 新增 |
| 学习路径接口(LearningUnit 抽象) | §17 新增 |
| 结局多线 | §18 新增 |

---

## 1. 设计目标

| 目标 | 解决什么 |
|------|---------|
| **Web 优先** | 部署简单、调试快、移动端可玩 |
| **后期转 Desktop 容易** | 不重写业务代码 |
| **用户系统后期接入容易** | MVP 不做,但接口和 schema 提前定 |
| **内容(剧本)与代码分离** | 美术/内容创作者不写代码也能更新 |
| **AI API 切换容易** | 后期可换开源 LLM/TTS(脱钩云服务) |

---

## 2. 三层架构(为迁移准备)

```
┌─────────────────────────────────────────────┐
│  Rendering Layer (Phaser 3, 后期可换 Godot)  │
│  - 场景渲染                                    │
│  - 角色立绘显示                                │
│  - 动画                                        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Core Business Layer (与渲染解耦)            │
│  - 对话状态机                                  │
│  - 剧本加载器                                  │
│  - 进度追踪                                    │
│  - 错题本                                      │
│  - 词汇本                                      │
│  - 反馈卡生成                                  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  API Client Layer (抽象数据来源)              │
│  - 后端 REST 调用 / IndexedDB stub            │
│  - 阿里云 DashScope 客户端                    │
│  - 错误处理 + 重试                             │
└─────────────────────────────────────────────┘
```

**关键原则**:
- **Core 不知道 Phaser 存在**(纯 TypeScript,无 DOM/Canvas 依赖)
- **API Client 不知道后端存在**(内部根据环境切换真实 API / IndexedDB)
- **渲染层只调用 Core,不直接调 API**

---

## 3. 目录结构

```
german-learning/
├── docs/                       # 文档
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── users.py
│   │   │   ├── progress.py
│   │   │   ├── errors.py
│   │   │   ├── vocabulary.py
│   │   │   └── dialogue.py
│   │   ├── services/
│   │   │   ├── asr.py          # Fun-ASR 封装
│   │   │   ├── tts.py          # CosyVoice 封装
│   │   │   ├── llm.py          # Qwen 封装
│   │   │   └── eval.py         # Qwen2-Audio 封装
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── progress.py
│   │   │   ├── error.py
│   │   │   └── vocabulary.py
│   │   ├── data/
│   │   │   ├── scenarios/      # 剧本 JSON 文件
│   │   │   │   ├── berlin_cafe_01.json
│   │   │   │   ├── munich_oktoberfest_01.json
│   │   │   │   └── ...
│   │   │   └── encyclopedia/   # 城市百科数据
│   │   │       ├── berlin.json
│   │   │       └── ...
│   │   ├── core/
│   │   │   ├── dialogue_engine.py
│   │   │   ├── scenario_loader.py
│   │   │   └── progress_tracker.py
│   │   └── db.py               # 数据库连接
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── frontend/                   # Web 前端(Vite + React + Phaser)
│   ├── src/
│   │   ├── core/               # 业务层(可复用到 Godot)
│   │   │   ├── dialogue-state.ts
│   │   │   ├── scenario-loader.ts
│   │   │   ├── progress-tracker.ts
│   │   │   ├── error-collector.ts
│   │   │   ├── vocabulary-tracker.ts
│   │   │   ├── feedback-generator.ts
│   │   │   └── api-client.ts
│   │   ├── game/               # 渲染层(Phaser,后期换 Godot 时只重写)
│   │   │   ├── main.ts
│   │   │   ├── scenes/
│   │   │   │   ├── BootScene.ts
│   │   │   │   ├── MapScene.ts        # 德国地图
│   │   │   │   ├── CityScene.ts       # 城市章节
│   │   │   │   └── DialogueScene.ts   # 关卡对话
│   │   │   ├── sprites/
│   │   │   │   ├── NPCSprite.ts
│   │   │   │   └── ...
│   │   │   └── animations/
│   │   ├── ui/                 # React UI 层
│   │   │   ├── App.tsx
│   │   │   ├── components/
│   │   │   │   ├── DialogueBox.tsx
│   │   │   │   ├── FeedbackCard.tsx
│   │   │   │   ├── CityEncyclopedia.tsx
│   │   │   │   ├── MapOverlay.tsx
│   │   │   │   ├── MicButton.tsx
│   │   │   │   └── ...
│   │   │   └── pages/
│   │   │       ├── HomePage.tsx
│   │   │       ├── GamePage.tsx
│   │   │       └── ReviewPage.tsx
│   │   ├── audio/              # 音频处理
│   │   │   ├── recorder.ts     # Web Audio API 录音
│   │   │   └── player.ts       # 音频播放
│   │   ├── api/                # API 客户端实现
│   │   │   ├── backend-client.ts
│   │   │   └── local-stub.ts   # IndexedDB 实现
│   │   ├── store/              # 状态管理(Zustand / Redux)
│   │   │   ├── user-store.ts
│   │   │   └── game-store.ts
│   │   └── types/              # TypeScript 类型定义
│   │       ├── scenario.ts
│   │       ├── user.ts
│   │       └── ...
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── assets/                     # 美术资源
│   ├── characters/
│   ├── scenes/
│   ├── ui/
│   ├── cities/
│   ├── map/
│   └── fonts/
├── shared/                     # 前后端共享
│   ├── types/                  # TypeScript 类型 / Pydantic 模型
│   │   ├── scenario.py
│   │   ├── user.py
│   │   └── ...
│   └── schemas/
└── README.md
```

---

## 4. Core 业务层 API(关键)

### 4.1 DialogueState(对话状态机)

```typescript
// core/dialogue-state.ts

export interface DialogueRound {
  roundId: string;
  type: 'npc_starts' | 'player_responds' | 'free';
  npcSays?: string;
  expectedPlayerSays?: string[];
  hints?: string[];
}

export interface DialogueContext {
  scenarioId: string;
  currentRoundIndex: number;
  rounds: DialogueRound[];
  history: Array<{ role: 'npc' | 'player'; text: string; audioUrl?: string }>;
  learningPoints: string[];  // 已学过的
  errors: Array<{ type: string; content: string; fix: string }>;
}

export class DialogueState {
  private context: DialogueContext;
  
  constructor(scenario: Scenario) { ... }
  
  // 获取当前 NPC 应该说啥
  getCurrentNpcLine(): string | null;
  
  // 处理玩家输入(异步,调 LLM + ASR)
  async processPlayerInput(audioBlob: Blob): Promise<{
    transcription: string;
    evaluation: EvaluationResult;
    npcResponse: string;
    npcAudioUrl: string;
  }>;
  
  // 进入下一回合
  nextRound(): boolean;
  
  // 是否关卡完成
  isCompleted(): boolean;
  
  // 生成最终反馈卡
  generateFeedbackCard(): FeedbackCard;
}
```

### 4.2 ProgressTracker(进度追踪)

```typescript
// core/progress-tracker.ts

export interface UserProgress {
  userId: string;
  scenarioId: string;
  status: 'not_started' | 'in_progress' | 'completed';
  score: number;
  attempts: number;
  firstCompletedAt?: Date;
  lastAttemptedAt?: Date;
  timeSpentSeconds: number;
}

export class ProgressTracker {
  async markStarted(scenarioId: string): Promise<void>;
  async markCompleted(scenarioId: string, score: number): Promise<void>;
  async getProgress(scenarioId: string): Promise<UserProgress>;
  async getAllProgress(): Promise<UserProgress[]>;
  async getCompletedCities(): Promise<string[]>;
}
```

### 4.3 ApiClient(API 客户端抽象)

```typescript
// core/api-client.ts

export interface IApiClient {
  // 用户
  getUser(userId: string): Promise<User>;
  updateUser(userId: string, data: Partial<User>): Promise<User>;
  
  // 进度
  getProgress(userId: string): Promise<UserProgress[]>;
  saveProgress(userId: string, progress: UserProgress): Promise<void>;
  
  // 错题本
  getErrors(userId: string): Promise<UserError[]>;
  saveError(userId: string, error: UserError): Promise<void>;
  
  // 词汇
  getVocabulary(userId: string): Promise<UserVocabulary[]>;
  saveVocabulary(userId: string, vocab: UserVocabulary): Promise<void>;
  
  // 对话(实时)
  sendAudio(audioBlob: Blob, context: DialogueContext): Promise<DialogueResponse>;
}

// 实现 1: 后端 API
export class BackendApiClient implements IApiClient { ... }

// 实现 2: 本地 IndexedDB(MVP)
export class LocalStubApiClient implements IApiClient { ... }

// 工厂
export function createApiClient(): IApiClient {
  if (process.env.NEXT_PUBLIC_API_MODE === 'local') {
    return new LocalStubApiClient();
  }
  return new BackendApiClient(process.env.NEXT_PUBLIC_API_URL);
}
```

**关键**:
- 业务代码依赖 `IApiClient` 接口,不知道具体实现
- MVP 用 `LocalStubApiClient`(写 IndexedDB)
- Phase 2 切 `BackendApiClient`,只改环境变量
- **业务代码 0 改动**

---

## 5. Web → Desktop 迁移路径

### 5.1 Phase 1: 纯 Web
- Vite + TypeScript + React + Phaser 3
- 浏览器运行
- 部署到 Vercel / Netlify

### 5.2 Phase 2 (可选): Tauri Desktop
- **Tauri 是什么**: 把 Web 应用打包成原生 Desktop 应用
- **优势**: 同一份 TypeScript 代码,几乎 0 改动
- **打包**:
  - Windows → .exe / .msi
  - macOS → .dmg
  - Linux → .deb / .AppImage
- **额外能力**:
  - 直接访问文件系统
  - 系统通知
  - 更好的离线支持

**集成方式**:
```bash
# 安装 Tauri CLI
npm install -D @tauri-apps/cli

# 初始化 Tauri
npx tauri init

# 打包
npx tauri build
```

### 5.3 Phase 3 (可选): Godot 4 重写
**什么时候值得重写**:
- Phaser 性能/效果不够
- 需要更复杂的游戏机制
- 想上 Steam / Switch

**重写范围**:
- 只重写 `frontend/src/game/` 目录(Phaser 场景)
- `core/` 和 `api/` 业务逻辑保留(转 GDScript 或 C#)
- 后端完全不动

**预估工作量**: 2-3 个月(单人)

### 5.4 跨端代码共享

| 平台 | 渲染层 | 业务层 | 后端 |
|------|--------|--------|------|
| Web (Phase 1) | Phaser 3 | TypeScript | Python |
| Desktop (Phase 2) | Phaser 3 (Tauri 打包) | TypeScript | Python |
| Desktop (Phase 3 可选) | Godot 4 (GDScript/C#) | GDScript 移植 | Python |

**业务层从 TypeScript → GDScript 的转换**: 状态机、剧本加载等核心逻辑,语义层面通用,只是语法转换。

---

## 6. 用户系统设计(框架预留)

### 6.1 MVP 状态(无后端)
- 用户首次访问,自动生成 UUID 存 localStorage
- 所有数据(进度、错题、词汇)存 IndexedDB
- 单机游戏,无跨设备同步

### 6.2 Phase 2 升级路径

**Step 1**: 加入后端(阿里云 ECS / 函数计算)
- FastAPI 部署到云
- PostgreSQL 数据库
- 阿里云 OSS 存音频文件

**Step 2**: 加入注册/登录
- 邮箱 + 密码(简化版)
- 或第三方登录(Google / Apple)

**Step 3**: 数据迁移
- 检测到已登录用户,提示"是否上传本地数据"
- 一次性同步到云端
- 之后双写(本地 + 云端)

### 6.3 数据库 Schema

参见 [PROPOSAL.md § 4](PROPOSAL.md#4-用户系统设计框架预留mvp-不实现)

### 6.4 API 设计(完整)

```
用户
GET    /api/v1/users/{user_id}
PUT    /api/v1/users/{user_id}
POST   /api/v1/users  (注册)

进度
GET    /api/v1/users/{user_id}/progress
GET    /api/v1/users/{user_id}/progress/{scenario_id}
POST   /api/v1/users/{user_id}/progress
PUT    /api/v1/users/{user_id}/progress/{scenario_id}

错题
GET    /api/v1/users/{user_id}/errors
POST   /api/v1/users/{user_id}/errors
DELETE /api/v1/users/{user_id}/errors/{error_id}

词汇
GET    /api/v1/users/{user_id}/vocabulary
POST   /api/v1/users/{user_id}/vocabulary
PUT    /api/v1/users/{user_id}/vocabulary/{word}

会话
POST   /api/v1/users/{user_id}/sessions
GET    /api/v1/users/{user_id}/sessions

对话(实时)
POST   /api/v1/dialogue/process  (multipart/form-data: audio + context)
```

---

## 7. 内容与代码分离

### 7.1 剧本格式(标准 JSON)

```json
{
  "scenario_id": "berlin_cafe_01",
  "version": "1.0",
  "metadata": {
    "name": "在柏林咖啡馆点单",
    "city": "Berlin",
    "cefr_level": "A1",
    "textbook_ref": "Menschen A1, Lektion 3",
    "estimated_minutes": 5,
    "difficulty": 1
  },
  "scene": {
    "location": "Café Einstein, Berlin Kreuzberg",
    "time": "Samstag, 10:00",
    "npc": {
      "id": "anna",
      "name": "Anna",
      "role": "Kellnerin",
      "personality": "freundlich, geduldig",
      "voice_settings": {
        "speed": 0.9,
        "pitch": 1.0
      }
    }
  },
  "learning_objectives": {
    "expressions": [
      "Hallo!",
      "Ich möchte einen Kaffee",
      "Was empfehlen Sie?",
      "Mit Milch, bitte",
      "Die Rechnung, bitte"
    ],
    "grammar": [
      "möchten + Akkusativ",
      "bestimmte/unbestimmte Artikel"
    ],
    "vocabulary": [
      { "word": "der Kaffee", "translation": {"zh": "咖啡", "en": "coffee"} },
      { "word": "die Milch", "translation": {"zh": "牛奶", "en": "milk"} }
    ],
    "culture": "在德国咖啡馆不需要给小费,服务费已含在账单中"
  },
  "rounds": [
    {
      "round_id": 1,
      "type": "npc_starts",
      "npc_says": "Hallo! Herzlich willkommen im Café Einstein. Was darf es sein?",
      "tts_voice": "anna_default",
      "transition": "fade_in"
    },
    {
      "round_id": 2,
      "type": "player_responds",
      "expected_says": [
        "Ich möchte einen Kaffee",
        "Einen Kaffee, bitte",
        "Ich hätte gern einen Kaffee"
      ],
      "hints": [
        "Ich möchte...",
        "Einen Kaffee, bitte"
      ],
      "evaluation": {
        "grammar_check": true,
        "pronunciation_check": true,
        "must_understand": true
      },
      "feedback_on_success": {
        "npc_says": "Sehr gerne. Möchten Sie auch etwas essen dazu?",
        "points_awarded": ["Ich möchte einen Kaffee"]
      },
      "feedback_on_error": {
        "npc_says": "Einen Kaffee, bitte. Möchten Sie auch etwas essen?",
        "points_missed": ["Ich möchte einen Kaffee"]
      }
    }
  ],
  "completion": {
    "min_rounds": 5,
    "success_criteria": "完成 80% 表达点",
    "encyclopedia_card_id": "berlin_kaffeekultur"
  }
}
```

### 7.2 城市百科格式

```json
{
  "card_id": "berlin_kaffeekultur",
  "city": "Berlin",
  "category": "Kultur",
  "title": "Berliner Kaffeekultur",
  "image": "encyclopedia/berlin_cafe_history.png",
  "sections": [
    {
      "heading": "历史",
      "text": "柏林的咖啡馆文化起源于 17 世纪...",
      "keywords": [
        { "word": "die Kaffeekultur", "translation": {"zh": "咖啡文化"} }
      ]
    },
    {
      "heading": "特色",
      "text": "柏林咖啡馆以独立小店为主..."
    }
  ],
  "references": [
    "https://www.visitberlin.de/en/cafe-culture"
  ]
}
```

### 7.3 内容创作者工作流

1. 用 JSON 编辑器(VS Code / 在线 JSON 工具)编辑剧本
2. 提交到 `backend/app/data/scenarios/` 目录(Git)
3. 后端自动加载新剧本
4. 前端无需改动

**这是 Phase 2+ 的目标**,MVP 阶段剧本直接 hardcode 在后端。

---

## 8. AI 服务抽象层

### 8.1 接口设计

```python
# backend/app/services/

class ASRService(Protocol):
    async def transcribe(self, audio: bytes) -> str: ...

class TTSService(Protocol):
    async def synthesize(self, text: str, voice: str) -> bytes: ...

class LLMService(Protocol):
    async def chat(self, messages: list[dict]) -> str: ...
    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]: ...

class EvaluationService(Protocol):
    async def evaluate_audio(
        self, 
        audio: bytes, 
        reference: list[str]  # 目标表达
    ) -> dict: ...
```

### 8.2 实现切换

```python
# 当前
class DashScopeASRService(ASRService):
    """使用阿里云 Fun-ASR"""
    ...

# 未来(开源 Plan B)
class WhisperASRService(ASRService):
    """使用本地 Whisper"""
    ...
```

**通过依赖注入切换**:
```python
# config.py
ASR_SERVICE = "dashscope"  # 或 "whisper"

# main.py
asr_service = create_asr_service(ASR_SERVICE)
```

业务代码不变。

---

## 9. 部署架构

### 9.1 MVP(本地)
```
后端:localhost:8000 (uvicorn)
前端:localhost:5173 (vite dev)
存储:IndexedDB
TTS/ASR/LLM:阿里云 API
```

### 9.2 Phase 2(云端)
```
前端:Vercel / Netlify (静态托管)
后端:阿里云 ECS (2 核 4GB) / 函数计算
数据库:阿里云 RDS PostgreSQL
音频文件:阿里云 OSS
缓存:Redis(可选)
TTS/ASR/LLM:阿里云 API
```

### 9.3 Phase 3(规模)
```
前端:CDN 加速
后端:负载均衡 + 多实例 ECS
数据库:PostgreSQL 主从 + 读写分离
音频:OSS + CDN
AI API:考虑多供应商容灾(阿里云 + 自建)
监控:阿里云日志服务 / Sentry
```

---

## 10. 安全考虑

### MVP 阶段
- 不收集用户敏感信息(只用本地 UUID)
- 阿里云 API Key 在后端,不在前端
- 录音数据临时处理,不持久化(可选)

### Phase 2+
- HTTPS 全程
- API Key 加密存储
- 用户密码 bcrypt 哈希
- 速率限制(防止滥用)
- 内容审核(用户输入可能有问题,需要过滤)

---

## 11. 性能考虑

### 关键延迟
- ASR 转写: ~500ms
- LLM 思考: ~2-3s
- 发音评估: ~2s
- TTS 流式首包: ~150ms
- **总单回合**: ~3-5s(可接受)

### 优化方向
- 异步调用 ASR + LLM + 评估(并行)
- LLM 用流式输出,边生成边 TTS
- 客户端预加载下一关 NPC 音频(可选)

---

## 12. 监控与可观测性(MVP 后考虑)

- 日志: 结构化日志(structlog)
- 错误追踪: Sentry
- 性能监控: 自建 metrics
- 用户行为: 埋点(产品迭代用)

---

OK,架构设计到此。你 review 后告诉我:这个分层和迁移路径,有没有要调整的地方?

---

# 第二部分:v2.0 新增架构(2026-06-21)

> 配合 `docs/GAME_DESIGN.md` 一起看。本节是新设计在架构层的具体落地。

---

## 13. 三轨并行学习(Track 系统)

### 13.1 Track 抽象

```typescript
// core/track.ts
interface Track {
  id: 'german' | 'alevels' | 'ielts';
  displayName: { de: string; zh: string };
  // 进度追踪(继承 ProgressTracker)
  progressTracker: ProgressTracker;
  // 学习单元加载器(从 YAML 读)
  unitLoader: LearningUnitLoader;
  // 评估 API(根据 track 不同)
  evaluator: Evaluator;
}
```

### 13.2 三个具体 Track

| Track | 评估 API | 内容格式 | 内容来源 |
|-------|---------|---------|---------|
| **german** | Fun-ASR + Qwen2-Audio + Qwen-Plus | `learning_paths/german/*.yaml` | 我方写(已写) |
| **alevels** | Qwen-Plus(tutor 模式)+ Math.js | `learning_paths/alevels/*.yaml` | **另一个 agent 填** |
| **ielts** | Qwen-Plus(IELTS rubric)+ Qwen2-Audio(口语) | `learning_paths/ielts/*.yaml` | **另一个 agent 填** |

### 13.3 Track 选择 UI

```vue
<TrackSelector>
  <TrackButton track="german" icon="🇩🇪" progress="32%" />
  <TrackButton track="alevels" icon="📚" progress="67%" />
  <TrackButton track="ielts" icon="✏️" progress="45%" />
</TrackSelector>
```

---

## 14. 双语切换机制(NPC lang_pref)

### 14.1 NPC 元数据扩展

```typescript
interface NPC {
  id: string;
  name: { de: string; zh: string };
  age: number;
  role: string;
  portraitKey: string;
  backstory: string;
  // NEW v2.0: 语言偏好
  langPref: {
    de: number;    // 0-1, 概率开场德语
    en: number;    // 0-1, 概率开场英文
  };
  canSpeakEnglish: boolean;  // 是否能切换英文
  englishProficiency: CEFR;  // B1/B2/C1
}
```

### 14.2 场景语言基线

```typescript
// data/scene-language.ts
const LANG_BASE = {
  airport:           { de: 0.5, en: 0.5, enAvailable: 100 },
  big_city_attraction: { de: 0.7, en: 0.3, enAvailable: 100 },
  university_town:   { de: 0.8, en: 0.2, enAvailable: 90 },
  big_city_cafe:     { de: 0.9, en: 0.1, enAvailable: 50 },
  mid_city_cafe:     { de: 0.95, en: 0.05, enAvailable: 30 },
  rural_gasthaus:    { de: 1.0, en: 0.0, enAvailable: 0 },   // 硬性
  school_class_de:   { de: 1.0, en: 0.0, enAvailable: 0 },   // 德语课
  school_class_en:   { de: 0.1, en: 0.9, enAvailable: 100 }, // A-levels 全英文
  government:        { de: 1.0, en: 0.0, enAvailable: 0 },
  private_family:    { de: 1.0, en: 0.0, enAvailable: 0 },
};
```

### 14.3 玩家选择流程

```
[NPC 出现]
    ↓
Game 调用 NPC.langPref 随机选语言(或基于玩家历史)
    ↓
[NPC 说话: 'Hallo! Was darf\'s sein?' 或 'Hello! What can I get you?']
    ↓
DialogueBox 渲染两行(德语 + 英语 + 中文)
    ↓
[玩家点 "Versuche es auf Deutsch" / "Switch to English"]
    ↓
Game 切换 dialogueState.useEnglish
    ↓
后续对话语言改变 + XP 收益变化:
  - 德语模式: +100% German XP, +50% NPC affinity
  - 英语模式: +0% German XP, -10% NPC affinity(如果 NPC 不喜欢英文)
    ↓
玩家录音 → Fun-ASR → Qwen-Plus 评分 → Qwen2-Audio 评分
    ↓
合并反馈 → NPC 反应 → 玩家修正或继续
```

### 14.4 双语教学反馈循环

```
玩家录音德语/英语音频
    ↓
Fun-ASR 1.5 → 转写文本(Werder/Hochdeutsch)
    ↓
Qwen-Plus → 评分:语法 + 词汇 + 语义(context-aware)
    ↓
Qwen2-Audio-7B → 评分:发音 + 流利度 + 语调
    ↓
合并反馈 → DialogueBox 显示 + NPC 反应(表情 + 文本)
    ↓
玩家可选择:重试 / 继续 / 切英文 / 查看文化卡片
```

---

## 15. RPG 角色属性系统

### 15.1 Stats 数据结构

```typescript
interface PlayerStats {
  // 基础身份
  name: string;
  age: number;

  // 语言能力(CEFR 6 等级)
  language: {
    german: 'A0' | 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';
    english: 'A0' | 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';
  };

  // A-levels 学科成绩(A*-U)
  subjects: Record<string, 'A*' | 'A' | 'B' | 'C' | 'D' | 'E' | 'U'>;

  // RPG 资源
  mood: number;       // 0-100
  energy: number;     // 0-100
  money: number;      // EUR

  // 时间
  date: {
    year: 1 | 2;     // Year 12 / 13
    month: number;   // 1-12
    day: number;     // 1-31
  };

  // 位置
  location: string;   // 'berlin' / 'munich' / 'school' / etc.

  // 社交
  relationships: Record<string, number>;  // npcId → affinity 0-100

  // 收集
  culturalCards: string[];  // 卡片 ID 列表
}
```

### 15.2 状态效果

```typescript
interface StatusEffect {
  source: string;       // 来源('hunger', 'illness', 'homesick', ...)
  modifier: { stat: keyof PlayerStats, delta: number, durationDays: number };
}
```

### 15.3 状态变化触发器

- **mood < 30**: 学习效率 -50%, 易生病, 触发负面事件
- **energy < 20**: 上课注意力涣散, minigame 失败率 +30%
- **money < 0**: 触发"向父母要钱"剧情, mood -20
- **homesick**: 长期 mood -10/week, 触发心理咨询

---

## 16. 走遍德国地图 + 文化百科

### 16.1 地图数据结构

```typescript
// data/germany-map.ts
interface MapNode {
  id: string;
  name: { de: string; zh: string };
  type: 'city' | 'attraction' | 'scene_point';
  lat: number;
  lng: number;
  unlockLevel: CEFR;  // 解锁所需德语等级
  difficulty: CEFR;
  englishAvailable: number;  // 0-100

  // 内部场景点列表
  scenes: ScenePoint[];
}

interface ScenePoint {
  id: string;
  name: { de: string; zh: string };
  type: 'cafe' | 'train_station' | 'museum' | 'street' | 'shop' | ...;
  difficulty: CEFR;
  npc: NPC;
  learningObjectives: string[];
  scriptRef: string;  // 对应 JSON 剧本文件
}
```

### 16.2 文化百科卡片

```typescript
interface CulturalCard {
  id: string;          // e.g. 'kaffee_und_kuchen'
  category: 'Kultur' | 'Wirtschaft' | 'Essen' | 'Tourismus' | 'Bildung';
  title: { de: string; zh: string };
  content: { de: string; zh: string };
  imageKey?: string;
  unlockedBy: string; // 哪个场景解锁
}
```

### 16.3 走遍德国 = 12 城市

```
北部: Hamburg, Bremen, Kiel
东部: Berlin, Dresden, Leipzig
中部: Hannover, Göttingen, Frankfurt
南部: München, Heidelberg, Freiburg
西部: Köln, Düsseldorf, Aachen
邻国德语区(可选): Wien, Salzburg, Zürich, Luzern
```

每城市 5-10 个场景点 × 12 城市 = **60-120 个场景点**(M2+ 逐步解锁)。

---

## 17. 学习路径接口(LearningUnit 抽象)

> **关键**: 不论德语 / A-levels / 雅思 / 文化百科,**所有学习内容用统一格式**。
> 这样我们的引擎代码通用,对方 agent 只需要填 YAML。

### 17.1 YAML Schema

```yaml
# learning_paths/alevels/mathematics_aqa_pure_1.yaml
learning_unit:
  id: alevel_math_aqa_pure_1
  subject: mathematics
  track: a_levels
  exam_board: aqa           # edexcel / ocr / caie
  level: a-level             # gcse / a-level / b1 / ielts_5.0

  meta:
    title: "Proof and Algebra"
    description: "..."
    estimated_time_minutes: 45
    difficulty: 1            # 1-5

  content:
    concepts:
      - name: "Mathematical proof"
        explanation: "..."
        examples: [...]

    practice_questions:
      - type: multiple_choice
        prompt: "..."
        options: [...]
        correct: "B"
        explanation: "..."

      - type: essay
        prompt: "Discuss..."
        rubric: "..."

      - type: experiment
        prompt: "Drag the slider..."
        validation: { answer: 9.8, tolerance: 0.1 }

  progression:
    prerequisites: []
    unlocks: ["alevel_math_aqa_pure_2"]

  mock_exam:
    - month: 11
      format: paper1
      duration_minutes: 120
      questions: [...]
```

### 17.2 引擎消费方式

```typescript
// core/learning/loader.ts
import yaml from 'js-yaml';

class LearningUnitLoader {
  async load(path: string): Promise<LearningUnit> {
    const res = await fetch(path);
    const text = await res.text();
    return yaml.load(text) as LearningUnit;
  }
}

// 使用
const unit = await loader.load('/learning_paths/alevels/mathematics_aqa_pure_1.yaml');
// 渲染 minigame、评分、进度更新 — 全部通用
```

### 17.3 与另一个 agent 的协作

- **我方提供**: `core/learning/loader.ts` + `learning_paths/german/a1_001.yaml`(样例)+ schema 文档
- **对方提供**: A-levels 各科 YAML + 雅思各 section YAML
- **整合测试**: 加载对方文件 → 在游戏中能跑通

---

## 18. 结局多线

### 18.1 结局计算器

```typescript
// core/ending-calculator.ts
interface EndingResult {
  type: 'academic' | 'social' | 'psychological' | 'hidden';
  name: { zh: string; en: string };
  reason: string;
  university?: string;
}

function calculateEnding(stats: PlayerStats, choices: Choice[]): EndingResult {
  // 学术结局
  if (stats.subjects.math === 'A*' &&
      stats.subjects.physics === 'A*' &&
      stats.language.english === 'C1' &&
      stats.examResults.ielts >= 7.5) {
    return { type: 'academic', name: '英国 G5', university: 'Imperial College London' };
  }

  if (stats.language.german === 'C1' &&
      stats.subjects.math >= 'A' &&
      stats.location === 'munich') {
    return { type: 'academic', name: '德国 TU9', university: 'TU München' };
  }

  // ... 更多规则

  // 隐藏结局
  if (stats.subjects.math === 'A*' &&
      stats.language.german === 'C1' &&
      stats.examResults.ielts >= 8.0 &&
      stats.culturalCards.length >= 50) {
    return { type: 'hidden', name: '学术全满贯', reason: '...' };
  }

  return { type: 'default', name: '完成 3 年' };
}
```

### 18.2 结局类型

| 类型 | 触发条件 | 场景 |
|------|---------|------|
| 学术-英国 G5 | 3A* + IELTS 7.5 + English C1 | Oxbridge / IC / UCL offer |
| 学术-英国 Top 20 | AAB + IELTS 7.0 | Manchester / Warwick offer |
| 学术-德国 TU9 | ABB + 德语 C1 | TUM / RWTH offer |
| 学术-混合 | 雅思 7.0 + 德语 B2 | 英国本科 + 德国交换 |
| 社交-朋友圈 | 5+ 德国好友 + 文化适应 | 温馨结局 |
| 心理-自信成长 | mood 均值 70+ | 独立结局 |
| 隐藏-学术全满贯 | 3A* + 德语 C1 + IELTS 8.0 + 50 卡片 | 完美结局 |

---

## 19. 骨架实现 v0.1(已交付 2026-06-21)

### 19.1 已完成
- ✅ Vue 3 + Vite + Pinia + Phaser 3 基础栈
- ✅ App.vue 三层布局(状态栏 + 主画布 + 底部状态栏)
- ✅ StatusBar.vue: 主角名 / 日期 / 心情 / 体力 / 资金 / 语言能力 / 位置
- ✅ DialogueBox.vue: NPC 立绘 + 语言切换 + 选项 + 录音按钮(占位)
- ✅ GameCanvas.vue: Phaser 场景包装
- ✅ BootScene.js + CityScene.js: 柏林顶视图 RPG 场景(3 个可点击场景点)
- ✅ Pinia store: 主角 stats / 当前场景 / 对话状态 / 语言切换
- ✅ 资源软链: `frontend/public/assets → ../assets`(AI 生成图可直接用)

### 19.2 当前 dev server
```bash
cd /Volumes/NewDisk/GermanLearning/frontend
npm run dev  # http://127.0.0.1:5173
```

### 19.3 待办(后续 Phase)
- Phase 0 step 2-5: CosyVoice + Fun-ASR + Qwen2-Audio 接入 DialogueBox
- Phase 1: 写第 1 关 JSON 剧本 + 完整对话流程
- Phase 2: 学校子系统 + 选课 + 课堂 minigame
- Phase 3: 地图子系统 + 多个城市 + 完整 NPC
- Phase 4: 生活子系统 + 节日 + 社交
- Phase 5: 多结局 + 用户系统

---

## 20. 成就系统集成(v2.0 新增)

> **详细设计**: 见 `docs/ACHIEVEMENT_SYSTEM.md`(1226 行,~1860 个成就)。
> 本节关注成就系统如何接入现有架构。

### 20.1 新增模块

```
core/
├── achievement/
│   ├── AchievementService.ts    # 后端风格(无依赖)
│   ├── UnlockChecker.ts         # 条件检查器
│   └── ProgressTracker.ts       # 进度追踪(已存在,扩展)
├── store/
│   └── achievements.ts          # Pinia store
└── events/
    └── GameEventBus.ts          # 全局事件总线(成就/进度/对话共用)

shared/
└── types/
    └── achievement.ts           # 类型定义(Achievement/Discovery/Reward/UnlockCondition)
```

### 20.2 事件驱动架构

```
游戏行为发生
    ↓
GameEventBus.emit(GameEvent)
    ├─ type: 'kp_completed' | 'level_completed' | 'discovery_visited' |
    │         'dialogue_ended' | 'npc_relationship_changed' |
    │         'streak_extended' | 'mock_taken' | 'purchase' | 'travel'
    └─ payload: { ... }
    ↓
订阅者 1: ProgressTracker(更新学习进度)
订阅者 2: AchievementService.check_unlock()(检查成就)
订阅者 3: EndingCalculator.update()(影响结局)
订阅者 4: GameLog(记录日志)
    ↓
如有新成就解锁 → 触发 NotificationCenter → UI 弹窗 + BGM
```

### 20.3 新增玩家属性

```typescript
// 已在 PlayerStats 中(§15.1)扩展
interface PlayerStats {
  // 已有:language/subjects/mood/energy/money/date/location/relationships/culturalCards
  xp: number;             // 经验值(从学习+探索来)
  level: number;          // 等级 1-100(M-LEVEL)
  taler: number;          // 游戏内货币(不同于 € 真实生活)
  unlocked_achievements: Map<string, Achievement>;  // id → 解锁详情
  achievement_progress: Map<string, number>;        // id → 进度 0-1
  titles: string[];       // 已获称号(["Deutschlandkenner", "Sprichwort-Meister", ...])
  active_title?: string;  // 当前展示称号
}
```

### 20.4 AchievementService 接口

```typescript
// core/achievement/AchievementService.ts
class AchievementService {
  // 加载所有成就定义(从 static JSON / 后端)
  async loadCatalog(): Promise<Achievement[]>;

  // 监听事件总线
  subscribe(events: GameEventBus): void;

  // 检查解锁条件
  async checkUnlock(userId: string, event: GameEvent): Promise<Achievement[]>;

  // 获取某成就进度(用于 UI)
  async getProgress(userId: string, achievementId: string): Promise<Progress>;

  // 获取某类成就墙数据
  async getWall(userId: string, category: Category): Promise<WallResponse>;

  // 获取探索地图(已点亮城市 + 打卡点)
  async getDiscoveryMap(userId: string): Promise<MapData>;
}
```

### 20.5 与现有系统的关联

| 系统 | 关联 |
|------|------|
| **ProgressTracker** | 完成 KP → 触发 `kp_completed` 事件 → 检查 L1-L3 成就 |
| **NPC 系统** | 好感度变 → 触发 `npc_relationship_changed` → 检查 M4 + 隐藏 H-LIEBE |
| **走遍德国地图** | 打卡 → 触发 `discovery_visited` → 检查 E1-E11 成就 |
| **真实一天循环** | 每天事件 → 触发 `streak_extended` / `mock_taken` → 检查 M1 + M5 |
| **学习路径接口** | 完成单元 → 触发 `level_completed` → 检查 L 单元级成就 |
| **结局多线** | 成就总数 / 稀有度 → 影响结局权重 |

### 20.6 UI 组件(待 Phase 1 实现)

```vue
<!-- AchievementWall.vue — 成就墙 -->
<AchievementWall :category="'E2'">
  <ProgressBar :progress="35/280" />
  <AchievementCard v-for="ach in achievements" :achievement="ach" />
</AchievementWall>

<!-- DiscoveryMap.vue — 探索地图 -->
<DiscoveryMap>
  <StateMarker v-for="state in states" :state="state" />
  <DiscoveryDetailDialog v-if="selected" :discovery="selected" />
</DiscoveryMap>

<!-- UnlockNotification.vue — 解锁弹窗 -->
<UnlockNotification :achievement="newAchievement">
  <RarityBadge :rarity="newAchievement.rarity" />
  <RewardDisplay :reward="newAchievement.reward" />
</UnlockNotification>
```

### 20.7 数据流时序图

```
[用户行为] → 对话完成
    ↓
GameEventBus.emit('dialogue_ended', {npc_id, language_used, success})
    ↓
[AchievementService] 监听
    ↓
for each Achievement in catalog:
  if event.type === 'dialogue_ended':
    if Achievement.id matches (e.g. 'M-CHAT-DE-FIRST' for first DE dialogue):
      if condition met → unlock!
    ↓
[新成就 H-LIEBE 解锁] (玩家对 Lisa 说出 Ich liebe dich)
    ↓
NotificationCenter.push({
  type: 'achievement_unlocked',
  rarity: 'diamond',
  achievement: {...},
  reward: {xp: 5000, taler: 2000, title: '德语告白家'}
})
    ↓
UI: 中心弹窗 + BGM 切换(特殊紫色光 + 慢动作)
    ↓
player.xp += 5000; player.taler += 2000; player.titles.push('德语告白家')
```

### 20.8 与 curriculum KP 的关联(关键)

```typescript
// 每个探索成就都关联一组 KP,实现"打卡带学"
interface Discovery {
  id: string;
  name_de: string;
  name_zh: string;
  city_id: string;
  related_kp_ids: string[];   // 关联 KP 列表
  unlock_dialogue?: string;   // 解锁后跟 NPC 的对话
  visit_count_required: number;
}

// 联动示例
discovery = { id: 'E-CASTLE-NEUSCHWANSTEIN', ... }
on visit:
  1. 显示文化卡片(德语 + 中文)
  2. 提示关联 KP:HIST-LUDWIG-II
  3. 若 KP 未完成 → 加入"待学习"清单
  4. 检查成就 E-SEHENS-100 进度
```

### 20.9 货币双轨

| 货币 | 来源 | 用途 | 现实映射 |
|------|------|------|---------|
| **€ EUR** | 父母汇款 + 打工 | 真实生活开销(房租/餐/交通) | 1:1 真实 |
| **Taler** | 成就奖励 + 学习 XP | 游戏内(买皮肤/装饰/装饰品) | 纯游戏 |

不互通 — Taler 是 RPG 货币,€ 是真实生活费。两个系统独立。

### 20.10 一个需要用户确认的细节

成就文档 §L1.2 提到 **TestDaF**(TDN 3/4/5),但本游戏已改为 A-levels + 雅思。TestDaF 不在主线。请用户在 §15A.8 决策:
- (a) 保留 TestDaF 作为可选
- (b) 替换为 A-level 德语 KP
- (c) 删除,只用 CEFR 等级里程碑

---

OK,新架构到此。看 `docs/GAME_DESIGN.md` 了解完整游戏设计,这里专注架构落地。
