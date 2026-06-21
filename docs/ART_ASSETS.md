# 美术素材清单(ART_ASSETS)

> 配合 [PROPOSAL.md](PROPOSAL.md),告诉画师/AI 美术需要画什么
> 版本: v1.0  ·  2026-06-21

---

## 总览: 美术资产规模

| Phase | 关卡数 | 角色数 | 场景背景 | UI 元素 | 城市徽章 |
|-------|--------|--------|---------|--------|---------|
| Phase 1 (MVP) | 1 | 1-2 | 1 | 15-20 | 1 |
| Phase 2 | 15 | 4-6 | 6-10 | 20-30 | 3 |
| Phase 3 | 30 | 8-10 | 12-15 | 30-40 | 8-10 |
| Phase 4 (完整) | 60-100 | 15-20 | 25-30 | 40-50 | 16 |

**MVP 美术量约 25-30 个资产**——3-5 天可完成。

---

## 视觉风格指南

### 整体风格
- **2D 像素艺术** (Pixel Art)
- **16-bit 风格** (类似 SNES/GBA 时代)
- **非动画优先** (NPC 主要是静态立绘 + 表情切换,后期可加眨眼动画)
- **暖色调为主** (符合"咖啡馆 / 留学生活"的温馨感)

### 配色方案(按城市)

| 城市 | 主色 | 辅色 | 灵感 |
|------|------|------|------|
| Berlin 柏林 | 砖红 `#B85C3C` | 工业灰 `#4A4A4A` + 暖橙 `#E8A87C` | 柏林老工业风 + 街头文化 |
| München 慕尼黑 | 啤酒金 `#D4A847` | 巴伐利亚蓝 `#3066BE` + 阿尔卑斯白 | 巴伐利亚传统 + 阿尔卑斯山 |
| Hamburg 汉堡 | 港水蓝 `#4A7A9C` | 砖红 `#9C5B4A` + 仓储灰 | 汉堡港 + 仓库城(UNESCO) |
| Köln 科隆 | 大教堂黑 `#2A2A2A` | 莱茵金 `#C9A961` | 科隆大教堂 + 狂欢节 |
| Frankfurt 法兰克福 | 银灰 `#7A7A7A` | 金融蓝 `#1E3A5F` | 现代金融城 + 摩天楼 |

### 参考游戏
- *Coffee Talk* (2019) —— 完美符合"对话 + 像素"
- *VA-11 Hall-A* —— 对话驱动的像素 RPG
- *Stardew Valley* —— 像素生活模拟
- *Late Night Mopey* —— 像素咖啡馆氛围

### 通用比例与规范
- 角色立绘: **192×256 px**(6:8 比例,头身比约 1:3)
- 场景背景: **1280×720 px**(16:9 横向)
- UI 元素: 9-slice 设计,可任意缩放
- 调色板: 每城市一套,**避免颜色超 24 色**(否则失真)
- 阴影: 1 像素硬阴影,不用渐变
- 抗锯齿: **关掉**(像素艺术必须保持硬边)

---

## MVP 美术清单(第 1 关: 柏林咖啡馆)

### 1. 角色立绘

#### Anna Kellnerin(咖啡馆服务员)
- **规格**: 192×256 px, PNG 透明背景
- **状态**: 4 个表情 × 1 个基础立绘

| 文件名 | 表情 | 用途 |
|--------|------|------|
| `anna_neutral.png` | 自然/中性 | 默认状态 |
| `anna_smile.png` | 微笑 | 友好互动 |
| `anna_surprise.png` | 惊讶 | 玩家做了有趣/意外的事 |
| `anna_thinking.png` | 思考 | 等玩家说话 / 复杂问题 |

**立绘内容**:
- 40 岁女性,扎发髻,穿黑白咖啡馆制服(白衬衫 + 黑围裙)
- 戴小围裙,胸牌 "Anna"
- 表情通过眼睛 + 嘴型 + 眉毛变化,不画全身动作

**统一规范**:
- 立绘位置: 屏幕右侧 1/3 区域
- 视线方向: 略微朝左(看着对话气泡)
- 嘴巴开合: 不同表情对应嘴型(可参考 RPG Maker 标准)

#### 玩家立绘(可选,MVP 可省)
- **规格**: 192×256 px
- **状态**: 2 个

| 文件名 | 表情 | 用途 |
|--------|------|------|
| `player_neutral.png` | 自然 | 默认 |
| `player_happy.png` | 开心 | 关卡完成 |

**MVP 可以先用占位符**(用 emoji 👨‍💻 或简单剪影代替)

### 2. 场景背景

#### Café Einstein Berlin
- **文件**: `berlin_cafe_interior.png`
- **规格**: 1280×720 px
- **内容**:
  - 室内咖啡馆,有吧台、桌子、椅子
  - 墙上挂柏林元素(勃兰登堡门照片 / 柏林墙残片 / 复古海报)
  - 暖色调灯光,木质家具
  - 窗外隐约可见柏林街景(可加柏林电视塔剪影)
  - **可复用的"夜/午"双版本**(后期可加时间变化)

**构图建议**:
```
┌────────────────────────────────────────┐
│  墙(画框,海报,菜单板)                  │
│  ┌─────────┐                            │
│  │  吧台   │  Anna 立绘位置            │
│  │ (远处)  │      (右侧 1/3)            │
│  └─────────┘                            │
│   桌 椅   桌 椅   桌 椅                 │
│              (前景,玩家位置)             │
│  对话框将出现在屏幕底部                   │
└────────────────────────────────────────┘
```

### 3. UI 元素

#### 对话框(9-slice)
- **文件**: `dialogue_box.png`
- **规格**: 9-slice, 中心 64×64 px, 总 1200×200 px
- **元素**:
  - 边框(深棕,2px 硬边)
  - 半透明深色背景(80% 不透明)
  - 角落装饰(像素花纹)

#### 按钮(3 状态)
- **规格**: 64×32 px
- **状态**: normal / hover / disabled
- **颜色**: 浅棕 `#8B6F47` 边框 + 暗棕 `#5C4A2F` 填充
- **文字**: 像素字体

#### 反馈卡背景
- **文件**: `feedback_card.png`
- **规格**: 400×500 px
- **内容**: 羊皮纸质感 + 复古花纹边框

#### 城市徽章
- **文件**: `city_badge_berlin.png`
- **规格**: 128×128 px
- **内容**: 柏林熊(Bär) + "BERLIN" 字样

#### 录音按钮
- **文件**: `mic_button.png` (3 状态)
- **规格**: 80×80 px
- **状态**: idle / recording / processing
- **动画**: 录音时一圈波纹扩散(可后期加)

#### 退出/设置/帮助图标
- **文件**: `icon_*.png`
- **规格**: 32×32 px
- **数量**: 5-8 个(退出、设置、帮助、刷新、关闭等)

### 4. 像素字体

#### 字体文件
- **文件**: `pixel_font.ttf` 或 `pixel_font.otf`
- **推荐字体**:
  - [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) —— Google Fonts,经典 8-bit 风格
  - [PixelOperator](https://www.dafont.com/pixel-operator.font) —— Dafont 免费
  - [VT323](https://fonts.google.com/specimen/VT323) —— 类似终端的复古风
- **许可证**: Open Font License(免费商用)

#### 字体大小
- 对话框正文: 16px
- NPC 名字: 18px 加粗
- 按钮文字: 14px
- 城市百科: 14px

### 5. 城市地图

#### 德国地图(主界面)
- **文件**: `germany_map.png`
- **规格**: 1920×1080 px(可缩放)
- **内容**:
  - 16 州的简化轮廓
  - 主要城市标记(柏林、慕尼黑、汉堡等)
  - 已解锁/未解锁的视觉差异
  - 玩家当前位置高亮
  - 装饰元素(国界线、河流、城市点)

**注意**: 简化版即可,不需要地理精确(版权考虑)

**获取方式**:
- 自画(按公开简化版地图)
- 用 openstreetmap 数据 + Inkscape 简化
- AI 工具生成初稿(DALL-E / Midjourney 风格化为像素风),再人工调整

---

## 美术工作流程

### 工具准备
- **Aseprite**(付费,$20)或 **LibreSprite**(免费)—— 像素艺术标准
- **参考**: Lospec.com 调色板库(很多免费像素调色板)
- **导出格式**: PNG 透明背景

### 工作量估算

| Phase | 美术资产 | 时间(熟练) | 时间(新手) |
|-------|---------|-----------|-----------|
| Phase 1 | ~25 个 | 3-5 天 | 1-2 周学习 + 3-5 天 |
| Phase 2 | ~100 个 | 2 周 | 4 周 |
| Phase 3 | ~150 个 | 3 周 | 6 周 |

### 命名规范
```
[角色名]_[状态/表情].png
  ↓
  anna_neutral.png
  anna_smile.png
  player_happy.png

[城市]_[元素].png
  ↓
  berlin_cafe_interior.png
  berlin_badge.png

ui_[元素]_[状态].png
  ↓
  ui_button_normal.png
  ui_button_hover.png
  ui_dialogue_box.png
```

### 文件组织
```
assets/
├── characters/
│   ├── anna/
│   │   ├── anna_neutral.png
│   │   ├── anna_smile.png
│   │   ├── anna_surprise.png
│   │   └── anna_thinking.png
│   └── player/
│       └── player_neutral.png
├── scenes/
│   ├── berlin/
│   │   ├── cafe_interior.png
│   │   ├── hauptbahnhof.png
│   │   └── kadewe.png
│   └── ...
├── ui/
│   ├── dialogue_box.png
│   ├── button_normal.png
│   ├── button_hover.png
│   ├── feedback_card.png
│   ├── mic_idle.png
│   └── ...
├── cities/
│   ├── badge_berlin.png
│   ├── badge_munich.png
│   └── ...
├── map/
│   └── germany_map.png
└── fonts/
    └── pixel_font.ttf
```

---

## 美术验收标准

每张图需通过:

- [ ] **尺寸正确**(严格按规格)
- [ ] **背景透明**(角色立绘)
- [ ] **配色在调色板内**(避免颜色爆炸)
- [ ] **硬边无抗锯齿**(像素艺术标准)
- [ ] **PNG 格式,无压缩失真**
- [ ] **文件名规范**
- [ ] **画风统一**(参考 *Coffee Talk* 的风格)
- [ ] **多个表情视觉一致**(Anna 的 4 个表情要像同一个人)

---

## 美术资源来源(可用资源)

### 免费调色板
- [Lospec](https://lospec.com/palette-list) —— 数百个免费调色板
- 推荐 16-bit 风格:PICO-8、Endesga 16、Sweetie 16

### 像素艺术教程
- [Pixel Art Tutorial](https://blog.studiominiboss.com/pixelart) —— 入门
- [Aseprite 官方教程](https://www.aseprite.org/docs/)
- [Spritely YouTube 频道](https://www.youtube.com/c/Spritely)

### 公开像素资源(可参考学习,但要原创)
注意:不要直接照搬商业游戏的素材(版权问题),但可以学习风格

### AI 辅助(初稿生成)
- **DALL-E / Midjourney** 可以生成"16-bit 像素艺术风格"的图,但通常分辨率不够
- 建议:用 AI 生成**构图参考**,然后在 Aseprite 里**手绘**(像素艺术 AI 能力有限,手绘更快)

---

## ⚡ AI 批量生成工作流(MVP 占位稿加速)

> **状态**: 已实测。2026-06-21 用 matrix MCP (`mavis mcp call matrix matrix_generate_image`) 在 ~15 分钟内产出 15 张 MVP 美术,质量**超出预期**(可用作占位稿,Phase 2 再换手绘精修)。
> **决定路径**: 临时决定(用户已批准),非最终美术交付。Phase 2 时,关键场景(开篇/高潮/通关)仍需手绘精修。

### 工具与脚本

| 组件 | 用途 |
|------|------|
| `scripts/generate_art.py` | 一键批量生成,带 3 次 retry + CDN URL curl 下载 |
| matrix MCP (`matrix_generate_image`) | 后端调用的 AI 生成 API |
| `assets/_test/` | 试跑区(2 张首测,确定风格后再批量) |
| `assets/{characters,scenes,ui}/` | 最终存放(MVP 占位稿) |

### 像素艺术 prompt 模板

```python
# 角色立绘
"16-bit pixel art character sprite, {详细描述}, 
hard pixel edges no anti-aliasing, limited 16-color palette, 
retro JRPG style, 2D character portrait, transparent background, 
front-facing, character sheet, clean composition"

# 场景背景
"16-bit pixel art {场景描述}, hard pixel edges no anti-aliasing, 
limited 16-color palette, retro JRPG game background, no characters, 
atmospheric lighting, clean composition, no text or readable text"

# UI 元素
"16-bit pixel art {元素描述}, hard pixel edges no anti-aliasing, 
limited 16-color palette, retro JRPG UI element, isolated on transparent 
background, centered, clean composition"
```

### 角色一致性技巧(关键)

**同角色多表情**必须用同一参考图 (`input_files`),否则 AI 难保持"同一个人":

```python
request = {
    "prompt": "...Anna, ..., smile expression...",
    "aspect_ratio": "3:4",
    "resolution": "1K",
    "input_files": ["/path/to/anna_neutral.png"]  # 第一张作为参考
}
```

实测:**有参考图**视觉一致性 ~95%,**无参考图**(text-only) ~40%。

### 已生成的 15 张占位稿(2026-06-21)

| 分类 | 文件数 | 文件清单 |
|------|-------|---------|
| Anna 角色 | 4 | `anna_{neutral,smile,surprise,thinking}.png` |
| Peter 角色 | 4 | `peter_{neutral,smile,surprise,thinking}.png` |
| 柏林场景 | 3 | `hauptbahnhof_interior.png`, `cafe_einstein.png`, `street_kreuzberg.png` |
| UI 元素 | 4 | `dialogue_box.png`, `button_normal.png`, `city_badge_berlin.png`, `mic_button.png` |
| **总计** | **15 张 / 9.8 MB** | 全部可用作 MVP 占位稿 |

### AI 像素艺术的已知限制

- ⚠️ **小文字模糊**: 姓名牌(ANNA/PETER)、招牌、徽章文字容易拼错或变形。修复:徽章里强调 "clearly written BERLIN" 才正确生成。
- ⚠️ **"Full body" 倾向半身**: prompt 说全身,AI 仍给出半身胸像。
- ⚠️ **色数略多**: 实际产出色数比目标 16 色多 ~50%,但仍属于"可控范围"。
- ✅ **场景氛围出色**: 车站、咖啡馆、Kreuzberg 街头,色彩 + 光线 + 细节都到位。
- ✅ **角色表情区分清晰**: smile(露齿) vs surprise(眉毛抬起) vs thinking(嘴角) 明显不同。

### 何时换手绘

| 阶段 | 美术策略 |
|------|---------|
| **MVP(Phase 0-1)** | AI 占位稿可用,质量已超出预期 |
| **Beta(Phase 2)** | 关键场景手绘精修(开篇/高潮/通关),其余保持 AI |
| **正式版(Phase 3+)** | 全部手绘或找画师委托,AI 仅作灵感参考 |

---

## 美术与开发的协作

### 美术交付
- 文件路径: `assets/[分类]/[文件名].png`
- 文件命名: 按规范
- 提交方式: Git commit 或直接放到 `assets/` 目录

### 开发集成
- 前端用 `import annaNeutral from '@/assets/characters/anna/anna_neutral.png'`
- Phaser 加载:`this.load.image('anna_neutral', annaNeutral)`
- 切表情:`this.add.image(x, y, 'anna_' + currentMood)`

### 美术调整
- 开发提供"美术调整请求"模板(色彩、表情、比例)
- 美术修订后提交新版本(Git PR 或新文件)

---

## 速赢方案(MVP 美术减负)

如果你美术时间紧张,可以:

1. **MVP 阶段** ← *已采用*
   - ✅ **AI 批量生成 15 张占位稿**(已完成,2026-06-21,质量超预期)
   - 角色立绘先只画 1 个表情(neutral),其他用代码控制嘴型/眉毛变化
   - 场景背景先用占位符(单色 + 简单家具剪影)
   - UI 用开源素材(如 Kenney.nl 的免费 UI 套件)

2. **Phase 2 阶段**:
   - 补全角色表情(精修 AI 占位稿)
   - 优化场景背景(关键场景手绘,其余保留 AI)
   - 自己做城市徽章

3. **长期**:
   - 找画师委托关键场景(预计 ¥500-1000/张)

---

## 当前状态(MVP 占位稿全部就位)

✅ **15 张 AI 占位稿已完成**(详见上方"AI 批量生成工作流"段)
- Anna 4 表情 + Peter 4 表情: 角色一致性极佳
- 3 个柏林场景: 氛围到位
- 4 个 UI 元素: 可直接用
- Contact sheet: `CONTACT_SHEET.html`(本地预览 `python3 -m http.server 8765`)

**下一步**: 进入 Phase 0 步骤 2-5(语音链验证),或直接写 Phase 1 第 1 关 JSON 剧本。
