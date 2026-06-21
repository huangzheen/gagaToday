# KP (Knowledge Point) 详细规范 v2.0

> 所有轨道(德语 / 雅思 / A-levels)共用的 KP 定义标准
> 本文档是**所有 KP 文档的写作模板**,所有 KP 必须严格遵守
> 版本: v2.0  ·  2026-06-21

---

## 1. 什么是 KP(Knowledge Point)

**定义**:一个**可单独测试、可单独教学、有明确 source 引用**的最小知识单元。

**例子(对比)**:

| 不是 KP ❌ | 是 KP ✅ |
|----------|---------|
| "数学" | "Solving quadratic equations by factorisation" |
| "英语听力" | "Identifying main idea in IELTS Listening Section 3" |
| "德语语法" | "möchten + Akkusativ(我想要某物)" |

判断标准:**这个知识点能出 1 道考试题吗?能,就是 KP;不能,继续拆。**

---

## 2. 文件结构

每个 KP 文件包含 **1 个或多个 KP**。按主题组织(通常一个 unit topic 一个文件)。

**目录约定**:
```
tracks/alevels/knowledge-points/mathematics/
├── c1-algebra.md          # 一个 unit topic 一个文件
├── c2-quadratics.md
├── c3-equations-and-inequalities.md
└── ...
```

**为什么不是 1 个 KP 1 个文件?**
- 10000 个 KP 拆成 10000 个文件,Github 浏览体验差
- 同一个 unit topic 的 KP 互相引用,放一起维护更方便
- 1 个文件包含 10-30 个 KP(典型 unit topic 粒度)

---

## 3. KP YAML Frontmatter 必填字段

```yaml
---
kp_id: kp_alevels_mathematics_c1_001           # 必填,全局唯一
track: alevels                                   # 必填,枚举: deutsch / ielts / alevels
exam_board: edexcel_ial                          # 必填,具体考试局/考试
subject: mathematics                             # 必填,学科
unit: c1                                         # 必填,unit code
topic: algebra                                   # 必填,topic name
type: concept                                    # 必填,枚举:见 § 4

specification_ref:                               # 必填,至少 1 个
  - "Edexcel IAL Mathematics Specification 2024, §1.1"

textbook_ref:                                    # 推荐,至少 1 个
  - url: "https://www.physicsandmathstutor.com/maths-revision/alevel-maths-ial/algebra/..."
    label: "PMT C1 Algebra Notes"
  - url: "https://znotes.io/ial-mathematics/c1/algebra/..."
    label: "Znotes C1 Algebra"

past_paper_ref:                                  # 推荐,至少 1 个
  - paper: "2024 Jan IAL C1"
    question: "Q1"
    note: "典型求根公式应用"

prerequisites:                                   # 推荐
  - kp_alevels_mathematics_c1_000               # 前置 KP ID

difficulty: 2                                    # 推荐,1-5(5 最难)
exam_weight: high                                # 推荐,high / medium / low
exam_frequency: high                             # 推荐,历史出题频次

review_status: draft                             # 必填,draft / reviewed / approved
last_updated: 2026-06-21                         # 必填,YYYY-MM-DD
---
```

### 3.1 字段详解

#### `kp_id` (必填,全局唯一)
- 格式: `kp_{track}_{subject}_{unit}_{number}`
- `subject` 用 kebab-case: `further-mathematics` / `english-language` / `government-and-politics`
- `unit` 用官方 unit code: `c1` / `p1` / `w1` / `s1`
- `number` 3 位数补零: `001`, `002`, ...
- 例:
  - `kp_alevels_mathematics_c1_001`
  - `kp_alevels_physics_p1_001`
  - `kp_ielts_listening_p1_001`(剑雅 Test 1 Part 1)
  - `kp_deutsch_a1_001`

#### `track` (必填,枚举)
- `deutsch` / `ielts` / `alevels`

#### `exam_board` (必填)
- `edexcel_ial` / `edexcel_gce`(英国本土) / `cambridge_caie` / `aqa` / `ocr`
- `ielts_academic` / `ielts_general`
- `testdaf` / `goethe_c1` / `dsh`

#### `type` (必填,枚举)

| Track | type 枚举 |
|-------|----------|
| **alevels** | `concept` / `formula` / `procedure` / `skill` / `application` / `experiment` |
| **ielts** | `micro-skill` / `strategy` / `vocabulary` / `grammar` / `topic-vocabulary` / `task-type` |
| **deutsch** | `expression` / `grammar` / `vocabulary` / `culture` / `phonetics` / `strategy` |

#### `specification_ref` (必填,**至少 1 个**)
- 官方 Specification 文件 + 章节号
- 例:
  - `"Edexcel IAL Mathematics Spec 2024, §1.1 Algebra"`
  - `"Edexcel IAL Physics Spec 2024, Topic 1: Mechanics"`
  - `"IELTS Speaking Band Descriptors, Lexical Resource 7.0"`

#### `textbook_ref` / `past_paper_ref` (推荐)
- 第三方权威资源链接
- 标签清晰,标明来源类型

#### `difficulty` / `exam_weight` / `exam_frequency` (推荐)
- `difficulty`: 1-5(主观评估,后续可用真题数据校准)
- `exam_weight`: high / medium / low(占总分比例)
- `exam_frequency`: high / medium / low(过去 5 年出题频次)

#### `review_status` (必填)
- `draft`: AI 生成,未人工 review
- `reviewed`: 人工 review 过
- `approved`: 人工 review + 测试通过

---

## 4. KP 正文结构(Markdown Body)

```markdown
## 1. 名称 / Title
**Solving quadratic equations by factorisation**

## 2. 定义 / Definition
[1-2 句精确定义,说明这是什么、解决什么问题]

## 3. 为什么重要 / Why it matters
[考试意义,实际应用]

## 4. 知识点讲解 / Explanation
[用学习者易懂的语言讲解,可有公式/图/例子]

### 4.1 关键概念
### 4.2 解题步骤
### 4.3 易错点

## 5. 例子 / Examples
[典型例子 2-3 个,从简到难]

## 6. 真题示例 / Past Paper Examples
[至少 1 题,标注出处]

## 7. 关联 KP / Related KPs
- 前置: kp_xxx
- 后继: kp_yyy
- 相关: kp_zzz

## 8. 关联练习 / Practice
[指向练习库或附 2-3 题]

## 9. 关联关卡 / Game Scenarios
[指向游戏关卡 ID,游戏内引用此 KP]

## 10. 文化 / 历史背景(可选)
[该知识点的历史背景、实际应用场景]
```

---

## 5. 完整示例(A-levels Mathematics C1)

```markdown
---
kp_id: kp_alevels_mathematics_c1_001
track: alevels
exam_board: edexcel_ial
subject: mathematics
unit: c1
topic: algebra
type: procedure

specification_ref:
  - "Edexcel IAL Mathematics Specification 2024, §1.1 Algebra — Quadratic equations"

textbook_ref:
  - url: "https://www.physicsandmathstutor.com/maths-revision/alevel-maths-ial/algebra/quadratics/"
    label: "PMT C1 Quadratics Notes"
  - url: "https://znotes.io/ial-mathematics/c1/quadratics/"
    label: "Znotes C1 Quadratics"

past_paper_ref:
  - paper: "2024 Jan IAL C1"
    question: "Q2"
    note: "基础因式分解,常数项为正"
  - paper: "2023 May IAL C1"
    question: "Q3"
    note: "需要先提取公因式"

prerequisites:
  - kp_alevels_mathematics_c1_000  # 基本代数运算

difficulty: 2
exam_weight: high
exam_frequency: high
review_status: draft
last_updated: 2026-06-21
---

## 1. Title
**Solving quadratic equations by factorisation**

## 2. Definition
因式分解法解一元二次方程。通过把二次多项式写成两个一次因式相乘的形式,
令每个因式为 0 求出根。

## 3. Why it matters
- C1 Paper 必考,占 6-8 分
- A2 中解二次不等式、解联立方程组都依赖此技能
- 物理、化学、经济学场景中"求交点/平衡点"核心工具

## 4. Explanation

### 4.1 关键概念
- 标准形:`ax² + bx + c = 0`,其中 `a ≠ 0`
- 因式分解形:`(px + q)(rx + s) = 0`,展开后: `prx² + (ps + qr)x + qs = 0`
- 零因子定理:如果 `(px + q)(rx + s) = 0`,则 `px + q = 0` 或 `rx + s = 0`

### 4.2 解题步骤
1. 移到一边,确保等式右边为 0
2. 因式分解(尝试找两个数,乘积为 c,和为 b)
3. 令每个因式 = 0,解一次方程
4. 写出两个解(可能相等)
5. 验证(可选,代入原方程)

### 4.3 易错点
- 忘记移到一边(`x² + 5x = 6` 写成 `x² + 5x - 6` 后再解,不是直接分解)
- 二次项系数 a ≠ 1 时,需要先考虑提取公因式
- 写成 `(x + 3)(x + 2) = 0` 时,x = -3, x = -2(**符号**)

## 5. Examples

**Example 1**(简单):
`x² + 5x + 6 = 0`
→ `(x + 2)(x + 3) = 0`
→ `x = -2` 或 `x = -3`

**Example 2**(需提取公因式):
`2x² + 6x + 4 = 0`
→ `2(x² + 3x + 2) = 0`
→ `2(x + 1)(x + 2) = 0`
→ `x = -1` 或 `x = -2`

## 6. Past Paper Examples
- **2024 Jan IAL C1 Q2**: 基础 `x² - 7x + 12 = 0` 分解 → `(x-3)(x-4)=0` → x=3 或 4
- **2023 May IAL C1 Q3**: 提取公因式 `3x² - 12x + 9 = 0` → `3(x²-4x+3)=0` → `3(x-1)(x-3)=0` → x=1 或 3

## 7. Related KPs
- 前置: kp_alevels_mathematics_c1_000 (基本代数运算)
- 后继: kp_alevels_mathematics_c1_002 (Quadratic formula 求根公式)
- 后继: kp_alevels_mathematics_c1_003 (Completing the square 配方法)
- 相关: kp_alevels_mathematics_c1_010 (二次不等式, A2 深入)

## 8. Practice
- Textbook: PMT C1 Quadratics Worksheet
- Past paper: 2018-2024 IAL C1 Q1-Q3(本题型反复出现)

## 9. Game Scenarios
[未来游戏关卡中,涉及"解一元二次方程"的关卡会引用此 KP ID]
```

---

## 6. 多 KP 文件的写法

一个文件可以包含多个 KP(同 topic):

```markdown
---
kp_id: kp_alevels_mathematics_c1_001
... (字段 1)
---

## KP #1: Solving quadratic equations by factorisation

[正文...]

---

---
kp_id: kp_alevels_mathematics_c1_002
... (字段 2)
---

## KP #2: Quadratic formula

[正文...]
```

**用 `---` 分隔每个 KP 的 frontmatter,文件首部包含目录(TOC)。**

---

## 7. 跨赛道 KP 的特殊处理

### 7.1 同一概念出现在多个赛道

例:语法"虚拟语气"
- A-levels English Language 有这个 KP
- 雅思 Writing 也会涉及

**做法**: **每个赛道独立建 KP**(`kp_alevels_english-language_xxx_001` 和 `kp_ielts_writing_xxx_001`),**不共享**。理由:
- 教学目标不同(A-levels 偏分析,雅思偏应用)
- 考试要求不同(A-levels 评分看 terminology,雅思看 band descriptors)
- 维护边界清晰

### 7.2 KP 之间的跨赛道关联

用 `related_kps_cross_track` 字段(可选):
```yaml
related_kps_cross_track:
  - kp_ielts_writing_g_001  # IELTS 写作中类似语法点
```

---

## 8. 质量检查(LLM 辅助生成后必查)

生成 KP 后,**必须**经过以下检查:

### 8.1 完整性检查(脚本)
- [ ] `kp_id` 唯一
- [ ] `track` / `exam_board` / `subject` / `unit` / `type` 必填
- [ ] `specification_ref` 至少 1 个
- [ ] `review_status` 必填

### 8.2 准确性检查(人工 + LLM)
- [ ] KP 定义是否清晰?能否出 1 道题?
- [ ] specification_ref 章节号是否真实?(不能瞎编)
- [ ] past_paper_ref 出处是否真实?(必须查 Edexcel 官网 / Physics & Maths Tutor 验证)
- [ ] prerequisites 关系是否合理?(不能循环依赖)
- [ ] difficulty 评估是否合理?

### 8.3 一致性检查(脚本)
- [ ] 同 unit 内的 KP 是否覆盖了 spec 的所有 sections?
- [ ] KP 编号是否连续?
- [ ] prerequisites 引用的 KP 是否存在?

---

## 9. Review 流程

```
AI 生成 KP (review_status: draft)
    ↓
自动检查(脚本)
    ↓
人工 review(用户或专业老师)
    ↓
标记 review_status: reviewed
    ↓
教学测试(用 KP 出 1-2 道题,验证 KP 是否讲清楚了)
    ↓
标记 review_status: approved
```

**当前阶段**:所有 KP 都是 `draft`,等用户 review。

---

## 10. LLM Prompt 模板(KP 生成用)

```markdown
你是一个 A-levels 数学老师。请根据以下 Specification 段落,生成 KP(Knowledge Point)YAML。

【输入】
Specification 段落:
"§1.1 Algebra
Students should be able to:
(a) solve quadratic equations by factorisation, completing the square and using the quadratic formula
(b) understand the discriminant and its relationship to the number of real roots
..."

Unit: c1
Subject: mathematics
Exam Board: edexcel_ial

【输出要求】
1. 拆成 3-5 个 KP,每个 KP 一个 YAML frontmatter + 简短正文(200-300 字)
2. 每条 KP 必填 kp_id / specification_ref
3. 正文必须包含:Definition / Why it matters / Explanation / Examples
4. 如果你不确定某个信息(比如具体 past paper 出处),标 [REVIEW_NEEDED],不要瞎编
5. 只输出 KP,不要展开讲元方法论
```

---

OK,KP 规范到此。**所有 KP 文档写作时必须严格遵守本规范**。Phase A1 的数学 C1 algebra KP 文档是这个规范的第一个实例。
