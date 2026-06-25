#!/usr/bin/env bash
# scripts/stop.sh — 停 gagaToday 3 个服务
#
# 用法:   bash scripts/stop.sh
# 起服:   bash scripts/start.sh

PIDS_FILE="/tmp/gagaToday-services.pids"

echo "🛑 按 $PIDS_FILE 杀..."
if [ -f "$PIDS_FILE" ]; then
  while read pid; do
    [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null && echo "  killed $pid" || true
  done < "$PIDS_FILE"
  rm -f "$PIDS_FILE"
else
  echo "  (无 PIDs 文件)"
fi

echo ""
echo "🧹 按端口 8000/8081/5174 兜底..."
for port in 8000 8081 5174; do
  pids=$(lsof -nP -iTCP:$port -sTCP:LISTEN -t 2>/dev/null)
  if [ -n "$pids" ]; then
    kill -9 $pids 2>/dev/null && echo "  port $port: killed $pids"
  else
    echo "  port $port: free"
  fi
done

echo ""
echo "✅ 全部停完"
