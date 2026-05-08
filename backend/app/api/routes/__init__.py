from .auth import router as auth_router
from .configs import router as configs_router
from .health import router as health_router
from .logs import router as logs_router
from .menus import router as menus_router
from .permissions import router as permissions_router
from .providers import router as providers_router
from .roles import router as roles_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "configs_router",
    "health_router",
    "logs_router",
    "menus_router",
    "permissions_router",
    "providers_router",
    "roles_router",
    "users_router",
]
