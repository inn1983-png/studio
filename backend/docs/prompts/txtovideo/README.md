# Txtovideo Prompt Templates

本目录记录 Txtovideo Studio V1 提示词模板体系。模板的唯一维护源位于：

`backend/src/prompts/txtovideo/`

## V1 模板清单

| 模板 ID | 文件 | 用途 |
| --- | --- | --- |
| `script_adapt` | `script_adapt_v1.md` | 原文改编为 OS / 对白 / 留白剧本 |
| `character_extract` | `character_extract_v1.md` | 提取角色资产 |
| `scene_extract` | `scene_extract_v1.md` | 提取场景资产 |
| `prop_extract` | `prop_extract_v1.md` | 提取道具资产 |
| `storyboard_cap_desc_promopt` | `storyboard_cap_desc_promopt_v1.md` | 生成分镜 JSON，保留 `desc_promopt` 字段 |
| `image_prompt` | `image_prompt_v1.md` | 生成每个分镜的图片提示词 |
| `video_prompt_ltx` | `video_prompt_ltx_v1.md` | 生成 LTX 视频提示词 |
| `video_prompt_seedance` | `video_prompt_seedance_v1.md` | 生成 Seedance 视频提示词 |
| `quality_score` | `quality_score_v1.md` | 质量评分与问题定位 |
| `rewrite_fix` | `rewrite_fix_v1.md` | 根据质检结果修复文本或 JSON |

## API

- `GET /api/v1/txtovideo/prompts/templates`
- `GET /api/v1/txtovideo/prompts/templates/{template_id}`

前端工作台会按步骤保存所选模板版本到本地草稿的 `promptUsed` 字段，并在导出 manifest 中记录 `prompt_template_versions`。

