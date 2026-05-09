from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class LlmProvider(TimestampMixin, Base):
    __tablename__ = "llm_provider"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # "openai" | "ollama"
    api_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    models: Mapped[list["LlmModel"]] = relationship(back_populates="provider", cascade="all, delete-orphan", passive_deletes=True)
