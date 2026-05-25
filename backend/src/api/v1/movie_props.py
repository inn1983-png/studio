"""
电影道具相关API路由
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.logging import get_logger
from src.models.user import User
from src.api.dependencies import get_current_user_required
from src.api.schemas.movie import (
    MoviePropBase,
    PropExtractRequest,
    PropUpdateRequest,
    PropGenerateRequest,
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/chapters/{chapter_id}/extract-props", summary="从章节提取道具")
async def extract_props(
    chapter_id: str,
    req: PropExtractRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_extract_props
    task = movie_extract_props.delay(chapter_id, req.api_key_id, req.model)
    return {"task_id": task.id, "message": "道具提取任务已提交"}


@router.get("/projects/{project_id}/props")
async def list_props(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.services.movie import MovieService

    movie_service = MovieService(db)
    props = await movie_service.list_props(project_id)

    result = [MoviePropBase.from_orm_with_signed_urls(prop) for prop in props]
    return {"props": [r.model_dump() for r in result]}


@router.put("/props/{prop_id}", response_model=MoviePropBase)
async def update_prop(
    prop_id: str,
    req: PropUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.services.movie import MovieService

    movie_service = MovieService(db)
    updated_prop = await movie_service.update_prop(prop_id, req.dict(exclude_unset=True))
    if not updated_prop:
        raise HTTPException(status_code=404, detail="Prop not found")
    return MoviePropBase.from_orm_with_signed_urls(updated_prop)


@router.delete("/props/{prop_id}", summary="删除道具")
async def delete_prop(
    prop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.services.movie import MovieService

    movie_service = MovieService(db)
    success = await movie_service.delete_prop(prop_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prop not found")
    return {"success": True, "message": "道具已删除"}


@router.post("/props/{prop_id}/generate", summary="生成道具图")
async def generate_prop_image(
    prop_id: str,
    api_key_id: str = Form(...),
    model: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    style: Optional[str] = Form("cinematic"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_generate_prop_image

    task = movie_generate_prop_image.delay(prop_id, api_key_id, model, prompt, style)
    return {"task_id": task.id, "message": "道具图生成任务已提交"}


@router.post("/projects/{project_id}/props/batch-generate", summary="批量生成道具图")
async def batch_generate_prop_images(
    project_id: str,
    req: PropExtractRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.tasks.movie import movie_batch_generate_prop_images

    task = movie_batch_generate_prop_images.delay(project_id, req.api_key_id, req.model)
    return {"task_id": task.id, "message": "批量生成道具图任务已提交"}


@router.post("/props/{prop_id}/reference-images", summary="上传道具参考图")
async def upload_reference_image(
    prop_id: str,
    file: UploadFile = File(..., description="参考图片"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.models.movie import MovieProp
    from src.models.project import Project

    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    prop = await db.get(MovieProp, prop_id)
    if not prop:
        raise HTTPException(status_code=404, detail="道具不存在")

    project = await db.get(Project, prop.project_id)

    from src.utils.storage import get_storage_client

    storage_client = await get_storage_client()

    upload_result = await storage_client.upload_file(
        user_id=str(project.owner_id),
        file=file,
        metadata={"prop_id": str(prop.id), "type": "reference_image"}
    )
    object_key = upload_result["object_key"]

    refs = list(prop.reference_images) if prop.reference_images else []
    if object_key not in refs:
        refs.append(object_key)
        prop.reference_images = refs
        await db.commit()

    return {"success": True, "reference_image_url": object_key, "message": "参考图上传成功"}


@router.delete("/props/{prop_id}/reference-images/{image_index}", summary="删除道具参考图")
async def delete_reference_image(
    prop_id: str,
    image_index: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    from src.models.movie import MovieProp
    from src.utils.storage import get_storage_client

    prop = await db.get(MovieProp, prop_id)
    if not prop:
        raise HTTPException(status_code=404, detail="道具不存在")

    refs = list(prop.reference_images) if prop.reference_images else []
    if image_index < 0 or image_index >= len(refs):
        raise HTTPException(status_code=400, detail="无效的图片索引")

    image_url = refs[image_index]
    try:
        storage_client = get_storage_client()
        storage_client.delete_object(image_url)
    except Exception as e:
        logger.error(f"删除MinIO文件失败: {e}")

    refs.pop(image_index)
    prop.reference_images = refs
    await db.commit()

    return {"success": True, "message": "参考图删除成功"}
