---
title: RBAC 权限模型
type: concept
created: 2026-04-29
updated: 2026-04-30
sources: [models-user, models-role, models-permission, models-menu, services-rbac, services-authorization, seed-data]
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
- 扩展字段：`username`(唯一)、`avatar`、`status`、`is_builtin`、`must_change_password`
- 通过 `roles` 关联角色
- 内置用户不允许删除

### Role
- 字段：`name`(唯一)、`code`(唯一索引)、`description`、`status`、`is_builtin`
- 双向关联 `users` 和 `permissions`
- 内置角色不允许删除，已绑定用户的角色不允许删除

### Permission
- 字段：`name`、`identifier`(唯一索引)、`type`、`status`
- 通过 `roles` 反向关联角色
- 类型：菜单权限、按钮权限、API 权限

### Menu
- 树形自引用结构（`parent_id` → `menu.id`）
- 字段：`name`、`path`、`component`、`permission`、`icon`、`sort`、`status`
- `children` 按 `sort` 排序，级联删除

## 认证机制

- Bearer Token 认证（fastapi-users）
- Redis 存储 token（key 前缀：`max_agent_token:`）
- 滑动窗口策略：每次读取 token 自动延长 TTL（默认 30 分钟）

## 授权机制

- `require_permission(permission: str)` 依赖工厂
- 超级用户 (`is_superuser=True`) 绕过所有权限检查
- 权限标识符格式：`module:action`（如 `user:create`、`role:update`）

## 预置权限（34 个）

**菜单权限**：`dashboard:view`, `model:view`, `skill:view`, `tool:view`, `setting:view`, `setting:user`, `setting:role`, `setting:permission`, `setting:menu`, `setting:config`, `setting:operation-log`, `setting:login-log`

**按钮权限**：`user:create/update/delete/status`, `role:create/update/delete/status/assign-permission`, `permission:create/update/delete/status`, `menu:create/update/delete/status`, `config:create/update/delete`

**API 权限**：`operation-log:read`, `login-log:read`

## 预置角色

| 角色 | Code | 说明 |
|------|------|------|
| 超级管理员 | admin | 拥有全部权限 |
| 编辑 | editor | 部分权限 |
| 访客 | viewer | 只读权限 |

## 前端权限控制

- 路由守卫：检查 `userStore.menus` 控制菜单可见性
- 按钮级：`userStore.hasPermission()` 控制操作按钮显隐
- `/setting/*` 路由访问时检查菜单权限，无权限重定向到首个可访问菜单
