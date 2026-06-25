> ⚠️ **本知识库当前未接入游戏代码**（标记于 2026-06-25 文档收敛）
>
> Curriculum 知识库是 2026-06-21 起草的远期内容资产（德语/雅思/A-levels 三轨道），
> 用作未来关卡剧本的"单一源"。当前实现（A 方案：POI 探索 + 素材生成器）
> **不直接消费** KP（知识库条目）——POI 内容是 LLM 即兴生成 + OSM 数据提取。
>
> 下一阶段决定：是否把 KP 体系接入 POI 生成器的内容审核工作流，
> 或保持本目录作为长期资产独立演进。
>
# Curriculum 课程知识库

> **项目课程内容的"单一源"(single source of truth)** —— 所有教材、知识点、学习路径、关卡剧本都从这里出发
> 版本: v2.0  ·  2026-06-21
> 适配 PROPOSAL.md v2.0:走遍德国 + 文化融入 + 德福 → **扩展到雅思 7.0+ + A-levels IAL 全科**

---

## 1. 这个目录是干嘛的

之前 PROPOSAL 里的内容创作是 **"教材 → 关卡剧本"** 的两步模型。
现在三个赛道(德语 / 雅思 / A-levels)一起上,如果每个关卡都重新写一遍知识点,**信息会爆炸且无法保持一致**。

所以多插入一层:**Knowledge Point (KP) 知识库**。

```
官方 Specification       第三方资源(PMT / Znotes)
   │                            │
   └────────────┬───────────────┘
                ↓
       Knowledge Point(KP) ← 知识库的最小单元
                ↓
       关卡剧本(Scenario JSON)   ← 游戏里用
                ↓
       错题本 / 词汇本           ← 用户侧
```

**每条 KP 唯一**、**每个关卡只是 KP 的引用**、**每道错题挂回 KP**。改一处,处处同步。

---

## 2. 三条赛道(Track)

| Track | 目标考试 | 起点 → 目标 | 范围 |
|-------|---------|------------|------|
| **deutsch** 德语 | TestDaF(德福) | A1 → TDN 4-5(B2-C1) | Phase 1-5 已有规划,沿用 |
| **ielts** 雅思 | IELTS Academic | 5.0 → **每科 7.0+** | 4 项全到 7.0+ |
| **alevels** A-levels | Edexcel IAL | IGCSE → A* | **25-33 科全拆到 KP** |

**当前重心**:`alevels` 知识库搭建(全新,工作量最大)+ `ielts` 4 项 + `deutsch` 沿用。

---

## 3. "教材一致性"的方法论(关键)

> **我们不是"教材的搬运工",我们以"考试"为中心。**

### 3.1 三个赛道的"四件套"

每个 KP 必带 `sources:` 字段,至少 1 个 **官方 Specification** + 1 个 **第三方权威资源**。**没有 source 的 KP 不能入库**。

| 赛道 | 官方 Spec(必引) | 第三方权威资源(选引) | 真题(选引) |
|------|------------------|---------------------|-----------|
| **deutsch** | TestDaF Modellsatz / Goethe-Zertifikat C1 | Menschen / Aspekte 教材目录 | TestDaF 真题集 |
| **ielts** | British Council 官方 Band Descriptors + 题型说明 | 剑桥雅思真题 4-19(剑雅) | 剑雅真题 |
| **alevels** | Edexcel IAL Specification(每科 PDF) | Physics & Maths Tutor / Savemyexams / Znotes | Edexcel IAL Past Papers + Mark Scheme |

### 3.2 为什么不是"以教材为中心"?

- A-levels 同考点不同书能讲出花来,买 Pearson Edexcel 教材的电子版要 ¥300+ 一门,33 门 = 1 万+
- 官方 Specification PDF **免费**,考点定义就是真理
- Past Papers + Mark Scheme 决定了"实际怎么考",比教材重要
- Physics & Maths Tutor(英国学生用的免费站)有逐章讲解视频+笔记,质量超过大多数教材

**所以**:不依赖单一教材,依赖 **官方 Spec + Past Papers + 第三方权威资源** 的三角验证。

### 3.3 强制字段(保证"详尽"且"一致")

```yaml
---
kp_id: kp_math_ial_c1_001
track: alevels                  # 必填,枚举
exam_board: edexcel_ial         # 必填
subject: mathematics            # 必填
unit: c1                        # 必填,unit code
type: concept                   # 必填,枚举

specification_ref:              # 必填,至少 1 个
  - "Edexcel IAL Mathematics Spec 2024, §1.1 Algebra"

textbook_ref:                   # 推荐,至少 1 个
  - url: "https://www.physicsandmathstutor.com/..."
    label: "PMT C1 Algebra Notes"
  - url: "https://..."
    label: "Znotes C1 Algebra"

past_paper_ref:                 # 推荐,至少 1 个
  - paper: "2024 Jan C1"
    question: "Q1"
    note: "典型求根公式应用"

prerequisites:                  # 推荐
  - kp_math_ial_c1_000

difficulty: 2                   # 1-5(5 最难)
exam_weight: high               # high/medium/low
exam_frequency: high            # 历史出题频次

review_status: draft            # draft / reviewed / approved
last_updated: 2026-06-21
---
```

任何 **缺 specification_ref** 的 KP 视为不完整,不入库(脚本检查)。

---

## 4. 目录结构

```
docs/curriculum/
├── README.md                    # 本文件(总览)
├── KP_SCHEMA.md                 # KP 详细规范(必读)
│
├── tracks/
│   ├── deutsch/                 # 德语(沿用 SCRIPT_METHODOLOGY)
│   │   ├── 00-overview.md
│   │   ├── syllabus.md
│   │   ├── knowledge-points/    # KP 库
│   │   ├── textbooks/           # 教材结构(章/节)
│   │   ├── scenarios/           # 软链 → backend/app/data/scenarios/
│   │   └── path.md
│   │
│   ├── ielts/                   # 雅思
│   │   ├── 00-overview.md
│   │   ├── knowledge-points/
│   │   │   ├── listening.md     # 4 项
│   │   │   ├── reading.md
│   │   │   ├── writing.md
│   │   │   └── speaking.md
│   │   ├── question-bank/       # 剑雅 4-19 索引
│   │   ├── path.md
│   │   └── scenarios/           # 口语对话剧本
│   │
│   └── alevels/                 # A-levels(新,重点建设)
│       ├── 00-overview.md       # 考试局选型 + 全部 25-33 科
│       ├── subjects/            # 33 门学科元数据
│       │   ├── mathematics.md
│       │   ├── physics.md
│       │   └── ...(33 门)
│       ├── knowledge-points/    # KP 库(每科一个目录)
│       │   ├── mathematics/
│       │   │   ├── c1-algebra.md
│       │   │   ├── c2-functions.md
│       │   │   └── ...
│       │   └── ...(33 科)
│       ├── past-papers/         # 真题索引
│       └── path.md              # IGCSE → AS → A2 → A*
│
└── routes/                      # 跨轨道路线
    ├── apply-to-germany.md      # 申请德国(主路线)
    └── _templates/              # 路线模板
```

---

## 5. 工作量与节奏

### 5.1 估算(以 Edexcel IAL 为准)

| 项 | 估算 |
|----|------|
| IAL 全部可选科目 | 25-33 门 |
| 平均每门 KP 数 | 200-400 条 |
| **总 KP 数** | **5000-12000 条** |
| 雅思 KP(4 项) | ~400 条 |
| 德语 KP(沿用) | ~600 条 |
| **总计** | **~10000 条 KP** |

### 5.2 节奏

| 阶段 | 时间 | 产出 |
|------|------|------|
| **Phase A1**(现在) | 本周 | 骨架 + KP_SCHEMA + 1 门(数学)完整跑通 + 路线 |
| **Phase A2** | 1-2 周 | 数学 IAL 全 8 单元 + 物理 / 化学 IGCSE + AS 完整 |
| **Phase A3** | 3-6 周 | 8 门主科全部 KP + 雅思 4 项 |
| **Phase A4** | 6-12 周 | 33 科全 KP + 错题关联 |
| **Phase B** | 持续 | 关卡剧本基于 KP 编写 |

**不要尝试一次写完 10000 条 KP**。每批建好,用户 review,再扩下一批。

### 5.3 自动化保障

- `scripts/curriculum/fetch_edexcel_specs.py` —— 抓 Edexcel 官网 Specification 目录
- `scripts/curriculum/validate_kp.py` —— 扫所有 KP,检查 source 字段完整性
- `scripts/curriculum/coverage_report.py` —— 覆盖率报告(spec 段落 → KP 的映射)

---

## 6. 怎么用这个知识库

### 6.1 写关卡剧本时(下游)

Scenario JSON 引用 KP:
```json
{
  "scenario_id": "berlin_cafe_01",
  "learning_objectives_kp_refs": [
    "kp_deutsch_a1_007",   // möchten + Akkusativ
    "kp_deutsch_a1_012"    // 食物词汇
  ]
}
```

**好处**:改 KP 一次,所有引用 KP 的关卡自动同步。

### 6.2 写错题本时(下游)

错题挂到 KP:
```typescript
interface UserError {
  kp_ref: string;            // 挂到 KP
  scenario_ref: string;
  error_type: 'grammar' | 'vocabulary' | 'pronunciation';
  user_input: string;
  suggested_fix: string;
  // ...
}
```

**好处**:错题本可以按 KP 聚合,看到"哪个 KP 错得最多"。

### 6.3 前端展示(可选)

KP 列表可渲染为"知识点地图":
- 用户查看已学/未学 KP
- KP 关联的关卡、错题、词汇一目了然
- 间隔重复算法(Anki 风格)可基于 KP 列表

---

## 7. Phase A1 任务(本周)

✅ 已完成(本目录下):
- `tracks/alevels/00-overview.md` —— Edexcel IAL 选型 + 33 科清单
- `tracks/alevels/subjects/mathematics.md` —— 数学科元数据
- `tracks/alevels/knowledge-points/mathematics/c1-algebra.md` —— **数学 C1 Algebra 完整 KP 拆解(模板)**
- `tracks/ielts/00-overview.md` —— 雅思 4 项元数据
- `tracks/deutsch/00-overview.md` —— 德语(沿用现有规划)
- `routes/apply-to-germany.md` —— 申请德国路线
- `KP_SCHEMA.md` —— KP 详细规范
- `scripts/curriculum/fetch_edexcel_specs.py` —— 抓 Edexcel specs 工具

⏳ 后续:
- 用户 review `c1-algebra.md`(模板,验证 KP 拆解质量)
- 用模板扩展到数学其他单元 + 物理 IGCSE/AS
- 持续扩展到全科

---

## 8. 命名约定

- **Track**: `deutsch` / `ielts` / `alevels`(小写,无连字符)
- **Subject**: `mathematics` / `further-mathematics` / `physics` / ...(kebab-case)
- **Unit code**: 用 Edexcel 官方 unit code,如 `c1` / `c2` / `p1` / `p2` / `w1` / `w2`
- **KP ID**: `kp_{track}_{subject}_{unit}_{number}`,如:
  - `kp_alevels_mathematics_c1_001`
  - `kp_ielts_listening_p1_001`
  - `kp_deutsch_a1_001`
- **文件路径**: `tracks/{track}/knowledge-points/{subject}/{unit}-{topic}.md`

---

OK,总览到此。下一步:开始按 Phase A1 写各个文件。
