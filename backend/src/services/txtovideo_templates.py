from typing import Any, Dict, List

from src.core.logging import get_logger

logger = get_logger(__name__)

PROJECT_TEMPLATES = [
    {
        "id": "urban_romance",
        "name": "都市爱情",
        "description": "现代都市背景的爱情短剧",
        "defaults": {
            "era": "现代",
            "style": "都市爱情",
            "aspect_ratio": "9:16",
            "target_platform": "douyin",
            "source_type": "novel",
        },
        "suggested_steps": [
            "script_adapt",
            "character_extract",
            "scene_extract",
            "storyboard_generate",
            "image_prompt_generate",
            "video_prompt_generate",
        ],
    },
    {
        "id": "ancient_costume",
        "name": "古装剧",
        "description": "古代背景的古装短剧",
        "defaults": {
            "era": "古代",
            "style": "古装武侠",
            "aspect_ratio": "9:16",
            "target_platform": "douyin",
            "source_type": "novel",
        },
        "suggested_steps": [
            "script_adapt",
            "character_extract",
            "scene_extract",
            "storyboard_generate",
            "image_prompt_generate",
            "video_prompt_generate",
        ],
    },
    {
        "id": "suspense_thriller",
        "name": "悬疑惊悚",
        "description": "悬疑推理类短剧",
        "defaults": {
            "era": "现代",
            "style": "悬疑推理",
            "aspect_ratio": "9:16",
            "target_platform": "douyin",
            "source_type": "novel",
        },
        "suggested_steps": [
            "script_adapt",
            "character_extract",
            "scene_extract",
            "prop_extract",
            "storyboard_generate",
            "image_prompt_generate",
            "video_prompt_generate",
        ],
    },
    {
        "id": "campus_youth",
        "name": "校园青春",
        "description": "校园背景的青春短剧",
        "defaults": {
            "era": "现代",
            "style": "校园青春",
            "aspect_ratio": "9:16",
            "target_platform": "douyin",
            "source_type": "novel",
        },
        "suggested_steps": [
            "script_adapt",
            "character_extract",
            "scene_extract",
            "storyboard_generate",
            "image_prompt_generate",
            "video_prompt_generate",
        ],
    },
    {
        "id": "fantasy_xianxia",
        "name": "玄幻仙侠",
        "description": "玄幻仙侠类短剧",
        "defaults": {
            "era": "古代",
            "style": "玄幻仙侠",
            "aspect_ratio": "9:16",
            "target_platform": "douyin",
            "source_type": "novel",
        },
        "suggested_steps": [
            "script_adapt",
            "character_extract",
            "scene_extract",
            "prop_extract",
            "storyboard_generate",
            "image_prompt_generate",
            "video_prompt_generate",
        ],
    },
]


class TxtovideoTemplateService:
    def __init__(self):
        pass

    def list_templates(self) -> List[Dict[str, Any]]:
        return PROJECT_TEMPLATES

    def get_template(self, template_id: str) -> Dict[str, Any] | None:
        for t in PROJECT_TEMPLATES:
            if t["id"] == template_id:
                return t
        return None
