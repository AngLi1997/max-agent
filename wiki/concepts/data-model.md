---
title: 数据模型
type: concept
created: 2026-04-29
updated: 2026-04-29
sources: [models-user, models-role, models-permission, models-menu]
tags: [database, backend, model]
related: [[concepts/rbac]], [[concepts/backend-architecture]], [[entities/postgresql]]
---

# 数据模型

## ER 关系

```
┌──────────┐     ┌────────────┐     ┌──────────┐
│   User   │────>│ user_roles │<────│   Role   │
└──────────┘     └────────────┘     └──────────┘
                                         │
                                    ┌────────────────┐
                                    │role_permissions │
                                    └────────────────┘
                                         │
                                    ┌────────────┐
                                    │ Permission │
                                    └────────────┘

┌──────────┐
│   Menu   │──(self-ref: parent_id)
└──────────┘
```

## 通用 Mixin

`TimestampMixin`：为所有模型提供 `created_at` / `updated_at` 时间戳。

## 数据库

- PostgreSQL 17 + pgvector 扩展
- 异步驱动：asyncpg
- 迁移工具：Alembic
- 连接管理：`AsyncSession` + `async_sessionmaker`
