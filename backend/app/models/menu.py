from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Menu(TimestampMixin, Base):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    permission: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    icon: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    sort: Mapped[int] = mapped_column(default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menu.id", ondelete="CASCADE"), nullable=True)

    parent = relationship("Menu", remote_side=lambda: [Menu.id], back_populates="children")
    children = relationship(
        "Menu",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="Menu.sort",
    )
