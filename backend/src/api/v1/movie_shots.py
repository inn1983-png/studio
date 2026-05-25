"""
电影分镜相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.logging import get_logger
from src.models.user import User
from src.models.movie import MovieShot
from src.api.dependencies import get_current_user_required
from src.api.schemas.movie import StoryboardExtractRequest, KeyframeGenerateRequest, ShotUpdateRequest, MovieShotResponse

logger = get_logger(__name__)
router = APIRouter()

@router.post("/scripts/{script_id}/extract-shots", summary="从剧本提取分镜")
async def extract_shots(
    script_id: str,
    req: StoryboardExtractRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_extract_shots
    task = movie_extract_shots.delay(script_id, req.api_key_id, req.model)
    return {"task_id": task.id, "message": "分镜提取任务已提交"}

@router.post("/scripts/{script_id}/generate-keyframes", summary="生成剧本分镜关键帧")
async def generate_keyframes(
    script_id: str,
    req: KeyframeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_generate_keyframes
    task = movie_generate_keyframes.delay(script_id, req.api_key_id, req.model)
    return {"task_id": task.id, "message": "分镜关键帧生成任务已提交"}

@router.post("/shots/{shot_id}/generate-keyframe", summary="生成单个分镜关键帧")
async def generate_single_keyframe(
    shot_id: str,
    req: KeyframeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_generate_single_keyframe
    task = movie_generate_single_keyframe.delay(shot_id, req.api_key_id, req.model, req.prompt)
    return {"task_id": task.id, "message": "关键帧生成任务已提交"}

@router.post("/scenes/{scene_id}/extract-shots", summary="从单个场景重新提取分镜")
async def extract_single_scene_shots(
    scene_id: str,
    req: StoryboardExtractRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_extract_single_scene_shots
    task = movie_extract_single_scene_shots.delay(scene_id, req.api_key_id, req.model)
    return {"task_id": task.id, "message": "单场景分镜提取任务已提交"}

@router.put("/shots/{shot_id}", summary="更新分镜信息")
async def update_shot(
    shot_id: str,
    req: ShotUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.services.movie import MovieService
    movie_service = MovieService(db)
    updated = await movie_service.update_shot(shot_id, req.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Shot not found")
    return {"success": True, "message": "分镜已更新"}

@router.delete("/shots/{shot_id}", summary="删除分镜")
async def delete_shot(
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.models.movie import MovieShot
    shot = await db.get(MovieShot, shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")
    await db.delete(shot)
    await db.commit()
    return {"success": True, "message": "分镜已删除"}

@router.put("/shots/{shot_id}/order", summary="更新分镜顺序")
async def update_shot_order(
    shot_id: str,
    order_index: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.models.movie import MovieShot
    shot = await db.get(MovieShot, shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")
    shot.order_index = order_index
    await db.commit()
    return {"success": True, "message": "分镜顺序已更新"}

@router.get("/shots/by-chapter/{chapter_id}", summary="获取章节的所有分镜")
async def get_shots_by_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    stmt = select(MovieShot).where(MovieShot.chapter_id == chapter_id).order_by(MovieShot.order_index)
    result = await db.execute(stmt)
    shots = result.scalars().all()
    return [MovieShotResponse.model_validate(shot) for shot in shots]
