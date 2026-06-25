#!/bin/bash
# gagaToday POI 内容生成器 — 一键启动脚本
# 用法: bash backend/poi-generator/start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 启动 gagaToday POI 内容生成器..."
echo ""

# 1. 加载 API 密钥
SECRETS_FILE="/Volumes/NewDisk/.agent-secrets/secrets.env"
if [ -f "$SECRETS_FILE" ]; then
  echo "🔑 加载 API 密钥..."
  source "$SECRETS_FILE"
  export DASHSCOPE_API_KEY
fi

# 2. 启动 FastAPI 后端
echo "📡 启动后端 (FastAPI :8000)..."
uvicorn backend.poi-generator.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 3. 启动 Vite 前端
echo "🖥️  启动前端 (Vite :5174)..."
cd "$PROJECT_ROOT/frontend/poi-generator" && npx vite --port 5174 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

echo ""
echo "✅ 已启动！"
echo "   前端: http://localhost:5174/"
echo "   后端: http://localhost:8000/"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待子进程
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
