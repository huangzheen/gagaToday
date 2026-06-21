# 教材剧本化方法 v2.0

> 把德福备考教材改编成"走遍德国"地图游戏关卡的具体方法
> 版本: v2.0  ·  2026-06-21  ·  适配 PROPOSAL.md v2.0:走遍德国 + 文化融入 + 德福

---

## 核心理念

**不是把教材"搬进"游戏,而是把教材"拆碎"再"重组"成地图探索剧情**。

玩家动机:
- 不是"我要学 Lektion 3"(教学驱动)
- 而是"我要解锁柏林下一个区域"(探索驱动 + 文化好奇)

**学习效果 = 沉浸动机 × 高频反馈 × 真实场景**

---

## 1. 整体内容架构(自顶向下)

```
德国地图(主界面)
  ↓
城市(柏林 / 慕尼黑 / 汉堡 / 科隆 / 法兰克福 / ...)
  ↓
城市章节(每个城市 3-5 关)
  ↓
关卡(1 个生活场景对话)
  ↓
回合(每回合 1 次玩家-NPC 交互)
```

**3 个内容创作层级**:
1. **地图层** (城市规划师): 决定哪些城市入选 + 解锁顺序
2. **城市层** (文化编辑): 写城市百科卡 + 决定本城主题
3. **关卡层** (剧本作者): 写具体对话 + 学习点

工作量分配:**地图 5% / 城市百科 25% / 关卡 70%**

---

## 2. 教材选型与映射(德福备考视角)

### 2.1 教材策略

| 阶段 | 教材 | 学习目标 | 城市范围 |
|------|------|---------|---------|
| Phase 1 (MVP) | *Menschen A1* | A1 生活场景 | 柏林(政治/文化) |
| Phase 2 | *Menschen A2* + *Aspekte B1+* | A2-B1 | 慕尼黑 + 汉堡 |
| Phase 3 | *Aspekte B2* + *Mit Erfolg zum TestDaF* | B2 | 5-8 城市 |
| Phase 4 | 德福真题 + 留学场景 | B2-C1,德福 TDN 4-5 | 10+ 城市 + 留学专题 |

**注意**: 不要硬把教材 Lektion 1:1 映射到关卡,而是按**生活场景**重组教材内容。

### 2.2 内容映射示例

**Menschen A1 Lektion 3 "Essen und Trinken"** → **多城市多个关卡**:

| 教材内容 | 改编为 |
|---------|--------|
| Kaffee, Tee, Wasser 等词汇 | 柏林关卡:咖啡馆点单 |
| 食物名称 (Brot, Käse, Wurst) | 慕尼黑关卡:啤酒节小吃 |
| Ich möchte... 句型 | 各城市复用 |
| Möchten Sie...? 句型 | 各城市复用 |

**不是 1 个 Lektion = 1 个关卡,而是 1 个 Lektion 的内容散布到多个城市多个关卡**。

---

## 3. 关卡设计流程(5 步)

### Step 1: 选场景(从城市主题出发)

每个关卡对应一个真实生活场景。

**柏林(Phase 1)5 个关卡**(示例):

| 关卡 | 场景 | 学习主题 | 难度 | 文化卡 |
|------|------|---------|------|--------|
| 1.1 | 火车站初到,问路 | Hallo, Entschuldigung, Weg | A1 | 柏林交通 |
| 1.2 | 咖啡馆点单 | möchten, 食物, 数字 | A1 | 柏林咖啡文化 |
| 1.3 | 超市购物 | 食品词汇, 价格 | A1 | 德国超市(Aldi/Lidl) |
| 1.4 | 看医生 | 身体部位, 预约 | A2 | 德国医疗系统 |
| 1.5 | 朋友家做客 | 自我介绍, 爱好, 礼物 | A2 | 柏林朋克文化 |

**第 1 关 (柏林火车站)** 的完整设计见后文示例。

### Step 2: 写场景背景

**场景设定三要素**:
- **地点**(具体街道 / 建筑 / 城市地标)
- **时间**(季节 / 一天中的时刻 / 节日)
- **NPC**(名字 + 职业 + 性格 + 语速)

**示例**:
```yaml
场景: 在柏林 Hauptbahnhof 中央火车站
时间: 周日上午 11:00
主角: 刚到柏林的中国留学生(玩家)
NPC: 
  - 信息员(Info-Person), 男, 50 岁, 柏林本地人, 语速慢
  
学习目标:
  - 5 个核心表达:Hallo, Entschuldigung, Wo ist..., Wie komme ich zum..., Danke
  - 2 个语法点:Wo 问句, zu + Dativ
  - 1 个文化点:柏林 Hauptbahnhof 是欧洲最大火车站之一
```

### Step 3: 设计 5-8 回合对话

**回合类型**:
- `npc_starts`: NPC 主动开场
- `player_responds`: 玩家回应(主要)
- `npc_continues`: NPC 继续说(没有玩家选择)
- `free`: 自由对话(高级关卡)

**每回合的设计模式**:
```
[Round X] 类型 / 目标
  NPC: <德语台词>
  玩家预期回复: <多个正确说法>
  提示(如需要): <可选>
  评判:
    语法: ✓ / 错误信息
    发音: ✓ / 错误音素
    理解度: 100% / 部分
  NPC 回复(基于评判):
    成功: <自然继续>
    失败: <自然重述,不直接纠错>
  反馈卡(关卡结束):
    知识点: <语法 + 词汇>
    发音: <如有>
    鼓励: <中文反馈>
```

### Step 4: 写 NPC 提示词 + 评判逻辑

**NPC 角色 LLM 提示词**:
```
你扮演 [场景] 中的 [角色]。

【角色设定】
- 名字: ...
- 年龄: ...
- 性格: ...
- 说话风格: ...

【本次对话目标】
玩家要完成的任务: ...
本次对话要练习的表达: [...]
本次对话要练习的语法: [...]

【对话规则】
1. 保持角色,不要跳出来当老师
2. 自然纠错,不要直接说"你语法错了"
   - 玩家说错时,你要"自然重复正确版本"
   - 例: 玩家说"Ich gehe zur Markt" → 你说"Ah, Sie gehen zum Markt"
3. 鼓励为主
4. 每次回复 1-2 句,不要超过 3 句
5. 推进对话,如果玩家卡住,主动引导
```

**评判 LLM 提示词**:
```
玩家刚才说: <玩家音频转写>

请评判:
1. 语法错误(如有):指出
2. 词汇错误(如有):指出  
3. 表达是否达成目标:是/部分/否
4. 给出 0-10 评分
5. 给玩家一个鼓励性的中文反馈(1 句话)

输出 JSON 格式:
{
  "transcription": "...",
  "grammar_errors": ["错误 1", "错误 2"],
  "vocabulary_errors": [],
  "target_achieved": "yes/partial/no",
  "score": 0-10,
  "feedback_zh": "..."
}
```

### Step 5: 写反馈卡(关卡结束)

**反馈卡 4 个区块**:
1. **评分** (0-10)
2. **语法错误**(本关玩家犯的)
3. **发音问题**(本关 Qwen2-Audio 报告的)
4. **掌握的表达**(达成目标)
5. **文化卡 + 城市百科更新**

---

## 4. 完整示例:柏林第 1 关

```json
{
  "scenario_id": "berlin_bahnhof_01",
  "version": "1.0",
  "metadata": {
    "name": "在柏林火车站问路",
    "city": "Berlin",
    "cefr_level": "A1",
    "textbook_ref": "Menschen A1, Lektion 1+2",
    "estimated_minutes": 5,
    "difficulty": 1,
    "is_first_scenario": true
  },
  "scene": {
    "location": "Berlin Hauptbahnhof, Information",
    "time": "Sonntag, 11:00",
    "npc": {
      "id": "info_peter",
      "name": "Peter",
      "role": "Info-Mitarbeiter",
      "personality": "hilfsbereit, ruhig",
      "voice_settings": {
        "speed": 0.9,
        "pitch": 1.0
      }
    }
  },
  "learning_objectives": {
    "expressions": [
      "Entschuldigung",
      "Wo ist...?",
      "Wie komme ich zum/zur...?",
      "Danke schön",
      "Tschüss"
    ],
    "grammar": [
      "Wo + ist + 名词(地点问句)",
      "zu + Dativ(方向)"
    ],
    "vocabulary": [
      { "word": "der Bahnhof", "translation": {"zh": "火车站"} },
      { "word": "das Hotel", "translation": {"zh": "酒店"} },
      { "word": "die Straße", "translation": {"zh": "街道"} },
      { "word": "links", "translation": {"zh": "左"} },
      { "word": "rechts", "translation": {"zh": "右"} },
      { "word": "geradeaus", "translation": {"zh": "直走"} }
    ],
    "culture": "柏林中央火车站(Hauptbahnhof)是欧洲最大的十字交叉式车站,日均客流量 30 万"
  },
  "rounds": [
    {
      "round_id": 1,
      "type": "npc_starts",
      "npc_says": "Hallo! Sie sehen aus, als ob Sie Hilfe brauchen. Kann ich Ihnen helfen?",
      "tts_voice": "peter_default"
    },
    {
      "round_id": 2,
      "type": "player_responds",
      "expected_says": [
        "Ja, bitte",
        "Entschuldigung",
        "Ich brauche Hilfe"
      ],
      "hints": ["Ja, bitte", "Entschuldigung"],
      "evaluation": {
        "grammar_check": true,
        "pronunciation_check": true,
        "must_understand": true
      },
      "feedback_on_success": {
        "npc_says": "Gerne! Was kann ich für Sie tun?",
        "points_awarded": []
      },
      "feedback_on_error": {
        "npc_says": "Ja, natürlich. Was kann ich für Sie tun?",
        "points_missed": []
      }
    },
    {
      "round_id": 3,
      "type": "player_responds",
      "prompt_for_player": "告诉 Peter 你想找一个酒店",
      "expected_says": [
        "Wo ist ein Hotel?",
        "Ich suche ein Hotel",
        "Wie komme ich zu einem Hotel?"
      ],
      "hints": [
        "Wo ist...?",
        "Ich suche..."
      ],
      "evaluation": {
        "grammar_check": true,
        "pronunciation_check": true,
        "must_understand": true,
        "key_expressions": ["Wo ist"]
      },
      "feedback_on_success": {
        "npc_says": "Klar! Das Hotel Adlon ist ganz in der Nähe. Gehen Sie hier rechts, dann geradeaus, etwa 5 Minuten zu Fuß.",
        "points_awarded": ["Wo ist", "Hotel"]
      },
      "feedback_on_error": {
        "npc_says": "Ah, Sie suchen ein Hotel! Das Hotel Adlon ist ganz in der Nähe. Gehen Sie hier rechts, dann geradeaus.",
        "points_missed": ["Wo ist"]
      }
    },
    {
      "round_id": 4,
      "type": "player_responds",
      "prompt_for_player": "确认方向,问怎么走",
      "expected_says": [
        "Wie komme ich dahin?",
        "Muss ich weit laufen?",
        "Ist es weit?"
      ],
      "hints": [
        "Wie komme ich...?",
        "Ist es weit?"
      ],
      "feedback_on_success": {
        "npc_says": "Nein, nur 5 Minuten. Sie gehen hier rechts, dann immer geradeaus, am Brandenburger Tor vorbei. Sehr schön!",
        "points_awarded": ["Wie komme ich"]
      }
    },
    {
      "round_id": 5,
      "type": "player_responds",
      "prompt_for_player": "道谢",
      "expected_says": [
        "Vielen Dank",
        "Danke schön",
        "Danke"
      ],
      "feedback_on_success": {
        "npc_says": "Gerne! Schönen Aufenthalt in Berlin!",
        "points_awarded": ["Danke"]
      }
    }
  ],
  "completion": {
    "min_rounds": 5,
    "success_criteria": "完成 80% 关键表达",
    "encyclopedia_card_id": "berlin_hauptbahnhof"
  }
}
```

---

## 5. 城市百科卡(文化融入)

### 5.1 类别

每个城市 5-10 张百科卡,分布在 5 个类别:

| 类别 | 内容 | 示例(柏林) |
|------|------|------------|
| **Kultur 文化** | 历史、艺术、名人 | 柏林墙历史、博物馆岛、爱因斯坦 |
| **Wirtschaft 经济** | 产业、公司、就业 | 柏林初创公司、奔驰/宝马工厂、德国经济 |
| **Essen 饮食** | 当地食物、餐厅、习惯 | 咖喱香肠(Currywurst)、柏林白啤酒 |
| **Tourismus 旅游** | 景点、行程、季节 | 勃兰登堡门、博物馆岛、国会大厦 |
| **Bildung 教育** | 大学、留学、奖学金 | 柏林自由大学、洪堡大学、DAAD 奖学金 |

### 5.2 模板

```yaml
encyclopedia_card:
  id: "berlin_hauptbahnhof"
  city: "Berlin"
  category: "Tourismus"
  title: "柏林中央火车站"
  icon: "🚉"
  image: "encyclopedia/berlin_hauptbahnhof.png"
  
  content:
    sections:
      - heading: "概览"
        text: |
          柏林中央火车站(Berlin Hauptbahnhof)于 2006 年开放,
          是欧洲最大的十字交叉式车站,日均客流量 30 万人次。
          铁路东西方向(巴黎-莫斯科)和南北方向(哥本哈根-米兰)在此交汇。
        keywords:
          - word: "der Hauptbahnhof"
            translation: {"zh": "中央火车站"}
            
      - heading: "从机场怎么去"
        text: |
          从 BER 机场可乘 FEX 快车直达 Hauptbahnhof,约 30 分钟,€4.40。
          或乘 S9 / S45 慢车,约 45 分钟。
        keywords:
          - word: "der Flughafen"
            translation: {"zh": "机场"}
          - word: "der Zug"
            translation: {"zh": "火车"}
            
      - heading: "周边景点"
        text: |
          - 联邦政府区(Regierungsviertel):步行 10 分钟
          - 勃兰登堡门(Brandenburger Tor):步行 15 分钟
          - 菩提树下大街(Unter den Linden):步行 10 分钟
          
  related_scenarios:
    - "berlin_bahnhof_01"
    
  references:
    - "https://www.bahn.de/..."
    - "https://www.visitberlin.de/..."
```

### 5.3 LLM 辅助生成

**Prompt 模板**:
```
请帮我为德国[城市名]写一张百科卡。

主题:[主题]
类别:[Kultur/Wirtschaft/Essen/Tourismus/Bildung]
目标读者:准备去德国留学的中国学生

要求:
1. 200-300 字,简洁易懂
2. 包含 3-5 个德语新词(标注阳性/阴性/中性)
3. 提供中文翻译
4. 适合初学者(避免生僻表达)
5. 准确(德国当地人视角)

格式:Markdown
```

**你审校**: 生成的初稿可能有不准确的地方,需要你(中文母语+德国相关知识)审校,这是**质量保证的关键**。

---

## 6. 角色与 NPC 设计

### 6.1 NPC 池设计

| NPC | 角色 | 常驻城市 | 性格 | 语速 |
|-----|------|---------|------|------|
| Anna | Kellnerin | Berlin | freundlich, geduldig | 慢 |
| Peter | Info-Mitarbeiter | Berlin | hilfsbereit, ruhig | 慢 |
| Lisa | Verkäuferin | Berlin | schnell, professionell | 中 |
| Dr. Schmidt | Arzt | Berlin | ernst, präzise | 中 |
| Klaus | Bäcker | München | traditionell, herzlich | 中 |
| Maria | Bedienung im Hofbräuhaus | München | locker, lustig | 中 |
| Hans | Fischer | Hamburg | wortkarg, direkt | 慢(方言) |
| Sabine | Bibliothekarin | Hamburg | gebildet, hilfsbereit | 中 |

**设计原则**:
- 同一城市 NPC 性格多样(覆盖不同对话风格)
- 北部/南部 NPC 有方言色彩(汉莎/巴伐利亚)
- 主要 NPC 在多关卡出现(玩家熟悉感)

### 6.2 NPC 立绘 × 表情

每个 NPC 至少 4 个表情:neutral / smile / surprise / thinking

**MVP 第 1 关 NPC Peter**: 4 张立绘
**Phase 1 完整 (5 个 NPC × 4 表情 = 20 张)**

---

## 7. 内容创作工作流

### 7.1 角色分工(单人项目)

| 内容类型 | 工作量 | 工具 |
|---------|--------|------|
| 城市选择 + 解锁顺序 | 1 次性 | 文档 |
| 城市百科 | 5-10 卡/城市,每卡 1-2 小时 | LLM 生成 + 审校 |
| 关卡剧本 | 1 关 4-8 小时 | 手工 + LLM 辅助 |
| NPC 设定 | 一次性,1-2 小时/NPC | 文档 |
| TTS 音频 | 1 句 1 分钟(用 LLM + CosyVoice) | 阿里云 API |

**单人工作量估算**:
- 1 城市 5 关 + 5 张百科卡: 60-80 小时(2-3 周)
- 3 城市 15 关 + 15 张百科卡: 180-240 小时(2-3 个月)

### 7.2 LLM 辅助剧本生成

**辅助场景**:
- 城市百科卡初稿
- NPC 角色设定
- 对话变体(同一场景多种表达方式)
- 反馈卡文案模板

**不辅助**:
- 关卡核心结构(教学设计)
- 学习点选择
- 文化准确性

### 7.3 审校清单

每张剧本/百科卡发布前审校:

- [ ] 德语语法正确
- [ ] 表达自然(母语者能接受)
- [ ] 文化准确(非刻板印象)
- [ ] 难度匹配标注的 CEFR 等级
- [ ] 关键表达都标注了 gender(der/die/das)
- [ ] 中文翻译自然
- [ ] 没有不合适的政治内容

**专业审校**: 强烈建议找德语专业朋友(或母语者)做最终审校,自己看 10 遍也会漏。

---

## 8. 内容更新策略

### Phase 1: 集中创作
- 一次性写完柏林 5 关
- 写完再上线,避免边写边改

### Phase 2+: 持续更新
- 每 2 周发布 1 个新关卡
- 每月更新 1-2 张百科卡
- 节假日专题(慕尼黑啤酒节、科隆狂欢节、圣诞市场)

### 内容版本管理
- Git 管理所有 JSON
- Tag 标记内容版本
- 后端按版本加载

---

## 9. 内容质量 vs 数量的平衡

**核心原则**:**5 个高质量关卡 > 20 个粗制滥造关卡**

每关必须有:
- 真实场景(不是"为练语法而练")
- 自然对话(不是"填空题对话")
- 文化信息(让玩家有获得感)
- 难度曲线合理(上一关到下一关有递进)

宁可少做,也要做好。

---

## 10. 7-3-1 内容法则(每关)

**7 个核心**(必须):
1. 明确场景(在哪、和谁)
2. 1 个核心任务(玩家要做什么)
3. 5-10 个目标表达
4. 1-2 个语法点
5. 4-6 轮对话
6. 每个表达点有"对/错"判定逻辑
7. 反馈卡文案

**3 个锦上添花**(可选):
- 干扰项(背景对话、其他顾客)
- 文化点(德国习惯、风俗)
- 表情 / 情绪变化

**1 个文化彩蛋**(必备):
- 1 个让玩家"哦原来德国是这样"的瞬间
- 例:柏林咖啡馆内一张照片——1961 年柏林墙建起的同一天

---

OK,剧本化方法到这里。等你确认这个框架后,我会写出**柏林完整 5 关**的 JSON 剧本(预计 30-50KB),作为 Phase 1 的内容交付物。
