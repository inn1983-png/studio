# Txtovideo Studio

Txtovideo Studio 是一个面向个人生产的小说短剧工作站，用于把小说、短文案和剧情设定整理成适合 AI 视频生产的结构化素材包。

本项目当前处于个人生产工具和实验版本阶段，目标是先跑通“文本到素材包”的稳定链路，不承诺商用稳定性，也不追求一开始成为通用 SaaS 平台。

## 当前定位

- 项目名称：Txtovideo Studio
- 中文定位：小说短剧工作站
- 当前版本目标：Txtovideo Studio V1
- 核心方向：导出型短剧工作台
- 使用场景：小说/文案到剧本、角色、场景、分镜、图片提示词、视频提示词和导出文件

V1 会保留原有后端接口、画布、Movie 相关服务和生成链路，但前端主入口会先收口到短剧生产所需功能。

## V1 主流程

```text
小说/文案输入
→ 剧本改编
→ 角色资产提取
→ 场景资产提取
→ 道具资产提取
→ 分镜 JSON 生成
→ 图片提示词生成
→ 视频提示词生成
→ 质量评分与修复
→ 导出素材包
→ 外部 ComfyUI / RunningHub / 剪映 使用
```

V1 默认不自动跑完整链路，每一步都应允许用户查看、编辑、保存和重试。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、Pinia、Vue Router、Konva
- 后端：FastAPI、SQLAlchemy Async、Alembic、Pydantic Settings
- 数据库：PostgreSQL
- 缓存与任务：Redis、Celery
- 对象存储：MinIO
- 桌面壳：Electron

## 本地启动方式

### 基础设施

```bash
./scripts/start.sh
```

### 后端

```bash
cd backend
uv sync
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档地址：

```text
http://localhost:8000/docs
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发地址通常为：

```text
http://localhost:3000
```

如果端口被占用，Vite 会自动切换到下一个可用端口。

## Docker 启动方式

```bash
docker compose up -d
```

生产配置示例：

```bash
docker compose -f docker-compose.prod.yml up -d
```

常用服务地址：

- 前端应用：http://localhost:3000 或 http://localhost:3001
- API 文档：http://localhost:8000/docs
- MinIO 控制台：http://localhost:9001

## 当前已完成功能

- 用户注册、登录和 JWT 鉴权
- 项目管理、文件上传和文本导入
- 长文本解析、章节与段落处理
- 角色、场景、分镜、关键帧等原有 Movie 链路
- 画布工作台基础能力
- API 密钥管理
- MinIO 文件存储
- 剪映和视频导出相关基础接口
- Electron 打包配置

## 当前未完成功能

- Txtovideo 专用短剧数据模型
- 线性短剧工作台 MVP
- 集中化 Txtovideo 提示词模板
- Txtovideo ZIP 素材包导出
- 步骤状态机、失败重试和 stale 标记
- ComfyUI / RunningHub Provider 对接
- 音频驱动视频模式
- 文本与 JSON 层面的质量评分和自动修复

## 开发路线图

1. Phase 0：品牌统一与入口收口
2. Phase 1：短剧业务数据结构固化
3. Phase 2：短剧主流程 MVP
4. Phase 3：Txtovideo 提示词模板体系
5. Phase 4：导出中心和 ZIP 素材包
6. Phase 5：任务状态机与步骤重试
7. Phase 6：画布工作台收口
8. Phase 7：ComfyUI / RunningHub 对接
9. Phase 8：音频驱动版本
10. Phase 9：质量评分与自动修复
11. Phase 10：桌面版与本地部署优化
12. Phase 11：生产效率优化
13. Phase 12：V2 画布化重构评估

## License

本项目使用 Apache License 2.0。详见 [LICENSE](LICENSE)。
