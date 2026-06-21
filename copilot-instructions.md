---
applyTo: "**"
---

# 项目规则 (copilot-instructions)

本文件为本项目的工作约定,适用于所有 Copilot 代理会话。

## 1. 语言
- **永远使用中文**与用户交流项目信息、状态、操作动作。
- 代码、变量名、文件名、commit message 等保持英文(技术性内容用英文)。

## 2. Git / GitHub
- 任何代码 / 配置 / 文档更新(新增、修改、删除文件)完成后,都必须:
  1. `git add` 相关变更
  2. `git commit -m "<清晰的变更说明>"`
  3. `git push origin main` 推送到 https://github.com/huangzheen/gagaToday
- commit message 简洁清晰,使用中文或英文皆可。
- 不要跳过推送步骤,本地与远端必须保持一致。

## 3. 部署
- 项目应部署在**本机 Docker** 内部。
- 任何新增 / 改动服务时,需同步更新 `Dockerfile` 与 `docker-compose.yml`。
- 启动方式优先使用 `docker compose up -d`(若只有单容器则用 `docker run`)。
- 镜像构建失败、容器无法启动时,优先排查 Docker 端,不要在宿主机直接跑服务。