# Physics IAL 科元数据

> 真实 IAL 物理 6 个 unit(2018 改革后) — 本次覆盖 Unit 1-4(WPH11-WPH14,AS + A2 首段)
> 版本: v1.0  ·  2026-06-21

---

## 1. 基本信息

```yaml
subject: physics
subject_zh: 物理
exam_board: edexcel_ial
unit_prefix: WPH              # IAL Physics paper code 前缀
total_units: 6                # IAL Physics 6 个 unit (本次做 1-4)
total_papers: 6
qualification: IAL            # International A Level
specification_version: "2018" # 现行 spec(2018 改革后)
specification_url: "https://qualifications.pearson.com/en/qualifications/edexcel-international-a-levels/physics-2018.html"
```

---

## 2. 考试结构(IAL Physics 2018 spec)

### 2.1 完整 A-level 必须通过的 6 个 unit

| Unit | Code | 主题 | Weight | 形式 |
|------|------|------|--------|------|
| **Unit 1: Mechanics and Materials** | WPH11/01 | 力学与材料 | IAS 50% / IAL 25% | 1h 30m / 80 marks |
| **Unit 2: Waves and Electricity** | WPH12/01 | 波与电学 | IAS 50% / IAL 25% | 1h 30m / 80 marks |
| **Unit 3: Practical Skills in Physics I** | WPH13/01 | 实用技能 I | IAS 31.25% / IAL 12.5% | 1h 15m / 50 marks |
| **Unit 4: Further Mechanics, Fields and Particles** | WPH14/01 | 进阶力学、场、粒子 | IA2 50% / IAL 25% | 1h 45m / 90 marks |
| Unit 5: Thermodynamics, Radiation, Oscillations and Cosmology | WPH15/01 | 热力学、辐射、振动、宇宙学 | IA2 50% / IAL 25% | 1h 45m / 90 marks |
| Unit 6: Practical Skills in Physics II | WPH16/01 | 实用技能 II | IA2 31.25% / IAL 12.5% | 1h 15m / 50 marks |

> **2018 改革前后对比**:
> - 改革前 Unit 3/6 满分 40,新 spec 提到 50
> - 改革前 Unit 4/5 满分 80 / 1h 35m,新 spec 提到 90 / 1h 45m
> - 新版加了 Moments 和 Lenses;删了一些 Materials 性质
> - 教材基本沿用 2015 版 GCE 教材内容(差异小)

### 2.2 评分

- 满分 480 分(6 个 paper 加权后)
- A-level 等级: A* / A / B / C / D / E / U
- **A* 条件**: 总分 ≥ 480 **且** A2 部分(Unit 4 + 5 + 6)标准化分 ≥ 270

---

## 3. 本次覆盖范围(Unit 1-4)

### 3.1 Unit 1 (WPH11/01) — Mechanics and Materials

**Spec 章节**:
- **1.3 Mechanics**(力学)
  - Vectors and Scalars
  - Kinematics (suvat)
  - Projectile motion
  - Dynamics (Newton's laws, F=ma)
  - Moments and couples
  - Work, energy and power
  - Momentum and impulse (1D)
- **1.4 Materials**(材料)
  - Density, upthrust, Archimedes
  - Fluid pressure, flow, Bernoulli
  - Hooke's law and elastic deformation
  - Stress, strain, Young's modulus
  - Drag, terminal velocity, Stokes' law

**KP 数**: 12 个(`p1-mechanics-materials.md`)

### 3.2 Unit 2 (WPH12/01) — Waves and Electricity

**Spec 章节**:
- **2.3 Waves and Particle Nature of Light**
  - Progressive waves (basics)
  - Waves on strings and stationary waves
  - Refraction, TIR, polarisation
  - Diffraction and interference (Young's)
  - Photons and photoelectric effect
  - Wave-particle duality (de Broglie)
  - Intensity of radiation (inverse square)
- **2.4 Electric Circuits**
  - Charge, current, energy, EMF
  - Resistance, resistivity, components
  - Potential dividers, internal resistance

**KP 数**: 10 个(`p2-waves-electricity.md`)

### 3.3 Unit 3 (WPH13/01) — Practical Skills in Physics I

**Spec 章节**:
- 8 个 Core Practicals (CP1-CP8)
- 实验规划、实施、评估能力

**Core Practicals**:
1. CP1 — Acceleration of a freely-falling object
2. CP2 — Viscosity of a liquid
3. CP3 — Young modulus of a material
4. CP4 — Speed of sound in air
5. CP5 — Frequency of a vibrating string
6. CP6 — Wavelength of light (diffraction grating)
7. CP7 — Electrical resistivity of a material
8. CP8 — EMF and internal resistance

**KP 数**: 8 个(`p3-practical-skills.md`)— 每个 CP 一个 KP

### 3.4 Unit 4 (WPH14/01) — Further Mechanics, Fields and Particles

**Spec 章节**:
- **4.3 Further Mechanics**
  - Impulse and momentum (2D)
  - Circular motion
- **4.4 Electric and Magnetic Fields**
  - Electric fields (point + parallel plate)
  - Capacitance (parallel plate)
  - Charging/discharging RC circuits
  - Magnetic fields and force on a current
  - Electromagnetic induction (Faraday, Lenz)
  - Charged particles in fields
- **4.5 Nuclear and Particle Physics**
  - Quark model
  - Radioactivity and half-life
  - Mass-energy equivalence E=mc²

**KP 数**: 9 个(`p4-further-mechanics-fields-particles.md`)

---

## 4. KP 分布汇总

| Unit | Spec 章节数 | KP 数 | 主要 KP 类别 |
|------|------------|-------|--------------|
| **Unit 1** | 2 (1.3, 1.4) | **12** | 力学 7 + 材料 5 |
| **Unit 2** | 2 (2.3, 2.4) | **10** | 波 6 + 电 4 |
| **Unit 3** | 8 CP | **8** | 8 个 Core Practical |
| **Unit 4** | 3 (4.3, 4.4, 4.5) | **9** | 力学 2 + 场 6 + 粒子 1 |
| **本次总计** | 15 章节 + 8 CP | **39 KP** | (本次不做 Unit 5/6) |

> **39 个 KP 都是从 2018 spec 章节标题 + Edexcel 官方 KP 列表 + PMT by-topic QP 1:1 映射反推出来的**,不是凭空写的。

---

## 5. 已下载的 PMT 资源

### 5.1 Notes PDF(16 个,`raw_pmt/Physics_Notes/`)
- **Unit 1 Combined Notes** — 70 页 factsheet 集合(PMT 自创,不是 Edexcel 官方)
- **Unit 2 Combined Notes** — factsheet 集合
- **Unit 4 Combined Notes** — factsheet 集合
- **Unit 2/3/4 Detailed Notes**:
  - Unit 2: 2.3 Waves and Particle Nature of Light, 2.4 Electric Circuits
  - Unit 3: CP1-CP8(8 个独立 CP 笔记)
  - Unit 4: 4.3 Further Mechanics, 4.4 Electric & Magnetic Fields, 4.5 Nuclear & Particle Physics

### 5.2 By-topic QP/MS(50 个,`raw_pmt/Physics_questions/`)
- **Unit 1 Set N** — 8 topics × 2 = 16 PDFs
  - Vectors, Kinematics, Forces and Moments, Work Energy Power, Momentum, Density and Upthrust, Fluids, Hooke's Law and Young's Modulus
- **Unit 2 Set N** — 10 topics × 2 = 20 PDFs
  - Waves, Waves on Strings, Refraction/Reflection/Polarisation, Diffraction, Photons, Intensity of Radiation, Charge/Energy/Current, Resistance/Components/Resistivity, Potential Dividers/EMF/Internal Resistance
- **Unit 4 Set N** — 9 topics × 2 = 18 PDFs
  - Impulse and Momentum (×2), Circular Motion, Electric Fields, Capacitance, Magnetic Fields and EM Induction, Charged Particles in Fields, Nuclear and Particle Physics
- **Unit 3**: 无 by-topic(只有 CP detailed notes)

### 5.3 Past Papers(119 个,`raw_pmt/Physics_papers/`)
- **Unit 1**: ~30 papers × 2 (QP+MS) = 60 PDFs(2020-2024 + Specimen)
- **Unit 2**: ~30 papers × 2 = 60 PDFs
- **Unit 3**: ~29 papers × 2 = 58 PDFs
- **Unit 4**: ~30 papers × 2 = 60 PDFs

---

## 6. 前置关系

```
IGCSE Physics (4PH1 / Science Double Award)
    ↓
IAL IAS Unit 1 (Mechanics and Materials)      ← AS 阶段
    ↓
IAL IAS Unit 2 (Waves and Electricity)        ← AS 阶段
    ↓
IAL IAS Unit 3 (Practical Skills I)           ← AS 阶段(可与 U1/U2 同步)
    ↓
IAL IA2 Unit 4 (Further Mechanics, Fields, Particles)  ← A2 阶段
    ↓
IAL IA2 Unit 5 (Thermodynamics, Radiation, Oscillations, Cosmology) ← A2 阶段(暂不做)
    ↓
IAL IA2 Unit 6 (Practical Skills II)          ← A2 阶段(暂不做)
```

**考试局特点**:
- Edexcel 物理爱考**简答题 + 论述题**,需要清晰英文表述
- CAIE 物理爱考**计算题 + 实验设计**
- **A*率**(2022):物理 ~21-22%(CAIE 物理 21.1%,爱德思物理 ~22.4% 之类)

---

## 7. 关键 Source of Truth

### 7.1 官方(必引)
- **Edexcel IAL Physics Specification 2018**(PDF)
  - URL: `https://qualifications.pearson.com/en/qualifications/edexcel-international-a-levels/physics-2018.html`
  - 包含每条 KP 的官方定义、Assessment objectives
- **Edexcel IAL Physics Past Papers + Mark Scheme**(2019-2024,2018 spec)
  - 单元代码: WPH11/01, WPH12/01, WPH13/01, WPH14/01, WPH15/01, WPH16/01
  - Pearson 官方下载,PMT 镜像

### 7.2 第三方权威资源
- **Physics & Maths Tutor (PMT)**
  - URL: `https://www.physicsandmathstutor.com/physics-revision/a-level-edexcel-ial/`
  - 每个 topic 的笔记 + 视频 + 真题分类
  - 注意:物理 Combined Notes 是 factsheet 风格(独立小节随机排列),不像数学那么连贯
- **Pearson Edexcel International A Level Physics textbook**(2018 版)
  - 6 本(Unit 1-6 各一本)
  - 与旧版 GCE 2015 教材内容相似

---

## 8. KP 拆解计划

| 阶段 | 范围 | 状态 |
|------|------|------|
| Phase P-A | Unit 1 (12 KP) | ✅ Done (`p1-mechanics-materials.md`) |
| Phase P-A | Unit 2 (10 KP) | ✅ Done (`p2-waves-electricity.md`) |
| Phase P-A | Unit 3 (8 KP / CPs) | ✅ Done (`p3-practical-skills.md`) |
| Phase P-A | Unit 4 (9 KP) | ✅ Done (`p4-further-mechanics-fields-particles.md`) |
| Phase P-B | `learning_paths/physics_year12.yaml` 教学计划 | ⏳ Next |
| Phase P-C | Unit 5 (Thermodynamics/Radiation/Oscillations/Cosmology) | 视需要 |
| Phase P-C | Unit 6 (Practical Skills II) | 视需要 |
| Phase P-D | Chemistry / Biology Tier 1 | 下次 |

---

## 9. 关键提醒

- **物理 KP 比数学 KP 跨页更长**:每个 KP 包含 description + key_formulae + common_mistakes + by_topic_refs(2 个文件:QP + MS)+ past_paper_refs
- **事实性内容必须以官方 spec + Edexcel past paper 真题为锚**,不能凭印象写
- **新 spec 的特殊性**:2018 spec 比 2015 GCE spec 改了一小部分(加 Moments 和 Lenses,删了一些 Materials),教材沿用旧 GCE — 跨 spec 出题可能略有差异,但 KP 核心一致
- **本 metadata 不替代 spec**:这是索引 + 拆解说明,具体 KP 描述见 `knowledge-points/physics/` 下的 4 个文件
- **本次未做 Unit 5/6** — 用户说 "1-4",实际 IAL 物理 6 个 unit(WPH11-16)。Unit 5 + Unit 6 是 A2 进阶,如果学生要走 IAL 全科,需要后续补