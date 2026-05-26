"""
Txtovideo Studio dedicated business models.
"""

from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class SourceType(str, Enum):
    NOVEL = "novel"
    SHORT_TEXT = "short_text"
    SCRIPT = "script"


class TargetPlatform(str, Enum):
    DOUYIN = "douyin"
    SHIPINHAO = "shipinhao"
    BILIBILI = "bilibili"
    CUSTOM = "custom"


class TxtovideoWorkflowMode(str, Enum):
    TXTOVIDEO = "txtovideo"


class TxtovideoStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"


class QualityTargetType(str, Enum):
    SCRIPT = "script"
    CHARACTER = "character"
    SCENE = "scene"
    STORYBOARD = "storyboard"
    IMAGE_PROMPT = "image_prompt"
    VIDEO_PROMPT = "video_prompt"


class ShortDramaProject(BaseModel):
    """Txtovideo short drama project root.

    project_id is an optional bridge to the legacy projects table. Child tables
    use their own project_id to point to this table's id.
    """

    __tablename__ = "txtovideo_projects"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
        comment="旧 projects 表桥接ID",
    )
    title = Column(String(200), nullable=False, comment="短剧项目标题")
    source_text = Column(Text, nullable=False, default="", comment="原文/文案")
    source_type = Column(String(20), nullable=False, default=SourceType.NOVEL.value)
    era = Column(String(100), nullable=True, comment="时代背景")
    style = Column(String(100), nullable=True, comment="视觉风格")
    aspect_ratio = Column(String(20), nullable=False, default="9:16")
    target_platform = Column(String(20), nullable=False, default=TargetPlatform.DOUYIN.value)
    workflow_mode = Column(String(40), nullable=False, default=TxtovideoWorkflowMode.TXTOVIDEO.value)

    legacy_project = relationship("Project")
    scripts = relationship("ScriptVersion", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("CharacterAsset", back_populates="project", cascade="all, delete-orphan")
    scenes = relationship("SceneAsset", back_populates="project", cascade="all, delete-orphan")
    props = relationship("PropAsset", back_populates="project", cascade="all, delete-orphan")
    shots = relationship("StoryboardShot", back_populates="project", cascade="all, delete-orphan")
    image_prompts = relationship("ImagePrompt", back_populates="project", cascade="all, delete-orphan")
    video_prompts = relationship("VideoPrompt", back_populates="project", cascade="all, delete-orphan")
    quality_reports = relationship("QualityReport", back_populates="project", cascade="all, delete-orphan")
    export_packages = relationship("ExportPackage", back_populates="project", cascade="all, delete-orphan")
    workflow_steps = relationship("WorkflowStep", back_populates="project", cascade="all, delete-orphan")
    audio_tracks = relationship("AudioTrack", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_txtovideo_project_mode", "workflow_mode"),
        Index("idx_txtovideo_project_platform", "target_platform"),
    )


class ScriptVersion(BaseModel):
    __tablename__ = "txtovideo_script_versions"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(Integer, nullable=False, default=1)
    script_text = Column(Text, nullable=False, default="")
    format_type = Column(String(50), nullable=False, default="os_dialogue_blank")
    prompt_used = Column(Text, nullable=True)
    model_used = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default=TxtovideoStatus.DRAFT.value, index=True)

    project = relationship("ShortDramaProject", back_populates="scripts")

    __table_args__ = (
        UniqueConstraint("project_id", "version", name="uq_txtovideo_script_project_version"),
    )


class CharacterAsset(BaseModel):
    __tablename__ = "txtovideo_character_assets"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(String(50), nullable=True)
    identity = Column(String(200), nullable=True)
    appearance = Column(Text, nullable=True)
    costume = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    relation = Column(Text, nullable=True)
    stable_prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    reference_image_url = Column(String(500), nullable=True)
    is_locked = Column(Integer, nullable=False, default=0, comment="1=锁定角色设定")

    project = relationship("ShortDramaProject", back_populates="characters")

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_txtovideo_character_project_name"),
        Index("idx_txtovideo_character_gender", "gender"),
    )


class SceneAsset(BaseModel):
    __tablename__ = "txtovideo_scene_assets"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    era = Column(String(100), nullable=True)
    location_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    lighting = Column(String(200), nullable=True)
    mood = Column(String(200), nullable=True)
    props = Column(JSON, nullable=False, default=list)
    stable_prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    reference_image_url = Column(String(500), nullable=True)
    is_locked = Column(Integer, nullable=False, default=0, comment="1=锁定场景设定")

    project = relationship("ShortDramaProject", back_populates="scenes")

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_txtovideo_scene_project_name"),
    )


class PropAsset(BaseModel):
    __tablename__ = "txtovideo_prop_assets"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=True)
    era = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    visual_prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    must_appear = Column(Integer, nullable=False, default=0, comment="1=必须出现在画面")

    project = relationship("ShortDramaProject", back_populates="props")

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_txtovideo_prop_project_name"),
    )


class StoryboardShot(BaseModel):
    __tablename__ = "txtovideo_storyboard_shots"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_index = Column(Integer, nullable=False)
    theme = Column(String(8), nullable=False, comment="两个汉字主题")
    cap = Column(Text, nullable=False, comment="原文连续片段")
    desc_promopt = Column(Text, nullable=False, comment="兼容字段: 画面描述")
    characters = Column(JSON, nullable=False, default=list)
    scene = Column(String(100), nullable=True)
    props = Column(JSON, nullable=False, default=list)
    camera = Column(String(200), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default=TxtovideoStatus.DRAFT.value, index=True)

    project = relationship("ShortDramaProject", back_populates="shots")
    image_prompts = relationship("ImagePrompt", back_populates="shot", cascade="all, delete-orphan")
    video_prompts = relationship("VideoPrompt", back_populates="shot", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", "order_index", name="uq_txtovideo_shot_project_order"),
        Index("idx_txtovideo_shot_project_status", "project_id", "status"),
    )


class ImagePrompt(BaseModel):
    __tablename__ = "txtovideo_image_prompts"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shot_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_storyboard_shots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    positive_prompt = Column(Text, nullable=False, default="")
    negative_prompt = Column(Text, nullable=False, default="")
    model_hint = Column(String(100), nullable=True)
    aspect_ratio = Column(String(20), nullable=False, default="9:16")
    seed = Column(Integer, nullable=True)
    reference_assets = Column(JSON, nullable=False, default=list)

    project = relationship("ShortDramaProject", back_populates="image_prompts")
    shot = relationship("StoryboardShot", back_populates="image_prompts")

    __table_args__ = (
        UniqueConstraint("shot_id", name="uq_txtovideo_image_prompt_shot"),
    )


class VideoPrompt(BaseModel):
    __tablename__ = "txtovideo_video_prompts"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shot_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_storyboard_shots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    engine = Column(String(50), nullable=False, default="ltx")
    duration_seconds = Column(Float, nullable=True)
    prompt = Column(Text, nullable=False, default="")
    camera_motion = Column(Text, nullable=True)
    character_motion = Column(Text, nullable=True)
    scene_motion = Column(Text, nullable=True)
    avoid = Column(Text, nullable=True)
    first_frame_ref = Column(String(500), nullable=True)
    last_frame_ref = Column(String(500), nullable=True)

    project = relationship("ShortDramaProject", back_populates="video_prompts")
    shot = relationship("StoryboardShot", back_populates="video_prompts")

    __table_args__ = (
        UniqueConstraint("shot_id", "engine", name="uq_txtovideo_video_prompt_shot_engine"),
        Index("idx_txtovideo_video_prompt_engine", "engine"),
    )


class QualityReport(BaseModel):
    __tablename__ = "txtovideo_quality_reports"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type = Column(String(50), nullable=False, index=True)
    target_id = Column(PostgreSQLUUID(as_uuid=True), nullable=True, index=True)
    score = Column(Float, nullable=False, default=0)
    issues = Column(JSON, nullable=False, default=list)
    suggestions = Column(JSON, nullable=False, default=list)
    fixed_output = Column(JSON, nullable=True)

    project = relationship("ShortDramaProject", back_populates="quality_reports")

    __table_args__ = (
        Index("idx_txtovideo_quality_target", "target_type", "target_id"),
    )


class AudioTrack(BaseModel):
    __tablename__ = "txtovideo_audio_tracks"

    project_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("txtovideo_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    track_name = Column(String(200), nullable=False, comment="音轨名称")
    audio_type = Column(String(30), nullable=False, default="bgm", comment="类型: bgm/voice/sfx")
    file_url = Column(String(500), nullable=True, comment="音频文件URL")
    duration_seconds = Column(Float, nullable=True, comment="时长(秒)")
    bpm = Column(Integer, nullable=True, comment="BPM")
    lyrics_text = Column(Text, nullable=True, comment="歌词/台词文本")
    lyrics_timestamps = Column(JSON, nullable=True, default=list, comment="时间戳对齐数据")
    beat_markers = Column(JSON, nullable=True, default=list, comment="节拍标记")
    is_primary = Column(Boolean, nullable=False, default=False, comment="是否主音轨")

    project = relationship("ShortDramaProject", back_populates="audio_tracks")


class StepState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_DEPENDENCY = "waiting_dependency"
    STALE = "stale"


class WorkflowStep(BaseModel):
    __tablename__ = "txtovideo_workflow_steps"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_name = Column(String(50), nullable=False, comment="步骤名称")
    status = Column(String(30), nullable=False, default=StepState.PENDING.value, comment="步骤状态")
    input_hash = Column(String(64), nullable=True, comment="输入内容哈希")
    input_snapshot = Column(Text, nullable=True, comment="输入快照")
    output_snapshot = Column(Text, nullable=True, comment="输出快照")
    error_message = Column(Text, nullable=True, comment="错误信息")
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")
    model_used = Column(String(100), nullable=True, comment="使用的模型")
    prompt_used = Column(Text, nullable=True, comment="使用的提示词")
    started_at = Column(None, nullable=True, comment="开始时间")
    finished_at = Column(None, nullable=True, comment="完成时间")

    project = relationship("ShortDramaProject", back_populates="workflow_steps")

    __table_args__ = (
        UniqueConstraint("project_id", "step_name", name="uq_txtovideo_step_project_name"),
        Index("idx_txtovideo_step_status", "status"),
    )


class ExportPackage(BaseModel):
    __tablename__ = "txtovideo_export_packages"

    project_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("txtovideo_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    package_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    manifest = Column(JSON, nullable=False, default=dict)

    project = relationship("ShortDramaProject", back_populates="export_packages")

    __table_args__ = (
        Index("idx_txtovideo_export_package_type", "project_id", "package_type"),
    )


__all__ = [
    "AudioTrack",
    "CharacterAsset",
    "ExportPackage",
    "ImagePrompt",
    "PropAsset",
    "QualityReport",
    "QualityTargetType",
    "SceneAsset",
    "ScriptVersion",
    "ShortDramaProject",
    "SourceType",
    "StepState",
    "StoryboardShot",
    "TargetPlatform",
    "TxtovideoStatus",
    "TxtovideoWorkflowMode",
    "VideoPrompt",
    "WorkflowStep",
]
