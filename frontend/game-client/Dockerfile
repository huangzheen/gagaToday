# gagaToday game-client — Vue 3 + Vite SPA
# 多阶段构建:node builder → nginx serve dist/
#
# docker build context = 项目根(GermanLearning/)
# 用法:
#   docker build -f frontend/game-client/Dockerfile -t gagatoday-game-client:latest .
#   # 构建时会跑 vue-tsc + vite build,需要把 node_modules 排除(.dockerignore 处理)

# ── Stage 1: build ──
FROM node:20-alpine AS builder

WORKDIR /build

# 1. 依赖(cache 友好)
COPY frontend/game-client/package.json \
     frontend/game-client/package-lock.json \
     /build/
RUN npm ci --no-audit --no-fund

# 2. 源码(从项目根拷,因为 vite.config.ts 用 path.resolve(__dirname, './src'))
COPY frontend/game-client/ /build/

# 3. 构建
#    Vite 默认输出到 dist/
#    如果 build 时需要 API key 等,在 build-arg 里传(目前 game-client 没用到)
RUN npm run build

# ── Stage 2: serve ──
FROM nginx:1.27-alpine

# 默认配置不要,用自己的
RUN rm /etc/nginx/conf.d/default.conf

COPY deploy/nginx/gagatoday.conf /etc/nginx/conf.d/gagatoday.conf

# dist/ 从 builder 拷到 nginx serve 目录
COPY --from=builder /build/dist/ /usr/share/nginx/html/

# 健康检查
# 注意: alpine 镜像里 wget 默认走 IPv6 (::1),但 nginx listen IPv4
# 所以用 curl + 127.0.0.1 强制 IPv4
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1/healthz || exit 1

EXPOSE 80

# nginx -g "daemon off;" 是官方镜像默认 CMD,不用改