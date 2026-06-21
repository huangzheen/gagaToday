# Mathematics IAL 科元数据

> 真实 IAL 单元命名(C1 → P1)+ 真实 21 门体系
> 版本: v2.0  ·  2026-06-21  ·  v2 主要修正:C1→P1 命名 + 真实 Edexcel 21 门

---

## 1. 基本信息

```yaml
subject: mathematics
subject_zh: 数学
exam_board: edexcel_ial
unit_prefix: WMA              # IAL Mathematics paper code 前缀
total_units: 5                 # IAL Mathematics 5 个 unit
total_papers: 5                # 5 个 paper(每个 unit 一个)
qualification: IAL             # International A Level
specification_version: "2024"  # 当前使用的 spec 版本
specification_url: "https://.../IAL-Mathematics-2024.pdf"  # [需查证]
```

---

## 2. 考试结构(IAL Mathematics)

### 2.1 完整 A-level 必须通过的 5 个 unit(2018 改革后命名)

| Unit | Code | Topics(粗看) | Weight | 形式 |
|------|------|--------------|--------|------|
| **Pure Mathematics 1 (P1)** | WMA11/01 | Algebra, Coordinate geometry, Sequences & series, Differentiation, Integration, Trigonometry | 1/5 | 1h 30m 笔试 |
| **Pure Mathematics 2 (P2)** | WMA12/01 | Algebra & functions, Coordinate geometry, Sequences, Trigonometry, Exponentials & logs, Calculus | 1/5 | 1h 30m 笔试 |
| **Pure Mathematics 3 (P3)** | WMA13/01 | Algebra & functions, Trigonometry, Differentiation, Integration, Numerical methods, Vectors | 1/5 | 1h 30m 笔试 |
| **Pure Mathematics 4 (P4)** | WMA14/01 | Algebra & series, Coordinate geometry, Calculus, Vectors, Differential equations | 1/5 | 1h 30m 笔试 |
| **Application 选修 1 个** | WST01/01 或 WME01/01 | Statistics 1 / Mechanics 1(可二选一) | 1/5 | 1h 30m 笔试 |

### 2.2 选修(必须从以下 2 个选 1)

- **S1 - Statistics 1**(WST01/01):数据收集、表示、概率、相关回归
- **M1 - Mechanics 1**(WME01/01):运动学、力学模型、抛体、力的平衡

> **2018 改革前的旧名**:
> - C1 (WMA01/01) → 现 P1 (WMA11/01)
> - C2 (WMA02/01) → 现 P2 (WMA12/01)
> - C3 (WMA03/01) → 现 P3 (WMA13/01)
> - C4 (WMA04/01) → 现 P4 (WMA14/01)
>
> **2024 年实际考试用 WMA11/01,不再用 WMA01/01**

### 2.3 评分

- 满分 600 分(5 个 paper × 100 + IAS / IA2 折算)
- A-level 等级: A* (480+) / A (420+) / B (360+) / C (300+) / D (240+) / E (200+)
- **A* 条件**: 总分 ≥ 480 **且** P4 + 选修(M1/S1) 等级 A*

---

## 3. P1 实际内容(从 2023 Jan 真题反推)

**2023 January WMA11/01 真题 Q1-Q11**(B站真题讲评,实际题目):

| Q | 主题 | KP 所属 |
|---|------|--------|
| Q1 | Derivative & Tangent 导数与切线 | §4 Differentiation |
| Q2 | Geometry & Rectangle 几何与矩形 | §2 Coordinate geometry |
| Q3 | Integral 积分 | §5 Integration |
| Q4 | Determinant 判别式 | §1 Algebra(quadratics) |
| Q5 | Substitution & Logarithm 代换与对数 | §1 Algebra(indices) + §5(C2 范围内) |
| Q6 | Sector & Arc 扇形与弧 | §6 Trigonometry |
| Q7 | Transformation & Linear equation 变换与一次方程 | §2 Coordinate geometry + §6(图像变换) |
| Q8 | Intersection of line and curve 直线与曲线交点 | §2 Coordinate geometry(simultaneous) |
| Q9 | Trigonometry 三角 | §6 Trigonometry |
| Q10 | Polynomial 多项式 | §1 Algebra(polynomial) |
| Q11 | Integration 应用 | §5 Integration |

**P1 真实 6 大主题**(从真题反推):
1. **Algebra** —— indices, surds, quadratics, simultaneous, inequalities, polynomials, partial fractions
2. **Coordinate geometry** —— straight line, circle, intersection, transformation
3. **Sequences and series** —— arithmetic, geometric, sigma
4. **Differentiation** —— basic derivatives, tangent, gradient
5. **Integration** —— basic integrals, constant of integration, simple applications
6. **Trigonometry** —— radians, sectors, arcs, basic trig functions

---

## 4. KP 分布估算(按真实 spec)

| Unit | 主题数 | 估算 KP 数 | 主要 topic 类别 |
|------|--------|----------|----------------|
| **P1** | 6 | ~150 | Algebra / Coordinate geometry / Sequences / Differentiation / Integration / Trigonometry |
| **P2** | 7 | ~180 | 同 P1 + Exponentials & logs(扩展) + 复杂 Differentiation/Integration |
| **P3** | 6 | ~170 | Functions / 复杂 Trigonometry / 复杂 Differentiation / Numerical methods / Vectors |
| **P4** | 6 | ~170 | Algebra & series / 复杂 Coordinate geometry / 复杂 Calculus / Differential equations |
| **S1**(选修) | 5 | ~120 | Statistics & probability |
| **M1**(选修) | 5 | ~120 | Mechanics & kinematics |
| **总计** | ~30 | **~910 KP** | (修正:之前我估 350,实际更细) |

> 数字粗算。具体拆解以 `knowledge-points/mathematics/` 下的实际 KP 数量为准。

---

## 5. P1 §1 Algebra KP 修正版

`knowledge-points/mathematics/p1-algebra.md` 文件已重命名,内容仍为 §1 Algebra 25 个 KP。

**真实 P1 §1 应包含的 topic**(从 2018+ 真实 spec 反推):
- (a) Laws of indices(指数律)
- (b) Surds(根式化简与运算)
- (c) Quadratic functions and equations(二次)
- (d) Simultaneous equations(联立)
- (e) Inequalities(不等式)
- (f) Polynomial division(多项式除法)
- (g) Factor theorem(因子定理)
- (h) Graphs of cubic / quartic / reciprocal functions(高次函数图像)
- (i) Algebraic proof(代数证明)
- (j) Partial fractions(部分分式)

**当前 p1-algebra.md 已覆盖 (a)-(j) 全 10 个 sub-topic,25 KP**。**但**:
- 命名需改:`c1-algebra` → `p1-algebra`(已做)
- [REVIEW_NEEDED] 标注需要逐条查证(待做)
- past_paper_ref 需要真实查证(待做)

---

## 6. 前置关系

```
IGCSE Mathematics (Mathematics A or B 4MA1)
    ↓
IAL IAS P1
    ↓
IAL IAS P2
    ↓
IAL IAS P3
    ↓
IAL IA2 P4
    ↓
IAL Application 选修 (S1 or M1)
    ↓
[可选] CAIE 9231 Further Mathematics(IAL 不提供 FP)
```

**注意**: IAL Mathematics ≠ IGCSE Mathematics。中国学生通常:
- 国内初三毕业 → 直接进 IAL IAS(用 IGCSE 基础补充)
- 国内高一/二 → 进 IAL IAS 全部 / 直接 IAL(跳 IAS)

---

## 7. 关键 Source of Truth

### 7.1 官方(必引)
- **Edexcel IAL Mathematics Specification 2024**(PDF, 需查证)
  - 包含每条 KP 的官方定义
  - 包含每章 Assessment objectives
  - 包含 past paper 出题格式
- **Edexcel IAL Mathematics Past Papers + Mark Scheme**(2019-2024, 改革后)
  - 单元 **WMA11/01, WMA12/01, WMA13/01, WMA14/01, WST01/01, WME01/01**
  - Pearson 官方下载

### 7.2 第三方权威资源(必引至少 1 个)
- **Physics & Maths Tutor (PMT)** —— 英国最全的免费 A-level 资源站
  - URL: `https://www.physicsandmathstutor.com/maths-revision/`
  - 每个 topic 的笔记 + 视频 + 真题分类
  - 2024 改革后:PMT 用 "Pure – Year 1" / "Pure – Year 2" 命名(对应 P1-P4)
- **Savemyexams** —— 重点大学的总结
  - URL: `https://www.savemyexams.com/`
- **Znotes** —— 学生笔记整理
  - URL: `https://znotes.io/`

### 7.3 教材(辅助,非必须)
- **Pearson Edexcel International A Level Mathematics**(官方教材)
  - P1 / P2 / P3 / P4 / S1 / M1 各一本
  - 旧版叫 "Core Mathematics",2018 改革后叫 "Pure Mathematics"
  - 不强制购买,免费资源够用

---

## 8. KP 拆解计划(修正版)

| 阶段 | 范围 | 完成时间 | 状态 |
|------|------|---------|------|
| Phase A1 | P1 §1 Algebra(模板) | 本周 | ✅ 重命名完成,内容待 review |
| Phase A2 | **P1 §1-6 全 6 主题**(~150 KP) | 1-2 周 | 下一步 |
| Phase A2 | P2 / P3 全部 topic | 1-2 周 | |
| Phase A3 | P4 + S1 / M1 | 3-6 周 | |
| Phase A3 | Physics / Chemistry / Biology Tier 1 主科 | 3-6 周 | |
| Phase A4 | Tier 2 副科 12 门 | 6-12 周 | |

---

## 9. 游戏化设计预留(同前)

数学 KP 的游戏化,可能形态:
- **单元关卡**:每个 unit 一个"主题关卡群",如:
  - P1 Algebra → "密码破译"(解方程破密码)
  - P1 Coordinate geometry → "航海家"(用坐标定位)
  - P1 Differentiation → "极速赛车"(求瞬时速度)
- **战斗关卡**:NPC 出题,答对得分数
- **解锁条件**:前置 KP 掌握(用 progress tracker 检测)

具体关卡设计在 Phase B(基于 KP 写关卡剧本)做。

---

## 10. Subject 元数据模板说明

其他 20 门学科都建一份 `{subject}.md`,结构同本文件。Tier 1 优先建,Tier 2 后续建。

---

OK,数学科元数据 v2.0 修正完。**C1 → P1 是 2018 改革后的真实命名**。
