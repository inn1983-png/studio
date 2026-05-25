"""Add depends_on column to video_tasks table

Revision ID: 031
Revises: 030
Create Date: 2026-05-23 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '031'
down_revision = '030'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'video_tasks',
        sa.Column(
            'depends_on',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='[]',
            comment='依赖的任务ID列表（JSON数组）',
        )
    )


def downgrade():
    op.drop_column('video_tasks', 'depends_on')
