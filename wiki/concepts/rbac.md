---
title: RBAC 权限模型
type: concept
created: 2026-04-29
updated: 2026-04-29
sources: [models-user, models-role, models-permission, models-menu]
tags: [rbac, auth, backend]
related: [[overview]], [[concepts/data-model]], [[concepts/backend-architecture]]
---

# RBAC 权限模型

## 三层结构

```
User ──M:N──> Role ──M:N──> Permission
                              │
Menu (树形，含 permission 字段) ─┘
```

## 关联表

- `user_roles`：用户-角色多对多（CASCADE 删除）
- `role_permissions`：角色-权限多对多（CASCADE 删除）

## 实体说明

### User
- 继承 `SQLAlchemyBaseUserTable[int]`（fastapi-users）
- 扩展字段：`username`（唯一）、`avatar`
- 通过 `roles` 关联角色

### Role
- 字段：`name`（唯一）、`code`（唯一索引）、`description`、`status`
- 双向关联 `users` 和 `permissions`

### Permission
- 字段：`name`、`identifier`（唯一索引）、`type`、`status`
- 通过 `roles` 反向关联角色

### Menu
- 树形自引用结构（`parent_id` → `menu.id`）
- 字段：`name`、`path`、`permission`、`icon`、`sort`、`status`
- `children` 按 `sort` 排序，级联删除
