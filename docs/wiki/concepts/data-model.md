---
title: 数据模型
type: concept
created: 2026-04-29
updated: 2026-04-30
sources: [models-user, models-role, models-permission, models-menu, models-logs, models-config]
tags: [database, backend, model]
related: [[concepts/rbac]], [[concepts/backend-architecture]], [[entities/postgresql]]
---

# 数据模型

## ER 关系

```
┌──────────┐     ┌────────────┐     ┌──────────┐
│   User   │────>│ user_roles │<────│   Role   │
└──────────┘     └────────────┘     └──────────┘
     │                                    │
     │                              ┌────────────────┐
     │                              │role_permissions │
     │                              └────────────────┘
     │                                    │
     │                              ┌────────────┐
     │                              │ Permission │
     │                              └────────────┘
     │
     ├──> OperationLog (operator_id FK)
     └──> LoginLog (user_id FK)

┌──────────┐
│   Menu   │──(self-ref: parent_id)
└──────────┘

┌──────────────┐
│ SystemConfig │ (独立，无 FK)
└──────────────┘
```

## 模型详情

### User
- 继承 `SQLAlchemyBaseUserTable[int]` + `TimestampMixin`
- 字段：`id`, `username`(unique), `email`(unique), `hashed_password`, `avatar`, `status`, `is_active`, `is_superuser`, `is_verified`, `is_builtin`, `must_change_password`
- 关系：`roles` (M:N via user_roles)

### Role
- 字段：`id`, `name`(unique), `code`(unique), `description`, `status`, `is_builtin`
- 关系：`users` (M:N), `permissions` (M:N via role_permissions)

### Permission
- 字段：`id`, `name`, `identifier`(unique), `type`, `status`
- 关系：`roles` (M:N)

### Menu
- 树形自引用：`parent_id` → `menu.id`
- 字段：`id`, `name`, `path`, `component`, `permission`, `icon`, `sort`, `status`, `parent_id`
- `children` 按 `sort` 排序，级联删除

### OperationLog
- 字段：`id`, `operator_id`(FK→user), `operator_name`, `module`, `action`, `method`, `result`, `detail`, `ip`

### LoginLog
- 字段：`id`, `user_id`(FK→user), `username`, `ip`, `location`, `device`, `result`, `detail`

### SystemConfig
- 字段：`id`, `name`, `key`(unique), `value`, `description`

## 关联表

- `user_roles`：用户-角色多对多（CASCADE 删除）
- `role_permissions`：角色-权限多对多（CASCADE 删除）

## 通用 Mixin

`TimestampMixin`：为所有模型提供 `created_at` / `updated_at` 时间戳。

## 数据库

- PostgreSQL 17 + pgvector 扩展
- 异步驱动：asyncpg
- 迁移工具：Alembic（2 个版本：初始 schema + 系统设置 RBAC）
- 连接管理：`AsyncSession` + `async_sessionmaker`
