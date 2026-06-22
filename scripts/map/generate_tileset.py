#!/usr/bin/env python3
"""
生成 FF6 风格 16x16 像素 tileset
输出: frontend/public/assets/munich_map/tileset.png

调色板参考 FF6 (SNES) 风格:
- 限制色数, 低饱和度, 硬边
"""

from PIL import Image

TILE_SIZE = 16  # px

# ── FF6 灵感调色板 (R, G, B) ──
COLORS = {
    "grass_1":     (0x3c, 0x7a, 0x3c),  # 深绿
    "grass_2":     (0x4c, 0x8a, 0x4c),  # 中绿 (高光)
    "grass_3":     (0x2c, 0x6a, 0x2c),  # 暗绿
    "grass_dot":   (0x5c, 0x9a, 0x4c),  # 点缀浅绿
    "road_1":      (0xb8, 0xa8, 0x7c),  # 沙色主
    "road_2":      (0xa0, 0x90, 0x68),  # 沙色暗
    "road_3":      (0xc8, 0xb8, 0x88),  # 沙色亮
    "road_line":   (0xd4, 0xc4, 0x94),  # 道路中线
    "build_1":     (0x68, 0x5c, 0x4c),  # 建筑墙主
    "build_2":     (0x7c, 0x6e, 0x5a),  # 建筑墙亮
    "build_3":     (0x54, 0x4a, 0x3c),  # 建筑墙暗
    "build_roof":  (0x8c, 0x3a, 0x2c),  # 屋顶红
    "build_door":  (0x3c, 0x2a, 0x1c),  # 门
    "roof_tile":   (0x9c, 0x4a, 0x3c),  # 屋顶瓦亮
    "sidewalk_1":  (0xbc, 0xb4, 0xa8),  # 人行道主
    "sidewalk_2":  (0xcc, 0xc4, 0xb8),  # 人行道亮
    "water_1":     (0x38, 0x70, 0xa0),  # 水面主
    "water_2":     (0x4c, 0x84, 0xb0),  # 水面亮
    "water_3":     (0x2c, 0x60, 0x8c),  # 水面临
    "park_1":      (0x2c, 0x6a, 0x2c),  # 公园绿
    "park_2":      (0x3c, 0x7a, 0x3c),  # 公园亮
    "park_3":      (0x4c, 0x8a, 0x2c),  # 公园点缀
    "plaza_1":     (0xd0, 0xc0, 0xa0),  # 广场石主
    "plaza_2":     (0xc0, 0xb0, 0x90),  # 广场石暗
    "poi_fg":      (0xf8, 0xd8, 0x28),  # POI 前景 (金)
    "poi_bg":      (0xd8, 0xa0, 0x00),  # POI 背景 (暗金)
    "poi_spark":   (0xff, 0xf8, 0x88),  # POI 闪光
    "black":       (0x00, 0x00, 0x00),
    "outline":     (0x18, 0x18, 0x10),  # 建筑轮廓
}


def make_tile(pixels_16x16):
    """从 16x16 颜色名矩阵创建 tile (PIL Image)"""
    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE))
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            cname = pixels_16x16[y][x] if isinstance(pixels_16x16[y], (list, tuple)) else pixels_16x16[y]
            img.putpixel((x, y), COLORS.get(cname, COLORS["black"]))
    return img


def grass_tile():
    """🌿 草地"""
    p = [["grass_1"] * 16 for _ in range(16)]
    # 随机纹理
    import random
    random.seed(42)
    noise_spots = [(random.randint(0,15), random.randint(0,15)) for _ in range(20)]
    for x, y in noise_spots:
        if p[y][x] == "grass_1":
            p[y][x] = "grass_2" if random.random() < 0.5 else "grass_dot"
    # 暗影
    for y in range(16):
        for x in range(16):
            if (x + y) % 13 == 0:
                p[y][x] = "grass_3"
    return p


def road_tile():
    """🛣️ 道路"""
    p = [["road_1"] * 16 for _ in range(16)]
    # 车道线
    for x in range(6, 10):
        for y in [2, 5, 8, 11, 14]:
            p[y][x] = "road_line"
    # 边缘暗
    for x in [0, 15]:
        for y in range(16):
            p[y][x] = "road_2"
    for y in [0, 15]:
        p[y] = ["road_2"] * 16
    # 随机杂色
    import random
    random.seed(7)
    for _ in range(8):
        x, y = random.randint(2, 13), random.randint(2, 13)
        p[y][x] = "road_3"
    return p


def building_tile():
    """🏠 建筑 (上色俯视图)"""
    import random
    random.seed(13)

    # 屋顶基色
    base = random.choice(["build_1", "build_2"]) if random.random() < 0.5 else "build_roof"
    if base in ("build_1", "build_2"):
        roof_c = base
        accent = "build_3"
    else:
        roof_c = "build_roof"
        accent = "roof_tile"

    p = [[roof_c] * 16 for _ in range(16)]

    # 屋顶线 (模拟瓦片/金属板)
    for y in range(0, 16, 4):
        for x in range(16):
            p[y][x] = accent

    # 阴影边缘
    for x in [0, 15]:
        for y in range(16):
            p[y][x] = "build_3"
    for y in [0, 15]:
        p[y] = ["build_3"] * 16

    # 窗户 (小亮点)
    for y in range(3, 14, 4):
        for x in range(3, 14, 4):
            if random.random() < 0.6:
                p[y][x] = "sidewalk_2"
                p[y][x+1] = "sidewalk_2"
                p[y+1][x] = "sidewalk_2"
                p[y+1][x+1] = "sidewalk_2"
    return p


def sidewalk_tile():
    """人行道"""
    p = [["sidewalk_1"] * 16 for _ in range(16)]
    # 石板缝
    for x in [3, 7, 11]:
        for y in range(16):
            p[y][x] = "road_2"
    for y in [3, 7, 11]:
        p[y] = [("road_2" if x in [3, 7, 11] else "sidewalk_1") for x in range(16)]
        p[y][3] = "road_2"
        p[y][7] = "road_2"
        p[y][11] = "road_2"
    # 高光
    import random
    random.seed(23)
    for _ in range(6):
        x, y = random.randint(1, 14), random.randint(1, 14)
        if p[y][x] == "sidewalk_1":
            p[y][x] = "sidewalk_2"
    return p


def water_tile():
    """💧 水面 (带波纹)"""
    p = [["water_1"] * 16 for _ in range(16)]
    # 波纹线
    for y in [2, 6, 10, 14]:
        for x in range(0, 16, 3):
            if x+1 < 16:
                p[y][x] = "water_2"
                p[y][x+1] = "water_2"
    # 暗纹
    for y in [4, 8, 12]:
        for x in range(1, 16, 4):
            p[y][x] = "water_3"
    # 反光点
    import random
    random.seed(55)
    for _ in range(5):
        x, y = random.randint(1, 14), random.randint(1, 14)
        if p[y][x] == "water_1":
            p[y][x] = "water_2"
    return p


def park_tile():
    """🌳 公园/树丛"""
    import random
    random.seed(31)
    p = [["park_1"] * 16 for _ in range(16)]
    # 随机树冠
    for _ in range(30):
        x, y = random.randint(1, 14), random.randint(1, 14)
        p[y][x] = random.choice(["park_2", "park_3", "park_1"])
    # 树桩/阴影
    for y in range(13, 16):
        for x in range(0, 16, 4):
            p[y][x] = "grass_3"
    return p


def plaza_tile():
    """🏛️ 广场/石铺地"""
    p = [["plaza_1"] * 16 for _ in range(16)]
    import random
    random.seed(71)
    # 石缝 (十字形)
    for x in [3, 7, 11]:
        for y in range(16):
            p[y][x] = "road_2"
    for y in [3, 7, 11]:
        for x in range(16):
            if p[y][x] != "road_2":
                p[y][x] = "road_2"
    # 石面差异
    for _ in range(15):
        x, y = random.randint(1, 14), random.randint(1, 14)
        if p[y][x] == "plaza_1":
            p[y][x] = "plaza_2" if random.random() < 0.5 else "sidewalk_2"
    return p


def poi_marker_tile():
    """⭐ POI 高亮 (金色闪烁标记)"""
    p = [["plaza_1"] * 16 for _ in range(16)]
    # 金色星号/菱形
    diamond = [
        [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
        [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,"fg","fg","fg",1,1,1,1,1,1,0],
        [1,1,1,1,1,1,"fg","sp","fg",1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
        [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
        [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],
    ]
    for y in range(16):
        for x in range(16):
            v = diamond[y][x]
            if v == "fg":
                p[y][x] = "poi_fg"
            elif v == "sp":
                p[y][x] = "poi_spark"
            elif v == 1:
                p[y][x] = "poi_bg"
            # 0 stays as plaza base
    return p


def main():
    tileset = Image.new("RGB", (TILE_SIZE * 8, TILE_SIZE))

    tiles = [
        ("草地", 0, grass_tile),
        ("道路", 1, road_tile),
        ("建筑", 2, building_tile),
        ("人行道", 3, sidewalk_tile),
        ("水面", 4, water_tile),
        ("公园", 5, park_tile),
        ("广场", 6, plaza_tile),
        ("POI", 7, poi_marker_tile),
    ]

    for name, idx, pixels_fn in tiles:
        tile_img = make_tile(pixels_fn())
        tileset.paste(tile_img, (idx * TILE_SIZE, 0))
        print(f"  🎨 Tile {idx}: {name}", flush=True)

    out_path = "frontend/public/assets/munich_map/tileset.png"
    tileset.save(out_path)
    print(f"💾 tileset.png 已保存 ({TILE_SIZE*8}×{TILE_SIZE})", flush=True)
    print("✅ 完成!")


if __name__ == "__main__":
    main()
