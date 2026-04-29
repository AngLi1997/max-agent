# max-agent

max-agent 是一个智能体管理平台，面向智能体对话、配置管理与后台运营场景。

## 项目定位

平台分为两个主要部分：

- `frontend/`: 基于 Vite + Vue 构建的智能体对话门户，同时承载基于 Ant Design Vue 的后台管理页面。
- `backend/`: 基于 FastAPI 的服务端，负责认证、智能体管理、对话编排、文件管理与数据访问。

## 技术选型

### 前端

- Vite
- Vue 3
- TypeScript
- Ant Design Vue

前端承担两类界面能力：

- 面向终端用户的智能体对话门户
- 面向运营与管理人员的后台管理系统

### 后端

- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- pgvector
- Uvicorn

后端负责：

- 智能体配置与生命周期管理
- 会话、消息与上下文管理
- 基于 PostgreSQL 的业务数据持久化
- 基于 pgvector 的向量检索能力

### 基础设施

- Redis: 缓存、会话态辅助存储、令牌状态管理
- JWT + Redis: 认证与登录态控制
- MinIO: 文件上传、对象存储与静态资源管理

## 架构说明

整个仓库采用前后端分离结构：

- `frontend/` 是独立的 Web 应用工程
- `backend/` 是独立的 API 服务工程
- 前端通过 HTTP API 与后端交互
- 后端统一访问 PostgreSQL、Redis 和 MinIO 等基础设施

从职责划分上看：

- Vue 前端负责用户交互、对话展示、配置编辑与后台操作入口
- FastAPI 后端负责业务编排、认证鉴权、数据访问与外部服务集成
- Pydantic 用于请求与响应模型定义及数据校验
- PostgreSQL 存储核心业务数据
- pgvector 为知识检索、语义搜索或智能体记忆提供向量能力
- Redis 用于热点数据缓存、登录态约束与短时状态管理
- MinIO 用于文件与对象资源存储

## 目录结构

```text
.
├── backend/   # FastAPI 服务
├── frontend/  # Vite + Vue 前端应用
└── CLAUDE.md  # 面向 Claude Code 的仓库协作说明
```

## 开发命令

### 基础设施

```bash
docker compose up -d
```

- `docker compose up -d`: 启动 PostgreSQL (pgvector)、Redis、MinIO 基础设施服务
- `docker compose down`: 停止所有基础设施服务
- `docker compose ps`: 查看服务运行状态

服务端口：
- PostgreSQL: 5432
- Redis: 6379
- MinIO API: 9000 / 控制台: 9001

### 后端

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

- `uv sync`: 安装并同步 Python 依赖
- `uv run uvicorn main:app --reload`: 使用 Uvicorn 启动 FastAPI 开发服务

### 前端

```bash
cd frontend
pnpm install
pnpm dev
pnpm build
pnpm preview
```

- `pnpm install`: 安装前端依赖
- `pnpm dev`: 启动前端开发服务
- `pnpm build`: 构建生产产物
- `pnpm preview`: 本地预览构建结果

## 当前仓库状态

当前仓库已经具备前后端基础工程目录：

- 前端目录为 Vite + Vue 工程基础结构
- 后端目录为 FastAPI 工程基础结构

其余技术选型包括 SQLAlchemy、PostgreSQL、pgvector、Redis、JWT、MinIO 代表该平台的目标后端能力边界，可作为后续功能实现与模块拆分的基础。
