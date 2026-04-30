---
title: 后端架构
type: concept
created: 2026-04-29
updated: 2026-04-30
sources: [backend-app-structure]
tags: [backend, architecture]
related: [[overview]], [[concepts/tech-stack]], [[concepts/rbac]], [[concepts/data-model]]
---

# 后端架构

## 分层结构

```
backend/
├── main.py                 # FastAPI 应用入口 (lifespan 管理启动/关闭)
├── alembic/                # 数据库迁移
│   └── versions/           # 迁移脚本
├── app/
│   ├── api/                # 路由层
│   │   ├── router.py       # 路由注册中心 (8 个子路由器)
│   │   └── routes/         # 各模块路由
│   │       ├── auth.py     # 认证 (login/logout/me/change-password)
│   │       ├── users.py    # 用户 CRUD + 状态管理
│   │       ├── roles.py    # 角色 CRUD + 权限分配
│   │       ├── permissions.py # 权限 CRUD
│   │       ├── menus.py    # 菜单 CRUD (树形)
│   │       ├── configs.py  # 系统配置 CRUD
│   │       ├── logs.py     # 操作日志 + 登录日志查询
│   │       └── health.py   # 健康检查
│   ├── auth/               # 认证模块
│   ├── core/               # 核心配置
│   │   ├── config.py       # Settings (pydantic-settings, .env)
│   │   └── redis.py        # Redis 连接
│   ├── db/                 # 数据库层
│   │   ├── base.py         # SQLAlchemy Base
│   │   ├── session.py      # AsyncSession 工厂
│   │   ├── mixins.py       # TimestampMixin
│   │   ├── seed.py         # 数据初始化 (角色/权限/用户/菜单/配置)
│   │   └── user.py         # 用户数据访问
│   ├── models/             # SQLAlchemy ORM 模型 (7 个)
│   │   ├── user.py         # User (继承 fastapi-users)
│   │   ├── role.py         # Role + user_roles/role_permissions 关联表
│   │   ├── permission.py   # Permission
│   │   ├── menu.py         # Menu (树形自引用)
│   │   ├── system_config.py # SystemConfig
│   │   ├── operation_log.py # OperationLog
│   │   └── login_log.py    # LoginLog
│   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── auth.py, user.py, role.py, permission.py
│   │   ├── menu.py, system_config.py, log.py
│   │   └── common.py       # ListResponse[T] 泛型
│   └── services/           # 业务逻辑层 (9 个服务)
│       ├── auth.py          # 认证 (SlidingRedisStrategy)
│       ├── authorization.py # 权限检查依赖
│       ├── rbac.py          # RBAC 聚合 (权限收集 + 菜单树构建)
│       ├── audit.py         # 审计日志 (操作日志 + 登录日志)
│       ├── system_users.py  # 用户管理业务逻辑
│       ├── system_roles.py  # 角色管理业务逻辑
│       ├── system_menus.py  # 菜单管理业务逻辑
│       ├── system_permissions.py # 权限管理业务逻辑
│       └── system_configs.py # 系统配置业务逻辑
└── tests/                  # 测试套件 (9 个测试文件)
```

## 关键设计

- **异步优先**：asyncpg + AsyncSession，全链路异步
- **配置管理**：pydantic-settings 从 `.env` 加载，`@lru_cache` 单例
- **认证**：fastapi-users + Bearer Token，Redis 滑动窗口策略（每次读取刷新 TTL，默认 30 分钟）
- **授权**：`require_permission()` 依赖工厂，超级用户绕过检查
- **审计**：所有写操作自动记录操作日志，登录/登出记录登录日志
- **数据库迁移**：Alembic 管理 schema 变更（2 个迁移版本）
- **API 前缀**：统一 `/api` 前缀
- **CORS**：允许 localhost:5173 和 127.0.0.1:5173
- **Seed 数据**：预置 admin 用户、3 个角色、34 个权限、12 个菜单、3 个系统配置

## API 端点总览

| 模块 | 前缀 | 端点数 | 说明 |
|------|------|--------|------|
| auth | `/auth` | 4 | 登录/登出/用户信息/改密 |
| users | `/users` | 5 | 用户 CRUD + 状态 |
| roles | `/roles` | 7 | 角色 CRUD + 状态 + 权限分配 |
| permissions | `/permissions` | 5 | 权限 CRUD + 状态 |
| menus | `/menus` | 5 | 菜单 CRUD (树形) + 状态 |
| configs | `/configs` | 4 | 系统配置 CRUD |
| logs | `/` | 2 | 操作日志 + 登录日志查询 |
| health | `/health` | 1 | 健康检查 |
