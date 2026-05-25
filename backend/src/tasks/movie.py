"""
电影制作相关的 Celery 任务
"""
from typing import Any, Dict, List
from src.tasks.app import celery_app
from src.tasks.base import async_task_decorator
from src.core.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

RETRY_KWARGS = dict(
    autoretry_for=(ConnectionError, TimeoutError, OSError),
    retry_backoff=False,
)


@celery_app.task(bind=True, max_retries=3, name="movie.extract_scenes", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_extract_scenes(db_session: AsyncSession, self, chapter_id: str, api_key_id: str, model: str = None):
    from src.services.scene_service import SceneService
    logger.info(f"Celery任务开始: movie_extract_scenes (chapter_id={chapter_id})")

    async def on_progress(percent, msg):
        self.update_state(state='PROGRESS', meta={'percent': percent, 'message': msg})

    service = SceneService(db_session)
    result = await service.extract_scenes_from_chapter(chapter_id, api_key_id, model, on_progress=on_progress)

    logger.info(f"Celery任务完成: movie_extract_scenes")
    return {"script_id": str(result.id)}


@celery_app.task(bind=True, max_retries=3, name="movie.extract_shots", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_extract_shots(db_session: AsyncSession, self, script_id: str, api_key_id: str, model: str = None):
    from src.services.storyboard_service import StoryboardService
    logger.info(f"Celery任务开始: movie_extract_shots (script_id={script_id})")

    service = StoryboardService(db_session)
    result = await service.batch_extract_shots_from_script(script_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_extract_shots, 成功 {result['success']}, 失败 {result['failed']}")
    return result


@celery_app.task(bind=True, max_retries=3, name="movie.extract_single_scene_shots", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_extract_single_scene_shots(db_session: AsyncSession, self, scene_id: str, api_key_id: str, model: str = None):
    from src.services.storyboard_service import StoryboardService
    logger.info(f"Celery任务开始: movie_extract_single_scene_shots (scene_id={scene_id})")

    service = StoryboardService(db_session)
    shots = await service.extract_shots_from_single_scene_with_deletion(scene_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_extract_single_scene_shots, 生成 {len(shots)} 个分镜")
    return {"success": True, "shot_count": len(shots)}


@celery_app.task(bind=True, max_retries=3, name="movie.create_transitions", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_create_transitions(db_session: AsyncSession, self, script_id: str, api_key_id: str, model: str = None):
    from src.services.transition_service import TransitionService
    logger.info(f"Celery任务开始: movie_create_transitions (script_id={script_id})")

    service = TransitionService(db_session)
    result = await service.batch_create_transitions(script_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_create_transitions, 成功 {result['success']}")
    return result


@celery_app.task(bind=True, max_retries=3, name="movie.extract_characters", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_extract_characters(db_session: AsyncSession, self, chapter_id: str, api_key_id: str, model: str = None):
    from src.services.movie_character_service import MovieCharacterService
    logger.info(f"Celery任务开始: movie_extract_characters (chapter_id={chapter_id})")

    service = MovieCharacterService(db_session)
    chars = await service.extract_characters_from_chapter(chapter_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_extract_characters, extracted {len(chars)} characters")
    return {"character_count": len(chars)}


@celery_app.task(bind=True, max_retries=3, name="movie.generate_character_avatar", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_generate_character_avatar(
    db_session: AsyncSession,
    self,
    character_id: str,
    api_key_id: str,
    model: str = None,
    prompt: str = None,
    style: str = "cinematic",
    reference_indices: list = None
):
    from src.services.movie_character_service import MovieCharacterService
    logger.info(f"Celery任务开始: movie_generate_character_avatar (character_id={character_id}, reference_indices={reference_indices})")

    service = MovieCharacterService(db_session)
    url = await service.generate_character_avatar(
        character_id,
        api_key_id,
        model,
        prompt,
        style,
        reference_indices
    )

    logger.info(f"Celery任务完成: movie_generate_character_avatar")
    return {"avatar_url": url}


@celery_app.task(bind=True, max_retries=3, name="movie.generate_keyframes", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_generate_keyframes(db_session: AsyncSession, self, script_id: str, api_key_id: str, model: str = None):
    from src.services.visual_identity_service import VisualIdentityService
    logger.info(f"Celery任务开始: movie_generate_keyframes (script_id={script_id})")

    service = VisualIdentityService(db_session)
    stats = await service.batch_generate_keyframes(script_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_generate_keyframes")
    return stats


@celery_app.task(bind=True, max_retries=3, name="movie.generate_single_keyframe", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_generate_single_keyframe(db_session: AsyncSession, self, shot_id: str, api_key_id: str, model: str = None, prompt: str = None):
    from src.services.visual_identity_service import VisualIdentityService
    logger.info(f"Celery任务开始: movie_generate_single_keyframe (shot_id={shot_id})")

    service = VisualIdentityService(db_session)
    url = await service.generate_single_keyframe(shot_id, api_key_id, model, prompt)

    logger.info(f"Celery任务完成: movie_generate_single_keyframe")
    return {"success": True}


@celery_app.task(bind=True, max_retries=2, name="movie.generate_transition_videos", **RETRY_KWARGS)
@async_task_decorator(max_retries=2, retry_delays=[120, 600])
async def movie_generate_transition_videos(
    db_session: AsyncSession,
    self,
    script_id: str,
    api_key_id: str,
    video_model: str
):
    from src.services.transition_service import TransitionService
    logger.info(f"Celery任务开始: movie_generate_transition_videos (script_id={script_id})")

    service = TransitionService(db_session)
    result = await service.batch_generate_transition_videos(script_id, api_key_id, video_model)

    logger.info(f"Celery任务完成: movie_generate_transition_videos, 结果: {result}")
    return result


@celery_app.task(bind=True, max_retries=2, name="movie.generate_single_transition", **RETRY_KWARGS)
@async_task_decorator(max_retries=2, retry_delays=[120, 600])
async def movie_generate_single_transition(db_session: AsyncSession, self, transition_id: str, api_key_id: str, video_model: str):
    from src.services.transition_service import TransitionService
    logger.info(f"Celery任务开始: movie_generate_single_transition (transition_id={transition_id})")

    service = TransitionService(db_session)
    task_id = await service.generate_transition_video(transition_id, api_key_id, video_model)

    logger.info(f"Celery任务完成: movie_generate_single_transition, task_id={task_id}")
    return {"success": True, "video_task_id": task_id}


@celery_app.task(bind=True, max_retries=1, name="movie.sync_transition_video_status")
@async_task_decorator(max_retries=1, retry_delays=[30])
async def sync_transition_video_status(db_session: AsyncSession, self):
    from src.services.transition_service import TransitionService
    logger.info(f"Celery任务开始: sync_transition_video_status")

    service = TransitionService(db_session)
    result = await service.sync_transition_video_status()

    logger.info(f"Celery任务完成: sync_transition_video_status, 结果: {result}")
    return result


@celery_app.task(bind=True, max_retries=3, name="movie.batch_generate_avatars", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_batch_generate_avatars(db_session: AsyncSession, self, project_id: str, api_key_id: str, model: str = None):
    from src.services.movie_character_service import MovieCharacterService

    logger.info(f"Celery任务开始: movie_batch_generate_avatars (project_id={project_id})")

    service = MovieCharacterService(db_session)
    result = await service.batch_generate_avatars(project_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_batch_generate_avatars, 成功: {result['success']}, 失败: {result['failed']}")
    return result


@celery_app.task(bind=True, max_retries=3, name="movie.generate_scene_images", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_generate_scene_images(db_session: AsyncSession, self, script_id: str, api_key_id: str, model: str = None):
    from src.services.scene_image_service import SceneImageService
    logger.info(f"Celery任务开始: movie_generate_scene_images (script_id={script_id})")

    service = SceneImageService(db_session)
    stats = await service.batch_generate_scene_images(script_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_generate_scene_images, 成功 {stats['success']}, 失败 {stats['failed']}")
    return stats


@celery_app.task(bind=True, max_retries=3, name="movie.generate_single_scene_image", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_generate_single_scene_image(db_session: AsyncSession, self, scene_id: str, api_key_id: str, model: str = None, prompt: str = None):
    from src.services.scene_image_service import SceneImageService
    logger.info(f"Celery任务开始: movie_generate_single_scene_image (scene_id={scene_id})")

    service = SceneImageService(db_session)
    url = await service.generate_scene_image(scene_id, api_key_id, model, prompt)

    logger.info(f"Celery任务完成: movie_generate_single_scene_image")
    return {"scene_image_url": url}


@celery_app.task(bind=True, max_retries=3, name="movie.regenerate_transition_prompt", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_regenerate_transition_prompt(
    db_session: AsyncSession,
    self,
    transition_id: str,
    api_key_id: str,
    model: str = None
):
    from src.services.transition_service import TransitionService
    from src.models.movie import MovieShotTransition
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    logger.info(f"Celery任务开始: movie_regenerate_transition_prompt (transition_id={transition_id})")

    stmt = (
        select(MovieShotTransition)
        .where(MovieShotTransition.id == transition_id)
        .options(
            selectinload(MovieShotTransition.from_shot),
            selectinload(MovieShotTransition.to_shot)
        )
    )
    result = await db_session.execute(stmt)
    transition = result.scalar_one_or_none()

    if not transition:
        raise ValueError(f"过渡不存在: {transition_id}")

    if not transition.from_shot or not transition.to_shot:
        raise ValueError(f"过渡缺少关联的分镜信息: {transition_id}")

    service = TransitionService(db_session)
    new_prompt = await service.generate_video_prompt(
        transition.from_shot,
        transition.to_shot,
        api_key_id,
        model
    )

    transition.video_prompt = new_prompt
    await db_session.commit()

    logger.info(f"Celery任务完成: movie_regenerate_transition_prompt, 新提示词长度: {len(new_prompt)}")
    return {
        "success": True,
        "transition_id": str(transition_id),
        "video_prompt": new_prompt
    }


@celery_app.task(bind=True, max_retries=3, name="movie.extract_props", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_extract_props(db_session: AsyncSession, self, chapter_id: str, api_key_id: str, model: str = None):
    from src.services.movie_prop_service import MoviePropService
    logger.info(f"Celery任务开始: movie_extract_props (chapter_id={chapter_id})")

    service = MoviePropService(db_session)
    props = await service.extract_props_from_chapter(chapter_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_extract_props, extracted {len(props)} props")
    return {"prop_count": len(props)}


@celery_app.task(bind=True, max_retries=3, name="movie.generate_prop_image", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_generate_prop_image(
    db_session: AsyncSession,
    self,
    prop_id: str,
    api_key_id: str,
    model: str = None,
    prompt: str = None,
    style: str = "cinematic",
):
    from src.services.movie_prop_service import MoviePropService
    logger.info(f"Celery任务开始: movie_generate_prop_image (prop_id={prop_id})")

    service = MoviePropService(db_session)
    url = await service.generate_prop_image(prop_id, api_key_id, model, prompt, style)

    logger.info(f"Celery任务完成: movie_generate_prop_image")
    return {"image_url": url}


@celery_app.task(bind=True, max_retries=3, name="movie.batch_generate_prop_images", **RETRY_KWARGS)
@async_task_decorator(max_retries=3)
async def movie_batch_generate_prop_images(db_session: AsyncSession, self, project_id: str, api_key_id: str, model: str = None):
    from src.services.movie_prop_service import MoviePropService
    logger.info(f"Celery任务开始: movie_batch_generate_prop_images (project_id={project_id})")

    service = MoviePropService(db_session)
    result = await service.batch_generate_images(project_id, api_key_id, model)

    logger.info(f"Celery任务完成: movie_batch_generate_prop_images, 成功: {result['success']}, 失败: {result['failed']}")
    return result
