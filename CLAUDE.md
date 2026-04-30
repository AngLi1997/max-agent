# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概览

这是一个前后端分离的双目录仓库，没有根级别的 workspace 或统一任务入口：

- `backend/`: 独立的 Python/FastAPI 服务，使用 `uv` 管理依赖，采用 Pydantic 做数据校验，并使用 Uvicorn 作为启动服务器。
- `frontend/`: 独立的 Vue 3 + TypeScript + Vite 单页应用，使用 `pnpm` 管理依赖。

前后端当前是并列初始化状态，而不是已经打通的全栈应用：仓库里还没有前端请求后端的代码，也没有 Vite 代理配置。

## 常用命令

### 基础设施 (Docker Compose)

```bash
docker compose up -d
docker compose down
docker compose ps
```

- 启动基础设施: `docker compose up -d`（PostgreSQL + pgvector、Redis、MinIO）
- 停止基础设施: `docker compose down`
- 查看服务状态: `docker compose ps`

服务端口：PostgreSQL 5432、Redis 6379、MinIO API 9000 / 控制台 9001。

### Backend (`/backend`)

```bash
uv sync
uv run uvicorn main:app --reload
```

- 安装/同步依赖: `uv sync`
- 启动开发服务器: `uv run uvicorn main:app --reload`

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
- 使用 Pydantic 作为 FastAPI 请求/响应模型的数据校验基础。
- 通过 Uvicorn 运行 ASGI 应用。
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

## 前端编码规范

### 表格页面布局规范

所有包含 Ant Design Table 的页面必须遵循以下统一布局模式：

**HTML 结构：**

```html
<div class="page-container">
  <!-- 搜索栏区域 -->
  <div class="page-section">
    <div class="page-toolbar">...</div>
  </div>
  <!-- 表格区域 -->
  <div :ref="tableScroll.tableSectionRef" class="page-section page-table-section">
    <a-table :scroll="{ y: tableScroll.tableScrollY }" .../>
  </div>
</div>
```

**必须使用 `useTableScrollY` 组合式函数：**

```ts
import { useTableScrollY } from '@/composables/useTableScrollY'
const tableScroll = useTableScrollY()
```

- `:ref="tableScroll.tableSectionRef"` 绑定到 `.page-table-section` 容器
- `:scroll="{ y: tableScroll.tableScrollY }"` 传给 `<a-table>`
- 数据加载完成后调用 `tableScroll.updateTableScrollY()`

**CSS flex 链路（`style.css` 已全局定义，不要在页面中重复声明）：**

从 `.page-table-section` 到 `.ant-table-body` 的完整 flex 链必须保持连续：

```
.page-table-section        → flex: 1; min-height: 0; overflow: hidden
  .ant-table-wrapper        → flex: 1; min-height: 0; display: flex; flex-direction: column
    .ant-spin-nested-loading → (同上)
      .ant-spin-container    → (同上)
        .ant-table           → (同上)
          .ant-table-container → (同上)  ← 不可遗漏
            .ant-table-header  → 自然高度
            .ant-table-body    → flex: 1; min-height: 0; overflow-y: auto
        .ant-pagination      → flex-shrink: 0
```

关键点：Ant Design Vue 4.x 在 `.ant-table` 和 header/body 之间有 `.ant-table-container` 层，flex 链路中不可遗漏此层，否则表格内容会溢出屏幕。

### Drawer / Modal UI 规范

**标题蓝色矩形装饰：** 全局 CSS 已为所有 `a-drawer` 和 `a-modal` 标题自动添加蓝色矩形装饰（`::before` 伪元素），无需在组件中手动添加。

**表单按钮右对齐：** 全局 CSS 已将 Drawer/Modal 内表单最后一个 `a-form-item` 的内容区域设为 `flex + justify-content: flex-end`，按钮自动右对齐，无需在组件中单独设置。

**中文化要求：**
- 所有 placeholder 使用中文（"请输入…"、"请选择…"）
- 确认/取消按钮使用中文（"确认"、"取消"）
- 提示信息、校验消息均使用中文

## 当前代码状态的实际含义

这是一个刚初始化的仓库：

- 后端是单文件 FastAPI 原型。
- 前端是 Vue/Vite 默认模板页面。
- 没有根级别统一命令。
- 没有测试、lint、CI 或前后端联调配置。

未来实例在修改代码时，应优先把前后端视为两个独立应用分别操作，而不是假设仓库已经存在共享构建链路或统一开发脚本。
