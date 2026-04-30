from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin
from app.models.role import user_roles


class User(SQLAlchemyBaseUserTable[int], TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
