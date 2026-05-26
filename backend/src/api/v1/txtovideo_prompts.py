"""Txtovideo prompt template API."""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user_required
from src.api.schemas.txtovideo_prompt import (
    TxtovideoPromptTemplateDetail,
    TxtovideoPromptTemplateSummary,
)
from src.core.exceptions import NotFoundError
from src.models.user import User
from src.prompts.txtovideo import (
    get_txtovideo_template,
    list_txtovideo_templates,
)

router = APIRouter()


@router.get(
    "/templates",
    response_model=list[TxtovideoPromptTemplateSummary],
)
async def list_templates(
    current_user: User = Depends(get_current_user_required),
) -> list[TxtovideoPromptTemplateSummary]:
    """List available Txtovideo prompt templates."""
    _ = current_user
    return [
        TxtovideoPromptTemplateSummary(
            template_id=template.template_id,
            name=template.name,
            version=template.version,
            category=template.category,
            filename=template.filename,
            variables=list(template.variables),
        )
        for template in list_txtovideo_templates()
    ]


@router.get(
    "/templates/{template_id}",
    response_model=TxtovideoPromptTemplateDetail,
)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user_required),
) -> TxtovideoPromptTemplateDetail:
    """Read one Txtovideo prompt template."""
    _ = current_user
    template = get_txtovideo_template(template_id)
    if template is None:
        raise NotFoundError(
            "提示词模板不存在",
            resource_type="txtovideo_prompt_template",
            resource_id=template_id,
        )

    return TxtovideoPromptTemplateDetail(
        template_id=template.template_id,
        name=template.name,
        version=template.version,
        category=template.category,
        filename=template.filename,
        variables=list(template.variables),
        content=template.content,
    )


__all__ = ["router"]

