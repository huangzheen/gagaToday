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

# ── 默认模型 ──
LLM_MODEL_DEFAULT = "qwen-plus"        # 日常生成
LLM_MODEL_COMPLEX = "qwen3-max"        # 复杂任务(知识卡、剧情)

# ── 图片参数 ──
IMAGE_DEFAULT_STYLE = "16-bit pixel art, hard pixel edges no anti-aliasing, limited 16-color palette, retro JRPG style"
IMAGE_DEFAULT_ASPECT = "16:9"
IMAGE_DEFAULT_RESOLUTION = "1K"

# ── 图片生成输出目录（前端可访问）──
GENERATED_PUBLIC_DIR = PROJECT_ROOT / "frontend" / "poi-generator" / "public" / "generated"

# ── CORS ──
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
