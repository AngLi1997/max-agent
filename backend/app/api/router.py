from fastapi import APIRouter

from app.api.routes import (
    auth_router,
    configs_router,
    health_router,
    logs_router,
    menus_router,
    permissions_router,
    roles_router,
    users_router,
)

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
api_router.include_router(menus_router)
api_router.include_router(configs_router)
api_router.include_router(logs_router)
