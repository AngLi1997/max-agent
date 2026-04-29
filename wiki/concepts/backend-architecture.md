---
title: 后端架构
type: concept
created: 2026-04-29
updated: 2026-04-29
sources: [backend-app-structure]
tags: [backend, architecture]
related: [[overview]], [[concepts/tech-stack]], [[concepts/rbac]], [[concepts/data-model]]
---

# 后端架构

## 分层结构

```
backend/app/
├── api/            # 路由层
│   ├── router.py   # 路由注册中心
│   └── routes/     # 各模块路由 (auth, health)
├── auth/           # 认证模块
├── core/           # 核心配置
│   ├── config.py   # Settings (pydantic-settings, .env)
│   └── redis.py    # Redis 连接
├── db/             # 数据库层
│   ├── base.py     # SQLAlchemy Base
│   ├── session.py  # AsyncSession 工厂
│   ├── mixins.py   # 通用 Mixin (TimestampMixin)
│   ├── seed.py     # 数据初始化
│   └── user.py     # 用户数据访问
├── models/         # SQLAlchemy ORM 模型
│   ├── user.py     # User (继承 fastapi-users)
│   ├── role.py     # Role + 关联表
│   ├── permission.py # Permission
│   └── menu.py     # Menu (树形自引用)
├── schemas/        # Pydantic 请求/响应模型
│   ├── auth.py
│   └── user.py
└── services/       # 业务逻辑层
    └── auth.py
```

## 关键设计

- **异步优先**：使用 asyncpg + AsyncSession，全链路异步
- **配置管理**：pydantic-settings 从 `.env` 加载，`@lru_cache` 单例
- **认证**：基于 fastapi-users + JWT，token TTL 可配置
- **数据库迁移**：Alembic 管理 schema 变更
- **API 前缀**：统一 `/api` 前缀
