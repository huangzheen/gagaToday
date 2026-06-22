# gagaToday — Munich MVP Game Design

> 当前第一版实际基线 · v0.1.0 · 2026-06-22

## 版本说明

| 项 | 内容 |
|---|---|
| **状态** | 当前主线 |
| **规模** | 慕尼黑 5 个 POI / 1 个游戏日(Day 1 闭环)/ 单机 Web Demo |
| **数据版本** | `content_version: mvp-0.1` |
| **技术栈** | Vue 3 + Pinia + Phaser 3 + Vite / 无后端 / 本地存档 |
| **详细实施计划** | [MVP_IMPLEMENTATION_PLAN.md](./MVP_IMPLEMENTATION_PLAN.md) |
| **工程分层** | [PROJECT_FRAMEWORK.md](./PROJECT_FRAMEWORK.md) |
| **长期愿景(冻结)** | [GAME_DESIGN_v2.0_ASPIRATIONAL.md](./GAME_DESIGN_v2.0_ASPIRATIONAL.md) |

---

## 1. 基础设定

### 1.1 主角

| 字段 | 值 |
|---|---|
| 姓名 | Lena |
| 年龄 | 16(初三毕业后) |
| 国籍 | 中国 |
| 起点城市 | 慕尼黑(München) |
| 起点日期 | Year 1 · 9 月 1 日 · Monday · morning |
| 起点位置 | 寄宿家庭(Gastfamilie) |

### 1.2 初始属性(`player_start.json`)

```yaml
wallet:
  cash_eur: 500            # 起始现金
  monthly_support_eur: 650 # 家庭每月资助

status:
  energy: 80               # 体力
  mood: 75                 # 心情
  stress: 20               # 压力
  health: 90               # 健康

skills:
  german: { cefr: A0, xp: 0 }
  english: { cefr: B1, xp: 0 }
  math: { level: igcse_bridge, xp: 0 }
  life: { xp: 0 }

parent_trust: { level: 2, score: 60 }
```

### 1.3 设计原则(MVP Phase 1)

1. **数据驱动**:所有内容(locations / dialogues / tasks / routes / daily_events)通过 `content/munich/*.json` 加载,改 JSON 即可扩展
2. **三层架构**:Vue/Phaser 只渲染;`core/*` 只算规则;`content/*` 只描述
3. **离线优先**:localStorage 存档,刷新可恢复
4. **AI 不阻塞**:3 个语音任务可后置,MVP Day 1 用固定剧本兜底
5. **每个改动记录来源**:`source_records.json` 跟踪数据出处

---

## 2. 慕尼黑 5 个 POI

`frontend/src/content/munich/locations.json`

| ID | 德语名 | 中文 | 类型 | 难度 | EN% | NPC | 坐标(x,y) | MVP 角色 |
|---|---|---|---|---|---|---|---|---|
| `host_home` | Gastfamilie | 寄宿家庭 | home | A1 | 100 | Frau Schneider | 0.16, 0.68 | 每日起点终点 |
| `school` | Internationale Schule | 国际学校 | school | A1 | 100 | Herr Weber | 0.36, 0.34 | 学习核心 |
| `bakery` | Bäckerei am Platz | 广场面包店 | bakery | A1 | 40 | Anna | 0.55, 0.56 | 第一次买面包 |
| `supermarket` | Supermarkt | 超市 | grocery | A1 | 30 | Kassierer | 0.72, 0.72 | 预算与购物 |
| `library` | Stadtbibliothek | 市立图书馆 | library | A1 | 60 | Frau Keller | 0.70, 0.28 | 学习与关系 |

**MVP Phase 1 启用**:全部 5 个 POI 都参与 Day 1 闭环。

---

## 3. NPC 与对话(`dialogues.json`)

每个 POI 一个 NPC 对话脚本,统一结构:

```yaml
npc_name_de: Anna
npc_name_zh: Anna 店长
npc_role: Bäckerei-Inhaberin
npc_portrait: /assets/characters/anna/anna_smile.png
lang_pref: de  # 'de' | 'mixed' | 'en'
turns:
  - de: "Hallo! Was darf es sein?"
    zh: "你好！请问要点什么？"
    en: "Hello! What would you like?"
    options_de:
      - "Ein Brötchen, bitte. | 一个小面包,谢谢。"
      - "Was empfehlen Sie? | 您推荐什么？"
```

**MVP Phase 1 限制**:每个 NPC 仅 1 句对话 + 2 个选项。Phase 2 再扩展多轮对话树。

---

## 4. Day 1 任务闭环(`tasks.json`)

| 任务 ID | 标题 | 类型 | 触发点 | 奖励 | 失败效果 |
|---|---|---|---|---|---|
| `task_day01_get_to_school` | 准时到学校 | travel | school_morning deadline | +2 父母信任 / +5 life_xp / +2 心情 | +5 压力 / -3 心情 |
| `task_day01_order_brotchen` | 第一次独自买面包 | dialogue | bakery | +10 german_xp / +5 life_xp / +3 心情 / -€1.2 | — |
| `task_day01_reply_parent` | 回复父母消息 | message_reply | evening deadline | +3 父母信任 / -2 压力 | -4 父母信任 / +4 压力 |

**Day 1 流程线**:
```
起床(host_home) → 出门(travel) → 面包店(bakery,对话) → 学校(school,学习) → 放学 → 超市(supermarket,可选) → 图书馆(library,可选) → 回家(host_home) → 父母消息(message_reply) → 睡觉结算
```

---

## 5. 系统核心(8 个模块)

`frontend/src/core/` + `frontend/src/stores/game.js`

| 模块 | 文件 | 职责 | 状态 |
|---|---|---|---|
| player/state | `core/player/state.js` | PlayerState 工厂 + 状态栏派生 | ✅ 已实现 |
| events/effects | `core/events/effects.js` | applyEffects 通用效果应用 | ✅ 已实现 |
| economy/wallet | `core/economy/wallet.js` | spendMoney / 交易记录 | ✅ 已实现 |
| travel/routes | `core/travel/routes.js` | travelTo / findRoute 路线成本 | ✅ 已实现 |
| tasks/tasks | `core/tasks/tasks.js` | getActiveTasks / unlockTask / completeTask | ✅ 已实现 |
| calendar/time | `core/calendar/time.js` | advanceTimeBlock + TIME_BLOCKS | ✅ 已实现 |
| save/localSave | `core/save/localSave.js` | loadPlayerState / savePlayerState / clear | ✅ 已实现 |
| game store | `stores/game.js` | Pinia 状态层 + 动作封装 | ✅ 已实现 |

**统一入口**:`import { ... } from '@/core'` (`core/index.js`)

---

## 6. 内容数据(已批准 vs Drafts)

### 6.1 已批准(`content/munich/`,进入 MVP)

| 文件 | 行数 | 状态 |
|---|---|---|
| `locations.json` | 67 | approved |
| `player_start.json` | 54 | approved |
| `dialogues.json` | 92 | approved |
| `tasks.json` | 57 | approved |
| `routes.json` | 38 | approved |
| `daily_events.json` | 82 | approved |

### 6.2 待审核(`content/drafts/`,48 个 JSON,Phase 2/3 用)

```
drafts/
├── transport/         慕尼黑 U-Bahn/S-Bahn/DB 完整数据
├── art/               美术资产审计结果
├── restaurants/       Hofbräuhaus 详细档案
├── npcs/              NPC 完整档案(7-8 个)
├── exploration/       11 个景点 + 知识卡
└── food/              食谱 + 食材 + 价格 + 文化卡
```

**重要原则**:Drafts 内容**不可**直接被前端 import。所有使用必须先 review → approved → 移入 `content/munich/`。

---

## 7. Phase 1 验收标准

### Must Have(2 周内必须达成)

- [x] Phaser 骨架(Vue + Pinia + Phaser + Vite)
- [x] 慕尼黑 5 个 POI 数据
- [x] 5 个 NPC 对话脚本(单回合)
- [x] 3 个 Day 1 任务
- [x] PlayerState + 8 个核心模块接口
- [x] 本地存档(刷新可恢复)
- [ ] 玩家能从 Day 1 起床 → 出门 → 完成 3 任务 → 回家睡觉
- [ ] 至少发生一次花钱(€1.2 买面包)+ 一次学习(+10 german_xp)+ 一次对话+ 一次状态结算
- [ ] `npm run dev` 启动后浏览器可见慕尼黑地图 + 5 POI 可点击

### Nice to Have

- [ ] 多回合对话树(>1 turn)
- [ ] 时间推进(从 morning 到 evening)
- [ ] 失败惩罚实际生效
- [ ] 状态栏数值动态更新

### 不做(MUST NOT in MVP)

- 用户注册/登录
- 移动端 App
- 实时流式对话 / 跟读发音评分
- 全德国地图 / 实时路线 API
- 排行榜 / 社交 / 数据分析
- 全量 A-levels / 全量 IELTS

---

## 8. 当前骨架已能跑通的验证

```bash
cd frontend && npm run dev
# vite 已在 127.0.0.1:5173 监听
curl -I http://127.0.0.1:5173/                       # HTTP 200
curl http://127.0.0.1:5173/src/main.js                # 编译输出
curl http://127.0.0.1:5173/src/App.vue               # 编译输出
curl http://127.0.0.1:5173/src/phaser/BootScene.js   # 编译输出
curl http://127.0.0.1:5173/src/content/munich/locations.json  # 5 POI 数据
```

打开浏览器访问 http://127.0.0.1:5173/ 可见:
- 顶部 StatusBar(玩家状态)
- 中部 Phaser CityScene 慕尼黑地图(5 POI + 连线)
- 底部 DialogueBox(对话组件)
- Footer 标 v0.1.0 · Skeleton

---

## 9. 跟 v2.0 长期愿景的关系

[GAME_DESIGN_v2.0_ASPIRATIONAL.md](./GAME_DESIGN_v2.0_ASPIRATIONAL.md) 描述的是:
- 柏林 Mitte + 18 POI
- A-levels + 雅思双轨主线
- Track 系统 + 跨城旅行 + €900 月账
- 1860 个成就 + ~250 L/XP 路径

这些是**长期目标**,不是 MVP 范围。MVP 的第一版只做:
- 慕尼黑 5 POI
- 单一日内闭环
- 8 个核心模块 + Vue/Phaser 渲染

**Phase 1 完成后**,根据玩家反馈决定:
- (A) 慕尼黑扩 30 天(MVP Phase 4)
- (B) 慕尼黑完成后做柏林(对应 v2.0 部分)
- (C) 调头重做 Track 系统(对应 v2.0 核心)

---

## 10. 当前骨架需要继续补的(下一阶段)

| 优先级 | 缺口 | 工作量 | 备注 |
|---|---|---|---|
| P0 | 柏林占位图替换为慕尼黑场景图(`assets/scenes/munich/`) | 0.5d | 暂时可继续用柏林图占位 |
| P0 | Day 1 时序流程串通(起床→出门→面包店→学校→...→睡觉) | 2-3d | 当前各模块独立,需在 game.js 编排时序 |
| P1 | Vue App.vue 增加时序 UI(早/中/晚切换) | 1d | 状态栏已能显示 stats |
| P1 | NPC 多回合对话树 | 2d | 当前 1 turn,Phase 2 扩 3-5 turns |
| P2 | 失败效果触发(任务超时/钱不够) | 1d | task 定义已含 failure_effects |
| P2 | `daily_events.json` 接入 | 0.5d | 已有 82 行数据未接 |

---

## 11. 变更日志

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-06-22 | v0.1.0 | 新建 — 取代 v2.0 设计文档作为实际基线 |