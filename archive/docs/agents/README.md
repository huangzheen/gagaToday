# 智能体说明 (B 方案，未实现)

> ⚠️ **本文档说明的智能体未在当前实现中跟进**（标记于 2026-06-25 文档收敛）

本目录包含 17 个角色化智能体的设计文档，是 2026-06-21 起草的 **B 方案（30 天生活模拟）** 配套定义。

## 状态

- 这些是面向 B 方案"多智能体协作"模型的**角色定义**（NPC 智能体 / 美食智能体 / 课程智能体 / ...）
- **当前实现（A 方案：POI 探索 + 素材生成器）不依赖这些智能体**
- 当前 AI 能力统一封装在 FastAPI 后端的 `services/llm_service.py` 和 `services/multi_image_service.py`

## 是否保留

保留作为远景参考。如果未来决定：
- 启动 B 方案：这些定义是直接可用的起点
- 继续 A 方案：可以删除整个 `docs/agents/` 目录，或者把有价值的角色定义（如 NPC 智能体）接入 POI 生成器的内容审核工作流

## 关联文档

- [README.md](../../README.md) — 当前架构
- [docs/ARCHITECTURE.md](../ARCHITECTURE.md) — 当前实现
- [docs/AGENT_WORKFLOW.md](../AGENT_WORKFLOW.md) — 中性的多 agent 协作约定（不限于这 17 个角色）
