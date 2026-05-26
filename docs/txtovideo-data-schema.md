# Txtovideo Studio Data Schema

本文档记录 Txtovideo Studio V1 的短剧业务数据结构。Phase 1 的原则是新增独立的 `txtovideo_*` 表，不覆盖旧 `projects`、`movie_*`、`canvas_*` 表。

## 命名与兼容约定

- 所有 Txtovideo 专用表使用 `txtovideo_` 前缀。
- `txtovideo_projects.project_id` 是对旧 `projects.id` 的可选桥接字段，用于从现有项目进入短剧工作台。
- 其他表中的 `project_id` 指向 `txtovideo_projects.id`。
- 分镜字段必须保留兼容拼写 `desc_promopt`，不能改成 `desc_prompt`。
- 时间字段继承 `BaseModel`：`id`、`created_at`、`updated_at`。

## Table: txtovideo_projects

短剧项目根表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | Txtovideo 项目 ID |
| project_id | uuid, nullable, unique | 旧 `projects.id` 桥接 |
| title | string(200) | 项目标题 |
| source_text | text | 原文/文案 |
| source_type | string(20) | `novel` / `short_text` / `script` |
| era | string(100) | 时代背景 |
| style | string(100) | 视觉风格 |
| aspect_ratio | string(20) | 默认 `9:16` |
| target_platform | string(20) | `douyin` / `shipinhao` / `bilibili` / `custom` |
| workflow_mode | string(40) | 默认 `txtovideo` |

## Table: txtovideo_script_versions

剧本版本表。剧本格式必须支持：

```text
【OS】
【角色名】
【留白】
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| version | integer | 版本号 |
| script_text | text | 剧本文本 |
| format_type | string(50) | 默认 `os_dialogue_blank` |
| prompt_used | text | 生成提示词 |
| model_used | string(100) | 使用模型 |
| status | string(20) | `draft` / `pending` / `running` / `success` / `failed` |

约束：`project_id + version` 唯一。

## Table: txtovideo_character_assets

角色资产表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| name | string(100) | 角色名 |
| gender | string(20) | 性别 |
| age | string(50) | 年龄 |
| identity | string(200) | 身份 |
| appearance | text | 外貌 |
| costume | text | 服装 |
| personality | text | 性格 |
| relation | text | 人物关系 |
| stable_prompt | text | 稳定提示词 |
| negative_prompt | text | 负向提示词 |
| reference_image_url | string(500) | 参考图 |
| is_locked | integer | `1` 表示锁定 |

约束：`project_id + name` 唯一，用于避免同名角色重复创建冲突设定。未识别角色在业务层统一使用“龙套”。

## Table: txtovideo_scene_assets

场景资产表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| name | string(100) | 场景名 |
| era | string(100) | 时代 |
| location_type | string(100) | 地点类型 |
| description | text | 场景描述 |
| lighting | string(200) | 光线 |
| mood | string(200) | 氛围 |
| props | json | 场景道具 |
| stable_prompt | text | 稳定提示词 |
| negative_prompt | text | 负向提示词 |
| reference_image_url | string(500) | 参考图 |
| is_locked | integer | `1` 表示锁定 |

约束：`project_id + name` 唯一。

## Table: txtovideo_prop_assets

道具资产表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| name | string(100) | 道具名 |
| type | string(100) | 道具类型 |
| era | string(100) | 时代 |
| description | text | 道具描述 |
| visual_prompt | text | 视觉提示词 |
| negative_prompt | text | 负向提示词 |
| must_appear | integer | `1` 表示必须出现在画面中 |

约束：`project_id + name` 唯一。

## Table: txtovideo_storyboard_shots

分镜表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| order_index | integer | 分镜顺序 |
| theme | string(8) | 两个汉字主题 |
| cap | text | 原文连续片段 |
| desc_promopt | text | 画面描述，兼容字段名 |
| characters | json | 角色名数组 |
| scene | string(100) | 场景名 |
| props | json | 道具名数组 |
| camera | string(200) | 镜头 |
| duration_seconds | float | 时长 |
| status | string(20) | 状态 |

约束：`project_id + order_index` 唯一。

## Table: txtovideo_image_prompts

图片提示词表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| shot_id | uuid | `txtovideo_storyboard_shots.id` |
| positive_prompt | text | 正向提示词 |
| negative_prompt | text | 负向提示词 |
| model_hint | string(100) | 模型提示 |
| aspect_ratio | string(20) | 画幅 |
| seed | integer | 随机种子 |
| reference_assets | json | 引用资产 |

约束：每个 `shot_id` 默认只保留一条图片提示词。

## Table: txtovideo_video_prompts

视频提示词表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| shot_id | uuid | `txtovideo_storyboard_shots.id` |
| engine | string(50) | `ltx` / `seedance` / `runninghub` / `custom` |
| duration_seconds | float | 时长 |
| prompt | text | 视频提示词 |
| camera_motion | text | 镜头运动 |
| character_motion | text | 角色动作 |
| scene_motion | text | 场景运动 |
| avoid | text | 避免项 |
| first_frame_ref | string(500) | 首帧引用 |
| last_frame_ref | string(500) | 尾帧引用 |

约束：`shot_id + engine` 唯一。

## Table: txtovideo_quality_reports

质量评分表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| target_type | string(50) | `script` / `character` / `scene` / `storyboard` / `image_prompt` / `video_prompt` |
| target_id | uuid | 被评分对象 ID |
| score | float | 评分 |
| issues | json | 问题列表 |
| suggestions | json | 修复建议 |
| fixed_output | json | 修复后输出 |

## Table: txtovideo_export_packages

导出包记录表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| project_id | uuid | `txtovideo_projects.id` |
| package_type | string(50) | 导出类型 |
| file_path | string(500) | 文件路径 |
| manifest | json | 导出清单 |

## Phase 1 验收对照

- 不破坏旧数据结构：新增 `txtovideo_*` 表，旧表不改名、不删除。
- 新增 Txtovideo 模式：`workflow_mode = txtovideo`。
- 后续短剧功能可围绕这些结构开发：项目、剧本、角色、场景、道具、分镜、图片提示词、视频提示词、质量报告、导出包均已建模。
- `desc_promopt` 已按兼容字段保留。
