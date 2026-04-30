from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_log import LoginLog
from app.models.operation_log import OperationLog
from app.utils.request import describe_ip_location


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
            location=describe_ip_location(ip),
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
