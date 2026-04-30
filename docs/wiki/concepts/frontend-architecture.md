---
title: 前端架构
type: concept
created: 2026-04-29
updated: 2026-04-30
sources: [frontend-src-structure, router-index, stores, api-layer, views]
tags: [frontend, architecture]
related: [[overview]], [[concepts/tech-stack]], [[concepts/rbac]], [[concepts/table-layout-convention]], [[concepts/ui-global-conventions]]
---

# 前端架构

## 目录结构

```
frontend/src/
├── api/            # API 请求层 (11 个文件)
│   ├── request.ts  # Axios 实例 (baseURL=/api, 超时 10s, token 拦截)
│   ├── user.ts     # 认证 + 用户管理 (9 个接口)
│   ├── role.ts     # 角色管理 (7 个接口)
│   ├── permission.ts # 权限管理 (5 个接口)
│   ├── menu.ts     # 菜单管理 (5 个接口)
│   ├── config.ts   # 系统配置 (4 个接口)
│   ├── log.ts      # 日志查询 (2 个接口)
│   ├── dashboard.ts # 仪表盘 (Mock 数据)
│   ├── model.ts    # 模型管理 (Mock 数据)
│   ├── skill.ts    # Skills 管理 (Mock 数据)
│   └── tool.ts     # 工具管理 (Mock 数据)
├── composables/    # 组合式函数
│   ├── useDrawerWidth.ts  # 响应式抽屉宽度 (<=768:100%, <=1200:50%, >1200:520px)
│   └── useTableScrollY.ts # 表格滚动高度 (ResizeObserver)
├── components/     # 公共组件
│   ├── TabBar.vue  # 多标签页栏 (右键菜单管理)
│   └── ForcePasswordChangeModal.vue # 强制改密弹窗
├── layouts/
│   └── BasicLayout.vue # 主布局 (侧边栏+标签页+KeepAlive)
├── router/
│   └── index.ts    # 路由配置 (14 条路由 + 守卫)
├── stores/         # Pinia 状态管理
│   ├── user.ts     # 用户状态 (token/roles/permissions/menus)
│   ├── app.ts      # 应用状态 (侧边栏折叠/主题色)
│   └── tab.ts      # 标签页状态 (打开/关闭/缓存)
└── views/          # 页面视图 (12 个页面)
    ├── login/      # 登录页
    ├── dashboard/  # 仪表盘 (统计卡片 + ECharts 趋势图)
    ├── model/      # 模型管理 (Mock)
    ├── skill/      # Skills 管理 (Mock)
    ├── tool/       # 工具管理 (Mock)
    └── setting/    # 系统设置
        ├── user/           # 用户管理
        ├── role/           # 角色管理 + 权限分配
        ├── permission/     # 权限管理
        ├── menu/           # 菜单配置 (树形)
        ├── config/         # 系统配置
        ├── operation-log/  # 操作日志
        └── login-log/      # 登录日志
```

## 路由结构

| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录页 | 无 |
| `/dashboard` | 仪表盘 | 需认证 |
| `/model` | 模型管理 | 需认证 |
| `/skill` | Skills 管理 | 需认证 |
| `/tool` | 工具管理 | 需认证 |
| `/setting/user` | 用户管理 | 需认证 + 菜单权限 |
| `/setting/role` | 角色管理 | 需认证 + 菜单权限 |
| `/setting/permission` | 权限管理 | 需认证 + 菜单权限 |
| `/setting/menu` | 菜单配置 | 需认证 + 菜单权限 |
| `/setting/config` | 系统配置 | 需认证 + 菜单权限 |
| `/setting/operation-log` | 操作日志 | 需认证 + 菜单权限 |
| `/setting/login-log` | 登录日志 | 需认证 + 菜单权限 |

## 认证守卫

路由守卫为 `async beforeEach`，在导航前确保用户信息已加载：

1. 无 token 且非登录页 → 重定向到 `/login`
2. 有 token 且在登录页 → 重定向到 `/dashboard`
3. 有 token 但 `userInfo` 为空（页面刷新场景）→ 异步调用 `getUserInfoApi()` 加载用户信息，失败则清除 token 跳转登录
4. 访问 `/setting/*` 时检查菜单权限，无权限重定向到首个可访问菜单

用户信息加载在路由守卫中完成（而非 App.vue onMounted），确保刷新任意页面时 menus 数据在权限判断前就绪。

## 布局结构

```
┌─────────────────────────────────────────────┐
│  Sidebar (220px)  │  Header (64px)          │
│  - Logo           │  - Menu Toggle          │
│  - Menu Tree      │  - User Dropdown        │
│  - Dark Theme     │  - Logout               │
├─────────────────────────────────────────────┤
│  TabBar (标签页栏，支持右键菜单)            │
├─────────────────────────────────────────────┤
│  KeepAlive + RouterView (页面内容)          │
└─────────────────────────────────────────────┘
```

## API 层状态

- **已对接后端**：user, role, permission, menu, config, log（系统设置全部模块）
- **本地 Mock**：model, skill, tool, dashboard（业务模块尚未对接）

## 表格页面布局

所有管理页面的表格统一使用 `.page-container` + `.page-table-section` 布局模式，配合 `useTableScrollY` 组合式函数实现自适应滚动。详见 [[concepts/table-layout-convention]]。
