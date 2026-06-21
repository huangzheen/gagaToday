# 游戏设计: Auf nach Deutschland! (走向德国!)

> **版本**: v2.0 (2026-06-21)
> **状态**: 设计草稿,等待用户 review
> **核心改变**:
> - v1.0 (2026-06-21 早上): 主角是 15-16 岁中考毕业生,三轨并行学习(德语 + A-levels + 雅思),RPG 沉浸式探索
> - v2.0 (2026-06-21 中午): **真实地图 + 模拟真实一天循环 + 多 POI 探索 + 跨城旅行 + 真实生活费系统**

---

## 1. 一句话定位

**一个 15-16 岁中国中考毕业生,只身到德国读国际高中,同时学德语 + 考英国 A-levels + 考雅思,通过 RPG 探索走遍德国。**

不是"刷题 app",**是 RPG**——沉浸式、有社交、有生活压力、有剧情分支。

---

## 2. 主角档案

| 属性 | 值 | 说明 |
|------|------|------|
| 姓名 | Lena(默认,可改) | 主角 |
| 年龄 | 15-16 岁 | 中考刚结束 |
| 母语 | 普通话 | 中文对话与 NPC 永远可用 |
| **德语** | A0 零基础 | 起点,游戏推进 |
| **英语** | A2-B1(中考水平) | 起点,IELTS 5.0-5.5 |
| 学科(数学/科学/语文) | 初三毕业 | 起点 |
| 性格设定 | 紧张但好奇,想交朋友 | 通过开局对话呈现 |
| 家庭 | 普通中产 | 父母支持留学 |
| 资金 | 父母汇款 + 打工 | 学生签证限制 120 天/年 |

**3 年游戏时长**:Year 12 (A-levels Year 1) + Year 13 (A-levels Year 2) + 中间暑假
**真实时间**: 玩家决策 1 个游戏日 = 现实 5-10 分钟(可加速)

---

## 3. 三轨并行学习系统(核心)

### 3.1 德语轨 (German Track) — 游戏内探索
- **目标**: A0 → C1(欧洲语言标准)
- **场景**: 走遍德国地图,每个城市/地点解锁对话关卡
- **关卡类型**: 点单、问路、买东西、办手续、看病、社交、聊天
- **难度梯度**: A1(咖啡馆) → A2(餐厅) → B1(办公室) → B2(医院/政府)
- **能力展示**: 主角的"德语能力 stat"影响 NPC 反应(发音评分 Qwen2-Audio + 流利度)
- **奖励**: 解锁新地点 + 获得新 NPC 好感度 + 文化百科卡片(Kultur/Wirtschaft/Essen/Tourismus/Bildung)

### 3.2 A-levels 轨 (A-levels Track) — 学校子系统
- **目标**: 选 3-4 门课,A*-B(英国大学入学门槛)
- **教学语言**: **全英文**
- **选课**: Year 12 选 3-4 门(数学常必修 + 自选 2-3 门)
  - 数学(Mathematics) / 进阶数学(Further Maths) / 物理 / 化学 / 生物 / 经济 / 文学 / 历史 / 地理 / 计算机 / 心理学 / 艺术设计 / 德语(对,德国读 A-levels 可以选 A-level 德语!相当于 A2-B1 即可,练德语双赢)
- **课堂 minigame**: 解题(数学) / 实验模拟(物理化学) / essay draft(文学) / 图表分析(经济)
- **考试**: 每月 mock,期末 mock,5-6 月正式 A-levels(可分两年考)
- **AI tutor**: Qwen-Plus 当辅导员,英文对话(Ask anything 模式)

### 3.3 雅思轨 (IELTS Track) — 考试系统
- **目标**: 5.0 → 7.0+(英国 G5 入学门槛 7.0+,G5 以下 6.5)
- **考试频率**: 每月一次 mock(可参加或不参加,每次 ¥200 报名费)
- **4 section**: 听力 + 阅读 + 写作 + 口语
- **听力/阅读**: 游戏内置(可加速或正常)
- **写作**: AI 评分(Qwen-Plus,按雅思 rubric)
- **口语**: AI 评分(Qwen2-Audio,发音 + 流利度 + 内容)

### 三轨之间的关系
- **独立**: 三个进度条各自独立,可单独练
- **互相影响**: 
  - 德语学得好 → 在德国社交解锁更多支线 → 心情 +10%
  - A-levels 考好 → 心情 + → 打工可做更高端的家教(时薪高)
  - 雅思分数高 → 解锁"英国大学申请线"结局
- **时间竞争**: 每天 24 小时有限,要平衡(优先级选择)

---

## 4. 双语切换机制(关键设计)

### 4.1 不是 UI 切换,是 NPC 偏好 + 玩家选择

**核心机制**: 每个 NPC 有一个 `lang_pref` 属性(德语概率 + 英文可用度),玩家在对话开始时可选"用德语"或"用英语"。

```
[NPC metadata]
name: Anna Kellnerin
age: 42
location_type: cafe  # 决定 lang_pref 基础值
personality: patient, helps beginners
lang_pref:
  de: 0.7  # 70% 概率开场德语
  en: 0.3  # 30% 概率开场英文
can_speak_english: true  # 能否切换
english_proficiency: B2
```

### 4.2 场景类型的语言分布

| 场景类型 | 德语默认 | 英文可用度 | 例子 | 难度 |
|---------|---------|-----------|------|------|
| 国际大都市景点/车站 | 70% | 100% | Berlin Hbf, München tourist info | ⭐ |
| 大学城/国际公司 | 80% | 90% | Heidelberg university | ⭐ |
| 大城市餐厅/商店 | 90% | 50% | Berlin Mitte café | ⭐⭐ |
| 中型城市小餐厅 | 95% | 30% | Dresden Bäckerei | ⭐⭐ |
| 德国农村酒馆 | 100% | **0%** | Rothenburg Gasthof | ⭐⭐⭐ |
| 学校教室 | 90%(德语课) | 100%(A-levels 课) | Deutsch 文法 / A-levels Math | ⭐ |
| 政府/医院 | 100% | **0%**(硬性) | Ausländerbehörde | ⭐⭐⭐ |
| 私人家庭 | 100% | 0%(老一代) | 寄宿家庭 Oma | ⭐⭐⭐ |

### 4.3 玩家策略影响

- **英文通关**: 玩家可一直用英文,绕过德语关卡——但损失:
  - 减少德语 XP 50%
  - 部分剧情(NPC 个人故事)被跳过
  - 解锁成就 "Tourist" 而非 "Immigrant"
- **德语尝试**: 玩家用德语对话:
  - 即使发音烂,NPC 会耐心纠正
  - 错的单词变成"可学习错题本"
  - 成功后大幅德语 XP + NPC 好感度
- **混合策略**: 大城市用德语(练),农村用德语(必须),A-levels 用英文(必须)

### 4.4 教学反馈循环

```
玩家录音德语
    ↓
Fun-ASR 1.5 → 转写文本
    ↓
Qwen-Plus → 判断:语法 + 词汇 + 语义
    ↓
Qwen2-Audio → 评分:发音 + 流利度
    ↓
合并反馈 → NPC 反应(文本 + 表情)
    ↓
玩家修正 → 重试 / 继续
```

---

## 5. 走遍德国地图子系统

### 5.1 主地图(德国 + 德语区)

```
德国 16 州,精选 12 个有代表性的城市:

北部: Hamburg, Bremen, Kiel
东部: Berlin, Dresden, Leipzig
中部: Hannover, Göttingen, Frankfurt
南部: München, Heidelberg, Freiburg
西部: Köln, Düsseldorf, Aachen
邻国德语区(可选): Wien(奥地利), Salzburg, Zürich, Luzern(瑞士)
```

每个城市:
- **5-10 个场景点**: 餐厅、咖啡馆、火车站、景点、博物馆、书店、商店、朋友家
- **难度等级**: 城市整体 A1/C1 评级
- **英文可用度**: 0-100% 城市基线
- **特殊 NPC**: 1-2 个常驻 NPC(每个 NPC 有完整 backstory)

### 5.2 场景点详情

每个场景点是一段对话剧本(JSON 定义):
```json
{
  "id": "berlin_cafe_einstein_order",
  "city": "berlin",
  "type": "cafe",
  "difficulty": "A1",
  "npc": "anna_kellnerin",
  "lang_pref": { "de": 0.7, "en": 0.3 },
  "learning_objectives": [
    "问候 (Guten Tag, Hallo)",
    "点单 (Ich möchte..., Haben Sie...?)",
    "数字 (zwei Kaffee, bitte)"
  ],
  "script": [
    { "turn": 1, "npc_de": "Hallo! Was darf's sein?", "npc_en": "Hello! What can I get you?" },
    ...
  ],
  "feedback": {
    "de_vocab": ["Hallo", "Kaffee", "bitte", "danke"],
    "de_grammar": ["möchte + Akkusativ"],
    "culture_card": "Kaffee und Kuchen"
  }
}
```

### 5.3 文化百科卡片(特色功能)

每完成一个场景点,解锁一张文化卡片(可在大地图上收集展示):
- **Kultur**: 德国节日/习俗/历史
- **Wirtschaft**: 经济/品牌/产业
- **Essen**: 食物/餐厅/超市
- **Tourismus**: 景点/旅行/铁路
- **Bildung**: 学校/考试/学制

例:Kaffee und Kuchen(咖啡与蛋糕)—— 15:00 德国人吃蛋糕习俗,Einstein Café 起源,推荐搭配 Schwarzwälder Kirsch。

---

## 6. 学校子系统(v1.0 概要,详见 §11D v2.0 升级版)

> **v2.0 提示**: 本节是 v1.0 的概要设计。**详细升级版(课表自动生成、minigame 类型、老师/同学关系)见 §11D**。

### 6.1 概要

玩家在 Year 12 选课(数学必修 + 自选 2-3 门),系统生成周课表。每天 6-8 节课,每节课 45 分钟,触发对应 minigame。详见 §11D 详细规格。

### 6.2 选课(与 §11D.1 同步)

- **数学**: 必修
- **自选 2-3 门**: 物理、化学、生物、经济、文学、历史、地理、计算机、心理学、艺术、**A-level 德语**(独特优势!)

### 6.3 考试日历(与 §11.4 同步)

| 月份 | 事件 |
|------|------|
| 9 月 | Year 12 开始 |
| 11 月 | 第一次 mock(月考) |
| 12 月 | 圣诞假 |
| 1 月 | 圣诞假结束 |
| 3 月 | 复活节假 |
| 5-6 月 | **正式 A-levels 考试** |
| 7 月 | 出成绩 + 暑假 |

雅思 mock:每月可参加(¥200),9/11/1/3/5 真考报名

---

## 7. RPG 角色属性系统

```
主角 stats:
  德语: A0 → C1 (CEFR 6 等级)
  英语: B1 → C1 (CEFR 6 等级)
  学科: 数学 / 物理 / 化学 / 生物 / 经济 / 文学 / 历史 / 地理 (各 A*-U)
  心情: 0-100
  体力: 0-100(每日恢复)
  金钱: €0-€10000
  社交: 德国朋友数 / 国际朋友数 / NPC 好感度列表
  文化百科: 已收集卡片数 / 总数
```

心情/体力影响:
- 心情 < 30: 学习效率 -50%,易生病,触发负面事件
- 体力 < 20: 上课注意力涣散,小游game 失败率 +30%
- 金钱 < 0: 触发"向父母要钱"剧情,心情 -20

---

## 8. 生活子系统(疏漏补全)

### 8.1 住宿

3 种住宿可选(开局决定):
1. **寄宿家庭(Gastfamilie)**: €400-600/月,沉浸德语环境,有家规,可能有 Opa/Oma
2. **学生宿舍(Studentenwohnheim)**: €300-500/月,公共厨房,室友可能是各国学生
3. **合租公寓(WG)**: €350-550/月,自由度高,但可能分心

每种住宿带来不同的支线剧情。

### 8.2 打工系统

- **学生签证限制**: 120 天/年 或 20 小时/周(学期中)
- **可做工作**:
  - 餐厅服务生(练德语 + 时薪 €10)
  - 超市收银(基础德语)
  - 家教(教数学/物理/中文给德国小孩,€15-25/小时,练英语 + 用所学)
  - 图书馆(安静,边赚钱边复习)
  - 节日季节工(圣诞市场、Oktoberfest)

### 8.3 节日与文化

- **9-10 月**: Oktoberfest(慕尼黑),Erntedankfest(感恩节)
- **11 月**: Volkstrauertag, Totensonntag(静默节日)
- **12 月**: Weihnachtsmarkt(圣诞市场全德),圣诞假
- **1-2 月**: Karneval(科隆/杜塞尔多夫/美因茨)
- **3-4 月**: Easter(Ostern),复活节假
- **5-6 月**: Pfingsten(圣灵降临节),A-levels 考试
- **7-8 月**: 暑假

每个节日触发特殊剧情或文化卡片。

### 8.4 健康与心理

- **生病**: 看医生(必须德语/或英语医生)
- **心理支持**: 学校心理咨询师(免费,英文),可倾诉思乡/压力
- **健康保险**: 法定/私立(影响看病体验)

### 8.5 交通

- **Deutschlandticket**: €49/月 2026,全国公交/地铁/区域火车
- **DB 火车**: 城际 IC/ICE,Schüler-Ticket 半价
- **自行车**: 德国人必备,城市间骑车
- **预算消耗**: 交通占生活费的 10-15%

---

## 9. 社交与人际关系

### 9.1 NPC 系统

每个城市有 5-15 个有名有姓的 NPC:
- 完整 backstory(家庭、职业、爱好)
- 好感度 0-100
- 关系类型: 邻居、同学、老师、同事、朋友、恋人

例:
- **Anna Kellnerin**(柏林 Café Einstein 服务员): 42 岁,单身,爱音乐
- **Peter**(柏林 Hauptbahnhof 问询处): 50 岁,退休工程师,爱火车模型
- **Hans Müller**(海德堡房东): 60 岁,教授,爱古典音乐
- **Lena Becker**(德国同班同学): 16 岁,学生会主席
- **Tom Williams**(英国室友): 16 岁,足球迷
- **Yuki Tanaka**(日本交换生): 16 岁,动漫宅

### 9.2 好感度效果

- 高好感度 → 触发专属剧情 + 解锁支线任务 + 文化卡片
- 低好感度 → NPC 冷淡 / 拒绝帮忙 / 触发冲突
- 关系冲突: 德国同学 vs 国际生 / 朋友 vs 学习 / 父母期望 vs 自己兴趣

### 9.3 派对与社交事件

- 生日派对(德国 16 岁可喝酒)
- 周末酒吧(Kneipe)
- 学校舞会(Abiball)
- 节日聚会(圣诞、Karneval)
- 派对选择影响: 健康(酒)、心情(社交)、学业(翘课)

---

## 10. 结局多线(RPG 核心)

### 10.1 学术结局(基于 A-levels + 雅思 + 德语成绩)

| 结局 | 条件 | 场景 |
|------|------|------|
| **英国 G5** | A-levels 3A*, IELTS 7.5, 德语 B2 | 收到 Oxbridge / IC / UCL / LSE / Edinburgh offer |
| **英国 Top 20** | A-levels AAB, IELTS 7.0 | 收到 Manchester / Warwick / Bristol 等 |
| **德国 TU9** | A-levels ABB + Abitur + 德语 C1 | 收到 TUM / RWTH / TU Berlin offer |
| **混合:英德本科** | 雅思 7.0 + 德语 B2 + A-levels AAB | 在英国读本科 + 在德国交换 |
| **回国** | 任何成绩但主动选择回国 | 高考 / 国内大学 / 创业 |

### 10.2 社交结局

- **朋友圈结局**: 5+ 德国好朋友 + 文化适应良好
- **恋人结局**: 与某 NPC 确定关系(德国同学 / 寄宿家庭子女 / 同事)
- **孤独结局**: 朋友少,思乡重,回国

### 10.3 心理结局

- **自信成长**: 心情均值 70+, 独立自主
- **坚持不放弃**: 即使压力,完成 3 年
- **退学重读**: 失败 → 选择重新开始

### 10.4 隐藏结局

- **隐藏学霸**: 3A* + 德语 C1 + 雅思 8.0 + 5 张文化卡片(满分)
- **隐藏创业者**: 打工攒钱 → 暑假创业 → 拿到投资
- **隐藏政治家**: 加入学生会 → 模拟议会 → 成为学生主席

---

## 11. 游戏循环(完整日 / 周 / 月 / 年)

> **v2.0 重大升级**: 从"事件流"升级到**模拟真实一天**。每天从起床开始,主角需要做早餐、通勤、上课、午餐、下午课、放学探索、晚餐、学习/社交/打工、睡觉。

### 11.1 每日循环 (Daily Loop) — 详细时间表

```
06:30  ⏰ 起床 (闹钟 + 心情 + 体力)
        ├─ 闹钟响了!按掉 / 再睡5min(体力 +5,但赶不上早餐)
        └─ 自然醒(体力满)
        
07:00  🍳 早餐决策 (3 选 1)
        ├─ 🏠 在家做饭 (€3,体力 +15,时间 30min,省钱)
        │   └─ 需要:冰箱有食材(周末超市买过)、厨房设备
        ├─ 🍞 Bäckerei 买 (€4-6,体力 +20,时间 15min)
        │   └─ 德语对话 A1:NPC Bäcker
        │   └─ 练习:Hallo / Brötchen / bitte / danke / 数字
        └─ ⏭️ 跳过早餐 (省钱,但体力 -20,下午困)
        
07:30  🚇 通勤决策 (3 选 1)
        ├─ 🚶 步行去学校 (免费,15-30min,体力 -5)
        ├─ 🚌 U-Bahn / Bus (Deutschlandticket €49/月包月,10min,体力 -2)
        └─ 🚲 自行车 (一次性 €50-200 购买,8min,体力 -3,自由穿行)
        
08:00-12:30  🏫 上午 4 节课 (按周课表自动进入教室)
        ├─ 节课 1 (08:00-08:45) → 教室场景 → minigame
        ├─ 节课 2 (09:00-09:45)
        ├─ 小休 09:45-10:00 (休息,可社交)
        ├─ 节课 3 (10:00-10:45)
        ├─ 节课 4 (11:00-11:45)
        └─ 大课间 11:45-12:30 (社交 / 校园活动)
        
12:30  🍽️ 午餐决策 (3 选 1)
        ├─ 🏫 Mensa 食堂 (€4-6,与同学社交机会)
        ├─ 🥪 自带便当 (在家做的,€0,但社交少)
        └─ 🍕 校外餐厅 (€8-15,练德语点单)
        
13:30-16:00  📚 下午 3 节课(周三下午无课 → 自由活动日)
        ├─ 节课 5/6/7 (45min × 3)
        └─ 周三:自由活动(可打工/探索/学习)
        
16:00  🏙️ 放学后探索 (核心自由时间!)
        ├─ 🛒 超市 REWE (€20-50/周,买菜日用品,练德语)
        ├─ 🏛️ 博物馆 (€0-12,文化百科,讲解员可能英文)
        ├─ 📖 图书馆 (免费,自习 / 借书 / 学习小组)
        ├─ 🍺 同学聚会 Kneipe (心情 +,亲和度 +,€10-20)
        ├─ 💼 打工 (餐厅/超市/家教,€10-25/h)
        ├─ 🌳 公园 / 教堂 (休息 / 文化活动)
        ├─ 🛍️ 商店 / Kaufhaus (买衣服/电子产品)
        ├─ 🏠 直接回家 (省钱,体力恢复)
        └─ 🎂 同学生日 / 派对(随机事件)
        
18:00  🍴 晚餐决策 (3 选 1,类似午餐)
        ├─ 🏠 寄宿家庭提供 (€0,包含在寄宿费,与 Gastfamilie 社交)
        ├─ 🍳 自己做 (€3,需要食材)
        └─ 🍕 餐厅 (€8-15)
        
19:00-22:00  🌙 晚间时间 (3 选 1 / 复合)
        ├─ 📖 学习 / 写作业 (A-levels 复习 / 雅思备考 / 德语练习)
        ├─ 💬 社交 (微信/电话家人 / 与朋友聊天)
        ├─ 🚶 城市夜景探索 (夜市 / 圣诞市场)
        └─ 😴 早睡(体力提前恢复)
        
22:00  😴 睡觉 → 第二天
        └─ 月末结算(详细见 §11.4)
```

### 11.2 每周循环 (Weekly Loop)
- **周一-周五**: 学校(课表固定)
- **周三下午**: 自由活动日(无课,关键探索窗口)
- **周六**: 大块时间(旅游/打工/休息/超市采购)
- **周日**: 复习/休息/做饭(寄宿家庭文化时间)

### 11.3 每月循环 (Monthly Loop)
- 雅思 mock(可选,¥200)
- A-levels 月考
- 工资 + 房租扣款
- 心情波动 + 心理支持
- 月末结算(详细见 §11.4)

### 11.4 每年循环 (Yearly Loop)
- 9 月: 新学年(选课)
- 10 月: Halloween(德国部分校园)
- 11 月: Volkstrauertag, Sankt Martin
- 12 月: Weihnachtsmarkt + 圣诞假(2 周)
- 1 月: 新年 + 圣诞假结束
- 2 月: Karneval(科隆/杜塞尔多夫)
- 3 月: 复活节假(2 周)
- 5-6 月: 正式 A-levels 考试 + Pfingsten
- 7-8 月: 暑假(旅游/打工/家庭)

---

## 11A. 真实地图系统(v2.0 新增)

> **取代 v1.0 的"3 个场景卡片"**。现在主角在 2D 城市地图上 WASD 自由移动,地图上散布各种 POI 触发交互。

### 11A.1 地图层级结构

```
游戏世界
├── 德国总览地图(宏观)
│   ├── 12 个城市节点(柏林/汉堡/慕尼黑/...)
│   └── 邻国德语区(维也纳/苏黎世/...)
│
├── 城市地图(中观) ← 玩家主要活动区域
│   ├── 柏林 Mitte / Kreuzberg / Charlottenburg / ...
│   ├── 各区域:学校区 / 商业区 / 住宅区 / 文化区
│   └── 城市间通过 Bahnhof / Flughafen 跳转
│
└── POI 内部场景(微观) ← 触发后进入对话
    ├── 建筑外观(像素 sprite)
    └── 内部场景(对话 / minigame / 商店列表)
```

### 11A.2 柏林 Mitte 城市地图布局示例

```
柏林 Mitte 城市地图(2D 俯视 RPG Maker / Stardew Valley 风格)
分辨率: 32×24 tile × 16px = 512×384,可扩展

  ┌─────────────────────────────────────────────────┐
  │ ☰学校(International School)                    │
  │                                                  │
  │  📖图书馆          🏛️博物馆                      │
  │                                                  │
  │       🛒 REWE超市     🍞 Bäckerei              │
  │                                                  │
  │       🚇 U-Bahn站     🍽️ Mensa食堂             │
  │                                                  │
  │  🌳公园             🏠 Gastfamilie(家)←起点   │
  │                                                  │
  │  ⛪教堂             🏪 Kaufhaus                │
  │                                                  │
  │  🍺 Kneipe酒馆      🎬 Kino电影院              │
  └─────────────────────────────────────────────────┘

每个 POI:
- 占据 1-2 个 tile,玩家走到附近自动弹出"进入"按钮
- 进入后切换到该 POI 的内部场景(对话 / 商店 / minigame)
- 离开后回到城市地图同一位置
```

### 11A.3 POI 类型清单(完整覆盖日常)

| 类型 | 德文名 | 难度 | NPC | 玩法 | 频率 |
|------|--------|------|-----|------|------|
| 🏠 **家** | Gastfamilie / WG | A1-A2 | 寄宿家庭 / 室友 | 做饭 / 睡觉 / 私人对话 | 每天 |
| ☰ **学校** | Internationale Schule | A2-C1 | 老师 / 同学 | 上 8 节课(minigame) | 每天 8h |
| 🍞 **Bäckerei** | Bäckerei | A1 | Bäcker | 买早餐 / 数字 / 问候 | 每天(可选) |
| 🛒 **超市** | REWE / EDEKA / Lidl / Aldi | A1-A2 | 收银员 / 店员 | 买菜日用品 / 找零 | 1-3 次/周 |
| 🏛️ **博物馆** | Deutsches Museum / DDR Museum | B1-B2 | 讲解员(常英文) | 文化百科 / 历史 | 1-2 次/月 |
| 📖 **图书馆** | Bibliothek / Stadtbibliothek | A2 | 图书管理员 | 自习 / 借书 / 学习小组 | 经常 |
| 🚇 **U-Bahn / S-Bahn** | U-Bahnhof | A1 | 售票员 / 工作人员 | 通勤 / 跨城 | 每天(通勤) |
| 🍽️ **Mensa 食堂** | Mensa | A1-A2 | 食堂阿姨 + 同学 | 午餐 / 数字 / 排队 | 每天 |
| 🌳 **公园** | Park / Volkspark | A1-A2 | 路人 / 老人 | 散步 / 社交 / 慢跑 | 偶尔 |
| ⛪ **教堂** | Kirche / Dom | B1+ | 牧师 / 志愿者 | 文化活动 / 圣诞市集 / 静思 | 节日多 |
| 🍺 **Kneipe / 酒吧** | Kneipe | A2-B1 | 酒保 / 客人 | 社交 / 16 岁可饮啤酒/葡萄酒 | 周末 |
| 🛍️ **商店** | Kaufhaus / Thalia 书店 | A1-A2 | 店员 | 买衣服/电子产品/书 | 偶尔 |
| 🎬 **电影院** | Kino | A2-B1 | 售票员 | 看电影练听力(英/德字幕) | 偶尔 |
| 🏥 **医院** | Krankenhaus / Arztpraxis | B1+ | 医生 / 护士 | 看病(必须德语为主) | 生病时 |
| 🏛️ **政府** | Ausländerbehörde | B2 | 官员 | 办签证/居留(必须德语) | 偶尔 |
| 🏦 **银行** | Bank / Sparkasse | A2 | 职员 | 开户 / 存款 / 转账 | 偶尔 |
| 📮 **邮局** | Post / DHL | A1 | 职员 | 寄包裹 / 取件 | 偶尔 |
| 🎓 **大学开放日** | Universität | B2 | 教授 / 学生 | 探索未来大学 | Year 13 |

### 11A.4 POI 互动流程

```
玩家主角 sprite 走到 POI 触发区(tile-based)
    ↓
弹出"按 E 进入 [Bäckerei]"
    ↓
玩家按 E(或鼠标点击)
    ↓
切换到 POI 内部场景(对话框 / 商店界面 / minigame)
    ↓
完成对话/购买/minigame
    ↓
返回城市地图(玩家位置不变)
    ↓
NPC 好感度更新 + 文化卡片可能解锁 + 经验值 + 金钱变动
```

### 11A.5 真实地图实现技术

- **编辑器**: Tiled Map Editor(开源)或手画 PNG 切块
- **引擎**: Phaser TileMap API + Matter.js(碰撞)
- **图层**:
  - 底层:地面 tile(草/路/水/建筑墙)
  - 中层:装饰物(树/长椅/路灯)
  - 顶层:碰撞区 + POI 触发区
- **角色**: 主角 Lena sprite 4 朝向 × 4 表情 = 16 frame
- **状态**: 站立 / 走路(每方向 2-3 frame 循环)

---

## 11B. 真实生活费系统(v2.0 新增)

### 11B.1 月度收支表(寄宿家庭基准)

| 支出项目 | 月金额 | 说明 |
|---------|--------|------|
| 寄宿费(含早晚餐) | €500 | Gastfamilie 包早晚餐 |
| 午餐 + 零食 | €200 | Mensa €4-6/天 × 22 天 ≈ €100 + 零食/偶尔外卖 €100 |
| 交通 Deutschlandticket | €49 | 全国公交包月(2026 标准) |
| 文具 / 书籍 | €30 | A-levels 教材 / 文具 |
| 手机 + 网络 | €25 | 德国学生套餐 |
| 娱乐 / 社交 | €50 | Kneipe / Kino / 偶尔外出 |
| 杂项 | €50 | 衣服 / 日用品补充 |
| **总支出** | **~€900/月** | |

| 收入项目 | 月金额 | 说明 |
|---------|--------|------|
| 父母汇款 | €800-1000 | 默认 €900 |
| 打工(餐厅/超市/家教) | €200-500 | 学生签证 120 天/年限制 |
| 奖学金(可选) | €0-300 | 视申请情况 |
| **总收入** | **~€1000-1800/月** | |

### 11B.2 消费决策影响

| 决策 | 影响 |
|------|------|
| 省钱(都自己做 + 走路) | 月盈余 €200+,但心情 -10(社交少)/ 文化卡片少 |
| 平衡(混合) | 月盈余 €50-100,心情 OK |
| 体验型(常聚会/旅游) | 月亏空 €50-200,触发"向父母要钱"剧情 |
| 极端消费(奢侈品) | 严重亏空,父母失望 + 心情大降 |

### 11B.3 月末结算

```
每月 1 号 00:00 自动结算:
  父母汇款 → bank_balance += €900
  寄宿费 → bank_balance -= €500
  其他自动扣款 → 略
  月末余额 = bank_balance
  
触发剧情:
  - bank_balance < €100 → "向父母要钱" 剧情
  - bank_balance < €0 → 触发"严重警告" + 强制打工
  - bank_balance > €2000 → 解锁"买自行车/电脑" 选项
  - 连续 3 月盈余 > €500 → 解锁"暑假欧洲游" 选项
```

### 11B.4 关键消费触发器

| 触发事件 | 金额 | 备注 |
|---------|------|------|
| 买自行车 | €50-200 | 一次性,加速通勤 |
| 买电脑(笔电) | €400-800 | A-levels 学习用 |
| 周末短途旅行 | €50-150 | 火车票 + 餐饮 |
| 假期长途旅行 | €300-1000 | 火车/飞机 + 住宿 |
| 同学生日礼物 | €10-30 | 社交维系 |
| 节日礼物(父母) | €20-50 | 维系亲情 |
| 雅思考费 | ¥2000 ≈ €260 | 每次真考报名 |
| A-levels 真考费 | £100+ / 科 | 每年多次 |
| 节日活动(Weihnachtsmarkt) | €20-50/次 | Glühwein + 礼物 |

---

## 11C. 跨城旅行(v2.0 新增)

### 11C.1 三种规模

```
1. 周末短途(1 天往返)
   范围: 柏林 ↔ 德累斯顿 / 汉堡 / 汉诺威(2-3 小时火车)
   费用: €20-40 单程
   玩法: 早出晚归,1-2 个 POI 深度

2. 周末长途(2 天 1 晚)
   范围: 柏林 ↔ 慕尼黑 / 海德堡 / 科隆(4-6 小时火车)
   费用: €40-100 单程 + 旅馆 €30-80
   玩法: 2 天探索多个 POI + 住 1 晚

3. 假期长途(5-14 天)
   范围: 圣诞 / 复活节 / 暑假 → 任意城市 / 国家
   费用: €500-1500(火车/飞机 + 住宿 + 餐饮)
   玩法: 沉浸式多城市探索 + 文化百科密集解锁
```

### 11C.2 跨城流程

```
游戏内 Bahnhof 站
    ↓
玩家点 "Reisen" (旅行)
    ↓
UI: 选择目的地 + 出发日期 + 票种(Sparpreis / Flexpreis)
    ↓
德语对话: "Guten Tag, ich möchte nach München fahren. Wann fährt der nächste Zug?"
    ↓
买票(扣 €)
    ↓
切换到 Zug 场景(火车 mini-scene)
    ├─ 车厢对话(可选:与邻座 NPC 闲聊)
    ├─ 看风景(过场动画,各城市缩略图)
    └─ 看手机/写作业/睡觉(时间快进)
    ↓
到达新城市 → 加载新城市地图
    ↓
探索 POI + 解锁 NPC + 文化卡片
    ↓
返程(或住几晚 → 多日结算)
```

### 11C.3 跨城文化百科奖励

每到达一个新城市,解锁 3-5 张文化卡片:

| 城市 | 文化卡片示例 |
|------|------------|
| 柏林 | Berliner Mauer 历史 / Currywurst 来源 / S-Bahn 系统 |
| 慕尼黑 | Oktoberfest 起源 / Bayern dialect / Hofbräuhaus |
| 海德堡 | 德国最老大学 / 城堡历史 / 学生监狱 |
| 汉堡 | Hafen 港口 / Reeperbahn 红灯区 / 鱼市 |
| 科隆 | Kölner Dom / Karneval / Eau de Cologne |
| 德累斯顿 | Zwinger 宫殿 / Frauenkirche / 易北河畔 |
| 维也纳(奥) | Kaffeehaus 文化 / 圆舞曲 / 西班牙骑术学校 |
| 苏黎世(瑞) | Swiss German / 银行保密 / Bahnhofstrasse |

---

## 11D. 学校子系统详细(v2.0 升级)

### 11D.1 课表系统(动态生成)

玩家在 Year 12 选课(数学必修 + 自选 2-3 门),系统自动生成周课表:

```
示例课表(Lena 选了 Math / Physics / Chemistry):

  | 时间       | 周一   | 周二   | 周三   | 周四   | 周五   |
  |------------|--------|--------|--------|--------|--------|
  | 08:00-08:45 | Math  | Physics | Chem  | Math  | Phys  |
  | 09:00-09:45 | Engl  | Math   | Math  | Chem  | Math  |
  | 09:45-10:00 | Pause | Pause  | Pause | Pause | Pause |
  | 10:00-10:45 | Deut  | Chem   | Free  | Deut  | Chem  |
  | 11:00-11:45 | Phys  | Engl   | Free  | Engl  | Phys  |
  | 11:45-12:30 | Lunch | Lunch  | Lunch | Lunch | Lunch |
  | 13:30-14:15 | Lit   | Tutor  | Sport | Lit   | Sport |
  | 14:30-15:15 | Hist  | Lab    | Sport | Hist  | Lab  |
  | 15:30-16:00 | Free  | Lab    | Free  | Free  | Free  |

  Pause = 小休
  Free = 自由时间
  Sport = 体育课(操场)
  Lab = 实验课(实验室)
  Tutor = 导师面谈
```

### 11D.2 教室场景(每天 8 次)

```
玩家按时间自动进入下一节课
    ↓
教室场景加载:
  ├─ 背景:教室(桌子/黑板/老师讲台)
  ├─ 老师 NPC(头图 + 名牌 Herr Müller / Frau Schmidt)
  ├─ 同学 NPC(可对话:邻座)
  └─ minigame 启动
    ↓
minigame 类型(根据学科):
  - Math: 解方程式 + 函数图像绘制
  - Physics: 滑块实验 + 公式填空
  - Chemistry: 元素配对 + 反应方程式
  - Biology: 标注细胞 + 解剖 quiz
  - Literature: Essay 写作(200 字 → 1000 字)
  - History: 时间线排序 + 事件连线
  - English: 阅读理解 + 写作
  - German: 发音 + 词汇 + 语法(全德语教学)
    ↓
完成 minigame → 知识点 +1 → 退出教室
```

### 11D.3 老师 + 同学关系

**老师**:
- 好感度 0-100(影响给分宽松度)
- 每节课后:回答问题正确 → 好感 +5,错误 → 好感 -2
- 老师角色:
  - **严厉型** (Herr Müller): 错题扣分多,讲解细
  - **温和型** (Frau Schmidt): 错题不扣分,鼓励探索
  - **实用型** (Mr. Williams): 真题导向,练题多

**同学**:
- 固定 5-8 个有名有姓的同学 NPC(德国学生 + 国际生)
- 互动方式:
  - 课间闲聊 → 好感度 +
  - 抄作业 → 知识点 -5 但省钱省时
  - 学习小组 → 双方知识点 +1
  - 派对邀请 → 心情 + 但可能熬夜影响明天
- 恋人:与某 NPC 好感度 90+ 触发告白选项

---

## 12. AI 集成(扩展)

### 12.1 AI 对话(双轨)

- **德语对话**: CosyVoice 3.5(de-DE voices) + Qwen-Plus(de prompt)
- **英语对话**: CosyVoice 3.5(en-US voices) + Qwen-Plus(en prompt)
- **NPC 实时反应**: Qwen-Plus 根据 NPC personality 生成反应
- **流式语音**: CosyVoice Realtime API 150ms 首包

### 12.2 AI 评分(多轨)

- **德语发音**: Qwen2-Audio-7B-Instruct(音频直评)
- **德语语法**: Qwen-Plus(文本评分)
- **英语发音**: 同 Qwen2-Audio
- **英语写作**: Qwen-Plus(IELTS rubric)
- **数学/科学 tutor**: Qwen-Plus(英文对话,可任意提问)

### 12.3 AI 文化百科生成

- 收集到某个城市/场景后,AI 自动生成文化卡片(德语 + 中文双语)
- 内容来源: NPC 解释 + Wikipedia 摘要 + Qwen-Plus 编辑

### 12.4 AI 心理支持

- 心情低时,NPC 心理咨询师主动出现
- 玩家可倾诉(中文/英文),AI 给建议(根据剧情进展)

---

## 13. 学习路径接口(关键)

你说"让另一个 agent 写"——我**只定义 schema/loader**,让那个 agent 输出格式直接接入:

### 13.1 统一 LearningUnit 抽象

不论德语 / A-levels / 雅思 / 文化百科,所有学习内容统一格式:

```yaml
learning_unit:
  id: alevel_math_pure_1_proofs
  subject: mathematics  # 学科分类
  track: a_levels  # 三大轨之一
  exam_board: aqa  # 或 edexcel / ocr / caie
  level: a-level  # 或 gcse / b1 / c1 / ielts 5.0 / etc
  
  meta:
    title: "Proof and Algebra"
    description: "..."
    estimated_time_minutes: 45
    difficulty: 1-5
  
  content:
    concepts:
      - name: "Mathematical proof"
        explanation: "..."
        examples: [...]
    practice_questions:
      - type: multiple_choice
        prompt: "..."
        options: [...]
        correct: "..."
        explanation: "..."
      - type: essay
        prompt: "..."
        rubric: "..."
  
  progression:
    prerequisites: []
    unlocks: ["alevel_math_pure_1_algebra"]
  
  mock_exam:
    - month: 11
      format: paper1
      duration_minutes: 120
      questions: [...]
```

### 13.2 消费方式

引擎(我们的游戏代码)消费:
- 加载 YAML/JSON → 渲染学习卡片
- 玩家答题 → 评分 → 更新 stats
- 完成单元 → 解锁下一单元 + 进度条更新

### 13.3 与另一个 agent 的协作

- 我方提供: `learning_path_schema.yaml` + `learning_path_loader.py` + 样例(德语 A1 单元)
- 对方提供: A-levels 各科 YAML + 雅思各 section YAML
- 整合测试: 加载对方文件 → 在游戏中能跑通

---

## 14. 技术栈与架构

### 14.1 前端
- **引擎**: Phaser 3(RPG 场景 + 角色移动 + 碰撞)
- **HUD**: Vue 3 overlay(状态栏 + 对话框 + 菜单)
- **样式**: TailwindCSS + DaisyUI
- **状态管理**: Pinia
- **构建**: Vite

### 14.2 后端(Phase 2)
- **API**: FastAPI(Python)
- **数据库**: SQLite(MVP) → PostgreSQL(Phase 2)
- **认证**: JWT(Phase 2 用户系统)

### 14.3 AI 服务
- **LLM**: Qwen-Plus / Qwen-Max(文本)
- **TTS**: CosyVoice 3.5 Plus(语音合成)
- **ASR**: Fun-ASR 1.5(语音识别)
- **Audio Eval**: Qwen2-Audio-7B-Instruct(发音 + 综合音频评估)

### 14.4 数据库(MVP Schema)

```sql
-- 之前已有
users, progress, errors, vocabulary, sessions

-- 新增(本设计需要)
schools: id, name, type, city, lang
selections: user_id, subject, exam_board, start_date
exam_results: id, user_id, exam_type (ielts/alevels), date, score
locations: id, city, lat, lng, lang_default, unlock_level
location_scenes: id, location_id, name, type, difficulty
npcs: id, name, age, role, location_id, lang_pref, backstory
npc_relationships: user_id, npc_id, affinity, events
inventory: user_id, item_type, item_id, quantity
currency: user_id, amount_eur, transactions
calendar_events: id, user_id, date, type, description
cultural_cards: id, category, title, content_de, content_zh, collected_by
```

---

## 15. 美术与风格

### 15.1 视觉风格
- **2D 俯视 RPG**(RPG Maker 风格 + Stardew Valley 色调)
- **主角 sprite**: 16-bit 像素,4 个表情
- **NPC**: 4-8 个不同 NPC,每个 4 表情
- **场景**: 像素艺术城市地图 + 室内场景

### 15.2 美术资产已就位
- ✅ Anna 4 表情 + Peter 4 表情(已 AI 生成)
- ✅ 柏林 3 个场景(已 AI 生成)
- ✅ UI 4 元素(已 AI 生成)
- ⏳ 主角 Lena sprite(待生成,4 表情)
- ⏳ 更多城市 + NPC + 场景(后续生成)

### 15.3 后续生成策略
- 主角 Lena 用 Anna 作参考(相似风格)
- 海德堡/慕尼黑/汉堡等场景批量生成
- 每个 NPC 第一张生成后,后续表情用 image-to-image 锁定

---

## 15A. 成就系统(v2.0 集成,设计见 `ACHIEVEMENT_SYSTEM.md`)

> **来源**: 另一个 agent 设计的完整成就系统文档,见 `/Volumes/NewDisk/GermanLearning/docs/ACHIEVEMENT_SYSTEM.md`(1226 行,~1830 个成就)。
> **集成时间**: 2026-06-21

### 15A.1 三大类总览

| 类别 | 编号 | 子类数 | 总数 | 主 XP 来源 |
|------|-----|-------|------|----------|
| **Lernen 学习** | L | 4 | ~250 | 主线(80% XP) |
| **Entdecken 探索** | E | 11 | ~1500 | 收集(20% XP) |
| **Meta 元** | M | 5 | ~80 | 习惯 |
| **Hidden 隐藏** | H | 1 | ~30 | 彩蛋 |
| **合计** | - | 21 | **~1860** | - |

### 15A.2 跟主游戏设计的映射

| 游戏元素 | 关联成就类 | 示例 |
|---------|----------|------|
| **德语学习** | L1 + E11 | A1→C2 等级 / 谚语 / 方言 |
| **雅思考试** | L2 | 4 项分项 + 总分 + 写作 task |
| **A-levels** | L3 | 21 门学科 × 4 等级 = 84 个 + 跨学科 10 个 |
| **走遍德国** | E1-E6 | 16 州 / 50 城市 / 100 景点 / 52 世遗 |
| **POI 探索** | E2 + E3 + E7 | 博物馆 / 美食 / 日常 |
| **跨城旅行** | E4 | 火车站 / 机场 / 桥梁 |
| **节日文化** | E5 | 圣诞市集 / Volksfeste / Karneval |
| **生活费系统** | E7 | 超市 / 行政 / 租房 |
| **社交关系** | M4 | 朋友 / 学习小组 / 德语对话次数 |
| **日常习惯** | M1 / M5 | 连续打卡 / 特殊事件 |
| **彩蛋** | H | 告白 / 啤酒 / 垃圾分类 / 凌晨 3:33 上线 |

### 15A.3 新增玩家属性(由于成就系统)

主角 stats 新增字段:

```typescript
interface PlayerStats {
  // ... 已有:语言/学科/心情/体力/金钱/日期/位置
  xp: number;             // 经验值
  level: number;          // 等级(M-LEVEL 进度)
  taler: number;          // 游戏内货币(跟 € 并存,€ 真实生活,Taler 成就/装饰)
  unlocked_achievements: Map<string, Achievement>;  // id → 解锁详情
  achievement_progress: Map<string, number>;        // id → 进度 0-1
  titles: string[];       // 已获称号(E-LAND-ALL → "Deutschlandkenner")
}
```

### 15A.4 成就解锁触发器(事件驱动)

```
游戏事件发生
    ↓
GameEvent 派发:
  - kp_completed(知识点完成)
  - level_completed(关卡通关)
  - discovery_visited(探索点打卡)
  - dialogue_ended(对话结束)
  - npc_relationship_changed(NPC 好感度变)
  - streak_extended(连续学习天数)
  - mock_taken(模拟考完成)
    ↓
AchievementService.check_unlock(user_id, event)
    ↓
遍历该用户所有成就 → 检查 unlock_condition → 解锁新成就
    ↓
触发 UI 弹窗(中心 + BGM 切换)
    ↓
更新 Pinia store + 同步后端(Phase 2+)
```

### 15A.5 与"走遍德国"的集成

每到达新城市 → 自动解锁:
- E-LAND-{州缩写}(州成就,16 个)
- E-CITY-{城市名}(城市成就,50 个)
- 3-5 个探索打卡(景点/美食/...)
- 5-10 个相关德语 KP(自动学习)
- 1 张城市徽章 UI 奖励

### 15A.6 与"真实一天循环"的集成

每天触发可能的成就:
- **早上 7:00 Bäckerei 打卡** → E7.2 超市品牌 + 1 个德语对话 M4
- **上课答对 5 题** → L-MATH-P1-STAR 进度 +
- **放学去博物馆** → E2.1 博物馆 + 文化百科
- **Kneipe 第 3 杯酒** → H-DRITTES-GLAS(隐藏)
- **熬夜到凌晨 3:33** → H-NIGHT-OWL(隐藏)

### 15A.7 Phase 拆分

| Phase | 成就范围 | 数量 |
|-------|---------|------|
| **Phase A(MVP)** | L1 + L2 + L3 + L4 + E1.1-E1.3 + E2.1 + E3.1 + E4.1 + E5.1 + E7.1+E7.2+E7.6 + M1-M3 + 隐藏 10 | ~700 |
| **Phase B** | E1.4-E1.5 + E2.2-E2.6 + E3.2-E3.6 + E4.2-E4.5 + E5.2-E5.4 + E6 + E11.2-E11.5 + E10 + E8 + E9 + M4-M5 + 隐藏 20 | ~1100 |
| **Phase C** | 节日限定 + 跨文化彩蛋 + 校友认证 | 长尾 |

### 15A.8 一个不一致需要确认

成就文档 §L1.2 提到 **TestDaF 专项**(TDN 3/4/5),但我们游戏已经改为 **A-levels + 雅思**(英式路径)。TestDaF 不在主线。请用户确认:

- **(a)** 保留 TestDaF 作为可选/补充(给想申德国大学的学生)?
- **(b)** 替换成 A-level 德语 KP(如果学生选了 A-level 德语课)?
- **(c)** 删除 TestDaF,只用 CEFR 等级里程碑?

### 15A.9 关联设计文档

- **完整设计**: `/Volumes/NewDisk/GermanLearning/docs/ACHIEVEMENT_SYSTEM.md`
- **数据结构**: `shared/types/achievement.ts`(`Achievement`, `Discovery`, `Reward`, `UnlockCondition`)
- **后端 API**: `backend/api/achievements.py`(`check_unlock`, `get_progress`, `get_wall`, `get_discovery_map`)
- **前端 Store**: `frontend/src/store/achievements.ts`
- **UI**: Achievement Wall / 探索地图 / 解锁弹窗(4 套草图在 §9)

---

| Phase | 内容 | 时间估计 |
|-------|------|---------|
| **Phase 0** | 技术验证 + 美术就位 | ✅ 1-2 周 |
| Phase 1 | 骨架 + 第 1 关剧本 + 基础对话 | 2-3 周 |
| Phase 2 | 学校子系统 + 选课 + 课堂 minigame | 3-4 周 |
| Phase 3 | 地图子系统 + 多个城市 + 完整 NPC | 4-6 周 |
| Phase 4 | 生活子系统 + 节日 + 社交 | 2-3 周 |
| Phase 5 | 多结局 + 完成度统计 + 用户系统(可选) | 2-3 周 |

---

## 17. 当前决定点(请用户 review)

### v2.0 已确认(用户 2026-06-21 中午)
1. ✅ **三轨并行**(德语 + A-levels + 雅思)— 用户确认
2. ✅ **双语切换机制代价** — "暂时可以"(后续可调)
3. ✅ **12 城市** — "暂时用那么多,以后再加"
4. ✅ **3 年时长** — Year 12 + Year 13 + 暑假
5. ✅ **模拟真实一天** — 起床 → 早餐 → 通勤 → 学校 → 放学探索 → 晚餐 → 睡觉
6. ✅ **真实地图** — 2D 城市地图 + POI 散布 + 主角 WASD 自由走动
7. ✅ **多 POI 类型** — 超市/博物馆/餐厅/图书馆/...
8. ✅ **跨城旅行** — 周末/假期去周边城市
9. ✅ **真实生活费** — €900/月开销 + 父母汇款 + 打工
10. ✅ **老师 + 同学关系** — 三轨并行基础上,加上社交维度
11. ✅ **成就系统** — 已集成 ACHIEVEMENT_SYSTEM.md(详见 §15A,~1860 个成就,3 类 + 隐藏彩蛋)

### v2.0 待决策点(请用户 review 6 个选择)

| # | 决策点 | 选项 |
|---|--------|------|
| **1** | **地图精度** | A. RPG Maker(WASD 自由走动,慢)<br>B. 简化(点击 POI,快)<br>C. 混合(城内自由走,跨城快进) |
| **2** | **时间流速** | A. 1 游戏小时 = 3 分钟<br>B. 1 游戏小时 = 1 分钟<br>C. 可调 1x/2x/4x |
| **3** | **学校深度** | A. 完整 minigame(每科 30+ 题)<br>B. 简化(每科 5-10 题)<br>C. 文本对话为主 |
| **4** | **生活费** | A. 详细(每月账单 + 打工 + 父母对话)<br>B. 简化(€总数 + 大笔确认)<br>C. 自动(玩家不管) |
| **5** | **跨城旅行** | A. 真实火车场景<br>B. 简化(选目的地 → 跳跃 → 到达)<br>C. 地图快进 |
| **6** | **交通真实度** | A. 完整(每段通勤要时间 + 钱)<br>B. 简化(Deutschlandticket 一张包月)<br>C. 无视(自由穿城) |

### 我的推荐组合(主打沉浸但保留效率)

| # | 推荐 | 理由 |
|---|------|------|
| 1 | **C 混合** | 城内 WASD 沉浸,跨城跳跃避免拖节奏 |
| 2 | **C 可调** | 默认 1x(1h=3min),赶时间 4x |
| 3 | **B 简化** | 每科 5-10 题核心,后续 DLC 加深 |
| 4 | **A 详细** | 你强调的"模拟真实消费"核心卖点 |
| 5 | **B 简化** | 主线快速推进,车上有小对话 |
| 6 | **B 简化** | Deutschlandticket 一张包月,不重复算 |

请告诉我这 6 个决策点的选择(或同意我的推荐),我再开始 Phase 0 实施(柏林 Mitte 真实地图 + 1 个 POI 完整 demo)。