---
title: 技术栈
type: concept
created: 2026-04-29
updated: 2026-04-30
sources: [pyproject-toml, package-json, docker-compose]
tags: [tech-stack, overview]
related: [[overview]], [[concepts/backend-architecture]], [[concepts/frontend-architecture]], [[entities/postgresql]], [[entities/redis]], [[entities/minio]]
---

# 技术栈

## 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.5.32 | UI 框架，Composition API |
| TypeScript | ~6.0.2 | 类型安全 |
| Vite | ^8.0.10 | 构建工具与开发服务器 |
| Ant Design Vue | ^4.2.6 | UI 组件库 |
| Pinia | ^3.0.4 | 状态管理 |
| Vue Router | ^4.6.4 | 前端路由 |
| Axios | ^1.15.2 | HTTP 请求 |
| ECharts | ^6.0.0 | 图表库 |
| vue-echarts | ^8.0.1 | Vue ECharts 集成 |
| @ant-design/icons-vue | ^7.0.1 | 图标库 |

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
| argon2-cffi | 密码哈希 |
| pytest | 测试框架 |

## 基础设施

| 服务 | 镜像 | 端口 |
|------|------|------|
| PostgreSQL + pgvector | pgvector/pgvector:pg17 | 5432 |
| Redis | redis:7.4-alpine | 6379 |
| MinIO | minio/minio:RELEASE.2025-02-28 | 9000 (API) / 9001 (控制台) |

## 开发环境

- Vite 代理：`/api` → `http://127.0.0.1:8000`（开发时前后端联调）
- 后端启动：`uv run uvicorn main:app --reload`
- 前端启动：`pnpm dev`
