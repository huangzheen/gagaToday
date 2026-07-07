"""
POI Generator — 配置模块
从环境变量加载密钥和路径

路径相关变量支持 env override(容器化部署时用):
  PROJECT_ROOT  默认 /Volumes/NewDisk/GermanLearning(开发机)
  ASSETS_ROOT   默认 $PROJECT_ROOT/assets
  DB_PATH       默认 $PROJECT_ROOT/backend/poi-generator/game_data.db
  CONTENT_DRAFTS_ROOT  默认 $PROJECT_ROOT/frontend/src/content/drafts/poi_generator
  CONTENT_MUNICH_ROOT  默认 $PROJECT_ROOT/frontend/src/content/munich
  GENERATED_PUBLIC_DIR 默认 $PROJECT_ROOT/frontend/poi-generator/public/generated
"""

import os
from pathlib import Path

# ── 项目根目录(可 env 覆盖,容器部署时改成 /app) ──
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", "/Volumes/NewDisk/GermanLearning"))

# ── 输出目录(每个都允许 env 覆盖) ──
ASSETS_ROOT = Path(os.environ.get("ASSETS_ROOT", str(PROJECT_ROOT / "assets")))
CONTENT_DRAFTS_ROOT = Path(
    os.environ.get(
        "CONTENT_DRAFTS_ROOT",
        str(PROJECT_ROOT / "frontend" / "src" / "content" / "drafts" / "poi_generator"),
    )
)
CONTENT_MUNICH_ROOT = Path(
    os.environ.get(
        "CONTENT_MUNICH_ROOT",
        str(PROJECT_ROOT / "frontend" / "src" / "content" / "munich"),
    )
)

# ── 数据库(可 env 覆盖) ──
DB_PATH = Path(
    os.environ.get(
        "DB_PATH",
        str(PROJECT_ROOT / "backend" / "poi-generator" / "game_data.db"),
    )
)

# ── API 密钥 ──
# DashScope (Qwen LLM)
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-0a581f1d36c9464ab2dfe19a9e32cc73")

# DeepSeek (V4 系列 — chat/reasoner 2026/07/24 弃用)
# 按 INVENTORY §6 约定,项目隔离的 key 在 vault 里以 GERMANLEARNING_ 前缀存在;
# 同时兼容裸 DEEPSEEK_API_KEY(开发/调试场景直接 export)
DEEPSEEK_API_KEY = (
    os.environ.get("GERMANLEARNING_DEEPSEEK_API_KEY", "")
    or os.environ.get("DEEPSEEK_API_KEY", "")
)
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# Brave Search (Wikipedia DE 缺失时的 fallback 搜索)
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "") or os.environ.get("BRAVE_SEARCH_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# ── 默认模型 ──
# DeepSeek V4 Flash 作为日常默认(快、质量好、token 友好);
# 复杂任务(NPC、剧情、知识卡)仍走 Qwen3-Max(更稳)
LLM_MODEL_DEFAULT = "deepseek-v4-flash"  # 日常生成
LLM_MODEL_COMPLEX = "qwen3-max"          # 复杂任务(知识卡、剧情)

# ── 模型 provider 路由(按 model id 前缀) ──
def get_provider(model: str) -> str:
    """根据 model id 决定走 DashScope 还是 DeepSeek"""
    if not model:
        return "dashscope"
    m = model.lower()
    if m.startswith("deepseek"):
        return "deepseek"
    return "dashscope"

# ── 图片参数 ──
IMAGE_DEFAULT_STYLE = "16-bit pixel art, hard pixel edges no anti-aliasing, limited 16-color palette, retro JRPG style"
IMAGE_DEFAULT_ASPECT = "16:9"
IMAGE_DEFAULT_RESOLUTION = "1K"

# ── 图片生成输出目录(前端可访问) ──
GENERATED_PUBLIC_DIR = Path(
    os.environ.get(
        "GENERATED_PUBLIC_DIR",
        str(PROJECT_ROOT / "frontend" / "poi-generator" / "public" / "generated"),
    )
)

# ── CORS ──
# dev: Vite 本地端口
# prod: cloudflared 隧道后的域名(Zero Trust 自动 HTTPS,允许跨子域同源调用)
CORS_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "https://gagatoday.hzone.biz",
    "https://poi.hzone.biz",
]
