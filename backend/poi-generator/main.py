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
from fastapi.staticfiles import StaticFiles

from .config import ASSETS_ROOT, CORS_ORIGINS
from .routers import game_content

# Phase 2: text/image/save/pois_v2/osm/wiki 这些 router 依赖 openai/dashscope 等
# 在 dev/ci 环境可能没装,用 try/except 包裹 — 缺时不挂载,但不阻断 uvicorn 启动
try:
    from .routers import text, image, save, pois_v2, osm, wiki  # noqa: F401
    _HEAVY_ROUTERS_AVAILABLE = True
except ImportError as _e:
    print(f"[warn] Heavy routers 未加载(openai/dashscope 等): {_e}", flush=True)
    _HEAVY_ROUTERS_AVAILABLE = False

# db_service 用了 Python 3.10+ 语法(PEP 604 union),Python 3.9 跑不动
# Phase 2 game_content 不依赖它,缺时跳过 init_db()
try:
    from .services.db_service import init_db as _init_db
    _DB_SERVICE_AVAILABLE = True
except (ImportError, SyntaxError, TypeError) as _e:
    print(f"[warn] db_service 未加载(Python 兼容问题): {_e}", flush=True)
    _init_db = None
    _DB_SERVICE_AVAILABLE = False

app = FastAPI(
    title="gagaToday POI 内容生成器",
    description="为德国留学模拟 RPG 生成 POI 全套内容（图片、NPC、对话、知识卡、剧情等）",
    version="0.2.0",
)

# CORS — 允许前端 Vite dev server 调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 3: 静态资源 — scene 图 / audio / 未来 sprite 等
# 必须先于路由 mount(否则 /assets/* 会被路由接管)
if ASSETS_ROOT.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(ASSETS_ROOT), check_dir=False),
        name="assets",
    )

# 注册 Phase 2 路由(必需)
app.include_router(game_content.router)

# 注册历史路由(可选,缺依赖时跳过)
if _HEAVY_ROUTERS_AVAILABLE:
    from .routers import text, image, save, pois_v2, osm, wiki
    app.include_router(text.router)
    app.include_router(image.router)
    app.include_router(save.router)
    app.include_router(pois_v2.router)
    app.include_router(osm.router)
    app.include_router(wiki.router)


@app.on_event("startup")
async def startup():
    """启动时初始化数据库(可选)"""
    if _DB_SERVICE_AVAILABLE and _init_db:
        _init_db()


@app.get("/")
async def root():
    return {
        "service": "gagaToday POI 内容生成器",
        "version": "0.2.0",
        "endpoints": {
            "POST /api/generate/text": "LLM 自由文本生成",
            "POST /api/generate/json": "LLM 结构化 JSON 生成",
            "POST /api/generate/image": "AI 图片生成",
            "POST /api/save/json": "保存 JSON 到 drafts",
            "POST /api/save/image": "保存图片到 assets",
            "POST /api/save/source": "保存来源记录",
            "GET  /api/pois": "列出已有 draft 的 POI",
            "GET  /api/pois/{id}": "获取指定 POI 的数据",
            "GET  /api/game/v1/cities": "列出所有可用城市(Phase 2)",
            "GET  /api/game/v1/cities/{city_id}/bundle": "取 CityBundle,支持 ETag/304(Phase 2)",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health")
async def api_health():
    """前端代理用的 health 端点"""
    return {"status": "ok"}
