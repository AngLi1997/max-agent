# 系统设置 RBAC 与后端联调设计文档

## 概述

本期目标是将后台管理中的“系统设置”模块从前端本地 mock 状态升级为真实可用的 RBAC 基础层，完成后端接口开发、数据库落地、初始化数据、真实日志记录和前端联调。

本次范围覆盖：
- 用户管理
- 角色管理
- 权限管理
- 菜单配置
- 系统配置
- 登录日志
- 操作日志
- 登录后基于角色与权限返回菜单树和权限集合
- 前端基于权限控制系统设置模块的菜单与核心操作按钮显隐

本次不覆盖模型管理、Skills 管理、工具管理的真实后端接口，也不做细粒度数据权限和复杂审计导出。

## 当前状态

### 后端现状

当前后端已经具备：
- FastAPI 应用入口与 CORS 配置
- Redis token 登录态
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/health`
- SQLAlchemy 模型：`user`、`role`、`permission`、`menu`
- 多对多关系：`user_roles`、`role_permissions`
- Alembic 初始迁移

当前后端尚未具备：
- 用户、角色、权限、菜单、配置的 CRUD 接口
- 角色分配权限接口
- 多角色用户查询与写入接口
- 登录日志、操作日志表与查询接口
- 初始化系统配置表
- 基于权限聚合返回可见菜单树的能力

### 前端现状

当前前端已经具备系统设置页面骨架和交互：
- 用户、角色、权限、菜单、配置、操作日志、登录日志页面
- 登录页与基础 token 存储
- `frontend/src/api/user.ts` 已接真实登录接口
- 其余系统设置 API 仍为本地 mock 数据

当前前端尚未具备：
- 用户多角色编辑
- 登录后加载真实角色、权限、菜单
- 基于权限的菜单控制与核心按钮显隐
- 首次登录强制修改密码流程

## 目标与边界

### 目标

1. 补齐系统设置模块对应数据库结构与后端接口。
2. 用户支持绑定多个角色。
3. 角色支持绑定多个权限。
4. 登录后后端返回当前用户角色、权限集合和可见菜单树。
5. 前端使用真实接口替换系统设置模块 mock 数据。
6. 操作日志和登录日志采用真实业务流程写入，而不是前端手动调用日志接口。
7. 提供默认管理员、默认角色、默认权限、默认菜单和默认配置项，保证迁移和 seed 后可直接联调。
8. 支持首次登录强制修改密码。
9. 保护内置用户与内置角色，禁止删除。

### 本期不做

- 模型管理、Skills 管理、工具管理真实接口
- 复杂动态路由生成体系
- 细粒度数据权限
- 审计日志删除、导出、归档
- 头像上传、文件上传、密码找回
- 全站所有按钮权限覆盖

## 总体架构

后端在现有 `backend/app/` 结构下按模块补齐：
- `models/`：实体模型
- `schemas/`：请求与响应模型
- `services/`：业务逻辑、权限聚合、日志写入
- `api/routes/`：接口入口

前端保留现有页面目录与路由结构，重点改造：
- 将系统设置模块 mock API 替换为真实请求
- `userStore` 增加 `roles`、`permissions`、`menus`
- 用户页角色编辑改为多选
- 登录后按后端返回的菜单树与权限集合驱动页面显示

后端负责真实授权结果与审计日志；前端负责展示控制和交互联调。

## 数据模型设计

### 1. user

在现有 `user` 表基础上新增：
- `status`：`active` / `inactive`
- `is_builtin`：是否为内置用户
- `must_change_password`：是否首次登录必须修改密码

保留现有：
- `id`
- `username`
- `email`
- `avatar`
- `hashed_password`
- `is_active`
- `is_superuser`
- `is_verified`
- `created_at`
- `updated_at`

说明：
- 认证可继续依赖 `is_active`，业务接口对外统一使用 `status`。
- `status=inactive` 时同步保证用户不可登录。
- `is_builtin=true` 的用户不可删除。
- 用户与角色通过 `user_roles` 维持多对多关系。

### 2. role

在现有 `role` 表基础上新增：
- `is_builtin`：是否为内置角色

保留现有：
- `id`
- `name`
- `code`
- `description`
- `status`
- `created_at`
- `updated_at`

说明：
- `is_builtin=true` 的角色不可删除。
- 角色通过 `role_permissions` 绑定多个权限。

### 3. permission

保留现有字段：
- `id`
- `name`
- `identifier`
- `type`
- `status`
- `created_at`
- `updated_at`

权限类型维持前端现状：
- `菜单`
- `按钮`
- `API`

说明：
- `identifier` 全局唯一。
- 被禁用的权限不参与用户权限聚合。
- 被角色引用的权限不可删除。

### 4. menu

在现有 `menu` 表基础上保留：
- `id`
- `name`
- `path`
- `permission`
- `icon`
- `sort`
- `status`
- `parent_id`
- `created_at`
- `updated_at`

新增：
- `component`：前端组件映射标识

说明：
- `menu` 使用树结构。
- 删除菜单允许级联删除其子菜单。
- 被禁用的菜单不参与可见菜单树聚合。
- `permission` 作为菜单可见性校验使用的权限标识。
- `component` 用于前端将菜单映射到已有页面组件。

### 5. system_config

新增 `system_config` 表：
- `id`
- `name`
- `key`
- `value`
- `description`
- `created_at`
- `updated_at`

说明：
- `key` 全局唯一。
- 配置项支持增删改查。

### 6. operation_log

新增 `operation_log` 表：
- `id`
- `operator_id`，可空
- `operator_name`
- `module`
- `action`
- `method`
- `result`
- `detail`
- `ip`
- `created_at`

说明：
- 记录系统设置模块所有关键写操作。
- 仅提供查询与详情，不支持删除。

### 7. login_log

新增 `login_log` 表：
- `id`
- `user_id`，可空
- `username`
- `ip`
- `location`
- `device`
- `result`
- `detail`
- `created_at`

说明：
- 记录登录成功、登录失败、退出登录。
- `location` 在本期可先存空字符串，字段保留，后续可接真实 IP 解析。
- `device` 由请求头中的 `User-Agent` 生成或直接存原始值。

## 权限模型与聚合规则

### 用户、角色、权限关系

- 一个用户可绑定多个角色。
- 一个角色可绑定多个权限。
- 用户最终权限集合为所有启用角色的启用权限并集。
- 超级管理员默认拥有全部有效权限。

### 菜单可见性规则

登录后由后端聚合当前用户可见菜单树：
- 菜单自身需为启用状态。
- 菜单配置了 `permission` 时，用户必须拥有该权限。
- 父菜单可因子菜单可见而保留。
- 超级管理员可看到全部启用菜单。

### 路由与按钮控制策略

本期不重写前端路由系统，采用折中方案：
- 页面组件映射继续静态维护在前端。
- 后端返回可见菜单树，前端据此渲染左侧菜单。
- 前端路由守卫根据 `permissions` 与 `menus` 判断页面可访问性。
- 页面内按钮显隐只覆盖系统设置模块的核心操作：新增、编辑、删除、分配权限、状态切换。

## 认证与当前用户信息

### 登录

保留：
- `POST /api/auth/login`

行为：
- 校验用户名/邮箱与密码。
- 成功后签发 Redis token。
- 记录登录成功日志。
- 失败时记录登录失败日志。
- 若用户被禁用，则视为登录失败。

### 当前用户信息

扩展：
- `GET /api/auth/me`

返回结构：

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "avatar": "",
  "roles": [
    { "id": 1, "name": "超级管理员", "code": "admin" }
  ],
  "permissions": ["setting:user", "user:create"],
  "menus": [
    {
      "id": 5,
      "name": "系统设置",
      "path": "/setting",
      "permission": "setting:view",
      "icon": "SettingOutlined",
      "component": "Layout",
      "sort": 5,
      "status": "active",
      "parentId": null,
      "children": []
    }
  ],
  "mustChangePassword": false
}
```

说明：
- `roles` 返回当前用户有效角色列表。
- `permissions` 返回聚合后的权限标识集合。
- `menus` 返回已过滤后的可见菜单树。
- `mustChangePassword` 用于首次登录强制改密。

### 退出登录

保留：
- `POST /api/auth/logout`

行为：
- 销毁 Redis token。
- 记录退出登录日志。

### 修改本人密码

新增：
- `POST /api/auth/change-password`

请求体：

```json
{
  "oldPassword": "old-password",
  "newPassword": "new-password"
}
```

行为：
- 仅允许当前登录用户修改自己的密码。
- 校验旧密码。
- 更新密码哈希。
- 将 `must_change_password` 置为 `false`。
- 写入操作日志。

## 系统设置接口设计

后端列表接口统一返回：

```json
{
  "list": [],
  "total": 0
}
```

树接口直接返回数组，创建与更新返回单对象。

### 1. 用户管理

- `GET /api/users`
- `POST /api/users`
- `PUT /api/users/{id}`
- `DELETE /api/users/{id}`
- `PATCH /api/users/{id}/status`

#### GET /api/users

查询参数：
- `username`
- `status`

返回项包含：
- `id`
- `username`
- `email`
- `roles: [{ id, name, code }]`
- `roleIds: number[]`
- `status`
- `createdAt`
- `isBuiltin`

#### POST /api/users

请求体：
- `username`
- `email`
- `roleIds: number[]`
- `status`

行为：
- 后端生成随机初始密码。
- 新建用户时 `must_change_password=true`。
- 创建成功后返回用户信息与一次性临时密码。

返回结构：

```json
{
  "user": {
    "id": 2,
    "username": "editor",
    "email": "editor@example.com",
    "roles": [],
    "roleIds": [],
    "status": "active",
    "createdAt": "2026-04-30 10:00:00",
    "isBuiltin": false
  },
  "temporaryPassword": "Abc12345"
}
```

#### PUT /api/users/{id}

请求体：
- `username`
- `email`
- `roleIds: number[]`
- `status`

说明：
- 编辑用户时不允许修改密码。
- 可修改角色绑定关系。

#### DELETE /api/users/{id}

规则：
- 内置用户不可删除。
- 删除成功写入操作日志。

#### PATCH /api/users/{id}/status

请求体：

```json
{ "status": "inactive" }
```

行为：
- 状态切换时同步影响登录可用性。

### 2. 角色管理

- `GET /api/roles`
- `POST /api/roles`
- `PUT /api/roles/{id}`
- `DELETE /api/roles/{id}`
- `PATCH /api/roles/{id}/status`
- `GET /api/roles/{id}/permissions`
- `PUT /api/roles/{id}/permissions`

#### GET /api/roles

查询参数：
- `name`
- `status`

返回项包含：
- `id`
- `name`
- `code`
- `description`
- `status`
- `isBuiltin`
- `createdAt`

#### PUT /api/roles/{id}/permissions

请求体：

```json
{ "permissionIds": [1, 2, 3] }
```

行为：
- 覆盖角色权限集合。
- 写入操作日志。

#### DELETE /api/roles/{id}

规则：
- 内置角色不可删除。
- 仍被用户绑定的角色不可删除。

### 3. 权限管理

- `GET /api/permissions`
- `POST /api/permissions`
- `PUT /api/permissions/{id}`
- `DELETE /api/permissions/{id}`
- `PATCH /api/permissions/{id}/status`

查询参数：
- `name`
- `type`

返回项包含：
- `id`
- `name`
- `identifier`
- `type`
- `status`
- `createdAt`

规则：
- `identifier` 唯一。
- 被角色引用的权限不可删除。
- 权限被禁用后，不再参与用户权限聚合；依赖该权限的菜单会在后续登录态刷新或重新获取 `auth/me` 后从可见菜单中消失。

### 4. 菜单配置

- `GET /api/menus/tree`
- `POST /api/menus`
- `PUT /api/menus/{id}`
- `DELETE /api/menus/{id}`
- `PATCH /api/menus/{id}/status`

返回项包含：
- `id`
- `name`
- `path`
- `permission`
- `icon`
- `component`
- `sort`
- `status`
- `parentId`
- `children`

规则：
- 删除菜单允许级联删除子菜单。
- 状态更新后会影响登录后菜单可见性。

### 5. 系统配置

- `GET /api/configs`
- `POST /api/configs`
- `PUT /api/configs/{id}`
- `DELETE /api/configs/{id}`

查询参数：
- `key`

返回项包含：
- `id`
- `name`
- `key`
- `value`
- `description`

规则：
- `key` 唯一。

### 6. 操作日志

- `GET /api/operation-logs`

查询参数：
- `operator`
- `module`
- `startTime`
- `endTime`

返回项包含：
- `id`
- `operator`
- `module`
- `action`
- `method`
- `result`
- `time`
- `detail`

说明：
- 只读。
- 支持详情查看。

### 7. 登录日志

- `GET /api/login-logs`

查询参数：
- `username`
- `result`
- `startTime`
- `endTime`

返回项包含：
- `id`
- `username`
- `ip`
- `location`
- `device`
- `result`
- `time`
- `detail`

说明：
- 只读。
- 支持详情查看。

## 日志写入策略

### 登录日志

在以下流程中真实写入：
- 登录成功
- 登录失败
- 退出登录

记录字段：
- 用户名
- 用户 ID
- IP
- 设备信息
- 结果
- 详情
- 时间

### 操作日志

在以下业务动作成功后显式写入：
- 创建用户
- 更新用户
- 删除用户
- 切换用户状态
- 创建角色
- 更新角色
- 删除角色
- 切换角色状态
- 分配角色权限
- 创建权限
- 更新权限
- 删除权限
- 切换权限状态
- 创建菜单
- 更新菜单
- 删除菜单
- 切换菜单状态
- 创建配置
- 更新配置
- 删除配置
- 用户修改自己的密码

实现方式：
- 使用轻量业务日志服务。
- 在每个明确写操作成功后显式调用。
- 不依赖全局中间件推断业务语义。

这样可以保证日志详情准确，例如：
- “为用户 admin 绑定角色 [admin, editor]”
- “将角色 viewer 状态改为 inactive”

## 前端联调设计

### 1. API 替换

以下文件由 mock 改为真实请求：
- `frontend/src/api/role.ts`
- `frontend/src/api/permission.ts`
- `frontend/src/api/menu.ts`
- `frontend/src/api/config.ts`
- `frontend/src/api/log.ts`
- 用户管理页中内联 mock 逻辑需要抽出为真实 API 模块

### 2. userStore 扩展

`frontend/src/stores/user.ts` 扩展为管理：
- `token`
- `userInfo`
- `roles`
- `permissions`
- `menus`
- `mustChangePassword`

新增能力：
- `hasPermission(permission: string)`
- 清理登录态时同步清空角色、权限、菜单和改密标记

### 3. 登录流程

登录页流程改为：
1. 调用 `POST /api/auth/login`
2. 保存 token
3. 调用 `GET /api/auth/me`
4. 将用户信息、角色、权限、菜单写入 store
5. 若 `mustChangePassword=true`，强制打开修改密码流程
6. 修改密码完成前不允许继续正常使用系统页面
7. 完成后进入首页

### 4. 用户页改造

`frontend/src/views/setting/user/index.vue` 改造为：
- 角色从单选改为多选
- 列表展示角色标签数组
- 新增成功后展示临时密码弹窗
- 编辑用户不提供密码输入框
- 删除内置用户时前端隐藏删除入口

### 5. 角色页改造

`frontend/src/views/setting/role/index.vue` 改造为：
- 分配权限抽屉使用真实权限树
- 打开分配权限时加载当前角色权限
- 提交时调用 `PUT /api/roles/{id}/permissions`
- 内置角色隐藏删除入口

### 6. 菜单与权限联动

前端菜单渲染以 `auth/me` 返回的 `menus` 为准。

页面内按钮显示规则以 `permissions` 为准，仅覆盖系统设置模块核心按钮：
- 新增
- 编辑
- 删除
- 分配权限
- 状态切换

### 7. 路由控制

不重写为完全动态路由。

采用方式：
- 现有页面组件映射继续静态维护
- 登录后菜单来源于后端 `menus`
- 路由守卫在访问受限页面时校验当前菜单或权限是否存在
- 无权限时重定向到首个可访问页面或登录页

## 初始化数据设计

通过 seed 初始化以下数据：

### 默认用户
- 超级管理员用户：`admin`
- `is_builtin=true`
- 默认可直接登录
- `must_change_password=false`

### 默认角色
- 超级管理员
- 编辑
- 访客

其中超级管理员角色：
- `is_builtin=true`
- 拥有全部系统设置相关权限

### 默认权限

至少包含：
- `setting:view`
- `setting:user`
- `setting:role`
- `setting:permission`
- `setting:menu`
- `setting:config`
- `setting:operation-log`
- `setting:login-log`
- `user:create`
- `user:update`
- `user:delete`
- `user:status`
- `role:create`
- `role:update`
- `role:delete`
- `role:status`
- `role:assign-permission`
- `permission:create`
- `permission:update`
- `permission:delete`
- `permission:status`
- `menu:create`
- `menu:update`
- `menu:delete`
- `menu:status`
- `config:create`
- `config:update`
- `config:delete`
- `operation-log:read`
- `login-log:read`

### 默认菜单

与现有前端路径对齐：
- `/setting`
- `/setting/user`
- `/setting/role`
- `/setting/permission`
- `/setting/menu`
- `/setting/config`
- `/setting/operation-log`
- `/setting/login-log`

并补齐每个菜单的：
- `permission`
- `icon`
- `component`
- `sort`
- `status`

### 默认配置项

至少包含：
- 站点名称
- 站点描述
- 上传限制

## 约束规则

- 用户创建时由后端自动生成随机初始密码。
- 用户首次登录必须修改密码。
- 编辑用户资料时不能修改密码。
- 禁用用户后不可登录。
- 内置用户不可删除。
- 内置角色不可删除。
- 删除角色前，如果仍有用户绑定，则禁止删除。
- 删除权限前，如果仍被角色引用，则禁止删除。
- 删除菜单允许级联删除子菜单。
- 配置项 `key` 全局唯一。
- 超级管理员默认拥有全部有效权限。
- 日志列表只读，不支持删除。

## 数据迁移与索引

本期新增迁移包括：
- 为 `user` 增加 `status`、`is_builtin`、`must_change_password`
- 为 `role` 增加 `is_builtin`
- 为 `menu` 增加 `component`
- 新建 `system_config`
- 新建 `operation_log`
- 新建 `login_log`

建议索引：
- `system_config.key` 唯一索引
- `operation_log.created_at` 索引
- `operation_log.operator_name` 索引
- `operation_log.module` 索引
- `login_log.created_at` 索引
- `login_log.username` 索引
- 视实际查询需要补充组合索引

## 验证方案

### 后端验证

- 执行数据库迁移
- 执行 seed
- 启动 FastAPI
- 验证登录、登出、改密
- 验证用户 CRUD 与多角色绑定
- 验证角色 CRUD 与分配权限
- 验证权限 CRUD
- 验证菜单树 CRUD
- 验证配置 CRUD
- 验证登录日志与操作日志查询
- 验证 `auth/me` 返回 roles、permissions、menus、mustChangePassword
- 验证内置对象保护与删除限制

### 前端验证

- 启动 Vite
- 浏览器真实登录
- 验证首次登录强制改密流程
- 验证用户多角色编辑与临时密码展示
- 验证角色分配权限
- 验证系统设置菜单按权限显示
- 验证核心按钮按权限显隐
- 验证配置维护
- 验证日志查询与详情
- 验证 401 自动清登录态并回到登录页

## 实施顺序

1. 完成数据库迁移与模型补充。
2. 扩展 seed，生成默认用户、角色、权限、菜单、配置。
3. 实现角色、权限、菜单、配置、日志基础查询接口。
4. 实现用户管理接口与随机密码生成逻辑。
5. 实现角色分配权限与用户绑定角色逻辑。
6. 实现操作日志与登录日志写入服务。
7. 扩展 `auth/me` 返回角色、权限、菜单和改密标记。
8. 前端替换系统设置模块 mock API。
9. 前端完成用户多角色、首次改密、菜单与按钮权限联动。
10. 浏览器联调并修正字段与交互细节。

## 结论

本设计将系统设置模块升级为可真实工作的 RBAC 基础层，覆盖用户、角色、权限、菜单、配置与审计日志闭环，并通过初始化数据与前端联调保证可直接验证。实施完成后，当前仓库将具备一套可扩展、可继续承接后续模型管理、技能管理和工具管理模块的后台权限基础设施。
