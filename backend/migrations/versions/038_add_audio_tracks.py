"""add audio tracks table

Revision ID: 038
Revises: 037
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "038"
down_revision = "037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "txtovideo_audio_tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("track_name", sa.String(length=200), nullable=False, comment="音轨名称"),
        sa.Column("audio_type", sa.String(length=30), nullable=False, comment="类型: bgm/voice/sfx"),
        sa.Column("file_url", sa.String(length=500), nullable=True, comment="音频文件URL"),
        sa.Column("duration_seconds", sa.Float(), nullable=True, comment="时长(秒)"),
        sa.Column("bpm", sa.Integer(), nullable=True, comment="BPM"),
        sa.Column("lyrics_text", sa.Text(), nullable=True, comment="歌词/台词文本"),
        sa.Column("lyrics_timestamps", postgresql.JSONB(), nullable=True, comment="时间戳对齐数据"),
        sa.Column("beat_markers", postgresql.JSONB(), nullable=True, comment="节拍标记"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, comment="是否主音轨"),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_txtovideo_audio_tracks_project_id", "txtovideo_audio_tracks", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_txtovideo_audio_tracks_project_id", table_name="txtovideo_audio_tracks")
    op.drop_table("txtovideo_audio_tracks")
