<template>
  <div class="keyframe-panel">
    <div class="panel-header">
      <h3>关键帧生成</h3>
      <div class="actions">
        <el-button 
          type="primary"
          :loading="batchGenerating"
          :disabled="!canGenerate || batchGenerating || generatingIds.size > 0"
          @click="handleBatchGenerateClick"
        >
          批量生成关键帧
        </el-button>
      </div>
    </div>

    <div class="keyframe-list">
      <el-empty
        v-if="sceneGroups.length === 0"
        description="暂无分镜数据，请先提取分镜"
      />
      
      <!-- 按场景分组显示 -->
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
              </div>
            </div>
          </template>

          <!-- 该场景的分镜关键帧列表 -->
          <div class="keyframe-grid">
            <div 
              v-for="shot in group.shots" 
              :key="shot.id"
              class="keyframe-card"
            >
              <div class="keyframe-header">
                <span class="shot-number">镜头 {{ shot.order_index }}</span>
                <div class="shot-actions">
                  <el-button
                    v-if="!shot.keyframe_url"
                    type="success"
                    size="small"
                    :loading="generatingIds.has(shot.id)"
                    :disabled="generatingIds.has(shot.id)"
                    @click="handleGenerateKeyframe(shot)"
                  >
                    生成
                  </el-button>
                  <el-button
                    v-else
                    type="warning"
                    size="small"
                    :loading="generatingIds.has(shot.id)"
                    :disabled="generatingIds.has(shot.id)"
                    @click="handleRegenerateKeyframe(shot)"
                  >
                    重新生成
                  </el-button>
                  <el-button
                    v-if="shot.keyframe_url"
                    type="info"
                    size="small"
                    @click="handleShowHistory(shot.id)"
                  >
                    <el-icon><Clock /></el-icon>
                  </el-button>
                </div>
              </div>
              
              <div class="shot-description">
                <p>{{ shot.shot }}</p>
              </div>

              <!-- 关键帧图片 - 可点击放大 -->
              <div
                v-if="shot.keyframe_url"
                class="keyframe-image"
                @click="handlePreviewImage(shot.keyframe_url)"
              >
                <img
                  :src="shot.keyframe_url"
                  alt="关键帧"
                >
                <div class="keyframe-overlay">
                  <el-icon><ZoomIn /></el-icon>
                </div>
              </div>
              <div
                v-else
                class="keyframe-placeholder"
              >
                <el-icon :size="40">
                  <Picture />
                </el-icon>
                <p>待生成关键帧</p>
              </div>

              <!-- 分镜包含的角色 -->
              <div
                v-if="shot.characters && shot.characters.length > 0"
                class="shot-characters"
              >
                <el-tag 
                  v-for="charName in shot.characters" 
                  :key="charName"
                  size="small"
                  type="success"
                  style="margin-right: 4px; margin-bottom: 4px;"
                >
                  {{ charName }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 批量生成对话框 -->
    <el-dialog
      v-model="showBatchDialog"
      title="批量生成关键帧"
      width="500px"
    >
      <el-form
        :model="batchFormData"
        label-width="100px"
      >
        <el-form-item label="API Key">
          <el-select
            v-model="batchFormData.apiKeyId"
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
            v-model="batchFormData.model" 
            placeholder="选择模型" 
            style="width: 100%"
            :loading="loadingBatchModels"
            filterable
            allow-create
            default-first-option
          >
            <el-option
              v-for="model in batchModelOptions"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchDialog = false">
          取消
        </el-button>
        <el-button 
          type="primary" 
          :disabled="!batchFormData.apiKeyId || !batchFormData.model" 
          @click="handleBatchDialogConfirm"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 单个关键帧生成对话框 -->
    <el-dialog
      v-model="showKeyframeDialog"
      :title="keyframeDialogType === 'generate' ? '生成关键帧' : '重新生成关键帧'"
      width="700px"
    >
      <el-form
        :model="keyframeFormData"
        label-width="100px"
      >
        <el-form-item label="API Key">
          <el-select
            v-model="keyframeFormData.apiKeyId"
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
            v-model="keyframeFormData.model" 
            placeholder="选择模型" 
            style="width: 100%"
            :loading="loadingKeyframeModels"
            filterable
            allow-create
            default-first-option
          >
            <el-option
              v-for="model in keyframeModelOptions"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="生成提示词">
          <el-input
            v-model="keyframeFormData.prompt"
            type="textarea"
            :rows="12"
            placeholder="专业提示词（可编辑调整）"
            style="font-family: monospace; font-size: 12px;"
          />
          <div style="margin-top: 8px; color: #909399; font-size: 12px;">
            💡 提示词已包含场景、分镜和角色信息，强调真人电影风格。您可以根据需要调整。
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showKeyframeDialog = false">
          取消
        </el-button>
        <el-button 
          type="primary" 
          :disabled="!keyframeFormData.apiKeyId || !keyframeFormData.model" 
          @click="handleKeyframeDialogConfirm"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="showImageViewer"
      :url-list="[currentPreviewImage]"
      @close="showImageViewer = false"
    />

    <!-- 历史记录面板 -->
    <GenerationHistoryPanel
      v-model="showHistory"
      resource-type="shot_keyframe"
      :resource-id="currentHistoryResourceId"
      media-type="image"
      @selected="handleHistorySelected"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture, ZoomIn, Clock } from '@element-plus/icons-vue'
import GenerationHistoryPanel from '@/components/GenerationHistoryPanel.vue'
import api from '@/services/api'

const props = defineProps({
  sceneGroups: {
    type: Array,
    default: () => []
  },
  canGenerate: {
    type: Boolean,
    default: true
  },
  apiKeys: {
    type: Array,
    default: () => []
  },
  generatingIds: {
    type: Set,
    default: () => new Set()
  },
  batchGenerating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['batch-generate', 'generate-keyframe', 'refresh'])

const activeScenes = ref([])

// 批量生成
const showBatchDialog = ref(false)
const batchFormData = ref({
  apiKeyId: '',
  model: ''
})
const batchModelOptions = ref([])
const loadingBatchModels = ref(false)

// 单个生成
const showKeyframeDialog = ref(false)
const keyframeDialogType = ref('generate')
const currentShot = ref(null)
const keyframeFormData = ref({
  apiKeyId: '',
  model: '',
  prompt: ''
})
const keyframeModelOptions = ref([])
const loadingKeyframeModels = ref(false)

// 图片预览
const showImageViewer = ref(false)
const currentPreviewImage = ref('')

// 历史记录相关
const showHistory = ref(false)
const currentHistoryResourceId = ref('')

const handleShowHistory = (shotId) => {
  currentHistoryResourceId.value = shotId
  showHistory.value = true
}

const handleHistorySelected = async () => {
  ElMessage.success('已切换到选中的历史版本')
  emit('refresh')
}

// 监听批量生成API Key变化
watch(() => batchFormData.value.apiKeyId, async (newKeyId) => {
  if (!newKeyId) {
    batchModelOptions.value = []
    batchFormData.value.model = ''
    return
  }
  
  loadingBatchModels.value = true
  try {
    const models = await api.get(`/api-keys/${newKeyId}/models?type=image`)
    batchModelOptions.value = models || []
    if (batchModelOptions.value.length > 0) {
      batchFormData.value.model = batchModelOptions.value[0]
    }
  } catch (error) {
    console.error('获取模型列表失败', error)
    ElMessage.warning('获取模型列表失败')
    batchModelOptions.value = []
    batchFormData.value.model = ''
  } finally {
    loadingBatchModels.value = false
  }
})

// 监听单个生成API Key变化
watch(() => keyframeFormData.value.apiKeyId, async (newKeyId) => {
  if (!newKeyId) {
    keyframeModelOptions.value = []
    keyframeFormData.value.model = ''
    return
  }
  
  loadingKeyframeModels.value = true
  try {
    const models = await api.get(`/api-keys/${newKeyId}/models?type=image`)
    keyframeModelOptions.value = models || []
    if (keyframeModelOptions.value.length > 0) {
      keyframeFormData.value.model = keyframeModelOptions.value[0]
    }
  } catch (error) {
    console.error('获取模型列表失败', error)
    ElMessage.warning('获取模型列表失败')
    keyframeModelOptions.value = []
    keyframeFormData.value.model = ''
  } finally {
    loadingKeyframeModels.value = false
  }
})

const handleBatchGenerateClick = () => {
  batchFormData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: ''
  }
  showBatchDialog.value = true
}

const handleBatchDialogConfirm = () => {
  if (!batchFormData.value.apiKeyId || !batchFormData.value.model) {
    return
  }
  emit('batch-generate', batchFormData.value.apiKeyId, batchFormData.value.model)
  showBatchDialog.value = false
}

const handleGenerateKeyframe = (shot) => {
  currentShot.value = shot
  keyframeDialogType.value = 'generate'
  keyframeFormData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: '',
    prompt: shot.generated_prompt || shot.shot || ''
  }
  showKeyframeDialog.value = true
}

const handleRegenerateKeyframe = (shot) => {
  currentShot.value = shot
  keyframeDialogType.value = 'regenerate'
  keyframeFormData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: '',
    prompt: shot.generated_prompt || shot.shot || ''
  }
  showKeyframeDialog.value = true
}

const handleKeyframeDialogConfirm = () => {
  if (!keyframeFormData.value.apiKeyId || !keyframeFormData.value.model || !currentShot.value) {
    return
  }
  emit('generate-keyframe', 
    currentShot.value.id, 
    keyframeFormData.value.apiKeyId, 
    keyframeFormData.value.model,
    keyframeFormData.value.prompt
  )
  showKeyframeDialog.value = false
}

const handlePreviewImage = (url) => {
  currentPreviewImage.value = url
  showImageViewer.value = true
}
</script>

<style scoped>
.keyframe-panel {
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
}

.scene-number {
  font-weight: 600;
  font-size: 16px;
  color: #409eff;
}

.keyframe-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.keyframe-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
  background: white;
}

.keyframe-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.keyframe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.shot-number {
  font-weight: 600;
  color: #67c23a;
  font-size: 14px;
  flex-shrink: 0;
}

.shot-actions {
  flex-shrink: 0;
}

.shot-description {
  margin-bottom: 12px;
}

.shot-description p {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.shot-description {
  margin-bottom: 12px;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.shot-description p {
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.shot-characters {
  margin-top: 12px;
  margin-bottom: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.keyframe-image {
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  aspect-ratio: 16/9;
}

.keyframe-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s;
}

.keyframe-image:hover img {
  transform: scale(1.05);
}

.keyframe-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
  font-size: 32px;
}

.keyframe-image:hover .keyframe-overlay {
  opacity: 1;
}

.keyframe-placeholder {
  aspect-ratio: 16/9;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.keyframe-placeholder p {
  margin: 8px 0 0 0;
  font-size: 13px;
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
</style>
