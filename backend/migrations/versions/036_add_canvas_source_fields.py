"""add canvas_items source_type and source_ref columns

Revision ID: 036
Revises: 035
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa


revision = "036"
down_revision = "035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("canvas_items", sa.Column("source_type", sa.String(length=30), nullable=True, comment="来源类型: txtovideo/manual"))
    op.add_column("canvas_items", sa.Column("source_ref", sa.String(length=200), nullable=True, comment="来源引用: txtovideo://{project_id}/{step}/{asset_name}"))


def downgrade() -> None:
    op.drop_column("canvas_items", "source_ref")
    op.drop_column("canvas_items", "source_type")
