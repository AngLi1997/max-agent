from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.llm_model import LlmModel
from app.models.user import User
from app.schemas.common import ListResponse
from app.services.authorization import require_permission
from pydantic import BaseModel


class DashboardStats(BaseModel):
    userCount: int
    modelCount: int
    skillCount: int
    toolCount: int


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("dashboard:view")),
) -> DashboardStats:
    user_count = await session.scalar(select(func.count(User.id)))
    model_count = await session.scalar(select(func.count(LlmModel.id)))
    return DashboardStats(
        userCount=user_count or 0,
        modelCount=model_count or 0,
        skillCount=0,
        toolCount=0,
    )
