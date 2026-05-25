"""Txtovideo prompt template schemas."""

from pydantic import BaseModel, Field


class TxtovideoPromptTemplateSummary(BaseModel):
    """Prompt template summary for list views."""

    template_id: str = Field(..., description="模板 ID")
    name: str = Field(..., description="模板名称")
    version: str = Field(..., description="模板版本")
    category: str = Field(..., description="模板分类")
    filename: str = Field(..., description="模板文件名")
    variables: list[str] = Field(default_factory=list, description="支持变量")


class TxtovideoPromptTemplateDetail(TxtovideoPromptTemplateSummary):
    """Prompt template detail including content."""

    content: str = Field(..., description="模板正文")


__all__ = [
    "TxtovideoPromptTemplateSummary",
    "TxtovideoPromptTemplateDetail",
]

