"""
任务基础工具模块 - 提供异步任务运行、数据库会话管理和重试策略
"""
import asyncio
import functools
import threading
from typing import Any, Callable, Coroutine, Optional, Tuple, Type, TypeVar

from src.core.database import get_async_db
from src.core.logging import get_logger
from src.models.task_status import check_dependencies_met, get_retry_delay, DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAYS

logger = get_logger(__name__)

T = TypeVar("T")

DEFAULT_RETRY_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
)

_worker_loop = None
_worker_loop_thread = None
_worker_loop_lock = threading.Lock()
_worker_loop_ready = threading.Event()


def _worker_loop_runner() -> None:
    global _worker_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _worker_loop = loop
    _worker_loop_ready.set()
    try:
        loop.run_forever()
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )
        loop.close()
        _worker_loop = None

def get_worker_loop():
    global _worker_loop_thread
    with _worker_loop_lock:
        if (
            _worker_loop is None
            or _worker_loop.is_closed()
            or _worker_loop_thread is None
            or not _worker_loop_thread.is_alive()
        ):
            _worker_loop_ready.clear()
            _worker_loop_thread = threading.Thread(
                target=_worker_loop_runner,
                name="celery-worker-async-loop",
                daemon=True,
            )
            _worker_loop_thread.start()
    _worker_loop_ready.wait()
    return _worker_loop

def run_async_task(coro: Coroutine[Any, Any, T]) -> T:
    loop = get_worker_loop()
    if threading.current_thread() is _worker_loop_thread:
        raise RuntimeError("run_async_task 不能在 worker loop 线程内部再次同步等待")
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

def async_task_decorator(
    func: Callable[..., Coroutine[Any, Any, T]] = None,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delays: Optional[list] = None,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    check_dependencies: bool = False,
) -> Callable[..., T]:
    """
    将异步函数包装为同步 Celery 任务的装饰器。
    自动注入数据库会话、处理异步运行和失败重试。

    参数:
        max_retries: 最大重试次数，默认3次
        retry_delays: 每次重试的延迟秒数列表，默认 [60, 300, 900]（指数退避）
        retry_on: 触发重试的异常类型元组，默认为网络/超时异常
        check_dependencies: 是否在执行前检查任务依赖，默认False

    使用方式:
        @async_task_decorator
        async def my_task(db, self, ...): ...

        @async_task_decorator(max_retries=5, retry_on=(ConnectionError, ValueError))
        async def my_task(db, self, ...): ...
    """
    _retry_on = retry_on or DEFAULT_RETRY_EXCEPTIONS

    def decorator(fn: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            task_self = args[0] if args else None

            async def _run():
                async with get_async_db() as db:
                    if check_dependencies:
                        video_task_id = kwargs.get('video_task_id') or (args[2] if len(args) > 2 else None)
                        if video_task_id:
                            deps_met = await _check_task_dependencies(db, video_task_id)
                            if not deps_met:
                                from src.models.video_task import VideoTask, VideoTaskStatus
                                from sqlalchemy import select
                                result = await db.execute(
                                    select(VideoTask).where(VideoTask.id == video_task_id)
                                )
                                task = result.scalar_one_or_none()
                                if task:
                                    task.status = VideoTaskStatus.PENDING.value
                                    await db.commit()
                                logger.warning(
                                    "Task %s skipped: dependencies not met for video_task_id=%s",
                                    task_self.name if task_self else fn.__name__,
                                    video_task_id,
                                )
                                return None
                    try:
                        return await fn(db, *args, **kwargs)
                    except _retry_on as exc:
                        if task_self is None or max_retries <= 0:
                            raise

                        retry_count = task_self.request.retries
                        if retry_count >= max_retries:
                            logger.error(
                                "Task %s exceeded max retries (%d): %s",
                                task_self.name, max_retries, exc,
                            )
                            raise

                        delay = get_retry_delay(retry_count + 1, retry_delays)
                        logger.warning(
                            "Task %s failed (attempt %d/%d), retrying in %ds: %s",
                            task_self.name, retry_count + 1, max_retries, delay, exc,
                        )
                        raise task_self.retry(exc=exc, countdown=delay, max_retries=max_retries)
                    except Exception:
                        raise

            return run_async_task(_run())

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


async def _check_task_dependencies(db, video_task_id: str) -> bool:
    from src.models.video_task import VideoTask
    from sqlalchemy import select

    result = await db.execute(
        select(VideoTask).where(VideoTask.id == video_task_id)
    )
    task = result.scalar_one_or_none()
    if not task or not task.depends_on:
        return True

    dep_ids = task.depends_on
    dep_result = await db.execute(
        select(VideoTask.id, VideoTask.status).where(VideoTask.id.in_(dep_ids))
    )
    task_statuses = {str(row.id): row.status for row in dep_result.all()}

    return check_dependencies_met(dep_ids, task_statuses)
