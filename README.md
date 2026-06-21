# GermanLearning

> 一款用游戏化 + AI 语音 + 地图 RPG 帮中国学生备考德福的应用
> "走遍德国"——在沉浸式对话中解锁城市,学德语、了解德国

## 项目愿景

玩家用德语"走遍德国"——通过完成各地的生活任务解锁城市地图,在沉浸式 AI 语音对话中备考德福(TestDaF),同时学习德国文化、饮食、工商业、旅游知识。

**三轨道学习体系**(2026-06-21 扩展):
1. 🇩🇪 **德语** —— TestDaF TDN 4-5,主线
2. 🇬🇧 **雅思** —— 每科 7.0+,申请 TU9/精英大学英语项目硬门槛
3. 📐 **A-levels** —— Edexcel IAL 全科(33 科),学术深度证明

**目标用户**:中德班 / 雨中国高类型学生(初三毕业 → 10-11 年级 → 申请德国)

## 三大核心体验

1. 🎮 **三轨道对话训练** —— 德语 / 雅思口语 → NPC 语音对话;A-levels → 题库关卡
2. 🌍 **文化认知** —— 解锁城市百科卡(德国 16 州 + 英国文化对照)
3. 🗺️ **RPG 体验** —— 地图点亮、关卡解锁、城市征服(走遍德国 + 闯荡英美 + 学术塔)

## 技术栈

| 层级 | 选型 | 理由 |
|------|------|------|
| 客户端 | Vite + React + TypeScript + Phaser 3 | Web 优先,后期 Tauri 打包 Desktop |
| 后端 | FastAPI (Python) | 对接 DashScope SDK 方便 |
| LLM | 阿里云 Qwen-Plus / Qwen3-Max | 中文友好,德语强,价格便宜 |
| TTS | CosyVoice 3.5 Plus | 流式,150ms 首包,德语,音色克隆 |
| ASR | Fun-ASR 1.5 / Qwen3-ASR | 30-52 语种,德语支持 |
| 发音评估 | Qwen2-Audio-7B-Instruct | 直接吃音频,自然语言评估 |
| 美术 | Aseprite / LibreSprite | 像素艺术标准 |

## 路线图

- **Phase 0** (1-2 周): 技术验证 + 选教材 + 拆第 1 关
- **Phase 1** (4-6 周): MVP - 柏林 1 关完整闭环
- **Phase 2** (6-8 周): 柏林 5 关 + 慕尼黑/汉堡 + 城市百科
- **Phase 3** (8-12 周): 用户系统 + 跨设备 + 5-10 城市
- **Phase 4** (8-12 周): 德福备考专题(B2-C1)
- **Phase 5** (6-12 月): 完整 16 州 60-100 关

## 成本估算

- 单关完整对话: **¥0.08-0.15**
- 完整 1 城市 5 关: **¥0.4-0.75**
- 完整 A1(柏林 5 关): **¥0.4-0.75**
- Phase 2(3 城市 15 关): **¥1.2-2.3**

几乎可忽略,无需优化成本。

## 文档

### 项目核心文档
- [PROPOSAL.md](docs/PROPOSAL.md) - 完整项目实施方案 v2.0
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计(Web→Desktop + 用户系统)
- [API_STACK.md](docs/API_STACK.md) - 阿里云 API 选型与对接
- [SCRIPT_METHODOLOGY.md](docs/SCRIPT_METHODOLOGY.md) - 教材剧本化方法 v2.0
- [ART_ASSETS.md](docs/ART_ASSETS.md) - 美术素材清单(画师指南)
- [MVP_TASKS.md](docs/MVP_TASKS.md) - 4-6 周 MVP 任务清单

### Curriculum 知识库(2026-06-21 新建)
- **[curriculum/README.md](docs/curriculum/README.md)** —— 三轨道课程知识库总览
- **[curriculum/KP_SCHEMA.md](docs/curriculum/KP_SCHEMA.md)** —— KP 详细规范
- **[curriculum/routes/apply-to-germany.md](docs/curriculum/routes/apply-to-germany.md)** —— 申请德国路线(主路线)
- **[curriculum/tracks/deutsch/00-overview.md](docs/curriculum/tracks/deutsch/00-overview.md)** —— 德语轨道
- **[curriculum/tracks/ielts/00-overview.md](docs/curriculum/tracks/ielts/00-overview.md)** —— 雅思 4 项
- **[curriculum/tracks/alevels/00-overview.md](docs/curriculum/tracks/alevels/00-overview.md)** —— A-levels 33 科
- **[curriculum/tracks/alevels/knowledge-points/mathematics/c1-algebra.md](docs/curriculum/tracks/alevels/knowledge-points/mathematics/c1-algebra.md)** —— 数学 C1 algebra 完整 25 KP 拆解(模板)

## 目录结构

```
GermanLearning/
├── docs/                # 项目文档(6 个)
├── scripts/             # 独立工具脚本
├── assets/              # 美术资源(像素图、立绘、UI)
│   ├── characters/      # 角色立绘
│   ├── scenes/          # 场景背景
│   ├── ui/              # UI 元素
│   ├── cities/          # 城市徽章
│   ├── map/             # 地图素材
│   └── fonts/           # 像素字体
├── backend/             # Python 后端(FastAPI)
├── frontend/            # Web 前端(Vite + React + Phaser)
│   ├── src/
│   │   ├── core/        # 业务层(可复用到 Godot)
│   │   ├── game/        # 渲染层(Phaser,后期可换 Godot)
│   │   ├── ui/          # UI 层(React)
│   │   ├── audio/       # 录音/播放
│   │   ├── api/         # API 客户端
│   │   └── store/       # 状态管理
└── README.md            # 本文件
```

## 关键设计原则

1. **回合制对话**而非实时流式 —— 避开实时发音纠错难点,延迟更宽松
2. **Core 与 Game 分离** —— 业务层(可复用到 Godot)和渲染层(Phaser)解耦
3. **MVP 用本地 stub,Phase 2 切云端** —— API Client 接口稳定,业务代码 0 改动
4. **内容(JSON)与代码分离** —— 美术/内容创作者不写代码也能更新关卡
5. **AI API 抽象** —— 后期可切换开源/自建方案,脱钩云服务

## 下一步

按 [MVP_TASKS.md](docs/MVP_TASKS.md) 的 Phase 0 推进:

1. 你注册阿里云账号,开通百炼服务
2. 我跑通 Python demo 脚本(录音→ASR→Qwen→TTS→播放)
3. 我写柏林第 1 关(火车站问路)完整 JSON 剧本
4. 你试画 1 个 NPC 立绘测试风格
5. Decision Gate:确认教学设计 + 技术栈 OK 后进入 Phase 1
