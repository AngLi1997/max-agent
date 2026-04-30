---
title: 项目总览
type: concept
created: 2026-04-29
updated: 2026-04-30
sources: [readme, claude-md, docker-compose, backend-app, frontend-src]
tags: [overview, architecture]
related: [[concepts/tech-stack]], [[concepts/rbac]], [[concepts/backend-architecture]], [[concepts/frontend-architecture]]
---

# max-agent 项目总览

max-agent 是一个智能体管理平台，面向智能体对话、配置管理与后台运营场景。

## 核心能力

- **智能体管理**：模型、技能（Skill）、工具（Tool）的配置与生命周期管理（前端 Mock，待对接后端）
- **RBAC 权限体系**：用户 → 角色 → 权限的三层访问控制，34 个预置权限，3 个预置角色
- **后台运营**：仪表盘、菜单配置、系统配置、操作日志、登录日志
- **基础设施**：PostgreSQL + pgvector、Redis、MinIO 提供数据存储、缓存与文件管理

## 架构模式

前后端分离：
- **前端**：Vue 3 + TypeScript + Vite + Ant Design Vue + Pinia + ECharts
- **后端**：FastAPI + SQLAlchemy + Pydantic + fastapi-users + Redis
- 通过 HTTP API 交互，Vite 开发代理转发 `/api` 请求

## 当前状态

### 已完成
- 后端分层架构（api/services/models/schemas/db），8 个路由模块，9 个服务，7 个数据模型
- 前端 12 个页面，14 条路由，11 个 API 模块，3 个 Pinia store
- 完整的 RBAC 权限体系（前后端联调完成）
- 系统设置全部模块已对接后端（用户/角色/权限/菜单/配置/日志）
- 认证体系（登录/登出/改密/强制改密）
- 审计日志（操作日志 + 登录日志）
- 多标签页浏览 + KeepAlive 缓存
- 表格自适应滚动布局
- 后端测试套件（9 个测试文件）

### 待完成
- 模型/Skills/工具管理后端 API（前端已有 Mock 页面）
- 仪表盘数据后端 API
- MinIO 文件管理集成
- CI/CD 配置
