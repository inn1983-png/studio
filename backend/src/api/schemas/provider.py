from typing import Any, Dict, List, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class CreateProviderRequest(PydanticBaseModel):
    name: str = Field(..., max_length=100)
    provider_type: str = Field(...)
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    is_active: bool = True
    priority: int = 0
    max_concurrent: int = 1
    rate_limit_per_minute: Optional[int] = None


class UpdateProviderRequest(PydanticBaseModel):
    name: Optional[str] = None
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    max_concurrent: Optional[int] = None
    rate_limit_per_minute: Optional[int] = None


class ProviderResponse(PydanticBaseModel):
    id: str
    name: str
    provider_type: str
    endpoint_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    is_active: bool = True
    priority: int = 0
    max_concurrent: int = 1
    rate_limit_per_minute: Optional[int] = None
    health_status: str = "unknown"

    class Config:
        from_attributes = True
