#!/usr/bin/env python3
"""
AI 美术生成工具
- 统一调 matrix_generate_image
- 每张图 prompt 可定制
- 同组(同一角色/场景)用同一参考图
- 自动归档到 assets 目录
- 失败 retry,记录日志
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

# ---- 配置 ----
ASSETS_ROOT = Path("/Volumes/NewDisk/GermanLearning/assets")
TEST_DIR = ASSETS_ROOT / "_test"
FINAL_DIR = ASSETS_ROOT
LOG_FILE = Path("/Volumes/NewDisk/GermanLearning/scripts/art_generation.log")


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")


def generate(
    prompt: str,
    output_name: str,
    reference_image: str = None,
    aspect_ratio: str = "3:4",
    resolution: str = "1K",
    target_dir: Path = FINAL_DIR,
) -> Path:
    """
    生成单张图,自动归档到 target_dir。
    返回最终文件路径。
    """
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

    # 只取文件名,避免路径嵌套
    output_name = Path(output_name).name

    log(f"GENERATING: {output_name}")
    log(f"  prompt: {prompt[:80]}...")

    for attempt in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            log(f"  ATTEMPT {attempt+1} subprocess failed: {result.stderr[:200]}")
            time.sleep(2)
            continue

        try:
            data = json.loads(result.stdout)
            if data.get("code") != 0 or data.get("total_success", 0) == 0:
                msg = data.get('message', 'unknown')
                log(f"  ATTEMPT {attempt+1} API failed: {msg[:100]}")
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
                log(f"  ATTEMPT {attempt+1} download failed: {dl.stderr[:200]}")
                time.sleep(2)
                continue

            size_kb = final_path.stat().st_size // 1024
            log(f"  OK (attempt {attempt+1}): {final_path} ({size_kb} KB)")
            return final_path
        except (KeyError, json.JSONDecodeError) as e:
            log(f"  ATTEMPT {attempt+1} parse failed: {e}")
            time.sleep(2)
            continue

    log(f"  FAILED after 3 attempts: {output_name}")
    return None


# ---- 通用 prompt 模板 ----

PROMPT_BASE_NPC = """
16-bit pixel art character sprite, {description}, 
hard pixel edges no anti-aliasing, limited 16-color palette, 
retro JRPG style, 2D character portrait, transparent background, 
front-facing, character sheet, clean composition
""".strip()

PROMPT_BASE_SCENE = """
16-bit pixel art {description}, 
hard pixel edges no anti-aliasing, limited 16-color palette, 
retro JRPG game background, no characters, atmospheric lighting, 
clean composition, no text or readable text
""".strip()

PROMPT_BASE_UI = """
16-bit pixel art {description}, 
hard pixel edges no anti-aliasing, limited 16-color palette, 
retro JRPG UI element, isolated on transparent background, 
centered, clean composition
""".strip()


# ---- MVP 美术清单 ----

ART_PLAN = {
    "anna": {
        "type": "npc",
        "reference": str(TEST_DIR / "anna_test_v1.png"),
        "aspect_ratio": "3:4",
        "items": [
            {
                "name": "characters/anna/anna_neutral.png",
                "description": "Anna, 40-year-old female cafe waitress, hair in a bun, white shirt and black apron with name tag, neutral calm expression, looking forward"
            },
            {
                "name": "characters/anna/anna_smile.png",
                "description": "Anna, 40-year-old female cafe waitress, hair in a bun, white shirt and black apron with name tag, warm friendly smile, looking forward, mouth slightly open"
            },
            {
                "name": "characters/anna/anna_surprise.png",
                "description": "Anna, 40-year-old female cafe waitress, hair in a bun, white shirt and black apron with name tag, surprised expression with raised eyebrows and slight smile, looking forward"
            },
            {
                "name": "characters/anna/anna_thinking.png",
                "description": "Anna, 40-year-old female cafe waitress, hair in a bun, white shirt and black apron with name tag, thoughtful expression with slight head tilt, looking forward"
            },
        ]
    },
    "peter": {
        "type": "npc",
        # 没有 Peter 参考图,先用文字描述引导风格
        "reference": str(TEST_DIR / "anna_test_v1.png"),  # 借用 Anna 风格参考
        "aspect_ratio": "3:4",
        "items": [
            {
                "name": "characters/peter/peter_neutral.png",
                "description": "Peter, 50-year-old male information desk worker at Berlin train station, short gray hair, wearing blue uniform shirt with name tag, calm neutral expression, looking forward"
            },
            {
                "name": "characters/peter/peter_smile.png",
                "description": "Peter, 50-year-old male information desk worker at Berlin train station, short gray hair, wearing blue uniform shirt with name tag, helpful friendly smile, looking forward"
            },
            {
                "name": "characters/peter/peter_surprise.png",
                "description": "Peter, 50-year-old male information desk worker at Berlin train station, short gray hair, wearing blue uniform shirt with name tag, slightly surprised helpful expression, looking forward"
            },
            {
                "name": "characters/peter/peter_thinking.png",
                "description": "Peter, 50-year-old male information desk worker at Berlin train station, short gray hair, wearing blue uniform shirt with name tag, thinking expression looking up slightly, looking forward"
            },
        ]
    },
    "scenes": {
        "type": "scene",
        "reference": str(TEST_DIR / "cafe_test_v1.png"),
        "aspect_ratio": "16:9",
        "items": [
            {
                "name": "scenes/berlin/hauptbahnhof_interior.png",
                "description": "Berlin Hauptbahnhof central train station interior, modern glass and steel architecture, ticket counter, large departure boards, travelers with luggage, warm indoor lighting, no specific people in foreground"
            },
            {
                "name": "scenes/berlin/cafe_einstein.png",
                "description": "Cozy Berlin cafe interior, warm orange lighting, wooden furniture, espresso machine, brick wall with framed vintage posters, large windows, retro European atmosphere"
            },
            {
                "name": "scenes/berlin/street_kreuzberg.png",
                "description": "Berlin Kreuzberg street view, colorful graffiti on buildings, Turkish shops, bicycle parked, late afternoon light, urban multicultural atmosphere, no people in foreground"
            },
        ]
    },
    "ui": {
        "type": "ui",
        "reference": None,
        "aspect_ratio": "1:1",
        "items": [
            {
                "name": "ui/dialogue_box.png",
                "description": "dialogue box UI element, parchment style with ornate corner decorations, dark semi-transparent center, retro game aesthetic, square format"
            },
            {
                "name": "ui/button_normal.png",
                "description": "pixel art button UI element, brown wood texture, simple rectangular shape, slightly raised look, retro game button"
            },
            {
                "name": "ui/city_badge_berlin.png",
                "description": "Berlin city badge, circular shield design, featuring a stylized Berlin bear silhouette, BERLIN text below, retro pixel art style"
            },
            {
                "name": "ui/mic_button.png",
                "description": "microphone button UI element, circular, dark gray with subtle red recording indicator, retro game button style"
            },
        ]
    },
}


def generate_group(group_name: str, group_config: dict):
    """生成一组图,每张独立 prompt + 同一参考图"""
    log(f"=== Group: {group_name} ({len(group_config['items'])} items) ===")

    if group_config["type"] == "npc":
        prompt_base = PROMPT_BASE_NPC
    elif group_config["type"] == "scene":
        prompt_base = PROMPT_BASE_SCENE
    else:
        prompt_base = PROMPT_BASE_UI

    results = []
    for item in group_config["items"]:
        full_prompt = prompt_base.format(description=item["description"])
        output_path = ASSETS_ROOT / item["name"]
        result = generate(
            prompt=full_prompt,
            output_name=item["name"],
            reference_image=group_config.get("reference"),
            aspect_ratio=group_config.get("aspect_ratio", "1:1"),
            target_dir=output_path.parent,
        )
        results.append((item["name"], result))

    success = sum(1 for _, r in results if r)
    log(f"=== Group {group_name}: {success}/{len(results)} succeeded ===\n")
    return results


def main():
    """主入口:按需生成"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_art.py anna          # 生成 Anna 4 表情")
        print("  python generate_art.py peter         # 生成 Peter 4 表情")
        print("  python generate_art.py scenes        # 生成柏林 3 个场景")
        print("  python generate_art.py ui            # 生成 UI 元素")
        print("  python generate_art.py all           # 全部生成")
        print("  python generate_art.py list          # 列出计划")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "list":
        for name, cfg in ART_PLAN.items():
            print(f"\n{name} ({len(cfg['items'])} items):")
            for item in cfg["items"]:
                print(f"  - {item['name']}")
        return

    if cmd == "all":
        for name, cfg in ART_PLAN.items():
            generate_group(name, cfg)
        return

    if cmd in ART_PLAN:
        generate_group(cmd, ART_PLAN[cmd])
        return

    print(f"Unknown command: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
