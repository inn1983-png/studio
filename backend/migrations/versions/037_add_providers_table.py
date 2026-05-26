"""add providers table

Revision ID: 037
Revises: 036
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "037"
down_revision = "036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "providers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("name", sa.String(length=100), nullable=False, comment="Provider名称"),
        sa.Column("provider_type", sa.String(length=30), nullable=False, comment="Provider类型"),
        sa.Column("endpoint_url", sa.String(length=500), nullable=True, comment="API端点"),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True, comment="加密API密钥"),
        sa.Column("config", postgresql.JSONB(), nullable=True, comment="配置参数"),
        sa.Column("capabilities", postgresql.JSONB(), nullable=True, comment="支持的能力列表"),
        sa.Column("is_active", sa.Boolean(), nullable=False, comment="是否启用"),
        sa.Column("priority", sa.Integer(), nullable=False, comment="优先级(越大越优先)"),
        sa.Column("max_concurrent", sa.Integer(), nullable=False, comment="最大并发数"),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True, comment="每分钟速率限制"),
        sa.Column("last_health_check", sa.DateTime(timezone=True), nullable=True),
        sa.Column("health_status", sa.String(length=20), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True, comment="所属用户(空=全局)"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_providers_user_id", "providers", ["user_id"])
    op.create_index("ix_providers_provider_type", "providers", ["provider_type"])


def downgrade() -> None:
    op.drop_index("ix_providers_provider_type", table_name="providers")
    op.drop_index("ix_providers_user_id", table_name="providers")
    op.drop_table("providers")
