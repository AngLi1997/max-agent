"""system settings rbac schema

Revision ID: 20260430_0002
Revises: 20260429_0001
Create Date: 2026-04-30 00:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260430_0002"
down_revision = "20260429_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("status", sa.String(length=20), nullable=False, server_default="active"))
    op.add_column("user", sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("user", sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("role", sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("menu", sa.Column("component", sa.String(length=255), nullable=False, server_default=""))

    op.create_table(
        "system_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=1000), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_system_config"),
    )
    op.create_index("ix_system_config_key", "system_config", ["key"], unique=True)

    op.create_table(
        "operation_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("operator_name", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("module", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("ip", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["operator_id"], ["user.id"], name="fk_operation_log_operator_id_user", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_operation_log"),
    )
    op.create_index("ix_operation_log_operator_id", "operation_log", ["operator_id"], unique=False)

    op.create_table(
        "login_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("ip", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("location", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("device", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_login_log_user_id_user", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_login_log"),
    )
    op.create_index("ix_login_log_user_id", "login_log", ["user_id"], unique=False)

    op.alter_column("user", "status", server_default=None)
    op.alter_column("user", "is_builtin", server_default=None)
    op.alter_column("user", "must_change_password", server_default=None)
    op.alter_column("role", "is_builtin", server_default=None)
    op.alter_column("menu", "component", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_login_log_user_id", table_name="login_log")
    op.drop_table("login_log")

    op.drop_index("ix_operation_log_operator_id", table_name="operation_log")
    op.drop_table("operation_log")

    op.drop_index("ix_system_config_key", table_name="system_config")
    op.drop_table("system_config")

    op.drop_column("menu", "component")
    op.drop_column("role", "is_builtin")
    op.drop_column("user", "must_change_password")
    op.drop_column("user", "is_builtin")
    op.drop_column("user", "status")
