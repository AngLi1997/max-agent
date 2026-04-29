# 后台管理系统前端设计文档

## 概述

基于 Ant Design Vue 4.x 开发的后台管理系统前端，采用浅色企业风视觉风格、侧边栏导航布局。包含登录页，以及仪表盘、模型管理、Skills 管理、工具管理和系统设置五个一级模块；其中系统设置下包含用户管理、角色管理、权限管理、菜单配置、系统配置、操作日志、登录日志等二级功能页面。

## 技术栈

| 层面 | 选型 |
|------|------|
| UI 框架 | ant-design-vue 4.x |
| 路由 | vue-router 4 |
| 状态管理 | Pinia |
| 图表 | echarts + vue-echarts |
| HTTP | axios |
| 构建 | Vite + TypeScript（沿用现有配置） |

## 目录结构

```
frontend/src/
├── api/              # axios 实例 + 各模块 API 函数
├── assets/           # 静态资源（logo 等）
├── components/       # 通用业务组件
├── layouts/
│   └── BasicLayout.vue   # 侧边栏 + 顶栏 + 内容区
├── router/
│   └── index.ts      # 路由定义 + 导航守卫
├── stores/
│   ├── user.ts       # 用户登录态、token
│   └── app.ts        # 侧边栏折叠等 UI 状态
├── views/
│   ├── login/        # 登录页
│   ├── dashboard/    # 仪表盘
│   ├── model/        # 模型管理
│   ├── skill/        # Skills 管理
│   ├── tool/         # 工具管理
│   └── setting/
│       ├── user/     # 用户管理
│       ├── role/     # 角色管理
│       ├── permission/ # 权限管理
│       ├── menu/     # 菜单配置
│       ├── config/   # 系统配置
│       ├── operation-log/ # 操作日志
│       └── login-log/ # 登录日志
├── App.vue
├── main.ts
└── style.css         # 全局基础样式（极简）
```

## 布局设计

### BasicLayout

采用 antd 的 `a-layout` 组件组合：

- **左侧 `a-layout-sider`**：可折叠侧边栏，展开宽度 220px，折叠后 80px。包含产品 logo 和垂直菜单。
- **顶部 `a-layout-header`**：左侧展示品牌名 **Max-Agent**，右侧放用户头像下拉菜单（个人信息、退出登录）。
- **中间 `a-layout-content`**：带面包屑导航 + 页面内容区，内容区有内边距。

### 侧边栏菜单

一级菜单 + 系统设置下展开二级菜单：

| 层级 | 菜单项 | 路由 | 图标 |
|------|--------|------|------|
| 一级 | 仪表盘 | /dashboard | DashboardOutlined |
| 一级 | 模型管理 | /model | RobotOutlined |
| 一级 | Skills 管理 | /skill | ThunderboltOutlined |
| 一级 | 工具管理 | /tool | ToolOutlined |
| 一级 | 系统设置 | — | SettingOutlined |
| 二级 | 用户管理 | /setting/user | UserOutlined |
| 二级 | 角色管理 | /setting/role | TeamOutlined |
| 二级 | 权限管理 | /setting/permission | SafetyCertificateOutlined |
| 二级 | 菜单配置 | /setting/menu | MenuOutlined |
| 二级 | 系统配置 | /setting/config | ControlOutlined |
| 二级 | 操作日志 | /setting/operation-log | FileTextOutlined |
| 二级 | 登录日志 | /setting/login-log | LoginOutlined |

## 登录页

居中卡片布局：

- 页面垂直水平居中，浅灰背景（#f0f2f5）
- 卡片宽度 400px，圆角 8px，带阴影
- 卡片内容：产品 logo + 标题、用户名输入框、密码输入框、"记住我" 复选框、登录按钮
- 使用 antd `a-form` 做表单校验（用户名和密码非空）
- 登录成功后将 token 存入 localStorage，跳转 `/dashboard`
- 未登录访问其他页面时，路由守卫重定向到 `/login`

## 各模块页面

### 仪表盘 /dashboard

- 顶部 4 个统计卡片（`a-card` + `a-statistic`）：用户数、模型数、Skills 数、工具数
- 下方趋势折线图（echarts via vue-echarts），展示近 7 天数据趋势

### 模型管理 /model

- 搜索栏：模型名称搜索 + 提供商筛选
- 操作按钮：新增模型
- 表格列：模型名称、提供商、状态、创建时间、操作
- 新增/编辑：抽屉表单

### Skills 管理 /skill

- 搜索栏：名称搜索 + 状态筛选
- 操作按钮：新增 Skill
- 表格列：名称、描述、状态、创建时间、操作
- 新增/编辑：抽屉表单

### 工具管理 /tool

- 搜索栏：名称搜索 + 类型筛选
- 操作按钮：新增工具
- 表格列：名称、类型、状态、创建时间、操作
- 新增/编辑：抽屉表单

### 系统设置

#### 用户管理 /setting/user

- 搜索栏：用户名关键词搜索 + 状态筛选
- 操作按钮：新增用户
- 表格列：用户名、邮箱、角色、状态（标签）、创建时间、操作（编辑/删除）
- 新增/编辑：抽屉表单（`a-drawer` + `a-form`）

#### 角色管理 /setting/role

- 搜索栏：角色名称搜索 + 状态筛选
- 操作按钮：新增角色
- 表格列：角色名称、角色编码、描述、状态、操作（编辑/删除/分配权限）
- 新增/编辑：抽屉表单
- 分配权限：弹窗中展示权限树（`a-tree` 带勾选）

#### 权限管理 /setting/permission

- 搜索栏：权限名称搜索 + 类型筛选
- 操作按钮：新增权限
- 表格列：权限名称、权限标识、类型、状态、操作（编辑/删除）
- 新增/编辑：抽屉表单

#### 菜单配置 /setting/menu

- 树形表格（`a-table` 带 `childrenColumnName`）
- 表格列：菜单名称、路由、权限标识、排序、状态、操作（编辑/删除/新增子菜单）
- 新增/编辑：抽屉表单，包含父菜单选择（树形下拉）

#### 系统配置 /setting/config

- 搜索栏：按 key 搜索
- 操作按钮：新增配置项
- 表格列：配置项名称、key、value、描述、操作（编辑/删除）
- 新增/编辑：抽屉表单

#### 操作日志 /setting/operation-log

- 搜索栏：操作人搜索 + 模块筛选 + 时间范围
- 表格列：操作人、模块、操作类型、请求方法、结果、时间、操作（查看详情）
- 只读，不提供编辑/删除

#### 登录日志 /setting/login-log

- 搜索栏：用户名搜索 + 登录结果筛选 + 时间范围
- 表格列：用户名、登录 IP、登录地点、设备/浏览器、登录结果、登录时间、操作（查看详情）
- 只读，不提供编辑/删除

### 系统设置 /setting（原 Tab 页）

已拆分为上述独立子页面，不再使用 Tab 页形式。

## 登录态与路由守卫

- Pinia `userStore` 管理 token 和用户信息
- `router.beforeEach`：无 token 且目标非 `/login` → 重定向登录页；有 token 访问 `/login` → 重定向仪表盘
- axios 请求拦截器自动附加 `Authorization: Bearer <token>`
- 401 响应时清除 token 并跳转登录页
- 当前不做角色权限控制，所有登录用户可访问全部页面

## 视觉风格

- 浅色企业风：使用 antd 默认浅色主题
- 主色调：antd 默认蓝色（#1677ff）
- 侧边栏：深色模式（`theme="dark"`），与浅色内容区形成对比
- 全局字体：沿用 antd 默认字体栈

## 不在本期范围

- 角色与权限控制
- 国际化 i18n
- 暗色模式切换
- 前后端联调（后端 API 尚未就绪，前端使用 mock 数据）
- 单元测试 / E2E 测试
