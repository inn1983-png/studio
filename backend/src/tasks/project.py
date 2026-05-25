"""
项目处理相关的 Celery 任务
"""
from typing import Any, Dict
from src.tasks.app import celery_app
from src.tasks.base import async_task_decorator
from src.core.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

@celery_app.task(
    bind=True,
    max_retries=2,
    name="file_processing.process_uploaded_file",
    autoretry_for=(ConnectionError, TimeoutError, OSError),
    retry_backoff=False,
)
@async_task_decorator(max_retries=2, retry_delays=[30, 120])
async def process_uploaded_file(db_session: AsyncSession, self, project_id: str, owner_id: str) -> Dict[str, Any]:
    """处理上传文件的 Celery 任务"""
    from src.services.project_processing import ProjectProcessingService
    logger.info(f"Celery任务开始: process_uploaded_file (project_id={project_id})")
    
    service = ProjectProcessingService(db_session)
    result = await service.process_file_task(project_id, owner_id)
    
    logger.info(f"Celery任务成功: process_uploaded_file (project_id={project_id})")
    return result

@celery_app.task(
    bind=True,
    max_retries=2,
    name="file_processing.retry_failed_project",
    autoretry_for=(ConnectionError, TimeoutError, OSError),
    retry_backoff=False,
)
@async_task_decorator(max_retries=2, retry_delays=[30, 120])
async def retry_failed_project(db_session: AsyncSession, self, project_id: str, owner_id: str) -> Dict[str, Any]:
    """重试失败项目的 Celery 任务"""
    from src.services.project_processing import ProjectProcessingService
    logger.info(f"Celery任务开始: retry_failed_project (project_id={project_id})")
    
    service = ProjectProcessingService(db_session)
    result = await service.retry_failed_project(project_id, owner_id)
    
    if result.get("success", False):
        logger.info(f"Celery任务成功: retry_failed_project (project_id={project_id})")
    else:
        logger.error(f"Celery任务失败: retry_failed_project (project_id={project_id}, error={result.get('message')})")
        
    return result
