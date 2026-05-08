"""add llm_provider and llm_model tables

Revision ID: 20260509_0003
Revises: 20260430_0002
Create Date: 2026-05-09 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260509_0003"
down_revision: Union[str, None] = "20260430_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "llm_provider",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("api_url", sa.String(length=500), nullable=False),
        sa.Column("api_key", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_llm_provider")),
    )
    op.create_table(
        "llm_model",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["llm_provider.id"], name=op.f("fk_llm_model_provider_id_llm_provider"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_llm_model")),
    )
    op.create_index(op.f("ix_llm_model_provider_id"), "llm_model", ["provider_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_llm_model_provider_id"), table_name="llm_model")
    op.drop_table("llm_model")
    op.drop_table("llm_provider")
