"""
LLM 文本生成服务
封装 DashScope API (Qwen-Plus / Qwen3-Max)
"""

import json
import dashscope
from dashscope import Generation
from ..config import DASHSCOPE_API_KEY, LLM_MODEL_DEFAULT, LLM_MODEL_COMPLEX

dashscope.api_key = DASHSCOPE_API_KEY


def generate_text(
    prompt: str,
    system_prompt: str = "你是 gagaToday 游戏的内容生成助手。你擅长生成结构化 JSON 数据，用于德国留学模拟 RPG 游戏。请严格按要求的格式输出，只返回 JSON，不要包含其他说明。",
    model: str = LLM_MODEL_DEFAULT,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict:
    """
    调用 Qwen LLM 生成文本

    Args:
        prompt: 用户提示词
        system_prompt: 系统角色设定
        model: 模型名 (qwen-plus / qwen3-max)
        temperature: 创造性 (0-1)
        max_tokens: 最大输出 token 数

    Returns:
        {"text": "...", "model_used": "...", "tokens": {...}}
    """
    response = Generation.call(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        result_format="message",
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if response.status_code != 200:
        raise RuntimeError(f"DashScope API error: {response.status_code} - {response.message}")

    tokens = {}
    try:
        usage = response.output.usage
        tokens = {
            "input": getattr(usage, "input_tokens", 0) or 0,
            "output": getattr(usage, "output_tokens", 0) or 0,
        }
    except (AttributeError, KeyError):
        tokens = {"input": 0, "output": 0}

    return {
        "text": response.output.choices[0].message.content,
        "model_used": model,
        "tokens": tokens,
    }


def generate_json(
    prompt: str,
    system_prompt: str = None,
    model: str = LLM_MODEL_COMPLEX,
    temperature: float = 0.3,
) -> dict:
    """
    调用 LLM 生成 JSON 数据，自动解析返回

    Returns:
        {"data": {...}, "raw_text": "...", "model_used": "...", "tokens": {...}}
    """
    if system_prompt is None:
        system_prompt = (
            "你是 gagaToday 游戏的内容生成助手。"
            "请严格按照要求的 JSON Schema 输出，只返回合法的 JSON，不要包含 ```json 标记或其他说明。"
        )

    result = generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=8192,
    )

    raw = result["text"].strip()
    # 清理可能的 markdown 代码块
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0].strip()
    if raw.startswith("```json"):
        raw = raw[7:].strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM 返回内容不是合法 JSON: {e}\n原始内容: {raw[:300]}")

    return {
        "data": data,
        "raw_text": raw,
        "model_used": result["model_used"],
        "tokens": result["tokens"],
    }
