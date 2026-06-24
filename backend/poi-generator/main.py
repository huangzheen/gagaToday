"""
POI 内容生成器 — FastAPI 后端入口

启动方式:
  cd /Volumes/NewDisk/GermanLearning
  source /Volumes/NewDisk/.agent-secrets/secrets.env
  uvicorn backend.poi-generator.main:app --reload --port 8000
"""

import sys
from pathlib import Path

# 确保 backend 包可导入
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .routers import text, image, save, pois_v2
from .services.db_service import init_db

app = FastAPI(
    title="gagaToday POI 内容生成器",
    description="为德国留学模拟 RPG 生成 POI 全套内容（图片、NPC、对话、知识卡、剧情等）",
    version="0.1.0",
)

# CORS — 允许前端 Vite dev server 调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(text.router)
app.include_router(image.router)
app.include_router(save.router)
app.include_router(pois_v2.router)


@app.on_event("startup")
async def startup():
    """启动时初始化数据库"""
    init_db()


@app.get("/")
async def root():
    return {
        "service": "gagaToday POI 内容生成器",
        "version": "0.1.0",
        "endpoints": {
            "POST /api/generate/text": "LLM 自由文本生成",
            "POST /api/generate/json": "LLM 结构化 JSON 生成",
            "POST /api/generate/image": "AI 图片生成",
            "POST /api/save/json": "保存 JSON 到 drafts",
            "POST /api/save/image": "保存图片到 assets",
            "POST /api/save/source": "保存来源记录",
            "GET  /api/pois": "列出已有 draft 的 POI",
            "GET  /api/pois/{id}": "获取指定 POI 的数据",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health")
async def api_health():
    """前端代理用的 health 端点"""
    return {"status": "ok"}
