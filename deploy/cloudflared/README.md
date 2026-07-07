# Cloudflare Zero Trust — 接入 gagatoday / poi

## 现状

你的 cloudflared 容器已经用 token 在跑(去 Cloudflare dashboard Networks → Tunnels 看自己的 tunnel id),ingress
规则在 Cloudflare dashboard 上配。`cloud.hzone.biz` 这条就是这么进来的(直接 → `gaga-nextcloud:80`)。

现在加两条,让 gagatoday 和 poi 也走 tunnel。

---

## 操作步骤(2 分钟)

### 1. 打开 Zero Trust dashboard

https://one.dash.cloudflare.com/

→ Networks → Tunnels → 选 tunnel `gagatoday`(你的 tunnel id,见 dashboard)
→ Configure → Public hostname tab → Add a public hostname

### 2. 加第一条: gagatoday.hzone.biz

| 字段 | 值 |
|---|---|
| Subdomain | `gagatoday` |
| Domain | `hzone.biz` |
| Service type | `HTTP` |
| URL | `gagatoday-web:80` |

### 3. 加第二条: poi.hzone.biz

| 字段 | 值 |
|---|---|
| Subdomain | `poi` |
| Domain | `hzone.biz` |
| Service type | `HTTP` |
| URL | `poi-web:80` |

### 4. 保存

dashboard 会自动 push 配置到 cloudflared 容器,无需重启。

---

## 验证

加完后 ~10 秒内生效。验证命令:

```bash
curl -sI https://gagatoday.hzone.biz/ | head -3
# 期望: HTTP/2 200, server: cloudflare

curl -sI https://poi.hzone.biz/ | head -3
# 期望: HTTP/2 200, server: cloudflare
```

如果不通:

1. **容器没起来?** `docker ps | grep -E 'gagatoday|poi-web|gagatoday-api'`
2. **cloudflared 没找到容器?** OrbStack Magic DNS 应该跨网络可达,从 cloudflared 容器测试:
   ```bash
   docker exec cloudflared wget -q -O- http://gagatoday-web/healthz
   # 应返回 "ok"
   ```
3. **dashboard 配置没 push?** 等 30 秒,或在 dashboard 点 "Save" 强制刷新

---

## DNS(自动)

dashboard 加 hostname 会自动在 Cloudflare DNS 加 CNAME 记录:

```
gagatoday.hzone.biz  CNAME  <tunnel-id>.cfargotunnel.com
poi.hzone.biz        CNAME  <tunnel-id>.cfargotunnel.com
```

Cloudflare proxied(橙色云朵)自动开启,免费 SSL 证书自动签发。

---

## 不动 cloudflared 容器

- token 模式跑着别动
- 不需要重启 cloudflared
- 不影响 cloud.hzone.biz / n8n.hzone.biz / 其他现有域名
- 配置是 dashboard 端的事,本地零变更

---

## 架构总览(更新后)

```
Internet
   ↓
Cloudflare Edge (auto HTTPS, DDoS, WAF)
   ↓ Zero Trust Tunnel (encrypted outbound)
   ↓
cloudflared 容器 (token 鉴权, 配置来自 dashboard)
   ↓ OrbStack Magic DNS(容器名 = DNS 名,跨网络解析)
   ↓
┌─────────────────────────────────────────────┐
│ gagatoday-web  ─── gagatoday.hzone.biz      │
│ poi-web        ─── poi.hzone.biz            │
│ gagatoday-api  ─── (内部调用,不直接暴露)     │
│ gaga-nextcloud ─── cloud.hzone.biz (原状)   │
│ ... 已有服务不动 ...                         │
└─────────────────────────────────────────────┘
```