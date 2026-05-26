<template>
  <div class="workbench-page">
    <template v-if="!isWorkbenchMode">
      <section class="page-header">
        <div>
          <h1>短剧工作台</h1>
          <p>小说短剧工作站</p>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            :icon="Folder"
            @click="router.push('/projects')"
          >
            选择项目
          </el-button>
        </div>
      </section>

      <section class="workflow-band">
        <el-steps
          :active="0"
          finish-status="success"
          align-center
        >
          <el-step
            v-for="step in steps"
            :key="step.id"
            :title="step.shortTitle"
          />
        </el-steps>
      </section>

      <section class="entry-grid">
        <button
          class="entry-item primary"
          type="button"
          @click="router.push('/projects')"
        >
          <el-icon><VideoCamera /></el-icon>
          <span>进入项目管理</span>
        </button>
        <button
          class="entry-item"
          type="button"
          @click="router.push('/canvas')"
        >
          <el-icon><Share /></el-icon>
          <span>打开画布工作台</span>
        </button>
        <button
          class="entry-item"
          type="button"
          @click="router.push('/exports')"
        >
          <el-icon><Download /></el-icon>
          <span>查看导出中心</span>
        </button>
      </section>
    </template>

    <template v-else>
      <section class="project-header">
        <div class="project-title-group">
          <el-button
            :icon="ArrowLeft"
            plain
            @click="router.push({ name: 'ProjectDetail', params: { projectId: resolvedProjectId } })"
          >
            项目详情
          </el-button>
          <div>
            <h1>{{ projectTitle }}</h1>
            <p>短剧工作台</p>
          </div>
        </div>
        <div class="project-meta">
          <el-tag
            effect="plain"
            type="info"
          >
            本地草稿
          </el-tag>
          <div class="progress-box">
            <span>{{ completionPercent }}%</span>
            <el-progress
              :percentage="completionPercent"
              :show-text="false"
              :stroke-width="8"
            />
          </div>
        </div>
      </section>

      <section
        v-if="projectLoading"
        class="loading-panel"
      >
        <el-skeleton
          :rows="10"
          animated
        />
      </section>

      <section
        v-else
        class="workbench-layout"
      >
        <aside class="step-sidebar">
          <button
            v-for="(step, index) in steps"
            :key="step.id"
            class="step-button"
            :class="{
              active: activeStepIndex === index,
              saved: isStepSaved(step.id)
            }"
            type="button"
            @click="goToStep(index)"
          >
            <span class="step-index">{{ index + 1 }}</span>
            <span class="step-copy">
              <strong>{{ step.title }}</strong>
              <small>{{ step.caption }}</small>
            </span>
            <el-icon
              v-if="getStepStatus(step) === 'success'"
              class="step-check"
              color="var(--el-color-success)"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else-if="getStepStatus(step) === 'failed'"
              class="step-check"
              color="var(--el-color-danger)"
            >
              <CircleClose />
            </el-icon>
            <el-icon
              v-else-if="getStepStatus(step) === 'stale'"
              class="step-check"
              color="var(--el-color-warning)"
            >
              <Warning />
            </el-icon>
            <el-icon
              v-else-if="getStepStatus(step) === 'running'"
              class="step-check step-spin"
              color="var(--el-color-primary)"
            >
              <Loading />
            </el-icon>
          </button>
        </aside>

        <main class="step-editor">
          <div class="step-editor-header">
            <div>
              <h2>{{ currentStep.title }}</h2>
              <p>{{ currentStep.caption }}</p>
            </div>
            <el-tag
              :type="currentValidation.valid ? 'success' : 'warning'"
              effect="plain"
            >
              {{ currentValidation.valid ? '可保存' : '需修正' }}
            </el-tag>
          </div>

          <section class="input-panel">
            <div class="panel-title">
              <span>输入</span>
              <el-tag
                size="small"
                effect="plain"
              >
                {{ currentStep.inputLabel }}
              </el-tag>
            </div>
            <pre>{{ currentInputPreview }}</pre>
          </section>

          <section class="output-panel">
            <div class="panel-title">
              <span>输出</span>
              <el-tag
                v-if="currentStep.format"
                size="small"
                type="info"
                effect="plain"
              >
                {{ currentStep.format }}
              </el-tag>
            </div>

            <div
              v-if="currentStep.id === 'source'"
              class="source-editor"
            >
              <el-row :gutter="12">
                <el-col
                  :xs="24"
                  :md="8"
                >
                  <el-form-item label="时代">
                    <el-select
                      v-model="workbench.source.era"
                      class="full-width"
                      @change="markStepDirty('source')"
                    >
                      <el-option
                        label="中国古代"
                        value="中国古代"
                      />
                      <el-option
                        label="民国"
                        value="民国"
                      />
                      <el-option
                        label="现代"
                        value="现代"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col
                  :xs="24"
                  :md="8"
                >
                  <el-form-item label="风格">
                    <el-select
                      v-model="workbench.source.style"
                      class="full-width"
                      @change="markStepDirty('source')"
                    >
                      <el-option
                        label="古风真人写实"
                        value="古风真人写实"
                      />
                      <el-option
                        label="电视剧电影感"
                        value="电视剧电影感"
                      />
                      <el-option
                        label="悬疑冷调写实"
                        value="悬疑冷调写实"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col
                  :xs="24"
                  :md="8"
                >
                  <el-form-item label="平台">
                    <el-select
                      v-model="workbench.source.platform"
                      class="full-width"
                      @change="markStepDirty('source')"
                    >
                      <el-option
                        label="抖音/视频号"
                        value="抖音/视频号"
                      />
                      <el-option
                        label="Bilibili"
                        value="Bilibili"
                      />
                      <el-option
                        label="自定义"
                        value="自定义"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="12">
                <el-col
                  :xs="24"
                  :md="12"
                >
                  <el-form-item label="画幅">
                    <el-select
                      v-model="workbench.source.aspectRatio"
                      class="full-width"
                      @change="markStepDirty('source')"
                    >
                      <el-option
                        label="9:16"
                        value="9:16"
                      />
                      <el-option
                        label="16:9"
                        value="16:9"
                      />
                      <el-option
                        label="1:1"
                        value="1:1"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col
                  :xs="24"
                  :md="12"
                >
                  <el-form-item label="单镜头时长">
                    <el-select
                      v-model="workbench.source.durationRange"
                      class="full-width"
                      @change="markStepDirty('source')"
                    >
                      <el-option
                        label="6-8 秒"
                        value="6-8 秒"
                      />
                      <el-option
                        label="8-12 秒"
                        value="8-12 秒"
                      />
                      <el-option
                        label="12-15 秒"
                        value="12-15 秒"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="source-toolbar">
                <el-upload
                  accept=".txt,text/plain"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleSourceFile"
                >
                  <el-button :icon="Upload">
                    导入 TXT
                  </el-button>
                </el-upload>
                <span>{{ sourceMetrics }}</span>
              </div>

              <el-input
                v-model="currentOutput"
                type="textarea"
                resize="vertical"
                :autosize="{ minRows: 16, maxRows: 24 }"
                placeholder="粘贴或导入小说原文"
              />
            </div>

            <el-input
              v-else
              v-model="currentOutput"
              type="textarea"
              resize="vertical"
              :autosize="{ minRows: 20, maxRows: 28 }"
              :placeholder="currentStep.placeholder"
            />

            <div
              v-if="currentStep.id === 'quality' && qualityResult"
              class="quality-score-panel"
            >
              <div class="quality-score-header">
                <div class="quality-score-number">
                  <span class="score-value">{{ qualityResult.overall_score }}</span>
                  <span class="score-label">分</span>
                </div>
                <el-tag
                  :type="qualityResult.grade === 'A' || qualityResult.grade === 'B' ? 'success' : qualityResult.grade === 'C' ? 'warning' : 'danger'"
                  size="large"
                  effect="dark"
                >
                  {{ qualityResult.grade }} 级
                </el-tag>
              </div>

              <div
                v-if="qualityResult.fix_suggestions && qualityResult.fix_suggestions.length > 0"
                class="quality-fix-list"
              >
                <strong>修复建议</strong>
                <ul>
                  <li
                    v-for="(fix, fixIdx) in qualityResult.fix_suggestions"
                    :key="fixIdx"
                  >
                    <el-tag
                      size="small"
                      type="warning"
                      effect="plain"
                    >
                      {{ fix.section }}
                    </el-tag>
                    {{ fix.check_name }}：{{ fix.suggestion }}
                  </li>
                </ul>
              </div>

              <div class="quality-section-scores">
                <div
                  v-for="(section, sectionKey) in qualityResult.sections"
                  :key="sectionKey"
                  class="quality-section-item"
                >
                  <span class="section-name">{{ sectionKey }}</span>
                  <el-progress
                    :percentage="section.score"
                    :stroke-width="10"
                    :color="section.score >= 75 ? '#16a34a' : section.score >= 50 ? '#e6a23c' : '#f56c6c'"
                  />
                </div>
              </div>
            </div>
          </section>
        </main>

        <aside class="preview-panel">
          <div class="preview-header">
            <h3>预览</h3>
            <el-tag
              :type="isStepSaved(currentStep.id) ? 'success' : 'info'"
              effect="plain"
            >
              {{ isStepSaved(currentStep.id) ? '已保存' : '未保存' }}
            </el-tag>
          </div>

          <div
            v-if="currentStep.outputKey"
            class="template-box"
          >
            <div class="template-title">
              <strong>提示词模板</strong>
              <el-tag
                size="small"
                effect="plain"
              >
                {{ currentPromptUsed?.version || '未生成' }}
              </el-tag>
            </div>
            <el-select
              v-model="workbench.selectedTemplates[currentStep.outputKey]"
              class="full-width"
              :loading="promptTemplateLoading"
              @change="handleTemplateChange"
            >
              <el-option
                v-for="template in templatesForCurrentStep"
                :key="template.template_id"
                :label="`${template.name} ${template.version}`"
                :value="template.template_id"
              />
            </el-select>
            <p>
              {{ currentPromptUsed ? `已使用 ${currentPromptUsed.filename}` : '重新生成后会记录 prompt_used' }}
            </p>
          </div>

          <pre class="json-preview">{{ previewContent }}</pre>

          <div class="validation-box">
            <strong>检查</strong>
            <ul>
              <li
                v-for="message in currentValidation.messages"
                :key="message"
              >
                {{ message }}
              </li>
            </ul>
          </div>

          <div class="side-actions">
            <el-button
              :icon="Refresh"
              @click="handleRegenerate"
            >
              重新生成
            </el-button>
            <el-button
              type="primary"
              :icon="Check"
              @click="saveCurrent"
            >
              保存
            </el-button>
            <el-button
              type="success"
              :icon="ArrowRight"
              :disabled="activeStepIndex === steps.length - 1"
              @click="handleNext"
            >
              下一步
            </el-button>
            <el-button
              v-if="currentStep.id === 'export'"
              :icon="Download"
              @click="downloadExportDraft"
            >
              下载清单
            </el-button>
            <el-button
              v-if="currentStep.id === 'export'"
              type="primary"
              :icon="Download"
              :loading="zipExporting"
              @click="downloadExportZip"
            >
              导出ZIP包
            </el-button>
            <el-button
              v-if="currentStep.id === 'export'"
              :icon="VideoCamera"
              @click="generateCanvas"
            >
              生成画布
            </el-button>
            <el-button
              v-if="currentStep.id === 'quality'"
              :icon="Refresh"
              :loading="qualityScoring"
              @click="runQualityScore"
            >
              重新评分
            </el-button>
          </div>
        </aside>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CircleClose,
  Download,
  Folder,
  Loading,
  Refresh,
  Share,
  Upload,
  VideoCamera,
  Warning
} from '@element-plus/icons-vue'
import { useProjectsStore } from '@/stores/projects'
import { txtovideoPromptsService } from '@/services/txtovideoPrompts'
import { txtovideoProjectsService } from '@/services/txtovideoProjects'
import { post } from '@/services/api'

const props = defineProps({
  projectId: {
    type: String,
    default: ''
  }
})

const router = useRouter()
const route = useRoute()
const projectsStore = useProjectsStore()

const NEGATIVE_PROMPT = '现代物品、现代建筑、现代服装、手机、电脑、电灯、眼镜、手表、拉链、塑料、欧美人、卡通、动漫、3D渲染、游戏风、低质量、模糊、畸形、多肢体、多人错误、性别错误'
const LTX_AVOID_RULES = [
  '单镜头只描述一个连续动作',
  '避免跨场景跳切',
  '避免角色数量变化',
  '避免服装和发型变化',
  '避免镜头内出现文字',
  '避免夸张运镜和高速旋转'
]

const TEMPLATE_STEP_MAP = {
  script: 'script_adapt',
  characters: 'character_extract',
  scenes: 'scene_extract',
  props: 'prop_extract',
  storyboard: 'storyboard_cap_desc_promopt',
  imagePrompts: 'image_prompt',
  videoPrompts: 'video_prompt_ltx',
  quality: 'quality_score',
  export: 'rewrite_fix'
}

const STEP_NAME_MAP = {
  script: 'script_adapt',
  characters: 'character_extract',
  scenes: 'scene_extract',
  props: 'prop_extract',
  storyboard: 'storyboard_generate',
  imagePrompts: 'image_prompt_generate',
  videoPrompts: 'video_prompt_generate',
  quality: 'quality_score',
  export: 'export_package'
}

const FALLBACK_TEMPLATES = [
  { template_id: 'script_adapt', name: '剧本改编', version: 'v1', category: 'script', filename: 'script_adapt_v1.md' },
  { template_id: 'character_extract', name: '角色提取', version: 'v1', category: 'asset', filename: 'character_extract_v1.md' },
  { template_id: 'scene_extract', name: '场景提取', version: 'v1', category: 'asset', filename: 'scene_extract_v1.md' },
  { template_id: 'prop_extract', name: '道具提取', version: 'v1', category: 'asset', filename: 'prop_extract_v1.md' },
  { template_id: 'storyboard_cap_desc_promopt', name: '分镜 cap/desc_promopt', version: 'v1', category: 'storyboard', filename: 'storyboard_cap_desc_promopt_v1.md' },
  { template_id: 'image_prompt', name: '图片提示词', version: 'v1', category: 'image', filename: 'image_prompt_v1.md' },
  { template_id: 'video_prompt_ltx', name: 'LTX 视频提示词', version: 'v1', category: 'video', filename: 'video_prompt_ltx_v1.md' },
  { template_id: 'video_prompt_seedance', name: 'Seedance 视频提示词', version: 'v1', category: 'video', filename: 'video_prompt_seedance_v1.md' },
  { template_id: 'quality_score', name: '质量评分', version: 'v1', category: 'quality', filename: 'quality_score_v1.md' },
  { template_id: 'rewrite_fix', name: '修复改写', version: 'v1', category: 'quality', filename: 'rewrite_fix_v1.md' }
]

const steps = [
  {
    id: 'source',
    title: '原文输入',
    shortTitle: '原文',
    caption: '项目原文和基础制作参数',
    inputLabel: '项目',
    format: 'Text',
    placeholder: '粘贴或导入小说原文'
  },
  {
    id: 'script',
    title: '剧本改编',
    shortTitle: '剧本',
    caption: '短剧分场、对白和动作描述',
    inputLabel: '原文',
    outputKey: 'script',
    format: 'Text',
    placeholder: '编辑短剧剧本'
  },
  {
    id: 'characters',
    title: '角色资产',
    shortTitle: '角色',
    caption: '角色设定、外观和一致性锚点',
    inputLabel: '剧本',
    outputKey: 'characters',
    format: 'JSON',
    expectsArray: true,
    placeholder: '编辑角色资产 JSON'
  },
  {
    id: 'scenes',
    title: '场景资产',
    shortTitle: '场景',
    caption: '场景空间、时代和氛围设定',
    inputLabel: '剧本',
    outputKey: 'scenes',
    format: 'JSON',
    expectsArray: true,
    placeholder: '编辑场景资产 JSON'
  },
  {
    id: 'props',
    title: '道具资产',
    shortTitle: '道具',
    caption: '关键道具和剧情用途',
    inputLabel: '剧本',
    outputKey: 'props',
    format: 'JSON',
    expectsArray: true,
    placeholder: '编辑道具资产 JSON'
  },
  {
    id: 'storyboard',
    title: '分镜生成',
    shortTitle: '分镜',
    caption: '镜头编号、主题、画面和运镜',
    inputLabel: '剧本 + 资产',
    outputKey: 'storyboard',
    format: 'JSON',
    expectsArray: true,
    placeholder: '编辑分镜 JSON'
  },
  {
    id: 'imagePrompts',
    title: '图片提示词',
    shortTitle: '图片',
    caption: '首帧图生成提示词和负面词',
    inputLabel: '分镜',
    outputKey: 'imagePrompts',
    format: 'JSON',
    expectsArray: true,
    placeholder: '编辑图片提示词 JSON'
  },
  {
    id: 'videoPrompts',
    title: '视频提示词',
    shortTitle: '视频',
    caption: 'LTX 视频提示词和运动约束',
    inputLabel: '分镜 + 图片提示词',
    outputKey: 'videoPrompts',
    format: 'JSON',
    expectsArray: true,
    placeholder: '编辑视频提示词 JSON'
  },
  {
    id: 'quality',
    title: '质量检查',
    shortTitle: '质检',
    caption: '字段完整性、时代一致性和导出阻断项',
    inputLabel: '全部产物',
    outputKey: 'quality',
    format: 'JSON',
    placeholder: '编辑质量检查报告 JSON'
  },
  {
    id: 'export',
    title: '导出',
    shortTitle: '导出',
    caption: '素材包清单和 manifest 预览',
    inputLabel: '通过质检的产物',
    outputKey: 'export',
    format: 'JSON',
    placeholder: '编辑导出清单 JSON'
  }
]

const project = ref(null)
const projectLoading = ref(false)
const zipExporting = ref(false)
const qualityResult = ref(null)
const qualityScoring = ref(false)
const stepStates = ref({})
const activeStepIndex = ref(0)
const savedStepIds = ref([])
const promptTemplates = ref([])
const promptTemplateLoading = ref(false)
const workbench = ref(createDefaultWorkbench())

const resolvedProjectId = computed(() => props.projectId || String(route.params.projectId || ''))
const isWorkbenchMode = computed(() => Boolean(resolvedProjectId.value))
const projectTitle = computed(() => project.value?.title || `项目 ${resolvedProjectId.value}`)
const storageKey = computed(() => `txtovideo-workbench:${resolvedProjectId.value}`)
const currentStep = computed(() => steps[activeStepIndex.value])
const completionPercent = computed(() => Math.round((savedStepIds.value.length / steps.length) * 100))
const currentTemplateId = computed(() => TEMPLATE_STEP_MAP[currentStep.value.outputKey] || '')
const templatesForCurrentStep = computed(() => {
  if (!currentTemplateId.value) {
    return []
  }
  if (currentStep.value.id === 'videoPrompts') {
    return promptTemplates.value.filter(template => template.category === 'video')
  }
  return promptTemplates.value.filter(template => template.template_id === currentTemplateId.value)
})
const currentPromptUsed = computed(() => {
  const outputKey = currentStep.value.outputKey
  if (!outputKey) {
    return null
  }
  return workbench.value.promptUsed[outputKey] || null
})

const currentOutput = computed({
  get() {
    if (currentStep.value.id === 'source') {
      return workbench.value.source.text
    }
    return workbench.value.outputs[currentStep.value.outputKey] || ''
  },
  set(value) {
    if (currentStep.value.id === 'source') {
      workbench.value.source.text = value
    } else {
      workbench.value.outputs[currentStep.value.outputKey] = value
    }
    markStepDirty(currentStep.value.id)
  }
})

const sourceMetrics = computed(() => {
  const text = normalizeText(workbench.value.source.text)
  const words = text.replace(/\s/g, '').length
  const paragraphs = text.split(/\n+/).filter(Boolean).length
  const shots = Math.max(1, Math.ceil(words / 120))
  return `${words} 字 · ${paragraphs} 段 · 约 ${shots} 个镜头`
})

const currentInputPreview = computed(() => {
  const stepId = currentStep.value.id
  if (stepId === 'source') {
    return compactPreview(formatJson({
      project_id: resolvedProjectId.value,
      title: projectTitle.value,
      file_name: project.value?.file_name || workbench.value.source.fileName || null,
      era: workbench.value.source.era,
      style: workbench.value.source.style,
      platform: workbench.value.source.platform,
      aspect_ratio: workbench.value.source.aspectRatio,
      duration_range: workbench.value.source.durationRange
    }))
  }
  if (stepId === 'script') {
    return compactPreview(workbench.value.source.text || '暂无原文')
  }
  if (['characters', 'scenes', 'props', 'storyboard'].includes(stepId)) {
    return compactPreview(workbench.value.outputs.script || '暂无剧本')
  }
  if (['imagePrompts', 'videoPrompts'].includes(stepId)) {
    return compactPreview(workbench.value.outputs.storyboard || '暂无分镜')
  }
  if (stepId === 'quality') {
    return compactPreview(formatJson({
      characters: countJsonArray('characters'),
      scenes: countJsonArray('scenes'),
      props: countJsonArray('props'),
      storyboard: countJsonArray('storyboard'),
      image_prompts: countJsonArray('imagePrompts'),
      video_prompts: countJsonArray('videoPrompts')
    }))
  }
  return compactPreview(formatJson({
    manifest: true,
    quality_status: readQualityStatus(),
    shot_count: countJsonArray('storyboard')
  }))
})

const previewContent = computed(() => {
  if (currentStep.value.id === 'source') {
    return compactPreview(workbench.value.source.text || '暂无原文')
  }
  if (currentStep.value.format === 'JSON') {
    const parsed = tryParseJson(currentOutput.value)
    if (parsed.ok) {
      return compactPreview(formatJson(parsed.value), 6000)
    }
  }
  return compactPreview(currentOutput.value || '暂无输出', 6000)
})

const currentValidation = computed(() => validateStep(currentStep.value))

const _pendingTimers = []

onMounted(async () => {
  await loadPromptTemplates()
  if (isWorkbenchMode.value) {
    await initialiseWorkbench()
  }
})

watch(resolvedProjectId, async (nextId, prevId) => {
  if (nextId && nextId !== prevId) {
    await initialiseWorkbench()
  }
})

function createDefaultWorkbench() {
  return {
    source: {
      text: '',
      fileName: '',
      genre: '古风权谋',
      era: '中国古代',
      style: '古风真人写实',
      platform: '抖音/视频号',
      aspectRatio: '9:16',
      durationRange: '8-12 秒'
    },
    outputs: {
      script: '',
      characters: formatJson([]),
      scenes: formatJson([]),
      props: formatJson([]),
      storyboard: formatJson([]),
      imagePrompts: formatJson([]),
      videoPrompts: formatJson([]),
      quality: formatJson({
        status: 'draft',
        checks: []
      }),
      export: formatJson({
        package_name: '',
        files: []
      })
    },
    selectedTemplates: buildDefaultTemplateSelection(),
    promptUsed: {},
    updatedAt: null
  }
}

function buildDefaultTemplateSelection() {
  return Object.fromEntries(
    Object.entries(TEMPLATE_STEP_MAP).map(([outputKey, templateId]) => [outputKey, templateId])
  )
}

async function loadPromptTemplates() {
  promptTemplateLoading.value = true
  try {
    promptTemplates.value = await txtovideoPromptsService.listTemplates()
  } catch (error) {
    console.warn('提示词模板接口不可用，使用内置模板清单:', error)
    promptTemplates.value = FALLBACK_TEMPLATES
  } finally {
    promptTemplateLoading.value = false
  }
}

async function initialiseWorkbench() {
  projectLoading.value = true
  workbench.value = loadDraft()
  activeStepIndex.value = 0

  try {
    project.value = await projectsStore.getProject(resolvedProjectId.value)

    try {
      const serverDraft = await txtovideoProjectsService.getDraft(resolvedProjectId.value)
      if (serverDraft && serverDraft.outputs) {
        workbench.value.source = serverDraft.source || workbench.value.source
        if (serverDraft.outputs.script) workbench.value.outputs.script = serverDraft.outputs.script
        if (serverDraft.outputs.characters) workbench.value.outputs.characters = formatJson(serverDraft.outputs.characters)
        if (serverDraft.outputs.scenes) workbench.value.outputs.scenes = formatJson(serverDraft.outputs.scenes)
        if (serverDraft.outputs.props) workbench.value.outputs.props = formatJson(serverDraft.outputs.props)
        if (serverDraft.outputs.storyboard) workbench.value.outputs.storyboard = formatJson(serverDraft.outputs.storyboard)
        if (serverDraft.outputs.imagePrompts) workbench.value.outputs.imagePrompts = formatJson(serverDraft.outputs.imagePrompts)
        if (serverDraft.outputs.videoPrompts) workbench.value.outputs.videoPrompts = formatJson(serverDraft.outputs.videoPrompts)
        if (serverDraft.outputs.quality) workbench.value.outputs.quality = formatJson(serverDraft.outputs.quality)
        persistDraft()
      }
    } catch (draftError) {
      console.warn('服务端草稿加载失败，使用本地草稿:', draftError)
    }

    try {
      const stepsData = await txtovideoProjectsService.getWorkflowSteps(resolvedProjectId.value)
      if (stepsData && stepsData.steps) {
        const stateMap = {}
        stepsData.steps.forEach(s => { stateMap[s.step_name] = s.status })
        stepStates.value = stateMap
      }
    } catch (stepsError) {
      console.warn('步骤状态加载失败:', stepsError)
    }

    if (!workbench.value.source.text) {
      await hydrateSourceFromProject()
    }
  } catch (error) {
    console.error('加载短剧工作台项目失败:', error)
    ElMessage.warning('项目详情加载失败，已进入本地草稿')
  } finally {
    projectLoading.value = false
  }
}

async function hydrateSourceFromProject() {
  try {
    const content = await projectsStore.fetchProjectContent(resolvedProjectId.value)
    const text = extractProjectContent(content)
    if (text) {
      workbench.value.source.text = text
      workbench.value.source.fileName = project.value?.file_name || ''
    }
  } catch (error) {
    console.warn('项目原文读取失败:', error)
  }
}

function extractProjectContent(content) {
  if (typeof content === 'string') {
    return content
  }
  return content?.content || content?.text || content?.file_content || ''
}

function loadDraft() {
  const fallback = createDefaultWorkbench()
  savedStepIds.value = []

  try {
    const raw = localStorage.getItem(storageKey.value)
    if (!raw) {
      return fallback
    }
    const draft = JSON.parse(raw)
    savedStepIds.value = Array.isArray(draft.savedStepIds) ? draft.savedStepIds : []
    return {
      source: { ...fallback.source, ...(draft.workbench?.source || {}) },
      outputs: { ...fallback.outputs, ...(draft.workbench?.outputs || {}) },
      selectedTemplates: {
        ...fallback.selectedTemplates,
        ...(draft.workbench?.selectedTemplates || {})
      },
      promptUsed: { ...fallback.promptUsed, ...(draft.workbench?.promptUsed || {}) },
      updatedAt: draft.workbench?.updatedAt || null
    }
  } catch (error) {
    console.warn('读取本地草稿失败:', error)
    return fallback
  }
}

function persistDraft() {
  try {
    workbench.value.updatedAt = new Date().toISOString()
    localStorage.setItem(storageKey.value, JSON.stringify({
      workbench: workbench.value,
      savedStepIds: savedStepIds.value
    }))
  } catch (error) {
    console.error('保存本地草稿失败:', error)
  }

  if (resolvedProjectId.value) {
    txtovideoProjectsService.saveDraft(resolvedProjectId.value, {
      source: workbench.value.source,
      outputs: workbench.value.outputs,
      prompt_used: workbench.value.promptUsed || null
    }).catch(err => {
      console.warn('服务端草稿保存失败:', err)
    })
  }
}

function handleSourceFile(uploadFile) {
  const file = uploadFile.raw
  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    workbench.value.source.text = String(reader.result || '')
    workbench.value.source.fileName = file.name
    markStepDirty('source')
    ElMessage.success('原文已导入')
  }
  reader.onerror = () => {
    ElMessage.error('文件读取失败')
  }
  reader.readAsText(file, 'utf-8')
}

function handleTemplateChange() {
  markStepDirty(currentStep.value.id)
  persistDraft()
}

function getSelectedTemplate(outputKey) {
  const selectedId = workbench.value.selectedTemplates[outputKey]
  return promptTemplates.value.find(template => template.template_id === selectedId) || null
}

function recordPromptUsed(stepId) {
  const step = steps.find(item => item.id === stepId)
  if (!step?.outputKey) {
    return
  }
  const template = getSelectedTemplate(step.outputKey)
  if (!template) {
    return
  }

  workbench.value.promptUsed[step.outputKey] = {
    template_id: template.template_id,
    name: template.name,
    version: template.version,
    category: template.category,
    filename: template.filename,
    used_at: new Date().toISOString()
  }
}

function goToStep(index) {
  activeStepIndex.value = index
}

function handleNext() {
  if (!saveCurrent({ silent: true })) {
    return
  }
  if (activeStepIndex.value < steps.length - 1) {
    activeStepIndex.value += 1
  }
}

function saveCurrent(options = {}) {
  const validation = validateStep(currentStep.value)
  if (!validation.valid) {
    ElMessage.warning(validation.messages[0] || '当前步骤未通过检查')
    return false
  }

  if (!savedStepIds.value.includes(currentStep.value.id)) {
    savedStepIds.value = [...savedStepIds.value, currentStep.value.id]
  }
  persistDraft()

  const stepName = STEP_NAME_MAP[currentStep.value.outputKey]
  if (stepName && resolvedProjectId.value) {
    txtovideoProjectsService.updateWorkflowStep(resolvedProjectId.value, stepName, {
      status: 'success'
    }).catch(err => console.warn('步骤状态更新失败:', err))

    if (currentStep.value.outputKey && currentStep.value.outputKey !== 'export') {
      txtovideoProjectsService.markDownstreamStale(resolvedProjectId.value, stepName)
        .then(res => {
          if (res.marked_stale && res.marked_stale.length > 0) {
            res.marked_stale.forEach(s => { stepStates.value[s] = 'stale' })
          }
        })
        .catch(err => console.warn('下游标记失败:', err))
    }
  }

  if (!options.silent) {
    ElMessage.success('已保存当前步骤')
  }
  return true
}

function handleRegenerate() {
  const stepId = currentStep.value.id
  if (stepId === 'source') {
    workbench.value.source.text = normalizeText(workbench.value.source.text)
  } else if (stepId === 'script') {
    workbench.value.outputs.script = buildScript()
  } else if (stepId === 'characters') {
    workbench.value.outputs.characters = formatJson(buildCharacters())
  } else if (stepId === 'scenes') {
    workbench.value.outputs.scenes = formatJson(buildScenes())
  } else if (stepId === 'props') {
    workbench.value.outputs.props = formatJson(buildProps())
  } else if (stepId === 'storyboard') {
    workbench.value.outputs.storyboard = formatJson(buildStoryboard())
  } else if (stepId === 'imagePrompts') {
    workbench.value.outputs.imagePrompts = formatJson(buildImagePrompts())
  } else if (stepId === 'videoPrompts') {
    workbench.value.outputs.videoPrompts = formatJson(buildVideoPrompts())
  } else if (stepId === 'quality') {
    workbench.value.outputs.quality = formatJson(buildQualityReport())
  } else if (stepId === 'export') {
    workbench.value.outputs.export = formatJson(buildExportManifest())
  }

  recordPromptUsed(stepId)
  markStepDirty(stepId)
  ElMessage.success('已生成当前步骤草稿')
}

function markStepDirty(stepId) {
  const stepIndex = steps.findIndex(step => step.id === stepId)
  savedStepIds.value = savedStepIds.value.filter(id => {
    const savedIndex = steps.findIndex(step => step.id === id)
    return savedIndex !== -1 && savedIndex < stepIndex
  })
}

function isStepSaved(stepId) {
  return savedStepIds.value.includes(stepId)
}

function getStepStatus(step) {
  const stepName = STEP_NAME_MAP[step.outputKey]
  if (stepName && stepStates.value[stepName]) {
    return stepStates.value[stepName]
  }
  if (isStepSaved(step.id)) return 'success'
  return 'pending'
}

function validateStep(step) {
  if (step.id === 'source') {
    const text = normalizeText(workbench.value.source.text)
    return {
      valid: text.length > 0,
      messages: text.length > 0 ? [sourceMetrics.value] : ['请先输入原文']
    }
  }

  if (step.id === 'script') {
    const script = normalizeText(workbench.value.outputs.script)
    return {
      valid: script.length > 0,
      messages: script.length > 0 ? [`剧本 ${script.length} 字`] : ['请生成或填写剧本']
    }
  }

  const parsed = tryParseJson(workbench.value.outputs[step.outputKey])
  if (!parsed.ok) {
    return {
      valid: false,
      messages: ['JSON 格式有误']
    }
  }

  if (step.expectsArray && !Array.isArray(parsed.value)) {
    return {
      valid: false,
      messages: ['输出应为数组']
    }
  }

  if (step.id === 'storyboard') {
    return validateStoryboard(parsed.value)
  }

  if (step.id === 'imagePrompts') {
    return validatePromptArray(parsed.value, 'negative_prompt', ['positive_prompt', 'prompt_zh'])
  }

  if (step.id === 'videoPrompts') {
    return validatePromptArray(parsed.value, 'avoid', ['prompt', 'prompt_zh'], ['ltx_avoid'])
  }

  if (step.id === 'quality') {
    return {
      valid: Boolean(parsed.value?.status),
      messages: [`质检状态：${parsed.value?.status || '缺失'}`]
    }
  }

  if (step.id === 'export') {
    return {
      valid: Array.isArray(parsed.value?.files),
      messages: Array.isArray(parsed.value?.files) ? [`导出文件 ${parsed.value.files.length} 项`] : ['缺少 files 数组']
    }
  }

  return {
    valid: true,
    messages: ['结构正常']
  }
}

function validateStoryboard(shots) {
  const missing = shots.filter(shot => !shot.cap || !shot.desc_promopt)
  const themeIssues = shots.filter(shot => String(shot.theme || '').replace(/\s/g, '').length !== 2)
  const messages = [
    `分镜 ${shots.length} 条`,
    missing.length ? `${missing.length} 条缺少 cap 或 desc_promopt` : 'cap / desc_promopt 完整',
    themeIssues.length ? `${themeIssues.length} 条主题不是两个汉字` : '主题字段符合两字约束'
  ]
  return {
    valid: shots.length > 0 && missing.length === 0,
    messages
  }
}

function validatePromptArray(items, fieldName, promptFields = ['prompt_zh'], alternativeFields = []) {
  const requiredFields = [fieldName, ...alternativeFields]
  const missing = items.filter(item => {
    const hasPrompt = promptFields.some(promptField => Boolean(item[promptField]))
    const hasRequired = requiredFields.some(requiredField => Boolean(item[requiredField]))
    return !hasPrompt || !hasRequired
  })
  return {
    valid: items.length > 0 && missing.length === 0,
    messages: [
      `${items.length} 条提示词`,
      missing.length ? `${missing.length} 条缺少提示词或 ${fieldName}` : '提示词字段完整'
    ]
  }
}

function buildScript() {
  const seeds = getStorySeeds(workbench.value.source.text)
  const lines = seeds.length > 0 ? seeds : ['主角被迫卷入危局', '关键人物现身试探', '主角抓住线索反击']
  return lines.slice(0, 6).map((line, index) => {
    const sceneNo = index + 1
    return [
      `第${sceneNo}场  ${pickSceneName(index)}  ${pickTime(index)}`,
      `人物：${index % 2 === 0 ? '萧云、沈璃' : '萧云、陆衡'}`,
      `动作：${line}`,
      `对白：${pickDialogue(index)}`,
      `情绪：${pickMood(index)}`
    ].join('\n')
  }).join('\n\n')
}

function buildCharacters() {
  return [
    {
      name: '萧云',
      role: '男主',
      age_range: '22-28',
      appearance: '黑发束冠，青色窄袖长袍，眉眼冷峻',
      personality: '隐忍、果断、重承诺',
      consistency_anchor: '青色长袍、玉佩、冷峻眼神'
    },
    {
      name: '沈璃',
      role: '女主',
      age_range: '20-26',
      appearance: '乌发半挽，白色披风，眼神清亮',
      personality: '聪敏、克制、敢于试探真相',
      consistency_anchor: '白色披风、银簪、清冷气质'
    },
    {
      name: '陆衡',
      role: '对手',
      age_range: '30-38',
      appearance: '深色官服，薄唇，手持折扇',
      personality: '精于算计、表面温和',
      consistency_anchor: '深色官服、折扇、微笑压迫感'
    }
  ]
}

function buildScenes() {
  return [
    {
      name: '宫门雨夜',
      era: workbench.value.source.era,
      location: '朱红宫门外的长阶',
      atmosphere: '大雨、火把、压迫感',
      visual_anchor: '湿冷石阶、红墙、夜色火光'
    },
    {
      name: '偏殿内室',
      era: workbench.value.source.era,
      location: '烛火摇晃的偏殿',
      atmosphere: '密谈、紧张、阴影明显',
      visual_anchor: '木案、屏风、昏黄烛光'
    },
    {
      name: '长街拂晓',
      era: workbench.value.source.era,
      location: '空旷青石长街',
      atmosphere: '雾气、追逐、临界反转',
      visual_anchor: '青石板、晨雾、远处城楼'
    }
  ]
}

function buildProps() {
  return [
    {
      name: '旧密信',
      category: '线索',
      appearance: '泛黄纸张，朱砂封印残破',
      story_use: '揭露主角被陷害的关键证据'
    },
    {
      name: '青玉佩',
      category: '身份物',
      appearance: '半透明青玉，边缘有裂痕',
      story_use: '确认萧云真实身份'
    },
    {
      name: '折扇',
      category: '人物锚点',
      appearance: '黑骨白面，扇面有墨竹',
      story_use: '强化陆衡的压迫感和伪装'
    }
  ]
}

function buildStoryboard() {
  const seeds = getStorySeeds(workbench.value.outputs.script || workbench.value.source.text)
  const characters = safeJsonArray('characters', buildCharacters())
  const scenes = safeJsonArray('scenes', buildScenes())
  const props = safeJsonArray('props', buildProps())

  return (seeds.length ? seeds : ['雨夜闯宫', '偏殿对峙', '密信出现', '长街追逐', '身份反转'])
    .slice(0, 8)
    .map((seed, index) => {
      const scene = scenes[index % scenes.length]
      const mainCharacter = characters[index % characters.length]
      const prop = props[index % props.length]
      return {
        shot_no: index + 1,
        theme: pickTheme(index),
        cap: seed,
        desc_promopt: `${scene.name}，${mainCharacter.name}${mainCharacter.appearance}，${prop.name}入画，${scene.atmosphere}，古风真人写实`,
        scene: scene.name,
        characters: [mainCharacter.name],
        props: [prop.name],
        camera: pickCamera(index),
        duration_seconds: index % 3 === 0 ? 8 : 10,
        status: 'draft'
      }
    })
}

function buildImagePrompts() {
  return safeJsonArray('storyboard', buildStoryboard()).map(shot => ({
    shot_no: shot.shot_no,
    positive_prompt: `${shot.theme}，${shot.desc_promopt}，电视剧电影真人写实风格，东方人物，中国古代服饰，真实纹理，自然颜色，电影级摄影，浅景深，真实光照，画面清晰，情绪明确，竖屏${workbench.value.source.aspectRatio}`,
    prompt_zh: `${shot.theme}，${shot.desc_promopt}，电影级光影，真实人物，竖屏${workbench.value.source.aspectRatio}，高细节，情绪明确`,
    negative_prompt: NEGATIVE_PROMPT,
    model_hint: 'realistic',
    aspect_ratio: workbench.value.source.aspectRatio,
    reference_assets: {
      characters: shot.characters || [],
      scene: shot.scene,
      props: shot.props || []
    },
    status: 'draft'
  }))
}

function buildVideoPrompts() {
  return safeJsonArray('storyboard', buildStoryboard()).map(shot => ({
    shot_no: shot.shot_no,
    engine: 'ltx',
    prompt: `${shot.cap}。${shot.camera}，人物动作连续但幅度轻，表情从克制到紧张，环境保持${shot.scene}一致。`,
    prompt_zh: `${shot.cap}。${shot.camera}，人物动作连续，表情从克制到紧张，环境保持${shot.scene}一致。`,
    camera_motion: shot.camera,
    character_motion: '轻微动作，保持身份和服装一致',
    scene_motion: '雨、雾、烛火、衣袖或尘埃可轻微运动',
    subject_motion: '保持单一主体动作连续，不新增人物',
    duration_seconds: shot.duration_seconds,
    avoid: LTX_AVOID_RULES,
    ltx_avoid: LTX_AVOID_RULES,
    status: 'draft'
  }))
}

function buildQualityReport() {
  const storyboard = safeJsonArray('storyboard', [])
  const imagePrompts = safeJsonArray('imagePrompts', [])
  const videoPrompts = safeJsonArray('videoPrompts', [])
  const storyboardValid = validateStoryboard(storyboard).valid
  const imageValid = validatePromptArray(imagePrompts, 'negative_prompt', ['positive_prompt', 'prompt_zh']).valid
  const videoValid = validatePromptArray(videoPrompts, 'avoid', ['prompt', 'prompt_zh'], ['ltx_avoid']).valid

  return {
    status: storyboardValid && imageValid && videoValid ? 'ready' : 'needs_fix',
    checks: [
      {
        name: '分镜字段',
        status: storyboardValid ? 'pass' : 'warning',
        message: storyboardValid ? 'cap 与 desc_promopt 完整' : '分镜缺少必要字段'
      },
      {
        name: '图片提示词',
        status: imageValid ? 'pass' : 'warning',
        message: imageValid ? '负面词已覆盖时代和质量约束' : '图片提示词不完整'
      },
      {
        name: '视频提示词',
        status: videoValid ? 'pass' : 'warning',
        message: videoValid ? 'LTX 运动约束已记录' : '视频提示词不完整'
      }
    ],
    updated_at: new Date().toISOString()
  }
}

function buildExportManifest() {
  const projectName = projectTitle.value.replace(/[\\/:*?"<>|]/g, '_')
  return {
    package_name: `${projectName || 'txtovideo-project'}_asset_package`,
    project_id: resolvedProjectId.value,
    generated_at: new Date().toISOString(),
    files: [
      'project_manifest.json',
      'source.txt',
      'script.txt',
      'characters.json',
      'scenes.json',
      'props.json',
      'storyboard.json',
      'image_prompts.json',
      'video_prompts_ltx.json',
      'quality_report.json',
      'subtitles.srt',
      'notes.md'
    ],
    manifest: {
      title: projectTitle.value,
      era: workbench.value.source.era,
      style: workbench.value.source.style,
      platform: workbench.value.source.platform,
      aspect_ratio: workbench.value.source.aspectRatio,
      duration_range: workbench.value.source.durationRange,
      shot_count: countJsonArray('storyboard'),
      quality_status: readQualityStatus(),
      prompt_template_versions: Object.fromEntries(
        Object.entries(workbench.value.promptUsed).map(([key, prompt]) => [
          key,
          `${prompt.template_id}@${prompt.version}`
        ])
      ),
      prompt_used: workbench.value.promptUsed
    }
  }
}

function downloadExportDraft() {
  const manifest = tryParseJson(workbench.value.outputs.export)
  const payload = manifest.ok ? manifest.value : buildExportManifest()
  const blob = new Blob([formatJson(payload)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${payload.package_name || 'txtovideo_manifest'}.json`
  link.click()
  URL.revokeObjectURL(url)
}

async function downloadExportZip() {
  zipExporting.value = true
  try {
    const manifest = tryParseJson(workbench.value.outputs.export)
    const payload = manifest.ok ? manifest.value : buildExportManifest()
    const res = await post('/export/txtovideo', {
      package_name: payload.package_name || 'txtovideo-project_asset_package',
      project_id: resolvedProjectId.value || null,
      source: workbench.value.source,
      outputs: workbench.value.outputs,
      prompt_used: workbench.value.promptUsed || null
    })
    if (res.download_url) {
      const link = document.createElement('a')
      link.href = res.download_url
      link.download = res.filename || 'txtovideo_export.zip'
      link.click()
      ElMessage.success('ZIP包导出成功')
    } else {
      ElMessage.warning('导出响应异常，请重试')
    }
  } catch (error) {
    console.error('ZIP导出失败:', error)
    ElMessage.error('ZIP导出失败，请稍后重试')
  } finally {
    zipExporting.value = false
  }
}

async function generateCanvas() {
  if (!resolvedProjectId.value) {
    ElMessage.warning('请先保存项目')
    return
  }
  try {
    const res = await txtovideoProjectsService.generateCanvas(resolvedProjectId.value)
    if (res.document_id) {
      ElMessage.success('画布已生成，即将跳转...')
      const timer = setTimeout(() => {
        router.push({ name: 'CanvasEditor', params: { canvasId: res.document_id } })
      }, 1000)
      _pendingTimers.push(timer)
    }
  } catch (error) {
    console.error('生成画布失败:', error)
    ElMessage.error('生成画布失败')
  }
}

async function runQualityScore() {
  if (!resolvedProjectId.value) {
    ElMessage.warning('请先保存项目')
    return
  }
  qualityScoring.value = true
  try {
    const res = await txtovideoProjectsService.scoreProjectQuality(resolvedProjectId.value)
    qualityResult.value = res
    workbench.value.outputs.quality = formatJson({
      status: res.grade === 'F' || res.grade === 'D' ? 'needs_fix' : 'ready',
      overall_score: res.overall_score,
      grade: res.grade,
      checks: res.checks,
      fix_suggestions: res.fix_suggestions,
      updated_at: new Date().toISOString()
    })
    markStepDirty('quality')
    ElMessage.success(`质量评分完成：${res.overall_score}分 (${res.grade}级)`)
  } catch (error) {
    console.error('质量评分失败:', error)
    ElMessage.error('质量评分失败，请稍后重试')
  } finally {
    qualityScoring.value = false
  }
}

function readQualityStatus() {
  const parsed = tryParseJson(workbench.value.outputs.quality)
  return parsed.ok ? parsed.value?.status || 'draft' : 'invalid'
}

function countJsonArray(outputKey) {
  return safeJsonArray(outputKey, []).length
}

function safeJsonArray(outputKey, fallback) {
  const parsed = tryParseJson(workbench.value.outputs[outputKey])
  return parsed.ok && Array.isArray(parsed.value) ? parsed.value : fallback
}

function tryParseJson(value) {
  try {
    return {
      ok: true,
      value: JSON.parse(value || 'null')
    }
  } catch (error) {
    return {
      ok: false,
      error
    }
  }
}

function getStorySeeds(text) {
  return normalizeText(text)
    .split(/\n+|[。！？!?]/)
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .slice(0, 8)
}

function normalizeText(text) {
  return String(text || '')
    .replace(/\r\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function compactPreview(text, limit = 3000) {
  const value = String(text || '')
  if (value.length <= limit) {
    return value
  }
  return `${value.slice(0, limit)}\n...`
}

function formatJson(value) {
  return JSON.stringify(value, null, 2)
}

function pickSceneName(index) {
  return ['宫门雨夜', '偏殿密谈', '长街拂晓', '后院追问'][index % 4]
}

function pickTime(index) {
  return ['夜', '深夜', '拂晓', '清晨'][index % 4]
}

function pickDialogue(index) {
  return [
    '萧云：这封信若是真的，今夜所有人都在局中。',
    '沈璃：你要活着走出去，才有资格翻案。',
    '陆衡：证据从来不重要，重要的是谁能留下来。',
    '萧云：那我便亲手改了这个结局。'
  ][index % 4]
}

function pickMood(index) {
  return ['压抑克制', '警惕试探', '紧张爆发', '反击坚定'][index % 4]
}

function pickTheme(index) {
  return ['夜奔', '密谈', '信现', '追逐', '反转', '对峙', '破局', '回望'][index % 8]
}

function pickCamera(index) {
  return ['低机位跟拍', '缓慢推进', '特写切入', '横移追随', '定镜压迫'][index % 5]
}

onBeforeUnmount(() => {
  _pendingTimers.forEach(clearTimeout)
  _pendingTimers.length = 0
})
</script>

<style scoped>
.workbench-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  min-height: 100%;
}

.page-header,
.project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-lg);
  padding: var(--space-xl);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.page-header h1,
.project-header h1 {
  margin: 0 0 var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-2xl);
  font-weight: 700;
}

.page-header p,
.project-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.header-actions,
.project-meta,
.project-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.project-meta {
  min-width: 260px;
  justify-content: flex-end;
}

.progress-box {
  display: grid;
  grid-template-columns: auto 120px;
  align-items: center;
  gap: var(--space-sm);
  color: var(--text-secondary);
  font-weight: 600;
}

.workflow-band,
.loading-panel {
  padding: var(--space-xl);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
}

.entry-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  min-height: 88px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--text-base);
  font-weight: 600;
  transition: all var(--transition-base);
}

.entry-item:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.entry-item.primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #fff;
}

.entry-item.primary:hover {
  color: #fff;
  background: var(--primary-hover);
}

.workbench-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 360px;
  align-items: start;
  gap: var(--space-lg);
}

.step-sidebar,
.step-editor,
.preview-panel {
  min-height: 640px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.step-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-sm);
  position: sticky;
  top: var(--space-lg);
}

.step-button {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) 20px;
  align-items: center;
  gap: var(--space-sm);
  width: 100%;
  padding: var(--space-sm);
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.step-button:hover,
.step-button.active {
  border-color: var(--primary-color);
  background: rgba(64, 158, 255, 0.08);
}

.step-button.saved .step-index {
  background: #16a34a;
  color: #fff;
}

.step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 700;
}

.step-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.step-copy strong {
  overflow: hidden;
  color: var(--text-primary);
  font-size: var(--text-sm);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.step-copy small {
  overflow: hidden;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.step-check {
  color: #16a34a;
}

.step-editor {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-lg);
}

.step-editor-header,
.preview-header,
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}

.step-editor-header h2,
.preview-header h3 {
  margin: 0 0 var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-xl);
}

.step-editor-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.input-panel,
.output-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.panel-title {
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 700;
}

.input-panel pre,
.json-preview {
  margin: 0;
  padding: var(--space-md);
  overflow: auto;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.input-panel pre {
  max-height: 180px;
}

.source-editor {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.source-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.full-width {
  width: 100%;
}

.preview-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-lg);
  position: sticky;
  top: var(--space-lg);
}

.json-preview {
  min-height: 320px;
  max-height: 440px;
}

.validation-box {
  padding: var(--space-md);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
}

.template-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-md);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
}

.template-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.template-box p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  line-height: 1.5;
}

.validation-box strong {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.validation-box ul {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.side-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
}

.quality-score-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-md);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
}

.quality-score-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}

.quality-score-number {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.quality-score-number .score-value {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
}

.quality-score-number .score-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.quality-fix-list {
  padding: var(--space-sm);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.quality-fix-list strong {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.quality-fix-list ul {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.quality-fix-list li {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

.quality-section-scores {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.quality-section-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.quality-section-item .section-name {
  min-width: 100px;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.quality-section-item .el-progress {
  flex: 1;
}

@media (max-width: 1200px) {
  .workbench-layout {
    grid-template-columns: 220px minmax(0, 1fr);
  }

  .preview-panel {
    grid-column: 1 / -1;
    position: static;
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .page-header,
  .project-header,
  .project-title-group,
  .project-meta,
  .source-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .project-meta {
    min-width: 0;
  }

  .progress-box {
    grid-template-columns: 1fr;
  }

  .entry-grid,
  .workbench-layout {
    grid-template-columns: 1fr;
  }

  .step-sidebar,
  .preview-panel {
    position: static;
    min-height: auto;
  }
}
</style>
