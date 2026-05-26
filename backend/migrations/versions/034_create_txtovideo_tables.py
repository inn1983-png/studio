"""create txtovideo business tables

Revision ID: 034
Revises: 033
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "txtovideo_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True, comment="旧 projects 表桥接ID"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="短剧项目标题"),
        sa.Column("source_text", sa.Text(), nullable=False, comment="原文/文案"),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("era", sa.String(length=100), nullable=True, comment="时代背景"),
        sa.Column("style", sa.String(length=100), nullable=True, comment="视觉风格"),
        sa.Column("aspect_ratio", sa.String(length=20), nullable=False),
        sa.Column("target_platform", sa.String(length=20), nullable=False),
        sa.Column("workflow_mode", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_txtovideo_projects_project_id", "txtovideo_projects", ["project_id"])
    op.create_index("idx_txtovideo_project_mode", "txtovideo_projects", ["workflow_mode"])
    op.create_index("idx_txtovideo_project_platform", "txtovideo_projects", ["target_platform"])

    op.create_table(
        "txtovideo_script_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("script_text", sa.Text(), nullable=False),
        sa.Column("format_type", sa.String(length=50), nullable=False),
        sa.Column("prompt_used", sa.Text(), nullable=True),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "version", name="uq_txtovideo_script_project_version"),
    )
    op.create_index("ix_txtovideo_script_versions_project_id", "txtovideo_script_versions", ["project_id"])
    op.create_index("ix_txtovideo_script_versions_status", "txtovideo_script_versions", ["status"])

    op.create_table(
        "txtovideo_character_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("age", sa.String(length=50), nullable=True),
        sa.Column("identity", sa.String(length=200), nullable=True),
        sa.Column("appearance", sa.Text(), nullable=True),
        sa.Column("costume", sa.Text(), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("relation", sa.Text(), nullable=True),
        sa.Column("stable_prompt", sa.Text(), nullable=True),
        sa.Column("negative_prompt", sa.Text(), nullable=True),
        sa.Column("reference_image_url", sa.String(length=500), nullable=True),
        sa.Column("is_locked", sa.Integer(), nullable=False, comment="1=锁定角色设定"),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_txtovideo_character_project_name"),
    )
    op.create_index("ix_txtovideo_character_assets_project_id", "txtovideo_character_assets", ["project_id"])
    op.create_index("idx_txtovideo_character_gender", "txtovideo_character_assets", ["gender"])

    op.create_table(
        "txtovideo_scene_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("era", sa.String(length=100), nullable=True),
        sa.Column("location_type", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("lighting", sa.String(length=200), nullable=True),
        sa.Column("mood", sa.String(length=200), nullable=True),
        sa.Column("props", sa.JSON(), nullable=False),
        sa.Column("stable_prompt", sa.Text(), nullable=True),
        sa.Column("negative_prompt", sa.Text(), nullable=True),
        sa.Column("reference_image_url", sa.String(length=500), nullable=True),
        sa.Column("is_locked", sa.Integer(), nullable=False, comment="1=锁定场景设定"),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_txtovideo_scene_project_name"),
    )
    op.create_index("ix_txtovideo_scene_assets_project_id", "txtovideo_scene_assets", ["project_id"])

    op.create_table(
        "txtovideo_prop_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=True),
        sa.Column("era", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("visual_prompt", sa.Text(), nullable=True),
        sa.Column("negative_prompt", sa.Text(), nullable=True),
        sa.Column("must_appear", sa.Integer(), nullable=False, comment="1=必须出现在画面"),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_txtovideo_prop_project_name"),
    )
    op.create_index("ix_txtovideo_prop_assets_project_id", "txtovideo_prop_assets", ["project_id"])

    op.create_table(
        "txtovideo_storyboard_shots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=8), nullable=False, comment="两个汉字主题"),
        sa.Column("cap", sa.Text(), nullable=False, comment="原文连续片段"),
        sa.Column("desc_promopt", sa.Text(), nullable=False, comment="兼容字段: 画面描述"),
        sa.Column("characters", sa.JSON(), nullable=False),
        sa.Column("scene", sa.String(length=100), nullable=True),
        sa.Column("props", sa.JSON(), nullable=False),
        sa.Column("camera", sa.String(length=200), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "order_index", name="uq_txtovideo_shot_project_order"),
    )
    op.create_index("ix_txtovideo_storyboard_shots_project_id", "txtovideo_storyboard_shots", ["project_id"])
    op.create_index("ix_txtovideo_storyboard_shots_status", "txtovideo_storyboard_shots", ["status"])
    op.create_index("idx_txtovideo_shot_project_status", "txtovideo_storyboard_shots", ["project_id", "status"])

    op.create_table(
        "txtovideo_image_prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("positive_prompt", sa.Text(), nullable=False),
        sa.Column("negative_prompt", sa.Text(), nullable=False),
        sa.Column("model_hint", sa.String(length=100), nullable=True),
        sa.Column("aspect_ratio", sa.String(length=20), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("reference_assets", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shot_id"], ["txtovideo_storyboard_shots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shot_id", name="uq_txtovideo_image_prompt_shot"),
    )
    op.create_index("ix_txtovideo_image_prompts_project_id", "txtovideo_image_prompts", ["project_id"])
    op.create_index("ix_txtovideo_image_prompts_shot_id", "txtovideo_image_prompts", ["shot_id"])

    op.create_table(
        "txtovideo_video_prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("engine", sa.String(length=50), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("camera_motion", sa.Text(), nullable=True),
        sa.Column("character_motion", sa.Text(), nullable=True),
        sa.Column("scene_motion", sa.Text(), nullable=True),
        sa.Column("avoid", sa.Text(), nullable=True),
        sa.Column("first_frame_ref", sa.String(length=500), nullable=True),
        sa.Column("last_frame_ref", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shot_id"], ["txtovideo_storyboard_shots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shot_id", "engine", name="uq_txtovideo_video_prompt_shot_engine"),
    )
    op.create_index("ix_txtovideo_video_prompts_project_id", "txtovideo_video_prompts", ["project_id"])
    op.create_index("ix_txtovideo_video_prompts_shot_id", "txtovideo_video_prompts", ["shot_id"])
    op.create_index("idx_txtovideo_video_prompt_engine", "txtovideo_video_prompts", ["engine"])

    op.create_table(
        "txtovideo_quality_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("issues", sa.JSON(), nullable=False),
        sa.Column("suggestions", sa.JSON(), nullable=False),
        sa.Column("fixed_output", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_txtovideo_quality_reports_project_id", "txtovideo_quality_reports", ["project_id"])
    op.create_index("ix_txtovideo_quality_reports_target_type", "txtovideo_quality_reports", ["target_type"])
    op.create_index("ix_txtovideo_quality_reports_target_id", "txtovideo_quality_reports", ["target_id"])
    op.create_index("idx_txtovideo_quality_target", "txtovideo_quality_reports", ["target_type", "target_id"])

    op.create_table(
        "txtovideo_export_packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, comment="主键ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("package_type", sa.String(length=50), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("manifest", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["txtovideo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_txtovideo_export_packages_project_id", "txtovideo_export_packages", ["project_id"])
    op.create_index("idx_txtovideo_export_package_type", "txtovideo_export_packages", ["project_id", "package_type"])


def downgrade() -> None:
    op.drop_index("idx_txtovideo_export_package_type", table_name="txtovideo_export_packages")
    op.drop_index("ix_txtovideo_export_packages_project_id", table_name="txtovideo_export_packages")
    op.drop_table("txtovideo_export_packages")

    op.drop_index("idx_txtovideo_quality_target", table_name="txtovideo_quality_reports")
    op.drop_index("ix_txtovideo_quality_reports_target_id", table_name="txtovideo_quality_reports")
    op.drop_index("ix_txtovideo_quality_reports_target_type", table_name="txtovideo_quality_reports")
    op.drop_index("ix_txtovideo_quality_reports_project_id", table_name="txtovideo_quality_reports")
    op.drop_table("txtovideo_quality_reports")

    op.drop_index("idx_txtovideo_video_prompt_engine", table_name="txtovideo_video_prompts")
    op.drop_index("ix_txtovideo_video_prompts_shot_id", table_name="txtovideo_video_prompts")
    op.drop_index("ix_txtovideo_video_prompts_project_id", table_name="txtovideo_video_prompts")
    op.drop_table("txtovideo_video_prompts")

    op.drop_index("ix_txtovideo_image_prompts_shot_id", table_name="txtovideo_image_prompts")
    op.drop_index("ix_txtovideo_image_prompts_project_id", table_name="txtovideo_image_prompts")
    op.drop_table("txtovideo_image_prompts")

    op.drop_index("idx_txtovideo_shot_project_status", table_name="txtovideo_storyboard_shots")
    op.drop_index("ix_txtovideo_storyboard_shots_status", table_name="txtovideo_storyboard_shots")
    op.drop_index("ix_txtovideo_storyboard_shots_project_id", table_name="txtovideo_storyboard_shots")
    op.drop_table("txtovideo_storyboard_shots")

    op.drop_index("ix_txtovideo_prop_assets_project_id", table_name="txtovideo_prop_assets")
    op.drop_table("txtovideo_prop_assets")

    op.drop_index("ix_txtovideo_scene_assets_project_id", table_name="txtovideo_scene_assets")
    op.drop_table("txtovideo_scene_assets")

    op.drop_index("idx_txtovideo_character_gender", table_name="txtovideo_character_assets")
    op.drop_index("ix_txtovideo_character_assets_project_id", table_name="txtovideo_character_assets")
    op.drop_table("txtovideo_character_assets")

    op.drop_index("ix_txtovideo_script_versions_status", table_name="txtovideo_script_versions")
    op.drop_index("ix_txtovideo_script_versions_project_id", table_name="txtovideo_script_versions")
    op.drop_table("txtovideo_script_versions")

    op.drop_index("idx_txtovideo_project_platform", table_name="txtovideo_projects")
    op.drop_index("idx_txtovideo_project_mode", table_name="txtovideo_projects")
    op.drop_index("ix_txtovideo_projects_project_id", table_name="txtovideo_projects")
    op.drop_table("txtovideo_projects")
