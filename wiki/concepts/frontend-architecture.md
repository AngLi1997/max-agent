---
title: 前端架构
type: concept
created: 2026-04-29
updated: 2026-04-29
sources: [frontend-src-structure, router-index]
tags: [frontend, architecture]
related: [[overview]], [[concepts/tech-stack]], [[concepts/rbac]]
---

# 前端架构

## 目录结构

```
frontend/src/
├── api/            # API 请求层 (Axios 封装)
│   ├── request.ts  # Axios 实例与拦截器
│   ├── user.ts, role.ts, permission.ts, menu.ts
│   ├── model.ts, skill.ts, tool.ts
│   ├── config.ts, log.ts, dashboard.ts
├── composables/    # 组合式函数
│   └── useDrawerWidth.ts
├── components/     # 公共组件
│   └── TabBar.vue
├── layouts/        # 布局组件
│   └── BasicLayout.vue
├── router/         # Vue Router 配置
├── stores/         # Pinia 状态管理
│   ├── user.ts     # 用户/认证状态
│   ├── app.ts      # 应用全局状态
│   └── tab.ts      # 标签页状态
└── views/          # 页面视图
    ├── login/      # 登录页
    ├── dashboard/  # 仪表盘
    ├── model/      # 模型管理
    ├── skill/      # 技能管理
    ├── tool/       # 工具管理
    └── setting/    # 系统设置 (user, role, permission, menu, config, logs)
```

## 路由结构

- `/login` — 登录页（未认证时重定向至此）
- `/dashboard` — 仪表盘（默认首页）
- `/model` — 模型管理
- `/skill` — Skills 管理
- `/tool` — 工具管理
- `/setting/*` — 系统设置子模块

## 认证守卫

路由守卫检查 `userStore.token`：
- 无 token 且非登录页 → 重定向到 `/login`
- 有 token 且在登录页 → 重定向到 `/dashboard`
