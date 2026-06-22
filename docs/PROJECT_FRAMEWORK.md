# gagaToday Project Framework

版本：v0.1  
日期：2026-06-21  
适用范围：MVP 到正式早期版本

---

## 1. 总体目标

gagaToday 是德国留学生活模拟 RPG。项目的工程目标不是先把所有内容做大，而是建立一个可以长期扩展的框架：

```text
生活模拟底盘
→ 学习系统
→ 预算与父母资助
→ 地图探索
→ NPC 关系
→ AI 语言任务
→ Agent 生成可审核内容
→ 未来云存档和 cohort 轻联网
```

MVP 只做慕尼黑 30 天单机体验，但从第一天开始预留内容版本、玩家 ID、行动日志和未来联网状态。

---

## 2. 项目分层

### 2.1 Game Client

目录：

```text
frontend/src/components/
frontend/src/phaser/
frontend/src/stores/
frontend/src/style.css
```

职责：

- 地图渲染；
- 场景点点击；
- 对话框；
- 状态栏；
- 手机、邮件、日历、银行、任务 UI；
- 做饭小游戏 UI；
- 学习、小测和反馈卡 UI。

限制：

- 不直接写死内容；
- 不直接调用 AI 供应商；
- 不直接决定核心数值规则；
- 只通过 Game Core 和 Content System 获取状态与内容。

### 2.2 Game Core

目标目录：

```text
frontend/src/core/
  calendar/
  player/
  economy/
  learning/
  relationships/
  tasks/
  travel/
  save/
  events/
```

职责：

- 游戏时间推进；
- 玩家状态计算；
- 金钱、交易和预算；
- 体力、心情、压力；
- 学习进度和测试结果；
- NPC 关系变化；
- 任务解锁与完成；
- 路线成本结算；
- 本地存档；
- 行动日志。

限制：

- 不包含 Vue 或 Phaser 依赖；
- 不读取 DOM；
- 不写 UI 文案；
- 不直接加载图片资源；
- 不编造真实世界数据。

### 2.3 Content System

目录：

```text
frontend/src/content/
  munich/
    player_start.json
    locations.json
    routes.json
    npcs.json
    dialogues.json
    daily_events.json
    messages.json
    mail.json
    bills.json
    lessons.json
    homework.json
    tests.json
    recipes.json
    achievements.json
```

职责：

- 定义所有可玩内容；
- 作为 MVP 的单一内容源；
- 让内容作者和 agent 可以不改代码地新增地点、任务、对话和课程；
- 为未来数据库或 CMS 提供迁移基础。

限制：

- 内容文件不能包含密钥；
- 真实世界来源必须进入 `source` 或 `source_record`；
- Agent 生成内容必须标记 `draft` 或 `needs_review`；
- 审核前不能标记 `published`。

### 2.4 AI Gateway

目标目录：

```text
backend/app/
  api/
  services/
  schemas/
  prompts/
```

职责：

- 统一封装 ASR；
- 统一封装 TTS；
- 统一封装 LLM 对话；
- 统一封装发音评估；
- 提供固定 API 给客户端；
- 记录成本、延迟和错误；
- 提供固定脚本兜底。

限制：

- 不把供应商 API key 写入代码；
- 不向前端暴露密钥；
- 不让 AI 直接改变玩家关键状态；
- AI 只返回结构化结果，最终判定由 Game Core 完成。

### 2.5 Content Agent Pipeline

目标目录：

```text
backend/app/agents/
docs/agent_runs/
frontend/src/content/drafts/
```

职责：

- 导入 POI 草稿；
- 生成打卡点草稿；
- 生成餐饮和菜单草稿；
- 生成预算平衡建议；
- 生成课程和作业草稿；
- 做合规检查；
- 创建人工审核任务。

限制：

- Agent 不直接发布正式内容；
- Agent 不复制未授权图片、评论、菜单照片；
- Agent 输出必须保留来源、抓取时间、可信度、审核状态；
- Agent 不改 Game Core 规则。

### 2.6 Future Backend

目标目录：

```text
backend/app/accounts/
backend/app/cloud_save/
backend/app/cohort/
```

职责：

- 用户账号；
- 云存档；
- cohort 轻联网；
- 学习小组；
- 共同打卡；
- 班级事件；
- 审核和举报。

MVP 只预留字段，不实现复杂联网。

---

## 3. 推荐目录结构

```text
GermanLearning/
  docs/
    PROJECT_FRAMEWORK.md
    AGENT_WORKFLOW.md
    CONTENT_SCHEMA.md
    MVP_IMPLEMENTATION_PLAN.md

  frontend/
    src/
      core/
        calendar/
        player/
        economy/
        learning/
        relationships/
        tasks/
        travel/
        save/
        events/
      content/
        munich/
      components/
      phaser/
      stores/

  backend/
    app/
      api/
      services/
      schemas/
      prompts/
      agents/

  assets/
    characters/
    scenes/
    ui/

  scripts/
    curriculum/
    content/
```

---

## 4. 数据流

### 4.1 单机 MVP 数据流

```text
Content JSON
→ Game Core 读取和验证
→ Pinia 暴露当前状态
→ Vue / Phaser 渲染
→ 玩家行动
→ Game Core 计算结果
→ Save 模块写本地存档
```

### 4.2 AI 语言任务数据流

```text
玩家录音
→ Client 上传音频
→ AI Gateway ASR
→ AI Gateway 发音 / 语法评估
→ AI Gateway NPC 回复和 TTS
→ Client 展示反馈
→ Game Core 根据结构化结果结算任务
```

AI 返回建议，Game Core 做判定。

### 4.3 Agent 内容生产数据流

```text
create_job
→ fetch_sources
→ normalize
→ transform_to_schema
→ compliance_check
→ draft content
→ human review
→ published content JSON
→ game content version bump
```

---

## 5. 核心领域模型

MVP 必须稳定的模型：

- `PlayerState`
- `Location`
- `Route`
- `Npc`
- `DialogueScenario`
- `DailyEvent`
- `Task`
- `Transaction`
- `Lesson`
- `Homework`
- `Test`
- `Message`
- `Mail`
- `Bill`
- `Recipe`
- `Achievement`
- `ActionLogEntry`

这些模型的字段规范见 `docs/CONTENT_SCHEMA.md`。

---

## 6. MVP 开发顺序

1. 内容 schema；
2. 慕尼黑内容 JSON；
3. Game Core 最小骨架；
4. 当前 Pinia store 迁移到 Game Core；
5. 每日循环；
6. 本地存档；
7. 手机 / 邮件 / 任务 UI；
8. 预算与父母信任；
9. 学习、作业、小测；
10. AI Gateway；
11. 三个语音任务；
12. 30 天内容补齐。

---

## 7. 非目标

MVP 不做：

- 开放世界 MMO；
- 自由私聊；
- 全德国实时路线；
- 自建地图瓦片；
- 所有 NPC 实时 AI；
- 全量 A-levels；
- 全量 IELTS；
- 未审核 Agent 自动发布；
- 未授权真实餐厅图片或评论。

---

## 8. 判断框架是否健康

一个新功能进入项目时，先问：

1. 它属于 Game Client、Game Core、Content、AI Gateway、Agent Pipeline 还是 Future Backend？
2. 它是否可以通过 content JSON 扩展？
3. 它是否把真实数据来源记录清楚？
4. 它是否破坏单机 MVP？
5. 它是否让 AI 直接控制关键游戏状态？
6. 它是否需要现在做，还是可以放到 Phase 2？

答不清楚，就先写设计，不直接改代码。
