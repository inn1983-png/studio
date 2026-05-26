from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CreateTxtovideoProjectRequest(BaseModel):
    title: str = Field(..., max_length=200)
    source_text: str = Field("", description="原文/文案")
    source_type: str = Field("novel")
    era: Optional[str] = Field(None)
    style: Optional[str] = Field(None)
    aspect_ratio: str = Field("9:16")
    target_platform: str = Field("douyin")
    workflow_mode: str = Field("txtovideo")


class UpdateTxtovideoProjectRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    source_text: Optional[str] = Field(None)
    source_type: Optional[str] = Field(None)
    era: Optional[str] = Field(None)
    style: Optional[str] = Field(None)
    aspect_ratio: Optional[str] = Field(None)
    target_platform: Optional[str] = Field(None)
    workflow_mode: Optional[str] = Field(None)


class SaveDraftRequest(BaseModel):
    source: Optional[Dict[str, Any]] = Field(None)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    prompt_used: Optional[Dict[str, Any]] = Field(None)


class TxtovideoProjectResponse(BaseModel):
    id: str
    title: str
    source_text: str = ""
    source_type: str = "novel"
    era: Optional[str] = None
    style: Optional[str] = None
    aspect_ratio: str = "9:16"
    target_platform: str = "douyin"
    workflow_mode: str = "txtovideo"
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class TxtovideoProjectListResponse(BaseModel):
    items: List[TxtovideoProjectResponse] = Field(default_factory=list)
    total: int = 0


__all__ = [
    "CreateTxtovideoProjectRequest",
    "UpdateTxtovideoProjectRequest",
    "SaveDraftRequest",
    "TxtovideoProjectResponse",
    "TxtovideoProjectListResponse",
]
