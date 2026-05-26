from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
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
from src.models.txtovideo import WorkflowStep, StepState
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


WORKFLOW_STEPS = [
    "script_adapt",
    "character_extract",
    "scene_extract",
    "prop_extract",
    "storyboard_generate",
    "image_prompt_generate",
    "video_prompt_generate",
    "quality_score",
    "export_package",
]

STEP_DEPENDENCIES = {
    "script_adapt": [],
    "character_extract": ["script_adapt"],
    "scene_extract": ["script_adapt"],
    "prop_extract": ["script_adapt"],
    "storyboard_generate": ["character_extract", "scene_extract", "prop_extract"],
    "image_prompt_generate": ["storyboard_generate"],
    "video_prompt_generate": ["image_prompt_generate"],
    "quality_score": ["video_prompt_generate"],
    "export_package": ["quality_score"],
}


@router.get("/{project_id}/steps")
async def get_workflow_steps(
    project_id: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.get_project(project_id, str(current_user.id))
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    result = await db.execute(
        select(WorkflowStep).filter(WorkflowStep.project_id == project_id)
    )
    steps = result.scalars().all()
    step_map = {s.step_name: s for s in steps}

    response = []
    for step_name in WORKFLOW_STEPS:
        step = step_map.get(step_name)
        if step:
            response.append(step.to_dict())
        else:
            response.append({
                "step_name": step_name,
                "status": StepState.PENDING.value,
                "retry_count": 0,
                "dependencies": STEP_DEPENDENCIES.get(step_name, []),
            })
    return {"steps": response, "dependencies": STEP_DEPENDENCIES}


@router.put("/{project_id}/steps/{step_name}")
async def update_workflow_step(
    project_id: str,
    step_name: str,
    body: Dict[str, Any],
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.get_project(project_id, str(current_user.id))
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if step_name not in WORKFLOW_STEPS:
        raise HTTPException(status_code=400, detail=f"无效步骤名: {step_name}")

    result = await db.execute(
        select(WorkflowStep).filter(
            WorkflowStep.project_id == project_id,
            WorkflowStep.step_name == step_name,
        )
    )
    step = result.scalar_one_or_none()

    if not step:
        step = WorkflowStep(
            project_id=project_id,
            step_name=step_name,
            status=StepState.PENDING.value,
        )
        db.add(step)

    new_status = body.get("status")
    if new_status:
        step.status = new_status
    if "error_message" in body:
        step.error_message = body["error_message"]
    if "input_hash" in body:
        step.input_hash = body["input_hash"]
    if "input_snapshot" in body:
        step.input_snapshot = body["input_snapshot"]
    if "output_snapshot" in body:
        step.output_snapshot = body["output_snapshot"]
    if "model_used" in body:
        step.model_used = body["model_used"]
    if "prompt_used" in body:
        step.prompt_used = body["prompt_used"]
    if new_status == StepState.RUNNING.value:
        step.retry_count = (step.retry_count or 0) + 1
    if new_status in (StepState.SUCCESS.value, StepState.FAILED.value):
        from datetime import datetime, timezone
        step.finished_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(step)
    return step.to_dict()


@router.post("/{project_id}/steps/{step_name}/retry")
async def retry_workflow_step(
    project_id: str,
    step_name: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.get_project(project_id, str(current_user.id))
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    result = await db.execute(
        select(WorkflowStep).filter(
            WorkflowStep.project_id == project_id,
            WorkflowStep.step_name == step_name,
        )
    )
    step = result.scalar_one_or_none()
    if not step:
        step = WorkflowStep(
            project_id=project_id,
            step_name=step_name,
            status=StepState.PENDING.value,
        )
        db.add(step)

    step.status = StepState.PENDING.value
    step.error_message = None
    step.finished_at = None
    await db.commit()
    await db.refresh(step)
    return step.to_dict()


@router.post("/{project_id}/steps/mark-stale")
async def mark_downstream_stale(
    project_id: str,
    body: Dict[str, Any],
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    service = TxtovideoProjectService(db)
    project = await service.get_project(project_id, str(current_user.id))
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    changed_step = body.get("step_name")
    if not changed_step:
        raise HTTPException(status_code=400, detail="缺少 step_name")

    downstream = _get_downstream_steps(changed_step)
    if not downstream:
        return {"marked_stale": []}

    result = await db.execute(
        select(WorkflowStep).filter(
            WorkflowStep.project_id == project_id,
            WorkflowStep.step_name.in_(downstream),
        )
    )
    steps = result.scalars().all()
    step_map = {s.step_name: s for s in steps}

    marked = []
    for step_name in downstream:
        step = step_map.get(step_name)
        if not step:
            step = WorkflowStep(
                project_id=project_id,
                step_name=step_name,
                status=StepState.STALE.value,
            )
            db.add(step)
        elif step.status in (StepState.SUCCESS.value, StepState.PENDING.value):
            step.status = StepState.STALE.value
        marked.append(step_name)

    await db.commit()
    return {"marked_stale": marked}


def _get_downstream_steps(step_name: str) -> List[str]:
    visited = set()
    queue = [step_name]
    while queue:
        current = queue.pop(0)
        for s, deps in STEP_DEPENDENCIES.items():
            if current in deps and s not in visited:
                visited.add(s)
                queue.append(s)
    return list(visited)
