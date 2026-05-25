<template>
  <div class="storyboard-editor">
    <div class="panel-header">
      <h3>分镜编辑器</h3>
      <div class="actions">
        <el-switch
          v-model="editMode"
          active-text="编辑"
          inactive-text="查看"
          style="margin-right: 12px"
        />
        <el-button
          type="primary"
          :loading="extracting"
          :disabled="!canExtract"
          @click="handleExtractClick"
        >
          {{ hasShots ? '重新提取分镜' : '提取分镜' }}
        </el-button>
      </div>
    </div>

    <div class="shot-list">
      <el-empty
        v-if="sceneGroups.length === 0"
        description="暂无分镜，请先提取分镜"
      />

      <el-collapse
        v-else
        v-model="activeScenes"
        class="scene-collapse"
      >
        <el-collapse-item
          v-for="group in sceneGroups"
          :key="group.scene.id"
          :name="group.scene.id"
        >
          <template #title>
            <div class="scene-header">
              <div class="scene-title-row">
                <span class="scene-number">场景 {{ group.scene.order_index }}</span>
                <el-tag
                  size="small"
                  type="info"
                >
                  {{ group.shots.length }} 个分镜
                </el-tag>
                <el-button
                  v-if="group.shots.length > 0"
                  size="small"
                  type="warning"
                  :loading="extractingScenes.has(group.scene.id)"
                  :disabled="extractingScenes.has(group.scene.id)"
                  style="margin-left: 8px"
                  @click.stop="handleSingleSceneExtractClick(group.scene.id)"
                >
                  {{ extractingScenes.has(group.scene.id) ? '提取中...' : '重新提取' }}
                </el-button>
              </div>
              <div
                v-if="group.scene.characters && group.scene.characters.length > 0"
                class="scene-characters"
              >
                <el-tag
                  v-for="char in group.scene.characters"
                  :key="char"
                  size="small"
                  effect="plain"
                  style="margin-right: 4px"
                >
                  {{ char }}
                </el-tag>
              </div>
            </div>
          </template>

          <div class="scene-description">
            <p>{{ group.scene.scene }}</p>
          </div>

          <div class="shot-grid">
            <div
              v-for="(shot) in group.shots"
              :key="shot.id"
              class="shot-card"
              :class="{ 'edit-mode': editMode, 'drag-over': dragOverId === shot.id }"
              :draggable="editMode"
              @dragstart="onDragStart($event, shot, group.scene.id)"
              @dragover.prevent="onDragOver($event, shot)"
              @dragleave="onDragLeave(shot)"
              @drop="onDrop($event, shot, group.scene.id)"
            >
              <div class="shot-header">
                <div class="shot-header-left">
                  <el-icon
                    v-if="editMode"
                    class="drag-handle"
                    :size="16"
                  >
                    <Rank />
                  </el-icon>
                  <span class="shot-number">镜头 {{ shot.order_index }}</span>
                </div>
                <div class="shot-header-right">
                  <el-tag
                    v-if="shot.keyframe_url"
                    type="success"
                    size="small"
                  >
                    关键帧
                  </el-tag>
                  <el-button
                    v-if="editMode"
                    type="danger"
                    size="small"
                    circle
                    @click="handleDeleteShot(shot)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>

              <div
                v-if="shot.keyframe_url"
                class="shot-keyframe"
                @click="handleImagePreview(shot.keyframe_url)"
              >
                <img
                  :src="shot.keyframe_url"
                  :alt="`镜头 ${shot.order_index}`"
                >
                <div class="preview-overlay">
                  <el-icon :size="20">
                    <ZoomIn />
                  </el-icon>
                </div>
              </div>

              <div class="shot-content">
                <div class="field-group">
                  <label>分镜描述</label>
                  <el-input
                    v-if="editMode"
                    v-model="shot._editShot"
                    type="textarea"
                    :autosize="{ minRows: 2, maxRows: 5 }"
                    @blur="handleShotBlur(shot)"
                  />
                  <p
                    v-else
                    class="shot-description"
                  >
                    {{ shot.shot }}
                  </p>
                </div>

                <div class="field-group">
                  <label>对话</label>
                  <el-input
                    v-if="editMode"
                    v-model="shot._editDialogue"
                    type="textarea"
                    :autosize="{ minRows: 1, maxRows: 3 }"
                    placeholder="无对话内容"
                    @blur="handleDialogueBlur(shot)"
                  />
                  <p
                    v-else-if="shot.dialogue"
                    class="shot-dialogue"
                  >
                    💬 {{ shot.dialogue }}
                  </p>
                </div>

                <div
                  v-if="shot.characters && shot.characters.length > 0"
                  class="shot-characters"
                >
                  <el-tag
                    v-for="char in shot.characters"
                    :key="char"
                    size="small"
                    type="warning"
                    effect="plain"
                  >
                    {{ char }}
                  </el-tag>
                </div>

                <div
                  v-if="shot.generated_prompt && !editMode"
                  class="shot-prompt"
                >
                  <el-collapse>
                    <el-collapse-item title="生成提示词">
                      <p class="prompt-text">
                        {{ shot.generated_prompt }}
                      </p>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <el-dialog
      v-model="previewVisible"
      title="关键帧预览"
      width="80%"
      class="preview-dialog"
      destroy-on-close
    >
      <div class="preview-container">
        <div class="preview-toolbar">
          <el-button-group>
            <el-button
              :disabled="previewScale <= 0.3"
              @click="previewScale -= 0.2"
            >
              <el-icon><ZoomOut /></el-icon>
            </el-button>
            <el-button @click="previewScale = 1">
              {{ Math.round(previewScale * 100) }}%
            </el-button>
            <el-button
              :disabled="previewScale >= 3"
              @click="previewScale += 0.2"
            >
              <el-icon><ZoomIn /></el-icon>
            </el-button>
          </el-button-group>
          <el-button @click="handleRotatePreview">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
          <span class="preview-info">{{ currentPreviewIndex + 1 }} / {{ allKeyframeUrls.length }}</span>
        </div>
        <div
          class="preview-body"
          @wheel.prevent="handlePreviewWheel"
        >
          <el-button
            v-if="allKeyframeUrls.length > 1"
            class="preview-nav prev"
            circle
            :disabled="currentPreviewIndex <= 0"
            @click="navigatePreview(-1)"
          >
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <img
            v-if="previewUrl"
            :src="previewUrl"
            :style="{ transform: `scale(${previewScale}) rotate(${previewRotation}deg)` }"
            class="preview-image"
          >
          <el-button
            v-if="allKeyframeUrls.length > 1"
            class="preview-nav next"
            circle
            :disabled="currentPreviewIndex >= allKeyframeUrls.length - 1"
            @click="navigatePreview(1)"
          >
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="showWarningDialog"
      title="重新提取分镜"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="warning-content">
        <div class="warning-icon">
          <el-icon
            :size="60"
            color="#f56c6c"
          >
            <WarningFilled />
          </el-icon>
        </div>
        <div class="warning-title">
          <h3>此操作将删除以下所有数据</h3>
        </div>
        <div class="warning-list">
          <div class="warning-item">
            <el-icon color="#f56c6c">
              <Delete />
            </el-icon><span>所有现有分镜脚本</span>
          </div>
          <div class="warning-item">
            <el-icon color="#f56c6c">
              <Delete />
            </el-icon><span>所有场景环境图</span>
          </div>
          <div class="warning-item">
            <el-icon color="#f56c6c">
              <Delete />
            </el-icon><span>所有关键帧图片</span>
          </div>
        </div>
        <el-alert
          type="error"
          :closable="false"
          show-icon
        >
          <template #title>
            <strong>⚠️ 此操作不可撤销，请谨慎操作！</strong>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button
          size="large"
          @click="showWarningDialog = false"
        >
          取消
        </el-button>
        <el-button
          type="danger"
          size="large"
          @click="handleWarningConfirm"
        >
          <el-icon><Delete /></el-icon>确认删除并重新提取
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showSingleSceneWarning"
      title="重新提取场景分镜"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="warning-content">
        <div class="warning-icon">
          <el-icon
            :size="60"
            color="#e6a23c"
          >
            <WarningFilled />
          </el-icon>
        </div>
        <div class="warning-title">
          <h3>此操作将删除该场景的以下数据</h3>
        </div>
        <div class="warning-list">
          <div class="warning-item">
            <el-icon color="#e6a23c">
              <Delete />
            </el-icon><span>该场景的所有分镜脚本</span>
          </div>
          <div class="warning-item">
            <el-icon color="#e6a23c">
              <Delete />
            </el-icon><span>该场景的所有关键帧图片</span>
          </div>
        </div>
        <el-alert
          type="warning"
          :closable="false"
          show-icon
        >
          <template #title>
            <strong>⚠️ 其他场景的分镜不会受影响</strong>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button
          size="large"
          @click="showSingleSceneWarning = false"
        >
          取消
        </el-button>
        <el-button
          type="warning"
          size="large"
          @click="handleSingleSceneWarningConfirm"
        >
          <el-icon><Delete /></el-icon>确认删除并重新提取
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showDialog"
      :title="currentSceneId ? '重新提取场景分镜' : '提取分镜'"
      width="500px"
    >
      <el-form
        :model="formData"
        label-width="100px"
      >
        <el-form-item label="API Key">
          <el-select
            v-model="formData.apiKeyId"
            placeholder="请选择API Key"
            style="width: 100%"
          >
            <el-option
              v-for="key in apiKeys"
              :key="key.id"
              :label="`${key.name} (${key.provider})`"
              :value="key.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型">
          <el-select
            v-model="formData.model"
            placeholder="选择模型"
            style="width: 100%"
            :loading="loadingModels"
            filterable
            allow-create
            default-first-option
          >
            <el-option
              v-for="model in modelOptions"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :disabled="!formData.apiKeyId || !formData.model"
          @click="currentSceneId ? handleSingleSceneDialogConfirm() : handleDialogConfirm()"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, Delete, Rank, ZoomIn, ZoomOut, ArrowLeft, ArrowRight, RefreshRight } from '@element-plus/icons-vue'
import movieService from '@/services/movie'
import api from '@/services/api'

const props = defineProps({
  sceneGroups: { type: Array, default: () => [] },
  extracting: { type: Boolean, default: false },
  canExtract: { type: Boolean, default: true },
  apiKeys: { type: Array, default: () => [] },
  extractingScenes: { type: Set, default: () => new Set() }
})

const emit = defineEmits(['extract-shots', 'extract-single-scene-shots', 'shots-updated'])

const editMode = ref(false)
const activeScenes = ref([])
const showDialog = ref(false)
const showWarningDialog = ref(false)
const showSingleSceneWarning = ref(false)
const formData = ref({ apiKeyId: '', model: '' })
const modelOptions = ref([])
const loadingModels = ref(false)
const currentSceneId = ref(null)
const previewVisible = ref(false)
const previewUrl = ref('')
const previewScale = ref(1)
const previewRotation = ref(0)
const currentPreviewIndex = ref(0)

const allKeyframeUrls = computed(() => {
  const urls = []
  for (const group of props.sceneGroups) {
    if (group.shots) {
      for (const shot of group.shots) {
        if (shot.keyframe_url) {
          urls.push(shot.keyframe_url)
        }
      }
    }
  }
  return urls
})

const dragSource = ref(null)
const dragOverId = ref(null)

const hasShots = computed(() => {
  return props.sceneGroups.some(group => group.shots && group.shots.length > 0)
})

watch(() => formData.value.apiKeyId, async (newKeyId) => {
  if (!newKeyId) {
    modelOptions.value = []
    formData.value.model = ''
    return
  }
  loadingModels.value = true
  try {
    const models = await api.get(`/api-keys/${newKeyId}/models?type=text`)
    modelOptions.value = models || []
    if (modelOptions.value.length > 0) {
      formData.value.model = modelOptions.value[0]
    } else {
      formData.value.model = ''
    }
  } catch (error) {
    console.error('获取模型列表失败', error)
    modelOptions.value = []
    formData.value.model = ''
  } finally {
    loadingModels.value = false
  }
})

watch(editMode, (val) => {
  if (val) {
    initEditFields()
  }
})

const initEditFields = () => {
  props.sceneGroups.forEach(group => {
    group.shots.forEach(shot => {
      if (shot._editShot === undefined) shot._editShot = shot.shot
      if (shot._editDialogue === undefined) shot._editDialogue = shot.dialogue || ''
    })
  })
}

const handleImagePreview = (url) => {
  if (!url) return
  previewUrl.value = url
  previewScale.value = 1
  previewRotation.value = 0
  currentPreviewIndex.value = allKeyframeUrls.value.indexOf(url)
  previewVisible.value = true
}

const navigatePreview = (delta) => {
  const newIndex = currentPreviewIndex.value + delta
  if (newIndex >= 0 && newIndex < allKeyframeUrls.value.length) {
    currentPreviewIndex.value = newIndex
    previewUrl.value = allKeyframeUrls.value[newIndex]
    previewScale.value = 1
    previewRotation.value = 0
  }
}

const handleRotatePreview = () => {
  previewRotation.value = (previewRotation.value + 90) % 360
}

const handlePreviewWheel = (e) => {
  if (e.deltaY < 0) {
    previewScale.value = Math.min(3, previewScale.value + 0.1)
  } else {
    previewScale.value = Math.max(0.3, previewScale.value - 0.1)
  }
}

const handleShotBlur = async (shot) => {
  if (shot._editShot === shot.shot) return
  if (!shot._editShot.trim()) {
    shot._editShot = shot.shot
    ElMessage.warning('分镜描述不能为空')
    return
  }
  try {
    await movieService.updateShot(shot.id, { shot: shot._editShot })
    shot.shot = shot._editShot
    ElMessage.success('分镜描述已更新')
  } catch (error) {
    ElMessage.error('更新失败')
    shot._editShot = shot.shot
  }
}

const handleDialogueBlur = async (shot) => {
  if (shot._editDialogue === (shot.dialogue || '')) return
  try {
    await movieService.updateShot(shot.id, { dialogue: shot._editDialogue || null })
    shot.dialogue = shot._editDialogue || null
    ElMessage.success('对话内容已更新')
  } catch (error) {
    ElMessage.error('更新失败')
    shot._editDialogue = shot.dialogue || ''
  }
}

const handleDeleteShot = async (shot) => {
  try {
    await ElMessageBox.confirm('确定要删除这个分镜吗？删除后不可恢复。', '删除确认', { type: 'warning' })
    await movieService.deleteShot(shot.id)
    ElMessage.success('分镜已删除')
    emit('shots-updated')
  } catch { /* user cancelled */ }
}

const onDragStart = (event, shot, sceneId) => {
  dragSource.value = { shot, sceneId }
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', shot.id)
}

const onDragOver = (event, shot) => {
  dragOverId.value = shot.id
}

const onDragLeave = (shot) => {
  if (dragOverId.value === shot.id) {
    dragOverId.value = null
  }
}

const onDrop = async (event, targetShot) => {
  dragOverId.value = null
  if (!dragSource.value) return

  const sourceShot = dragSource.value.shot
  if (sourceShot.id === targetShot.id) return

  try {
    const sourceOrder = sourceShot.order_index
    const targetOrder = targetShot.order_index

    await movieService.updateShotOrder(sourceShot.id, targetOrder)
    await movieService.updateShotOrder(targetShot.id, sourceOrder)

    sourceShot.order_index = targetOrder
    targetShot.order_index = sourceOrder

    ElMessage.success('分镜顺序已更新')
    emit('shots-updated')
  } catch (error) {
    ElMessage.error('调整顺序失败')
  } finally {
    dragSource.value = null
  }
}

const handleExtractClick = () => {
  if (hasShots.value) {
    showWarningDialog.value = true
  } else {
    formData.value = { apiKeyId: props.apiKeys[0]?.id || '', model: '' }
    showDialog.value = true
  }
}

const handleWarningConfirm = () => {
  showWarningDialog.value = false
  formData.value = { apiKeyId: props.apiKeys[0]?.id || '', model: '' }
  showDialog.value = true
}

const handleDialogConfirm = () => {
  if (!formData.value.apiKeyId || !formData.value.model) return
  emit('extract-shots', formData.value.apiKeyId, formData.value.model)
  showDialog.value = false
}

const handleSingleSceneExtractClick = (sceneId) => {
  currentSceneId.value = sceneId
  showSingleSceneWarning.value = true
}

const handleSingleSceneWarningConfirm = () => {
  showSingleSceneWarning.value = false
  formData.value = { apiKeyId: props.apiKeys[0]?.id || '', model: '' }
  showDialog.value = true
}

const handleSingleSceneDialogConfirm = () => {
  if (!formData.value.apiKeyId || !formData.value.model || !currentSceneId.value) return
  emit('extract-single-scene-shots', currentSceneId.value, formData.value.apiKeyId, formData.value.model)
  showDialog.value = false
  currentSceneId.value = null
}
</script>

<style scoped>
.storyboard-editor {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.actions {
  display: flex;
  align-items: center;
}

.scene-collapse {
  border: none;
}

.scene-header {
  flex: 1;
  padding-right: 20px;
}

.scene-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.scene-number {
  font-weight: 600;
  font-size: 16px;
  color: #409eff;
}

.scene-characters {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.scene-description {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 16px;
  border-left: 3px solid #409eff;
}

.scene-description p {
  margin: 0;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.shot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.shot-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
  background: white;
}

.shot-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.shot-card.edit-mode {
  cursor: grab;
  border-style: dashed;
}

.shot-card.edit-mode:active {
  cursor: grabbing;
}

.shot-card.drag-over {
  border-color: #409eff;
  border-width: 2px;
  background: #ecf5ff;
}

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.shot-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.shot-header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.drag-handle {
  color: #909399;
  cursor: grab;
}

.shot-number {
  font-weight: 600;
  color: #67c23a;
  font-size: 14px;
}

.shot-keyframe {
  width: 100%;
  max-height: 180px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  margin-bottom: 12px;
  background: #f5f7fa;
}

.shot-keyframe img {
  width: 100%;
  height: 100%;
  max-height: 180px;
  object-fit: cover;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s;
}

.shot-keyframe:hover .preview-overlay {
  opacity: 1;
}

.shot-content {
  margin-bottom: 4px;
}

.field-group {
  margin-bottom: 8px;
}

.field-group label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.shot-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.shot-dialogue {
  margin: 0;
  font-size: 13px;
  color: #909399;
  font-style: italic;
  padding: 8px;
  background: #f0f9ff;
  border-radius: 4px;
}

.shot-characters {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.shot-prompt {
  margin-top: 8px;
}

.prompt-text {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  white-space: pre-wrap;
}

.warning-content {
  text-align: center;
}

.warning-icon {
  margin-bottom: 16px;
}

.warning-title h3 {
  margin: 0 0 16px 0;
  color: #303133;
}

.warning-list {
  text-align: left;
  margin: 0 auto 16px;
  max-width: 300px;
}

.warning-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

:deep(.el-collapse-item__header) {
  background: #fafafa;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 14px;
}

:deep(.el-collapse-item__header:hover) {
  background: #f0f2f5;
}

:deep(.el-collapse-item__wrap) {
  border: none;
  background: transparent;
}

:deep(.el-collapse-item__content) {
  padding: 0 16px 16px;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.preview-container {
  display: flex;
  flex-direction: column;
  height: 70vh;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  flex-shrink: 0;
}

.preview-info {
  margin-left: auto;
  font-size: 14px;
  color: #909399;
}

.preview-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #1a1a2e;
  background-image:
    linear-gradient(45deg, #222 25%, transparent 25%),
    linear-gradient(-45deg, #222 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #222 75%),
    linear-gradient(-45deg, transparent 75%, #222 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  transition: transform 0.2s ease;
  user-select: none;
  -webkit-user-drag: none;
}

.preview-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background: rgba(255, 255, 255, 0.85) !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  width: 44px !important;
  height: 44px !important;
}

.preview-nav:hover {
  background: rgba(255, 255, 255, 0.95) !important;
}

.preview-nav.prev {
  left: 16px;
}

.preview-nav.next {
  right: 16px;
}
</style>
