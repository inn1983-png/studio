"""
导出相关 API 路由
"""

import os
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user_required
from src.api.schemas.export import (
    JianYingExportResponse,
    VideoExportResponse,
    BatchExportRequest,
    BatchExportResponse,
    TxtovideoExportRequest,
    TxtovideoExportResponse,
)
from src.core.database import get_db
from src.core.logging import get_logger
from src.models.user import User
from src.services.jianying_export import JianYingExportService, JianYingExportError
from src.services.txtovideo_export import TxtovideoExportService

logger = get_logger(__name__)
router = APIRouter()


@router.post("/jianying/{chapter_id}", response_model=JianYingExportResponse)
async def export_chapter_to_jianying(
    *,
    chapter_id: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    try:
        export_service = JianYingExportService(db)
        zip_path = await export_service.export_chapter(
            chapter_id=chapter_id,
            user_id=str(current_user.id)
        )
        filename = Path(zip_path).name
        encoded_filename = quote(filename)
        return JianYingExportResponse(
            success=True,
            message="导出成功",
            download_url=f"/api/v1/export/jianying/download/{encoded_filename}",
            filename=filename
        )
    except JianYingExportError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导出失败: {str(e)}")


@router.get("/jianying/download/{filename:path}")
async def download_jianying_export(
    filename: str,
    current_user: User = Depends(get_current_user_required)
):
    decoded_filename = unquote(filename)
    file_path = (Path(tempfile.gettempdir()) / decoded_filename).resolve()
    if not str(file_path).startswith(str(Path(tempfile.gettempdir()).resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid file path")

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在或已过期")

    def cleanup_file(path: str):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"清理文件失败: {e}")

    encoded_filename = quote(decoded_filename)
    response = FileResponse(
        path=str(file_path),
        filename=decoded_filename,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )
    response.background = BackgroundTasks()
    response.background.add_task(cleanup_file, str(file_path))
    return response


@router.post("/video/{chapter_id}", response_model=VideoExportResponse)
async def export_chapter_video(
    *,
    chapter_id: str,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    from src.models.chapter import Chapter
    from src.utils.storage import storage_client
    from datetime import timedelta

    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    if not chapter.video_url:
        raise HTTPException(status_code=400, detail="该章节尚未生成视频，请先完成视频合成")

    try:
        video_key = chapter.video_url
        temp_dir = tempfile.mkdtemp(prefix="video_export_")
        project_name = chapter.title or "video"
        safe_name = "".join(c for c in project_name if c.isalnum() or c in "._- ") or "video"
        filename = f"{safe_name}.mp4"
        local_path = os.path.join(temp_dir, filename)

        await storage_client.download_file_to_path(video_key, local_path)

        download_url = f"/api/v1/export/video/download/{quote(filename, safe='')}"

        return VideoExportResponse(
            success=True,
            message="视频导出就绪",
            download_url=download_url,
            filename=filename,
            duration=chapter.video_duration
        )
    except Exception as e:
        logger.error(f"视频导出失败: {e}")
        raise HTTPException(status_code=500, detail=f"视频导出失败: {str(e)}")


@router.get("/video/download/{filename:path}")
async def download_exported_video(
    filename: str,
    current_user: User = Depends(get_current_user_required)
):
    decoded_filename = unquote(filename)
    file_path = (Path(tempfile.gettempdir()) / decoded_filename).resolve()
    if not str(file_path).startswith(str(Path(tempfile.gettempdir()).resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid file path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在或已过期，请重新导出")

    def cleanup_file(path: str):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"清理文件失败: {e}")

    encoded_filename = quote(decoded_filename)
    response = FileResponse(
        path=str(file_path),
        filename=decoded_filename,
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )
    response.background = BackgroundTasks()
    response.background.add_task(cleanup_file, str(file_path))
    return response


@router.post("/video/batch", response_model=BatchExportResponse)
async def batch_export_videos(
    *,
    req: BatchExportRequest,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    from src.models.chapter import Chapter
    from src.utils.storage import storage_client

    results = []
    for chapter_id in req.chapter_ids:
        try:
            chapter = await db.get(Chapter, chapter_id)
            if not chapter:
                results.append(VideoExportResponse(
                    success=False, message="章节不存在", download_url="", filename=""
                ))
                continue

            if not chapter.video_url:
                results.append(VideoExportResponse(
                    success=False, message="该章节尚未生成视频", download_url="", filename=""
                ))
                continue

            temp_dir = tempfile.mkdtemp(prefix="batch_export_")
            project_name = chapter.title or "video"
            safe_name = "".join(c for c in project_name if c.isalnum() or c in "._- ") or "video"
            filename = f"{safe_name}_{chapter_id[:8]}.mp4"
            local_path = os.path.join(temp_dir, filename)

            await storage_client.download_file_to_path(chapter.video_url, local_path)

            results.append(VideoExportResponse(
                success=True,
                message="视频导出就绪",
                download_url=f"/api/v1/export/video/download/{quote(filename, safe='')}",
                filename=filename,
                duration=chapter.video_duration
            ))
        except Exception as e:
            logger.error(f"批量导出章节 {chapter_id} 失败: {e}")
            results.append(VideoExportResponse(
                success=False, message=f"导出失败: {str(e)}", download_url="", filename=""
            ))

    return BatchExportResponse(
        success=all(r.success for r in results),
        message=f"成功导出 {sum(1 for r in results if r.success)}/{len(req.chapter_ids)} 个视频",
        results=results
    )


__all__ = ["router"]


@router.post("/txtovideo", response_model=TxtovideoExportResponse)
async def export_txtovideo_package(
    req: TxtovideoExportRequest,
    current_user: User = Depends(get_current_user_required)
):
    try:
        export_service = TxtovideoExportService()
        zip_path = await export_service.export_package(
            package_name=req.package_name,
            project_id=req.project_id,
            source=req.source,
            outputs=req.outputs,
            prompt_used=req.prompt_used,
        )
        filename = Path(zip_path).name
        encoded_filename = quote(filename)
        return TxtovideoExportResponse(
            success=True,
            message="导出成功",
            download_url=f"/api/v1/export/txtovideo/download/{encoded_filename}",
            filename=filename,
        )
    except Exception as e:
        logger.error(f"Txtovideo导出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}",
        )


@router.get("/txtovideo/download/{filename:path}")
async def download_txtovideo_export(
    filename: str,
    current_user: User = Depends(get_current_user_required)
):
    decoded_filename = unquote(filename)
    file_path = (Path(tempfile.gettempdir()) / decoded_filename).resolve()
    if not str(file_path).startswith(str(Path(tempfile.gettempdir()).resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid file path")

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在或已过期")

    def cleanup_file(path: str):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"清理文件失败: {e}")

    encoded_filename = quote(decoded_filename)
    response = FileResponse(
        path=str(file_path),
        filename=decoded_filename,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )
    response.background = BackgroundTasks()
    response.background.add_task(cleanup_file, str(file_path))
    return response
