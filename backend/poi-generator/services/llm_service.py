"""
LLM 文本生成服务
封装 DashScope API (Qwen-Plus / Qwen3-Max) + DeepSeek API (V4 系列)
通过 model id 自动路由 provider(前缀 deepseek-* → DeepSeek,其他 → DashScope)
"""

import json
import dashscope
from dashscope import Generation
from openai import OpenAI
from ..config import (
    DASHSCOPE_API_KEY, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    LLM_MODEL_DEFAULT, LLM_MODEL_COMPLEX, get_provider,
)

dashscope.api_key = DASHSCOPE_API_KEY

# DeepSeek 客户端(OpenAI 兼容,延迟初始化避免无 key 时启动报错)
_deepseek_client = None
def _get_deepseek_client():
    global _deepseek_client
    if _deepseek_client is None:
        if not DEEPSEEK_API_KEY:
            raise RuntimeError("DEEPSEEK_API_KEY 未配置 — 请在 .env 或 vault 里设置")
        _deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _deepseek_client


def _generate_text_dashscope(
    prompt: str,
    system_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """DashScope (Qwen) 后端"""
    # DashScope 拒绝 None/空 system content — 跳过空 system 消息
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = Generation.call(
        model=model,
        messages=messages,
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


def _generate_text_deepseek(
    prompt: str,
    system_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """DeepSeek (V4 系列) 后端 — 用 OpenAI SDK

    V4 默认开 thinking 模式,会把 max_tokens 全吃光。
    - v4-flash: 关 thinking(Flash = 快,不要 reasoning 拖时间/拖 token)
    - v4-pro: 开 thinking + high effort(Pro = 深度推理)
    """
    client = _get_deepseek_client()

    kwargs = dict(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )
    # DeepSeek 也拒绝空 system content — 跳过空 system 消息
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    kwargs["messages"] = messages
    if model == "deepseek-v4-flash":
        # Flash 模式:关 thinking,响应快、token 预算都给最终答案
        kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
    elif model == "deepseek-v4-pro":
        # Pro 模式:开 thinking,高 reasoning effort
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        kwargs["reasoning_effort"] = "high"

    response = client.chat.completions.create(**kwargs)
    text = response.choices[0].message.content or ""
    tokens = {}
    if hasattr(response, "usage") and response.usage:
        tokens = {
            "input": getattr(response.usage, "prompt_tokens", 0) or 0,
            "output": getattr(response.usage, "completion_tokens", 0) or 0,
        }
    return {
        "text": text,
        "model_used": model,
        "tokens": tokens,
    }


def generate_text(
    prompt: str,
    system_prompt: str = "你是 gagaToday 游戏的内容生成助手。你擅长生成结构化 JSON 数据，用于德国留学模拟 RPG 游戏。请严格按要求的格式输出，只返回 JSON，不要包含其他说明。",
    model: str = LLM_MODEL_DEFAULT,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict:
    """
    调用 LLM 生成文本 — 按 model id 自动路由 DashScope / DeepSeek

    Args:
        prompt: 用户提示词
        system_prompt: 系统角色设定
        model: 模型名 (qwen-plus / qwen3-max / deepseek-v4-flash / deepseek-v4-pro)
        temperature: 创造性 (0-1)
        max_tokens: 最大输出 token 数

    Returns:
        {"text": "...", "model_used": "...", "tokens": {...}}
    """
    provider = get_provider(model)
    if provider == "deepseek":
        return _generate_text_deepseek(prompt, system_prompt, model, temperature, max_tokens)
    return _generate_text_dashscope(prompt, system_prompt, model, temperature, max_tokens)


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
