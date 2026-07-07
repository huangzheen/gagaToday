# gagaToday OrbStack 部署指南

## 架构

```
Internet
  ↓ Cloudflare Edge (auto HTTPS)
cloudflared 容器 (复用, Zero Trust Tunnel)
  ↓ OrbStack Magic DNS
┌────────────────────────────────────┐
│ gagatoday-web   (nginx + Vue)      │ → gagatoday.hzone.biz
│ poi-web         (nginx + Vue)      │ → poi.hzone.biz
│ gagatoday-api   (FastAPI)          │ → 内部 8000
└────────────────────────────────────┘
         ↑ 18GB assets volume
         ↑ SQLite volume
         ↑ secrets.env (vault)
```

## 快速启动

```bash
# 1. 准备 .env
cp deploy/.env.example deploy/.env
# 编辑 deploy/.env,或者 start.sh 会自动从 vault 同步

# 2. 启动
bash deploy/scripts/start.sh up

# 3. 接入 Cloudflare(2 分钟)
#    按 deploy/cloudflared/README.md 在 dashboard 加 2 条 hostname

# 4. 验证
curl -sI https://gagatoday.hzone.biz/ | head -3
curl -sI https://poi.hzone.biz/ | head -3
```

## 文件结构

```
deploy/
├── docker-compose.yml      # 3 服务编排
├── .env.example            # 环境变量模板
├── nginx/
│   ├── gagatoday.conf      # SPA + /api + /assets 反代
│   └── poi.conf            # 同上,独立配置
├── cloudflared/
│   └── README.md           # Zero Trust dashboard 操作手册
└── scripts/
    └── start.sh            # 一键 build + up / down / logs / status
```

## 代码改动(部署相关)

| 文件 | 改动 |
|---|---|
| `backend/poi-generator/config.py` | PROJECT_ROOT/ASSETS_ROOT/DB_PATH 等改成 env-driven,加 prod CORS 域名 |
| `frontend/poi-generator/src/App.vue` | 3 处 hardcoded `http://127.0.0.1:8000` → `/api` |

未改动: business logic / 路由 / 业务代码全部保留。

## 端口分配

| 容器 | 内部端口 | Host 端口(仅调试) |
|---|---|---|
| gagatoday-api | 8000 | 127.0.0.1:18000 |
| gagatoday-web | 80 | (expose, 不映射) |
| poi-web | 80 | (expose, 不映射) |

正式访问: 走 cloudflared → 容器名:80,不经过 host 端口。

## 部署后 Phase 6 TODO

- [ ] /assets 18GB PMTiles 迁移到 MinIO 或 OSS(s3.hzone.biz 已就绪)
- [ ] cloudflared 改成 config.yml 模式(版本可控,目前是 token 模式)
- [ ] 给 api 容器加 Sentry / OpenTelemetry
- [ ] SQLite 切 Postgres(多人并发时 SQLite 容易锁)
- [ ] CI 跑 `docker compose config` 验证 + `docker build` smoke test

## 故障排查

```bash
# 看容器状态
docker ps | grep gagatoday

# 看 api 日志
docker logs gagatoday-api --tail=50

# 看 web 容器内 nginx 配
docker exec gagatoday-web cat /etc/nginx/conf.d/gagatoday.conf

# 测试 cloudflared → 容器连通
docker exec cloudflared wget -q -O- http://gagatoday-web/healthz
docker exec cloudflared wget -q -O- http://poi-web/healthz
docker exec cloudflared wget -q -O- http://gagatoday-api:8000/health
```

## 回滚

```bash
bash deploy/scripts/start.sh down
# 数据保留在 gagatoday-api-db volume
docker volume rm gagatoday-api-db  # 真要清才跑
```