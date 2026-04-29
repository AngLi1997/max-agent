import asyncio

from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.menu import Menu
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User

password_hash = PasswordHash.recommended()


ROLES = [
    {"name": "超级管理员", "code": "admin", "description": "拥有所有权限", "status": "active"},
    {"name": "编辑", "code": "editor", "description": "可编辑内容", "status": "active"},
    {"name": "访客", "code": "viewer", "description": "只读权限", "status": "inactive"},
]

PERMISSIONS = [
    {"name": "用户查看", "identifier": "user:read", "type": "菜单", "status": "active"},
    {"name": "用户新增", "identifier": "user:create", "type": "按钮", "status": "active"},
    {"name": "模型查看", "identifier": "model:read", "type": "API", "status": "active"},
]

USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "admin123", "is_superuser": True, "role_code": "admin"},
    {"username": "editor", "email": "editor@example.com", "password": "admin123", "is_superuser": False, "role_code": "editor"},
    {"username": "viewer", "email": "viewer@example.com", "password": "admin123", "is_superuser": False, "role_code": "viewer"},
]

MENUS = [
    {"name": "仪表盘", "path": "/dashboard", "permission": "dashboard:view", "icon": "DashboardOutlined", "sort": 1, "status": "active", "parent_path": None},
    {"name": "模型管理", "path": "/model", "permission": "model:view", "icon": "RobotOutlined", "sort": 2, "status": "active", "parent_path": None},
    {"name": "Skills管理", "path": "/skill", "permission": "skill:view", "icon": "ThunderboltOutlined", "sort": 3, "status": "active", "parent_path": None},
    {"name": "工具管理", "path": "/tool", "permission": "tool:view", "icon": "ToolOutlined", "sort": 4, "status": "active", "parent_path": None},
    {"name": "系统设置", "path": "/setting", "permission": "setting:view", "icon": "SettingOutlined", "sort": 5, "status": "active", "parent_path": None},
    {"name": "用户管理", "path": "/setting/user", "permission": "setting:user", "icon": "UserOutlined", "sort": 1, "status": "active", "parent_path": "/setting"},
    {"name": "角色管理", "path": "/setting/role", "permission": "setting:role", "icon": "TeamOutlined", "sort": 2, "status": "active", "parent_path": "/setting"},
]

MENUS_CONTINUED = [
    {"name": "权限管理", "path": "/setting/permission", "permission": "setting:permission", "icon": "SafetyCertificateOutlined", "sort": 3, "status": "active", "parent_path": "/setting"},
    {"name": "菜单配置", "path": "/setting/menu", "permission": "setting:menu", "icon": "MenuOutlined", "sort": 4, "status": "active", "parent_path": "/setting"},
    {"name": "系统配置", "path": "/setting/config", "permission": "setting:config", "icon": "ControlOutlined", "sort": 5, "status": "active", "parent_path": "/setting"},
    {"name": "操作日志", "path": "/setting/operation-log", "permission": "setting:operation-log", "icon": "FileTextOutlined", "sort": 6, "status": "active", "parent_path": "/setting"},
    {"name": "登录日志", "path": "/setting/login-log", "permission": "setting:login-log", "icon": "LoginOutlined", "sort": 7, "status": "active", "parent_path": "/setting"},
]

ALL_MENUS = MENUS + MENUS_CONTINUED


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
            sort=data["sort"],
            status=data["status"],
            parent_id=parent_id,
        )
        session.add(menu)
        await session.flush()
        path_to_menu[data["path"]] = menu


async def seed_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            roles_map = await seed_roles(session)
            await seed_permissions(session)
            await seed_users(session, roles_map)
            await seed_menus(session)


if __name__ == "__main__":
    asyncio.run(seed_initial_data())
    print("Seed completed.")
