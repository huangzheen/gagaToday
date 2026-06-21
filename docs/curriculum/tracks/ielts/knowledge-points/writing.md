# IELTS Writing 写作 —— KP 拆解(框架)

> 雅思写作 7.0+ 的 KP 拆解框架
> 版本: v1.0  ·  2026-06-21
> 共 ~100 KP,覆盖 Task 1 / Task 2 + 语法 + 词汇 + 评分训练

---

## 1. Task 1 图表描述(30 KP)

### 1.1 6 大图表类型

| # | KP ID | 图表类型 | 核心结构 |
|---|-------|---------|---------|
| 1 | kp_ielts_writing_t1_001 | 柱状图(bar chart) | 趋势 + 比较 + 极值 |
| 2 | kp_ielts_writing_t1_002 | 折线图(line graph) | 趋势 + 转折 + 交叉 |
| 3 | kp_ielts_writing_t1_003 | 饼图(pie chart) | 比例 + 比较 + 最大最小 |
| 4 | kp_ielts_writing_t1_004 | 表格(table) | 多组数据 + 趋势 + 比较 |
| 5 | kp_ielts_writing_t1_005 | 流程图(process) | 步骤 + 时序 + 连接词 |
| 6 | kp_ielts_writing_t1_006 | 地图(map) | 变化 + 方位 + 前后对比 |

### KP #1 示例:柱状图

```yaml
---
kp_id: kp_ielts_writing_t1_001
track: ielts
exam_board: ielts_academic
subject: writing
unit: t1
topic: bar-chart
type: task-type

specification_ref:
  - "IELTS Writing Task 1: Bar chart"
  - "British Council Band Descriptors Task 1 Achievement 7.0"

textbook_ref:
  - url: "https://www.ieltsliz.com/ielts-writing-task-1/"
    label: "IELTS Liz Task 1 Bar Chart"

past_paper_ref:
  - paper: "剑桥雅思 16 Test 1 Writing Task 1"
    question: "Bar chart: consumption of food"
    note: "典型多组柱状图"

difficulty: 3
exam_weight: 1/3 of writing score
review_status: draft
last_updated: 2026-06-21
---
```

#### Title
**Task 1 Bar Chart 柱状图**

#### Definition
描述柱状图(单图 / 多图 / 动态 / 静态)。150-200 字,20 分钟内完成。

#### Structure (4 段)
1. **开头**(2 句):paraphrase 题目,说图讲什么
2. **概述**(2 句):概括最大特征 / 趋势 / 对比
3. **细节 1**(3-4 句):一组数据详细描述
4. **细节 2**(3-4 句):另一组数据详细描述

#### Key language
- **趋势动词**: increase, rise, grow, surge, decline, decrease, fall, drop, remain stable
- **程度副词**: slightly, significantly, dramatically, sharply, gradually, steadily
- **比较**: the highest, the lowest, twice as much as, compared to, in contrast

#### 7.0+ 要求
- 不只罗列数据
- 有 grouping / categorisation(把数据分组讲)
- 选关键数据,不平均描述

#### Example outline
```
The bar chart shows [paraphrase].

Overall, [main trend: e.g., consumption of X increased significantly in all countries].

In 2000, [Country A] had the highest consumption, at [number], while [Country B] was the lowest. By 2020, this had changed dramatically: [Country C] overtook all others, reaching [number].

In contrast, [Country D] showed the opposite pattern, with consumption falling from [number] to [number] over the same period.
```

---

### 1.2-1.6 其他图表(5 个 KP)结构同上,Phase A2 详细展开

---

### 1.3 通用 Task 1 技能(8 KP)

- kp_ielts_writing_t1_007: **Overview 概述段写作**(核心,决定 7.0+)
- kp_ielts_writing_t1_008: **数据分组策略**
- kp_ielts_writing_t1_009: **时态选择**(动态图用过去时,静态图用一般现在时)
- kp_ielts_writing_t1_010: **倍数 / 分数表达**
- kp_ielts_writing_t1_011: **约数 / 模糊表达**(about, around, approximately, roughly)
- kp_ielts_writing_t1_012: **连接词使用**(Furthermore, In contrast, Meanwhile)
- kp_ielts_writing_t1_013: **避免重复**(同义替换:increase / rise / grow)
- kp_ielts_writing_t1_014: **字数控制**(150-200,过短扣分,过长浪费时间)

---

## 2. Task 2 议论文(25 KP)

### 2.1 4 大题型

| # | KP ID | 题型 | 核心结构 |
|---|-------|------|---------|
| 1 | kp_ielts_writing_t2_001 | Opinion 观点题 | 表明立场 + 论据 1 + 论据 2 + 结论 |
| 2 | kp_ielts_writing_t2_002 | Discussion 讨论题 | 一方观点 + 另一方观点 + 我方观点 |
| 3 | kp_ielts_writing_t2_003 | Problem-solution 问题解决 | 描述问题 + 原因 + 解决方案 |
| 4 | kp_ielts_writing_t2_004 | Advantages-disadvantages 利弊 | 优势 + 劣势 + 我方看法 |

### KP #1 示例:Opinion 观点题

```yaml
---
kp_id: kp_ielts_writing_t2_001
track: ielts
exam_board: ielts_academic
subject: writing
unit: t2
topic: opinion
type: task-type

specification_ref:
  - "IELTS Writing Task 2: Opinion essays"
  - "British Council Band Descriptors Task 2 Task Response 7.0"

textbook_ref:
  - url: "https://ielts-simon.com/ielts-writing-task-2-opinion/"
    label: "IELTS Simon Opinion Essays"

past_paper_ref:
  - paper: "剑桥雅思 16 Test 2 Writing Task 2"
    question: "Opinion: Some people think... To what extent do you agree?"

difficulty: 4
exam_weight: 2/3 of writing score
review_status: draft
last_updated: 2026-06-21
---
```

#### Title
**Task 2 Opinion Essay 观点题**

#### Definition
对某观点表态:"To what extent do you agree or disagree?" 要求 250-300 字,40 分钟内完成。

#### Structure (4 段)
1. **开头**:paraphrase + 明确表态(agree / disagree / 部分同意)
2. **Body 1**:第一个论据(理由 1 + 例子)
3. **Body 2**:第二个论据(理由 2 + 例子)
4. **结尾**:重述立场 + 总结

#### 7.0+ 要求
- 立场明确(不能两边都不同意 → 模糊)
- 充分展开(每个理由 1 个具体例子)
- 例子真实(自己的 / 公共的 / 假设的)
- 词汇丰富,语法多样

#### Example outline
```
[Hook: paraphrase topic] [Thesis: I strongly agree/disagree because...]

[Body 1: Reason 1] [Explanation] [Example: e.g., a real company, a research finding]

[Body 2: Reason 2] [Explanation] [Example]

[Conclusion: restate + summary]
```

#### Common errors
- 立场模糊(两边都说对)
- 论据空洞(说"this is good"不给理由)
- 例子虚假(瞎编明显不真实的)
- 模板痕迹(用模板句,考官能看出)

---

### 2.2-2.4 其他 3 大题型 KP:Phase A2 展开

---

### 2.5 通用 Task 2 技能(15 KP)

- kp_ielts_writing_t2_005: **立场表达**(I agree / I disagree / I'm not entirely sure)
- kp_ielts_writing_t2_006: **论证结构**(claim + reason + evidence)
- kp_ielts_writing_t2_007: **举例技巧**(具体例子 vs 抽象论述)
- kp_ielts_writing_t2_008: **让步表达**(Although..., Nevertheless...)
- kp_ielts_writing_t2_009: **因果表达**(because / due to / owing to / as a result)
- kp_ielts_writing_t2_010: **对比表达**(However / In contrast / On the other hand)
- kp_ielts_writing_t2_011: **避免模板化**
- kp_ielts_writing_t2_012: **回应题目所有部分**(Don't miss any part of the question)
- kp_ielts_writing_t2_013: **逻辑连接**(First, In addition, Moreover, Therefore)
- kp_ielts_writing_t2_014: **结论段写作**
- kp_ielts_writing_t2_015: **字数控制**(250-300)
- kp_ielts_writing_t2_016: **时间管理**(10min plan + 25min write + 5min check)
- kp_ielts_writing_t2_017: **审题**(不跑题)
- kp_ielts_writing_t2_018: **拼写 / 标点自查**
- kp_ielts_writing_t2_019: **避免常见语法错误**

---

## 3. 语法 KP(20 条,Task 1 & 2 通用)

| # | KP ID | 语法点 | 应用场景 |
|---|-------|--------|---------|
| 1 | kp_ielts_writing_g_001 | 从句(名词性 / 定语 / 状语) | 提高复杂度 |
| 2 | kp_ielts_writing_g_002 | 倒装(Nor / Not only) | 高分亮点 |
| 3 | kp_ielts_writing_g_003 | 强调句(It is... that) | 高分亮点 |
| 4 | kp_ielts_writing_g_004 | 虚拟语气(If... were) | 假设性表达 |
| 5 | kp_ielts_writing_g_005 | 分词作状语 | 简洁表达 |
| 6 | kp_ielts_writing_g_006 | 非谓语(不定式 / 动名词) | 避免重复 |
| 7 | kp_ielts_writing_g_007 | 比较级 / 最高级 | 图表描述 |
| 8 | kp_ielts_writing_g_008 | 时态(一般过去 / 现在完成 / 过去完成) | 任务1 |
| 9 | kp_ielts_writing_g_009 | 主谓一致 | 基础 |
| 10 | kp_ielts_writing_g_010 | 冠词(a / an / the) | 基础 |
| ... | ... | ... | ... |

### KP #1 示例:从句

```yaml
---
kp_id: kp_ielts_writing_g_001
track: ielts
exam_board: ielts_academic
subject: writing
unit: misc
topic: clauses
type: grammar
specification_ref:
  - "British Council Band Descriptors: Grammatical Range 7.0+"
  - "剑雅 17 Test 1 Writing Task 2 (Sample answer)"
difficulty: 3
review_status: draft
last_updated: 2026-06-21
---
```

#### Title
**复杂从句应用**

#### Why it matters
- 7.0+ 要求"语法多样"(Grammatical Range)
- 只用简单句 = 6.0 封顶

#### Key clause types
- **定语从句**:`The company **that** was founded in 1990 has expanded globally.`
- **状语从句**:`**While** some people argue that..., **others** believe...`
- **名词性从句**:`**What** I want to say is **that** education matters.`
- **条件从句**:`**If** we invest in renewable energy, **we can** reduce emissions.`

#### Examples (Band 7+ 写作)
- `**Although** technology has made our lives easier, **it has also** created new problems **that** we did not anticipate.`
- `**There are those who** argue that social media is harmful, **but** others **believe** **that** it has revolutionised communication.`

#### Common errors
- 从句嵌套太深(到第 3 层就开始乱)
- 主从句时态不一致
- 关系代词 / 副词用错

---

## 4. 词汇 KP(15 条)

| # | KP ID | 类别 |
|---|-------|------|
| 1 | kp_ielts_writing_v_001 | 议论文常用连接词(因果/对比/递进/举例/总结) |
| 2 | kp_ielts_writing_v_002 | 替换 overused words:"good", "bad", "important", "big" |
| 3 | kp_ielts_writing_v_003 | 学术主题词(教育/环境/科技/健康) |
| 4 | kp_ielts_writing_v_004 | 抽象名词化表达(`develop → development`, `grow → growth`) |
| 5 | kp_ielts_writing_v_005 | 同义替换训练 |
| ... | ... | ... |

---

## 5. 评分训练 KP(10 条)

| # | KP ID | 训练内容 |
|---|-------|---------|
| 1 | kp_ielts_writing_r_001 | 自评 Task Response(任务回应) |
| 2 | kp_ielts_writing_r_002 | 自评 Coherence & Cohesion(连贯) |
| 3 | kp_ielts_writing_r_003 | 自评 Lexical Resource(词汇) |
| 4 | kp_ielts_writing_r_004 | 自评 Grammatical Range(语法) |
| 5 | kp_ielts_writing_r_005 | 7 分 vs 6 分范文对比 |
| 6 | kp_ielts_writing_r_006 | 高频失分点识别 |
| 7 | kp_ielts_writing_r_007 | 大作文改写(模仿高分范文) |
| 8 | kp_ielts_writing_r_008 | 老师批改后修改策略 |
| 9 | kp_ielts_writing_r_009 | 写作反馈循环(写 → 改 → 重写) |
| 10 | kp_ielts_writing_r_010 | 真题范文背诵(每月 2-3 篇) |

---

## 6. 拆解统计

| 类别 | 数量 |
|------|------|
| Task 1 题型(6 大 + 8 通用) | 14 KP(本文件) |
| Task 2 题型(4 大 + 15 通用) | 19 KP(本文件) |
| 语法 | 20 KP(本文件) |
| 词汇 | 15 KP(本文件) |
| 评分训练 | 10 KP(本文件) |
| **已拆(本文件)** | 78 KP 框架 |
| **待拆(Phase A2 详细)** | 22 KP 详细 |
| **总计(规划)** | **~100 KP** |

---

OK,Writing KP 拆解框架到此。Phase A2 把 Task 1/Task 2 4 大题型的 10 个 KP 详细写完(每个 200-300 字)。
