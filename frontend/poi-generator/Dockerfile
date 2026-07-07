# gagaToday poi-generator — Vue 3 + Vite SPA(运营/编辑用)
# 多阶段构建,跟 game-client 同结构
#
# docker build context = 项目根(GermanLearning/)

# ── Stage 1: build ──
FROM node:20-alpine AS builder

WORKDIR /build

COPY frontend/poi-generator/package.json \
     frontend/poi-generator/package-lock.json \
     /build/
RUN npm ci --no-audit --no-fund

COPY frontend/poi-generator/ /build/
RUN npm run build

# ── Stage 2: serve ──
FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY deploy/nginx/poi.conf /etc/nginx/conf.d/poi.conf

COPY --from=builder /build/dist/ /usr/share/nginx/html/

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1/healthz || exit 1

EXPOSE 80