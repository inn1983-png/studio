# Txtovideo Studio 改造计划

> 原项目名: AICG / AICON / ai-moive-studio
> 新项目名: Txtovideo Studio - 小说短剧工作站
> 创建时间: 2026-05-23
> 最后更新: 2026-05-24

---

## 总体策略: 分阶段渐进改造

| 阶段 | 内容 | 状态 |
|------|------|------|
| P0 | 品牌换皮（名称/LOGO/版权/标题/域名/包名/数据库迁移） | ✅ 已完成 |
| P1 | 配置系统 + Provider架构扩展 | ✅ 已完成 |
| P2 | 核心功能（任务队列/资产库/分镜工坊） | ✅ 已完成 |
| P3 | 前端改造 + 设置页 + 导出功能 | ✅ 已完成 |

---

## P0 - 品牌换皮 ✅ 已完成

### 品牌映射表

| 原始值 | 新值 |
|--------|------|
| AICG / Aicg / aicg | Txtovideo / txtovideo |
| AICON / Aicon / aicon | Txtovideo / txtovideo |
| AICG Platform | Txtovideo Studio |
| AICG内容分发平台 | Txtovideo Studio - 小说短剧工作站 |
| Content Distribution Platform | Novel-to-Drama Production Studio |
| aicg_platform (数据库名) | txtovideo_studio |
| aicg_user (数据库用户) | txtovideo_user |
| aicg-files (MinIO桶) | txtovideo-files |
| aicg-avatars (MinIO桶) | txtovideo-avatars |
| aicg-frontend (npm包名) | txtovideo-studio |
| aicon-network (Docker网络) | txtovideo-network |

### 前端文件修改清单

- [x] `frontend/index.html` — title、favicon引用
- [x] `frontend/package.json` — name、description
- [x] `frontend/package-lock.json` — name
- [x] `frontend/src/components/layout/AppSidebar.vue` — logo文字 "AICG" → "Txtovideo"
- [x] `frontend/src/components/layout/AuthLayout.vue` — logo文字、版权声明
- [x] `frontend/src/router/guards.js` — 页面标题后缀
- [x] `frontend/src/router/index.js` — 注册页副标题
- [x] `frontend/src/views/Dashboard.vue` — 欢迎文案
- [x] 新增 `frontend/public/favicon.svg` — LOGO SVG图标

### 后端文件修改清单

- [x] `backend/src/core/config.py` — APP_NAME、数据库/MinIO相关常量默认值
- [x] `backend/src/main.py` — FastAPI title/description/contact、日志、响应
- [x] `backend/src/core/exceptions.py` — AICGException → TxtovideoException
- [x] `backend/src/tasks/app.py` — Celery app name "aicon" → "txtovideo"
- [x] `backend/src/middleware/error.py` — 异常类引用和日志文本
- [x] `backend/src/assistant/agent_factory.py` — 系统提示词 "Aicon" → "Txtovideo"
- [x] `backend/src/api/v1/__init__.py` — API名称
- [x] `backend/src/api/schemas/file.py` — 示例桶名
- [x] `backend/src/api/health.py` — 服务名称
- [x] `backend/src/__init__.py` — 模块文档和作者
- [x] `backend/src/services/provider/factory.py` — CustomProvider 默认 base_url（保留 api.aiconapi.me，见备注）
- [x] `backend/src/services/provider/custom_provider.py` — 默认 base_url（保留 api.aiconapi.me，见备注）

### 配置/部署文件修改清单

- [x] `.env.example` — 数据库/MinIO相关命名
- [x] `.env` — 同上 + CORS端口
- [x] `backend/.env` — 数据库/MinIO/JWT相关命名 + CORS端口
- [x] `.env.production.example` — 同上 + Docker变量
- [x] `docker-compose.yml` — 容器名、网络名、数据库名
- [x] `docker-compose.prod.yml` — 容器名、网络名、镜像名、数据库名
- [x] `scripts/start.sh` — 启动脚本日志
- [x] `scripts/build-and-push.sh` — 镜像名和仓库
- [x] `build-docker.bat` — 镜像名和仓库
- [x] `build-docker.sh` — 镜像名和仓库
- [x] `start.bat` — 窗口标题
- [x] `stop.bat` — 窗口标题
- [x] `backend/environment.yml` — conda环境名
- [x] `backend/environment_gpu.yml` — conda环境名

### 测试文件修改清单

- [x] `backend/tests/integration/test_upload.py` — 桶名
- [x] `backend/tests/integration/test_canvas_api.py` — 桶名URL

### 数据库迁移

- [x] 创建新数据库 `txtovideo_studio`
- [x] 创建新用户 `txtovideo_user`
- [x] 迁移 `aicg_platform` 的所有数据到新数据库（pg_dump + psql）
- [x] 更新 `.env` 中的 `DATABASE_URL`

### MinIO 迁移

- [x] 创建新桶 `txtovideo-files`
- [x] 创建新桶 `txtovideo-avatars`
- [x] 迁移 `aicg-files` 的5个文件到新桶
- [x] `aicg-avatars` 桶不存在，跳过
- [x] 更新 `.env` 中的桶名配置

### 验证结果

- [x] 前端页面标题显示 "Txtovideo Studio - 小说短剧工作站"
- [x] 侧边栏 logo 文字显示 "Txtovideo"
- [x] 欢迎文案显示 "开始您的小说转短剧创作之旅"
- [x] 版权声明更新为 "© 2024-2026 Txtovideo Studio"
- [x] 后端 API 根路径返回 "欢迎使用 Txtovideo Studio"
- [x] 后端 API 信息返回 "Txtovideo Studio"
- [x] 后端 API v1 返回 "Txtovideo Studio API v1"
- [x] 健康检查返回 "txtovideo-backend"
- [x] 数据库连接正常（新用户/新数据库）
- [x] 用户注册/登录正常
- [x] MinIO 文件存取正常
- [x] 全局搜索确认无 AICG/AICON 残留引用

### 备注

- `api.aiconapi.me` 是外部 API 代理服务地址，保留不变。待新 API 域名就绪后替换。
- 旧数据库 `aicg_platform` 和旧 MinIO 桶 `aicg-files` 仍保留，可在确认无问题后手动删除。

---

## P1 - 配置系统 + Provider架构扩展 ✅ 已完成

### 配置系统改造

- [x] 将硬编码的品牌信息提取到配置文件（config.py 新增 APP_DESCRIPTION/APP_LOGO_TEXT/APP_COPYRIGHT/APP_SERVICE_NAME/APP_CELERY_NAME）
- [x] 支持通过环境变量覆盖品牌信息（pydantic_settings 自动支持）
- [x] 后端所有硬编码品牌文本改为引用 settings（main.py/health.py/api/__init__.py/tasks/app.py/agent_factory.py/middleware/error.py）
- [x] 新增 /brand API 端点（无需认证）
- [x] 前端通过 API 获取品牌配置（stores/brand.js + Pinia store）
- [x] 前端组件使用 brandStore 替代硬编码（AppSidebar/AuthLayout/Dashboard/guards.js）

### Provider 架构扩展

- [x] TTS Provider 独立抽象（BaseTTSProvider）
- [x] 图像生成 Provider 独立抽象（BaseImageProvider）
- [x] 视频生成 Provider 统一接口（BaseVideoProvider，VectorEngineProvider 已继承）
- [x] BaseLLMProvider 的 generate_image/generate_audio 改为非抽象方法，默认抛出 NotImplementedError
- [x] Provider 注册机制改进（@register_provider 装饰器 + _PROVIDER_REGISTRY）
- [x] APIKeyProvider 枚举新增 DEEPSEEK 和 VECTORENGINE，与 ProviderFactory 对齐
- [x] ProviderFactory 新增 get_supported_providers() 方法

---

## P2 - 核心功能改造

### 任务队列状态机

- [x] 统一任务状态管理（TaskStatus 枚举 + 状态转换校验 validate_transition）
- [x] 任务优先级（TaskPriority 枚举 + PRIORITY_ORDER）
- [x] 失败重试策略改进（指数退避 get_retry_delay + async_task_decorator 重试参数）
- [x] 任务依赖关系

### 资产库（角色/场景/道具）

- [x] 角色资产管理模型（已有 MovieCharacter）
- [x] 场景资产管理模型（已有 MovieScene）
- [x] 道具资产管理模型（新增 MovieProp + GenerationType.PROP_IMAGE）
- [x] 道具服务层（MoviePropService：提取/生成/批量生成）
- [x] 道具 API 路由（8个端点：CRUD + 生成 + 参考图）
- [x] 道具前端 API（movie.js 新增8个方法）
- [x] 道具前端 Composable（usePropWorkflow.js）
- [x] 道具前端组件（PropPanel.vue）
- [x] 数据库迁移（030_create_movie_props_table.py）

### 分镜工坊

- [x] 分镜编辑器前端页面（StoryboardEditor.vue：查看/编辑模式切换、内联编辑分镜描述/对话、拖拽排序、删除分镜、关键帧预览）
- [x] 分镜更新/删除/排序 API（PUT /shots/{id}, DELETE /shots/{id}, PUT /shots/{id}/order）
- [x] 前端 movie.js 新增 deleteShot/updateShotOrder 方法
- [x] 分镜与章节关联
- [x] 分镜预览功能增强（缩放/旋转/左右导航/滚轮缩放）

---

## P3 - 前端改造 + 设置页 + 导出功能

### 前端页面改造

- [x] 仪表盘快速操作优化（主推"小说转短剧制作"工作流）

### 设置页完善

- [x] 品牌配置管理（BrandSettings.vue：应用名称/描述/Logo文字/版权声明 + 实时预览）
- [x] 系统参数管理（SystemSettings.vue：重试策略/视频模型/存储配置）
- [x] Settings.vue 集成5个选项卡（个人资料/账户安全/偏好设置/品牌配置/系统参数）

### 导出剪辑功能

- [x] MP4 视频直接导出 API（POST /export/video/{chapter_id}）
- [x] MP4 视频下载 API（GET /export/video/download/{filename}）
- [x] 批量视频导出 API（POST /export/video/batch）
- [x] 前端 export.js 新增 exportVideo/batchExportVideos 方法
- [x] 项目详情页添加"导出视频"按钮（自动检测有视频的章节）

### Electron 打包

- [x] Electron 集成（独立 .cjs 方案，不依赖 vite-plugin-electron）
- [x] 安装包名称配置（electron-builder win/mac/linux 脚本）
- [x] 自动更新机制（electron-updater + GitHub publish）

---

## 发现的问题

### 已修复

- [2026-05-23] 项目删除功能不生效 — session.delete() 未执行 DELETE SQL，改用 sql_delete()
- [2026-05-23] Celery worker 不可用时文件处理永远不完成 — 添加异步直接处理后备方案
- [2026-05-23] 文本解析章节过滤阈值过高 — min_chapter_length 从 1000 降至 50
- [2026-05-23] UTF-8 BOM 标记影响章节检测 — 解析前自动清除
- [2026-05-23] .env CORS 缺少前端端口 — 添加 localhost:5173
- [2026-05-23] .env Redis 密码错误 — 本地 Redis 无密码

### 待修复

- (暂无)

---

## 变更日志

| 日期 | 内容 |
|------|------|
| 2026-05-23 | 创建改造计划，开始 P0 品牌换皮 |
| 2026-05-23 | 完成前端品牌替换（8个文件） |
| 2026-05-23 | 完成后端品牌替换（12个文件）：config.py、main.py、exceptions.py、app.py、middleware/error.py、agent_factory.py、api/v1/__init__.py、schemas/file.py、health.py、__init__.py、factory.py、custom_provider.py |
| 2026-05-23 | 完成配置/部署文件替换（16个文件）：.env系列、docker-compose系列、构建脚本、启动脚本、conda环境 |
| 2026-05-23 | 完成数据库迁移：创建 txtovideo_studio 数据库和 txtovideo_user 用户，从 aicg_platform 迁移全部数据 |
| 2026-05-23 | 完成 MinIO 迁移：创建 txtovideo-files 和 txtovideo-avatars 桶，迁移5个文件 |
| 2026-05-23 | 完成测试文件更新：test_upload.py、test_canvas_api.py |
| 2026-05-23 | P0 品牌换皮全部完成，所有验证通过 ✅ |
| 2026-05-23 | P1 配置系统改造：品牌配置提取到 config.py，新增 /brand API，前端 brandStore |
| 2026-05-23 | P1 Provider 架构重构：BaseVideoProvider/BaseTTSProvider/BaseImageProvider 独立抽象，@register_provider 注册机制，APIKeyProvider 对齐 |
| 2026-05-23 | P2 任务队列状态管理：TaskStatus 枚举（PENDING/PROCESSING/COMPLETED/FAILED/CANCELLED）+ validate_transition + TaskPriority |
| 2026-05-23 | P2 重试策略改进：async_task_decorator 支持 max_retries/retry_delays/retry_on 参数，指数退避延迟（60s→300s→900s→1800s...），默认重试 ConnectionError/TimeoutError/OSError，更新全部7个任务文件 |
| 2026-05-23 | P2 道具模型：MovieProp（13字段）+ PropImagePromptBuilder + MoviePropService（提取/生成/批量）+ 8个API端点 + 前端完整链路 + 数据库迁移030 |
| 2026-05-23 | P2 分镜编辑器：StoryboardEditor.vue（查看/编辑模式、内联编辑、拖拽排序、删除、关键帧预览）+ 后端3个新API（PUT/DELETE/排序）+ 前端API方法 |
| 2026-05-23 | P3 视频导出：3个后端API（MP4导出/下载/批量）+ 前端export.js + ProjectDetail导出按钮 |
| 2026-05-23 | P3 设置页完善：BrandSettings.vue（品牌配置+预览）+ SystemSettings.vue（系统参数）+ Settings.vue 5选项卡 |
| 2026-05-23 | P3 仪表盘优化：快速操作主推"小说转短剧制作"工作流 |
| 2026-05-23 | P2 任务依赖关系：VideoTask.depends_on（JSONB）+ check_dependencies_met + async_task_decorator check_dependencies 参数 + 迁移031 |
| 2026-05-23 | P2 分镜与章节关联：MovieShot.chapter_id + GET /shots/by-chapter/{chapter_id} + 前端 getShotsByChapter + 迁移032 |
| 2026-05-23 | 修复 ESLint 配置：安装 eslint-plugin-vue + vue-eslint-parser，修复19个 ESLint 错误（空catch块、未使用变量、重复key、常量条件等） |
| 2026-05-23 | 数据库迁移031/032成功执行，修复032中chapter_id类型不匹配（String→UUID） |
| 2026-05-23 | 开始 Electron 集成：正在安装 electron + electron-builder + vite-plugin-electron（安装中） |
| 2026-05-24 | 完成 Electron 集成：独立 .cjs 方案（main.cjs/preload.cjs/dev.cjs），放弃 vite-plugin-electron（与 Vue 插件冲突），添加 electron-copy.js 打包脚本，更新 package.json 脚本和 electron-builder 配置 |
| 2026-05-24 | 完成分镜预览增强：StoryboardEditor.vue 添加缩放/旋转/左右导航/滚轮缩放功能，CSS 样式完整 |
| 2026-05-24 | 修复 ESLint warnings：模板属性换行、img 自闭合、未使用变量，达到 0 errors 0 warnings |
| 2026-05-24 | P3 全部完成 ✅ |
| 2026-05-24 | Electron 自动更新：main.cjs 集成 electron-updater（发现新版本/下载进度/安装重启对话框），preload.cjs 暴露 checkForUpdates API，package.json 添加 GitHub publish 配置 |
| 2026-05-24 | 前端 chunk 优化：vite.config.js manualChunks 从静态映射改为函数式拆分，element-plus 按组件拆分（core/icons/table/tree/date-picker等），最大 chunk 从 1031KB 降至 576KB，构建警告消除 |
| 2026-05-24 | 后端修复：services/__init__.py 恢复 AvatarService 导入（之前被注释但 __all__ 仍导出） |
| 2026-05-24 | ESLint warnings 批量清理：从 103 降至 38（移除未使用导入70+处），剩余 38 个为 vue/require-default-prop(16)、_前缀未使用参数(6)、v-html(2)、测试文件(2)等低优先级项 |
| 2026-05-25 | ESLint 全部清零：0 errors 0 warnings（修复 v-html eslint-disable、移除未使用参数、测试文件 disable） |
| 2026-05-25 | 运行时全面验证通过：Dashboard/项目列表/项目详情/设置页/品牌配置/API健康检查/品牌API 全部正常 |
| 2026-05-25 | Electron 开发模式验证通过：v33.4.11 启动成功，连接 Vite dev server |
| 2026-05-25 | 全部改造计划完成 ✅✅✅ |

---

## 📌 当前进度快照（2026-05-25 完成）

### 已完成 ✅ 全部
- ✅ P0 品牌换皮
- ✅ P1 配置系统
- ✅ P2 核心功能（任务队列、重试策略、资产库、分镜编辑器、任务依赖、分镜关联）
- ✅ P3 全部完成（视频导出、设置页5选项卡、仪表盘优化、Electron集成、分镜预览增强）
- ✅ Electron 自动更新机制（electron-updater + GitHub publish）
- ✅ 前端 chunk 优化（element-plus 拆分，最大 chunk 576KB，无构建警告）
- ✅ 后端导入修复（AvatarService）
- ✅ ESLint 0 errors 0 warnings / 前端构建通过
- ✅ 数据库迁移全部执行到032（单 head）
- ✅ 运行时验证通过（前端5页面 + 后端3个API端点）
- ✅ Electron 开发模式验证通过
