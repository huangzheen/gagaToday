# IELTS Reading 阅读 —— KP 拆解(框架)

> 雅思阅读 30-32/40 题对 → 7.0+ 的 KP 拆解框架
> 版本: v1.0  ·  2026-06-21
> 共 ~120 KP,覆盖全部题型 + 话题词汇 + 阅读技能

---

## 1. 题型 KP(11 大类)

| # | KP ID | 题型 | 数量 | 难度 |
|---|-------|------|------|------|
| 1 | kp_ielts_reading_t_001 | True / False / Not Given | 12-15 题 | 3 |
| 2 | kp_ielts_reading_t_002 | Yes / No / Not Given(观点) | 8-10 题 | 4 |
| 3 | kp_ielts_reading_t_003 | Matching headings(段落大意) | 5-7 题 | 4 |
| 4 | kp_ielts_reading_t_004 | Matching information(细节定位) | 5-7 题 | 4 |
| 5 | kp_ielts_reading_t_005 | Matching features(作者/理论匹配) | 4-6 题 | 4 |
| 6 | kp_ielts_reading_t_006 | Matching sentence endings | 4-6 题 | 3 |
| 7 | kp_ielts_reading_t_007 | Multiple choice(单选) | 4-6 题 | 3 |
| 8 | kp_ielts_reading_t_008 | Multiple choice(多选) | 2-4 题 | 4 |
| 9 | kp_ielts_reading_t_009 | Short answer | 4-6 题 | 3 |
| 10 | kp_ielts_reading_t_010 | Summary / Note / Table completion | 6-10 题 | 4 |
| 11 | kp_ielts_reading_t_011 | Flowchart / Diagram label completion | 3-5 题 | 3 |

### KP #1 示例:True / False / Not Given

```yaml
---
kp_id: kp_ielts_reading_t_001
track: ielts
exam_board: ielts_academic
subject: reading
unit: misc
topic: tfng
type: task-type

specification_ref:
  - "IELTS Reading Test Format: True / False / Not Given"
  - "剑雅 16 Test 1 Reading Passage 1"

past_paper_ref:
  - paper: "剑桥雅思 16 Test 1 Reading P1"
    question: "Q1-7"
    note: "典型 TFNG 题型"

difficulty: 3
exam_weight: 12
exam_frequency: high
review_status: draft
last_updated: 2026-06-21
---
```

#### Title
**True / False / Not Given 判断题**

#### Definition
判断题目陈述与原文是否一致:
- **True**:题目与原文一致
- **False**:题目与原文矛盾
- **Not Given**:原文未提及(没说对也没说错)

#### Why it matters
- 几乎每套题都有 6-10 题 TFNG
- 7.0+ 至少 7/10 正确
- 中国学生常错(分不清 False 和 Not Given)

#### Key skills
- **False vs NG 关键区别**:
  - False = 原文有相反信息
  - NG = 原文根本没提
- 例:
  - 题目:"Cows are **green**."
  - 原文:"Cows are black and white." → **False**(颜色相反)
  - 原文:"Cows are common farm animals." → **Not Given**(没提颜色)

#### Common errors
- 把"原文没说"当 False(应是 NG)
- 凭常识判断(必须严格基于原文)
- 同义替换没看出来

#### Related KPs
- KP #11(同义替换)
- KP #12(细节定位)

---

### KP #2-11 题型:Phase A2 详细拆解(同 KP #1 结构)

每个题型一个 KP,含:
- Definition
- 7.0+ 答题策略
- 典型真题示例(剑雅 4-19)
- 易错点
- Related KPs

---

## 2. 阅读技能 KP(微观)

### KP #12: 略读 (skimming)
```yaml
kp_id: kp_ielts_reading_s_001
type: micro-skill
```
- 快速读段首段尾段中,抓主旨
- 速度目标:1 分钟 / 段

### KP #13: 扫读 (scanning)
```yaml
kp_id: kp_ielts_reading_s_002
type: micro-skill
```
- 找特定信息(数字 / 名字 / 时间)
- 速度目标:30 秒 / 题

### KP #14: 同义替换识别(paraphrase)
```yaml
kp_id: kp_ielts_reading_s_003
type: micro-skill
```
- 题面和原文用不同词说同一事
- 训练方法:做真题时积累 paraphrase 库

### KP #15: 长难句分析
```yaml
kp_id: kp_ielts_reading_s_004
type: micro-skill
```
- 学术文章句子长,需识别主谓宾
- 训练:每天 5 个长难句,断句找主干

### KP #16: 时间管理(60 分钟 / 40 题)
```yaml
kp_id: kp_ielts_reading_s_005
type: strategy
```
- 目标:平均 90 秒 / 题
- P1(简单) 15 分钟,P2 20 分钟,P3(难)25 分钟

### KP #17: 生词处理策略
```yaml
kp_id: kp_ielts_reading_s_006
type: strategy
```
- 不查字典,猜词义(根据上下文)
- 标注生词,做完再查

---

## 3. 学术话题词汇(40 个 KP)

按 9 大话题分类,每话题 4-5 个 KP:

| # | 话题 | KP 数量 | 示例词汇 |
|---|------|---------|---------|
| 1 | Education 教育 | 5 | curriculum, pedagogy, assessment, literacy |
| 2 | Environment 环境 | 5 | biodiversity, sustainability, ecosystem, climate |
| 3 | Technology 技术 | 5 | algorithm, AI, automation, innovation |
| 4 | Health 健康 | 5 | nutrition, disease, treatment, mental health |
| 5 | Society 社会 | 5 | urbanization, demographic, inequality, migration |
| 6 | History 历史 | 4 | archaeology, civilization, medieval, industrial |
| 7 | Economics 经济 | 4 | GDP, inflation, recession, globalization |
| 8 | Psychology 心理 | 4 | cognition, behavior, perception, motivation |
| 9 | Natural science 自然科学 | 4 | molecule, cell, evolution, biodiversity |

每话题 KP 结构:
- 词汇清单(15-20 词)
- 真题出处(剑雅 4-19 对应 passage)
- 释义(中文 + 英文 definition)
- 派生词 / 词族

### 示例:Education 话题

```yaml
---
kp_id: kp_ielts_reading_v_edu_001
track: ielts
exam_board: ielts_academic
subject: reading
unit: misc
topic: academic-vocabulary-education
type: vocabulary

specification_ref:
  - "IELTS Academic Word List: Education sublist"
  - "剑雅 16 Test 2 Reading P2 (Education topic)"

textbook_ref:
  - url: "https://www.ieltsbuddy.com/ielts-vocabulary-education.html"
    label: "IELTS Buddy Education Vocabulary"

past_paper_ref:
  - paper: "剑桥雅思 16 Test 2 Reading P2"
    question: "全文"
    note: "Education 主题文章"

difficulty: 3
review_status: draft
last_updated: 2026-06-21
---
```

#### Title
**Education 话题词汇(Reading 应用)**

#### Core vocabulary (15-20 words)
- **curriculum** [kəˈrɪkjʊləm] 课程
- **pedagogy** [ˈpedəɡɒdʒi] 教学法
- **literacy** [ˈlɪtərəsi] 读写能力
- **assessment** [əˈsesmənt] 评估
- **enrollment** [ɪnˈrəʊlmənt] 入学
- **vocational** [vəˈkeɪʃənəl] 职业的
- **tuition** [tjuˈɪʃn] 学费
- **compulsory** [kəmˈpʌlsəri] 强制的
- **extracurricular** [ˌekstrəkəˈrɪkjʊlə] 课外的
- **dropout** 辍学
- ... 等 15-20 词

#### Word family
- **literacy** → illiterate (形), literally (副,但意思不同)

#### Where it appears in past papers
- 剑 16 T2 P2:Education 主题
- 剑 15 T3 P2:Online learning
- 剑 14 T2 P1:History of education

#### Related KPs
- kp_ielts_listening_v_edu_001(听力中类似话题)

---

## 4. 拆解统计

| 类别 | 数量 |
|------|------|
| 11 大题型 | 11 KP(本文件 KP #1 详细,#2-11 Phase A2 拆) |
| 阅读技能 | 6 KP(框架,本文件) |
| 学术话题词汇 | 40 KP(框架,本文件示意 1 个) |
| **已拆(本文件)** | 12 KP |
| **待拆(Phase A2)** | 108 KP |
| **总计(规划)** | **~120 KP** |

---

OK,Reading KP 拆解框架到此。后续 Phase A2 详细展开 11 题型 + 40 话题词汇。
