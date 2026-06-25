# 成就系统 Achievement System

> 三轨道学习 RPG 的成就设计总纲
> 版本: v1.0  ·  2026-06-21
> 作者: Mavis(基于用户初版需求扩展)

---

## 1. 设计目标与原则

### 1.1 目标

让玩家在三类动机的驱动下持续玩下去:

| 动机 | 对应成就类 | 心理满足 |
|------|----------|---------|
| **想拿 offer** | 学习类 L | "我又拿了个 A*,稳了" |
| **想到处走走** | 探索类 E | "哦原来德国还有这种地方" |
| **想证明自己** | 元成就 M | "我居然坚持了 100 天" |

### 1.2 设计原则

1. **三轴交叉加权** —— 学习是主线(80% XP 来源),探索和元成就补足游戏性
2. **进度可见,缺口可见** —— 每个成就旁边显示"已解锁 X/Y",让玩家知道还差多少
3. **软性硬性并存** —— 软性"集邮"成就给收集欲,硬性"达成 A*"给真实结果
4. **学习嵌入探索** —— 每个新城市解锁 = 同时获得 5-10 个德语 KP + 3-5 个探索打卡
5. **彩蛋要有** —— 至少 10% 是隐藏成就(无进度条,纯惊喜)
6. **跟申请强挂钩** —— 凡是"申请德国可能用得上"的内容,都加成就有奖励加成

---

## 2. 三大类总览

| 类别 | 编号 | 子类数 | 成总数 | 主 XP 来源 |
|------|-----|-------|-------|----------|
| **Lernen 学习** | L | 4 | ~250 | 主线 |
| **Entdecken 探索** | E | 11 | ~1500 | 收集 |
| **Meta 元** | M | 5 | ~80 | 习惯 |
| **合计** | - | 20 | **~1830** | - |

**ID 规范**:`{类别}-{子类}-{编号}-{稀有度}`
- 示例:`L-MATH-P1-STAR` / `E-MUSEUM-100` / `E-CASTLE-NEUSCHWANSTEIN` / `M-STREAK-100` / `H-LIEBE`

---

## 3. 学习类 L — Lernen(主轨道,~250 个)

> **设计要点**:跟 curriculum 知识库强挂钩,每个成就背后是 N 个 KP 完成。
> 解锁 = KP 全过 + 模拟考达到分数 + 关联关卡通关。

### L1 德语 Deutsch(~80 个)

#### L1.1 CEFR 等级里程碑(6 个)
| ID | 名称 | 条件 | 稀有度 |
|----|------|-----|-------|
| L-DE-A1 | 初级握手 A1 | A1 全部 KP 完成 | 铜 |
| L-DE-A2 | 日常对话 A2 | A2 全部 KP | 银 |
| L-DE-B1 | 流利交流 B1 | B1 全部 KP | 银 |
| L-DE-B2 | 德福入门 B2 | B2 全部 KP | 金 |
| L-DE-C1 | 学术德语 C1 | C1 全部 KP | 钻石 |
| L-DE-C2 | 母语水平 C2 | C2 全部 KP | 白金(传说) |

#### L1.2 TestDaF 专项(10 个)
- L-TD-LESEN-3/4/5(阅读 TDN 3/4/5)
- L-TD-HOEREN-3/4/5(听力)
- L-TD-SCHREIBEN-3/4/5(写作)
- L-TD-MUENDLICH-3/4/5(口语)
- L-TD-ALL-5(全 4 项 TDN 5,传说)

#### L1.3 教材关卡(每教材一本 ~20 关,共 ~50 个)
- L-教材-MENSCHEN-A1 / A2 / B1 ...
- L-教材-STUDIO-DAF-A1 / B1 ...

#### L1.4 德语专项技能(14 个)
- 名词性别大满贯(der/die/das 500 道全对)
- 完成 100 个 Perfekt 句
- 听写准确率 95%+
- 模拟面试 Pass
- 写完 5 篇留学动机信
- ...

### L2 雅思 IELTS(~60 个)

#### L2.1 4 项分项(每项 4 等级,共 16 个)
- L-ILTS-LISTEN-6.5 / 7.0 / 7.5 / 8.0
- L-ILTS-READ-6.5 / 7.0 / 7.5 / 8.0
- L-ILTS-WRITE-6.5 / 7.0 / 7.5 / 8.0
- L-ILTS-SPEAK-6.5 / 7.0 / 7.5 / 8.0

#### L2.2 总分里程碑(5 个)
- L-ILTS-OVERALL-6.0 / 6.5 / 7.0 / 7.5 / 8.0

#### L2.3 写作 Task 1/2 专项(8 个)
- L-WRITING-T1-GRAPH / CHART / DIAGRAM / MAP
- L-WRITING-T2-OPINION / DISCUSSION / PROBLEM / TWO-PART

#### L2.4 口语话题全过(20 个)
- 1-20 套口语题库各 1 个

### L3 A-levels(21 科 × 平均 8 个 = ~170 个)

> **学科列表**(基于 curriculum/tracks/alevels/00-overview.md 真实数据,21 门):
> Mathematics / Physics / Chemistry / Biology / Economics / Business / Accounting / IT / English Language / English Literature / History / Geography / Psychology / Law / French / German / Spanish / Arabic / Greek(18 门 Edexcel IAL 主推) + Further Maths(CAIE 9231) + Computer Science(CAIE 9618) + Music/Art/Drama/Religious Studies(CAIE,选学)

#### L3.1 学科等级(每科 4 个等级,共 ~84 个)
- L-{SUBJ}-U-(AS 完成)
- L-{SUBJ}-A-(A-level 完整)
- L-{SUBJ}-A-STARS(A*)
- L-{SUBJ}-MASTER(全 KP + 5 套 past paper 90%+)

示例:
- L-MATH-P1-STAR(数学 P1 拿 A*)
- L-PHYS-P1-PASS(物理 P1 Pass)
- L-ECON-A-MASTER(经济 A-level 满分级)

#### L3.2 单元级(每科 5-6 单元 × 4 等级 = ~480 个,选做)
- L-MATH-P1-COMPLETE
- L-MATH-P2-COMPLETE
- L-MATH-P3-COMPLETE
- L-MATH-P4-COMPLETE
- L-MATH-S1-COMPLETE
- L-MATH-M1-COMPLETE

#### L3.3 跨学科(10 个)
- L-STEM-ALL-A(STEM 4 科全 A*)
- L-HUMANITIES-MASTER(人文类 5 科全 A)
- L-LANGUAGES-3(英德法西 4 选 3 全 A)
- L-EPQ-COMPLETE(EPQ 拓展项目)

### L4 学习习惯(~30 个)

> **核心作用**:让"学习行为"本身有回报,避免刷分。

#### L4.1 连续打卡
- L-STREAK-3 / 7 / 30 / 100 / 365 天

#### L4.2 复习
- L-REVIEW-100(累计复习 100 张错题卡)
- L-REVIEW-WEEK(连续 7 天复习)
- L-MASTERY-CARD(同一张错题卡复习 5 次到全对)

#### L4.3 模拟考
- L-MOCK-FIRST(完成第 1 套模拟考)
- L-MOCK-10(完成 10 套)
- L-MOCK-IMPROVE(分数比上一次提升 10%)

#### L4.4 时间投入
- L-HOUR-10(累计学习 10 小时)
- L-HOUR-100(累计 100 小时)
- L-MARATHON(单次学习 4 小时)

---

## 4. 探索类 E — Entdecken(核心游戏性,~1500 个)

> **设计要点**:**这是游戏的灵魂**。探索类成就是 RPG 地图点亮、百科卡、城市征服的载体。
> 每个城市解锁 = N 个德语 KP + N 个探索打卡 + 1 个城市徽章。
> **收集狂 + 实用知识**双满足。

### 4.1 探索大类速览

| ID | 大类 | 打卡点 | 跟学习关联 |
|----|------|-------|----------|
| E1 | Geographie 地理 | ~250 | 中学地理、气候、地形 |
| E2 | Kultur 文化建筑 | ~280 | 历史、艺术史 |
| E3 | Genuss 美食美酒 | ~250 | 生物(发酵)、化学、农业 |
| E4 | Verkehr 交通 | ~120 | 工程、地理 |
| E5 | Brauchtum 风俗节庆 | ~110 | 文化、人类学 |
| E6 | Sport 体育 | ~150 | 健康、PE、商业 |
| E7 | Alltag 日常生活 | ~150 | **最实用**——出国前心理准备 |
| E8 | Bildung 学术 | ~120 | **跟申请强绑定** |
| E9 | Design 创意设计 | ~100 | 艺术生专属 |
| E10 | Geschichte 历史 | ~110 | 历史课 |
| E11 | Sprache 语言文化 | ~150 | 德语学习本身 |

---

### E1. Geographie 地理(~250 个)

#### E1.1 Bundesländer 16 州(16 个)
- E-LAND-BW / BY / BE / BB / HB / HH / HE / MV / NI / NW / RP / SL / SN / ST / SH / TH
- 一次性集齐:E-LAND-ALL(稀有度:钻石,奖励"Deutschlandkenner"称号)

#### E1.2 Städte 主要城市(50 个)
- **百万级 4 个**:Berlin / Hamburg / München / Köln
- **50-100 万 10 个**:Frankfurt / Stuttgart / Düsseldorf / Leipzig / Dortmund / Essen / Bremen / Dresden / Hannover / Nürnberg
- **历史文化名城 36 个**:Heidelberg / Rothenburg / Lübeck / Quedlinburg / Bamberg / Weimar / Trier / Marburg / Göttingen / Tübingen / Freiburg / Regensburg / Würzburg / Passau / Augsburg / Mainz / Koblenz / Bonn / Aachen / Münster / Celle / Wismar / Stralsund / Rostock / Schwerin / Potsdam / Dessau / Weimar / Jena / Erfurt / Eisenach / Wittenberg / Meissen / Görlitz / Bautzen / Bayreuth

**彩蛋成就**:`E-CITY-BERLIN-WALL`(柏林墙徒步,3 段,12 公里) / `E-CITY-LICHTENBERG`(在柏林 Lichtenberg 区找到马克思-恩格斯广场)

#### E1.3 Sehenswürdigkeiten 100 景点(用户原本想的 ✓,扩展到 100)
- **城堡/宫殿 25 个**:新天鹅堡 / 霍亨索伦堡 / 海德堡城堡 / 林德霍夫宫 / 宁芬堡 / 申博恩宫殿 / 维尔茨堡官邸 / 布吕尔的奥古斯塔斯堡 / 莫里茨堡 / 什未林城堡 / 路德维希堡 / 韦茨拉尔/无忧宫 ...
- **教堂/大教堂 20 个**:科隆大教堂 / 乌尔姆敏斯特 / 亚琛大教堂 / 施派尔大教堂 / 班贝格大教堂 / 弗赖堡敏斯特 / 雷根斯堡大教堂 / 圣托马斯教堂(巴赫墓) / 托马斯教堂 / 圣米迦勒教堂 / 圣母教堂(德累斯顿) ...
- **自然奇观 25 个**:国王湖 / 吕根岛白垩崖 / 黑森林 / 莱茵河谷 / 多瑙河 / 阿尔卑斯山楚格峰 / 北海海岸 / 波罗的海 / 萨克森小瑞士 / 莱茵瀑布 / 米斯巴赫沼泽 / 瓦茨曼峰 ...
- **现代地标 20 个**:柏林国会大厦 / 勃兰登堡门 / 电视塔 / 柏林墙东边画廊 / 包豪斯档案馆 / 宝马世界 / 大众汽车城(Autostadt) / 杜塞尔多夫媒体港 / 慕尼黑宝马世界 / 法兰克福商业银行大厦(生态建筑) ...
- **历史遗址 10 个**:罗马边界 Limes / 罗马-日耳曼博物馆(科隆) / 条顿堡森林(Varusschlacht) / 瓦尔特堡(路德翻译圣经) / 拉文斯布吕克集中营 ...

**E-SEHENS-100 集齐成就**(钻石,稀有度仅次于白金)

#### E1.4 UNESCO-Welterbe 联合国世界遗产(52 个)
- E-WELT-001 至 E-WELT-052
- **E-WELT-ALL**(集齐 52 个,稀有度:白金)
- 单独抽 5 个"必看":科隆大教堂 / 罗马边界 / 博物馆岛 / 瓦尔特堡 / 蒙绍(Monschau) / 赖兴瑙岛 / 奎德林堡 / 拉默尔斯贝格矿

#### E1.5 Naturschauplätze 自然奇观精选 30 个
- 国王湖 / 吕根岛 / 北海 / 黑森林 / 巴伐利亚森林 / 阿尔卑斯山前沿 / 多瑙河 ...

---

### E2. Kultur 文化建筑(~280 个)

> 跟你原本想的"博物馆探索"是同一大类,但扩展到 5 个子类,让打卡更丰富。

#### E2.1 Museen 博物馆 50 个
- 博物馆岛 5 个(柏林):佩加蒙 / 新博物馆 / 老国家美术馆 / 博德博物馆 / 旧国家画廊
- 德意志博物馆(慕尼黑,科技)
- 德国历史博物馆
- 包豪斯档案馆
- 奔驰博物馆 / 宝马博物馆 / 大众汽车城(Autostadt)
- 墙博物馆(柏林墙)
- 犹太博物馆(柏林)
- 德国足球博物馆
- 巧克力博物馆(科隆)
- 香水博物馆(科隆)
- 体育与奥运博物馆(科隆)
- 罗马-日耳曼博物馆
- 路德维希博物馆(科布伦茨)
- 绿穹珍宝馆(德累斯顿)
- 老绘画大师馆 / 新大师馆(德累斯顿)
- 包豪斯博物馆(魏玛)
- 歌德故居 / 席勒故居
- 巴赫故居(爱森纳赫)
- 贝多芬故居(波恩)
- 贝多芬-瓦格纳-李斯特 联动:特里尔马克思故居 / 莱比锡巴赫 / 拜罗伊特瓦格纳故居
- 阿尔卑斯山博物馆
- 海洋博物馆(斯特拉斯松德)
- 民族学博物馆
- 通讯博物馆(纽伦堡)
- 玩具博物馆(纽伦堡)
- 德国卫生博物馆(德累斯顿)
- 欧洲文化博物馆(柏林)
- 装饰艺术博物馆
- 现代艺术博物馆
- 摄影博物馆
- 漫画博物馆
- 啤酒博物馆(慕尼黑)

**E-MUSEUM-50 集齐成就**(钻石)

#### E2.2 Schlösser & Burgen 城堡宫殿 100 个
- **必去 25 个**:新天鹅堡 / 老天鹅堡 / 林德霍夫宫 / 宁芬堡 / 海德堡 / 霍亨索伦 / 维尔茨堡 / 什未林 / 路德维希堡 / 申博恩 / 莫里茨堡 / 莫里茨堡 / 布吕尔 / 韦茨拉尔 / 韦斯特城堡 / 阿沙芬堡 / 韦尔尼格罗德 / 韦尔费尔施塔特 / 韦尔贝尔斯海姆 / 韦尔海姆斯多夫 ...
- 选 100 个:从德国 25000+ 城堡里挑 100 个有故事的

#### E2.3 Kirchen & Dome 教堂大教堂 30 个
- 科隆大教堂 / 乌尔姆敏斯特 / 亚琛 / 施派尔 / 班贝格 / 弗赖堡 / 圣斯蒂芬大教堂(维也纳?不,这是奥地利的)
- 维尔茨堡大教堂 / 美因茨大教堂 / 法兰克福大教堂 / 特里尔大教堂 / 帕德博恩大教堂
- 圣托马斯教堂(巴赫) / 圣十字教堂 / 圣米迦勒教堂 / 圣母教堂 / 海德堡圣灵教堂

#### E2.4 Bauhaus 包豪斯建筑 20 个
- E-BAUHAUS-001 至 E-BAUHAUS-020
- **E-BAUHAUS-ALL 集齐**(钻石)
- 单点 5 个:魏玛包豪斯博物馆 / 德绍包豪斯 / 耶拿艺术与音乐大学 / 柏林包豪斯档案馆 / 乌尔姆设计学院(HfG Ulm,包豪斯继承者)

#### E2.5 Konzerne 企业总部 30 个
> **跟商业/经济 A-levels 联动,让学生在打卡中理解企业**
- **汽车 8 个**:奔驰(斯图加特) / 宝马(慕尼黑) / 大众(沃尔夫斯堡) / 奥迪(英戈尔施塔特) / 保时捷(斯图加特) / 欧宝(吕塞尔斯海姆) / 博世(斯图加特) / 采埃孚(腓特烈港)
- **工业 8 个**:西门子(慕尼黑) / SAP(沃尔多夫) / 蒂森克虏伯(埃森) / 巴斯夫(路德维希港) / 拜耳(勒沃库森) / 赢创(埃森) / 林德(慕尼黑) / 通快(迪琴根)
- **消费品 6 个**:汉高(杜塞尔多夫) / 拜尔斯道夫(汉堡) / 阿迪达斯(黑措根奥拉赫) / 彪马(黑措根奥拉赫) / 雨果博斯(麦琴根) / 麦德龙(杜塞尔多夫)
- **金融 4 个**:德意志银行(法兰克福) / 安联(慕尼黑) / 慕尼黑再保险 / 商业银行
- **物流/媒体 4 个**:DHL(波恩) / 贝塔斯曼(居特斯洛) / 阿克塞尔·施普林格(柏林) / 杜伊斯堡港(世界最大内河港)

**E-KONZERN-30 集齐**(钻石,奖励"Mittelstandsexperte"称号,对申请商业/经济专业超有用)

#### E2.6 Berühmte-Häuser 名人故居 50 个
> **把历史人物和地点挂钩,学历史+地理双满足**
- **音乐家 15 个**:Bach(爱森纳赫/莱比锡) / Beethoven(波恩) / Mozart(曾住奥格斯堡+曼海姆) / Wagner(莱比锡) / Brahms(汉堡) / Schumann(茨维考) / Händel(哈雷) / Strauss(维也纳?不)/ Mendelssohn(莱比锡) / Schumann-Clara(莱比锡) / Liszt(魏玛) / Reger(魏登) / Orff(慕尼黑) / Henze(萨尔布吕肯)
- **哲学家 10 个**:Kant(柯尼斯堡,现加里宁格勒) / Hegel(斯图加特) / Marx(特里尔) / Engels(巴门) / Nietzsche(萨克森地区) / Heidegger(梅斯基尔希) / Schopenhauer(但泽) / Leibniz(莱比锡) / Fichte(拉门瑙) / Schiller(路德维希堡)
- **科学家 10 个**:Einstein(乌尔姆) / Planck(基尔) / Heisenberg(维尔茨堡) / Gauss(不伦瑞克) / Leibniz(同上) / Fraunhofer(斯特劳宾) / Röntgen(伦琴) / Helmholtz(波茨坦) / Huber(慕尼黑) / Benz(卡尔斯鲁厄)
- **文学家 10 个**:Goethe(美因河畔法兰克福/魏玛) / Schiller(路德维希堡) / Heine(杜塞尔多夫) / Thomas Mann(吕贝克) / Kafka(布拉格?不)/ 格林兄弟(卡塞尔) / 托马斯·曼 / 黑塞(卡尔夫/蒙塔尼奥拉) / 雷马克(奥斯纳布吕克) / 聚斯金德(慕尼黑)
- **画家 5 个**:Dürer(纽伦堡) / Cranach(威丁堡) / Holbein(奥格斯堡) / Beckmann(莱比锡) / Richter(德累斯顿)

**E-PERSON-50 集齐**(钻石,奖励"Geisteskenner"称号)

---

### E3. Genuss 美食美酒(~250 个)

> 跟你原本想的"美食探索"是同一大类,扩展到 6 个子类。

#### E3.1 Regionalküche 地方代表菜 16 道
- E-GERICH-BW:Maultaschen(施瓦本馅饺)
- E-GERICH-BY:Schweinshaxe(慕尼黑烤猪肘)+ Weißwurst
- E-GERICH-BE:Currywurst(柏林咖喱香肠)
- E-GERICH-HH:Labskaus(汉堡水手餐)
- E-GERICH-NW:Rheinischer Sauerbraten(莱茵酸牛肉)
- E-GERICH-HE:Frankfurter Grüne Soße(法兰克福绿酱)
- E-GERICH-HB:Knipp(不来梅燕麦肠)
- E-GERICH-NI:Schwarzwurzeln(黑森地区,芦笋)
- E-GERICH-RP:Pfälzer Saumagen(普法尔茨)
- E-GERICH-SL:Lywäwwel(Lorraine 边界)
- E-GERICH-SN:Sächsische Quarkkeulchen(萨克森奶酪球)
- E-GERICH-ST:Harzer Käse(哈尔茨奶酪)
- E-GERICH-SH:Birnen, Bohnen und Speck(什列斯维希)
- E-GERICH-MV:Baltische Küche(波罗的海)
- E-GERICH-BB:Beelitzer Spargel(比利茨白芦笋)
- E-GERICH-TH:Thüringer Klöße(图林根丸子)
- E-GERICH-HB:Bremer Klaben(不来梅圣诞面包)

**E-KÜCHE-16 集齐**(钻石,奖励"Feinschmecker"称号)

#### E3.2 Bier 啤酒 50 种
- 按啤酒厂划:Augustiner / Paulaner / Hofbräu / Hacker-Pschorr / Spaten-Franziskaner(慕尼黑 6 大)
- 按种类划:Pils / Helles / Export / Märzen / Bock / Doppelbock / Weizen / Kölsch / Alt / Berliner Weisse / Gose / Schwarzbier / Rauchbier / Kellerbier
- 选 50 种具体品牌
- **隐藏成就 `H-BIER-1L`**:在啤酒节连续喝 1L
- **E-BIER-50 集齐**(钻石)

#### E3.3 Wein 葡萄酒 13 个产区
- E-WEIN-001 至 E-WEIN-013
- Ahr / Baden / Franken / Hessische Bergstraße / Mittelrhein / Mosel / Nahe / Pfalz / Rheingau / Rheinhessen / Saale-Unstrut / Sachsen / Württemberg
- **E-WEIN-ALL 集齐**(钻石,奖励"Weinkenner"称号)

#### E3.4 Brot 面包 30 种
> 德国有 3000+ 种面包,选 30 种代表性的
- Pumpernickel(西发里亚黑面包) / Roggenbrot / Vollkornbrot / Bauernbrot / Dinkelbrot / Laugenbrezel / Brötchen ...
- **E-BROT-30 集齐**(金,奖励"Bäckermeister"称号)

#### E3.5 Wurst 香肠 30 种
> 德国有 1500+ 种香肠
- Bratwurst(纽伦堡/图林根/库伦堡/法兰克福) / Currywurst / Weißwurst / Bockwurst / Blutwurst / Leberwurst / Mettwurst / Knacker / Wiener ...
- **E-WURST-30 集齐**(金)

#### E3.6 Weihnachtsmarkt-Snacks 圣诞市集小吃 20 种
- Bratwurst / Reibekuchen / Schmalzkuchen / Lebkuchen / Stollen / Glühwein / Kinderpunsch / Maronen / Schokofrüchte / Döner / Crêpes ...
- **E-WEIHNACHT-SNACKS-20 集齐**(银)

---

### E4. Verkehr 交通(~120 个)

> 跟你原本想的"火车站探索"是同一大类,扩展到 5 个子类。

#### E4.1 Bahnhöfe 火车站 50 个
- **必打卡 10 个**:Berlin Hbf / Hamburg Hbf / München Hbf / Frankfurt(Main)Hbf / Köln Hbf / Stuttgart Hbf / Hannover Hbf / Düsseldorf Hbf / Nürnberg Hbf / Leipzig Hbf
- **历史名站 10 个**:Heidelberg Hbf(老车站) / Kassel-Wilhelmshöhe(山地车站) / Ahrweiler(老站) / Wuppertal(悬挂列车) / Dresden-Neustadt(老站) / Lübeck Hbf / Meiningen / Freiburg(老站) / Bad Schandau(萨克森小瑞士门户) / Monschau(老站)
- **文化 10 个**:Düsseldorf-Bilk(靠近媒体港) / Essen Hbf(鲁尔区) / Duisburg Hbf(世界最大内河港) / Wolfsburg Hbf(大众城门口) / Ingolstadt Hbf(奥迪城) / Regensburg Hbf(UNESCO 老城) / Bamberg Hbf(UNESCO 老城) / Passau Hbf(多瑙河) / Lindau Hbf(博登湖) / Westerland(北海)
- **特殊 20 个**:U-Bahn 经典站 / S-Bahn 山地站 / 边境站(已关闭)/ 改建的车站
- **E-BAHNHOF-50 集齐**(钻石)

#### E4.2 Flughäfen 机场 30 个
- 10 大机场 + 20 个支线
- **E-FLUGHAFEN-30 集齐**(钻石)

#### E4.3 Themenstraßen 主题公路 10 条
> 德国有 150+ 条"度假路线"(Ferienstraßen),选 10 条最有故事
- 浪漫之路 Romantische Straße
- 童话之路 Deutsche Märchenstraße
- 城堡之路 Burgenstraße
- 黑森林高地黑森林路
- 德国椴树大道
- 阿尔卑斯之路
- 莱茵河浪漫之路
- 半木结构之路 Deutsche Fachwerkstraße
- 罗马边界之路 Limesstraße
- 玻璃之路 Glasstraße
- **E-STRASSE-10 集齐**(金,奖励"Reisender"称号)

#### E4.4 Brücken 著名桥梁 20 个
- 科尔布兰特桥(科隆动物园站) / 莱茵河大桥数座 / 旧莱茵桥(沃尔姆斯) / 内卡桥 / 多瑙河桥 / 易北河桥 / 基尔运河桥
- **E-BRÜCKE-20 集齐**(银)

#### E4.5 Häfen 港口 10 个
- 北海港:汉堡港 / 不来梅港 / 库克斯港 / 埃姆登 / 威廉港
- 波罗的海:吕贝克港 / 基尔港 / 罗斯托克港 / 维斯马港
- 内河:杜伊斯堡港(世界最大)
- **E-HAFEN-10 集齐**(金)

---

### E5. Brauchtum 风俗节庆(~110 个)

> 跟你原本想的"节日探索"是同一大类,扩展到 4 个子类。

#### E5.1 Volksfeste 大型节庆 30 个
- 慕尼黑啤酒节 Oktoberfest
- 汉堡港口节 Hafengeburtstag
- 科隆狂欢节 Karneval
- 美因茨狂欢节
- 杜塞尔多夫狂欢节
- 柏林国际啤酒节
- 五月树节 Maibaumfest
- 施韦因富尔特老城节
- 纽伦堡老城节
- 莱比锡哥德节
- 拜罗伊特瓦格纳音乐节
- 萨尔茨堡?不(奥地利的)
- 巴登-巴登音乐节
- 鲁尔艺术节 RUHRTRIENNALE
- 柏林艺术周 Berlin Art Week
- 法兰克福书展
- 慕尼黑啤酒节相关:Pinkel & Bansen
- 海德堡老城节
- 雷根斯堡日耳曼历史节
- 拜罗伊特瓦格纳(重复)
- **E-FEST-30 集齐**(钻石,奖励"Festbesucher"称号)

#### E5.2 Weihnachtsmärkte 圣诞市集 30 个
- 纽伦堡 Christkindlesmarkt(最古老)
- 德累斯顿 Striezelmarkt(最古老之一)
- 慕尼黑 Marienplatz
- 法兰克福 Römerberg
- 科隆大教堂广场
- 柏林 Gendarmenmarkt
- 斯图加特
- 汉堡
- 杜塞尔多夫
- 罗斯托克(波罗的海风情)
- 海德堡
- 巴登-巴登
- 弗赖堡
- 奥格斯堡
- 特里尔
- 雷根斯堡
- 乌尔姆
- 美因茨
- 萨尔布吕肯
- 帕德博恩
- 选 30 个
- **E-WEIHNACHT-30 集齐**(钻石,奖励"Weihnachtsfan"称号)

#### E5.3 Regionale Feste 地方民俗 30 个
- 巴伐利亚:Fronleichnam(天主教圣体节) / Almabtrieb(牛下山节) / Leonhardiritt(圣莱昂哈德骑马节) / Fischerstechen(渔民决斗,雷根斯堡) / Funken(黑森林焚烧节)
- 北德:Ostseeküstenfest / Sturmtage(风暴节) / Biikebrennen(弗里斯兰焚烧节)
- 中部:Weinfeste(葡萄酒节 9 月) / Kirmes(集市) / Schützenfest(射击节) / Erntedankfest(感恩节)
- 西部:Karneval(狂欢节 11.11) / Schützenfest(射击节)
- 南部:Wallfahrt(朝圣) / Kirchweih(教堂祝圣)
- 东部:Erntedank(丰收节) / Reformationstag(新教改革日 10.31)
- 选 30 个具体地方节庆
- **E-BRAUCHTUM-30 集齐**(金)

#### E5.4 Musikfestivals 音乐节 20 个
- Rock am Ring(纽堡)
- Wacken Open Air(金属)
- Hurricane Festival
- Southside Festival
- Melt! Festival
- Fusion Festival
- Tomorrowland 德国?不
- 拜罗伊特瓦格纳
- 莱比锡巴赫音乐节
- 路德维希堡城堡节
- 斯图加特啤酒节(??)
- 慕尼黑歌剧节
- 巴登-巴登复活节音乐节
- 柏林森林音乐节(?)
- 柏林爱乐厅演出
- 选 20 个
- **E-MUSIKFEST-20 集齐**(金)

---

### E6. Sport 体育(~150 个)

> **完全是你没提的维度,但是是德国文化的灵魂之一**——德国足球世界第一,F1 主场,网球明星辈出,奥运大国。

#### E6.1 Bundesliga-Stadien 德甲主场 18 个
- **E-STADION-001 至 E-STADION-018**
- 拜仁慕尼黑 Allianz Arena / 多特蒙德 Signal Iduna Park / 沙尔克 Veltins-Arena / 勒沃库森 BayArena / 莱比锡 Red Bull Arena / 法兰克福 Waldstadion / 斯图加特 MHPArena / 汉堡 Volksparkstadion / 科隆 RheinEnergieStadion / 不莱梅 Weserstadion / 沃尔夫斯堡 Volkswagen Arena / 门兴格拉德巴赫 BORUSSIA-PARK / 奥格斯堡 WWK Arena / 弗赖堡 Dreisamstadion / 海登海姆 Voith-Arena / 圣保利 Millerntor-Stadion / 柏林赫塔 Olympiastadion / 柏林联盟 Alte Försterei
- **E-STADION-18 集齐**(钻石,奖励"Fußballfan"称号)

#### E6.2 Historische WM-Spielstätten 世界杯/欧洲杯主办场 12 个
- 1974 世界杯 9 个场地(慕尼黑/多特蒙德/汉堡/柏林/杜塞尔多夫/法兰克福/汉诺威/盖尔森基兴/斯图加特)
- 2006 世界杯 12 个场地
- 1988/2024 欧洲杯场地
- **E-WM-12 集齐**(金)

#### E6.3 Motorsport 赛车 10 个
- 纽博格林赛道 Nürburgring(车迷圣地)
- 霍根海姆 Hockenheimring
- 萨克森环 Sachsenring
- Lausitzring
- Oschersleben
- 选 10 个
- **E-MOTOR-10 集齐**(银)

#### E6.4 Wintersport 冬季运动 10 个
- 加米施-帕滕基兴 Garmisch-Partenkirchen(冬奥 1936/1940/2024 主办地,楚格峰)
- 奥伯斯特多夫 Oberstdorf(跳台滑雪,四峡跳台)
- 科尼希斯湖 Königssee(雪橇)
- 因斯布鲁克?不(奥地利)
- 温特贝格 Winterberg(雪橇/钢架雪车)
- 奥伯霍夫 Oberhof(冬季两项)
- 比绍夫斯格伦 Bischofswerda?不
- 选 10 个
- **E-WINTER-10 集齐**(银)

#### E6.5 Berühmte Sportler 体育明星 30 个
> **跟德语口语话题强相关**——讲到自己喜欢的运动员,是初学者最自然的话题
- 足球:Beckenbauer / Matthäus / Klose / Müller / Götze / Neuer / Kroos / Özil / Lahm / Bierhoff
- 网球:Boris Becker / Steffi Graf / Angelique Kerber / Alexander Zverev
- F1:Vettel / Schumacher / Rosberg / Hülkenberg
- 冬季:Bund(无)/ 奥伯霍夫相关 / Neuner(冬季两项) / 凯勒 / Vonn(美国)
- 其他:海因茨·马克斯 / 维特尔(重复)
- 选 30 个有故事的
- **E-SPORTLER-30 集齐**(金,奖励"Sportexperte"称号)

#### E6.6 Olympische Spiele 奥运 10 个
- 1936 柏林 / 1972 慕尼黑 / 2024 申请?
- 历史奥运冠军:Mike Krüger / Birgit Fischer / 选 10 个

---

### E7. Alltag 日常生活(~150 个)

> **这是我觉得最该加的维度**——留学前"心理准备"全靠这块。
> 学生 18 岁出国,德国生活第一年最容易出问题的事情:
> **垃圾分类、租房合同、银行开户、保险、医生预约、超市价格比较、公交月票、打工合同、税务、退房**——这些场景化词汇,场景化对话,场景化文化。

#### E7.1 Mülltrennung 垃圾分类 6 个大类
- E-MÜLL-PAPIER(纸)
- E-MÜLL-GLAS(玻璃,3 色)
- E-MÜLL-BIO(生物)
- E-MÜLL-VERPACKUNG(包装,黄袋)
- E-MÜLL-RESTMÜLL(剩余垃圾)
- E-MÜLL-SPERRMÜLL(大件垃圾,需预约)
- 隐藏成就 `H-RECYCLING-5-SORTEN`:一次分类 5 种全对
- **E-MÜLL-ALL 集齐**(金,留学最实用成就之一)

#### E7.2 Supermärkte 超市品牌 30 个
> 知道每个超市的定位 = 省 30% 生活费
- 廉价:ALDI / LIDL / PENNY / NETTO / NORMA / KAUFLAND
- 中端:REWE / EDEKA / REAL(已倒闭) / HIT
- 高端/有机:ALNATURA / BIO COMPANY / DENNS / LPG Biomarkt
- 药店:DM / ROSSMANN
- 家具:XXXLUTZ / IKEA / POCO / ROLLER
- 电器:MEDIA MARKT / SATURN
- 时尚:H&M / C&A / ZARA
- 选 30 个
- **E-SUPER-30 集齐**(金,奖励"Sparsame:r Student:in"称号)

#### E7.3 Berufe 职业 30 个
> 跟求职、打工、租房沟通、邻居对话挂钩
- 服务:Gastro / Verkäufer:in / Kellner:in / Barista
- 蓝领:Kfz-Mechatroniker / Elektriker / Maler / Klempner
- 白领:Softwareentwickler / Ingenieur / Buchhalter
- 学术:Wissenschaftler / Arzt / Lehrer / Professor
- 创意:Designer / Fotograf / Architekt
- 选 30 个
- **E-BERUF-30 集齐**(金)

#### E7.4 Wohnen 租房 20 个
- WG / 单人公寓 / 学生宿舍(Studentenwohnheim) / 临时公寓(Übergangswohnung)
- Kaution(押金)/ Miete(房租)/ Nebenkosten(附加费)/ Mietvertrag(租房合同)/ Kündigungsfrist(解约期)/ Übergabeprotokoll(交接单)
- 隐藏成就 `H-WG-CASTING`:完成一次 WG 招租模拟对话
- **E-WOHN-20 集齐**(金,留德华必备)

#### E7.5 ÖPNV 公共交通 20 个
- 巴登符腾堡州票 / 拜仁州票 / 49 欧票(Deutschlandticket)
- U-Bahn / S-Bahn / Straßenbahn / Bus / Regionalbahn / IC / ICE
- 隐藏成就 `H-TICKET-49`:连续 3 个月用 49 欧票出行
- **E-ÖPNV-20 集齐**(银)

#### E7.6 Behörden & Dokumente 行政 20 个
- Aufenthaltstitel(居留许可) / Anmeldung(户籍登记) / Steuer-ID(税务编号) / Sozialversicherung(社保) / Lohnsteuer(工资税) / Rundfunkbeitrag(广播电视费) / Kfz-Zulassung(车辆登记) / Führerschein(驾照) / Personalausweis / Reisepass
- 隐藏成就 `H-BÜROKRATIE`:在 1 小时内完成"Anmeldung"全流程(在游戏里)
- **E-BÜROKRATIE-20 集齐**(金,留德华终极成就)

#### E7.7 Versicherungen 保险 10 个
- 法定/私人健康保险(Krankenversicherung) / 责任险(Haftpflicht) / 家财险(Hausrat) / 意外险(Unfall) / 旅行险(Reise) / 法律保护险(Rechtsschutz) / 牙科附加(Zahnzusatz) / 长期护理险(Pflege) / 失业险(Arbeitslosigkeit) / 寿险(Leben)

#### E7.8 Essen & Trinken 日常饮食 10 个
- 早餐 Frühstück / 咖啡 Kaffee + Kuchen / 午餐 Mittagessen / 下午 Kaffee und Kuchen / 晚餐 Abendessen / 面包 Brotzeit / 超市 Pflücken / 食堂 Mensa / 餐厅 Restaurant / 快餐 Imbiss

#### E7.9 Tischmanieren 餐桌礼仪 10 个
- Guten Appetit / 餐具摆放 / 不可双手放桌下 / 不要早到 / 续杯文化 / 各自买单 vs AA / 生日歌 / 节庆 12 道菜 ...

---

### E8. Bildung 学术(~120 个)

> **跟申请德国大学强绑定,完成这些成就 ≈ 走通申请流程**

#### E8.1 Elite-Unis 精英大学 11 所
- **TU9 9 所**(理工精英):
  - E-UNI-RWTH(亚琛)
  - E-UNI-TU-MÜNCHEN
  - E-UNI-TU-BERLIN
  - E-UNI-TU-DARMSTADT
  - E-UNI-TU-DRESDEN
  - E-UNI-TU-HAMBURG
  - E-UNI-TU-KAISERSLAUTERN
  - E-UNI-TU-BRAUNSCHWEIG
  - E-UNI-KIT(卡尔斯鲁厄)
- **2 所其他精英**:Heidelberg / LMU München / Freiburg(精英计划)
- 单点 11 个,每个有 NPC 招生官对话剧情
- **E-UNI-ELITE-11 集齐**(钻石,奖励"Zukünftiger Student"称号,跟"申请清单"成就联动)

#### E8.2 Forschungsinstitute 研究机构 20 个
- Max-Planck(马普所)总部 + 10 个研究所
- Fraunhofer(弗朗霍夫)总部 + 5 个研究所
- Helmholtz(亥姆霍兹)联合大研究中心
- Leibniz(莱布尼茨)协会
- 选 20 个具体研究所
- **E-FORSCH-20 集齐**(金,奖励"Forschungsprofi"称号)

#### E8.3 Nobelpreisträger 诺贝尔奖得主 20 个
> 跟 A-levels Physics/Chemistry/Biology 联动,理解知识从哪儿来
- 物理 8 个:Einstein / Planck / Heisenberg / Born / Hertz / Wien / Stark / Gustav Hertz
- 化学 6 个:Hahn / Haber / Bosch / Nernst / Wallach / Wieland
- 医学/生理 6 个:Koch / Ehrlich / Warburg / Butenandt / Löffler / Behring
- **E-NOBEL-20 集齐**(金,奖励"Geniekenner"称号)

#### E8.4 Bewerbung 申请流程 15 个
> **这是"硬卡点"成就,完成 = 申请过过过**
- E-APS-COMPLETE(APS 审核)
- E-UNI-ASSIST-COMPLETE(uni-assist 评估)
- E-TESTDAF-BEST(德福 4×4)
- E-DAAD-COMPLETE(DAAD 奖学金申请)
- E-MOTIVATIONSSCHREIBEN(动机信 5 稿)
- E-LEBENSLAUF-CV(完整简历)
- E-EMPFEHLUNG-2(2 封推荐信)
- E-SPRACHNACHWEIS(语言证书)
- E-ZULASSUNG(拿到 Zu)
- E-VISUM-TERMINE(签证预约)
- E-BLOCKED-KONTO(资金证明)
- E-KRANKENVERSICHERUNG(保险证明)
- E-WOHNUNG-BESTÄTIGT(住房证明)
- E-ANMELDUNG(户籍登记)
- E-IMMATRIKULATION(注册入学)
- **E-BEWERBUNG-ALL 集齐**(白金,传说级,奖励"Stipendiat:in"称号)

#### E8.5 Fächer-Ranking 大学专业 30 个
- 机械工程 / 电气工程 / 计算机科学 / 物理 / 化学 / 生物 / 数学 / 经济 / 管理 / 法律 / 医学 / 心理学 / 哲学 / 历史 / 文学 / 语言学 / 艺术 / 音乐 / 体育 / 建筑 / 土木 / 化工 / 材料 / 光学 / 医学工程 / 环境工程 / 能源 / 航空 / 车辆工程 / 机器人
- 每个专业 1 个成就
- 关联 TU9 强势学科(慕尼黑工大机械 / 亚琛工大电气 / KIT 计算机 ...)
- **E-FACH-30 集齐**(金)

---

### E9. Design 创意设计(~100 个)

> **专门给艺术/设计方向学生,跟一般探索类有区隔**
> 这块可以延后到 Phase B 之后做,不影响主线

#### E9.1 Modemarken 服装品牌 20 个
- 运动:Adidas(黑措根奥拉赫) / Puma(同上) / Jack Wolfskin(伊德斯坦因) / Schöffel(慕尼黑)
- 高级:Hugo Boss(麦琴根) / Jil Sander(汉堡) / Escada(慕尼黑) / Strenesse(诺伊堡)
- 街头:Anine Bing(??) / Closed(汉堡) / Lala Berlin(柏林) / HUGO(麦琴根)
- 户外:Vaude(基斯莱格) / Mammut(瑞士,不算德国)/ Fjällräven(瑞典,不算)
- 鞋:Birkenstock(诺伊施塔特) / Sioux(汉堡)
- 配饰:Seeger(柏林) / Lederwaren
- 选 20 个
- **E-MODE-20 集齐**(银)

#### E9.2 Designschulen 设计学院 15 个
- 魏玛包豪斯大学(包豪斯)
- 乌尔姆 HfG(继承包豪斯)
- 卡塞尔艺术学院
- 杜塞尔多夫艺术学院
- 柏林艺术大学 UdK
- 汉堡艺术学院 HfBK
- 慕尼黑工大设计系
- 奥芬巴赫设计学院
- Pforzheim 珠宝设计学院
- 莱比锡 HGB 书籍艺术
- 选 15 个
- **E-DESIGNSCHULE-15 集齐**(金,奖励"Kreativkopf"称号)

#### E9.3 Bauhaus-Meister 包豪斯大师 20 个
- Gropius / Itten / Klee / Kandinsky / Albers / Moholy-Nagy / Breuer / Mies van der Rohe / Gunta Stölzl / Marcel Breuer(重复) / Herbert Bayer / Marianne Brandt / Wilhelm Wagenfeld / Christian Dell / Hans Przyrembel / Dörte Helm / Friedl Dicker / Max Bill(瑞士,不算)/ Tomás Maldonado(阿根廷) / Otl Aicher
- 选 20 个
- **E-MEISTER-20 集齐**(钻石,奖励"Bauhauskenner"称号,艺术史课直接加分)

#### E9.4 Kunst-Ausstellungen 艺术展览 25 个
- Documenta(卡塞尔 5 年一次)
- Skulptur Projekte(明斯特 10 年一次)
- Berlinale(柏林电影节,虽然不是艺术)
- Art Cologne
- Art Basel(瑞士,不算)
- Transmediale(柏林新媒体艺术)
- Lichtsicht(投影艺术)
- Bauhaus-Ausstellung(包豪斯展,常设)
- 选 25 个
- **E-AUSSTELLUNG-25 集齐**(金)

---

### E10. Geschichte 历史(~110 个)

> 跟 A-levels History 联动,知识背诵的同时有游戏乐趣

#### E10.1 Historische Ereignisse 历史事件 30 个
- 罗马时期:Limes 建造(约 100 AD)/ Varusschlacht 条顿堡森林(9 AD)
- 中世纪:Charlemagne 加冕(800)/ 神圣罗马帝国成立(962)/ 骑士团(Teutonic Order)
- 宗教改革:Luther 95 论(1517)/ 三十年战争(1618-1648)/ Westfälischer Friede(1648)
- 帝国时期:Bismarck 统一(1871)/ Wilhelm II
- 魏玛:Weimarer Republik(1919)
- 纳粹:Machtübernahme(1933)/ Kristallnacht(1938)/ Holocaust(1939-45)
- 二战:Zusammenbruch(1945)
- 战后:Grundgesetz(1949)/ Wirtschaftswunder / 柏林墙(1961)/ Mauerfall(1989)
- 当代:Wiedervereinigung(1990)/ Euro 引入(2002)
- 选 30 个
- **E-HIST-E-30 集齐**(金)

#### E10.2 Denkmäler & Gedenkstätten 纪念建筑 30 个
- 勃兰登堡门 / 柏林墙遗迹(东边画廊) / 犹太人纪念碑(柏林) / 联邦总理府 / 国会大厦 / 拉文斯布吕克集中营 / 萨克森豪森集中营 / 达豪集中营 / 纽伦堡审判庭 / 瓦尔特堡(路德) / 罗马边界 Limes 遗址 / 哈德良别墅(罗马) / 比特堡 / 班贝格老城 / 吕贝克老城 / 奎德林堡 / 维特瑙(维特尔斯巴赫王朝) / 拜罗伊特瓦格纳墓地 / 柏林新岗哨 / 包豪斯档案馆 ...
- **E-DENKMAL-30 集齐**(金)

#### E10.3 Historische Personen 历史人物 50 个
> 跟 E2.6 名人故居联动,补全重要但没有"故居"的人物
- 君主:Charlemagne / Otto I / Friedrich Barbarossa / Karl V / Friedrich der Große / Bismarck / Wilhelm II
- 政治家:Brandt / Schmidt / Kohl / Merkel / Adenauer
- 思想家:Kant / Hegel / Marx / Nietzsche / Weber
- 艺术家:Dürer / Cranach / Richter / Beuys
- 音乐家:Bach / Beethoven / Brahms / Wagner
- 科学家:Einstein / Planck / Heisenberg
- 选 50 个
- **E-PERSON-50 集齐**(钻石,历史课直接通)

---

### E11. Sprache 语言文化(~150 个)

> 跟德语学习本身强联动,跟 Culture 文化有部分重叠,但这里聚焦"语言现象"

#### E11.1 Dialekte 方言 16 种
> 16 州,各有特色方言
- E-DIALEKT-BAYRISCH(拜仁)
- E-DIALEKT-SÄCHSISCH(萨克森,德国最被黑的方言)
- E-DIALEKT-SCHWÄBISCH(施瓦本)
- E-DIALEKT-BERLINERISCH(柏林)
- E-DIALEKT-KÖLSCH(科隆)
- E-DIALEKT-PIÄTZISCH(普法尔茨)
- E-DIALEKT-HESSISCH(黑森)
- E-DIALEKT-SACHSEN-ANHALT
- E-DIALEKT-NORDDEUTSCH(北德)
- E-DIALEKT-FRISISCH(弗里斯兰)
- E-DIALEKT-NIEDERDEUTSCH(低地德语,跟英语关系近)
- E-DIALEKT-SÜDTIROLERISCH(南蒂罗尔,奥地利的,不算)
- E-DIALEKT-OSTBELGIEN??
- 选 16 个
- **E-DIALEKT-16 集齐**(金,奖励"Mundartkenner"称号,德国人看了惊呼)

#### E11.2 Redewendungen 成语谚语 100 个
- "Ich verstehe nur Bahnhof"(我只能听懂火车站——完全听不懂)
- "Tomaten auf den Augen haben"(眼睛上有西红柿——看不见眼前的事)
- "Da steppt der Bär"(熊在跳舞——那里很热闹)
- "Die Daumen drücken"(按大拇指——祝好运)
- "Klappe zu, Affe tot"(盖上,猴子死了——结束)
- "Alles hat ein Ende, nur die Wurst hat zwei"(一切都有尽头,只有香肠有两头)
- 100 个分级:
  - E-RW-A1(20 个 A1 级)
  - E-RW-A2(30 个 A2)
  - E-RW-B1(30 个 B1)
  - E-RW-B2-C1(20 个高级)
- **E-RW-100 集齐**(金,口语直接上 B2)

#### E11.3 Literatur 文学作品 30 个
- Goethe:Faust / Die Leiden des jungen Werthers / Wilhelm Meister
- Schiller:Die Räuber / Kabale und Liebe / Wilhelm Tell
- Thomas Mann:Die Buddenbrooks / Der Zauberberg
- Kafka:Die Verwandlung(用德语读)
- Hesse:Steppenwolf / Siddhartha
- Grass:Die Blechtrommel
- Brecht:Die Dreigroschenoper / Mutter Courage
- 选 30 个经典
- **E-LITERATUR-30 集齐**(钻石,奖励"Literaturkenner"称号,TestDaF 写作直接出彩)

#### E11.4 Filme 经典电影 30 个
- "Das Boot"(从海底出击)
- "Die Welle"(浪潮)
- "Good Bye, Lenin!"(再见列宁)
- "Lola rennt"(罗拉快跑)
- "Die fetten Jahre sind vorbei"(窃听风暴)
- "Soul Kitchen"(灵魂厨房)
- "Toni Erdmann"(托尼·厄德曼)
- 选 30 个
- **E-FILM-30 集齐**(金,听力语感大幅提升)

#### E11.5 Lieder 经典歌曲 30 个
- Beethoven:9 交响曲(欢乐颂 Ode an die Freude)
- Schubert:Der Erlkönig / Ave Maria
- Brahms:Wiegenlied
- Wagner:Lohengrin 婚礼合唱
- Bach:G弦上的咏叹调
- 圣诞:O Tannenbaum / Stille Nacht / Süßer die Glocken
- 民歌:Die Loreley / Muss i denn
- 现代:Nena 99 Luftballons / Scorpions Wind of Change
- 选 30 个
- **E-LIED-30 集齐**(金,奖励"Ohrwurm"称号)

---

## 5. 元成就类 M — Meta(~80 个)

> 持续行为、连胜、特殊事件

### M1 连续打卡 Streak(5 个)
- M-STREAK-3 / 7 / 30 / 100 / 365

### M2 单关评价(5 个)
- M-RATE-FIRST(首次给关卡评分)
- M-RATE-50(评 50 关)
- M-STAR-3 / 4 / 5(获得 3/4/5 星评价)

### M3 等级与里程碑(10 个)
- M-LEVEL-10 / 25 / 50 / 75 / 100(玩家等级)
- M-XP-1K / 10K / 100K(累计 XP)
- M-3TRACKS(3 个轨道都完成首关)
- M-FIRST-A(首次拿到 A)

### M4 朋友与社交(10 个)
- M-FRIEND-1 / 5 / 10 / 50(添加朋友)
- M-CHAT-DE-FIRST(第一次用德语跟 NPC 完成对话)
- M-CHAT-DE-100(100 次德语对话)
- M-CLASS-CHAT(创建/加入班级群)
- M-MENTOR(成为学伴,帮 1 人)
- M-MENTOR-10(帮 10 人)

### M5 特殊事件(50 个,以下举例)
- M-FIRST-LESSON(完成第一课)
- M-FIRST-WORD(学完第一个德语单词)
- M-FIRST-EXAM(完成第一次模拟考)
- M-MARATHON(单次 4 小时学习)
- M-NIGHT-OWL(凌晨 2 点还在学习)
- M-EARLY-BIRD(早上 6 点开课)
- M-WEEKEND-WARRIOR(周末 2 天连学)
- M-HOLIDAY(法定假日也学习)
- M-RAIN(下雨天学习)
- M-SUNNY(晴天不开游戏,意外解锁)
- M-MISTAKE-100(累计错 100 道题)
- M-CORRECT-100(累计对 100 道题)
- M-PERFECT-TEST(测试 100% 正确)
- M-FAIL-AND-RETRY(失败 5 次后第 6 次成功)
- M-RAPID-FIRE(1 分钟内答对 10 题)
- M-SAVED-BY-FRIEND(被朋友提醒关键知识点)
- M-TEACHER(2 次被 NPC 老师点赞)
- M-MULTILINGUAL(在 1 节课里同时练习德语/英语/数学)
- M-NEWS-JUNKIE(在游戏中读 5 篇德国新闻)
- M-POEM(写完一首德语诗)

---

## 6. 隐藏成就 H — Hidden(~30 个,无进度条)

> **彩蛋的精髓**——玩家不知道有这个东西,达成时弹出惊喜对话框,自带 BGM 切换
> 命名:`H-{keyword}`, 标题用紫色框 + 闪烁动效

| ID | 触发条件 | 标题 | 稀有度 |
|----|---------|------|-------|
| H-LIEBE | 第一次说出"Ich liebe dich"(在剧情里)| 德语告白家 | 钻石 |
| H-BIER-1L | 啤酒节喝完 1L 啤酒(剧情里) | Biertrinker | 金 |
| H-REDEWENDUNG-100 | 第 100 个谚语背下来 | Sprichwort-Meister | 钻石 |
| H-OKTOBERFEST-OPEN | 9 月 21 日 12:00 准时上线 | Pünktlich | 银 |
| H-MARX-QUOTE | 跟马克思 NPC 谈论资本论 | Materialist:in | 金 |
| H-BEETHOVEN-9 | 听完贝多芬第九 | Musikliebhaber:in | 金 |
| H-AIRPORT-LANDUNG | 模拟完成飞机降落慕尼黑 | Pilot:in | 银 |
| H-MÜLLTRENNUNG-PROFI | 1 分钟内分 10 种垃圾全对 | Mülltrennungs-Profi | 金 |
| H-DAUERWELLE | 1 小时内上 5 节德语课 | Dauerlerner:in | 银 |
| H-NIGHT-OWL | 凌晨 3:33 上线 | Eule | 银 |
| H-FIRST-SNOW | 12 月第一次下雪上线 | Winteranfang | 银 |
| H-BIRTHDAY | 注册日 +1 年回到游戏 | Geburtstagskind | 银 |
| H-TÜV | 完成一次 TÜV(德国车检)模拟对话 | Tüv-Expert:in | 银 |
| H-OKTOBERFEST-PROST | 在啤酒节说"Prost"获得 NPC 好感 | Bayer:in | 银 |
| H-APFELSTRUDEL | 学会做 Apfelstrudel | Bäcker:in | 银 |
| H-CURRYWURST-BERLIN | 柏林关吃 Currywurst | Berliner:in | 银 |
| H-BRATWURST-NÜRNBERG | 纽伦堡关吃 3 根 Bratwurst | Nürnberger:in | 银 |
| H-BAYERN-LIEBHABER | 拜仁关完成且得 5 星 | Bayern-Fan | 金 |
| H-BORUSSIA-DORTMUND | 多特蒙德关完成且得 5 星 | BVB-Fan | 金 |
| H-FRAU-HOLLE | 集齐"童话之路"全部 30 个节点 | Märchenerzähler:in | 钻石 |
| H-BAUHAUS-MEISTER-3 | 集齐 3 个包豪斯大师 | Bauhausjünger:in | 金 |
| H-EDISON-DEUTSCH | 学完所有科技相关 KP | Erfinder:in | 金 |
| H-MEIN-CAMPUS | 完整看一遍任意 TU9 校园 VR | Campuskenner:in | 银 |
| H-MAUS | 集齐 Sendung mit der Maus 全 30 集 | Maus-Fan | 银 |
| H-ICE | 跟 ICE 司机对话完成 1 次 | Fernreisende:r | 银 |
| H-DOSEN-BIER | 火车上喝完 1 罐啤酒 | Bahnfahrer:in | 银 |
| H-AUTOBAHN | 解锁"无限速公路"剧情 | Rasende:r | 银 |
| H-REWE-BRINGT | 跟 REWE 送货员 NPC 完成 1 次对话 | Online-Shopper:in | 银 |
| H-DRITTES-GLAS | 在 Weinstube 第 3 杯酒说出"Prost" | Weinkenner:in | 银 |
| H-2.0-SPEEDRUN | 60 分钟内完成 1 关 | Speedrunner:in | 金 |

---

## 7. 稀有度与奖励

### 7.1 稀有度等级

| 稀有度 | 视觉 | XP 奖励 | 货币奖励 | 框架 | 特殊效果 |
|--------|------|--------|---------|------|---------|
| 铜 Bronze | 棕底白字 | 50 | 10 | 铜框 | - |
| 银 Silver | 银底黑字 | 200 | 50 | 银框 | - |
| 金 Gold | 金底白字 | 800 | 200 | 金框 | 闪光 |
| 钻石 Diamond | 紫蓝白 | 3000 | 1000 | 钻石框 | 闪光+粒子 |
| 白金 Platinum | 白色光晕 | 10000 | 5000 | 彩虹框 | 全屏特效 |
| 隐藏 Hidden | 紫色 | 5000 | 2000 | 紫色神秘框 | 屏幕震动+特殊 BGM |

### 7.2 奖励体系

- **XP**:每个成就给玩家经验值,用于升级
- **金币 (Taler)**:虚拟货币,用于购买头像/主题
- **称号 (Title)**:部分成就给称号,显示在头像旁(例:Feinschmecker / Fußballfan / Biertrinker)
- **角色皮肤**:高稀有度成就解锁特殊 NPC 立绘(高斯/贝多芬/歌德等)
- **关卡解锁**:部分成就是新关卡的"钥匙"(啤酒节关卡要"拜仁之恋"成就解锁)
- **真实奖励(可后置)**:钻石级以上,可以输出 PDF 留学申请加分材料"我玩 GermanLearning 学了 1000 个德语 KP / 打卡 200 个文化点"

---

## 8. 数据结构(给前后端用)

```ts
// shared/types/achievement.ts

export type Rarity = 'bronze' | 'silver' | 'gold' | 'diamond' | 'platinum' | 'hidden';
export type Category = 'L' | 'E' | 'M' | 'H';
export type SubCategory =
  | 'L1' | 'L2' | 'L3' | 'L4'           // 学习
  | 'E1' | 'E2' | 'E3' | 'E4' | 'E5' | 'E6' | 'E7' | 'E8' | 'E9' | 'E10' | 'E11'  // 探索
  | 'M1' | 'M2' | 'M3' | 'M4' | 'M5'  // 元
  | 'H';                                  // 隐藏

export interface UnlockCondition {
  type: 'kp_count' | 'mock_score' | 'discovery_count' | 'streak' | 'time' | 'event' | 'composite';
  target_id?: string;         // 关联 KP/关卡/城市
  threshold?: number;         // 数量阈值
  comparator?: 'gte' | 'lte' | 'eq';
  sub_conditions?: UnlockCondition[];  // 复合条件
}

export interface Reward {
  xp: number;
  taler: number;
  title?: string;             // 称号
  skin_id?: string;           // 解锁皮肤
  unlocks_level_id?: string;  // 解锁关卡
  unlocks_dialogue_id?: string;
}

export interface Achievement {
  id: string;                 // L-MATH-P1-STAR
  category: Category;
  subcategory: SubCategory;
  title_de: string;
  title_zh: string;
  title_en: string;
  description: string;
  icon: string;               // /assets/achievements/l-math-p1-star.png
  rarity: Rarity;
  unlock_condition: UnlockCondition;
  reward: Reward;
  related_track?: 'deutsch' | 'ielts' | 'alevels';
  related_kp_ids?: string[];
  related_level_ids?: string[];
  is_hidden: boolean;
  sort_order: number;
}

// 探索类打卡点
export interface Discovery {
  id: string;                 // E-CASTLE-NEUSCHWANSTEIN
  category: SubCategory;      // E2
  name_de: string;
  name_zh: string;
  name_en: string;
  city_id: string;
  coordinates?: { lat: number; lng: number };
  description: string;
  image: string;
  related_achievement_id: string;  // 关联到哪个成就
  related_npc_id?: string;
  related_kp_ids?: string[];
  unlock_dialogue?: string;   // 解锁后跟 NPC 的对话
  visit_count_required: number;  // 几次"访问"算解锁(防刷)
}
```

---

## 9. UI/UX 呈现

### 9.1 主入口

```
[我的家园页面]
├── 顶部:玩家等级、XP、Taler
├── 中部:16 州地图(已点亮 vs 未点亮)
├── 右侧:连续学习天数
├── 底部:3 大轨道进度条
│    ├── 🇩🇪 德语: A1(100%) / A2(45%)
│    ├── 🇬🇧 雅思: 总分未测 / 阅读 6.5
│    └── 📐 A-levels: 数学 P1(80%) / 物理 P1(20%)
```

### 9.2 成就墙

```
Tab 切换:[学习 L] [探索 E] [元 M] [隐藏 H]

每大类有 1 个进度条 + 多个成就卡:
┌──────────────────────────────────┐
│  E2 Kultur 文化建筑      35/280  │
│  ████░░░░░░░░░░░░░░ 12%         │
├──────────────────────────────────┤
│  [E2.1 博物馆  15/50]   [铜+15] │
│  [E2.2 城堡    8/100]   [银+2 ] │
│  [E2.3 教堂    4/30 ]   [银+1 ] │
│  [E2.4 包豪斯  1/20 ]   [铜+1 ] │
│  [E2.5 企业    5/30 ]   [银+1 ] │
│  [E2.6 名人    2/50 ]   [铜+2 ] │
└──────────────────────────────────┘
```

### 9.3 探索地图

```
德国 16 州地图,每个州 1 个图标:
- 已全完成:🌟 金色
- 部分完成:🟡 黄色
- 刚解锁:⚪ 白色
- 未解锁:🔒 灰色

点击州 → 进入子页面:
- 城市列表
- 打卡点列表(景点/美食/... )
- 当前关卡
- 文化介绍
```

### 9.4 成就解锁弹窗

```
中心弹窗 + BGM 切换:
+-------------------------+
|  [紫色闪光]              |
|  🏆 成就解锁!            |
|                          |
|  隐藏成就:德语告白家      |
|  H-LIEBE                 |
|                          |
|  你在柏林关对 Lisa 说出  |
|  了"Ich liebe dich",     |
|  触发剧情彩蛋!           |
|                          |
|  奖励: +5000 XP          |
|        +2000 Taler        |
|        标题 [德语告白家]  |
+-------------------------+
```

---

## 10. 实施路线图

### Phase A(主线,跟学习系统同步)—— MVP 必须
- L1 / L2 / L3 / L4 全部(250 个)
- E1.1(16 州) + E1.2(50 城市) + E1.3(100 景点) + E1.4(52 世遗) —— 250 个
- E2.1 博物馆 50 个
- E3.1 地方代表菜 16 道
- E4.1 火车站 50 个
- E5.1 大型节庆 30 个
- E7.1 垃圾分类 6 个 + E7.2 超市 30 个 + E7.6 行政 20 个(留学最关键)
- M1 / M2 / M3(20 个)
- 隐藏成就 10 个
- **小计:约 700 个**

### Phase B(扩展,游戏性)
- E1.5 自然奇观 30 + E2.2-2.6 城堡/教堂/包豪斯/企业/名人 250
- E3.2-3.6 啤酒/葡萄酒/面包/香肠/圣诞市集小吃 150
- E4.2-4.5 机场/公路/桥梁/港口 70
- E5.2-5.4 圣诞市集/地方民俗/音乐节 80
- E6 体育全系列 100
- E11.2-11.5 谚语/文学/电影/歌曲 110
- E10 历史全系列 110
- E8.1-8.5 申请流程 + 大学 + 研究所 + 诺奖 100
- E9 设计(艺术生专属) 100
- E11.1 方言 16 + E11.2 谚语 100
- M4 / M5 社交和事件 50
- 隐藏成就 20
- **小计:约 1100 个**

### Phase C(长尾,持续运营)
- 节日限定(每年 11.11 11:11 上线就送隐藏成就)
- 跨文化彩蛋(圣诞节/复活节/开斋节)
- 校友成就("留德华 1 周年" —— 真去德国后授予)

---

## 11. 关键设计决策与原因

### 决策 1:为什么"学习类"和"探索类"分两大块?

**原因**:
- 学习类是**结果导向**(拿 A*/TDN 4),有强反馈但也强挫败
- 探索类是**过程导向**(集邮文化点),弱反馈但容易上手
- 两者互补:**学习累了玩探索获得多巴胺,探索时看到相关 KP 提示就回去学习**
- 心理学上:学习是"工具性动机",探索是"内在动机",需要同时满足

### 决策 2:为什么"日常类 E7"是大头?

**原因**:
- 18 岁出国第一年,**80% 实际问题都是"日常"**(租房/银行/超市/医生/垃圾分类)
- **学校不教,父母没经验,德国人不主动告诉你**
- 学生玩到"成功在 Weinstube 第 3 杯酒说 Prost"时,既有游戏感又有真实技能

### 决策 3:为什么"申请流程 E8.4"做成 15 个独立成就而不是 1 个?

**原因**:
- 申请流程 8-12 个月,**心理上最容易放弃**的就是中间段
- 15 个里程碑让"100 天没进展 → 完成 1 个 APS 步骤 → 立刻获得成就"
- 跟 L1-L3 学习成就配合,让学生感觉"我每一项都在推进"

### 决策 4:为什么隐藏成就要有 30 个?

**原因**:
- 隐藏成就是"惊喜"的本质,无进度条 + 弹出动画
- 玩家会主动在游戏中"尝试奇怪的事情"
- 隐藏成就分享率高("我解锁了一个你可能没解锁的成就"是社交传播)
- **15-20% 隐藏成就是健康游戏的设计标准**

### 决策 5:为什么跟 A-levels 21 门都挂钩?

**原因**:
- 让学生**感觉每个学科都有"打完"的感觉**——不是只学数学
- 鼓励学生选 3-4 门 A-levels(不是只数学 + 物理)
- 学科之间可以联动成就(STEM 4 科全 A → 钻石级)

### 决策 6:为什么"统计"用累计数量(已解锁 X/Y)而不是进度条?

**原因**:
- 玩家可以看到"具体差几个"
- 数量本身是游戏乐趣(德国有 25000+ 城堡,玩家就知道 100 个是精选)
- 排行榜可对比("博物馆 50 个,你跟德国小学生比排第 X 位")

---

## 12. 关联系统(给后端/前端开发的接口)

```python
# backend/api/achievements.py

class AchievementService:
    async def check_unlock(self, user_id: str, event: GameEvent) -> list[Achievement]:
        """每次玩家行为触发,检查是否解锁成就"""
        
    async def get_progress(self, user_id: str, achievement_id: str) -> Progress:
        """获取某成就进度(用于 UI 显示)"""
        
    async def get_wall(self, user_id: str, category: Category) -> WallResponse:
        """获取某类成就墙"""
        
    async def get_discovery_map(self, user_id: str) -> MapData:
        """获取探索地图数据(已点亮城市 + 打卡点)"""

# 事件类型
class GameEvent:
    type: Literal['kp_completed', 'level_completed', 'discovery_visited', 
                  'streak_extended', 'mock_taken', 'dialogue_ended', 'npc_relationship_changed']
    payload: dict
```

```ts
// frontend/src/store/achievements.ts
interface AchievementStore {
  unlocked: Map<AchievementId, UnlockedAt>;
  progress: Map<AchievementId, Progress>;
  notifications: Notification[];
  
  // 实时监听后端 SSE 流
  subscribeToUnlocks(): void;
}
```

---

## 13. 跟 curriculum 知识库的关联

每个探索成就都关联一组 KP,实现"打卡带学"——

| 探索大类 | 关联 A-levels 学科 | 关联德语 KP |
|---------|------------------|------------|
| E1 Geographie | Geography | A2 描述城市、方向 |
| E2 Kultur | History, Art | B1 谈论历史/艺术 |
| E3 Genuss | Biology(发酵)/Chemistry(食品)/Business | A2 点餐、食物词汇 |
| E4 Verkehr | Mathematics(距离)、Geography | A2 问路、买票 |
| E5 Brauchtum | History、Sociology(CAIE 不在 21 门内但可关联) | B1 谈论节日 |
| E6 Sport | PE(Biology 关联) | A2 谈论运动 |
| E7 Alltag | — (实用德语) | **A1-B1 全部生活场景** |
| E8 Bildung | 全部学科 | **B2-C1 学术德语** |
| E9 Design | Art(CAIE) | A2 描述设计 |
| E10 Geschichte | History | B2 谈论历史 |
| E11 Sprache | English Language / German | **B1-C1 高级语法、谚语** |

**联动示例**:
- 玩家打卡"新天鹅堡" → 自动弹窗介绍路德维希二世 → 关联 KP `HIST-LUDWIG-II` → 同时检查是否解锁"中世纪历史"相关 KPs
- 玩家打卡"包豪斯档案馆" → 关联 KP `ART-BAUHAUS-HISTORY` 和 A-levels Art 历史 KPs

---

## 14. 后续可扩展方向

1. **跨游戏联动**——用户去德国后,跟校友社区对接,获得"实地打卡"加成
2. **NPC 好感度**——某些成就是某 NPC 的关键任务,完成后 NPC 立绘变化
3. **季节性成就**——每年圣诞/复活节/啤酒节期间做"特殊任务链",完成后给限定成就
4. **排行榜**——博物馆/城堡/啤酒收集 TOP 100 玩家
5. **真·留学预科内容**——9 月开学的"新生大礼包"成就(银行卡/手机卡/保险/报到/搬入宿舍……)
6. **学术科研成就**——给想读 PhD 的学生,关联"发表论文模拟"任务
7. **校友成就**——玩家真的去德国后,真·打卡上传,获得特殊徽章(留德华认证)

---

## 15. 总结:这个系统能做成什么样?

| 用户类型 | 他会怎么玩 |
|---------|----------|
| **中考完准备中考分流的学生** | 看到"100 个景点" → 心动 → 一周去 1 个 → 一年后德语 A1 完成 + 50 个景点 |
| **雨中国高高一学生** | 看到"TU9 11 所大学" → 看到"TUM 机械是欧洲第一" → 开始选 Math/Physics/Chem → 一年后 3 门 A-level A* + 30 个探索点 |
| **雨中国高高二学生** | 看到"申请流程 15 个里程碑" → 拆分到每周任务 → 一年后 APS+德福+动机信全完 + 200 个探索点 |
| **考前焦虑学生** | 看到"红牛 + 2 杯咖啡"= 隐藏成就 → 当晚少睡 1 小时多刷 10 道题 → 觉得游戏懂我 |
| **留德华大一大二** | 看到"垃圾分类 5 种全对" → 才发现咖啡胶囊算哪一类 → 立刻上线玩一遍 |
| **留德华大三老油条** | 看到"马克思-恩格斯广场" → "卧槽我自己都去过" → 立刻上线,获 3 个新成就 |

**核心**:**每个学生都有一类他最想要的"那种成就"**,这才是 RPG 的本质。

---

**v1.0 终,2026-06-21。**
**下一步**:把"探索"清单(~1500 个)跟 curriculum KP 做精确关联,生成 `discoveries.json` 数据文件。
