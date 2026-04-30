from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class LoginLog(TimestampMixin, Base):
    __tablename__ = "login_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    username: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    ip: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    device: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)
