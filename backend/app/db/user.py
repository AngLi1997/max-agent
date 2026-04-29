from collections.abc import AsyncGenerator

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.db.session import AsyncSessionLocal
from app.models.user import User


async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    async with AsyncSessionLocal() as session:
        yield SQLAlchemyUserDatabase(session, User)
