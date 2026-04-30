## [2026-04-30 17:00] ingest | UI 规范 + 路由守卫修复 + 后端 session 修复
- 创建概念页：[[concepts/ui-global-conventions]]（标题蓝色矩形装饰、表单按钮右对齐、中文化要求）
- 更新概念页：[[concepts/frontend-architecture]]（路由守卫改为 async，刷新时先加载用户信息再判断权限）
- 修复前端：路由守卫异步加载用户信息，解决刷新非仪表盘页面跳转到仪表盘的问题
- 修复后端：change_password 接口 session.add → session.merge，解决双 session 冲突
- 来源：style.css, router/index.ts, App.vue, backend/app/api/routes/auth.py

## [2026-04-30 16:00] ingest | 全项目扫描更新
- 更新总览：[[overview]]（补充已完成/待完成状态）
- 更新概念页：[[concepts/backend-architecture]]（完整分层结构、8 路由模块、9 服务、API 端点总览）
- 更新概念页：[[concepts/frontend-architecture]]（12 页面、14 路由、11 API 模块、布局结构、Mock 状态）
- 更新概念页：[[concepts/data-model]]（新增 OperationLog/LoginLog/SystemConfig 模型）
- 更新概念页：[[concepts/rbac]]（认证机制、授权机制、34 个预置权限、前端权限控制）
- 更新概念页：[[concepts/tech-stack]]（补充版本号、ECharts、开发环境配置）
- 更新索引：[[index]]（更新描述信息）
- 来源：全项目源码扫描

## [2026-04-30 14:00] ingest | 表格布局规范
- 创建概念页：[[concepts/table-layout-convention]]
- 更新概念页：[[concepts/frontend-architecture]]（添加 useTableScrollY、表格布局引用）
- 更新 CLAUDE.md：新增「前端编码规范 > 表格页面布局规范」章节
- 修复内容：style.css 补全 .ant-table-container flex 链路，.ant-table-body 添加 flex: 1
- 来源：style.css, useTableScrollY.ts, Chrome DevTools 实测

## [2026-04-29 初始化] ingest | 项目代码库
- 创建总览：[[overview]]
- 创建概念页：[[concepts/tech-stack]], [[concepts/backend-architecture]], [[concepts/frontend-architecture]], [[concepts/rbac]], [[concepts/data-model]]
- 创建实体页：[[entities/postgresql]], [[entities/redis]], [[entities/minio]]
- 来源：README.md, CLAUDE.md, docker-compose.yml, backend/app/**, frontend/src/**
