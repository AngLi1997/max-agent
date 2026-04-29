from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin
from app.models.role import user_roles


class User(SQLAlchemyBaseUserTable[int], TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
