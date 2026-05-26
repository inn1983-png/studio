"""Central registry for Txtovideo prompt templates."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class TxtovideoPromptTemplate:
    """Metadata and content for a prompt template."""

    template_id: str
    name: str
    version: str
    category: str
    filename: str
    variables: tuple[str, ...]
    content: str


TEMPLATE_MANIFEST = {
    "script_adapt": {
        "name": "剧本改编",
        "version": "v1",
        "category": "script",
        "filename": "script_adapt_v1.md",
    },
    "character_extract": {
        "name": "角色提取",
        "version": "v1",
        "category": "asset",
        "filename": "character_extract_v1.md",
    },
    "scene_extract": {
        "name": "场景提取",
        "version": "v1",
        "category": "asset",
        "filename": "scene_extract_v1.md",
    },
    "prop_extract": {
        "name": "道具提取",
        "version": "v1",
        "category": "asset",
        "filename": "prop_extract_v1.md",
    },
    "storyboard_cap_desc_promopt": {
        "name": "分镜 cap/desc_promopt",
        "version": "v1",
        "category": "storyboard",
        "filename": "storyboard_cap_desc_promopt_v1.md",
    },
    "image_prompt": {
        "name": "图片提示词",
        "version": "v1",
        "category": "image",
        "filename": "image_prompt_v1.md",
    },
    "video_prompt_ltx": {
        "name": "LTX 视频提示词",
        "version": "v1",
        "category": "video",
        "filename": "video_prompt_ltx_v1.md",
    },
    "video_prompt_seedance": {
        "name": "Seedance 视频提示词",
        "version": "v1",
        "category": "video",
        "filename": "video_prompt_seedance_v1.md",
    },
    "quality_score": {
        "name": "质量评分",
        "version": "v1",
        "category": "quality",
        "filename": "quality_score_v1.md",
    },
    "rewrite_fix": {
        "name": "修复改写",
        "version": "v1",
        "category": "quality",
        "filename": "rewrite_fix_v1.md",
    },
}

SUPPORTED_VARIABLES = (
    "source_text",
    "script_text",
    "characters",
    "scenes",
    "props",
    "era",
    "style",
    "platform",
    "aspect_ratio",
    "shot_count_min",
    "shot_count_max",
    "duration_seconds",
    "negative_rules",
)


@lru_cache(maxsize=1)
def list_txtovideo_templates() -> list[TxtovideoPromptTemplate]:
    """Load all Txtovideo templates from disk."""
    templates = []
    for template_id, metadata in TEMPLATE_MANIFEST.items():
        path = TEMPLATE_DIR / metadata["filename"]
        templates.append(
            TxtovideoPromptTemplate(
                template_id=template_id,
                name=metadata["name"],
                version=metadata["version"],
                category=metadata["category"],
                filename=metadata["filename"],
                variables=SUPPORTED_VARIABLES,
                content=path.read_text(encoding="utf-8"),
            )
        )
    return templates


def get_txtovideo_template(template_id: str) -> TxtovideoPromptTemplate | None:
    """Return one template by id."""
    return next(
        (
            template
            for template in list_txtovideo_templates()
            if template.template_id == template_id
        ),
        None,
    )

