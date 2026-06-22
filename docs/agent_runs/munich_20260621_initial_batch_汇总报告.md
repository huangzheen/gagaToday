# Munich MVP 初始批次 · 汇总报告

**批次**: `munich_20260621_initial_batch`
**日期**: 2026-06-21
**覆盖**: 4 个数据 agent(交通 / 美食 / 探索 / NPC)
**关联批次**: `munich_20260621_initial_audit`(美术,已完成)

---

## 一、总产出统计

| 类别 | 数量 |
|---|---|
| Draft JSON 文件 | 34 (交通 8 + 美食 9 + 探索 9 + NPC 8) |
| Draft JSON 总行数 | ~3,400 行 |
| Draft 数据记录 | 153 条 |
| Agent run docs | 12 (4 agent × 运行总结 + 合规 + 审核) |
| Source records | 105 个独立 source(官方站 + Wikipedia + Aldi + 用户上传) |
| 总目录 | `frontend/src/content/drafts/{transport,food,exploration,npcs}/munich_20260621_initial_batch/` |

---

## 二、4 个 Agent 产出概览

### P3 交通 (8 JSON / 45 条记录)

```
transport_stations.draft.json       8  stations
transport_lines.draft.json          7  U3/U4/U5/U6 + S1/S8 + Tram 19
transport_fares.draft.json          7  单程/短程/日票/条形/Deutschlandticket/IsarCard/U21
route_presets.draft.json            8  住宿↔学校↔面包店↔HBF↔机场
travel_time_estimates.draft.json    5  等待时长 + 配速
transport_passes.draft.json         3  月票
transport_knowledge_cards.draft.json 7  打卡/票价/Streik/问路
```

### P4 美食 (9 JSON / 53 条记录)

```
food_items.draft.json               10  Brötchen/Brezn/Schweinshaxe/Weißwurst/Spätzle/Currywurst/Apfelschorle/Schnitzel/Lebkuchen/Kaffee
food_culture_cards.draft.json       5  面包店/12 点规则/Kaffee/Abendbrot/Schulbrot
ingredients.draft.json              8  蛋/吐司/意面/番茄酱/黄油/奶酪/Brezn/土豆
recipes.draft.json                  5  蛋吐司/意面/三明治/Brezn黄油/土豆沙拉
cooking_steps.draft.json            7  含计时器 / 点击步骤
food_achievements.draft.json        6  6 种成就
grocery_price_estimates.draft.json  7  Aldi + 面包店价格
nutrition_notes.draft.json          5  含未成年酒精边界
```

### P5 探索 (9 JSON / 54 条记录)

```
exploration_locations.draft.json    9  Marienplatz/Frauenkirche/Viktualienmarkt/Deutsches/Englischer Garten/Nymphenburg/BMW/Olympiapark/Allianz
checkin_targets.draft.json          6  钟琴/塔顶/Eisbach/Biergarten/公园散步/矿区寻宝
ticket_prices.draft.json            8  含 3 个免费
opening_hours.draft.json            7  含 Viktualienmarkt 周日关门
knowledge_cards.draft.json          6  建筑/历史/文化
history_stories.draft.json          4  标 historical_fact / local_legend / cultural_context
treasure_items.draft.json           6  魔鬼脚印/Glockenspiel/Eisbach/美人画廊/Maibaum/矿区
image_candidates.draft.json         7  5 CC-BY-SA + 1 用户上传 + 1 FC Bayern 拒绝
```

### P6 NPC (8 JSON / 50 条记录)

```
npc_profiles.draft.json             8  Schneider 家 + Anna + Peter + Brown + Müller + Li Ming + Wagner
npc_schedules.draft.json            5  weekday 日程
relationship_profiles.draft.json    5  friendship/trust/familiarity 维度
npc_dialogue_hooks.draft.json       10 问候/点餐/介绍/邀请等
relationship_events.draft.json      8  低能量/宵禁/做饭/点餐/邀请/想家/作业/小测
shared_memories.draft.json          6  共同记忆与事件绑定
npc_safety_notes.draft.json         6  全员 all_ages + 全局政策
```

---

## 三、Schema 合规审计结果

✅ **通过**:
- 34 个 draft JSON 全部是数组
- 每条记录有 `id` + `review_status`(已修复 cooking_steps)
- 价格字段都有 `retrieved_at` / `confidence`
- 历史故事明确分类(`historical_fact / local_legend / cultural_context / gameplay_summary`)
- 所有 NPC `fictionalized: true`,无真实人物身份
- Allianz Arena / FC Bayern 商标拒绝,改用 CC-BY-SA 摄影
- 用户上传图片标 `needs_review`

⚠️ **已知 schema 缺口**(已在 P0/P1 提的迁移建议):

1. **Location ID 命名不一致**:
   - NPC 用语义 ID:`host_home / school / bakery / library`
   - Exploration 用前缀 ID:`explore_munich_*`
   - Transport 用前缀 ID:`station_munich_*`
   - **建议**: schema 强制要求 `location_munich_*` 格式,所有 draft 引用同一个 Location 表

2. **POI 缺 `real_coords` / `map_layer` / `scene_entry`**:已在地图POI智能体.md 标"需提交迁移建议"

3. **预算系统缺模型**:`Transaction / ExpenseCategory / BudgetRule / ParentSupportRule` — 已在欧元预算智能体.md 标

4. **美术缺 `ArtAsset` 整体模型** — 已在美术资产智能体.md 标

---

## 四、版权问题决策记录

按你的指示:**版权问题先忽略,发布前统一修改**。本批次处理如下:

| 风险项 | 当前处理 |
|---|---|
| Allianz.png 真实保险品牌 | 已标 `rejected_for_use`,游戏 UI 用 AI 占位 |
| FC Bayern / Allianz 商标 | image_candidates 拒绝 |
| Hofbräuhaus 官方图片(Schwemme) | 已有书面授权讨论文档,继续 |
| 用户上传慕尼黑大教堂.png | 标 `needs_review`,待你确认版权 |
| Anna 柏林 NPC 复用慕尼黑 | 标 `reuse_note`,立绘保持 |
| 8 张 user_2026_06_21/*.png | 已在美术 agent 整理,未在本批 draft 引用 |

---

## 五、跨 Agent 一致性

✅ **探索↔交通**: exploration 的 5 个 near_station_ids 全部对应 transport_stations 已有的 station ID

⚠️ **NPC↔探索/Location**: NPC 用 `host_home / school / bakery / library / englischer_garten / viktualienmarkt` 语义 ID,但 exploration draft 没用同样 ID(用 `explore_munich_englischer_garten`)
- **影响**: 跨 agent 数据迁移时需要做 ID 映射
- **修复建议**: 等架构 agent 把 Location 模型合并到 CONTENT_SCHEMA.md 时,统一定义 `location_munich_englischer_garten` 等

✅ **NPC↔美食**: Anna 在 bakery,与 food_brötchen / food_brezn 联动一致

✅ **探索↔美食**: Viktualienmarkt 在两个 agent 都出现,联动一致

---

## 六、需要你拍板的决策

### 决策 D1: Anna 复用策略(发布前)
- [ ] 接受"复用柏林 NPC 到慕尼黑面包店" + 标 `reuse_note` + 后续精修?
- [ ] 还是现在直接做慕尼黑特化版本?

### 决策 D2: 学校具体位置
- [ ] 学校在哪?(决定所有"住宿↔学校"路线的分钟数)
- [ ] 推荐虚构位置: Schwabing / Maxvorstadt 国际学校片区

### 决策 D3: 用户上传图片版权
- [ ] 慕尼黑大教堂.png 能否用于游戏?
- [ ] 是否还有其它 user_2026_06_21/*.png 需要归类?

### 决策 D4: Allianz Arena 进 MVP?
- [ ] 当前只在可选支线 — 是否加进球迷日剧情?
- [ ] 还是继续推迟?

### 决策 D5: 关系事件强度
- [ ] Frau Schneider curfew_violation 的 parent_like_trust -8 是否过严?(建议 -4)
- [ ] 第一次做饭的 parent_like_trust +8 是否合适?

### 决策 D6: 哪个 agent 负责合并 schema 迁移建议?
- [ ] 5 个 schema 扩展建议(POI 字段 + 4 个预算模型 + ArtAsset)集中提交给架构智能体?
- [ ] 还是你拍板直接合并到 CONTENT_SCHEMA.md?

---

## 七、Agent Run 总览

每个 agent 在 `docs/agent_runs/{德国交通,德国美食,德国探索,NPC}/munich_20260621_initial_batch/` 下都生成了:
- `运行总结.md` — 产出清单 + 覆盖范围
- `合规报告.md` — 来源 / 版权 / 未成年人 / Schema 审计
- `人工审核任务.md` — P0/P1/P2/P3 分级任务

---

## 八、下一步建议

1. **P10**:架构 agent 合并 5 个 schema 扩展建议到 `CONTENT_SCHEMA.md`,统一定义 Location ID
2. **P11**:你做人工审核 P0(Anna 复用、学校位置、用户图片版权、价格)
3. **P12**:通过审核后,迁入 `frontend/src/content/munich/{transport,food,exploration,npcs}/`
4. **P13**:内容流水线 agent 做 dialogue 详细文本(Anna / Frau Schneider / Frau Müller 等)
5. **P14**:NPC 立绘由美术 agent 生成(ann_* + frau_schneider + peter 等 8 个 NPC × 2-3 表情)

---

**生成者**: Mavis (main agent)
**审核状态**: 4 个 draft + 12 个 agent_run docs 全部就位,等待人工 review
**License**: 内部 MVP 使用