"""
文本生成路由 — 调用 Qwen LLM
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import LLM_MODEL_DEFAULT, LLM_MODEL_COMPLEX
from ..services.llm_service import generate_text, generate_json

router = APIRouter(prefix="/api/generate", tags=["text"])


@router.get("/llm-models")
async def api_list_llm_models():
    """列出可用的 LLM 模型"""
    return {
        "success": True,
        "models": [
            {"id": LLM_MODEL_DEFAULT, "name": "通义千问 Qwen-Plus", "provider": "阿里云 DashScope", "usage": "日常生成"},
            {"id": LLM_MODEL_COMPLEX, "name": "通义千问 Qwen3-Max", "provider": "阿里云 DashScope", "usage": "复杂任务"},
        ],
        "default": LLM_MODEL_DEFAULT,
        "complex": LLM_MODEL_COMPLEX,
    }


class TextRequest(BaseModel):
    prompt: str
    system_prompt: str = None
    model: str = "qwen-plus"
    temperature: float = 0.7
    max_tokens: int = 4096


class JsonRequest(BaseModel):
    prompt: str
    system_prompt: str = None
    model: str = "qwen3-max"
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
