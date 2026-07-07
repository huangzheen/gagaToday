# gagaToday FastAPI Backend
# 多阶段不必要(纯 Python),但分 cache 层加速重建
#
# 启动: uvicorn backend.poi-generator.main:app --host 0.0.0.0 --port 8000
# 路径: docker context = 项目根目录(GermanLearning/)

FROM python:3.12-slim AS base

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 仅装 curl 做 HEALTHCHECK(uvicorn[standard] 还需要 gcc 但 slim 已含)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── 1. Python 依赖层(cache 友好) ──
COPY backend/poi-generator/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# ── 2. 代码 ──
# docker build context 是项目根,所以 backend/ 整目录拷过去
COPY backend/ ./backend/

# ── 3. 路径 override ──
# 容器里代码在 /app/backend,但 PROJECT_ROOT 默认是 /Volumes/NewDisk/GermanLearning
# 必须用 env var 覆盖。注意:ASSETS_ROOT / DB_PATH 在 config.py 里也都支持 env override
ENV PROJECT_ROOT=/app \
    ASSETS_ROOT=/assets \
    DB_PATH=/data/game_data.db \
    CONTENT_DRAFTS_ROOT=/app/frontend/src/content/drafts/poi_generator \
    CONTENT_MUNICH_ROOT=/app/frontend/src/content/munich \
    GENERATED_PUBLIC_DIR=/app/frontend/poi-generator/public/generated

# ── 4. 健康检查 ──
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

EXPOSE 8000

# ── 5. 启动 ──
# 注意 main.py 第 14 行 sys.path.insert 依赖文件位置:
#   __file__=/app/backend/poi-generator/main.py
#   .parent.parent.parent=/app → 跟 PROJECT_ROOT 一致
# uvicorn 用 importlib 解析 backend.poi-generator(目录名带 dash 是历史包袱,见 backend/conftest.py)
CMD ["uvicorn", "backend.poi-generator.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]