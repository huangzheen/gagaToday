"""
多模型图片生成服务
支持: MiniMax (Matrix MCP), 火山引擎 ARK (Seedream), OpenRouter (GPT-5.4-Image-2), 阿里云 DashScope (Qwen-Image)
"""

import os
import json
import time
import subprocess
import base64
import httpx
from pathlib import Path
from ..config import GENERATED_PUBLIC_DIR

# ── API 密钥 ──
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ── 端点 ──
ARK_BASE = "https://ark.cn-beijing.volces.com/api/v3"
DASHSCOPE_BASE = "https://dashscope.aliyuncs.com/api/v1"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# ── 可用模型列表 ──
IMAGE_MODELS = [
    {
        "id": "minimax",
        "name": "MiniMax (Matrix MCP)",
        "provider": "MiniMax / Hailuo AI",
        "description": "通过 Matrix MCP 调用，16-bit 像素风格适配好",
        "status": "available",
    },
    {
        "id": "doubao-seedream-4-5-251128",
        "name": "Seedream 4.5",
        "provider": "火山引擎 (豆包)",
        "description": "火山引擎 ARK 平台，画质优秀，支持中文 prompt",
        "status": "available" if ARK_API_KEY else "no_key",
    },
    {
        "id": "openai/gpt-5.4-image-2",
        "name": "GPT-5.4 Image 2",
        "provider": "OpenRouter",
        "description": "通过 OpenRouter 调用，多模态生图",
        "status": "available" if OPENROUTER_API_KEY else "no_key",
    },
    {
        "id": "qwen-image-edit-plus-2025-10-30",
        "name": "Qwen Image Edit Plus",
        "provider": "阿里云 (DashScope)",
        "description": "通义千问图像编辑模型，支持参考图",
        "status": "available" if DASHSCOPE_API_KEY else "no_key",
    },
]


def get_available_models() -> list[dict]:
    """返回可用模型列表（含密钥状态）"""
    models = []
    for m in IMAGE_MODELS:
        mc = dict(m)
        if m["id"] == "minimax":
            mc["status"] = "available"  # MiniMax always available via mavis
        elif m["id"].startswith("doubao-"):
            mc["status"] = "available" if ARK_API_KEY else "no_key"
        elif m["id"].startswith("openai/"):
            mc["status"] = "available" if OPENROUTER_API_KEY else "no_key"
        elif m["id"].startswith("qwen-"):
            mc["status"] = "available" if DASHSCOPE_API_KEY else "no_key"
        models.append(mc)
    return models


# ═══════════════════════════════════════════════════════════════
# MiniMax (Matrix MCP) — 现有通路，不变
# ═══════════════════════════════════════════════════════════════

def generate_minimax(
    prompt: str,
    output_name: str,
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    target_dir: Path = None,
    max_retries: int = 3,
) -> Path | None:
    """通过 mavis mcp call matrix 生成图片（现有逻辑）"""
    if target_dir is None:
        target_dir = GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    request_body = {
        "requests": [{
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        }]
    }

    cmd = [
        "mavis", "mcp", "call", "matrix", "matrix_generate_image",
        json.dumps(request_body)
    ]

    output_name = Path(output_name).name

    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            time.sleep(2)
            continue

        if result.returncode != 0:
            time.sleep(2)
            continue

        try:
            data = json.loads(result.stdout)
            if data.get("code") != 0 or data.get("total_success", 0) == 0:
                time.sleep(3)
                continue

            item = data["success_items"][0]
            cdn_url = item["output_url"]
            final_path = target_dir / output_name

            dl = subprocess.run(
                ["curl", "-fsSL", "-o", str(final_path), cdn_url],
                capture_output=True, text=True, timeout=60
            )
            if dl.returncode != 0:
                time.sleep(2)
                continue

            size_kb = final_path.stat().st_size // 1024
            print(f"  [MiniMax] OK (attempt {attempt+1}): {final_path} ({size_kb} KB)")
            return final_path

        except (KeyError, json.JSONDecodeError):
            time.sleep(2)
            continue

    print(f"  [MiniMax] FAILED after {max_retries} attempts")
    return None


# ═══════════════════════════════════════════════════════════════
# 火山引擎 ARK (Seedream 4.5)
# ═══════════════════════════════════════════════════════════════

async def generate_ark(
    prompt: str,
    output_name: str,
    model: str = "doubao-seedream-4-5-251128",
    size: str = "1K",
    target_dir: Path = None,
    max_retries: int = 2,
) -> Path | None:
    """通过火山引擎 ARK API 生成图片"""
    if not ARK_API_KEY:
        raise RuntimeError("ARK_API_KEY 未配置")

    if target_dir is None:
        target_dir = GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    # ARK size: 必须 >= 3,686,400 像素，且至少 1 边 >= 960
    ark_size = size if "x" in size else "1920x1920"

    body = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": ark_size,
        "response_format": "url",
        "watermark": False,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ARK_API_KEY}",
    }

    output_name = Path(output_name).name

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{ARK_BASE}/images/generations",
                    json=body,
                    headers=headers,
                )
            data = resp.json()

            if not resp.is_success:
                err = data.get("error", {}).get("message", str(data))
                print(f"  [ARK] attempt {attempt+1} error: {err[:200]}")
                time.sleep(2)
                continue

            img_url = data.get("data", [{}])[0].get("url", "")
            if not img_url:
                print(f"  [ARK] attempt {attempt+1}: no url in response")
                time.sleep(2)
                continue

            final_path = target_dir / output_name
            async with httpx.AsyncClient(timeout=60) as client:
                img_resp = await client.get(img_url)
            if img_resp.status_code != 200:
                time.sleep(2)
                continue

            final_path.write_bytes(img_resp.content)
            size_kb = final_path.stat().st_size // 1024
            print(f"  [ARK] OK (attempt {attempt+1}): {final_path} ({size_kb} KB)")
            return final_path

        except Exception as e:
            print(f"  [ARK] attempt {attempt+1} exception: {e}")
            time.sleep(2)
            continue

    print(f"  [ARK] FAILED after {max_retries} attempts")
    return None


# ═══════════════════════════════════════════════════════════════
# OpenRouter (GPT-5.4 Image 2)
# ═══════════════════════════════════════════════════════════════

async def generate_openrouter(
    prompt: str,
    output_name: str,
    model: str = "openai/gpt-5.4-image-2",
    target_dir: Path = None,
    max_retries: int = 2,
) -> Path | None:
    """通过 OpenRouter chat/completions API 生成图片（modalities 模式）"""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY 未配置")

    if target_dir is None:
        target_dir = GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    body = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }],
        "modalities": ["image", "text"],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }

    output_name = Path(output_name).name

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                resp = await client.post(
                    f"{OPENROUTER_BASE}/chat/completions",
                    json=body,
                    headers=headers,
                )
            data = resp.json()

            if not resp.is_success:
                err = data.get("error", {}).get("message", str(data))
                print(f"  [OpenRouter] attempt {attempt+1} error: {err[:200]}")
                time.sleep(2)
                continue

            msg = data.get("choices", [{}])[0].get("message", {})
            images = msg.get("images", [])
            img_url = None

            if images:
                img_url = images[0].get("image_url", {}).get("url", "")
            if not img_url:
                # fallback: content parts
                parts = msg.get("content", [])
                if isinstance(parts, list):
                    for p in parts:
                        if p.get("type") == "image_url":
                            img_url = p.get("image_url", {}).get("url", "")
                            break

            if not img_url:
                print(f"  [OpenRouter] attempt {attempt+1}: no image in response")
                time.sleep(2)
                continue

            final_path = target_dir / output_name

            if img_url.startswith("data:"):
                # data URI
                b64 = img_url.split(",", 1)[-1]
                final_path.write_bytes(base64.b64decode(b64))
            else:
                async with httpx.AsyncClient(timeout=60) as client:
                    img_resp = await client.get(img_url)
                if img_resp.status_code != 200:
                    time.sleep(2)
                    continue
                final_path.write_bytes(img_resp.content)

            size_kb = final_path.stat().st_size // 1024
            print(f"  [OpenRouter] OK (attempt {attempt+1}): {final_path} ({size_kb} KB)")
            return final_path

        except Exception as e:
            print(f"  [OpenRouter] attempt {attempt+1} exception: {e}")
            time.sleep(2)
            continue

    print(f"  [OpenRouter] FAILED after {max_retries} attempts")
    return None


# ═══════════════════════════════════════════════════════════════
# 阿里云 DashScope (Qwen Image)
# ═══════════════════════════════════════════════════════════════

async def generate_dashscope(
    prompt: str,
    output_name: str,
    model: str = "qwen-image-edit-plus-2025-10-30",
    target_dir: Path = None,
    max_retries: int = 2,
) -> Path | None:
    """通过阿里云 DashScope 生成图片"""
    if not DASHSCOPE_API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置")

    if target_dir is None:
        target_dir = GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    body = {
        "model": model,
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "size": "1664*928",  # 16:9 1K
            "n": 1,
        },
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
    }

    output_name = Path(output_name).name

    for attempt in range(max_retries):
        try:
            # DashScope 使用异步任务模式
            async with httpx.AsyncClient(timeout=120) as client:
                # Step 1: 提交任务
                task_resp = await client.post(
                    f"{DASHSCOPE_BASE}/services/aigc/image-generation/generation",
                    json=body,
                    headers=headers,
                )
            task_data = task_resp.json()

            if not task_resp.is_success:
                err = task_data.get("message", str(task_data))
                print(f"  [DashScope] attempt {attempt+1} submit error: {err[:200]}")
                time.sleep(2)
                continue

            task_id = task_data.get("output", {}).get("task_id", "")
            if not task_id:
                print(f"  [DashScope] attempt {attempt+1}: no task_id")
                time.sleep(2)
                continue

            # Step 2: 轮询结果
            for _ in range(20):  # max 100s
                async with httpx.AsyncClient(timeout=30) as client:
                    poll_resp = await client.get(
                        f"{DASHSCOPE_BASE}/tasks/{task_id}",
                        headers=headers,
                    )
                poll_data = poll_resp.json()
                status = poll_data.get("output", {}).get("task_status", "")

                if status == "SUCCEEDED":
                    img_url = poll_data.get("output", {}).get("results", [{}])[0].get("url", "")
                    if not img_url:
                        break

                    final_path = target_dir / output_name
                    async with httpx.AsyncClient(timeout=60) as client:
                        img_resp = await client.get(img_url)
                    if img_resp.status_code != 200:
                        break

                    final_path.write_bytes(img_resp.content)
                    size_kb = final_path.stat().st_size // 1024
                    print(f"  [DashScope] OK (attempt {attempt+1}): {final_path} ({size_kb} KB)")
                    return final_path

                elif status == "FAILED":
                    err_msg = poll_data.get("output", {}).get("message", "unknown")
                    print(f"  [DashScope] attempt {attempt+1} task failed: {err_msg[:200]}")
                    break

                time.sleep(5)

        except Exception as e:
            print(f"  [DashScope] attempt {attempt+1} exception: {e}")
            time.sleep(2)
            continue

    print(f"  [DashScope] FAILED after {max_retries} attempts")
    return None


# ═══════════════════════════════════════════════════════════════
# 统一入口
# ═══════════════════════════════════════════════════════════════

async def generate_with_model(
    model: str,
    prompt: str,
    output_name: str,
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    target_dir: Path = None,
) -> Path | None:
    """根据模型 ID 路由到对应的生图服务"""
    if target_dir is None:
        target_dir = GENERATED_PUBLIC_DIR

    if model == "minimax":
        return generate_minimax(prompt, output_name, aspect_ratio, resolution, target_dir)
    elif model.startswith("doubao-"):
        return await generate_ark(prompt, output_name, model, resolution, target_dir)
    elif model.startswith("openai/"):
        return await generate_openrouter(prompt, output_name, model, target_dir)
    elif model.startswith("qwen-"):
        return await generate_dashscope(prompt, output_name, model, target_dir)
    else:
        raise ValueError(f"不支持的图片模型: {model}")


# ═══════════════════════════════════════════════════════════════
# 参考图模式 — 定妆照 → 变体（图像到图像）
# ═══════════════════════════════════════════════════════════════

async def _fetch_ref_as_b64(ref_url_or_path: str) -> str | None:
    """下载参考图并转为 base64 data URI"""
    try:
        if ref_url_or_path.startswith("http"):
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.get(ref_url_or_path)
            data = r.content
        else:
            data = Path(ref_url_or_path).read_bytes()
        return base64.b64encode(data).decode("ascii")
    except Exception as e:
        print(f"  fetch ref failed: {e}")
        return None


async def generate_with_reference(
    model: str,
    prompt: str,
    output_name: str,
    reference_path: str,
    target_dir: Path = None,
    max_retries: int = 2,
) -> Path | None:
    """
    使用参考图生成变体图片

    Args:
        model: 模型 ID（支持 doubao-seedream-* 和 openai/gpt-5.4-image-2）
        prompt: 变体描述（如 "winter snow covering the same scene, 16-bit pixel art"）
        output_name: 输出文件名
        reference_path: 参考图路径（本地文件或 URL）
        target_dir: 输出目录
    """
    if target_dir is None:
        target_dir = GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    output_name = Path(output_name).name
    ref_b64 = await _fetch_ref_as_b64(reference_path)
    if not ref_b64:
        return None

    if model.startswith("doubao-"):
        return await _ark_with_ref(prompt, output_name, model, ref_b64, target_dir, max_retries)
    elif model.startswith("openai/"):
        return await _openrouter_with_ref(prompt, output_name, model, ref_b64, target_dir, max_retries)
    else:
        raise ValueError(f"参考图模式仅支持 doubao-* 和 openai/* 模型，当前: {model}")


async def _ark_with_ref(
    prompt: str,
    output_name: str,
    model: str,
    ref_b64: str,
    target_dir: Path,
    max_retries: int,
) -> Path | None:
    """ARK (Seedream) — reference image mode with structural consistency prompts."""
    # ARK Seedream understands natural language better than code-like directives.
    # Wrap the user's variant prompt with strong structural-locking context.
    ark_prompt = (
        f"[Image-to-Image Reference Mode]\n"
        f"Using the provided reference image as the exact structural template, "
        f"generate a new image where the building, its shape, proportions, camera angle, framing, "
        f"and all architectural details remain completely identical to the reference.\n"
        f"Only apply the following atmospheric change:\n"
        f"{prompt}\n"
        f"Important: The output should look like the same building and location as the reference, "
        f"just with different weather/season/lighting. Structural consistency is paramount."
    )
    body = {
        "model": model,
        "prompt": ark_prompt,
        "n": 1,
        "size": "1920x1920",
        "response_format": "url",
        "watermark": False,
        "image": [f"data:image/jpeg;base64,{ref_b64}"],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ARK_API_KEY}"}

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=120) as c:
                resp = await c.post(f"{ARK_BASE}/images/generations", json=body, headers=headers)
            data = resp.json()
            if not resp.is_success:
                err = data.get("error", {}).get("message", str(data))
                print(f"  [ARK-ref] attempt {attempt+1} error: {err[:200]}")
                time.sleep(2)
                continue
            img_url = data.get("data", [{}])[0].get("url", "")
            if not img_url:
                time.sleep(2)
                continue
            fp = target_dir / output_name
            async with httpx.AsyncClient(timeout=60) as c:
                ir = await c.get(img_url)
            fp.write_bytes(ir.content)
            print(f"  [ARK-ref] OK: {fp} ({fp.stat().st_size//1024} KB)")
            return fp
        except Exception as e:
            print(f"  [ARK-ref] attempt {attempt+1} exception: {e}")
            time.sleep(2)
    return None


async def _openrouter_with_ref(
    prompt: str,
    output_name: str,
    model: str,
    ref_b64: str,
    target_dir: Path,
    max_retries: int,
) -> Path | None:
    """OpenRouter — reference image in content parts, with strong consistency constraints."""
    system_text = (
        "You are a professional game artist specializing in 16-bit pixel art. "
        "Your task is to take a reference architectural photograph and generate a pixel-art variant "
        "where the weather, season, lighting, and atmosphere change, but the building and composition remain absolutely locked. "
        "CRITICAL RULES:\n"
        "1. The building geometry, shape, proportion, position, and perspective must be 100% identical to the reference.\n"
        "2. The camera framing, horizon line, and angle must not change.\n"
        "3. Do NOT add, remove, or alter any structural element — windows, doors, towers, rooflines, all fixed.\n"
        "4. You MAY change: sky color, cloud cover, sun position, shadow direction/length, foliage color/amount, "
        "ground surface (snow/rain puddles/dry), color temperature of light, overall brightness/contrast.\n"
        "5. Output as pixel art with hard edges, blocky pixels, limited 16-color palette, no anti-aliasing, no smooth gradients.\n"
        "6. Do NOT output a photorealistic image. Output 16-bit retro JRPG background style."
    )
    content = [
        {"type": "text", "text": system_text},
        {"type": "text", "text": f"REFERENCE IMAGE (lock all structure from this):"},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{ref_b64}"}},
        {"type": "text", "text": f"VARIANT INSTRUCTION:\n{prompt}"},
    ]
    body = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {OPENROUTER_API_KEY}"}

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=180) as c:
                resp = await c.post(f"{OPENROUTER_BASE}/chat/completions", json=body, headers=headers)
            data = resp.json()
            if not resp.is_success:
                err = data.get("error", {}).get("message", str(data))
                print(f"  [OR-ref] attempt {attempt+1} error: {err[:200]}")
                time.sleep(2)
                continue
            msg = data.get("choices", [{}])[0].get("message", {})
            images = msg.get("images", [])
            img_url = None
            if images:
                img_url = images[0].get("image_url", {}).get("url", "")
            if not img_url:
                parts = msg.get("content", []) if isinstance(msg.get("content"), list) else []
                for p in parts:
                    if p.get("type") == "image_url":
                        img_url = p.get("image_url", {}).get("url", "")
                        break
            if not img_url:
                time.sleep(2)
                continue
            fp = target_dir / output_name
            if img_url.startswith("data:"):
                fp.write_bytes(base64.b64decode(img_url.split(",", 1)[-1]))
            else:
                async with httpx.AsyncClient(timeout=60) as c:
                    ir = await c.get(img_url)
                if ir.status_code != 200:
                    time.sleep(2)
                    continue
                fp.write_bytes(ir.content)
            print(f"  [OR-ref] OK: {fp} ({fp.stat().st_size//1024} KB)")
            return fp
        except Exception as e:
            print(f"  [OR-ref] attempt {attempt+1} exception: {e}")
            time.sleep(2)
    return None
