#!/usr/bin/env python3
"""
white_to_transparent.py — 把白底 PNG 转成透明底 PNG

gagaToday 视觉规范要求所有资产图用 white background,但游戏运行时
需要在不同背景上叠加,所以把白底转成透明底(纯白 → alpha=0,边缘羽化)。

用法:
    python3 scripts/white_to_transparent.py <file_or_dir> [...]
    python3 scripts/white_to_transparent.py assets/characters/munich/

依赖: pip install pillow numpy

逻辑:
    1. 读 PNG → RGBA
    2. 对每个像素:
       - RGB 都在 240+ → 完全透明(alpha=0)
       - RGB 都在 250+ 接近纯白 → 半透明(边缘羽化)
       - 其他 → 不透明(alpha=255)
    3. 备份原文件(加 .bak-white.png 后缀)
    4. 写回原路径(覆盖)

实现说明:
    阈值用 240(不是 255)是为了容忍 JPEG 噪声/AI 生成时的轻微偏色。
    边缘羽化用 240-250 之间的渐变,避免角色轮廓出现硬边。
"""

import sys
import shutil
from pathlib import Path
from PIL import Image


# 阈值常量
THRESHOLD_FULL_ALPHA = 250  # RGB 全部 ≥ 此值 → 完全透明
THRESHOLD_ZERO_ALPHA = 240  # RGB 全部 < 此值 → 完全不透明
# RGB 任一通道低于 ZERO 阈值,认为是有色像素 → 不透明(避免把肤色/亮色头发误判成背景)


def white_to_transparent(input_path: Path, backup: bool = True, overwrite: bool = True) -> bool:
    """
    把单张白底 PNG 转成透明底。

    Args:
        input_path: 输入 PNG 路径
        backup: 是否备份原文件(.bak-white.png)
        overwrite: 是否覆盖原文件;False 则写 *_transparent.png

    Returns:
        是否成功处理
    """
    if not input_path.exists():
        print(f'⚠️  跳过(不存在): {input_path}')
        return False
    if input_path.suffix.lower() not in ('.png', '.webp'):
        print(f'⚠️  跳过(非 PNG/WebP): {input_path}')
        return False

    try:
        img = Image.open(input_path).convert('RGBA')
    except Exception as e:
        print(f'❌ 读图失败 {input_path}: {e}')
        return False

    w, h = img.size
    pixels = img.load()
    n_white = 0
    n_edge = 0

    # 遍历所有像素,根据 RGB 调整 alpha
    for y in range(h):
        for x in range(w):
            r, g, b, _a = pixels[x, y]
            min_rgb = min(r, g, b)
            if min_rgb >= THRESHOLD_FULL_ALPHA:
                # 接近纯白 → 完全透明
                pixels[x, y] = (r, g, b, 0)
                n_white += 1
            elif min_rgb < THRESHOLD_ZERO_ALPHA:
                # 有色像素 → 不透明
                pixels[x, y] = (r, g, b, 255)
            else:
                # 边缘羽化带:alpha = 250 - min_rgb(线性)
                edge_alpha = THRESHOLD_FULL_ALPHA - min_rgb
                pixels[x, y] = (r, g, b, edge_alpha)
                n_edge += 1

    # 备份
    if backup:
        backup_path = input_path.with_suffix(input_path.suffix + '.bak-white.png')
        if not backup_path.exists():
            shutil.copy2(str(input_path), str(backup_path))
            print(f'  📦 备份: {backup_path.name}')

    out_path = input_path if overwrite else input_path.with_name(input_path.stem + '_transparent.png')

    img.save(str(out_path), optimize=True)

    # 统计
    total = w * h
    print(f'  ✅ {out_path.name}: {n_white}/{total} ({n_white*100/total:.1f}%) 透明,{n_edge} 边缘羽化')
    return True


def process_path(path: Path, recursive: bool = False) -> int:
    """处理单个路径(文件或目录),返回处理成功数"""
    if path.is_file():
        return 1 if white_to_transparent(path) else 0

    if path.is_dir():
        pattern = '**/*.png' if recursive else '*.png'
        files = sorted(path.glob(pattern))
        if not files:
            print(f'⚠️  {path} 下没找到 PNG 文件')
            return 0
        print(f'🔍 {path} 找到 {len(files)} 张 PNG')
        ok = sum(1 for f in files if white_to_transparent(f))
        print(f'✅ 完成: {ok}/{len(files)} 成功')
        return ok

    print(f'⚠️  路径不存在: {path}')
    return 0


def main():
    args = sys.argv[1:]
    if not args or '--help' in args or '-h' in args:
        print(__doc__)
        print('示例:')
        print('  python3 scripts/white_to_transparent.py assets/characters/munich/')
        print('  python3 scripts/white_to_transparent.py assets/characters/munich/npc_X/npc_X_head.png')
        sys.exit(0)

    recursive = '--recursive' in args or '-r' in args
    args = [a for a in args if a not in ('--recursive', '-r')]

    total_ok = 0
    for arg in args:
        p = Path(arg)
        total_ok += process_path(p, recursive=recursive)

    if total_ok == 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
