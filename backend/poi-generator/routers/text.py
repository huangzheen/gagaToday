"""
文本生成路由 — 调用 Qwen / DeepSeek LLM
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import LLM_MODEL_DEFAULT, LLM_MODEL_COMPLEX, DEEPSEEK_API_KEY
from ..services.llm_service import generate_text, generate_json

router = APIRouter(prefix="/api/generate", tags=["text"])


@router.get("/llm-models")
async def api_list_llm_models():
    """列出可用的 LLM 模型"""
    models = [
        {"id": "deepseek-v4-flash", "name": "DeepSeek V4 Flash", "provider": "DeepSeek", "usage": "快速对话/翻译/轻量写作(默认)"},
        {"id": "qwen-plus", "name": "通义千问 Qwen-Plus", "provider": "阿里云 DashScope", "usage": "日常生成"},
        {"id": "qwen3-max", "name": "通义千问 Qwen3-Max", "provider": "阿里云 DashScope", "usage": "复杂任务(知识卡/剧情)"},
    ]
    # DeepSeek Pro 仅在 key 已配置时列出(否则用户选了也跑不通)
    if DEEPSEEK_API_KEY:
        models.append({
            "id": "deepseek-v4-pro",
            "name": "DeepSeek V4 Pro",
            "provider": "DeepSeek",
            "usage": "深度推理/复杂任务",
        })
    return {
        "success": True,
        "models": models,
        "default": LLM_MODEL_DEFAULT,
        "complex": LLM_MODEL_COMPLEX,
    }


class TextRequest(BaseModel):
    prompt: str
    system_prompt: str = None
    model: str = LLM_MODEL_DEFAULT
    temperature: float = 0.7
    max_tokens: int = 4096


class JsonRequest(BaseModel):
    prompt: str
    system_prompt: str = None
    model: str = LLM_MODEL_COMPLEX
    temperature: float = 0.3


@router.post("/text")
async def api_generate_text(req: TextRequest):
    """调用 LLM 生成自由文本"""
    try:
        result = generate_text(
            prompt=req.prompt,
            system_prompt=req.system_prompt,
            model=req.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/json")
async def api_generate_json(req: JsonRequest):
    """调用 LLM 生成结构化 JSON"""
    try:
        result = generate_json(
            prompt=req.prompt,
            system_prompt=req.system_prompt,
            model=req.model,
            temperature=req.temperature,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
