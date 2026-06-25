"""
图片生成路由 — 多模型支持 (MiniMax / ARK / OpenRouter / DashScope)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from ..services.image_service import PROMPT_SCENE, PROMPT_NPC
from ..services.multi_image_service import generate_with_model, generate_with_reference, get_available_models
from ..config import GENERATED_PUBLIC_DIR

router = APIRouter(prefix="/api/generate", tags=["image"])


class ImageRequest(BaseModel):
    description: str
    output_name: str
    model: str = "minimax"         # minimax | doubao-seedream-4-5-251128 | openai/gpt-5.4-image-2 | qwen-image-edit-plus-2025-10-30
    aspect_ratio: str = "16:9"
    resolution: str = "1K"
    target_dir: str = None
    reference_image: str = None
    prompt_type: str = "scene"      # "scene" | "npc" | "ui"


@router.get("/models")
async def api_list_models():
    """列出可用的图片生成模型"""
    return {"success": True, "models": get_available_models()}


@router.post("/image")
async def api_generate_image(req: ImageRequest):
    """生成一张图片，保存到前端 public/generated/ 目录"""
    # 选择 prompt 模板
    if req.prompt_type == "npc":
        prompt_template = PROMPT_NPC
    elif req.prompt_type == "ui":
        prompt_template = "16-bit pixel art {description}, hard pixel edges no anti-aliasing, limited 16-color palette, retro JRPG UI element"
    else:
        prompt_template = PROMPT_SCENE

    raw_prompt = req.description
    if req.model == "minimax":
        # MiniMax 用模板（像素风格）
        raw_prompt = prompt_template.format(description=req.description)

    # 目标目录
    target_dir = Path(req.target_dir) if req.target_dir else GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        result_path = await generate_with_model(
            model=req.model,
            prompt=raw_prompt,
            output_name=req.output_name,
            aspect_ratio=req.aspect_ratio,
            resolution=req.resolution,
            target_dir=target_dir,
        )

        if result_path is None:
            raise HTTPException(status_code=500, detail=f"图片生成失败（模型: {req.model}）")

        web_url = f"/generated/{result_path.name}"

        return {
            "success": True,
            "model_used": req.model,
            "path": str(result_path),
            "url": web_url,
            "prompt": raw_prompt,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ReferenceVariantRequest(BaseModel):
    reference_path: str                    # /generated/xxx.jpg or absolute path
    description: str                       # variant specific, e.g. "winter + heavy snow"
    output_name: str
    model: str = "doubao-seedream-4-5-251128"  # ARK or OpenRouter for reference mode


class ReferenceUploadRequest(BaseModel):
    """接受 base64 图片上传"""
    filename: str
    data: str   # base64 encoded image data


@router.post("/with-reference")
async def api_generate_variant(req: ReferenceVariantRequest):
    """用参考图生成变体（保持构图一致，仅改天气/季节/光线）"""
    target_dir = GENERATED_PUBLIC_DIR

    try:
        result_path = await generate_with_reference(
            model=req.model,
            prompt=req.description,
            output_name=req.output_name,
            reference_path=req.reference_path,
            target_dir=target_dir,
        )
        if result_path is None:
            raise HTTPException(status_code=500, detail="变体生成失败")
        return {
            "success": True,
            "model_used": req.model,
            "path": str(result_path),
            "url": f"/generated/{result_path.name}",
            "description": req.description,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-reference")
async def api_upload_reference(req: ReferenceUploadRequest):
    """上传一张图片作为定妆照参考"""
    import base64 as b64
    try:
        data = b64.b64decode(req.data.split(",", 1)[-1] if req.data.startswith("data:") else req.data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    fname = Path(req.filename).stem + ".jpg"
    # 放 public/generated 便于前端加载
    target_dir = GENERATED_PUBLIC_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    fp = target_dir / fname
    fp.write_bytes(data)

    return {
        "success": True,
        "path": str(fp),
        "url": f"/generated/{fname}",
        "size_kb": len(data) // 1024,
    }
