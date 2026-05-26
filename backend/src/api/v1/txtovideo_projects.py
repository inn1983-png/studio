from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user_required
from src.api.schemas.txtovideo import (
    CreateTxtovideoProjectRequest,
    SaveDraftRequest,
    TxtovideoProjectListResponse,
    TxtovideoProjectResponse,
    UpdateTxtovideoProjectRequest,
)
from src.core.database import get_db
from src.core.logging import get_logger
from src.models.user import User
from src.services.txtovideo_service import TxtovideoProjectService

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=TxtovideoProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_txtovideo_project(
    req: CreateTxtovideoProjectRequest,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.create_project(str(current_user.id), req.model_dump())
    return project


@router.get("", response_model=TxtovideoProjectListResponse)
async def list_txtovideo_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    items = await service.list_projects(str(current_user.id), skip=skip, limit=limit)
    return TxtovideoProjectListResponse(items=items, total=len(items))


@router.get("/{project_id}", response_model=TxtovideoProjectResponse)
async def get_txtovideo_project(
    project_id: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.get_project(project_id, str(current_user.id))
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.patch("/{project_id}", response_model=TxtovideoProjectResponse)
async def update_txtovideo_project(
    project_id: str,
    req: UpdateTxtovideoProjectRequest,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    project = await service.update_project(project_id, str(current_user.id), data)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_txtovideo_project(
    project_id: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    deleted = await service.delete_project(project_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="项目不存在")


@router.put("/{project_id}/draft", response_model=TxtovideoProjectResponse)
async def save_txtovideo_draft(
    project_id: str,
    req: SaveDraftRequest,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.save_draft(
        project_id, str(current_user.id), req.model_dump()
    )
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.get("/{project_id}/draft")
async def get_txtovideo_draft(
    project_id: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.get_project(project_id, str(current_user.id))
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    characters = [c.to_dict() for c in project.characters] if project.characters else []
    scenes = [s.to_dict() for s in project.scenes] if project.scenes else []
    props = [p.to_dict() for p in project.props] if project.props else []
    shots = [s.to_dict() for s in project.shots] if project.shots else []

    image_prompts = []
    video_prompts = []
    for shot in (project.shots or []):
        for ip in (shot.image_prompts or []):
            image_prompts.append(ip.to_dict())
        for vp in (shot.video_prompts or []):
            video_prompts.append(vp.to_dict())

    quality_reports = [q.to_dict() for q in project.quality_reports] if project.quality_reports else []

    script_text = ""
    if project.scripts:
        latest = max(project.scripts, key=lambda s: s.version)
        script_text = latest.script_text

    return {
        "id": str(project.id),
        "title": project.title,
        "source": {
            "text": project.source_text,
            "era": project.era,
            "style": project.style,
            "platform": project.target_platform,
            "aspectRatio": project.aspect_ratio,
            "sourceType": project.source_type,
        },
        "outputs": {
            "script": script_text,
            "characters": characters,
            "scenes": scenes,
            "props": props,
            "storyboard": shots,
            "imagePrompts": image_prompts,
            "videoPrompts": video_prompts,
            "quality": quality_reports[0] if quality_reports else {"status": "draft", "checks": []},
        },
    }


__all__ = ["router"]
