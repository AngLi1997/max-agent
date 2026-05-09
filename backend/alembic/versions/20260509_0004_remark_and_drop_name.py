"""add remark to llm_model, drop name from llm_provider

Revision ID: 20260509_0004
Revises: 20260509_0003
Create Date: 2026-05-09 01:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260509_0004"
down_revision: Union[str, None] = "20260509_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("llm_model", sa.Column("remark", sa.String(length=500), nullable=True))
    op.drop_column("llm_provider", "name")


def downgrade() -> None:
    op.add_column("llm_provider", sa.Column("name", sa.String(length=100), nullable=False, server_default=""))
    op.alter_column("llm_provider", "name", server_default=None)
    op.drop_column("llm_model", "remark")
