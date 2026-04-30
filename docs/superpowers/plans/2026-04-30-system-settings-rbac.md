# 系统设置 RBAC 与后端联调 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为系统设置模块补齐真实后端、RBAC 聚合、首次登录改密、审计日志和前端联调，替换现有 mock 数据。

**Architecture:** 后端沿用现有 FastAPI + SQLAlchemy 结构，在 `app/models`、`app/schemas`、`app/services`、`app/api/routes` 下按领域拆分，实现“用户-角色-权限-菜单”聚合和显式审计日志服务。前端保留现有静态页面组件映射，只把系统设置模块替换为真实 API，并用 `auth/me` 返回的 `roles`、`permissions`、`menus` 驱动登录态、菜单可见性、核心按钮显隐和首次登录改密流程。

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, Redis, fastapi-users, Pydantic, Vue 3, TypeScript, Pinia, vue-router, ant-design-vue, axios

---

## File Map

### 新建文件

| 文件路径 | 职责 |
|---------|------|
| `backend/app/models/system_config.py` | 系统配置模型 |
| `backend/app/models/operation_log.py` | 操作日志模型 |
| `backend/app/models/login_log.py` | 登录日志模型 |
| `backend/app/schemas/common.py` | 通用分页响应模型 |
| `backend/app/schemas/menu.py` | 菜单树请求/响应模型 |
| `backend/app/schemas/permission.py` | 权限请求/响应模型 |
| `backend/app/schemas/role.py` | 角色请求/响应模型 |
| `backend/app/schemas/system_config.py` | 配置项请求/响应模型 |
| `backend/app/schemas/log.py` | 登录日志与操作日志响应模型 |
| `backend/app/services/rbac.py` | 用户权限聚合、菜单树构建、`auth/me` 载荷组装 |
| `backend/app/services/audit.py` | 登录日志和操作日志写入服务 |
| `backend/app/services/system_users.py` | 用户管理服务、随机密码生成、内置用户保护 |
| `backend/app/services/system_roles.py` | 角色 CRUD、角色分配权限、内置角色保护 |
| `backend/app/services/system_permissions.py` | 权限 CRUD 与删除保护 |
| `backend/app/services/system_menus.py` | 菜单树 CRUD 与级联删除 |
| `backend/app/services/system_configs.py` | 系统配置 CRUD |
| `backend/app/api/routes/users.py` | 用户管理接口 |
| `backend/app/api/routes/roles.py` | 角色管理与分配权限接口 |
| `backend/app/api/routes/permissions.py` | 权限管理接口 |
| `backend/app/api/routes/menus.py` | 菜单管理接口 |
| `backend/app/api/routes/configs.py` | 配置管理接口 |
| `backend/app/api/routes/logs.py` | 登录日志与操作日志查询接口 |
| `backend/tests/conftest.py` | pytest 异步数据库 fixture |
| `backend/tests/test_schema_contract.py` | 模型与导出契约测试 |
| `backend/tests/test_rbac_service.py` | RBAC 聚合服务测试 |
| `backend/tests/test_system_users_service.py` | 用户服务测试 |
| `backend/tests/test_system_roles_service.py` | 角色服务测试 |
| `frontend/src/components/ForcePasswordChangeModal.vue` | 首次登录强制改密弹窗 |

### 修改文件

| 文件路径 | 变更 |
|---------|------|
| `backend/pyproject.toml` | 增加测试依赖 |
| `backend/alembic/versions/*.py` | 新增迁移：用户/角色/菜单扩展 + 新表 |
| `backend/app/models/user.py` | 增加 `status`、`is_builtin`、`must_change_password` |
| `backend/app/models/role.py` | 增加 `is_builtin` |
| `backend/app/models/menu.py` | 增加 `component` |
| `backend/app/models/__init__.py` | 导出新增模型 |
| `backend/app/schemas/auth.py` | 增加改密请求模型 |
| `backend/app/schemas/user.py` | 扩展 `auth/me` 与用户列表结构 |
| `backend/app/services/auth.py` | 登录校验、改密逻辑、禁用用户拦截 |
| `backend/app/api/routes/auth.py` | 扩展 `auth/me`，新增改密接口，记录登录/退出日志 |
| `backend/app/api/routes/__init__.py` | 导出新增 router |
| `backend/app/api/router.py` | 注册系统设置相关 router |
| `backend/app/db/seed.py` | 补齐内置用户、内置角色、权限、菜单、配置初始化 |
| `frontend/src/api/user.ts` | 扩展登录态、改密、用户管理相关类型与请求 |
| `frontend/src/api/role.ts` | 角色真实接口 |
| `frontend/src/api/permission.ts` | 权限真实接口 |
| `frontend/src/api/menu.ts` | 菜单真实接口 |
| `frontend/src/api/config.ts` | 配置真实接口 |
| `frontend/src/api/log.ts` | 日志真实接口 |
| `frontend/src/App.vue` | 启动时加载完整 `auth/me` 载荷 |
| `frontend/src/router/index.ts` | 登录守卫、权限与菜单访问控制 |
| `frontend/src/stores/user.ts` | 管理 `roles`、`permissions`、`menus`、`mustChangePassword` |
| `frontend/src/layouts/BasicLayout.vue` | 用后端菜单树渲染侧栏，按钮按权限显示 |
| `frontend/src/views/login/index.vue` | 登录后加载 `auth/me`，首次登录改密 |
| `frontend/src/views/setting/user/index.vue` | 多角色编辑、临时密码展示、真实用户接口 |
| `frontend/src/views/setting/role/index.vue` | 真实权限树、真实分配权限接口 |
| `frontend/src/views/setting/permission/index.vue` | 真实权限接口 |
| `frontend/src/views/setting/menu/index.vue` | 真实菜单树接口 |
| `frontend/src/views/setting/config/index.vue` | 真实配置接口 |
| `frontend/src/views/setting/operation-log/index.vue` | 真实操作日志接口 |
| `frontend/src/views/setting/login-log/index.vue` | 真实登录日志接口 |

---

## Scope Note

这份计划覆盖同一个可交付子系统：系统设置 RBAC 基础层。它虽然同时改动前后端，但所有任务都围绕同一条主线：让“系统设置”从 mock 页面升级为真实可登录、可授权、可审计、可联调的后台模块。不要再拆成更小 spec；按下面任务顺序执行即可。

---

### Task 1: 后端测试基线 + 模型与迁移骨架

**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/app/models/user.py`
- Modify: `backend/app/models/role.py`
- Modify: `backend/app/models/menu.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/models/system_config.py`
- Create: `backend/app/models/operation_log.py`
- Create: `backend/app/models/login_log.py`
- Create: `backend/alembic/versions/20260430_0002_system_settings_rbac.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_schema_contract.py`

- [ ] **Step 1: 给后端加测试依赖**

`backend/pyproject.toml` 增加测试组依赖：

```toml
[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "aiosqlite>=0.20.0",
]
```

- [ ] **Step 2: 写失败的模型契约测试**

`backend/tests/test_schema_contract.py`:

```python
from app.models import LoginLog, Menu, OperationLog, Role, SystemConfig, User


def test_user_model_has_status_builtin_and_password_reset_flags() -> None:
    columns = User.__table__.c
    assert "status" in columns
    assert "is_builtin" in columns
    assert "must_change_password" in columns


def test_role_model_has_builtin_flag() -> None:
    assert "is_builtin" in Role.__table__.c


def test_menu_model_has_component_column() -> None:
    assert "component" in Menu.__table__.c


def test_new_models_are_exported() -> None:
    assert SystemConfig.__tablename__ == "system_config"
    assert OperationLog.__tablename__ == "operation_log"
    assert LoginLog.__tablename__ == "login_log"
```

- [ ] **Step 3: 运行测试，确认先失败**

Run:

```bash
cd backend && uv sync --group dev && uv run pytest tests/test_schema_contract.py -q
```

Expected: `ImportError` 或列缺失断言失败。

- [ ] **Step 4: 实现最小模型改动**

`backend/app/models/user.py` 增量片段：

```python
from sqlalchemy import Boolean, Integer, String

status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

`backend/app/models/role.py` 增量片段：

```python
from sqlalchemy import Boolean, ForeignKey, String, Table, Column

is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

`backend/app/models/menu.py` 增量片段：

```python
component: Mapped[str] = mapped_column(String(255), default="", nullable=False)
```

`backend/app/models/system_config.py`:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class SystemConfig(TimestampMixin, Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)
```

`backend/app/models/operation_log.py`:

```python
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class OperationLog(TimestampMixin, Base):
    __tablename__ = "operation_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operator_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    operator_name: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ip: Mapped[str] = mapped_column(String(64), default="", nullable=False)
```

`backend/app/models/login_log.py`:

```python
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class LoginLog(TimestampMixin, Base):
    __tablename__ = "login_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    username: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    ip: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    device: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)
```

`backend/app/models/__init__.py` 更新导出：

```python
from app.models.login_log import LoginLog
from app.models.menu import Menu
from app.models.operation_log import OperationLog
from app.models.permission import Permission
from app.models.role import Role, role_permissions, user_roles
from app.models.system_config import SystemConfig
from app.models.user import User

__all__ = [
    "Base",
    "LoginLog",
    "Menu",
    "OperationLog",
    "Permission",
    "Role",
    "SystemConfig",
    "User",
    "role_permissions",
    "user_roles",
]
```

迁移文件核心片段：

```python
op.add_column("user", sa.Column("status", sa.String(length=20), server_default="active", nullable=False))
op.add_column("user", sa.Column("is_builtin", sa.Boolean(), server_default=sa.false(), nullable=False))
op.add_column("user", sa.Column("must_change_password", sa.Boolean(), server_default=sa.false(), nullable=False))
op.add_column("role", sa.Column("is_builtin", sa.Boolean(), server_default=sa.false(), nullable=False))
op.add_column("menu", sa.Column("component", sa.String(length=255), server_default="", nullable=False))
op.create_table(
    "system_config",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("name", sa.String(length=100), nullable=False),
    sa.Column("key", sa.String(length=100), nullable=False),
    sa.Column("value", sa.String(length=1000), nullable=False),
    sa.Column("description", sa.String(length=255), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.PrimaryKeyConstraint("id", name="pk_system_config"),
)
op.create_index("ix_system_config_key", "system_config", ["key"], unique=True)
op.create_table(
    "operation_log",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("operator_id", sa.Integer(), nullable=True),
    sa.Column("operator_name", sa.String(length=50), nullable=False),
    sa.Column("module", sa.String(length=100), nullable=False),
    sa.Column("action", sa.String(length=100), nullable=False),
    sa.Column("method", sa.String(length=20), nullable=False),
    sa.Column("result", sa.String(length=20), nullable=False),
    sa.Column("detail", sa.Text(), nullable=False),
    sa.Column("ip", sa.String(length=64), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.ForeignKeyConstraint(["operator_id"], ["user.id"], name="fk_operation_log_operator_id_user", ondelete="SET NULL"),
    sa.PrimaryKeyConstraint("id", name="pk_operation_log"),
)
op.create_table(
    "login_log",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=True),
    sa.Column("username", sa.String(length=50), nullable=False),
    sa.Column("ip", sa.String(length=64), nullable=False),
    sa.Column("location", sa.String(length=255), nullable=False),
    sa.Column("device", sa.String(length=255), nullable=False),
    sa.Column("result", sa.String(length=20), nullable=False),
    sa.Column("detail", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_login_log_user_id_user", ondelete="SET NULL"),
    sa.PrimaryKeyConstraint("id", name="pk_login_log"),
)
```

- [ ] **Step 5: 再跑一次模型契约测试**

Run:

```bash
cd backend && uv run pytest tests/test_schema_contract.py -q
```

Expected: `4 passed`。

- [ ] **Step 6: 提交**

```bash
git add backend/pyproject.toml backend/app/models backend/alembic/versions backend/tests
git commit -m "feat: add RBAC schema models and migration"
```

---

### Task 2: Seed 初始化与 RBAC 聚合服务

**Files:**
- Modify: `backend/app/db/seed.py`
- Create: `backend/app/services/rbac.py`
- Create: `backend/tests/test_rbac_service.py`

- [ ] **Step 1: 写失败的 RBAC 聚合测试**

`backend/tests/test_rbac_service.py`:

```python
from app.models.menu import Menu
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.services.rbac import build_visible_menu_tree, collect_user_permissions


def test_collect_user_permissions_skips_inactive_roles_and_permissions() -> None:
    read = Permission(name="用户查看", identifier="setting:user", type="菜单", status="active")
    hidden = Permission(name="已禁用权限", identifier="setting:hidden", type="按钮", status="inactive")
    active_role = Role(name="编辑", code="editor", description="", status="active")
    inactive_role = Role(name="访客", code="viewer", description="", status="inactive")
    active_role.permissions = [read, hidden]
    inactive_role.permissions = [Permission(name="ignored", identifier="ignored", type="按钮", status="active")]
    user = User(username="editor", email="editor@example.com", hashed_password="x", is_active=True, is_superuser=False, is_verified=True, avatar="")
    user.roles = [active_role, inactive_role]

    assert collect_user_permissions(user) == {"setting:user"}


def test_build_visible_menu_tree_keeps_visible_parent() -> None:
    parent = Menu(name="系统设置", path="/setting", permission="setting:view", icon="SettingOutlined", component="Layout", sort=1, status="active", parent_id=None)
    child = Menu(name="用户管理", path="/setting/user", permission="setting:user", icon="UserOutlined", component="SettingUser", sort=1, status="active", parent_id=1)
    parent.children = [child]

    result = build_visible_menu_tree([parent], {"setting:user"})
    assert result[0]["path"] == "/setting"
    assert result[0]["children"][0]["path"] == "/setting/user"
```

- [ ] **Step 2: 运行测试，确认先失败**

Run:

```bash
cd backend && uv run pytest tests/test_rbac_service.py -q
```

Expected: `ModuleNotFoundError: No module named 'app.services.rbac'`。

- [ ] **Step 3: 实现聚合服务**

`backend/app/services/rbac.py`:

```python
from collections.abc import Iterable

from app.models.menu import Menu
from app.models.user import User


def collect_user_permissions(user: User) -> set[str]:
    if user.is_superuser:
        return {
            permission.identifier
            for role in user.roles
            for permission in role.permissions
            if permission.status == "active"
        }
    permissions: set[str] = set()
    for role in user.roles:
        if role.status != "active":
            continue
        for permission in role.permissions:
            if permission.status == "active":
                permissions.add(permission.identifier)
    return permissions


def build_visible_menu_tree(menus: Iterable[Menu], permissions: set[str]) -> list[dict]:
    result: list[dict] = []
    for menu in sorted(menus, key=lambda item: item.sort):
        if menu.status != "active":
            continue
        children = build_visible_menu_tree(menu.children, permissions) if menu.children else []
        visible = not menu.permission or menu.permission in permissions or bool(children)
        if not visible:
            continue
        result.append(
            {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "permission": menu.permission,
                "icon": menu.icon,
                "component": menu.component,
                "sort": menu.sort,
                "status": menu.status,
                "parentId": menu.parent_id,
                "children": children,
            }
        )
    return result
```

- [ ] **Step 4: 扩展 seed 数据**

`backend/app/db/seed.py` 关键常量改成：

```python
ROLES = [
    {"name": "超级管理员", "code": "admin", "description": "拥有所有权限", "status": "active", "is_builtin": True},
    {"name": "编辑", "code": "editor", "description": "可编辑内容", "status": "active", "is_builtin": False},
    {"name": "访客", "code": "viewer", "description": "只读权限", "status": "inactive", "is_builtin": False},
]

USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "admin123", "is_superuser": True, "role_codes": ["admin"], "is_builtin": True, "must_change_password": False, "status": "active"},
]

SYSTEM_PERMISSIONS = [
    {"name": "用户管理", "identifier": "setting:user", "type": "菜单", "status": "active"},
    {"name": "用户新增", "identifier": "user:create", "type": "按钮", "status": "active"},
    {"name": "角色分配权限", "identifier": "role:assign-permission", "type": "按钮", "status": "active"},
    {"name": "登录日志查看", "identifier": "login-log:read", "type": "API", "status": "active"},
]
```

`seed_menus()` 在写入菜单时补 `component`：

```python
menu = Menu(
    name=data["name"],
    path=data["path"],
    permission=data["permission"],
    icon=data["icon"],
    component=data["component"],
    sort=data["sort"],
    status=data["status"],
    parent_id=parent_id,
)
```

- [ ] **Step 5: 运行测试并执行 seed 验证**

Run:

```bash
cd backend && uv run pytest tests/test_rbac_service.py -q && uv run python app/db/seed.py
```

Expected: `2 passed`，随后打印 `Seed completed.`。

- [ ] **Step 6: 提交**

```bash
git add backend/app/db/seed.py backend/app/services/rbac.py backend/tests/test_rbac_service.py
git commit -m "feat: add RBAC aggregation and seed data"
```

---

### Task 3: 认证载荷、首次登录改密与登录/退出日志

**Files:**
- Modify: `backend/app/schemas/auth.py`
- Modify: `backend/app/schemas/user.py`
- Modify: `backend/app/services/auth.py`
- Modify: `backend/app/api/routes/auth.py`
- Create: `backend/app/services/audit.py`
- Create: `backend/tests/test_system_users_service.py`

- [ ] **Step 1: 写失败的用户改密与 `auth/me` 载荷测试**

`backend/tests/test_system_users_service.py`:

```python
from pwdlib import PasswordHash

from app.models.user import User
from app.services.system_users import build_current_user_payload, change_own_password


password_hash = PasswordHash.recommended()


def test_build_current_user_payload_includes_roles_permissions_menus() -> None:
    user = User(username="admin", email="admin@example.com", hashed_password="x", is_active=True, is_superuser=True, is_verified=True, avatar="")
    payload = build_current_user_payload(
        user=user,
        roles=[{"id": 1, "name": "超级管理员", "code": "admin"}],
        permissions={"setting:user"},
        menus=[{"path": "/setting/user"}],
    )
    assert payload["roles"][0]["code"] == "admin"
    assert payload["permissions"] == ["setting:user"]
    assert payload["menus"][0]["path"] == "/setting/user"


def test_change_own_password_clears_force_change_flag() -> None:
    user = User(
        username="editor",
        email="editor@example.com",
        hashed_password=password_hash.hash("old-pass"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        must_change_password=True,
    )

    change_own_password(user, old_password="old-pass", new_password="new-pass")
    assert user.must_change_password is False
```

- [ ] **Step 2: 运行测试，确认先失败**

Run:

```bash
cd backend && uv run pytest tests/test_system_users_service.py -q
```

Expected: `ModuleNotFoundError: No module named 'app.services.system_users'`。

- [ ] **Step 3: 实现审计服务与用户载荷组装**

`backend/app/services/audit.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_log import LoginLog
from app.models.operation_log import OperationLog


async def write_login_log(
    session: AsyncSession,
    *,
    user_id: int | None,
    username: str,
    ip: str,
    device: str,
    result: str,
    detail: str,
) -> None:
    session.add(
        LoginLog(
            user_id=user_id,
            username=username,
            ip=ip,
            location="",
            device=device,
            result=result,
            detail=detail,
        )
    )
    await session.flush()


async def write_operation_log(
    session: AsyncSession,
    *,
    operator_id: int | None,
    operator_name: str,
    module: str,
    action: str,
    method: str,
    result: str,
    detail: str,
    ip: str,
) -> None:
    session.add(
        OperationLog(
            operator_id=operator_id,
            operator_name=operator_name,
            module=module,
            action=action,
            method=method,
            result=result,
            detail=detail,
            ip=ip,
        )
    )
    await session.flush()
```

`backend/app/services/system_users.py`:

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def build_current_user_payload(*, user, roles, permissions: set[str], menus: list[dict]) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "roles": roles,
        "permissions": sorted(permissions),
        "menus": menus,
        "mustChangePassword": user.must_change_password,
    }


def change_own_password(user, *, old_password: str, new_password: str) -> None:
    verified, updated_hash = password_hash.verify_and_update(old_password, user.hashed_password)
    if not verified:
        raise ValueError("旧密码错误")
    user.hashed_password = updated_hash or password_hash.hash(new_password)
    user.must_change_password = False
```

- [ ] **Step 4: 更新认证 schema、service 和 route**

`backend/app/schemas/auth.py` 增加：

```python
class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str
```

`backend/app/schemas/user.py` 用于 `auth/me` 的响应结构：

```python
class RoleSummary(BaseModel):
    id: int
    name: str
    code: str


class MenuSummary(BaseModel):
    id: int
    name: str
    path: str
    permission: str
    icon: str
    component: str
    sort: int
    status: str
    parentId: int | None
    children: list["MenuSummary"] = []


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    roles: list[RoleSummary]
    permissions: list[str]
    menus: list[MenuSummary]
    mustChangePassword: bool
```

`backend/app/api/routes/auth.py` 新增改密接口片段：

```python
@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    change_own_password(user, old_password=payload.oldPassword, new_password=payload.newPassword)
    session.add(user)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="用户管理",
        action="修改本人密码",
        method="POST",
        result="成功",
        detail=f"用户 {user.username} 修改了自己的密码",
        ip="",
    )
    await session.commit()
    return {"message": "密码修改成功"}
```

`GET /api/auth/me` 用 `collect_user_permissions()`、`build_visible_menu_tree()` 和 `build_current_user_payload()` 组装完整返回。

- [ ] **Step 5: 运行测试验证通过**

Run:

```bash
cd backend && uv run pytest tests/test_system_users_service.py -q
```

Expected: `2 passed`。

- [ ] **Step 6: 提交**

```bash
git add backend/app/schemas backend/app/services backend/app/api/routes/auth.py backend/tests/test_system_users_service.py
git commit -m "feat: extend auth payload and first-login password flow"
```

---

### Task 4: 系统设置后端 CRUD、角色分配权限与日志查询接口

**Files:**
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/schemas/role.py`
- Create: `backend/app/schemas/permission.py`
- Create: `backend/app/schemas/menu.py`
- Create: `backend/app/schemas/system_config.py`
- Create: `backend/app/schemas/log.py`
- Create: `backend/app/services/system_roles.py`
- Create: `backend/app/services/system_permissions.py`
- Create: `backend/app/services/system_menus.py`
- Create: `backend/app/services/system_configs.py`
- Create: `backend/app/api/routes/roles.py`
- Create: `backend/app/api/routes/permissions.py`
- Create: `backend/app/api/routes/menus.py`
- Create: `backend/app/api/routes/configs.py`
- Create: `backend/app/api/routes/logs.py`
- Modify: `backend/app/api/routes/__init__.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_system_roles_service.py`

- [ ] **Step 1: 写失败的角色删除保护与权限分配测试**

`backend/tests/test_system_roles_service.py`:

```python
import pytest

from app.models.permission import Permission
from app.models.role import Role
from app.services.system_roles import delete_role_or_raise, replace_role_permissions


def test_delete_role_blocks_builtin_role() -> None:
    role = Role(name="超级管理员", code="admin", description="", status="active", is_builtin=True)
    with pytest.raises(ValueError, match="内置角色不允许删除"):
        delete_role_or_raise(role, linked_user_count=0)


def test_replace_role_permissions_overwrites_existing_list() -> None:
    role = Role(name="编辑", code="editor", description="", status="active")
    old = Permission(name="旧权限", identifier="old", type="按钮", status="active")
    new = Permission(name="新权限", identifier="new", type="按钮", status="active")
    role.permissions = [old]

    replace_role_permissions(role, [new])
    assert [permission.identifier for permission in role.permissions] == ["new"]
```

- [ ] **Step 2: 运行测试，确认先失败**

Run:

```bash
cd backend && uv run pytest tests/test_system_roles_service.py -q
```

Expected: `ModuleNotFoundError: No module named 'app.services.system_roles'`。

- [ ] **Step 3: 实现后端 schema 与 service 最小闭环**

`backend/app/schemas/common.py`:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    list: list[T]
    total: int
```

`backend/app/services/system_roles.py`:

```python
def delete_role_or_raise(role, *, linked_user_count: int) -> None:
    if role.is_builtin:
        raise ValueError("内置角色不允许删除")
    if linked_user_count > 0:
        raise ValueError("角色仍被用户绑定，不能删除")


def replace_role_permissions(role, permissions) -> None:
    role.permissions = list(permissions)
```

`backend/app/services/system_permissions.py`:

```python
def delete_permission_or_raise(*, linked_role_count: int) -> None:
    if linked_role_count > 0:
        raise ValueError("权限仍被角色引用，不能删除")
```

`backend/app/services/system_menus.py`:

```python
def apply_menu_status(menu, status: str) -> None:
    menu.status = status
```

`backend/app/services/system_configs.py`:

```python
def update_config_value(config, *, name: str, key: str, value: str, description: str) -> None:
    config.name = name
    config.key = key
    config.value = value
    config.description = description
```

- [ ] **Step 4: 接上 routes 和 router 聚合**

`backend/app/api/routes/roles.py` 关键片段：

```python
router = APIRouter(prefix="/roles", tags=["roles"])


@router.put("/{role_id}/permissions")
async def update_role_permissions(role_id: int, payload: RolePermissionAssignRequest, session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    role = await session.get(Role, role_id)
    permissions = list((await session.scalars(select(Permission).where(Permission.id.in_(payload.permissionIds)))).all())
    replace_role_permissions(role, permissions)
    await session.commit()
    return {"message": "权限分配成功"}
```

`backend/app/api/routes/logs.py` 关键片段：

```python
router = APIRouter(tags=["logs"])


@router.get("/operation-logs", response_model=ListResponse[OperationLogItem])
async def list_operation_logs(
    operator: str | None = None,
    module: str | None = None,
    startTime: datetime | None = None,
    endTime: datetime | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> ListResponse[OperationLogItem]:
    statement = select(OperationLog).order_by(OperationLog.created_at.desc())
    if operator:
        statement = statement.where(OperationLog.operator_name.contains(operator))
    if module:
        statement = statement.where(OperationLog.module == module)
    if startTime:
        statement = statement.where(OperationLog.created_at >= startTime)
    if endTime:
        statement = statement.where(OperationLog.created_at <= endTime)
    rows = list((await session.scalars(statement)).all())
    return ListResponse(
        list=[OperationLogItem.model_validate(row) for row in rows],
        total=len(rows),
    )


@router.get("/login-logs", response_model=ListResponse[LoginLogItem])
async def list_login_logs(
    username: str | None = None,
    result: str | None = None,
    startTime: datetime | None = None,
    endTime: datetime | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> ListResponse[LoginLogItem]:
    statement = select(LoginLog).order_by(LoginLog.created_at.desc())
    if username:
        statement = statement.where(LoginLog.username.contains(username))
    if result:
        statement = statement.where(LoginLog.result == result)
    if startTime:
        statement = statement.where(LoginLog.created_at >= startTime)
    if endTime:
        statement = statement.where(LoginLog.created_at <= endTime)
    rows = list((await session.scalars(statement)).all())
    return ListResponse(
        list=[LoginLogItem.model_validate(row) for row in rows],
        total=len(rows),
    )
```

`backend/app/api/routes/__init__.py` 改成：

```python
from .auth import router as auth_router
from .configs import router as configs_router
from .health import router as health_router
from .logs import router as logs_router
from .menus import router as menus_router
from .permissions import router as permissions_router
from .roles import router as roles_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "configs_router",
    "health_router",
    "logs_router",
    "menus_router",
    "permissions_router",
    "roles_router",
    "users_router",
]
```

`backend/app/api/router.py` 注册全部 router：

```python
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
api_router.include_router(menus_router)
api_router.include_router(configs_router)
api_router.include_router(logs_router)
```

- [ ] **Step 5: 运行服务测试与基础 API 冒烟**

Run:

```bash
cd backend && uv run pytest tests/test_system_roles_service.py -q && uv run uvicorn main:app --reload
```

Expected: 测试 `2 passed`，随后本地服务启动成功。

- [ ] **Step 6: 提交**

```bash
git add backend/app/schemas backend/app/services backend/app/api/routes backend/tests/test_system_roles_service.py
git commit -m "feat: add system settings CRUD and log query routes"
```

---

### Task 5: 用户管理接口、随机初始密码与内置用户保护

**Files:**
- Create: `backend/app/api/routes/users.py`
- Create: `backend/app/services/system_users.py`
- Modify: `backend/app/db/seed.py`
- Modify: `backend/tests/test_system_users_service.py`

- [ ] **Step 1: 先补用户服务测试**

把 `backend/tests/test_system_users_service.py` 追加成：

```python
import pytest

from app.models.user import User
from app.services.system_users import create_temporary_password, delete_user_or_raise


def test_create_temporary_password_returns_non_empty_secret() -> None:
    password = create_temporary_password()
    assert len(password) >= 12


def test_delete_user_blocks_builtin_user() -> None:
    user = User(username="admin", email="admin@example.com", hashed_password="x", is_active=True, is_superuser=True, is_verified=True, avatar="", is_builtin=True)
    with pytest.raises(ValueError, match="内置用户不允许删除"):
        delete_user_or_raise(user)
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```bash
cd backend && uv run pytest tests/test_system_users_service.py -q
```

Expected: 函数缺失导致失败。

- [ ] **Step 3: 实现用户服务与 route**

`backend/app/services/system_users.py` 增加：

```python
from secrets import choice
from string import ascii_letters, digits


def create_temporary_password(length: int = 12) -> str:
    alphabet = ascii_letters + digits
    return "".join(choice(alphabet) for _ in range(length))


def delete_user_or_raise(user) -> None:
    if user.is_builtin:
        raise ValueError("内置用户不允许删除")
```

`backend/app/api/routes/users.py` 关键片段：

```python
@router.post("/users", response_model=CreateUserResponse)
async def create_user(payload: UserCreateRequest, session: AsyncSession = Depends(get_db_session)) -> CreateUserResponse:
    temporary_password = create_temporary_password()
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=password_hash.hash(temporary_password),
        is_active=payload.status == "active",
        is_superuser=False,
        is_verified=True,
        avatar="",
        status=payload.status,
        is_builtin=False,
        must_change_password=True,
    )
    roles = list((await session.scalars(select(Role).where(Role.id.in_(payload.roleIds)))).all())
    user.roles = roles
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user_payload = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [{"id": role.id, "name": role.name, "code": role.code} for role in user.roles],
        "roleIds": [role.id for role in user.roles],
        "status": user.status,
        "createdAt": user.created_at.isoformat(sep=" ", timespec="seconds"),
        "isBuiltin": user.is_builtin,
    }
    return CreateUserResponse(user=UserListItem.model_validate(user_payload), temporaryPassword=temporary_password)
```

`PUT /api/users/{id}` 只接受 `username`、`email`、`roleIds`、`status`，不要接受密码字段。

- [ ] **Step 4: 运行用户服务测试**

Run:

```bash
cd backend && uv run pytest tests/test_system_users_service.py -q
```

Expected: `4 passed`。

- [ ] **Step 5: 手工验证临时密码与内置用户保护**

Run:

```bash
curl -X POST http://127.0.0.1:8000/api/users \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"username":"tester","email":"tester@example.com","roleIds":[],"status":"active"}'
```

Expected: 响应中包含 `temporaryPassword`；删除内置管理员时返回业务错误。

- [ ] **Step 6: 提交**

```bash
git add backend/app/services/system_users.py backend/app/api/routes/users.py backend/tests/test_system_users_service.py
git commit -m "feat: add system user management with temporary passwords"
```

---

### Task 6: 前端登录态、菜单渲染、首次登录改密与权限守卫

**Files:**
- Modify: `frontend/src/api/user.ts`
- Modify: `frontend/src/stores/user.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/layouts/BasicLayout.vue`
- Modify: `frontend/src/views/login/index.vue`
- Create: `frontend/src/components/ForcePasswordChangeModal.vue`

- [ ] **Step 1: 更新用户 API 类型与改密请求**

`frontend/src/api/user.ts` 变成：

```ts
import request from './request'

export interface RoleSummary {
  id: number
  name: string
  code: string
}

export interface MenuSummary {
  id: number
  name: string
  path: string
  permission: string
  icon: string
  component: string
  sort: number
  status: 'active' | 'inactive'
  parentId: number | null
  children: MenuSummary[]
}

export interface UserInfo {
  id: number
  username: string
  email: string
  avatar: string
  roles: RoleSummary[]
  permissions: string[]
  menus: MenuSummary[]
  mustChangePassword: boolean
}

export function changePasswordApi(params: { oldPassword: string; newPassword: string }) {
  return request.post('/auth/change-password', params) as Promise<{ message: string }>
}
```

- [ ] **Step 2: 扩展 `userStore`**

`frontend/src/stores/user.ts`:

```ts
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { MenuSummary, RoleSummary, UserInfo } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)
  const roles = ref<RoleSummary[]>([])
  const permissions = ref<string[]>([])
  const menus = ref<MenuSummary[]>([])
  const mustChangePassword = ref(false)

  function setAuthPayload(info: UserInfo) {
    userInfo.value = info
    roles.value = info.roles
    permissions.value = info.permissions
    menus.value = info.menus
    mustChangePassword.value = info.mustChangePassword
  }

  function hasPermission(permission: string) {
    return permissions.value.includes(permission)
  }

  function clearToken() {
    token.value = ''
    userInfo.value = null
    roles.value = []
    permissions.value = []
    menus.value = []
    mustChangePassword.value = false
    localStorage.removeItem('token')
  }

  return { token, userInfo, roles, permissions, menus, mustChangePassword, setAuthPayload, hasPermission, clearToken }
})
```

- [ ] **Step 3: 加首次登录改密弹窗**

`frontend/src/components/ForcePasswordChangeModal.vue`:

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { changePasswordApi } from '@/api/user'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ success: [] }>()
const formState = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const loading = ref(false)

async function handleSubmit() {
  if (formState.newPassword !== formState.confirmPassword) {
    message.error('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    await changePasswordApi({ oldPassword: formState.oldPassword, newPassword: formState.newPassword })
    message.success('密码修改成功')
    emit('success')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 4: 更新登录流程、App 启动加载和菜单渲染**

`frontend/src/views/login/index.vue` 关键改动：

```ts
const result = await loginApi({ username: formState.username, password: formState.password })
userStore.setToken(result.token)
const userInfo = await getUserInfoApi()
userStore.setAuthPayload(userInfo)
router.push(userInfo.menus[0]?.path || '/dashboard')
```

`frontend/src/App.vue` 改成：

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { getUserInfoApi } from './api/user'
import ForcePasswordChangeModal from './components/ForcePasswordChangeModal.vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

onMounted(async () => {
  if (userStore.token && !userStore.userInfo) {
    userStore.setAuthPayload(await getUserInfoApi())
  }
})
</script>

<template>
  <router-view />
  <ForcePasswordChangeModal :open="userStore.mustChangePassword" @success="userStore.mustChangePassword = false" />
</template>
```

`frontend/src/layouts/BasicLayout.vue` 把硬编码菜单替换为基于 `userStore.menus` 的递归渲染。

- [ ] **Step 5: 更新路由守卫并构建前端**

`frontend/src/router/index.ts` 守卫核心片段：

```ts
router.beforeEach((to) => {
  const userStore = useUserStore()
  if (!userStore.token && to.path !== '/login') return '/login'
  if (userStore.token && to.path === '/login') return userStore.menus[0]?.path || '/dashboard'
  if (to.path.startsWith('/setting') && userStore.menus.length > 0) {
    const visiblePaths = new Set<string>()
    const walk = (menus: typeof userStore.menus) => menus.forEach((menu) => {
      visiblePaths.add(menu.path)
      walk(menu.children)
    })
    walk(userStore.menus)
    if (!visiblePaths.has(to.path)) return userStore.menus[0]?.path || '/dashboard'
  }
})
```

Run:

```bash
cd frontend && pnpm build
```

Expected: Vite 输出 `built in <n>ms`，且没有 TypeScript 报错。

- [ ] **Step 6: 提交**

```bash
git add frontend/src/api/user.ts frontend/src/stores/user.ts frontend/src/App.vue frontend/src/router/index.ts frontend/src/layouts/BasicLayout.vue frontend/src/views/login/index.vue frontend/src/components/ForcePasswordChangeModal.vue
git commit -m "feat: wire auth payload, password reset modal and menu guards"
```

---

### Task 7: 前端系统设置页面替换真实接口并完成多角色/权限联调

**Files:**
- Modify: `frontend/src/api/user.ts`
- Modify: `frontend/src/api/role.ts`
- Modify: `frontend/src/api/permission.ts`
- Modify: `frontend/src/api/menu.ts`
- Modify: `frontend/src/api/config.ts`
- Modify: `frontend/src/api/log.ts`
- Modify: `frontend/src/views/setting/user/index.vue`
- Modify: `frontend/src/views/setting/role/index.vue`
- Modify: `frontend/src/views/setting/permission/index.vue`
- Modify: `frontend/src/views/setting/menu/index.vue`
- Modify: `frontend/src/views/setting/config/index.vue`
- Modify: `frontend/src/views/setting/operation-log/index.vue`
- Modify: `frontend/src/views/setting/login-log/index.vue`

- [ ] **Step 1: 先把 API 文件全部换成真实请求**

`frontend/src/api/role.ts`:

```ts
import request from './request'

export interface RoleItem {
  id: number
  name: string
  code: string
  description: string
  status: 'active' | 'inactive'
  isBuiltin: boolean
  createdAt: string
}

export function getRoleListApi(params: { name?: string; status?: string }) {
  return request.get('/roles', { params }) as Promise<{ list: RoleItem[]; total: number }>
}

export function updateRolePermissionsApi(id: number, permissionIds: number[]) {
  return request.put(`/roles/${id}/permissions`, { permissionIds }) as Promise<{ message: string }>
}
```

`frontend/src/api/menu.ts`:

```ts
export function getMenuTreeApi() {
  return request.get('/menus/tree') as Promise<MenuItem[]>
}
```

同样方式把 `permission.ts`、`config.ts`、`log.ts` 从 `new Promise + setTimeout` 改成 `request.get/post/put/delete/patch`。

- [ ] **Step 2: 用户页改成多角色 + 临时密码弹窗**

`frontend/src/views/setting/user/index.vue` 关键替换：

```ts
interface UserItem {
  id: number
  username: string
  email: string
  roles: { id: number; name: string; code: string }[]
  roleIds: number[]
  status: 'active' | 'inactive'
  createdAt: string
  isBuiltin: boolean
}

const formState = reactive({
  username: '',
  email: '',
  roleIds: [] as number[],
  status: undefined as 'active' | 'inactive' | undefined,
})
```

模板中的角色控件改成：

```vue
<a-select v-model:value="formState.roleIds" mode="multiple" placeholder="请选择角色">
  <a-select-option v-for="role in roleOptions" :key="role.id" :value="role.id">{{ role.name }}</a-select-option>
</a-select>
```

创建成功后显示临时密码：

```ts
const result = await createSystemUserApi(data)
Modal.success({ title: '用户创建成功', content: `初始密码：${result.temporaryPassword}` })
```

- [ ] **Step 3: 角色页接真实权限树和分配权限接口**

`frontend/src/views/setting/role/index.vue` 关键替换：

```ts
async function handleAssignPermission(record: RoleItem) {
  permissionRoleId.value = record.id
  permissionRoleName.value = record.name
  const [allPermissions, currentPermissions] = await Promise.all([
    getPermissionListApi({}),
    getRolePermissionsApi(record.id),
  ])
  permissionTree.value = buildPermissionTree(allPermissions.list)
  checkedPermissions.value = currentPermissions.permissionIds
  permissionModalVisible.value = true
}

async function handlePermissionOk() {
  await updateRolePermissionsApi(permissionRoleId.value!, checkedPermissions.value as number[])
  message.success('权限分配成功')
  permissionModalVisible.value = false
}
```

- [ ] **Step 4: 其余系统设置页面去掉 mock 逻辑**

每个页面统一改成：

```ts
async function fetchData() {
  loading.value = true
  try {
    const res = await getPermissionListApi({ name: searchForm.name, type: searchForm.type })
    dataSource.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}
```

删除：
- `mockData`
- `nextId`
- `setTimeout`
- 本地 `findAndUpdate`、`findAndDelete` 等假实现

- [ ] **Step 5: 构建并在浏览器里走完系统设置黄金路径**

Run:

```bash
cd frontend && pnpm build
```

然后手动验证：
1. 登录管理员账号。
2. 新建一个多角色用户，复制临时密码。
3. 打开角色页给“编辑”分配部分权限。
4. 退出管理员，用新用户首次登录并强制改密。
5. 确认新用户只能看到有权限的系统设置菜单和按钮。
6. 切换用户/角色/权限/菜单状态后刷新页面，确认可见性变化。
7. 打开操作日志和登录日志，确认出现刚刚的登录、改密、增删改记录。

- [ ] **Step 6: 提交**

```bash
git add frontend/src/api frontend/src/views/setting
git commit -m "feat: connect system settings pages to real APIs"
```

---

### Task 8: 全链路验证、迁移说明与最终收尾

**Files:**
- Modify: `backend/README.md`
- Modify: `README.md`

- [ ] **Step 1: 补充运行说明**

在 `backend/README.md` 增加：

```md
## 系统设置联调启动

执行顺序：
1. `docker compose up -d`
2. `cd backend`
3. `uv sync --group dev`
4. `uv run alembic upgrade head`
5. `uv run python app/db/seed.py`
6. `uv run uvicorn main:app --reload`

默认管理员：`admin / admin123`
```

在根 `README.md` 增加前端启动说明：

```md
前端开发命令：
- `cd frontend`
- `pnpm install`
- `pnpm dev`
```

- [ ] **Step 2: 跑后端测试**

Run:

```bash
cd backend && uv run pytest -q
```

Expected: 全部新增测试通过。

- [ ] **Step 3: 跑前端构建**

Run:

```bash
cd frontend && pnpm build
```

Expected: Vite 构建成功。

- [ ] **Step 4: 重新走一次端到端流程**

按顺序手动验证：

```text
1. 管理员登录
2. 新建用户并获取临时密码
3. 首次登录强制改密
4. 分配角色权限
5. 刷新菜单与按钮显隐
6. 查看登录日志与操作日志
7. 尝试删除内置管理员和内置角色，确认被拒绝
```

记录任何字段不一致问题，优先修接口字段命名，再修页面映射。

- [ ] **Step 5: 提交**

```bash
git add README.md backend/README.md
git commit -m "docs: document RBAC setup and verification flow"
```

---

## Self-Review

### Spec coverage check

- 用户多角色：Task 5 + Task 7 覆盖。
- 角色多权限：Task 4 + Task 7 覆盖。
- `auth/me` 返回 `roles` / `permissions` / `menus` / `mustChangePassword`：Task 3 + Task 6 覆盖。
- 首次登录改密：Task 3 + Task 6 覆盖。
- 内置用户、内置角色删除保护：Task 5 + Task 4 覆盖。
- 菜单 `component` 字段、菜单树可见性：Task 1 + Task 2 + Task 6 覆盖。
- 真实登录日志与操作日志：Task 3 + Task 4 + Task 7 覆盖。
- 初始化数据：Task 2 覆盖。
- 系统设置真实接口替换 mock：Task 4 + Task 7 覆盖。
- 最终验证与启动文档：Task 8 覆盖。

没有遗漏的 spec 要求。

### Placeholder scan

- 没有 `TODO`、`TBD`、`implement later`。
- 每个代码步骤都给了明确片段。
- 每个验证步骤都给了具体命令和预期。

### Type consistency check

- 后端统一使用 `must_change_password`（数据库）与 `mustChangePassword`（前端载荷）。
- 菜单载荷统一使用 `parentId`、`component`。
- 前端用户页统一使用 `roleIds` 和 `roles`。
- 角色分配权限接口统一使用 `permissionIds`。

一致性通过。
