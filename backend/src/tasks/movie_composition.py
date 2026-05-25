"""
电影合成 Celery 任务 - 从过渡视频合成完整电影
"""

from src.tasks.app import celery_app
from src.tasks.base import async_task_decorator
from src.core.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=2,
    name="movie.compose_video",
    autoretry_for=(ConnectionError, TimeoutError, OSError),
    retry_backoff=False,
)
@async_task_decorator(max_retries=2, retry_delays=[120, 600])
async def movie_compose_video(db_session: AsyncSession, self, task_id: str):
    from src.services.movie_video_service import MovieVideoService

    logger.info(f"Celery任务开始: movie_compose_video (task_id={task_id})")

    service = MovieVideoService(db_session)
    result = await service.synthesize_movie_from_transitions(task_id)

    logger.info(f"Celery任务成功: movie_compose_video (task_id={task_id})")
    return result


__all__ = ["movie_compose_video"]
