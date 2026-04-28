# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概览

这是一个前后端分离的双目录仓库，没有根级别的 workspace 或统一任务入口：

- `backend/`: 独立的 Python/FastAPI 服务，使用 `uv` 管理依赖。
- `frontend/`: 独立的 Vue 3 + TypeScript + Vite 单页应用，使用 `pnpm` 管理依赖。

前后端当前是并列初始化状态，而不是已经打通的全栈应用：仓库里还没有前端请求后端的代码，也没有 Vite 代理配置。

## 常用命令

### Backend (`/backend`)

```bash
uv sync
uv run fastapi dev main.py
```

- 安装/同步依赖: `uv sync`
- 启动开发服务器: `uv run fastapi dev main.py`

当前 `backend/pyproject.toml` 没有配置测试、lint 或额外脚本；仓库里也没有后端测试文件，因此现在没有可运行的单测命令。

### Frontend (`/frontend`)

```bash
pnpm install
pnpm dev
pnpm build
pnpm preview
```

- 安装依赖: `pnpm install`
- 启动开发服务器: `pnpm dev`
- 生产构建: `pnpm build`
- 本地预览构建产物: `pnpm preview`

当前 `frontend/package.json` 没有 `test` 或 `lint` script，因此现在没有前端测试或 lint 命令，也没有单独运行单测的入口。

## 高层架构

### Backend 架构

后端目前是一个极简 FastAPI 应用，所有服务端逻辑都在 `backend/main.py`：

- 在模块顶层创建 `app = FastAPI()`。
- 直接在同一文件中声明路由。
- 当前仅有两个接口：`GET /` 和 `GET /items/{item_id}`。

这说明后端还没有拆分为 `routers/`、`services/`、`models/` 之类的层次；后续新增服务端能力时，默认入口就是 `backend/main.py`，除非先进行结构化拆分。

### Frontend 架构

前端是标准的 Vite 启动结构：

- `frontend/src/main.ts` 是浏览器入口，负责创建 Vue 应用并挂载到 `#app`。
- `frontend/src/App.vue` 是根组件，目前只负责渲染 `HelloWorld`。
- `frontend/src/components/HelloWorld.vue` 承载当前页面主体，是模板示例界面。
- `frontend/src/style.css` 存放全局样式，控制整体页面布局与主题变量。

当前前端仍接近脚手架默认模板，没有状态管理、路由、API 层或业务模块分层。

### 资源与构建边界

- `frontend/public/` 中的文件会按 Vite 规则原样对外提供。
- `frontend/src/assets/` 中的资源会被前端构建流程打包处理。
- TypeScript 配置拆成两层：
  - `frontend/tsconfig.app.json` 用于浏览器端源码与 `.vue` 文件。
  - `frontend/tsconfig.node.json` 用于 `vite.config.ts` 这类 Node 侧配置文件。

## 当前代码状态的实际含义

这是一个刚初始化的仓库：

- 后端是单文件 FastAPI 原型。
- 前端是 Vue/Vite 默认模板页面。
- 没有根级别统一命令。
- 没有测试、lint、CI 或前后端联调配置。

未来实例在修改代码时，应优先把前后端视为两个独立应用分别操作，而不是假设仓库已经存在共享构建链路或统一开发脚本。
