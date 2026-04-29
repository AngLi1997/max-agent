# 后台管理系统前端设计文档

## 概述

基于 Ant Design Vue 4.x 开发的后台管理系统前端，采用浅色企业风视觉风格、侧边栏导航布局。包含登录页和六个业务模块：仪表盘、用户管理、模型管理、Skills 管理、工具管理、系统设置。

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
│   ├── user/         # 用户管理
│   ├── model/        # 模型管理
│   ├── skill/        # Skills 管理
│   ├── tool/         # 工具管理
│   └── setting/      # 系统设置
├── App.vue
├── main.ts
└── style.css         # 全局基础样式（极简）
```

## 布局设计

### BasicLayout

采用 antd 的 `a-layout` 组件组合：

- **左侧 `a-layout-sider`**：可折叠侧边栏，展开宽度 220px，折叠后 80px。包含产品 logo 和垂直菜单。
- **顶部 `a-layout-header`**：右侧放用户头像下拉菜单（个人信息、退出登录）。
- **中间 `a-layout-content`**：带面包屑导航 + 页面内容区，内容区有内边距。

### 侧边栏菜单

一级菜单，不做嵌套子菜单：

| 菜单项 | 路由 | 图标 |
|--------|------|------|
| 仪表盘 | /dashboard | DashboardOutlined |
| 用户管理 | /user | UserOutlined |
| 模型管理 | /model | RobotOutlined |
| Skills 管理 | /skill | ThunderboltOutlined |
| 工具管理 | /tool | ToolOutlined |
| 系统设置 | /setting | SettingOutlined |

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

### 用户管理 /user

- 搜索栏：用户名关键词搜索 + 状态筛选
- 操作按钮：新增用户
- 表格列：用户名、邮箱、角色、状态（标签）、创建时间、操作（编辑/删除）
- 新增/编辑：抽屉表单（`a-drawer` + `a-form`）

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

### 系统设置 /setting

- Tab 页形式（`a-tabs`）：
  - 基础配置：站点名称、站点描述等表单
  - 通知配置：通知开关、通知渠道等表单

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
