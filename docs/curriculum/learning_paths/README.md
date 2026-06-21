# Learning Paths 学习路径

> 用结构化 YAML 描述每科 / 每学年 / 每考试季的学习路径
> **本目录是 curriculum 知识库与游戏关卡之间的桥梁**
> 版本: v1.0  ·  2026-06-21

---

## 1. 这是什么

之前我们用 Markdown 文档 + KP(Knowledge Point)库来描述知识(适合人读)。

**YAML 学习路径是"机器可读"的教学流程**:
- 直接读 → 知道学生每学期 / 每周 / 每节课学什么
- 程序可读 → 可以自动生成 scenario JSON、错题计划、关卡脚本

```
KP 库 (Markdown)         ← 单个知识点(原子单位)
   ↓ 引用
Learning Path (YAML)     ← 教学流程(什么时间、什么课、用哪些 KP)
   ↓ 引用
Scenario JSON            ← 游戏关卡(用 KP + Path 包装成对话 / 题目)
   ↓ 引用
错题本 / 词汇本
```

---

## 2. 命名约定

```
learning_paths/{subject}_{year}.yaml

例:
  mathematics_year12.yaml      # 数学 12 年级(IAS / AS)
  mathematics_year13.yaml      # 数学 13 年级(IA2 / A2) [待建]
  physics_year12.yaml          # 物理 12 年级 [待建]
  ielts_full.yaml              # 雅思全程 [待建]
  deutsch_a1_b1.yaml           # 德语 A1 → B1 [待建]
```

---

## 3. YAML Schema 简版

(完整 schema 见 `../KP_SCHEMA.md`,这里只列 learning path 专属字段)

```yaml
metadata:
  subject: <string>           # 学科
  exam_board: <string>        # edexcel_ial | aqa | ocr | caie | ...
  level: <string>             # a-level-year12 | a-level-year13 | gcse | ...
  qualification: <string>      # IAL IAS | IAL IA2 | IAL | GCSE | ...
  duration_weeks: <int>       # 总周数
  total_lessons: <int>        # 总 lesson 数
  target_grade: <string>      # A* / A / B / 7.0+ / TDN 4 / ...

units:
  - id: <kebab-case>
    name: <string>             # e.g. "Pure Mathematics 1"
    code: <string>             # 考试局给的 paper code, e.g. "WMA11/01"
    difficulty: <string>       # easy | medium | hard | easy-medium | ...
    duration_weeks: <int>
    topics:
      - id: <kebab-case>
        name: <string>         # e.g. "Algebra"
        difficulty: <string>
        kp_count: <int>        # 估算本 topic 的 KP 数
        lessons:
          - id: <kebab-case>
            name: <string>     # e.g. "Laws of indices"
            kp_refs: [<string>] # 引用 KP 库中的 KP ID
                                #   - 真实 ID: kp_alevels_mathematics_p1_001
                                #   - 占位:    pending_kp_p1_026 (待 Phase A2 拆出)
            duration_minutes: <int>
            prerequisites: [<string>]
            objectives:
              - <string>       # 1-3 句话说明本课达成目标

mock_exams:
  - month: <int>               # 1-12
    name: <string>
    format: <string>           # paper1-p1 | paper2-p2 | full-mock
    duration_minutes: <int>
    source: <string>           # "P1 真题(2023 Jan)" | "Edexcel 官方 WMA11/01 真考"
    goal: <string>             # 这次模考的目的
    pass_threshold: <string>   # "60/75 (80%)" | "A*-A" | ...

weekly_schedule:
  total_lessons_per_week: <int>
  breakdown: ...

progress_tracking:
  total_kp_target: <int>
  current_kp_count: <int>
  completion_percent: <int>
```

---

## 4. 已建文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `mathematics_year12.yaml` | ✅ v1.0(2026-06-21) | 数学 Year 12 = P1 + P2,详尽 schema 示范 |

---

## 5. 待建文件

按用户项目优先级排:

1. `mathematics_year13.yaml` —— 数学 Year 13 = P3 + P4 + M1/S1
2. `physics_year12.yaml` —— 物理 Year 12(IGCSE 基础 + IAS 起步)
3. `physics_year13.yaml` —— 物理 Year 13
4. `chemistry_year12.yaml` + `chemistry_year13.yaml`
5. `biology_year12.yaml` + `biology_year13.yaml`
6. `further_mathematics_year13.yaml`(CAIE 9231)
7. `economics_year12.yaml` + `economics_year13.yaml`
8. `business_year12.yaml` + `business_year13.yaml`
9. `ielts_5_to_7.yaml`(雅思全程)
10. `deutsch_a1_b1.yaml`(德语 A1 → B1)
11. `deutsch_b1_c1.yaml`(德语 B1 → C1 / 德福)
12. Tier 2 副科 12 门 (各 1 个 YAML,简版)

---

## 6. 怎么用这个 YAML

### 6.1 人读
直接用 VS Code / 任意 YAML viewer 打开,清晰看到每学期每节课的内容。

### 6.2 程序读(后续)
我会在 `scripts/curriculum/` 下写脚本:
- `parse_learning_paths.py` —— 读 YAML,生成 markdown 教学计划
- `validate_learning_path.py` —— 校验 YAML schema + 检查 kp_refs 是否真存在
- `generate_scenarios.py` —— 从 YAML 自动生成 scenario JSON(关联到 KP)
- `coverage_report.py` —— 报告每 path 的 KP 覆盖率

### 6.3 跟 KP 库的关系
- KP 库定义**单条知识**(`kp_alevels_mathematics_p1_001 = 指数律`)
- Learning Path 定义**什么时候、什么课、用这些 KP**(`p1-algebra-l01-indices` 课用 KP #1-3)
- 修改 KP 库(添加新 KP、修改 explanation)→ 不影响 path
- 修改 path(调整 lesson 顺序、加新课)→ 不影响 KP 库
- **两边相互独立维护,通过 kp_refs 字段关联**

---

## 7. 下一步

我已经创建了:
1. `mathematics_year12.yaml` —— schema 完整示范,覆盖 P1 + P2 全部 13 topics / ~50 lessons
2. `README.md`(本文件)—— 解释怎么用

请用户 review `mathematics_year12.yaml` 决定:
- schema 是否 OK
- lesson 划分是否合理(每节 90 分钟,每周 4 节,32 周)
- mock_exams 时间安排是否合理
- topics 列表是否完整(P2 的 7 topics 是基于 2018+ IAL 推测,需要查证)

OK 的话,我就按同样方法继续建其他科目 + 年级。
