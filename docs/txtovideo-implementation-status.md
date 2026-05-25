# Txtovideo Studio Implementation Status

更新时间：2026-05-25

## 当前执行状态

| 轮次 | Phase | 状态 | 说明 |
| --- | --- | --- | --- |
| 第一轮 | Phase 0：品牌统一与入口收口 | 已完成 | README、品牌文案、主导航、实验功能收口、License 一致性已处理 |
| 第二轮 | Phase 1：短剧数据结构文档和最小数据模型 | 已完成 | 已新增 Txtovideo 专用模型、迁移和数据结构文档，并完成迁移验证 |
| 第三轮 | Phase 2：短剧工作台 MVP 页面 | 已完成 | 已新增项目级短剧工作台路由和本地草稿式 MVP 页面 |
| 第四轮 | Phase 3：Txtovideo 专用提示词模板 | 已完成 | 已新增后端模板 registry/API，并在工作台支持模板版本选择和 prompt_used 记录 |
| 第五轮 | Phase 4：导出 ZIP 包 | 未开始 | 后续 |

## 本次记录

- 新增 `backend/src/models/txtovideo.py`。
- 新增 Alembic 迁移 `034_create_txtovideo_tables.py`。
- 新增数据结构文档 `docs/txtovideo-data-schema.md`。
- 保持旧 `projects`、`movie_*`、`canvas_*` 表和路由不删除。
- 新增 `/txtovideo/projects/:projectId/workbench` 路由。
- 短剧项目详情页的“进入短剧工作台”已改为进入项目级 Txtovideo 工作台。
- 工作台 MVP 已覆盖原文、剧本、角色、场景、道具、分镜、图片提示词、视频提示词、质量检查、导出 10 个线性步骤。
- 当前工作台产物保存到浏览器本地草稿，后续 Phase 3/4 再接入专用提示词模板和 ZIP 导出。
- 新增 `backend/src/prompts/txtovideo/` 作为 Txtovideo V1 提示词模板唯一维护源。
- 新增 10 个 V1 模板：剧本改编、角色提取、场景提取、道具提取、分镜、图片提示词、LTX 视频提示词、Seedance 视频提示词、质量评分、修复改写。
- 新增 `/api/v1/txtovideo/prompts/templates` 模板列表 API 和模板详情 API。
- 短剧工作台支持按步骤选择模板版本，并把每次重新生成使用的模板写入本地草稿 `promptUsed` 和导出 manifest。

## 验证记录

- Phase 0 已验证：
  - `frontend: npm run build` 通过。
  - `backend: uv run python -X pycache_prefix=... -m compileall src` 通过。
  - `backend: uv run alembic current` 返回 `032`。
  - 浏览器检查登录页标题为 `Txtovideo Studio - 小说短剧工作站`。
- Phase 1 已验证：
  - `backend: uv run python -X pycache_prefix=... -m compileall src` 通过。
  - `backend: uv run python -c "from src.models.txtovideo import ..."` 通过。
  - `backend: uv run alembic heads` 返回 `034 (head)`。
  - `backend: uv run alembic upgrade head` 成功执行 `032 -> 033 -> 034`。
  - `backend: uv run alembic current` 返回 `034 (head)`。
  - `frontend: npm run build` 通过。
- Phase 2 已验证：
  - `frontend: npm run build` 通过。
  - `frontend: npx eslint src/views/ShortDramaWorkbench.vue src/router/index.js src/components/project/ProjectDetail.vue` 通过。
  - 浏览器打开 `http://127.0.0.1:5173/txtovideo/projects/demo/workbench` 无前端控制台错误；未登录状态由认证壳接管。
- Phase 3 已验证：
  - `backend: uv run python -m compileall src` 通过；仅保留既有 `src/utils/text_utils.py` 转义警告。
  - `backend: uv run python -c "from src.prompts.txtovideo import list_txtovideo_templates; ..."` 确认加载 10 个模板。
  - `frontend: npm run build` 通过。
  - `frontend: npx eslint src/views/ShortDramaWorkbench.vue src/services/txtovideoPrompts.js` 通过。

## 环境提示

- 本地 MinIO 当前不可用，后端检查时自动切换到本地文件存储。
- `compileall` 使用临时 `pycache_prefix`，避免 Windows 覆盖被占用的 `__pycache__` 文件。
