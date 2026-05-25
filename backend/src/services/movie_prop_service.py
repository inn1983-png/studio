"""
电影道具服务 - 负责道具提取、视觉特征建模、道具图生成
"""

import json
import re
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.logging import get_logger
from src.models.movie import MovieProp, MovieScript, MovieScene, MovieShot
from src.services.base import BaseService
from src.services.provider.factory import ProviderFactory
from src.services.api_key import APIKeyService
from src.services.image import retry_with_backoff
import uuid

logger = get_logger(__name__)


class PropImagePromptBuilder:
    TEMPLATE = """CINEMATIC PROP REFERENCE SHEET
featuring DETAILED PHOTOGRAPHED VIEWS
of the prop: {name}

Prop details:
- Name: {name}
- Category: {category}
- Era / Time Period: {era_background}
- Key Visual Traits: {key_visual_traits}

Photography Requirements:
- Multiple angles showing the prop clearly
- Real materials, textures, and wear patterns
- Natural lighting with studio-quality setup
- Scale reference where appropriate
- High detail close-up of key features

Cinematography & Photography Style:
- High-end film prop reference photos
- Professional studio lighting
- Photographed, not rendered
- Neutral or black studio background

STRICT CONSTRAINTS:
- NO 3D render
- NO CGI
- NO digital art style

Technical Output:
- Ultra-detailed prop reference photos
- Aspect ratio: 16:9
- Place the English name in the top-left corner, clearly visible and readable
"""

    @classmethod
    def build_prompt(
        cls,
        name: str,
        category: Optional[str] = None,
        era_background: Optional[str] = None,
        key_visual_traits: Optional[List[str]] = None,
        visual_traits: Optional[str] = None,
    ) -> str:
        era = era_background or "Modern era"
        cat = category or "General"

        if key_visual_traits and len(key_visual_traits) > 0:
            traits_str = ", ".join(key_visual_traits)
        elif visual_traits:
            traits_str = visual_traits[:100] + "..." if len(visual_traits) > 100 else visual_traits
        else:
            traits_str = "Standard appearance"

        return cls.TEMPLATE.format(
            name=name,
            category=cat,
            era_background=era,
            key_visual_traits=traits_str
        )


class MoviePropService(BaseService):

    EXTRACT_PROPS_PROMPT = """
你是一个资深的电影道具设计师。请分析以下电影剧本片段,提取出其中出现的所有重要道具。

### 输出要求:
必须以 JSON 格式输出,结构如下:
{{
  "props": [
    {{
      "name": "道具名称",
      "category": "道具分类(武器/交通工具/家具/饰品/通讯设备/文件/食物/其他)",
      "era_background": "时代背景(如: 1940s WWII, Victorian Era, Cyberpunk 2077, Modern era等)",
      "description": "道具的用途、重要性、在剧情中的作用",
      "visual_traits": "详细的视觉特征描述(如:材质、颜色、大小、磨损程度、特殊标记),用于AI生图。",
      "key_visual_traits": ["核心视觉特征1", "核心视觉特征2", "核心视觉特征3"]
    }}
  ]
}}

### 重要规则:
1. **道具名称一致性**: 同一道具必须使用完全相同的名称
2. **只提取重要道具**: 只提取在剧情中起关键作用的道具,忽略普通背景道具
3. **字段要求**:
   - category: 必须从给定分类中选择最匹配的
   - era_background: 根据剧本内容推断时代背景
   - key_visual_traits: 提取3-4个最关键的视觉特征
4. **特征提取要求**:
   - 优先从剧本中提取明确描述的视觉特征
   - 如果没有明确描述,根据道具的类型和时代背景合理推断

待分析剧本:
---
{text}
---
"""

    async def extract_props_from_chapter(self, chapter_id: str, api_key_id: str, model: str = None) -> List[MovieProp]:
        from src.models.chapter import Chapter

        chapter = await self.db_session.get(Chapter, chapter_id, options=[selectinload(Chapter.project)])
        if not chapter:
            raise ValueError("未找到章节")

        script_text = chapter.content or ""

        stmt = select(MovieScript).where(MovieScript.chapter_id == chapter_id).options(
            selectinload(MovieScript.scenes).selectinload(MovieScene.shots)
        )
        result = await self.db_session.execute(stmt)
        script = result.scalar_one_or_none()

        if script:
            for scene in script.scenes:
                script_text += f"\n场景 {scene.order_index}: {scene.scene}\n"
                for shot in scene.shots:
                    script_text += f"镜头 {shot.order_index}: {shot.shot}\n"
                    if shot.dialogue:
                        script_text += f"对话: {shot.dialogue}\n"
                script_text += "\n"

        api_key_service = APIKeyService(self.db_session)
        api_key = await api_key_service.get_api_key_by_id(api_key_id, str(chapter.project.owner_id))

        llm_provider = ProviderFactory.create(
            provider=api_key.provider,
            api_key=api_key.get_api_key(),
            base_url=api_key.base_url
        )

        try:
            prompt = self.EXTRACT_PROPS_PROMPT.format(text=script_text[:5000])
            response = await llm_provider.completions(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电影道具设计师JSON生成器。"},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            prop_data = json.loads(content)

            stmt_existing = select(MovieProp).where(MovieProp.project_id == chapter.project_id)
            existing_result = await self.db_session.execute(stmt_existing)
            existing_props = {prop.name: prop for prop in existing_result.scalars().all()}

            def normalize_name(name: str) -> str:
                return re.sub(r'\s*\([^)]*\)', '', name).strip()

            created_props = []
            for prop in prop_data.get("props", []):
                prop_name = prop.get("name", "").strip()
                if not prop_name:
                    continue

                existing_prop = None
                normalized_new = normalize_name(prop_name)
                for existing_name, existing_p in existing_props.items():
                    if normalize_name(existing_name) == normalized_new:
                        existing_prop = existing_p
                        break

                generated_prompt = PropImagePromptBuilder.build_prompt(
                    name=prop_name,
                    category=prop.get("category"),
                    era_background=prop.get("era_background"),
                    key_visual_traits=prop.get("key_visual_traits"),
                    visual_traits=prop.get("visual_traits"),
                )

                if existing_prop:
                    existing_prop.category = prop.get("category")
                    existing_prop.description = prop.get("description")
                    existing_prop.visual_traits = prop.get("visual_traits")
                    existing_prop.era_background = prop.get("era_background")
                    existing_prop.key_visual_traits = prop.get("key_visual_traits", [])
                    existing_prop.generated_prompt = generated_prompt
                    created_props.append(existing_prop)
                else:
                    new_prop = MovieProp(
                        project_id=chapter.project_id,
                        name=prop_name,
                        category=prop.get("category"),
                        description=prop.get("description"),
                        visual_traits=prop.get("visual_traits"),
                        era_background=prop.get("era_background"),
                        key_visual_traits=prop.get("key_visual_traits", []),
                        generated_prompt=generated_prompt
                    )
                    self.db_session.add(new_prop)
                    existing_props[prop_name] = new_prop
                    created_props.append(new_prop)

            await self.db_session.commit()
            return created_props

        except Exception as e:
            logger.error(f"提取道具失败: {e}")
            raise

    async def generate_prop_image(
        self,
        prop_id: str,
        api_key_id: str,
        model: str = None,
        prompt: str = None,
        style: str = "cinematic",
    ) -> str:
        prop = await self.db_session.get(MovieProp, prop_id)
        if not prop:
            raise ValueError("未找到道具")

        from src.models.project import Project
        project = await self.db_session.get(Project, prop.project_id)
        api_key_service = APIKeyService(self.db_session)
        api_key = await api_key_service.get_api_key_by_id(api_key_id, str(project.owner_id))

        image_provider = ProviderFactory.create(
            provider=api_key.provider,
            api_key=api_key.get_api_key(),
            base_url=api_key.base_url
        )

        try:
            if not prompt:
                raise ValueError("必须提供生成提示词")

            enhanced_prompt = f"{prompt}. IMPORTANT: Include the text '{prop.name}' in the top-left corner of the image, clearly visible and readable."

            logger.info(f"生成道具图提示词: {enhanced_prompt[:200]}...")

            result = await retry_with_backoff(
                lambda: image_provider.generate_image(
                    prompt=enhanced_prompt,
                    model=model
                )
            )

            from src.utils.image_utils import extract_and_upload_image

            object_key = await extract_and_upload_image(
                result=result,
                user_id=str(project.owner_id),
                metadata={"prop_id": str(prop.id)}
            )

            prop.image_url = object_key

            from src.services.generation_history_service import GenerationHistoryService
            from src.models.movie import GenerationType, MediaType

            history_service = GenerationHistoryService(self.db_session)
            await history_service.create_history(
                resource_type=GenerationType.PROP_IMAGE,
                resource_id=str(prop.id),
                result_url=object_key,
                prompt=enhanced_prompt,
                media_type=MediaType.IMAGE,
                model=model,
                api_key_id=str(api_key.id) if api_key else None
            )

            await self.db_session.commit()
            return object_key

        except Exception as e:
            logger.error(f"生成道具图失败: {e}")
            raise

    async def batch_generate_images(self, project_id: str, api_key_id: str, model: str = None) -> dict:
        import asyncio

        stmt = select(MovieProp).where(
            MovieProp.project_id == project_id,
            MovieProp.image_url == None
        )
        result = await self.db_session.execute(stmt)
        props = result.scalars().all()

        if not props:
            return {"success": 0, "failed": 0, "total": 0, "message": "没有需要生成图片的道具"}

        logger.info(f"开始批量生成 {len(props)} 个道具的图片")

        async def generate_single(prop):
            try:
                if not prop.generated_prompt:
                    logger.warning(f"道具 {prop.name} 没有 generated_prompt,跳过")
                    return {"success": False, "prop": prop.name, "error": "缺少生成提示词"}

                await self.generate_prop_image(
                    str(prop.id),
                    api_key_id,
                    model,
                    prop.generated_prompt,
                    "cinematic"
                )
                return {"success": True, "prop": prop.name}
            except Exception as e:
                logger.error(f"生成道具 {prop.name} 图片失败: {e}")
                return {"success": False, "prop": prop.name, "error": str(e)}

        results = await asyncio.gather(*[generate_single(p) for p in props], return_exceptions=True)

        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed_count = len(results) - success_count

        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(props),
            "details": results
        }


__all__ = ["MoviePropService"]
