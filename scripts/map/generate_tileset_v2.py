#!/usr/bin/env python3
"""
16-bit 像素风 tileset 生成器 — 32×32 瓦片

输出: assets/munich_map/tileset.png (横向排列, 32×32 per tile)
"""

from PIL import Image, ImageDraw
import random

TILE_SIZE = 32

# ── FF6 灵感调色板 ──
C = {
    # 草地
    "g1": (0x3c, 0x7a, 0x3c),  # 深绿
    "g2": (0x4c, 0x8a, 0x4c),  # 中绿
    "g3": (0x5c, 0x9a, 0x5c),  # 浅绿
    "g4": (0x2c, 0x6a, 0x2c),  # 暗绿
    "g5": (0x6c, 0xaa, 0x5c),  # 高光
    "g6": (0x8c, 0xba, 0x6c),  # 草花点缀
    "g7": (0x3a, 0x6a, 0x3a),  # 过渡
    # 道路
    "r1": (0xb0, 0xa0, 0x78),  # 沙色主
    "r2": (0x98, 0x88, 0x60),  # 暗
    "r3": (0xc8, 0xb8, 0x88),  # 亮
    "r4": (0xd4, 0xc4, 0x94),  # 石面
    "r5": (0x80, 0x74, 0x54),  # 边缘
    "r6": (0x8c, 0x7c, 0x58),  # 石缝
    # 建筑
    "b1": (0x8c, 0x3a, 0x2c),  # 红瓦
    "b2": (0x9c, 0x4a, 0x3c),  # 红瓦亮
    "b3": (0x7c, 0x2e, 0x20),  # 红瓦暗
    "b4": (0x68, 0x5c, 0x4c),  # 墙面
    "b5": (0x7c, 0x6e, 0x5a),  # 墙面亮
    "b6": (0x54, 0x4a, 0x3c),  # 墙面暗
    "b7": (0xd8, 0xc8, 0xa0),  # 米色墙
    "b8": (0xc0, 0xb0, 0x88),  # 米色墙暗
    "b9": (0x4c, 0x3a, 0x2c),  # 深木色
    "b0": (0x6c, 0x5a, 0x44),  # 中木色
    # 窗户/门
    "w1": (0x2c, 0x40, 0x60),  # 窗玻璃
    "w2": (0x3c, 0x54, 0x78),  # 窗亮
    "w3": (0x1c, 0x2c, 0x44),  # 窗暗
    "d1": (0x3c, 0x2a, 0x1c),  # 门
    # 水面
    "a1": (0x38, 0x70, 0xa0),  # 水主
    "a2": (0x4c, 0x84, 0xb0),  # 水亮
    "a3": (0x2c, 0x60, 0x8c),  # 水暗
    "a4": (0x6c, 0xa4, 0xc8),  # 水高光
    # 公园
    "p1": (0x2c, 0x6a, 0x2c),  # 深树
    "p2": (0x3c, 0x7a, 0x3c),  # 树
    "p3": (0x4c, 0x8a, 0x3c),  # 树亮
    "p4": (0x5c, 0x9a, 0x3c),  # 树高光
    "p5": (0x6c, 0x54, 0x3c),  # 树干
    # 广场
    "s1": (0xd0, 0xc0, 0xa0),  # 石主
    "s2": (0xc0, 0xb0, 0x90),  # 石暗
    "s3": (0xe0, 0xd0, 0xb0),  # 石亮
    "s4": (0xb0, 0xa0, 0x80),  # 石缝
    # POI
    "y1": (0xf8, 0xd8, 0x28),  # 金
    "y2": (0xd8, 0xa0, 0x00),  # 暗金
    "y3": (0xff, 0xf8, 0x88),  # 闪光
    "y4": (0xc8, 0x88, 0x00),  # 金轮廓
    # 阴影
    "h1": (0x00, 0x00, 0x00),  # 黑
    "h2": (0x18, 0x18, 0x10),  # 轮廓
    "h3": (0x0a, 0x0e, 0x1a),  # 暗蓝
    "h4": (0x20, 0x28, 0x38),  # 深蓝
    # 羊皮纸
    "k1": (0xf0, 0xde, 0xb8),  # 羊皮纸主
    "k2": (0xe8, 0xd4, 0xa8),  # 暗
    "k3": (0xf4, 0xe6, 0xc8),  # 亮
    # 额外
    "x1": (0xa8, 0x5a, 0x3a),  # 棕色屋顶
    "x2": (0x8a, 0x4a, 0x2a),  # 棕色屋顶暗
    "x3": (0x5a, 0x8a, 0x5a),  # 灰绿
}


def new_tile():
    """创建一个空的 32×32 图像"""
    return Image.new("RGB", (TILE_SIZE, TILE_SIZE))


def put(img, x, y, color):
    """安全设置像素"""
    if 0 <= x < TILE_SIZE and 0 <= y < TILE_SIZE:
        img.putpixel((x, y), color)


def vline(img, x, y0, y1, color):
    """画竖线"""
    for y in range(max(0, y0), min(TILE_SIZE, y1 + 1)):
        put(img, x, y, color)


def hline(img, y, x0, x1, color):
    """画横线"""
    for x in range(max(0, x0), min(TILE_SIZE, x1 + 1)):
        put(img, x, y, color)


def rect(img, x, y, w, h, color, fill=False):
    """矩形"""
    draw = ImageDraw.Draw(img)
    if fill:
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)
    else:
        draw.rectangle([x, y, x + w - 1, y + h - 1], outline=color)


def fill_rect(img, x, y, w, h, color):
    """填充矩形"""
    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def fill_tile(img, color):
    """填充整个 tile"""
    fill_rect(img, 0, 0, TILE_SIZE, TILE_SIZE, color)


# ── Tile 0: 草地 (3 种变体) ──
def grass_variant(seed):
    random.seed(seed)
    img = new_tile()
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            n = random.random()
            if n < 0.55:
                img.putpixel((x, y), C["g2"])
            elif n < 0.82:
                img.putpixel((x, y), C["g1"])
            else:
                img.putpixel((x, y), C["g3"])

    # 暗色 patches
    for _ in range(3):
        cx, cy = random.randint(4, 27), random.randint(4, 27)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if abs(dx) + abs(dy) <= 3:
                    put(img, cx + dx, cy + dy, C["g4"])

    # 小黄花
    for _ in range(4):
        fx, fy = random.randint(2, 29), random.randint(2, 29)
        put(img, fx, fy, C["g6"])
    return img


def grass_tile_0():
    return grass_variant(42)

def grass_tile_1():
    return grass_variant(99)

def grass_tile_2():
    return grass_variant(201)

# ── Tile 1: 道路 ──
def road_tile():
    img = new_tile()
    # 底色
    fill_tile(img, C["r1"])
    # 石纹理
    random.seed(7)
    for _ in range(40):
        x, y = random.randint(0, 31), random.randint(0, 31)
        img.putpixel((x, y), C["r2"])
    for _ in range(20):
        x, y = random.randint(0, 31), random.randint(0, 31)
        img.putpixel((x, y), C["r3"])
    # 车道虚线 (水平方向, 暗示道路走向)
    ym = random.randint(12, 20)
    for x in range(0, 32, 6):
        fill_rect(img, x, ym, 3, 2, C["r4"])
    # 边缘暗
    for x in range(32):
        put(img, x, 0, C["r5"])
        put(img, x, 31, C["r5"])
    for y in range(32):
        put(img, 0, y, C["r5"])
        put(img, 31, y, C["r5"])
    # 路面上的一些小石缝
    random.seed(13)
    for _ in range(8):
        put(img, random.randint(4, 27), random.randint(4, 27), C["r6"])
    return img


# ── Tile 2: 建筑 (多种变体) ──
def building_v0():
    """红瓦屋顶 + 米色墙"""
    img = new_tile()
    # 屋顶 (上 20px)
    fill_rect(img, 0, 0, 32, 20, C["b1"])
    # 屋顶瓦片纹理
    for y in range(2, 20, 4):
        for x in range(0, 32, 4):
            if (x // 4 + y // 4) % 2 == 0:
                fill_rect(img, x, y, 3, 3, C["b2"])
            else:
                fill_rect(img, x, y, 3, 3, C["b3"])
    # 屋顶边缘阴影
    fill_rect(img, 0, 18, 32, 2, C["h2"])
    # 墙面 (下 12px)
    fill_rect(img, 0, 20, 32, 12, C["b7"])
    # 窗户
    for wx in [6, 14, 22]:
        fill_rect(img, wx, 23, 4, 4, C["w1"])
        fill_rect(img, wx + 1, 23, 2, 2, C["w2"])
    # 门
    fill_rect(img, 12, 26, 8, 6, C["d1"])
    fill_rect(img, 15, 26, 2, 5, C["w3"])
    # 地面阴影
    fill_rect(img, 0, 20, 32, 1, C["h2"])
    return img


def building_v1():
    """灰蓝色屋顶 + 白色墙"""
    img = new_tile()
    fill_rect(img, 0, 0, 32, 20, C["x3"])
    for y in range(2, 20, 4):
        for x in range(0, 32, 4):
            if (x // 4 + y // 4) % 2 == 0:
                fill_rect(img, x, y, 3, 3, C["g7"])
    fill_rect(img, 0, 18, 32, 2, C["h2"])
    fill_rect(img, 0, 20, 32, 12, C["k1"])
    for wx in [4, 12, 20]:
        fill_rect(img, wx, 22, 5, 5, C["w3"])
        fill_rect(img, wx + 1, 23, 3, 3, C["w1"])
    fill_rect(img, 13, 26, 6, 6, C["b9"])
    return img


def building_v2():
    """棕色屋顶 + 深色墙 + 烟囱"""
    img = new_tile()
    fill_rect(img, 0, 0, 32, 18, C["x1"])
    for y in range(2, 18, 4):
        for x in range(0, 32, 4):
            if (x // 4 + y // 4) % 2 == 0:
                fill_rect(img, x, y, 3, 3, C["x2"])
    # 烟囱
    fill_rect(img, 24, 2, 5, 10, C["b6"])
    fill_rect(img, 24, 2, 5, 2, C["b4"])
    fill_rect(img, 0, 16, 32, 2, C["h2"])
    fill_rect(img, 0, 18, 32, 14, C["b4"])
    for wx in [5, 13, 21]:
        fill_rect(img, wx, 21, 4, 4, C["w1"])
        fill_rect(img, wx + 1, 21, 2, 3, C["w2"])
    fill_rect(img, 12, 26, 8, 6, C["d1"])
    return img


def building_v3():
    """大建筑 - 古典风格 (公共建筑)"""
    img = new_tile()
    # 山形墙
    draw = ImageDraw.Draw(img)
    draw.polygon([(0, 12), (16, 0), (32, 12)], fill=C["b1"], outline=C["b3"])
    # 屋顶剩余
    fill_rect(img, 0, 12, 32, 8, C["b2"])
    # 檐口
    fill_rect(img, 0, 18, 32, 2, C["k1"])
    # 墙面
    fill_rect(img, 0, 20, 32, 12, C["k2"])
    # 大窗
    fill_rect(img, 4, 22, 8, 7, C["w3"])
    fill_rect(img, 6, 23, 4, 5, C["w1"])
    fill_rect(img, 20, 22, 8, 7, C["w3"])
    fill_rect(img, 22, 23, 4, 5, C["w1"])
    # 大门
    fill_rect(img, 13, 25, 6, 7, C["b9"])
    return img


def building_v4():
    """小房子"""
    img = new_tile()
    fill_rect(img, 2, 4, 28, 12, C["x1"])
    for y in range(6, 14, 4):
        for x in range(4, 30, 4):
            if (x // 4 + y // 4) % 2 == 0:
                fill_rect(img, x, y, 3, 3, C["x2"])
    fill_rect(img, 0, 14, 32, 2, C["h2"])
    fill_rect(img, 0, 16, 32, 16, C["b7"])
    for wx in [6, 18]:
        fill_rect(img, wx, 19, 4, 4, C["w1"])
    fill_rect(img, 12, 22, 6, 10, C["d1"])
    return img


BUILDING_VARIANTS = [building_v0, building_v1, building_v2, building_v3, building_v4]


# ── Tile 3: 人行道 ──
def sidewalk_tile():
    img = new_tile()
    fill_tile(img, C["k2"])
    # 石板分割
    for x in [7, 15, 23]:
        vline(img, x, 0, 31, C["s4"])
    for y in [7, 15, 23]:
        hline(img, y, 0, 31, C["s4"])
    # 石板高光
    for gy in range(0, 4):
        for gx in range(0, 4):
            cx, cy = gx * 8 + 1, gy * 8 + 1
            fill_rect(img, cx, cy, 5, 5, C["k3"])
            img.putpixel((cx + 1, cy + 1), C["s3"])
    return img


# ── Tile 4: 水面 ──
def water_tile():
    img = new_tile()
    fill_tile(img, C["a1"])
    # 波纹
    for y in [4, 12, 20, 28]:
        for x in range(0, 32, 5):
            fill_rect(img, x, y, 3, 2, C["a2"])
    for y in [8, 16, 24]:
        for x in range(2, 32, 5):
            fill_rect(img, x, y, 2, 1, C["a4"])
    # 暗纹
    for y in [6, 14, 22]:
        for x in range(1, 32, 6):
            fill_rect(img, x, y, 2, 2, C["a3"])
    # 反光点
    random.seed(55)
    for _ in range(6):
        put(img, random.randint(4, 27), random.randint(4, 27), C["a4"])
    return img


# ── Tile 5: 公园/树丛 ──
def park_tile():
    img = new_tile()
    # 地面
    fill_tile(img, C["p1"])
    random.seed(31)
    for _ in range(60):
        x, y = random.randint(1, 30), random.randint(1, 30)
        img.putpixel((x, y), C["p2"] if random.random() < 0.5 else C["p3"])
    # 树冠 (4团)
    for ox, oy in [(6, 6), (20, 8), (14, 18), (26, 22)]:
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                d = abs(dx) + abs(dy)
                if d <= 4 and random.random() < 0.7:
                    c = C["p2"] if d <= 2 else C["p3"]
                    put(img, ox + dx, oy + dy, c)
                if d <= 2 and random.random() < 0.4:
                    put(img, ox + dx, oy + dy, C["p4"])
    # 树干
    for tx, ty in [(6, 16), (22, 18), (14, 26), (24, 28)]:
        for dy in range(0, 3):
            put(img, tx - 1, ty + dy, C["p5"])
            put(img, tx, ty + dy, C["p5"])
    return img


def park_tile_2():
    """小花园"""
    img = new_tile()
    fill_tile(img, C["g2"])
    random.seed(88)
    for _ in range(30):
        x, y = random.randint(1, 30), random.randint(1, 30)
        c = random.choice([C["g1"], C["g3"], C["g4"], C["g6"]])
        img.putpixel((x, y), c)
    # 花坛
    for cx, cy in [(8, 8), (24, 22)]:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                d = abs(dx) + abs(dy)
                if d <= 3:
                    c = (0xd0 + random.randint(0, 0x30), 0x30 + random.randint(0, 0x30), 0x30 + random.randint(0, 0x30))
                    put(img, cx + dx, cy + dy, c)
    return img


# ── Tile 6: 广场/石铺地 ──
def plaza_tile():
    img = new_tile()
    fill_tile(img, C["s1"])
    # 石缝网格
    for x in [7, 15, 23]:
        vline(img, x, 0, 31, C["s4"])
    for y in [7, 15, 23]:
        hline(img, y, 0, 31, C["s4"])
    # 石面差异
    random.seed(71)
    for _ in range(25):
        x, y = random.randint(2, 29), random.randint(2, 29)
        img.putpixel((x, y), C["s2"] if random.random() < 0.5 else C["s3"])
    return img


# ── Tile 7: POI 标记 ──
def poi_marker_tile():
    """金色星标高亮瓦片"""
    img = new_tile()
    fill_tile(img, C["s1"])
    # 金色菱形
    draw = ImageDraw.Draw(img)
    diamond = [
        (16, 2), (16, 3), (16, 4),
        (15, 5), (16, 5), (17, 5),
        (14, 6), (15, 6), (16, 6), (17, 6), (18, 6),
        (13, 7), (14, 7), (15, 7), (16, 7), (17, 7), (18, 7), (19, 7),
        (12, 8), (13, 8), (14, 8), (15, 8), (16, 8), (17, 8), (18, 8), (19, 8), (20, 8),
    ]
    for x, y in diamond:
        img.putpixel((x, y), C["y1"])
    for x, y in [(16, 5), (15, 6), (16, 6), (17, 6)]:
        img.putpixel((x, y), C["y3"])
    # 轮廓
    for x, y in diamond:
        if x in [12, 20] or y in [2, 3, 4, 8]:
            continue
    # 光晕效果
    for r in range(4, 8):
        draw.ellipse([16 - r, 4 - r, 16 + r, 4 + r], outline=C["y2"])
    return img


def poi_marker_tile_2():
    """旗帜标记"""
    img = new_tile()
    fill_tile(img, C["k2"])
    # 旗杆
    vline(img, 16, 4, 26, C["b9"])
    # 旗帜 (三角)
    draw = ImageDraw.Draw(img)
    draw.polygon([(17, 5), (28, 10), (17, 15)], fill=C["y1"], outline=C["y4"])
    # 底座
    fill_rect(img, 13, 26, 6, 3, C["b6"])
    return img


# ── Tile 8: 羊皮纸底色 (空) ──
def parchment_tile():
    img = new_tile()
    fill_tile(img, C["k1"])
    # 轻微纹理
    random.seed(173)
    for _ in range(15):
        x, y = random.randint(1, 30), random.randint(1, 30)
        img.putpixel((x, y), C["k2"])
    return img


# ┌──────────────────────────────────────────────┐
# │  tileset 布局: 每个序号可包含多个变体          │
# │  0: 草地 (x3)  1: 道路  2: 建筑 (x5)         │
# │  3: 人行道  4: 水面  5: 公园 (x2)             │
# │  6: 广场  7: POI (x2)  8: 羊皮纸              │
# └──────────────────────────────────────────────┘
TILE_GROUPS = [
    ("grass", [grass_tile_0, grass_tile_1, grass_tile_2]),
    ("road", [road_tile]),
    ("building", BUILDING_VARIANTS),
    ("sidewalk", [sidewalk_tile]),
    ("water", [water_tile]),
    ("park", [park_tile, park_tile_2]),
    ("plaza", [plaza_tile]),
    ("poi", [poi_marker_tile, poi_marker_tile_2]),
    ("parchment", [parchment_tile]),
]


def main():
    random.seed(42)

    # 总瓦片数 = 各 group 变体和
    total_tiles = sum(len(v) for _, v in TILE_GROUPS)
    tileset_w = TILE_SIZE * total_tiles
    tileset_h = TILE_SIZE
    tileset = Image.new("RGB", (tileset_w, tileset_h))

    idx = 0
    offset = 0
    for name, variants in TILE_GROUPS:
        for fn in variants:
            tile_img = fn()
            tileset.paste(tile_img, (offset * TILE_SIZE, 0))
            offset += 1
            idx += 1

    out_path = "assets/munich_map/tileset.png"
    tileset.save(out_path)
    print(f"💾 tileset.png 已保存 ({total_tiles} tiles × {TILE_SIZE}px)")
    print(f"   瓦片索引: 0-2 草地 | 3 道路 | 4-8 建筑 | 9 人行道 | 10 水面 | 11-12 公园 | 13 广场 | 14-15 POI | 16 羊皮纸")
    print("✅ 完成!")


if __name__ == "__main__":
    main()
