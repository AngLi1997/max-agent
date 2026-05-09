from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class LlmModel(TimestampMixin, Base):
    __tablename__ = "llm_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("llm_provider.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)

    provider: Mapped["LlmProvider"] = relationship(back_populates="models")
