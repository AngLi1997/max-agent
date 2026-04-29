from sqlalchemy import Boolean, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
)


class Role(TimestampMixin, Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
