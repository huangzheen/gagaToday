#!/bin/bash
# gagaToday 部署脚本
# 用法:
#   bash deploy/scripts/start.sh            # build + up
#   bash deploy/scripts/start.sh down       # down
#   bash deploy/scripts/start.sh logs       # 跟日志
#   bash deploy/scripts/start.sh status     # 健康检查
#   bash deploy/scripts/start.sh restart    # 重启

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$DEPLOY_DIR/.." && pwd)"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.yml"
ENV_FILE="$DEPLOY_DIR/.env"

# ── 1. 检查 .env ──
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ $ENV_FILE 不存在"
  echo "   cp $DEPLOY_DIR/.env.example $ENV_FILE"
  echo "   然后从 /Volumes/NewDisk/.agent-secrets/secrets.env 拷真实 API key 进去"
  exit 1
fi

# ── 2. 检查 vault ──
SECRETS="/Volumes/NewDisk/.agent-secrets/secrets.env"
if [ ! -f "$SECRETS" ]; then
  echo "❌ vault 文件不存在: $SECRETS"
  echo "   部署需要从 vault 加载 API key"
  exit 1
fi

# ── 3. 自动从 vault 补 key 到 .env(只在缺时) ──
# 这样用户不用手动复制,保持单一真相源
if grep -q '^DASHSCOPE_API_KEY=sk-placeholder' "$ENV_FILE" 2>/dev/null; then
  echo "🔑 从 vault 同步 API key 到 .env..."
  # shellcheck disable=SC1090
  set -a; source "$SECRETS"; set +a
  sed -i.bak \
    -e "s|^DASHSCOPE_API_KEY=.*|DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}|" \
    -e "s|^GERMANLEARNING_DEEPSEEK_API_KEY=.*|GERMANLEARNING_DEEPSEEK_API_KEY=${GERMANLEARNING_DEEPSEEK_API_KEY}|" \
    -e "s|^BRAVE_API_KEY=.*|BRAVE_API_KEY=${BRAVE_API_KEY}|" \
    "$ENV_FILE"
  rm -f "$ENV_FILE.bak"
  chmod 600 "$ENV_FILE"
  echo "   ✓ .env 已更新"
fi

# ── 4. 子命令分发 ──
CMD="${1:-up}"

cd "$PROJECT_ROOT"

case "$CMD" in
  up)
    echo "🏗️  docker compose build + up..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build
    echo ""
    echo "✅ 已启动"
    echo "   api 健康检查:"
    sleep 5
    curl -sf http://127.0.0.1:18000/health && echo "   ✓ api :8000 healthy" || echo "   ⚠️  api 还没起来,等几秒再试"
    echo ""
    echo "🌐 接下来:"
    echo "   1. Cloudflare Zero Trust dashboard 加两个 hostname(见 deploy/cloudflared/README.md)"
    echo "   2. 浏览器访问:"
    echo "      https://gagatoday.hzone.biz/"
    echo "      https://poi.hzone.biz/"
    ;;
  down)
    echo "🛑 docker compose down..."
    docker compose -f "$COMPOSE_FILE" down
    ;;
  restart)
    echo "🔄 restart..."
    docker compose -f "$COMPOSE_FILE" restart
    ;;
  logs)
    docker compose -f "$COMPOSE_FILE" logs -f --tail=100
    ;;
  status)
    docker compose -f "$COMPOSE_FILE" ps
    echo "---"
    curl -sf http://127.0.0.1:18000/health && echo "✓ api healthy" || echo "✗ api down"
    ;;
  build)
    echo "🏗️  build only..."
    docker compose -f "$COMPOSE_FILE" build
    ;;
  *)
    echo "用法: $0 {up|down|restart|logs|status|build}"
    exit 1
    ;;
esac