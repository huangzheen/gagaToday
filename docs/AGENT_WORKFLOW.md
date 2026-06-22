# gagaToday Agent Workflow

版本：v0.1  
日期：2026-06-21  
用途：让不同 agent 在同一项目中协作而不互相踩线

---

## 1. 所有 agent 必读顺序

每个 agent 在开始工作前，应按顺序阅读：

1. 根目录 `gagaToday_project_design_document.md`；
2. `docs/MVP_IMPLEMENTATION_PLAN.md`；
3. `docs/PROJECT_FRAMEWORK.md`；
4. `docs/CONTENT_SCHEMA.md`；
5. 本文档。
6. `docs/agents/` 中对应自己的角色文档。

如果任务只涉及课程内容，还要读：

- `docs/curriculum/README.md`；
- `docs/curriculum/KP_SCHEMA.md`。

如果任务涉及 AI API，还要读：

- `docs/API_STACK.md`。

各角色的单独工作说明位于：

```text
docs/agents/
  架构智能体.md
  游戏核心智能体.md
  前端智能体.md
  内容智能体.md
  NPC智能体.md
  课程智能体.md
  人工智能后端智能体.md
  内容流水线智能体.md
  餐馆导入智能体.md
  德国美食智能体.md
  德国探索智能体.md
  德国交通智能体.md
  质量测试智能体.md
```

---

## 2. 全局规则

所有 agent 必须遵守：

- 不读取、打印、复制 secrets vault；
- 不把密钥写进代码、文档或日志；
- 不改无关文件；
- 不重写别人刚完成的模块，除非任务明确要求；
- 不把旧文档的柏林 / TestDaF 主线重新当成 MVP 主线；
- 不让 Agent 生成内容直接进入 `published`；
- 不引入新框架，除非 `PROJECT_FRAMEWORK.md` 已更新并通过人工确认；
- 不把 UI、玩法规则、内容数据混在同一个文件里。

---

## 3. Agent 类型与职责

### 3.1 Architecture Agent

负责：

- 项目框架；
- 模块边界；
- schema；
- API 合约；
- 技术路线决策；
- 迁移计划。

可改：

```text
docs/PROJECT_FRAMEWORK.md
docs/AGENT_WORKFLOW.md
docs/CONTENT_SCHEMA.md
docs/MVP_IMPLEMENTATION_PLAN.md
docs/ARCHITECTURE.md
```

不可改：

- 具体课程内容；
- 大量 UI 代码；
- AI provider 具体密钥；
- 真实内容批量导入结果。

交付格式：

- 先写设计；
- 再给迁移步骤；
- 若需要改代码，只做骨架或接口，不做大面积实现。

### 3.2 Frontend Agent

负责：

- Vue 组件；
- Phaser 场景；
- UI 状态展示；
- 手机、邮箱、日历、银行、任务界面；
- 对话框；
- 做饭小游戏 UI；
- 学习和反馈卡 UI。

可改：

```text
frontend/src/components/
frontend/src/phaser/
frontend/src/stores/
frontend/src/style.css
frontend/src/App.vue
```

谨慎改：

```text
frontend/src/core/
frontend/src/content/
```

不可改：

- 后端 AI 服务；
- 课程知识库大纲；
- Agent pipeline；
- secrets。

要求：

- UI 不硬编码大量内容；
- 从 Content System 或 Game Core 取数据；
- 运行 `npm run build` 验证；
- 新 UI 需要考虑移动端和不同视口。

### 3.3 Game Core Agent

负责：

- 纯玩法逻辑；
- 每日循环；
- 资源结算；
- 预算；
- 父母信任；
- 学习进度；
- NPC 关系；
- 任务系统；
- 本地存档。

可改：

```text
frontend/src/core/
frontend/src/stores/
frontend/src/content/*/player_start.json
```

不可改：

- Phaser 视觉细节；
- 大量美术资源；
- AI provider 代码；
- 课程原始资料。

要求：

- Core 不依赖 Vue / Phaser；
- 规则要可测试；
- 状态变化要能生成 `ActionLogEntry`；
- 所有数值变动要可解释。

### 3.4 Content Agent

负责：

- 地点；
- 路线；
- NPC；
- 对话；
- 每日事件；
- 邮件；
- 消息；
- 账单；
- 菜谱；
- 成就。

可改：

```text
frontend/src/content/
docs/content_notes/
```

不可改：

- Game Core 规则；
- Vue / Phaser 代码；
- AI provider 代码；
- 未授权图片；
- 未审核真实评论原文。

要求：

- 必须符合 `CONTENT_SCHEMA.md`；
- 真实世界数据必须写 `source`；
- 不确定数据用 `confidence` 标注；
- 生成内容默认 `review_status: "draft"`；
- 每次新增内容说明用途和触发位置。

### 3.5 Curriculum Agent

负责：

- 德语 KP；
- Academic English；
- AS Mathematics 入门；
- A-levels 后续扩展；
- 作业和测试题；
- 学习目标映射。

可改：

```text
docs/curriculum/
frontend/src/content/*/lessons.json
frontend/src/content/*/homework.json
frontend/src/content/*/tests.json
```

不可改：

- 游戏地图；
- UI 结构；
- AI provider；
- 没有来源的考试知识点。

要求：

- KP 必须有官方或权威来源；
- MVP 先做少量高质量内容；
- 不一次性扩到 33 科；
- 每个 lesson 要映射到具体游戏场景或学习目标。

### 3.6 AI Backend Agent

负责：

- FastAPI；
- ASR；
- TTS；
- LLM 对话；
- 发音评估；
- AI Gateway；
- AI 错误兜底。

可改：

```text
backend/app/
backend/tests/
docs/API_STACK.md
```

不可改：

- 前端主玩法；
- 内容大纲；
- secrets vault；
- 付费价格策略。

要求：

- 从环境变量读取密钥；
- 不打印密钥；
- API 返回结构化 JSON；
- 记录 latency、provider、model、cost estimate；
- AI 失败时返回可用的 fallback。

### 3.7 Agent Pipeline Agent

负责：

- POI 导入草稿；
- 餐厅和菜单草稿；
- 预算平衡草稿；
- 课程草稿；
- 合规检查；
- review task。

可改：

```text
backend/app/agents/
scripts/content/
frontend/src/content/drafts/
docs/agent_runs/
```

不可改：

- `published` 内容；
- Game Core；
- UI；
- secrets。

要求：

- 输出必须是 draft；
- 保留 source record；
- 不复制未授权评论、图片、菜单照片；
- 不编造实时票价或营业时间；
- 人工审核后才能合并到正式 content。

### 3.8 QA Agent

负责：

- 验收；
- 测试；
- bug report；
- 数据 schema 检查；
- 构建检查；
- 回归检查。

可改：

```text
frontend/tests/
backend/tests/
scripts/validate_content.*
docs/QA_REPORTS/
```

谨慎改：

- 小型 bugfix。

不可改：

- 大规模重构；
- 产品方向；
- 内容策略。

要求：

- 优先报告问题；
- 给出复现步骤；
- 标明严重程度；
- 能修的小 bug 可以修，但不能顺手改架构。

---

## 4. 文件所有权

| 路径 | 主要负责 agent | 备注 |
|---|---|---|
| `docs/PROJECT_FRAMEWORK.md` | Architecture | 总架构 |
| `docs/AGENT_WORKFLOW.md` | Architecture | 分工规则 |
| `docs/CONTENT_SCHEMA.md` | Architecture / Content | schema 变更需谨慎 |
| `frontend/src/core/` | Game Core | 纯逻辑 |
| `frontend/src/content/` | Content | 游戏内容 |
| `frontend/src/components/` | Frontend | Vue UI |
| `frontend/src/phaser/` | Frontend | Phaser 渲染 |
| `frontend/src/stores/` | Frontend / Game Core | 过渡层 |
| `backend/app/services/` | AI Backend | AI 服务 |
| `backend/app/agents/` | Agent Pipeline | 内容生产 |
| `docs/curriculum/` | Curriculum | 课程知识库 |
| `assets/` | Frontend / Art | 图片素材 |

---

## 5. 变更流程

### 5.1 新功能

1. 判断所属模块；
2. 查 `PROJECT_FRAMEWORK.md` 是否已有位置；
3. 若没有，先更新架构文档；
4. 定义或更新 schema；
5. 写最小实现；
6. 加内容；
7. 构建或测试；
8. 写交付说明。

### 5.2 新内容

1. 查 `CONTENT_SCHEMA.md`；
2. 添加到对应 `frontend/src/content/{city}/` 文件；
3. 标记 `review_status`；
4. 如涉及真实数据，写 `source`；
5. 运行 schema 检查；
6. 运行前端构建。

### 5.3 AI 接入

1. 不直接在前端接供应商；
2. 先在 `backend/app/services/` 封装；
3. 再在 `backend/app/api/` 暴露统一接口；
4. 前端只调项目自己的 AI Gateway；
5. 提供 fallback；
6. 记录成本和延迟。

---

## 6. 冲突处理

如果两个 agent 的改动冲突：

1. 保留用户最新明确要求；
2. 保留已运行验证通过的最小改动；
3. 不删除对方新增内容；
4. 若内容和代码冲突，优先修 schema / adapter，而不是硬删内容；
5. 若方向冲突，回到根目录项目设计文档和 `MVP_IMPLEMENTATION_PLAN.md`。

---

## 7. 完成标准

一个任务完成时，agent 应说明：

- 改了哪些文件；
- 属于哪个模块；
- 如何验证；
- 有哪些未做或需要后续处理；
- 是否触碰了其他 agent 的责任区。

如果没有验证，也要明确说明原因。
