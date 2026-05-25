"""
过渡视频状态同步任务
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.logging import get_logger
from src.models.movie import MovieShotTransition
from src.services.api_key import APIKeyService
from src.tasks.base import async_task_decorator
from src.tasks.app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=1,
    name="movie.sync_transition_video_status",
)
@async_task_decorator(max_retries=1, retry_delays=[30])
async def sync_transition_video_status(db_session: AsyncSession, self):
    logger.info("开始同步过渡视频任务状态")

    stmt = select(MovieShotTransition).where(
        MovieShotTransition.status == "processing",
        MovieShotTransition.video_task_id.isnot(None)
    )
    result = await db_session.execute(stmt)
    transitions = result.scalars().all()

    if not transitions:
        logger.info("没有需要同步的过渡视频任务")
        return {"synced": 0, "completed": 0, "failed": 0}

    logger.info(f"找到 {len(transitions)} 个待同步的过渡视频任务")

    synced_count = 0
    completed_count = 0
    failed_count = 0

    transitions_by_key = {}
    for transition in transitions:
        task_id = transition.video_task_id
        if task_id not in transitions_by_key:
            transitions_by_key[task_id] = transition

    api_key_service = APIKeyService(db_session)

    for task_id, transition in transitions_by_key.items():
        try:
            logger.warning(f"跳过任务 {task_id}，需要完善API Key获取逻辑")
            continue

        except Exception as e:
            logger.error(f"同步任务 {task_id} 失败: {e}")
            failed_count += 1

    await db_session.commit()

    logger.info(f"同步完成: 总计 {synced_count}, 完成 {completed_count}, 失败 {failed_count}")
    return {
        "synced": synced_count,
        "completed": completed_count,
        "failed": failed_count
    }
