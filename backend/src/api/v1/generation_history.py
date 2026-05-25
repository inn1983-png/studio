"""
生成历史记录API - 统一管理所有类型的生成历史
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.generation_history_service import GenerationHistoryService
from src.models.movie import GenerationType
from src.models.user import User
from src.core.security import get_current_user_required
from src.utils.storage import get_storage_client
from src.api.schemas.generation_history import GenerationHistoryResponse, SelectHistoryRequest
from datetime import timedelta

router = APIRouter(prefix="/generation-history", tags=["generation-history"])

# ============================================================
# 通用端点
# ============================================================

@router.get("/{resource_type}/{resource_id}", response_model=List[GenerationHistoryResponse])
async def get_generation_history(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    获取资源的生成历史记录
    
    Args:
        resource_type: 资源类型 (scene_image/shot_keyframe/character_avatar/transition_video)
        resource_id: 资源ID
    """
    service = GenerationHistoryService(db)
    histories = await service.get_history(resource_type, resource_id)
    
    # 签名URL
    storage_client = await get_storage_client()
    results = []
    
    for history in histories:
        # 签名result_url
        signed_url = history.result_url
        if history.result_url and not history.result_url.startswith("http"):
            signed_url = storage_client.get_presigned_url(
                history.result_url,
                expires=timedelta(hours=24)
            )
        
        results.append(GenerationHistoryResponse(
            id=str(history.id),
            resource_type=history.resource_type,
            resource_id=str(history.resource_id),
            media_type=history.media_type,
            result_url=signed_url,
            prompt=history.prompt,
            model=history.model,
            is_selected=history.is_selected,
            created_at=history.created_at
        ))
    
    return results


@router.post("/{resource_type}/{resource_id}/select")
async def select_generation_history(
    resource_type: str,
    resource_id: str,
    request: SelectHistoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    选择特定的历史记录作为当前使用的版本
    
    Args:
        resource_type: 资源类型
        resource_id: 资源ID
        request: 包含history_id的请求体
    """
    service = GenerationHistoryService(db)
    
    try:
        history = await service.select_history(
            request.history_id,
            resource_type,
            resource_id
        )
        
        # 更新对应资源的URL字段
        await _update_resource_url(db, resource_type, resource_id, history.result_url)
        
        await db.commit()
        
        return {
            "success": True,
            "message": "历史记录已选中",
            "history_id": str(history.id),
            "result_url": history.result_url
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"选择历史记录失败: {str(e)}")


async def _update_resource_url(db: AsyncSession, resource_type: str, resource_id: str, url: str):
    """更新资源的URL字段"""
    from src.models.movie import MovieScene, MovieShot, MovieCharacter, MovieShotTransition
    
    if resource_type == GenerationType.SCENE_IMAGE:
        scene = await db.get(MovieScene, resource_id)
        if scene:
            scene.scene_image_url = url
    elif resource_type == GenerationType.SHOT_KEYFRAME:
        shot = await db.get(MovieShot, resource_id)
        if shot:
            shot.keyframe_url = url
    elif resource_type == GenerationType.CHARACTER_AVATAR:
        character = await db.get(MovieCharacter, resource_id)
        if character:
            character.avatar_url = url
    elif resource_type == GenerationType.TRANSITION_VIDEO:
        transition = await db.get(MovieShotTransition, resource_id)
        if transition:
            transition.video_url = url


# ============================================================
# 便捷端点（为特定资源类型提供简化的API）
# ============================================================

@router.get("/scenes/{scene_id}/images", response_model=List[GenerationHistoryResponse])
async def get_scene_image_history(
    scene_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """获取场景图历史记录"""
    return await get_generation_history(GenerationType.SCENE_IMAGE, scene_id, db, current_user)


@router.post("/scenes/{scene_id}/select-image")
async def select_scene_image(
    scene_id: str,
    request: SelectHistoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """选择场景图"""
    return await select_generation_history(GenerationType.SCENE_IMAGE, scene_id, request, db, current_user)


@router.get("/shots/{shot_id}/keyframes", response_model=List[GenerationHistoryResponse])
async def get_keyframe_history(
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """获取关键帧历史记录"""
    return await get_generation_history(GenerationType.SHOT_KEYFRAME, shot_id, db, current_user)


@router.post("/shots/{shot_id}/select-keyframe")
async def select_keyframe(
    shot_id: str,
    request: SelectHistoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """选择关键帧"""
    return await select_generation_history(GenerationType.SHOT_KEYFRAME, shot_id, request, db, current_user)


@router.get("/characters/{character_id}/avatars", response_model=List[GenerationHistoryResponse])
async def get_avatar_history(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """获取角色头像历史记录"""
    return await get_generation_history(GenerationType.CHARACTER_AVATAR, character_id, db, current_user)


@router.post("/characters/{character_id}/select-avatar")
async def select_avatar(
    character_id: str,
    request: SelectHistoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """选择角色头像"""
    return await select_generation_history(GenerationType.CHARACTER_AVATAR, character_id, request, db, current_user)


@router.get("/transitions/{transition_id}/videos", response_model=List[GenerationHistoryResponse])
async def get_transition_video_history(
    transition_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """获取过渡视频历史记录"""
    return await get_generation_history(GenerationType.TRANSITION_VIDEO, transition_id, db, current_user)


@router.post("/transitions/{transition_id}/select-video")
async def select_transition_video(
    transition_id: str,
    request: SelectHistoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """选择过渡视频"""
    return await select_generation_history(GenerationType.TRANSITION_VIDEO, transition_id, request, db, current_user)

