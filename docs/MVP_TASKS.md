# MVP 任务清单与验收标准 v2.0

> 目标: 4-6 周内完成"柏林第 1 关"完整闭环 + 走遍德国地图骨架
> 版本: v2.0  ·  2026-06-21  ·  适配 PROPOSAL.md v2.0

---

## Phase 0: 技术验证(1-2 周)

### Task 0.1: 阿里云账号 + DashScope API Key
- [ ] 注册阿里云账号
- [ ] 开通百炼服务
- [ ] 创建 API Key
- [ ] 配置 `DASHSCOPE_API_KEY` 环境变量

**验收**: 4 个 API(LLM/TTS/ASR/评估)都能用 SDK 调通

### Task 0.2: Python 最小 demo 脚本
- [ ] 脚本功能: 录音 → ASR → Qwen → CosyVoice → 播放
- [ ] 中文测试一遍
- [ ] 德语测试一遍
- [ ] 记录延迟(每段响应时间)

**验收**: 5 分钟内跑通,延迟 < 5 秒

### Task 0.3: Qwen2-Audio 评估实测
- [ ] 录制 5 段不同水平德语(初学/中级/高级 × 短句/长句)
- [ ] 调用 Qwen2-Audio API
- [ ] 评估输出质量
- [ ] 写 1 页评估报告

**验收**: 报告给出"用"或"不用 Qwen2-Audio"的明确决定

### Task 0.4: 选教材 + 拆第 1 关
- [ ] 教材:*Menschen A1*
- [ ] 第 1 关:柏林 Hauptbahnhof 问路(完整 JSON 剧本)
- [ ] 第 1 个 NPC:Peter(Info-Mitarbeiter)

**验收**: `backend/app/data/scenarios/berlin_bahnhof_01.json` 文件,有完整 Rounds

### Task 0.5: 美术学习与试画
- [ ] 下载 Aseprite 或 LibreSprite
- [ ] 看 2-3 个像素艺术教程(2-3 小时)
- [ ] 试画 1 个 NPC 头部(测试风格)
- [ ] 试画 1 个 UI 按钮

**验收**: 试画文件存档,确认美术风格

**Phase 0 完成时**:**Decision Gate** —— 决定是否进入 Phase 1。

---

## Phase 1: MVP(4-6 周)

### Week 1-2: 后端核心

#### Task 1.1: 项目骨架
- [ ] FastAPI 项目初始化
- [ ] 配置 `.env`
- [ ] 路由规划:`/api/v1/dialogue`, `/api/v1/scenarios`, `/api/v1/progress`
- [ ] 健康检查 `/health`

**验收**: `uvicorn main:app` 启动

#### Task 1.2: 阿里云服务封装
- [ ] `services/asr.py` - Fun-ASR 封装(德语)
- [ ] `services/tts.py` - CosyVoice 封装(流式,德语)
- [ ] `services/llm.py` - Qwen-Plus 封装(NPC 对话)
- [ ] `services/eval.py` - Qwen2-Audio 封装(发音+语法评估)
- [ ] `services/encyclopedia.py` - LLM 辅助生成城市百科

**验收**: 每个 service 有独立 demo 脚本

#### Task 1.3: 对话引擎
- [ ] 状态机: 等待玩家 → 转写 → 评判 → NPC 回复
- [ ] 剧本加载器(读 JSON)
- [ ] 反馈卡生成
- [ ] WebSocket 推流(NPC 音频流式)

**验收**: 单元测试覆盖主流程

#### Task 1.4: 数据模型 + 持久化
- [ ] Pydantic models(User, Progress, Error, Vocabulary, Session)
- [ ] SQLite 存储(本地,不需要后端服务)
- [ ] 迁移到 PostgreSQL 的设计(代码层面预留)

**验收**: 数据读写正常,接口符合 [ARCHITECTURE.md](ARCHITECTURE.md) 设计

### Week 3-4: 前端核心

#### Task 1.5: 前端框架初始化
- [ ] Vite + React + TypeScript
- [ ] 引入 Phaser 3
- [ ] 引入 Zustand(状态管理)
- [ ] 引入 React Router

**验收**: `npm run dev` 跑通,显示空白 Phaser 场景

#### Task 1.6: 核心层(可复用到 Godot)
- [ ] `core/dialogue-state.ts`
- [ ] `core/scenario-loader.ts`
- [ ] `core/progress-tracker.ts`
- [ ] `core/api-client.ts` (IApiClient 接口 + LocalStubApiClient)
- [ ] `core/feedback-generator.ts`

**验收**: 单元测试通过,接口稳定

#### Task 1.7: 游戏场景(Phaser)
- [ ] BootScene(启动加载)
- [ ] MapScene(德国地图骨架,可点击 Berlin)
- [ ] CityScene(城市章节,显示关卡列表)
- [ ] DialogueScene(关卡对话,显示 NPC + 对话框)

**验收**: 能从地图 → 城市 → 关卡 → 对话场景导航

#### Task 1.8: React UI 层
- [ ] DialogueBox(对话气泡)
- [ ] MicButton(录音按钮)
- [ ] FeedbackCard(反馈卡)
- [ ] CityEncyclopedia(城市百科)
- [ ] MapOverlay(地图覆盖层)

**验收**: 各个 UI 组件可独立测试

#### Task 1.9: 录音 + 音频处理
- [ ] Web Audio API 录音(16kHz mono PCM)
- [ ] 上传后端
- [ ] 接收 NPC 音频流并播放

**验收**: 在浏览器录音,后端返回音频,前端播放

### Week 5-6: 整合 + 美术

#### Task 1.10: 美术(用户自己画)
- [ ] Peter 立绘 4 张(neutral / smile / surprise / thinking)
- [ ] 柏林 Hauptbahnhof 场景背景 1 张
- [ ] UI 元素(对话框、按钮、徽章)
- [ ] 反馈卡背景
- [ ] 德国地图骨架(简化版)

**详细规格见 [ART_ASSETS.md](ART_ASSETS.md)**

**验收**: 美术文件齐备,符合风格指南

#### Task 1.11: 端到端打通
- [ ] 地图 → 城市 → 关卡 → 对话
- [ ] 录音 → 后端处理 → NPC 回复
- [ ] 反馈卡显示
- [ ] 进度保存

**验收**: 完整跑通 1 关,用户能完成对话

#### Task 1.12: 错误处理
- [ ] API 超时重试
- [ ] 录音失败提示
- [ ] 网络断开处理

**验收**: 异常情况不崩溃,友好提示

#### Task 1.13: 简单文档
- [ ] README(项目介绍 + 启动方式)
- [ ] 1 段 demo 视频(2 分钟)

**验收**: 别人能跟着跑起来

---

## Phase 1 验收标准

### 必须达成(Must Have)

- [ ] 玩家能从德国地图点 Berlin,进入城市章节
- [ ] 看到第 1 关"在柏林火车站问路",开始对话
- [ ] 玩家说德语 → 听到 NPC Peter 德语回复
- [ ] 完成 5-6 回合对话
- [ ] 看到反馈卡(语法 + 发音 + 表达点)
- [ ] 看到城市百科卡(柏林 Hauptbahnhof)
- [ ] 进度本地保存(刷新后能继续)
- [ ] 系统稳定,5 轮对话不崩

### 加分项(Nice to Have)

- [ ] 反馈卡内容 85% 准确
- [ ] NPC 回复自然(不像机器人)
- [ ] 加载时间 < 3 秒
- [ ] 移动端响应式(手机能玩)
- [ ] 简单的关卡失败提示(没拿到 80% 表达点可重试)

### 成本目标

- 1 关完整对话 API 成本 < ¥0.2
- 5 段不同德语发音评估成本 < ¥0.3

---

## Phase 2: 完整柏林 5 关 + 城市百科系统(6-8 周)

**前提**: Phase 1 完成 + 用户验证教学设计 OK

### Task 2.1: 柏林补全 4 个关卡
- [ ] 关卡 1.2:咖啡馆点单(Anna)
- [ ] 关卡 1.3:超市购物(Lisa)
- [ ] 关卡 1.4:看医生(Dr. Schmidt)
- [ ] 关卡 1.5:朋友家做客(Marie)

### Task 2.2: 城市百科系统
- [ ] 5 张柏林百科卡(覆盖 Kultur/Wirtschaft/Essen/Tourismus/Bildung)
- [ ] LLM 辅助生成初稿
- [ ] 用户审校流程
- [ ] 卡片展示 UI

### Task 2.3: 错题本 + 词汇本
- [ ] 错题自动收集(语法错误、发音问题)
- [ ] 词汇自动收集(本关新词)
- [ ] 复习界面(间隔重复算法 v1)

### Task 2.4: 进度可视化
- [ ] 地图上显示已解锁城市
- [ ] 城市内显示已通关关卡
- [ ] 总进度统计

### Task 2.5: 慕尼黑 + 汉堡(各 5 关)
- [ ] 慕尼黑 5 关(工业 / 啤酒节 / 阿尔卑斯)
- [ ] 汉堡 5 关(港口 / 媒体)
- [ ] 新 NPC 立绘

**Phase 2 验收**:
- 完整 1 个州(Berlin)体验
- 3 城市 15 关
- 错题本 + 词汇本可用
- 反馈卡持续优化

---

## Phase 3: 用户系统 + 跨设备(8-12 周)

### Task 3.1: 后端上云
- [ ] FastAPI 部署到阿里云 ECS / 函数计算
- [ ] PostgreSQL 数据库(阿里云 RDS)
- [ ] 阿里云 OSS 存音频
- [ ] 域名 + HTTPS

### Task 3.2: 用户系统
- [ ] 注册/登录(邮箱 + 密码)
- [ ] 第三方登录(Google / Apple)
- [ ] 数据迁移(本地 → 云端)
- [ ] 跨设备进度同步

### Task 3.3: Tauri Desktop 打包(可选)
- [ ] 集成 Tauri
- [ ] Windows / macOS / Linux 包
- [ ] 自动更新机制

### Task 3.4: 5-10 个城市
- [ ] 科隆 / 法兰克福 / 海德堡 / 莱比锡 / 杜塞尔多夫
- [ ] 5 城市 5 关 = 25 关

**Phase 3 验收**:
- 完整注册/登录 + 跨设备
- 5-10 城市内容
- 8-10 个 NPC

---

## Phase 4: 德福备考专题(8-12 周)

### Task 4.1: 留学场景关卡
- [ ] 大学注册(Immatrikulation)
- [ ] 租房(WG / 公寓 / 合同)
- [ ] 银行开户(Konto eröffnen)
- [ ] 延签(Aufenthaltstitel verlängern)

### Task 4.2: 阅读 + 写作训练
- [ ] 城市百科 → 阅读理解题目
- [ ] 写作任务(应用文 / 邮件 / 短文)

### Task 4.3: 德福模拟
- [ ] 4 项真题(对话式而非纸质)
- [ ] 评分系统(对齐德福 TDN 等级)

**Phase 4 验收**:
- 用户实测德福能到 TDN 4
- B2-C1 难度内容
- 留学场景完整覆盖

---

## Phase 5: 完整版(6-12 个月)

- [ ] 全 16 州 60-100 关
- [ ] Godot 4 重写(可选)
- [ ] 移动端(iOS / Android)
- [ ] 商业化(订阅 / 一次性买断)

---

## 不在 MVP 范围(MUST NOT)

- ❌ 用户注册/登录(MVP 用本地 UUID)
- ❌ 完整本 A1 教材(MVP 只 1 关)
- ❌ 移动端 App(MVP 只 Web)
- ❌ 复杂动画(MVP 只基础切换)
- ❌ 跟读发音评分(MVP 不做,后期加)
- ❌ 实时流式对话(MVP 用回合制)
- ❌ 排行榜 / 社交(MVP 无)
- ❌ 数据分析 / 埋点
- ❌ 国际化 i18n

---

## 风险与备选

| 风险 | Phase 影响 | 备选 |
|------|----------|------|
| Qwen2-Audio 评估不准 | 反馈差 | 切 wav2vec2 + LLM 组合 |
| LLM 跳出剧本 | 教学失控 | 强 system prompt + 输出 schema 约束 |
| 美术跟不上 | 视觉差 | 占位符(emoji + 色块)先上 |
| 城市百科工作量爆炸 | 进度慢 | LLM 生成 + 模板填充 |
| 阿里云 API 涨价 | 成本增 | 切自建(已在 ARCHITECTURE 预留) |
| 5 周完不成 MVP | 计划延 | 砍掉反馈卡,先做能玩 |
| 用户对教学设计不满 | 重做 | 5-10 个种子用户测试后再继续 |

---

## 关键里程碑

| 时间 | 里程碑 | 检验 |
|------|--------|------|
| Week 1 末 | Phase 0 完成 | 4 API 跑通,剧本写出 |
| Week 2 末 | 后端核心可用 | Python 脚本能跑 1 回合对话 |
| Week 4 末 | 前端框架选好 | 能打开网页看地图 → 关卡 |
| Week 6 末 | MVP 完成 | 第 1 关可玩,反馈卡准确 |
| Week 12 末 | Phase 2 完成 | 柏林 5 关 + 慕尼黑/汉堡 10 关 |
| Week 24 末 | Phase 3 完成 | 5 城市 + 用户系统 + 跨设备 |
| Week 36 末 | Phase 4 完成 | 德福 B2-C1 备考 |
| Month 12 | Phase 5 完成 | 60+ 关,全德地图 |

---

## 验证方法

每个 Phase 完成后:
1. 自己完整跑一遍
2. 找 1-2 个朋友测试
3. 收集反馈(对话是否自然 / 反馈是否有用 / 是否愿意再玩)
4. 决定是否进入下一 Phase

**种子用户**: 在德语学习群、Reddit r/German、知乎、小红书等找 5-10 个真实学习者测试。

---

OK,MVP 任务清单到这里。等你确认 Phase 0 的事(API Key、教材、第 1 关剧本、美术试画),我开始写代码。
