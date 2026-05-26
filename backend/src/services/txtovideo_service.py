import json
import uuid
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.txtovideo import *


class TxtovideoProjectService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verify_ownership(
        self, project_id: str, user_id: str
    ) -> Optional[ShortDramaProject]:
        stmt = select(ShortDramaProject).where(ShortDramaProject.id == project_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if project is None:
            return None
        if project.project_id is not None:
            from src.models.project import Project

            legacy = await self.db.get(Project, project.project_id)
            if legacy is None or str(legacy.owner_id) != str(user_id):
                return None
        return project

    async def create_project(self, user_id: str, data: dict) -> ShortDramaProject:
        from src.models.project import Project, ProjectType

        legacy = Project(
            owner_id=user_id,
            title=data.get("title", ""),
            type=ProjectType.AI_MOVIE,
            file_name="",
            file_size=0,
            file_type="txt",
            file_path="",
        )
        self.db.add(legacy)
        await self.db.flush()

        project = ShortDramaProject(
            project_id=legacy.id,
            title=data.get("title", ""),
            source_text=data.get("source_text", ""),
            source_type=data.get("source_type", "novel"),
            era=data.get("era"),
            style=data.get("style"),
            aspect_ratio=data.get("aspect_ratio", "9:16"),
            target_platform=data.get("target_platform", "douyin"),
            workflow_mode=data.get("workflow_mode", "txtovideo"),
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def get_project(
        self, project_id: str, user_id: str
    ) -> Optional[ShortDramaProject]:
        return await self._verify_ownership(project_id, user_id)

    async def list_projects(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[ShortDramaProject]:
        from src.models.project import Project

        stmt = (
            select(ShortDramaProject)
            .join(Project, ShortDramaProject.project_id == Project.id)
            .where(Project.owner_id == user_id)
            .order_by(ShortDramaProject.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_project(
        self, project_id: str, user_id: str, data: dict
    ) -> ShortDramaProject:
        project = await self._verify_ownership(project_id, user_id)
        if project is None:
            return None
        for key, value in data.items():
            if hasattr(project, key) and key not in (
                "id",
                "created_at",
                "updated_at",
                "project_id",
            ):
                setattr(project, key, value)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: str, user_id: str) -> bool:
        project = await self._verify_ownership(project_id, user_id)
        if project is None:
            return False
        await self.db.delete(project)
        await self.db.flush()
        return True

    async def save_draft(
        self, project_id: str, user_id: str, draft_data: dict
    ) -> ShortDramaProject:
        project = await self._verify_ownership(project_id, user_id)
        if project is None:
            return None

        pid = project.id

        characters_data = draft_data.get("characters", [])
        if isinstance(characters_data, str):
            characters_data = json.loads(characters_data)
        for char_data in characters_data:
            name = char_data.get("name")
            if not name:
                continue
            stmt = select(CharacterAsset).where(
                CharacterAsset.project_id == pid,
                CharacterAsset.name == name,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in char_data.items():
                    if key != "name" and hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                char = CharacterAsset(project_id=pid, **char_data)
                self.db.add(char)

        scenes_data = draft_data.get("scenes", [])
        if isinstance(scenes_data, str):
            scenes_data = json.loads(scenes_data)
        for scene_data in scenes_data:
            name = scene_data.get("name")
            if not name:
                continue
            stmt = select(SceneAsset).where(
                SceneAsset.project_id == pid,
                SceneAsset.name == name,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in scene_data.items():
                    if key != "name" and hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                scene = SceneAsset(project_id=pid, **scene_data)
                self.db.add(scene)

        props_data = draft_data.get("props", [])
        if isinstance(props_data, str):
            props_data = json.loads(props_data)
        for prop_data in props_data:
            name = prop_data.get("name")
            if not name:
                continue
            stmt = select(PropAsset).where(
                PropAsset.project_id == pid,
                PropAsset.name == name,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in prop_data.items():
                    if key != "name" and hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                prop = PropAsset(project_id=pid, **prop_data)
                self.db.add(prop)

        shots_data = draft_data.get(
            "storyboard", draft_data.get("shots", [])
        )
        if isinstance(shots_data, str):
            shots_data = json.loads(shots_data)
        shot_id_map = {}
        for shot_data in shots_data:
            order_index = shot_data.get("order_index")
            if order_index is None:
                continue
            stmt = select(StoryboardShot).where(
                StoryboardShot.project_id == pid,
                StoryboardShot.order_index == order_index,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in shot_data.items():
                    if key not in ("id", "order_index") and hasattr(
                        existing, key
                    ):
                        setattr(existing, key, value)
                shot_id_map[order_index] = existing.id
            else:
                shot = StoryboardShot(project_id=pid, **shot_data)
                self.db.add(shot)
                await self.db.flush()
                shot_id_map[order_index] = shot.id

        image_prompts_data = draft_data.get(
            "imagePrompts", draft_data.get("image_prompts", [])
        )
        if isinstance(image_prompts_data, str):
            image_prompts_data = json.loads(image_prompts_data)
        for ip_data in image_prompts_data:
            shot_id = ip_data.get("shot_id")
            if not shot_id:
                order_index = ip_data.get("order_index")
                if order_index is not None and order_index in shot_id_map:
                    shot_id = shot_id_map[order_index]
                else:
                    continue
            else:
                if not isinstance(shot_id, uuid.UUID):
                    shot_id = uuid.UUID(str(shot_id))
            stmt = select(ImagePrompt).where(ImagePrompt.shot_id == shot_id)
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            clean_data = {
                k: v for k, v in ip_data.items() if k not in ("shot_id",)
            }
            if existing:
                for key, value in clean_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                ip = ImagePrompt(project_id=pid, shot_id=shot_id, **clean_data)
                self.db.add(ip)

        video_prompts_data = draft_data.get(
            "videoPrompts", draft_data.get("video_prompts", [])
        )
        if isinstance(video_prompts_data, str):
            video_prompts_data = json.loads(video_prompts_data)
        for vp_data in video_prompts_data:
            shot_id = vp_data.get("shot_id")
            if not shot_id:
                order_index = vp_data.get("order_index")
                if order_index is not None and order_index in shot_id_map:
                    shot_id = shot_id_map[order_index]
                else:
                    continue
            else:
                if not isinstance(shot_id, uuid.UUID):
                    shot_id = uuid.UUID(str(shot_id))
            engine = vp_data.get("engine", "ltx")
            stmt = select(VideoPrompt).where(
                VideoPrompt.shot_id == shot_id,
                VideoPrompt.engine == engine,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            clean_data = {
                k: v
                for k, v in vp_data.items()
                if k not in ("shot_id", "engine")
            }
            if existing:
                for key, value in clean_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                vp = VideoPrompt(
                    project_id=pid,
                    shot_id=shot_id,
                    engine=engine,
                    **clean_data,
                )
                self.db.add(vp)

        await self.db.flush()
        await self.db.refresh(project)
        return project
