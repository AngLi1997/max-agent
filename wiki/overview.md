---
title: 项目总览
type: concept
created: 2026-04-29
updated: 2026-04-29
sources: [readme, claude-md, docker-compose]
tags: [overview, architecture]
related: [[concepts/tech-stack]], [[concepts/rbac]], [[concepts/backend-architecture]], [[concepts/frontend-architecture]]
---

# max-agent 项目总览

max-agent 是一个智能体管理平台，面向智能体对话、配置管理与后台运营场景。

## 核心能力

- **智能体管理**：模型、技能（Skill）、工具（Tool）的配置与生命周期管理
- **RBAC 权限体系**：用户 → 角色 → 权限的三层访问控制
- **后台运营**：仪表盘、菜单配置、系统配置、操作日志、登录日志
- **基础设施**：PostgreSQL + pgvector、Redis、MinIO 提供数据存储、缓存与文件管理

## 架构模式

前后端分离：
- **前端**：Vue 3 + TypeScript + Vite + Ant Design Vue
- **后端**：FastAPI + SQLAlchemy + Pydantic
- 通过 HTTP API 交互，Vite 开发代理转发 `/api` 请求

## 当前状态

后端已完成分层架构拆分（api/services/models/schemas/db），前端已实现路由、状态管理、API 层和多个业务页面。基础设施通过 Docker Compose 编排。
