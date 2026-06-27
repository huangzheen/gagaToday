# gagaToday 视觉风格与图片生成规范

版本：v1.0  
适用对象：gagaToday 项目中的所有图像生成 Agent、美术 Agent、地图素材 Agent、角色 Agent、场景 Agent、Prompt Agent、后处理 Agent  
用途：统一生成游戏配图、地标资产、地图 POI、人物角色、场景原画、食物物品、地图纹理、项目展示图等视觉内容  
背景设定：德国留学生活模拟 RPG  

---

## 0. 使用原则

本文件不是给 Custom GPT 的短指令，而是给所有 Agent 使用的完整视觉规范。任何 Agent 在为 gagaToday 生成图片前，都应先读取本文件，并根据图片用途选择对应的生成规则。

本规范的核心目标是：让所有图片都属于同一个 gagaToday 游戏世界，而不是看起来像不同模型、不同风格、不同项目生成出来的散图。

生成图片时，Agent 必须判断：用户要生成的是哪一类图片；是资产图还是完整场景；应使用什么比例；应该是白色背景还是完整背景；是地图图标、地点详情、人物、场景、食物、纹理还是宣传图；需要保留哪些真实德国元素；是否涉及季节、时间、天气、情绪；是否适合后续缩放到游戏内小尺寸使用；是否符合 gagaToday 独有气质。

---

# 1. 项目视觉定位

## 1.1 项目名称

**gagaToday**

## 1.2 项目类型

德国留学生活模拟 RPG / 教育游戏 / 城市探索游戏 / 真实生活模拟游戏。

## 1.3 游戏设定

玩家扮演一名中国学生，来到德国学习和生活。游戏包含德语学习、A-levels / 国际课程学习、德国城市探索、真实生活花费、地图打卡、餐饮美食、做饭、账单、邮件、信件、交通、朋友、老师、父母、女友等关系，以及考试、作业、压力与成长。

## 1.4 核心视觉一句话

**真实德国城市与留学生活，被转化成高级低精度像素风 RPG 游戏资产。**

英文核心描述：

> Real German study-abroad life transformed into premium low-resolution pixel art RPG assets.

## 1.5 气质关键词

gagaToday 的视觉应体现：真实德国、留学生活、青少年成长、温暖、略带孤独、有探索感、有学习压力、有生活细节、有欧洲城市质感。它不是幻想、不是照片、不是普通手游、不是 Q 版。

---

# 2. 总体风格定义

## 2.1 英文核心风格词

所有图片生成时都应优先包含以下核心风格：

```text
premium low-resolution pixel art,
refined 16-bit / 32-bit inspired game illustration,
grounded German realism,
Germany study-abroad life simulation RPG,
retro European RPG atmosphere,
warm nostalgic but not childish,
slightly lonely first-year-abroad mood,
handcrafted pixel-art texture,
crisp pixel edges,
readable silhouette,
limited color palette,
dark navy outline,
blocky highlights and shadows
```

## 2.2 中文解释

图像应该像低精度像素风，但不是廉价 8-bit；更接近 16-bit / 32-bit 的高级 RPG 插画；真实德国建筑和生活场景被游戏化；有清晰轮廓；有像素级高光和阴影；颜色克制；能放进游戏界面；能用于地图、详情页、任务、成就或场景展示。

## 2.3 不要生成的风格

严格避免：

```text
photorealistic photo,
3D render,
anime,
chibi,
generic cartoon,
mobile game cartoon,
fantasy RPG castle,
sci-fi,
cyberpunk,
neon,
watercolor,
oil painting,
smooth vector illustration,
plastic toy look,
overly cute style,
horror dark fantasy,
tourist poster,
travel agency poster,
flat corporate illustration,
random generic European building
```

---

# 3. 色彩规范

## 3.1 核心色板

gagaToday 的颜色应稳定在以下范围：

### 建筑石材

```text
warm parchment beige
muted Bavarian cream stone
pale sandstone
weathered limestone
```

### 屋顶

```text
terracotta roof red
muted brick brown
dark burnt sienna
aged clay tile red
```

### 阴影

```text
dark navy shadow
deep blue-gray
soft charcoal blue
```

### 绿植

```text
moss green
desaturated forest green
soft olive green
muted grass green
```

### 铜顶 / 金属 / 高光

```text
soft teal copper
aged oxidized green
antique gold highlight
muted brass
```

### 玻璃

```text
cool blue glass windows
muted navy window reflection
deep cobalt small window pixels
```

### UI 关联色

```text
dark navy
antique gold
parchment beige
muted teal
soft brick red
```

## 3.2 推荐十六进制色值

```text
Dark Navy: #07152B
Navy Shadow: #13213A
Antique Gold: #E8B85C
Gold Highlight: #FFCF72

Parchment Beige: #EFE2C2
Bavarian Cream: #D8C39B
Stone Shadow: #AD8F60
Stone Highlight: #F0DFB8

Terracotta Roof: #9C4331
Roof Light: #C35E45
Roof Shadow: #7B3025

Moss Green: #6F8F4E
Soft Grass: #8FB96C
Copper Dome: #4F7F73
Copper Highlight: #84BEA0

Window Blue: #24354F
Window Highlight: #3B5F93
```

## 3.3 禁止色彩倾向

避免高饱和霓虹色、糖果色、大面积纯黑、过度梦幻紫粉、科幻蓝紫、塑料玩具色、卡通儿童色、过多彩虹色、没有色彩秩序的随机调色。

---

# 4. 背景规则

## 4.1 当前项目统一规则

目前 gagaToday 资产图统一使用：

> **clean white background**

不再默认使用透明底。

## 4.2 白色背景定义

白色背景应为干净、简洁、不抢主体、不带灰色地台、不带棋盘格、不带复杂背景、不带大面积投影、不带 UI 框、不带海报排版。

允许少量：几块地面石板、入口台阶、小草、小灌木、自行车、路灯、学生背包、纸质地图、微弱 contact shadow。但这些必须是 grounding detail，不能变成完整背景。

## 4.3 场景原画例外

如果用户明确要求完整场景，例如课堂、地铁、晚餐、暴雨中的街道、面包店买早餐、体育课、博物馆参观、视频通话，则应生成完整背景场景，不使用白底资产规则。

---

# 5. 图片类型与尺寸规范

图像模型不一定严格输出指定像素尺寸。Agent 应优先控制用途、比例、构图、清晰度和后处理可缩放性。如果需要精确小尺寸，不应直接要求模型生成 16×16 或 32×32，而应先生成大图，再由后处理 Agent 缩小、裁切、像素化。

## 5.1 地图纹理 Tile

用途：草地、树、水波、石板、屋顶、铁轨等地图区域填充。  
比例：1:1。  
生成尺寸建议：512×512 或 1024×1024。  
后处理目标：16×16 或 32×32。  
视觉要求：

```text
seamless pixel texture tile,
low contrast,
repeatable,
not too dense,
white background,
clear pixel pattern,
suitable for map polygon fill
```

纹理图不能画得太满。公园纹理应该是“淡绿色底色 + 低对比草/树纹理”，不是满屏树图案。水纹理应该是“蓝色底 + 少量水波”，不是复杂海浪。

## 5.2 小型真实 POI 图标

用途：真实地图上的普通兴趣点，如普通餐厅、普通咖啡馆、小店、车站入口、普通景点、公共设施。  
比例：1:1。  
生成尺寸建议：512×512。  
后处理目标：16×16 或 24×24。  
视觉要求：简单、类别颜色明确、不要复杂细节、小尺寸可读、白色背景。

## 5.3 地图主 POI 图标

用途：游戏关键地点，如学校、面包店、地铁站、博物馆、教堂、球场、超市、图书馆、学生公寓、餐厅、公园。  
比例：1:1。  
生成尺寸建议：512×512 或 1024×1024。  
后处理目标：32×32 / 48×48 / 64×64。  
视觉要求：

```text
clear icon silhouette,
dark navy outline,
optional antique gold accent,
white background,
category color,
readable at 64px and 128px,
clickable game POI feeling
```

分类色建议：餐饮/面包店/餐厅为橙红；教育/学校/图书馆为绿色；文化/博物馆/教堂为紫色或古金色；交通/U-Bahn/车站为蓝色；地标/打卡为金色；日常生活/超市/公寓为棕色或青绿色；体育/球场为蓝绿色。

## 5.4 地点详情资产

用途：右侧详情栏、地点百科、打卡页面。  
对象：慕尼黑圣母教堂、德意志博物馆、安联球场、玛丽亚广场、中央车站、学校、面包店、学生公寓、餐厅。  
比例：1:1。  
生成尺寸建议：1024×1024。  
视觉要求：白色背景、主体居中、正面或轻微 3/4 视角、可以有少量 grounding details、可在 256px 仍然识别、不要完整背景、不要旅游海报、要像玩家可以进入、打卡、学习和探索的地点资产。

## 5.5 成就 / 打卡卡片图

用途：已访问地标、美食成就、课程成就、第一次独自买早餐、第一次坐 U-Bahn、第一次考试通过。  
比例：1:1 或 4:3。  
生成尺寸建议：1024×1024 或 1200×900。  
视觉要求：卡片式构图、干净白色或浅色背景、不要加文字除非用户要求、可以加入少量象征性元素、适合放进成就系统。

## 5.6 人物半身头像

用途：对话框、联系人、手机聊天、关系系统、任务列表。  
比例：1:1。  
生成尺寸建议：512×512 或 1024×1024。  
视觉要求：白色背景、半身或胸像、表情清晰、非 anime、非 chibi、年龄与设定相符、真实德国留学生活气质。

## 5.7 人物全身立绘

用途：人物档案、关系系统、角色介绍、剧情选择界面。  
比例：3:4 或 2:3。  
生成尺寸建议：768×1024 或 1024×1536。  
视觉要求：白色背景、全身站姿、服装真实、姿态表达性格、不性感化、不幻想服装、可后处理为 sprite 参考。

## 5.8 小 Sprite 角色

用途：地图行走角色、场景 NPC、简单动画。  
比例：2:3。  
生成尺寸建议：512×768。  
后处理目标：32×48 或 48×64。  
视觉要求：全身、轮廓清楚、正面或 3/4、可缩小、服装简洁、不要复杂背景。

## 5.9 食物 / 道具 / 物品

用途：菜单、背包、做饭小游戏、成就、任务道具。  
比例：1:1。  
生成尺寸建议：512×512 或 1024×1024。  
视觉要求：白色背景、居中、3/4 top-down view、可识别、颜色温暖、适合物品栏、不要桌面完整背景。

## 5.10 交通工具资产

用途：U-Bahn、S-Bahn、tram、bus、bicycle、ticket machine、train platform sign。  
比例：4:3 或 1:1。  
生成尺寸建议：1024×768 或 1024×1024。  
视觉要求：白色背景、侧面或轻微 3/4、德国城市交通真实感、可作为游戏资产、避免真实品牌 logo 过多。

## 5.11 室内房间资产

用途：卧室、厨房、教室、图书馆、食堂、面包店、超市、地铁车厢。  
比例：16:9 或 4:3。  
生成尺寸建议：1792×1024 或 1600×1200。  
视觉要求：完整可探索场景、slight top-down 3/4 RPG room view、有生活细节、不使用白底资产规则、不出现 UI 和对白框，除非用户要求。

## 5.12 剧情场景原画

用途：买早餐、坐地铁、上课、午餐、体育课、博物馆、晚餐、看球、视频通话、睡觉、暴雨中回家。  
比例：16:9。  
生成尺寸建议：1792×1024 或 1920×1080。  
视觉要求：完整背景、电影感构图、RPG 探索视角、不要 UI、不要文字、要体现真实德国留学生活。

## 5.13 PPT / 项目展示图

用途：投资汇报、项目计划、产品介绍、商业模式展示、技术架构展示。  
比例：16:9。  
生成尺寸建议：1792×1024 或 1920×1080。  
视觉要求：适合放进 PPT、清楚干净、可带视觉化信息、不要密集小字。如果需要文字，应由后期排版添加。

## 5.14 手机竖版宣传图

用途：短视频封面、App 宣传、社交媒体竖图。  
比例：9:16。  
生成尺寸建议：1024×1792 或 1080×1920。

## 5.15 游戏封面

用途：商店封面、游戏盒子封面、Steam / App Store 素材、项目投资展示封面。  
比例：3:4 或 2:3。  
生成尺寸建议：1024×1536。  
视觉要求：完整背景、主角 + 德国城市 + 学校/地标、留学成长感、可预留标题空间。不要自动生成错误文字，标题建议后期添加。

## 5.16 横版海报 / 官网 Hero

用途：官网顶部、宣传海报、横版广告、PPT 首页。  
比例：16:9。  
生成尺寸建议：1792×1024 或 1920×1080。

---

# 6. 四种核心资产风格

gagaToday 的资产图不只是一种风格。Agent 应根据用户需求自动选择 A/B/C/D 之一。

## 6.1 A. 地图 POI 图标风

用途：地图小图标、打卡点、兴趣点。  
适合对象：地铁站、面包店、学校、博物馆、教堂、球场、超市、图书馆、餐厅。  
特点：更扁平、更低精度、更清楚、适合小尺寸、64px / 128px 可读、白色背景、中心构图、深色描边、少量金色强调。

提示词核心：

```text
compact low-resolution pixel art POI icon,
white background,
centered,
clear readable silhouette,
designed for an in-game map marker,
dark navy outline,
antique gold accent,
readable at 64px and 128px
```

## 6.2 B. 地点详情资产风

用途：右侧详情栏、地点百科、打卡页面。  
适合对象：慕尼黑圣母教堂、德意志博物馆、安联球场、玛丽亚广场、中央车站、学校建筑、面包店门头。  
特点：白色背景、单个主体、正面或轻微 3/4、细节比 POI 图标多、但不要完整背景、不要像普通建筑图鉴、要有“玩家可以进入”的感觉。

提示词核心：

```text
location detail asset,
white background,
centered isolated landmark,
front or slight 3/4 view,
minimal grounding details,
suitable for game location detail panel,
visitable, collectible, educational
```

## 6.3 C. 旅行手账 × 像素资产风

用途：gagaToday 特色打卡资产、成就资产。  
特点：主体周围可加入少量留学生活元素，如学生背包、纸质地图、路灯、自行车、几块广场石板、小灌木、咖啡杯、车票、德语笔记。  
注意：不是完整背景，主体地点仍然是核心。

提示词核心：

```text
collectible travel-check-in asset,
German study-abroad RPG,
white background,
tiny student-life details around the base,
backpack, paper map, bicycle, small shrubs,
warm nostalgic travel journal feeling,
not a poster, not a full scene
```

## 6.4 D. 低精度欧洲 RPG 地点卡风

用途：地点详情、成就卡、城市探索卡。  
特点：可以比 C 更有小场景感，例如小半圈石板地、一两棵树、一个小学生角色背影、自行车、路灯、几个生活小物件。但背景边缘仍保持干净开放，整体仍是 white-background asset。

提示词核心：

```text
European RPG location-card asset,
white background,
compact landmark scene,
small semicircle of cobblestone plaza,
one tiny student figure with backpack,
one bicycle,
warm but slightly lonely study-abroad mood
```

---

# 7. 建筑与地标规范

## 7.1 基本原则

真实地点必须可识别。不要画成泛用欧洲建筑。不要把现实建筑幻想化。不要为了好看丢掉关键特征。

## 7.2 默认视角

建筑资产默认：正面或轻微 3/4 front view；不要俯视太多；不要强透视；轮廓清楚；适合放进详情栏。

## 7.3 细节处理

应保留标志性轮廓、屋顶形状、窗户节奏、入口、钟面、铜顶、柱廊、站台标识、立面材质。  
但应简化成 blocky stone texture、roof tile rhythm、small window pixels、dark navy outline、subtle shadow blocks、pixel highlights。

## 7.4 慕尼黑圣母教堂示例规则

如果用户输入慕尼黑大教堂、慕尼黑圣母教堂、Frauenkirche、Cathedral of Our Dear Lady in Munich，必须生成 Munich Frauenkirche，而不是泛用教堂。

必须包含：

```text
two tall symmetrical towers
iconic green copper onion domes
pale Bavarian stone facade
red terracotta roof sections
Gothic arched windows
tower clock details
central church body
small entrance portal
```

必须避免：

```text
generic cathedral
fantasy castle
single tower
missing onion domes
Gothic fantasy exaggeration
wrong silhouette
```

---

# 8. 人物规范

## 8.1 总体方向

人物不是 anime，也不是 chibi。人物应是德国留学生活中的真实低精度像素角色。

## 8.2 角色类型

可生成：中国学生主角、德国同学、中国留学生朋友、德语老师、数学 / A-levels 老师、父母、女友 / 男友、店长、图书馆管理员、房东、路人、球友、地铁乘客。

## 8.3 年龄与适龄表达

主角多为 15-18 岁。所有青少年角色必须真实、克制、适龄。禁止性感化、成人化、暧昧过度化。恋爱角色表现为陪伴、学习、晚餐、散步、鼓励，不表现成人内容。

## 8.4 服装

推荐：hoodie、casual jacket、simple coat、backpack、sneakers、jeans、muted colors、winter scarf、rain jacket、school bag。  
避免：fantasy armor、Japanese school uniform unless requested、luxury fashion、overly sexy outfit、idol costume。

## 8.5 表情表现

情绪必须通过眼睛、眉毛、嘴、姿态、手势、肩膀、道具互动来表达。

- Happy / 开心：soft smile、relaxed eyes、open posture、warm highlight。
- Angry / 生气：eyebrows down、tense mouth、stiff shoulders、crossed arms，不要动漫爆怒。
- Sad / 难过：lowered eyes、small mouth、shoulders down、cool blue shadow，适合思乡或考试失败。
- Cheerful / 愉快：bright smile、lively pose、lifted eyebrows、energetic but not childish。
- Nervous / 紧张：clutching backpack strap、stiff posture、uncertain eyes、slight sweat pixel allowed。
- Confused / 困惑：tilted head、unsure eyes、slightly open mouth，不要巨大的问号符号，除非用户要求。
- Tired / 疲惫：half-open eyes、slouched posture、messy hair、backpack hanging lower、dark eye pixels。
- Confident / 自信：straight posture、calm smile、focused eyes、clean silhouette。

---

# 9. 室内场景规范

适用场景：学生卧室、寄宿家庭房间、厨房、教室、食堂、图书馆、面包店、超市、餐厅、地铁车厢。  
推荐视角：slight top-down 3/4 RPG room view。  
可使用街机 RPG 室内视角、可探索房间布局、轻微俯视、物件摆放清楚。

根据场景加入：German textbooks、backpack、phone、letters、calendar、desk lamp、grocery bag、cooking tools、school notes、laptop、water bottle、small wallet、train ticket、German worksheet、exam paper、parent message on phone。

室内场景应该有安静、真实、略孤独、有生活压力但仍有希望的气质。

---

# 10. 食物与物品规范

适合生成：Brötchen、Brezel、Schnitzel、Currywurst、Apfelstrudel、coffee、cafeteria tray、supermarket ingredients、cooking mini-game ingredients。  
推荐视角：3/4 top-down view。  
用途：菜单、背包、做饭小游戏、美食成就、餐厅系统。  
要求：白色背景、居中、清楚、颜色温暖、不过饱和、不要完整桌面背景、可在 128px 识别。

---

# 11. 交通规范

适用对象：U-Bahn、S-Bahn、tram、bus、bicycle、train station、platform、ticket machine。  
资产视角：side view 或 slight 3/4 view，清楚轮廓，德国城市交通真实感，白色背景。  
完整场景可包含站台、售票机、等车学生、冷色灯光、地铁车厢内部。避免真实品牌 logo 过多。

---

# 12. 地图与纹理规范

gagaToday 地图是：

```text
真实 OSM 数据 + 像素风渲染 + RPG UI + 游戏 POI
```

地图底图规则：

- 建筑统一红棕色；
- 道路米黄色；
- 水域蓝色；
- 公园绿色；
- 真实 POI 小彩点；
- 游戏 POI 大图标；
- UI 深蓝 + 金色；
- 不要像 Google Map；
- 不要像随机 tile map；
- 不要像海报手绘地图。

地图纹理用于 polygon fill：grass、tree、water、stone、roof、rail。  
生成纹理时使用 1:1、white background、seamless pixel tile、low contrast、repeatable、not too dense、suitable for downscaling to 16×16 or 32×32。

---

# 13. 季节、时间、天气规范

## 春天 Spring

```text
fresh soft green
light blossoms
hopeful new-start mood
mild sunlight
clean air
```

适合初到德国、新学期、早晨上学、公园探索。

## 夏天 Summer

```text
lush green
clear daylight
active outdoor life
warm afternoon
outdoor cafés
```

适合城市探索、球赛、博物馆、同学活动。

## 秋天 Autumn

```text
amber leaves
warm nostalgic light
study season atmosphere
soft orange glow
cooler air
```

最适合 gagaToday 主视觉，有学习、成长、怀旧和略孤独的感觉。

## 冬天 Winter

```text
muted cold light
light snow
warm window glow
quiet German winter
```

适合思乡、考试、圣诞市场、夜晚写作业。

## 暴雨 Heavy Rain

```text
wet cobblestone reflections
dark navy shadows
warm yellow lights
rain streaks
lonely study-abroad mood
```

适合迷路、迟到、账单压力、面包店、地铁站、夜晚回家。

## 时间段

Morning：pale golden light、quiet street、fresh start、long soft shadows。  
Noon：clear daylight、crisp shadows、active school day、readable colors。  
Sunset：warm orange rim light、nostalgic after-school mood、soft European glow。  
Midnight：dark navy shadows、warm window light、quiet loneliness、study pressure。

---

# 14. 场景原画规范

适合场景：起床、买早餐、坐地铁、到学校、上课、午餐、体育课、放学、博物馆、回家作业、测试、睡觉、与母亲视频通话、与女友晚餐、看球赛、暴雨回家。

推荐构图：

```text
16:9 premium pixel art RPG scene
street-level or slight top-down exploration camera
layered depth
clear focal point
cinematic but playable
```

不要出现 UI、对话框、大量文字、logo、水印、现代海报排版、过多人物、过度复杂细节、无法看清玩法的构图。

---

# 15. 生成提示词模板

## 15.1 通用资产模板

```text
Create a white-background game asset for gagaToday, a Germany study-abroad life simulation RPG.

Subject: [subject]

Visual style:
premium low-resolution pixel art, refined 16-bit / 32-bit inspired game illustration, grounded German realism, retro European study-abroad RPG atmosphere, warm nostalgic but not childish, slightly lonely first-year-abroad mood, limited color palette, crisp pixel edges, readable silhouette, handcrafted pixel-art texture, dark navy outline, blocky pixel highlights and shadows.

Composition:
centered isolated asset on a clean white background. Use [front view / slight 3/4 view / 3/4 top-down view depending on subject]. Keep the subject readable at small size. Add only minimal grounding details if useful, such as a few plaza stones, small shrubs, entrance steps, a street lamp, backpack, or bicycle.

Color palette:
warm parchment beige, muted Bavarian cream, terracotta roof red, muted brick brown, moss green, soft teal copper, antique gold highlights, dark navy shadows, cool blue window glass.

Detail direction:
simplify real-world details into readable game art. Use blocky texture, pixel highlights, small window pixels, roof rhythm, clean dark outline, subtle shadow blocks. The asset should feel like a collectible object or place inside a German study-abroad RPG.

Negative prompt:
photorealistic, 3D render, anime, chibi, generic cartoon, mobile game cartoon, fantasy castle, sci-fi, cyberpunk, neon, watercolor, oil painting, smooth vector illustration, plastic toy look, excessive noise, unreadable over-detail, random invented architecture, wrong landmark silhouette, transparent background, checkerboard background, gray platform, big floor shadow, text, logo, watermark, UI frame, poster layout, blurry edges, soft anti-aliased look.
```

## 15.2 通用场景模板

```text
Create a 16:9 premium pixel art RPG scene for gagaToday, a Germany study-abroad life simulation RPG.

Scene: [scene]

Visual style:
premium low-resolution pixel art, refined 16-bit / 32-bit inspired game scene, grounded German realism, retro European study-abroad RPG atmosphere, warm nostalgic but not childish, slightly lonely first-year-abroad mood, handcrafted pixel-art texture, crisp pixel edges, limited color palette, layered depth, readable silhouettes.

Composition:
street-level or slight top-down RPG exploration camera, cinematic but playable composition, clear focal point, realistic German study-abroad life details. No UI, no dialogue box, no text overlay, no logo, no watermark.

Atmosphere:
[season], [time of day], [weather], with appropriate lighting, mood, and environmental details.

Color palette:
warm parchment beige stone, terracotta roof red, muted Bavarian cream, moss green, dark navy shadows, cool blue reflections, antique gold highlights, warm window light if appropriate.

Negative prompt:
photorealistic, 3D render, anime, chibi, generic cartoon, fantasy, sci-fi, cyberpunk neon, watercolor, oil painting, smooth vector illustration, poster layout, UI frame, text, logo, watermark, blurry edges, excessive noise.
```

---

# 16. 示例提示词

## 16.1 慕尼黑圣母教堂：地点详情资产

```text
Create a white-background location detail asset for gagaToday, a Germany study-abroad life simulation RPG.

Subject: Munich Frauenkirche, the Cathedral of Our Dear Lady in Munich, Germany.

Show the landmark accurately: two tall symmetrical towers, iconic green copper onion domes, pale Bavarian stone facade, red terracotta roof sections, Gothic arched windows, tower clock details, central church body, small entrance portal. It must be recognizable as Munich Frauenkirche, not a generic cathedral.

Visual style:
premium low-resolution pixel art, refined 16-bit / 32-bit inspired game illustration, grounded German realism, warm nostalgic European study-abroad RPG atmosphere, crisp pixel edges, readable silhouette, handcrafted pixel-art texture, limited color palette, dark navy outline, blocky stone texture, pixel highlights.

Composition:
centered isolated landmark asset on a clean white background, front-facing or slight 3/4 front view. Add only minimal grounding details: a few warm beige plaza stones, two small moss-green shrubs, maybe one tiny street lamp. No full background, no sky, no gray platform.

Color palette:
warm parchment beige stone, muted Bavarian cream, terracotta roof red, soft teal copper domes, antique gold highlights, moss green plants, dark navy shadows, cool blue window glass.

Negative prompt:
photorealistic, 3D render, anime, chibi, fantasy cathedral, generic RPG castle, white platform, gray platform, transparent background, checkerboard background, text, logo, watermark, UI frame, blurry edges, missing onion domes, wrong silhouette.
```

## 16.2 暴雨中的面包店：完整场景

```text
Create a 16:9 premium pixel art RPG scene for gagaToday, a Germany study-abroad life simulation RPG.

Scene: a small German bakery storefront during heavy rain, where a Chinese student is buying breakfast before school.

Visual style:
premium low-resolution pixel art, refined 16-bit / 32-bit inspired game scene, grounded German realism, warm nostalgic European RPG atmosphere, handcrafted pixel-art texture, crisp pixel edges, limited color palette, layered depth.

Composition:
street-level exploration-game camera angle, bakery storefront on a German cobblestone street, warm yellow bakery light inside, wet cobblestone reflections, rain streaks, small signboard shape without readable text, bread display visible through the window, student with backpack and umbrella near the entrance. No UI, no dialogue box, no text overlay, no logo, no watermark.

Atmosphere:
heavy rain, early morning, dark navy sky, warm interior light, quiet first-year-abroad feeling, slightly lonely but hopeful.

Color palette:
dark navy rain shadows, warm bakery gold light, terracotta roof red, muted beige stone, wet gray cobblestones, moss green plants, cool blue reflections.

Negative prompt:
photorealistic, 3D render, anime, chibi, cyberpunk neon, fantasy shop, modern American storefront, poster layout, UI frame, text, logo, watermark, blurry edges, over-detailed noise.
```

---

# 17. 后处理建议

## 17.1 图标缩小

```text
512×512 → 64×64 / 48×48 / 32×32
```

缩小时使用 nearest-neighbor 或 pixelated sampling，不要使用平滑缩放。

## 17.2 地图纹理

```text
512×512 → 32×32 或 16×16
```

应检查是否可平铺。如不可平铺，需要人工或脚本做 seamless 处理。

## 17.3 白底裁切

资产图应自动裁切多余白边，但保留 5%-10% breathing room。

## 17.4 颜色统一

所有资产应尽量回到 gagaToday 色板。可以做轻微调色：降低饱和度、增加暗蓝阴影、控制屋顶红、保持石材米色、强化轮廓。

---

# 18. 最终统一判断标准

任何 gagaToday 图片都应通过以下检查：

1. 看起来是否属于德国留学生活模拟 RPG？
2. 是否不是照片、不是幻想、不是 anime、不是普通手游？
3. 是否有温暖但略孤独的留学氛围？
4. 是否能用于游戏界面或游戏内容？
5. 真实地标是否保留了关键特征？
6. 小尺寸下是否还能识别？
7. 颜色是否符合 gagaToday 色板？
8. 是否避免了错误背景、文字、logo、水印？
9. 是否能让玩家感到“这个地方可以进入、打卡、学习、探索”？
10. 是否具有 gagaToday 的专属感，而不是通用 pixel art？
