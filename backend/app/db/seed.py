import asyncio

from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.menu import Menu
from app.models.permission import Permission
from app.models.role import Role
from app.models.system_config import SystemConfig
from app.models.user import User

password_hash = PasswordHash.recommended()


ROLES = [
    {"name": "超级管理员", "code": "admin", "description": "拥有所有权限", "status": "active", "is_builtin": True},
    {"name": "编辑", "code": "editor", "description": "可编辑内容", "status": "active", "is_builtin": False},
    {"name": "访客", "code": "viewer", "description": "只读权限", "status": "inactive", "is_builtin": False},
]

PERMISSIONS = [
    {"name": "系统设置查看", "identifier": "setting:view", "type": "菜单", "status": "active"},
    {"name": "用户管理", "identifier": "setting:user", "type": "菜单", "status": "active"},
    {"name": "角色管理", "identifier": "setting:role", "type": "菜单", "status": "active"},
    {"name": "权限管理", "identifier": "setting:permission", "type": "菜单", "status": "active"},
    {"name": "菜单配置", "identifier": "setting:menu", "type": "菜单", "status": "active"},
    {"name": "系统配置", "identifier": "setting:config", "type": "菜单", "status": "active"},
    {"name": "操作日志", "identifier": "setting:operation-log", "type": "菜单", "status": "active"},
    {"name": "登录日志", "identifier": "setting:login-log", "type": "菜单", "status": "active"},
    {"name": "用户新增", "identifier": "user:create", "type": "按钮", "status": "active"},
    {"name": "用户编辑", "identifier": "user:update", "type": "按钮", "status": "active"},
    {"name": "用户删除", "identifier": "user:delete", "type": "按钮", "status": "active"},
    {"name": "用户状态", "identifier": "user:status", "type": "按钮", "status": "active"},
    {"name": "角色新增", "identifier": "role:create", "type": "按钮", "status": "active"},
    {"name": "角色编辑", "identifier": "role:update", "type": "按钮", "status": "active"},
    {"name": "角色删除", "identifier": "role:delete", "type": "按钮", "status": "active"},
    {"name": "角色状态", "identifier": "role:status", "type": "按钮", "status": "active"},
    {"name": "角色分配权限", "identifier": "role:assign-permission", "type": "按钮", "status": "active"},
    {"name": "权限新增", "identifier": "permission:create", "type": "按钮", "status": "active"},
    {"name": "权限编辑", "identifier": "permission:update", "type": "按钮", "status": "active"},
    {"name": "权限删除", "identifier": "permission:delete", "type": "按钮", "status": "active"},
    {"name": "权限状态", "identifier": "permission:status", "type": "按钮", "status": "active"},
    {"name": "菜单新增", "identifier": "menu:create", "type": "按钮", "status": "active"},
    {"name": "菜单编辑", "identifier": "menu:update", "type": "按钮", "status": "active"},
    {"name": "菜单删除", "identifier": "menu:delete", "type": "按钮", "status": "active"},
    {"name": "菜单状态", "identifier": "menu:status", "type": "按钮", "status": "active"},
    {"name": "配置新增", "identifier": "config:create", "type": "按钮", "status": "active"},
    {"name": "配置编辑", "identifier": "config:update", "type": "按钮", "status": "active"},
    {"name": "配置删除", "identifier": "config:delete", "type": "按钮", "status": "active"},
    {"name": "操作日志查看", "identifier": "operation-log:read", "type": "API", "status": "active"},
    {"name": "登录日志查看", "identifier": "login-log:read", "type": "API", "status": "active"},
]

USERS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "is_superuser": True,
        "role_code": "admin",
        "is_builtin": True,
        "must_change_password": False,
        "status": "active",
    },
]

MENUS = [
    {"name": "仪表盘", "path": "/dashboard", "permission": "dashboard:view", "icon": "DashboardOutlined", "component": "Dashboard", "sort": 1, "status": "active", "parent_path": None},
    {"name": "模型管理", "path": "/model", "permission": "model:view", "icon": "RobotOutlined", "component": "Model", "sort": 2, "status": "active", "parent_path": None},
    {"name": "Skills管理", "path": "/skill", "permission": "skill:view", "icon": "ThunderboltOutlined", "component": "Skill", "sort": 3, "status": "active", "parent_path": None},
    {"name": "工具管理", "path": "/tool", "permission": "tool:view", "icon": "ToolOutlined", "component": "Tool", "sort": 4, "status": "active", "parent_path": None},
    {"name": "系统设置", "path": "/setting", "permission": "setting:view", "icon": "SettingOutlined", "component": "Layout", "sort": 5, "status": "active", "parent_path": None},
    {"name": "用户管理", "path": "/setting/user", "permission": "setting:user", "icon": "UserOutlined", "component": "SettingUser", "sort": 1, "status": "active", "parent_path": "/setting"},
    {"name": "角色管理", "path": "/setting/role", "permission": "setting:role", "icon": "TeamOutlined", "component": "SettingRole", "sort": 2, "status": "active", "parent_path": "/setting"},
]

MENUS_CONTINUED = [
    {"name": "权限管理", "path": "/setting/permission", "permission": "setting:permission", "icon": "SafetyCertificateOutlined", "component": "SettingPermission", "sort": 3, "status": "active", "parent_path": "/setting"},
    {"name": "菜单配置", "path": "/setting/menu", "permission": "setting:menu", "icon": "MenuOutlined", "component": "SettingMenu", "sort": 4, "status": "active", "parent_path": "/setting"},
    {"name": "系统配置", "path": "/setting/config", "permission": "setting:config", "icon": "ControlOutlined", "component": "SettingConfig", "sort": 5, "status": "active", "parent_path": "/setting"},
    {"name": "操作日志", "path": "/setting/operation-log", "permission": "setting:operation-log", "icon": "FileTextOutlined", "component": "SettingOperationLog", "sort": 6, "status": "active", "parent_path": "/setting"},
    {"name": "登录日志", "path": "/setting/login-log", "permission": "setting:login-log", "icon": "LoginOutlined", "component": "SettingLoginLog", "sort": 7, "status": "active", "parent_path": "/setting"},
]

ALL_MENUS = MENUS + MENUS_CONTINUED

SYSTEM_CONFIGS = [
    {"name": "站点名称", "key": "site.name", "value": "Max-Agent", "description": "站点名称"},
    {"name": "站点描述", "key": "site.description", "value": "AI Agent管理平台", "description": "站点描述"},
    {"name": "上传文件大小限制", "key": "upload.maxSize", "value": "10MB", "description": "上传文件最大尺寸"},
]


async def seed_roles(session: AsyncSession) -> dict[str, Role]:
    roles_map: dict[str, Role] = {}
    for data in ROLES:
        existing = await session.scalar(select(Role).where(Role.code == data["code"]))
        if existing:
            roles_map[data["code"]] = existing
            continue
        role = Role(**data)
        session.add(role)
        await session.flush()
        roles_map[data["code"]] = role
    return roles_map


async def seed_permissions(session: AsyncSession) -> list[Permission]:
    result: list[Permission] = []
    for data in PERMISSIONS:
        existing = await session.scalar(select(Permission).where(Permission.identifier == data["identifier"]))
        if existing:
            result.append(existing)
            continue
        perm = Permission(**data)
        session.add(perm)
        await session.flush()
        result.append(perm)
    return result


async def seed_users(session: AsyncSession, roles_map: dict[str, Role]) -> None:
    for data in USERS:
        existing = await session.scalar(
            select(User).where(
                or_(User.username == data["username"], User.email == data["email"])
            )
        )
        if existing:
            role = roles_map.get(data["role_code"])
            if role and role not in existing.roles:
                existing.roles.append(role)
                session.add(existing)
                await session.flush()
            continue
        user = User(
            username=data["username"],
            email=data["email"],
            hashed_password=password_hash.hash(data["password"]),
            is_active=True,
            is_superuser=data["is_superuser"],
            is_verified=True,
            avatar="",
            is_builtin=data["is_builtin"],
            must_change_password=data["must_change_password"],
            status=data["status"],
        )
        role = roles_map.get(data["role_code"])
        if role:
            user.roles.append(role)
        session.add(user)
        await session.flush()


async def seed_menus(session: AsyncSession) -> None:
    path_to_menu: dict[str, Menu] = {}
    for data in ALL_MENUS:
        existing = await session.scalar(select(Menu).where(Menu.path == data["path"]))
        if existing:
            path_to_menu[data["path"]] = existing
            continue
        parent_id = None
        if data["parent_path"] and data["parent_path"] in path_to_menu:
            parent_id = path_to_menu[data["parent_path"]].id
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
        session.add(menu)
        await session.flush()
        path_to_menu[data["path"]] = menu


async def seed_system_configs(session: AsyncSession) -> None:
    for data in SYSTEM_CONFIGS:
        existing = await session.scalar(select(SystemConfig).where(SystemConfig.key == data["key"]))
        if existing:
            continue
        config = SystemConfig(**data)
        session.add(config)
        await session.flush()


async def seed_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            roles_map = await seed_roles(session)
            all_permissions = await seed_permissions(session)
            await seed_users(session, roles_map)
            await seed_menus(session)
            await seed_system_configs(session)

            # 将所有权限绑定到 admin 角色
            admin_role = roles_map.get("admin")
            if admin_role:
                for perm in all_permissions:
                    if perm not in admin_role.permissions:
                        admin_role.permissions.append(perm)
                session.add(admin_role)
                await session.flush()


if __name__ == "__main__":
    asyncio.run(seed_initial_data())
    print("Seed completed.")
