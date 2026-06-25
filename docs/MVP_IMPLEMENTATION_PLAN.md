> ⚠️ **本文档当前未在实现中跟进**（标记于 2026-06-25 文档收敛）
>
> 描述的是 **B 方案：慕尼黑 30 天生活模拟**（时间/金钱/体力/日历/NPC 关系/做饭小游戏等）。
> 当前实现是 **A 方案：POI 探索 + 素材生成器**——见 [README.md](../../README.md) 和 [docs/ARCHITECTURE.md](../ARCHITECTURE.md)。
>
> 本文档保留作为远景参考。下一阶段决定是否启动 B 方案。
>
# gagaToday MVP Implementation Plan

版本：v0.1  
日期：2026-06-21  
主线来源：根目录 `gagaToday_project_design_document.md`

---

## 1. 项目实施原则

gagaToday 的 MVP 不做完整三年德国留学平台，而是先验证一个 30 天的可玩闭环：

> 玩家在德国慕尼黑附近生活，每天在有限时间、金钱、体力、语言能力和学习压力下做选择，并通过学习、社交、预算管理和城市探索获得成长。

MVP 的重点不是内容量，而是验证四件事：

1. 德国生活模拟是否有持续游玩动力；
2. 学习、预算、探索、社交是否能形成互相牵制的系统；
3. 关键德语语音任务是否能显著增强沉浸感；
4. 内容是否可以用数据驱动方式持续扩展。

---

## 2. 技术路线决策

### 2.1 MVP 客户端

MVP 继续使用当前仓库已有的 Web 技术栈：

- Vue 3；
- Pinia；
- Phaser 3；
- Vite；
- 本地存档。

原因：

- 仓库已有可运行骨架；
- 已有角色、场景、UI 像素素材；
- Web 版本便于快速演示、内测和投融资沟通；
- 后续可以通过 Tauri 或 Electron 包装成桌面 Demo；
- 核心玩法验证前，迁移 Godot 会增加不必要成本。

Godot 4 作为 Phase 2 之后的可选迁移方向。迁移前提是：MVP 玩法闭环和付费意愿已经验证。

### 2.2 后端

MVP 后端只承担必要职责：

- AI 语音任务；
- 内容 Agent 的离线生成与审核；
- 后续云存档预留。

早期不要让后端控制主玩法。主玩法应在客户端通过数据文件和本地存档跑通。

推荐后端栈：

- FastAPI；
- PostgreSQL；
- Redis 可后置；
- 对象存储可后置；
- AI Gateway 封装 ASR / TTS / LLM / 发音评估。

---

## 3. 旧文档与残留内容处理

### 3.1 作为主线的文档

- `gagaToday_project_design_document.md`

### 3.2 可回收内容

- `docs/ARCHITECTURE.md`：保留业务层和渲染层分离思想；
- `docs/API_STACK.md`：保留 AI API 组合方案；
- `docs/curriculum/KP_SCHEMA.md`：保留 KP 知识点体系；
- `docs/ART_ASSETS.md`：保留像素美术规范；
- `assets/`：保留现有角色、场景、UI 素材；
- `frontend/`：保留现有 Vue + Phaser 骨架。

### 3.3 需要降级或归档的内容

- 柏林第一关不再是主线，可作为技术测试场景；
- TestDaF / IELTS 不作为 MVP 主线；
- A-levels 33 科全量知识库不进入 MVP；
- React 架构设想不采用，当前代码以 Vue 为准；
- 全德国地图、实时路线 API、轻联网、全 NPC AI 都放到 MVP 之后。

---

## 4. MVP 内容边界

### 4.1 基础设定

- 城市：慕尼黑；
- 时间：30 个游戏日；
- 主角：15-16 岁中国学生，初三毕业后赴德国国际学校；
- 产品形态：单机 Web Demo；
- 路线：人工配置预设路线；
- AI：只用于 3 个关键语言任务；
- 存档：本地存档，预留 `player_id`、`cohort_id`、`content_version`。

### 4.2 地点

MVP 地点控制在 10 个：

1. 寄宿家庭 / 学生房间；
2. 学校；
3. 面包店；
4. 超市；
5. 图书馆；
6. 球场 / 体育馆；
7. Marienplatz；
8. Hauptbahnhof / U-Bahn 站；
9. Deutsches Museum；
10. 咖啡馆或食堂。

### 4.3 NPC

MVP NPC 控制在 8 个以内：

1. 寄宿家庭成员；
2. 德语老师；
3. 数学 / A-levels 老师；
4. 德国同学；
5. 中国留学生；
6. 面包店店长；
7. 图书馆管理员；
8. 朋友 / 轻量关系支线角色。

### 4.4 系统

必须进入 MVP：

- 每日循环；
- 时间、金钱、体力、心情；
- 地图与地点；
- 预设路线；
- 课堂、作业、小测；
- 德语 A1 语言任务；
- 预算系统；
- 父母信任与资助；
- 手机 / 邮件 / 信件；
- 兴趣打卡；
- 美食成就；
- 做饭小游戏；
- 基础 NPC 关系；
- 本地存档。

暂缓：

- 轻联网；
- 自由私聊；
- 全德国真实路线；
- 全量 A-levels；
- IELTS 全考试系统；
- 所有 NPC 实时 AI；
- 真实餐厅图片与商业平台评论。

---

## 5. 数据驱动内容结构

从 MVP 起，内容不应硬编码在 Phaser 场景或 Vue store 中。建议采用以下内容文件：

```text
frontend/src/content/
  munich/
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

第一阶段可以只实现：

- `locations.json`;
- `dialogues.json`;
- `routes.json`;
- `daily_events.json`;
- `player_start.json`。

后续再拆到数据库或远程 CMS。

---

## 6. 12 周实施计划

### Phase 1：第 1-2 周，产品收敛与一天闭环

目标：

- 确认 MVP 边界；
- 将硬编码内容迁移到 JSON；
- 跑通一个完整游戏日。

交付：

- `MVP_IMPLEMENTATION_PLAN.md`；
- 慕尼黑内容 JSON 初版；
- 起床、看手机、去学校、面包店、回家、睡觉结算；
- 基础状态栏；
- 本地存档草案。

验收：

- 玩家可以完成第 1 天；
- 至少发生一次花钱、一次学习、一次对话、一次状态结算；
- 页面刷新后能恢复基础状态。

### Phase 2：第 3-5 周，7 天可玩版本

目标：

- 扩展到一周生活；
- 引入预算、父母信任、作业、邮件。

交付：

- 7 天事件日历；
- 5 个地点；
- 4 个 NPC；
- 作业与小测；
- 邮箱与手机消息；
- 父母信任初版；
- 做饭小游戏 v1。

验收：

- 玩家可以玩完 7 天；
- 钱不够、作业没做、睡眠不足会影响后续；
- 至少有一个补救剧情。

### Phase 3：第 6-9 周，AI 与内容扩展

目标：

- 接入 3 个 AI 语音任务；
- 扩展到 15-20 天；
- 加入更完整的探索和关系反馈。

交付：

- FastAPI AI Gateway；
- 面包店点餐语音任务；
- 课堂自我介绍语音任务；
- 同学聊天语音任务；
- 8 个地点；
- 6 个 NPC；
- 成就与打卡系统；
- 餐饮与预算数值调优。

验收：

- AI 任务失败时有固定脚本兜底；
- 单次 AI 语言任务成本可控；
- 玩家能感受到学习能力影响世界解锁。

### Phase 4：第 10-12 周，30 天展示版本

目标：

- 完成可用于展示、测试和投资沟通的 MVP。

交付：

- 30 天内容；
- 10 个地点；
- 8 个 NPC；
- 一次月度学习反馈；
- 一次预算危机；
- 一次父母视频沟通；
- 一个周末探索高潮；
- Demo 引导和结尾总结；
- 基础官网 / Pitch Demo 素材。

验收：

- 新用户 20-40 分钟可体验核心乐趣；
- Demo 不依赖实时路线 API；
- AI 失败不阻塞主线；
- 内容扩展不需要改核心代码。

---

## 7. 核心工程任务拆解

### 7.1 前端

- 建立 `content` 数据目录；
- 抽离地点、NPC、对话、路线；
- 建立 `GameEngine` 或等价纯业务模块；
- 建立每日时间推进；
- 建立本地存档；
- 将 Phaser 只作为地图和场景渲染层；
- 将 Vue 负责状态栏、手机、邮件、对话框和弹窗 UI。

### 7.2 内容

- 慕尼黑 10 地点；
- 每地点 1-3 个交互；
- 第 1 周每日事件；
- 30 天日历；
- 8 个 NPC 的基础档案；
- 3 个 AI 语音任务脚本；
- 10-20 个德语 A1 KP；
- AS Mathematics 入门任务；
- Academic English 入门任务。

### 7.3 后端与 AI

- FastAPI 项目骨架；
- `/health`；
- `/api/ai/asr`；
- `/api/ai/tts`；
- `/api/ai/dialogue-eval`；
- `/api/ai/pronunciation-eval`；
- AI 失败兜底；
- 日志记录但不泄露密钥。

### 7.4 Agent

MVP 只做离线辅助，不做自动发布：

- POI Draft Agent；
- Food/Menu Draft Agent；
- Budget Balance Agent；
- Curriculum Builder Agent；
- Compliance Checker Agent。

所有 Agent 输出必须进入 `draft` 或 `needs_review`。

---

## 8. 第一周立即行动

1. 统一文档：将此文件作为实施主计划；
2. 新增慕尼黑 `content` 数据；
3. 改造前端从 JSON 读取地点与对话；
4. 做第 1 天流程；
5. 加入本地存档；
6. 运行 `npm run build` 验证。

---

## 9. 判断项目是否走对的指标

MVP 早期不看内容规模，看以下指标：

- 玩家是否愿意继续到第二天；
- 玩家是否理解钱、时间、体力、学习之间的取舍；
- 玩家是否会主动选择德语尝试而不是永远英文兜底；
- 玩家是否记得 NPC 和地点；
- 玩家是否因为预算或作业做出不同选择；
- 内容新增是否可以主要通过 JSON 完成。

如果这些成立，再扩城市、课程、Agent 和联网。
