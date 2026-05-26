# Txtovideo Studio V2 评估文档

更新时间：2026-05-26

---

## 1. V1 现状总结（Phase 0–11）

### 已完成功能

| Phase | 内容 | 状态 |
|-------|------|------|
| 0 | 品牌统一与入口收口 | ✅ |
| 1 | 短剧数据结构文档和最小数据模型 | ✅ |
| 2 | 短剧工作台 MVP 页面 | ✅ |
| 3 | Txtovideo 专用提示词模板 | ✅ |
| 4 | 导出 ZIP 包 | 待定 |
| 5–9 | 工作流增强、质量评分、画布编辑器、音频轨道 | ✅ |
| 10 | 桌面版优化（本地启动脚本、Docker 开发配置） | ✅ |
| 11 | 生产效率优化（项目模板预设、模板 API） | ✅ |

### V1 架构特征

- **后端**：FastAPI + SQLAlchemy（异步） + PostgreSQL + Redis + MinIO
- **前端**：Vue 3 + Element Plus + Pinia + Konva.js（画布）
- **数据模型**：Txtovideo 线性工作流（9 步骤依赖链） + Canvas 画布（文档/节点/连接/生成记录）
- **工作台**：`ShortDramaWorkbench.vue` — 线性步骤式 UI，草稿保存到浏览器 localStorage
- **画布编辑器**：`CanvasEditor.vue` — 基于 Konva.js 的节点编辑器，支持拖拽、连线、批量操作
- **认证**：JWT Bearer Token，30 分钟有效期

### V1 已知局限

1. **线性工作流**：9 步骤严格依赖链，无法跳步或并行，灵活性不足
2. **草稿存储**：工作台产物保存在浏览器 localStorage，无法跨设备同步
3. **画布与工作流割裂**：画布编辑器和工作台是两个独立页面，数据不互通
4. **模板硬编码**：项目模板和提示词模板均为静态数据，无法用户自定义
5. **无实时协作**：单用户操作，无 WebSocket 推送
6. **导出能力有限**：ZIP 导出尚未完整实现

---

## 2. V2 画布化重构目标

### 核心愿景

将线性工作流升级为**画布驱动的可视化创作流**，让用户在同一个画布界面中完成从文本到视频的全部创作流程。

### 具体目标

1. **统一入口**：工作台和画布合并为单一页面，消除页面切换
2. **自由布局**：节点可自由拖拽、分组、缩放，不再受线性步骤约束
3. **并行处理**：支持多分支并行生成，如同时生成图片和视频提示词
4. **实时预览**：节点内嵌预览，无需跳转即可查看生成结果
5. **模板驱动**：项目模板自动生成画布布局，一键开始创作
6. **协作就绪**：WebSocket 基础设施，为多人协作预留接口

---

## 3. 技术评估

### 3.1 画布引擎对比

| 维度 | Konva.js（当前） | Fabric.js | 自研 Canvas |
|------|------------------|-----------|-------------|
| **当前集成** | ✅ 已集成，V1 画布编辑器使用中 | ❌ 需替换 | ❌ 从零开始 |
| **节点编辑** | 需自行实现连线逻辑 | 偏向图像编辑 | 完全可控 |
| **性能** | 中等，1000+ 节点需优化 | 中等 | 可针对性优化 |
| **社区生态** | 活跃，React/Vue 封装可用 | 活跃，偏设计工具 | 无 |
| **学习成本** | 团队已熟悉 | 中等 | 高 |
| **维护成本** | 低（社区维护） | 低 | 高（全部自维护） |
| **扩展性** | 插件体系，自定义 Shape | 丰富 API | 完全自由 |

### 3.2 推荐方案：Konva.js + 自定义节点系统

**理由**：

1. V1 已基于 Konva.js 构建画布编辑器，迁移成本最低
2. Konva 的 Shape/Group 体系足够灵活，可封装自定义节点组件
3. 连线逻辑已在 V1 中实现（`CanvasConnection` 模型 + 渲染），可复用
4. 性能可通过虚拟化（viewport culling）和分层渲染优化

**需增强的能力**：

- 节点内嵌表单/预览（当前节点仅展示标题和缩略图）
- 分组折叠/展开
- 小地图导航
- 自动布局算法（dagre/elkjs）

### 3.3 替代方案：Vue Flow

Vue Flow 是基于 Vue 3 的节点编辑器库，提供开箱即用的节点/连线/小地图功能。

| 维度 | Vue Flow | Konva.js 自研 |
|------|----------|---------------|
| 开发速度 | 快，开箱即用 | 慢，需自建 |
| 定制性 | 中等，受组件约束 | 高，完全可控 |
| 性能 | 中等 | 可针对性优化 |
| 与现有代码兼容 | 需替换画布层 | 无缝衔接 |

**结论**：如果 V2 时间紧迫且节点形态相对标准化，可考虑 Vue Flow 快速落地；如果需要深度定制节点交互（内嵌表单、实时预览、拖拽生成），继续使用 Konva.js 更合适。

---

## 4. 数据模型迁移方案

### 4.1 V1 现有模型

```
TxtovideoProject
├── WorkflowStep (9 步线性依赖)
├── TxtovideoCharacter
├── TxtovideoScene
├── TxtovideoProp
├── TxtovideoShot (分镜)
│   ├── TxtovideoImagePrompt
│   └── TxtovideoVideoPrompt
└── TxtovideoQualityReport

CanvasDocument
├── CanvasItem (节点)
├── CanvasConnection (连线)
└── CanvasItemGeneration (生成记录)
```

### 4.2 V2 目标模型

```
Project (统一项目)
├── CanvasDocument (画布文档，1:1)
│   ├── CanvasItem (增强节点)
│   │   ├── item_type: 扩展为 workflow_step | asset | note
│   │   ├── content_json: 承载步骤配置/产物数据
│   │   └── CanvasItemGeneration[]
│   ├── CanvasConnection (增强连线)
│   │   └── connection_type: data_flow | dependency | reference
│   └── CanvasGroup (新增：分组)
└── ProjectTemplate (模板快照)
```

### 4.3 迁移策略

1. **Phase A — 数据库扩展**：
   - `CanvasItem` 新增 `item_type` 枚举值 `workflow_step`
   - `CanvasConnection` 新增 `connection_type` 字段
   - 新增 `canvas_groups` 表（分组折叠/展开）
   - `TxtovideoProject` 与 `CanvasDocument` 建立 1:1 关联

2. **Phase B — 数据迁移脚本**：
   - 将现有 `TxtovideoProject` 的线性步骤转换为画布节点
   - 步骤依赖关系转换为画布连线
   - 角色提取/场景提取/道具提取产物转换为 `asset` 类型节点
   - 保留旧表不删除，通过视图兼容 V1 API

3. **Phase C — API 兼容层**：
   - V1 API（`/txtovideo/projects/{id}/steps`）继续可用
   - V2 API（`/canvas/documents/{id}/items`）为新的统一入口
   - 双写期间通过事件同步保证一致性

### 4.4 迁移时间估算

| 阶段 | 工作量 | 时间 |
|------|--------|------|
| Phase A：数据库扩展 | 3 个迁移文件 | 1 天 |
| Phase B：数据迁移脚本 | 1 个迁移 + 回滚 | 2 天 |
| Phase C：API 兼容层 | 适配器模式 | 3 天 |

---

## 5. 前端架构重构方案

### 5.1 当前架构

```
ShortDramaWorkbench.vue (线性工作台)
  ├── StepPanel (步骤面板)
  └── OutputPanel (产物面板)

CanvasEditor.vue (画布编辑器)
  ├── KonvaCanvasStage (Konva 画布)
  ├── CanvasWorkbenchLayout (工具栏)
  └── Canvas*Studio (属性面板)
```

### 5.2 V2 目标架构

```
UnifiedWorkbench.vue (统一工作台)
  ├── CanvasViewport (画布视口)
  │   ├── KonvaCanvasStage (增强画布)
  │   ├── MiniMap (小地图)
  │   └── AutoLayout (自动布局)
  ├── NodePalette (节点面板 — 拖拽添加)
  ├── PropertyPanel (属性面板 — 上下文感知)
  │   ├── StepConfigPanel (步骤配置)
  │   ├── AssetPreviewPanel (资产预览)
  │   └── GenerationPanel (生成控制)
  └── TemplateLauncher (模板启动器)
```

### 5.3 组件拆分

| 新组件 | 职责 | 来源 |
|--------|------|------|
| `UnifiedWorkbench.vue` | 统一工作台容器 | 新建 |
| `CanvasViewport.vue` | 画布视口 + 小地图 | 重构 `CanvasEditor.vue` |
| `NodePalette.vue` | 节点拖拽面板 | 新建 |
| `PropertyPanel.vue` | 上下文属性面板 | 合并 `Canvas*Studio` |
| `StepConfigPanel.vue` | 工作流步骤配置 | 从 `ShortDramaWorkbench` 提取 |
| `AssetPreviewPanel.vue` | 图片/视频预览 | 新建 |
| `GenerationPanel.vue` | 生成任务控制 | 从 `CanvasItemStudio` 提取 |
| `TemplateLauncher.vue` | 模板选择和启动 | 新建 |

### 5.4 状态管理

V1 现状：
- 画布状态：组件内 `ref()` 管理
- 工作台状态：`localStorage` 草稿

V2 方案：
- 统一使用 Pinia store
- 新增 `useCanvasStore`：画布节点/连线/视口状态
- 新增 `useWorkflowStore`：工作流步骤状态（从画布节点派生）
- 新增 `useGenerationStore`：生成任务队列和状态
- 保留 `useAuthStore`：认证状态

---

## 6. 时间线估算

### 总体时间：8–10 周

| 阶段 | 内容 | 时间 | 依赖 |
|------|------|------|------|
| **Sprint 1** | 数据模型扩展 + 迁移脚本 | 1 周 | 无 |
| **Sprint 2** | 画布节点增强（内嵌表单/预览） | 2 周 | Sprint 1 |
| **Sprint 3** | 统一工作台 UI 框架 | 2 周 | Sprint 2 |
| **Sprint 4** | 工作流步骤 → 画布节点迁移 | 1 周 | Sprint 3 |
| **Sprint 5** | 模板启动器 + 自动布局 | 1 周 | Sprint 4 |
| **Sprint 6** | API 兼容层 + 集成测试 | 1 周 | Sprint 5 |
| **Sprint 7** | 性能优化 + Bug 修复 | 1 周 | Sprint 6 |
| **缓冲** | 预留 | 1 周 | — |

### 里程碑

- **M1（第 1 周末）**：数据库迁移完成，V1 API 不受影响
- **M2（第 3 周末）**：画布节点支持内嵌表单和预览
- **M3（第 5 周末）**：统一工作台可运行，线性工作流可迁移到画布
- **M4（第 7 周末）**：模板启动器可用，V2 功能完整
- **M5（第 8 周末）**：V2 发布就绪

---

## 7. 风险评估

### 高风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Konva.js 大规模节点性能 | 画布卡顿，用户体验差 | 虚拟化渲染、viewport culling、节点懒加载 |
| 数据迁移丢失 | 用户项目数据不完整 | 双写 + 校验脚本 + 回滚方案 |
| V1/V2 API 共存复杂度 | 前端状态不一致 | 明确 API 版本边界，逐步废弃 V1 |

### 中风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 节点内嵌表单交互复杂 | 开发周期延长 | 先实现只读预览，再迭代可编辑表单 |
| 自动布局算法不理想 | 画布布局混乱 | 提供"重置布局"按钮，允许手动调整 |
| 模板系统扩展性不足 | 无法满足多样化需求 | 模板 JSON Schema 化，支持用户自定义 |

### 低风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 小地图导航精度 | 定位偏差 | 使用 Konva Stage 坐标系直接映射 |
| 分组折叠动画 | 视觉闪烁 | CSS transition + requestAnimationFrame |

---

## 附录：V2 技术栈确认

| 层 | 技术 | 版本 |
|----|------|------|
| 前端框架 | Vue 3 | 3.x |
| UI 组件库 | Element Plus | 最新 |
| 画布引擎 | Konva.js | 最新 |
| 状态管理 | Pinia | 最新 |
| 后端框架 | FastAPI | 0.100+ |
| ORM | SQLAlchemy | 2.x（异步） |
| 数据库 | PostgreSQL | 16 |
| 缓存 | Redis | 7 |
| 对象存储 | MinIO | 最新 |
| 容器化 | Docker + Docker Compose | 最新 |
