from enum import Enum as PyEnum

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID

from src.models.base import BaseModel


class ProviderType(str, PyEnum):
    RUNNINGHUB = "runninghub"
    COMFYUI = "comfyui"
    LOCAL = "local"


class ProviderCapability(str, PyEnum):
    TEXT_TO_IMAGE = "text_to_image"
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    AUDIO_TO_VIDEO = "audio_to_video"


class Provider(BaseModel):
    __tablename__ = "providers"

    name = Column(String(100), nullable=False, comment="Provider名称")
    provider_type = Column(String(30), nullable=False, comment="Provider类型")
    endpoint_url = Column(String(500), nullable=True, comment="API端点")
    api_key_encrypted = Column(Text, nullable=True, comment="加密API密钥")
    config = Column(JSONB, nullable=True, default=dict, comment="配置参数")
    capabilities = Column(JSONB, nullable=True, default=list, comment="支持的能力列表")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")
    priority = Column(Integer, nullable=False, default=0, comment="优先级(越大越优先)")
    max_concurrent = Column(Integer, nullable=False, default=1, comment="最大并发数")
    rate_limit_per_minute = Column(Integer, nullable=True, comment="每分钟速率限制")
    last_health_check = Column(sa.DateTime(timezone=True), nullable=True)
    health_status = Column(String(20), nullable=False, default="unknown")
    user_id = Column(PostgreSQLUUID(as_uuid=True), nullable=True, comment="所属用户(空=全局)")


__all__ = [
    "Provider",
    "ProviderType",
    "ProviderCapability",
]
