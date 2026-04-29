from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.login_log import LoginLog
from app.models.operation_log import OperationLog
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.log import LoginLogItem, OperationLogItem
from app.services.auth import current_active_user

router = APIRouter(tags=["logs"])


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@router.get("/operation-logs", response_model=ListResponse[OperationLogItem])
async def list_operation_logs(
    operator: str | None = None,
    module: str | None = None,
    startTime: str | None = None,
    endTime: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(current_active_user),
) -> ListResponse[OperationLogItem]:
    q = select(OperationLog)
    if operator:
        q = q.where(OperationLog.operator_name.ilike(f"%{operator}%"))
    if module:
        q = q.where(OperationLog.module.ilike(f"%{module}%"))

    start_dt = _parse_datetime(startTime)
    end_dt = _parse_datetime(endTime)
    if start_dt and end_dt:
        q = q.where(and_(OperationLog.created_at >= start_dt, OperationLog.created_at <= end_dt))
    elif start_dt:
        q = q.where(OperationLog.created_at >= start_dt)
    elif end_dt:
        q = q.where(OperationLog.created_at <= end_dt)

    rows = (await session.scalars(q.order_by(OperationLog.created_at.desc()))).all()
    items = [
        OperationLogItem(
            id=row.id,
            operator=row.operator_name,
            module=row.module,
            action=row.action,
            method=row.method,
            result=row.result,
            time=row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            detail=row.detail,
        )
        for row in rows
    ]
    return ListResponse(list=items, total=len(items))


@router.get("/login-logs", response_model=ListResponse[LoginLogItem])
async def list_login_logs(
    username: str | None = None,
    result: str | None = None,
    startTime: str | None = None,
    endTime: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(current_active_user),
) -> ListResponse[LoginLogItem]:
    q = select(LoginLog)
    if username:
        q = q.where(LoginLog.username.ilike(f"%{username}%"))
    if result:
        q = q.where(LoginLog.result == result)

    start_dt = _parse_datetime(startTime)
    end_dt = _parse_datetime(endTime)
    if start_dt and end_dt:
        q = q.where(and_(LoginLog.created_at >= start_dt, LoginLog.created_at <= end_dt))
    elif start_dt:
        q = q.where(LoginLog.created_at >= start_dt)
    elif end_dt:
        q = q.where(LoginLog.created_at <= end_dt)

    rows = (await session.scalars(q.order_by(LoginLog.created_at.desc()))).all()
    items = [
        LoginLogItem(
            id=row.id,
            username=row.username,
            ip=row.ip,
            location=row.location,
            device=row.device,
            result=row.result,
            time=row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            detail=row.detail,
        )
        for row in rows
    ]
    return ListResponse(list=items, total=len(items))
