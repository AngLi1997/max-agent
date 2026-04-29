---
title: 技术栈
type: concept
created: 2026-04-29
updated: 2026-04-29
sources: [pyproject-toml, package-json, docker-compose]
tags: [tech-stack, overview]
related: [[overview]], [[concepts/backend-architecture]], [[concepts/frontend-architecture]], [[entities/postgresql]], [[entities/redis]], [[entities/minio]]
---

# 技术栈

## 前端

| 技术 | 用途 |
|------|------|
| Vue 3 | UI 框架，Composition API |
| TypeScript | 类型安全 |
| Vite | 构建工具与开发服务器 |
| Ant Design Vue | UI 组件库 |
| Pinia | 状态管理 |
| Vue Router | 前端路由 |
| Axios | HTTP 请求 |

## 后端

| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架 (ASGI) |
| SQLAlchemy 2.x | ORM，async 模式 |
| Pydantic / pydantic-settings | 数据校验与配置管理 |
| fastapi-users | 用户认证与管理 |
| asyncpg | PostgreSQL 异步驱动 |
| Alembic | 数据库迁移 |
| Uvicorn | ASGI 服务器 |
| uv | Python 依赖管理 |

## 基础设施

| 服务 | 镜像 | 端口 |
|------|------|------|
| PostgreSQL + pgvector | pgvector/pgvector:pg17 | 5432 |
| Redis | redis:7.4-alpine | 6379 |
| MinIO | minio/minio:RELEASE.2025-02-28 | 9000 (API) / 9001 (控制台) |
