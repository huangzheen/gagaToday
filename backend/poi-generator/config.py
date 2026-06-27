"""
POI Generator — 配置模块
从环境变量加载密钥和路径
"""

import os
from pathlib import Path

# ── 项目根目录 ──
PROJECT_ROOT = Path("/Volumes/NewDisk/GermanLearning")

# ── 输出目录 ──
ASSETS_ROOT = PROJECT_ROOT / "assets"
CONTENT_DRAFTS_ROOT = PROJECT_ROOT / "frontend" / "src" / "content" / "drafts" / "poi_generator"
CONTENT_MUNICH_ROOT = PROJECT_ROOT / "frontend" / "src" / "content" / "munich"

# ── 数据库 ──
DB_PATH = PROJECT_ROOT / "backend" / "poi-generator" / "game_data.db"

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

# ── 图片生成输出目录（前端可访问）──
GENERATED_PUBLIC_DIR = PROJECT_ROOT / "frontend" / "poi-generator" / "public" / "generated"

# ── CORS ──
CORS_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
