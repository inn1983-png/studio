"""create txtovideo workflow steps table

Revision ID: 035
Revises: 034
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "035"
down_revision = "034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "txtovideo_workflow_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_name", sa.String(length=50), nullable=False, comment="步骤名称"),
        sa.Column("status", sa.String(length=30), nullable=False, comment="步骤状态"),
        sa.Column("input_hash", sa.String(length=64), nullable=True, comment="输入内容哈希"),
        sa.Column("input_snapshot", sa.Text(), nullable=True, comment="输入快照"),
        sa.Column("output_snapshot", sa.Text(), nullable=True, comment="输出快照"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="错误信息"),
        sa.Column("retry_count", sa.Integer(), nullable=False, comment="重试次数"),
        sa.Column("model_used", sa.String(length=100), nullable=True, comment="使用的模型"),
        sa.Column("prompt_used", sa.Text(), nullable=True, comment="使用的提示词"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True, comment="开始时间"),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True, comment="完成时间"),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "step_name", name="uq_txtovideo_step_project_name"),
    )
    op.create_index("ix_txtovideo_workflow_steps_project_id", "txtovideo_workflow_steps", ["project_id"])
    op.create_index("idx_txtovideo_step_status", "txtovideo_workflow_steps", ["status"])


def downgrade() -> None:
    op.drop_index("idx_txtovideo_step_status", table_name="txtovideo_workflow_steps")
    op.drop_index("ix_txtovideo_workflow_steps_project_id", table_name="txtovideo_workflow_steps")
    op.drop_table("txtovideo_workflow_steps")
