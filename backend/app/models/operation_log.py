from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class OperationLog(TimestampMixin, Base):
    __tablename__ = "operation_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    operator_name: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ip: Mapped[str] = mapped_column(String(64), default="", nullable=False)
