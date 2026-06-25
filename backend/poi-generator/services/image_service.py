"""
图片生成服务
封装 matrix_generate_image (通过 mavis mcp call)
复用 generate_art.py 的方案
"""

import json
import subprocess
import time
from pathlib import Path
from ..config import ASSETS_ROOT, IMAGE_DEFAULT_STYLE


def generate_image(
    prompt: str,
    output_name: str,
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    target_dir: Path = None,
    reference_image: str = None,
    max_retries: int = 3,
) -> Path:
    """
    生成单张图片

    Args:
        prompt: 图片描述 prompt
        output_name: 输出文件名 (如 "exterior_spring.png")
        aspect_ratio: 宽高比 (16:9, 3:4 等)
        resolution: 分辨率 (1K, 2K)
        target_dir: 输出目录，默认为 ASSETS_ROOT
        reference_image: 参考图路径（可选）
        max_retries: 最大重试次数

    Returns:
        生成的文件路径，失败返回 None
    """
    if target_dir is None:
        target_dir = ASSETS_ROOT

    target_dir.mkdir(parents=True, exist_ok=True)

    request = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if reference_image:
        request["input_files"] = [reference_image]

    cmd = [
        "mavis", "mcp", "call", "matrix", "matrix_generate_image",
        json.dumps({"requests": [request]})
    ]

    output_name = Path(output_name).name  # 只取文件名，避免路径嵌套

    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            print(f"  ATTEMPT {attempt+1} timed out")
            time.sleep(2)
            continue

        if result.returncode != 0:
            print(f"  ATTEMPT {attempt+1} subprocess failed: {result.stderr[:200]}")
            time.sleep(2)
            continue

        try:
            data = json.loads(result.stdout)
            if data.get("code") != 0 or data.get("total_success", 0) == 0:
                msg = data.get("message", "unknown")
                print(f"  ATTEMPT {attempt+1} API failed: {msg[:100]}")
                time.sleep(3)
                continue

            item = data["success_items"][0]
            cdn_url = item["output_url"]

            final_path = target_dir / output_name
            final_path.parent.mkdir(parents=True, exist_ok=True)

            dl = subprocess.run(
                ["curl", "-fsSL", "-o", str(final_path), cdn_url],
                capture_output=True, text=True, timeout=60
            )
            if dl.returncode != 0:
                print(f"  ATTEMPT {attempt+1} download failed: {dl.stderr[:200]}")
                time.sleep(2)
                continue

            size_kb = final_path.stat().st_size // 1024
            print(f"  OK (attempt {attempt+1}): {final_path} ({size_kb} KB)")
            return final_path

        except (KeyError, json.JSONDecodeError) as e:
            print(f"  ATTEMPT {attempt+1} parse failed: {e}")
            time.sleep(2)
            continue

    print(f"  FAILED after {max_retries} attempts: {output_name}")
    return None


# ── Prompt 模板 ──

PROMPT_SCENE = """
16-bit pixel art {description},
hard pixel edges no anti-aliasing, limited 16-color palette,
retro JRPG game background, no characters, atmospheric lighting,
clean composition, no text or readable text
""".strip()

PROMPT_NPC = """
16-bit pixel art character sprite, {description},
hard pixel edges no anti-aliasing, limited 16-color palette,
retro JRPG style, 2D character portrait, transparent background,
front-facing, character sheet, clean composition
""".strip()

PROMPT_UI = """
16-bit pixel art {description},
hard pixel edges no anti-aliasing, limited 16-color palette,
retro JRPG UI element, isolated on transparent background,
centered, clean composition
""".strip()
