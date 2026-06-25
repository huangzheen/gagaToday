#!/usr/bin/env bash
# scripts/start.sh — gagaToday 3 服务一键启动
#
# 用法:   bash scripts/start.sh
# 停服:   bash scripts/stop.sh
#
# 启动的 3 个服务：
#   8000  后端 API  (uvicorn)
#   8081  地图前端  (node server.cjs)
#   5174  素材生成器 (vite --host)
#
# 注意：本脚本为用户终端设计（用 nohup & 后台化）。
#      Codex 沙盒里的启动方式见脚本底部注释。

set -e

ROOT="/Volumes/NewDisk/GermanLearning"
PIDS_FILE="/tmp/gagaToday-services.pids"
LOG_DIR="/tmp"

echo "🧹 清理端口 8000/8081/5174 上的旧进程..."
for port in 8000 8081 5174; do
  pids=$(lsof -nP -iTCP:$port -sTCP:LISTEN -t 2>/dev/null)
  if [ -n "$pids" ]; then
    echo "  port $port: killing $pids"
    kill -9 $pids 2>/dev/null || true
  fi
done
sleep 1

> "$PIDS_FILE"

echo ""
echo "🗺️  启动地图 (port 8081)..."
cd "$ROOT/frontend"
nohup node server.cjs > "$LOG_DIR/gagaToday-map.log" 2>&1 &
echo $! >> "$PIDS_FILE"

echo "🎨  启动生成器 (port 5174)..."
cd "$ROOT/frontend/poi-generator"
nohup npx vite --host > "$LOG_DIR/gagaToday-vite.log" 2>&1 &
echo $! >> "$PIDS_FILE"

echo "⚙️  启动后端 (port 8000)..."
source /Volumes/NewDisk/.agent-secrets/secrets.env
cd "$ROOT"
nohup uvicorn backend.poi-generator.main:app --reload --port 8000 \
  > "$LOG_DIR/gagaToday-backend.log" 2>&1 &
echo $! >> "$PIDS_FILE"

sleep 3

echo ""
echo "✅ 启动完成"
echo "  地图:     http://localhost:8081"
echo "  生成器:  http://localhost:5174"
echo "  后端:    http://localhost:8000/docs"
echo ""
echo "📋 PIDs: $PIDS_FILE"
echo "📜 日志: tail -f $LOG_DIR/gagaToday-{map,vite,backend}.log"
echo "🛑 停服: bash $ROOT/scripts/stop.sh"

# === Codex 沙盒启动方式（参考） ===
# Codex 沙盒里 nohup & 会被 reaper 杀掉，必须用 exec 前台模式 + session_id 保活。
# 每个服务一条 exec_command（require_escalated，yield_time_ms 5-8s）：
#
#   cd /Volumes/NewDisk/GermanLearning/frontend && exec node server.cjs
#   cd /Volumes/NewDisk/GermanLearning/frontend/poi-generator && exec npx vite --host
#   cd /Volumes/NewDisk/GermanLearning && source /Volumes/NewDisk/.agent-secrets/secrets.env \\
#     && exec uvicorn backend.poi-generator.main:app --reload --port 8000
#
# 返回的 session_id 用 write_stdin 可交互（Ctrl-C 停服等）。
