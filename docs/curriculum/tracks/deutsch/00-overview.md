# Deutsch 德语轨道总览

> 德语(德福)知识库总览
> 版本: v1.0  ·  2026-06-21
> **本轨道是项目原始轨道,已有 SCRIPT_METHODOLOGY 和完整 scenario 体系,本文件作为 curriculum 知识库的对接说明**

---

## 1. 与现有文档的关系

德语轨道**沿用**以下现有文档的内容:
- [../PROPOSAL.md](../../PROPOSAL.md) v2.0
- [../ARCHITECTURE.md](../../ARCHITECTURE.md) v1.0
- [../SCRIPT_METHODOLOGY.md](../../SCRIPT_METHODOLOGY.md) v2.0
- [../MVP_TASKS.md](../../MVP_TASKS.md) v2.0
- [../API_STACK.md](../../API_STACK.md) v1.0

**本文件**只补充 curriculum 知识库视角的内容,不重复上述文档。

---

## 2. 目标设定

| 项 | 内容 |
|----|------|
| **考试** | TestDaF(德福) |
| **目标等级** | TDN 4(5 项中 4 项) |
| **对齐欧标** | B2-C1 |
| **理由** | 申请德国大学普遍要求 TDN 4 / 5 |

---

## 3. Source of Truth(权威资源)

### 3.1 官方(必引)
- **TestDaF Modellsatz**(官方模拟题,免费下载)
- **TestDaF Aufgabenbeschreibung**(题型说明,官方)
- **Goethe-Zertifikat C1 Modellsatz**(辅助,Goethe C1 与 TestDaF TDN 5 等价)
- **欧洲语言共同参考框架 CEFR**(C1 = 德福 TDN 5,B2 = 德福 TDN 4)

### 3.2 教材(主流)
| 阶段 | 教材 | 理由 |
|------|------|------|
| A1 | *Menschen A1*(Hueber) | 入门首选,场景化 |
| A2 | *Menschen A2* | 续 A1 |
| B1+ | *Aspekte B1+* | 中级衔接 |
| B2 | *Aspekte B2* | 德福备考 |
| C1 | *Mit Erfolg zum TestDaF* | 德福专项 |
| 词汇 | *Menschen / Aspekte* 配套词汇书 | 系统性 |

### 3.3 第三方资源
| 资源 | 用途 | 链接 |
|------|------|------|
| **Deutsche Welle (DW)** | 免费视频/音频/课程 | dw.com/deutschlernen |
| **Goethe-Institut** | 课程 + 考试信息 | goethe.de |
| **Schubert Verlag** | 教材配套资源(在线练习) | schubert-verlag.de |
| **Lingolia** | 语法讲解 + 练习 | deutsch.lingolia.com |
| **Mein Deutschebuch** | 免费语法 + 练习 | mein-deutschebuch.de |

---

## 4. KP 拆解规划(沿用现有 + 补充)

### 4.1 已有 KP(从 scenario JSON 中提取)

`backend/app/data/scenarios/` 下的 scenario JSON 已经引用了 KP,需要**回填**到 `knowledge-points/` 目录。

例: `berlin_bahnhof_01.json` 中的 `learning_objectives.expressions` 5 条对应 5 个 KP。

### 4.2 待补 KP(按 CEFR 等级)

| CEFR | 阶段 | KP 数量估算 | 对应教材 |
|------|------|------------|---------|
| **A1** | 入门 | ~150 KP | Menschen A1 (12 Lektionen × 12 KP 平均) |
| **A2** | 基础 | ~150 KP | Menschen A2 |
| **B1** | 中级 | ~150 KP | Aspekte B1+ |
| **B2** | 中高级 | ~150 KP | Aspekte B2 |
| **C1** | 高级 / 德福 | ~100 KP | Mit Erfolg zum TestDaF |
| **总计** | | **~700 KP** | |

### 4.3 KP 分类(德语)

按 `KP_SCHEMA.md` § 3.1 的枚举:
- `expression`:表达 / 句型
- `grammar`:语法
- `vocabulary`:词汇
- `culture`:文化
- `phonetics`:发音
- `strategy`:学习策略

---

## 5. KP 与 scenario 的关系(回填方案)

### 5.1 当前状态
- scenario JSON 已有 `learning_objectives` 字段
- 但里面是**内联的知识列表**,没有引用 KP ID

### 5.2 改进方向
1. 把每个 scenario 的 `learning_objectives` 拆成 KP,放进 `knowledge-points/`
2. scenario JSON 改为引用 KP ID:
   ```json
   {
     "learning_objectives_kp_refs": [
       "kp_deutsch_a1_007",
       "kp_deutsch_a1_012"
     ]
   }
   ```
3. 这样**改 KP 一次,所有引用它的关卡自动同步**

### 5.3 工具
- `scripts/curriculum/extract_kps_from_scenarios.py` —— 从 scenario JSON 自动提取 KP 候选项
- 人工 review 后入库

---

## 6. 学习路径(A1 → 德福 TDN 4)

沿用 SCRIPT_METHODOLOGY.md 的规划:

| 阶段 | 时长 | 目标 | 教材 | 城市 |
|------|------|------|------|------|
| **A1** | 12-16 周 | 入门生活场景 | Menschen A1 | 柏林 |
| **A2** | 12-16 周 | 扩展生活场景 | Menschen A2 | 柏林 + 慕尼黑 |
| **B1** | 16-20 周 | 学术 / 抽象话题 | Aspekte B1+ | 慕尼黑 + 汉堡 + 科隆 |
| **B2** | 16-20 周 | 德福基础 | Aspekte B2 | 5+ 城市 |
| **C1 / 德福** | 12-16 周 | 德福 TDN 4-5 | Mit Erfolg zum TestDaF | 5+ 城市 + 留学场景 |

**总时间**:**约 18-24 个月**(每周 15-20 小时)

---

## 7. 当前进度

- ✅ `00-overview.md`(本文件)
- ⏳ `knowledge-points/` 下 KP 文件 —— **从已有 scenario 回填**,Phase A2 启动
- ⏳ `textbooks/` 下教材结构 —— Phase A2 启动
- ⏳ `scenarios/` 软链 → `backend/app/data/scenarios/` —— **现在做**

---

## 8. 与游戏化的关系

德语是项目**核心**,所有游戏关卡优先建德语:
- "走遍德国"地图 = 德语关卡集合
- NPC 角色 = 德语对话对象
- 反馈卡 = 德语发音 + 语法评估

其他两个轨道(雅思 / A-levels)作为**辅助**:
- 雅思口语 → 类似德语对话模式(英文 NPC)
- A-levels → 题库训练 + 概念讲解(用游戏任务形式包装)

详见 `routes/apply-to-germany.md` § 5"游戏化整合"。

---

OK,德语总览到此。下一步:**从现有 scenario JSON 回填 KP 到 knowledge-points/**。
