"""
导出相关 API Schema
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JianYingExportResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="消息")
    download_url: str = Field("", description="下载URL")
    filename: str = Field("", description="文件名")


class VideoExportResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="消息")
    download_url: str = Field("", description="下载URL")
    filename: str = Field("", description="文件名")
    duration: Optional[int] = Field(None, description="视频时长（秒）")


class BatchExportRequest(BaseModel):
    chapter_ids: List[str] = Field(..., description="要导出的章节ID列表")


class BatchExportResponse(BaseModel):
    success: bool = Field(True, description="是否成功")
    message: str = Field("", description="消息")
    results: List[VideoExportResponse] = Field(default_factory=list, description="导出结果列表")


class TxtovideoExportRequest(BaseModel):
    package_name: str = Field("txtovideo-project_asset_package", description="包名")
    project_id: Optional[str] = Field(None, description="项目ID")
    source: Optional[Dict[str, Any]] = Field(None, description="原文信息")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="各步骤输出")
    prompt_used: Optional[Dict[str, Any]] = Field(None, description="使用的提示词记录")


class TxtovideoExportResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="消息")
    download_url: str = Field("", description="下载URL")
    filename: str = Field("", description="文件名")


__all__ = [
    "JianYingExportResponse",
    "VideoExportResponse",
    "BatchExportRequest",
    "BatchExportResponse",
    "TxtovideoExportRequest",
    "TxtovideoExportResponse",
]
