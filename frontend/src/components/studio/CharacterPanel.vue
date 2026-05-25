<template>
  <div class="character-panel">
    <div class="panel-header">
      <h3>角色管理</h3>
      <div class="actions">
        <el-button 
          type="primary" 
          :loading="extracting"
          :disabled="!canExtract"
          @click="handleExtractClick"
        >
          提取角色
        </el-button>
        <el-button 
          type="success"
          :loading="batchGenerating"
          :disabled="characters.length === 0 || batchGenerating"
          @click="handleBatchGenerateClick"
        >
          批量生成形象
        </el-button>
      </div>
    </div>

    <div class="character-list">
      <el-empty
        v-if="characters.length === 0"
        description="暂无角色，请先提取角色"
      />
      
      <div
        v-else
        class="character-grid"
      >
        <div 
          v-for="char in characters" 
          :key="char.id"
          class="character-card"
        >
          <div
            class="character-avatar"
            @click="handleImagePreview(char.avatar_url)"
          >
            <img
              v-if="char.avatar_url"
              :src="char.avatar_url"
              :alt="char.name"
            >
            <div
              v-else
              class="avatar-placeholder"
            >
              <el-icon :size="40">
                <User />
              </el-icon>
            </div>
            <div
              v-if="char.avatar_url"
              class="preview-overlay"
            >
              <el-icon :size="24">
                <ZoomIn />
              </el-icon>
            </div>
          </div>
          
          <div class="character-info">
            <h4>{{ char.name }}</h4>
            <p class="role">
              {{ char.role_description }}
            </p>
            <p class="traits">
              {{ char.visual_traits }}
            </p>
          </div>

          <!-- 参考图画廊 -->
          <div class="reference-gallery">
            <div class="gallery-header">
              <span v-if="char.reference_images && char.reference_images.length > 0">参考图 ({{ char.reference_images.length }})</span>
              <span v-else>参考图</span>
              <el-upload
                class="upload-btn-inline"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="(file) => handleUploadReferenceImage(char.id, file)"
              >
                <el-button
                  type="primary"
                  size="small"
                  icon="Plus"
                  circle
                />
              </el-upload>
            </div>
            <div
              v-if="char.reference_images && char.reference_images.length > 0"
              class="gallery-images"
            >
              <div 
                v-for="(imgUrl, index) in char.reference_images" 
                :key="index"
                class="gallery-item"
              >
                <img
                  :src="imgUrl"
                  :alt="`参考图${index + 1}`"
                  @click="handleImagePreview(imgUrl)"
                >
                <el-button
                  class="delete-btn"
                  type="danger"
                  size="small"
                  icon="Delete"
                  circle
                  @click.stop="handleDeleteReferenceImage(char.id, index)"
                />
              </div>
            </div>
          </div>

          <div class="character-actions">
            <el-button 
              v-if="!char.avatar_url"
              type="primary" 
              size="small"
              :loading="generatingIds.has(char.id)"
              :disabled="generatingIds.has(char.id)"
              @click="handleGenerateClick(char)"
            >
              生成形象
            </el-button>
            <template v-else>
              <el-button 
                type="success" 
                size="small"
                icon="Check"
                disabled
              >
                已生成
              </el-button>
              <el-button 
                type="warning" 
                size="small"
                icon="Refresh"
                :loading="generatingIds.has(char.id)"
                :disabled="generatingIds.has(char.id)"
                @click="handleRegenerateClick(char)"
              >
                重新生成
              </el-button>
              <el-button 
                type="info" 
                size="small"
                @click="handleShowHistory(char.id)"
              >
                <el-icon><Clock /></el-icon>
              </el-button>
            </template>
            <el-button 
              type="danger" 
              size="small"
              icon="Delete"
              @click="$emit('delete-character', char.id)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- API Key选择对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="dialogTitle"
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
        <el-form-item
          v-if="dialogType === 'generate' || dialogType === 'regenerate'"
          label="提示词"
        >
          <el-input 
            v-model="formData.prompt" 
            type="textarea"
            :rows="3"
            placeholder="可选，留空使用默认提示词"
          />
        </el-form-item>
        <el-form-item
          v-if="dialogType === 'generate' || dialogType === 'regenerate'"
          label="参考图"
        >
          <div class="reference-image-section">
            <div
              v-if="currentCharacter && currentCharacter.reference_images && currentCharacter.reference_images.length > 0"
              class="existing-references"
            >
              <div class="section-label">
                选择参考图（最多3张）:
              </div>
              <div class="reference-options">
                <div 
                  v-for="(imgUrl, index) in currentCharacter.reference_images" 
                  :key="index"
                  class="reference-option"
                  :class="{ selected: formData.selectedReferenceIndices?.includes(index) }"
                  @click="toggleReferenceSelection(index)"
                >
                  <img
                    :src="imgUrl"
                    :alt="`参考图${index + 1}`"
                  >
                  <el-icon
                    v-if="formData.selectedReferenceIndices?.includes(index)"
                    class="check-icon"
                  >
                    <Check />
                  </el-icon>
                  <div
                    v-if="formData.selectedReferenceIndices?.includes(index)"
                    class="selection-badge"
                  >
                    {{ formData.selectedReferenceIndices.indexOf(index) + 1 }}
                  </div>
                </div>
              </div>
            </div>
            <div
              v-else
              class="no-references"
            >
              <el-empty
                description="暂无参考图，请在角色卡片上上传"
                :image-size="60"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :disabled="!formData.apiKeyId || !formData.model"
          @click="handleDialogConfirm"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="showImageViewer"
      :url-list="[previewImageUrl]"
      @close="showImageViewer = false"
    />

    <!-- 历史记录面板 -->
    <GenerationHistoryPanel
      v-model="showHistory"
      resource-type="character_avatar"
      :resource-id="currentHistoryResourceId"
      media-type="image"
      @selected="handleHistorySelected"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { User, ZoomIn, Clock, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import GenerationHistoryPanel from '@/components/GenerationHistoryPanel.vue'
import api from '@/services/api'
import movieService from '@/services/movie'

const props = defineProps({
  characters: {
    type: Array,
    default: () => []
  },
  extracting: {
    type: Boolean,
    default: false
  },
  generatingIds: {
    type: Set,
    default: () => new Set()
  },
  batchGenerating: {
    type: Boolean,
    default: false
  },
  canExtract: {
    type: Boolean,
    default: true
  },
  apiKeys: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'extract-characters',
  'generate-avatar',
  'delete-character',
  'batch-generate',
  'refresh'
])

const showDialog = ref(false)
const dialogType = ref('extract')
const dialogTitle = ref('')
const currentCharacter = ref(null)
const formData = ref({
  apiKeyId: '',
  model: '',
  prompt: '',
  selectedReferenceIndices: []
})
const modelOptions = ref([])
const loadingModels = ref(false)

// 图片预览
const showImageViewer = ref(false)
const previewImageUrl = ref('')

const handleImagePreview = (url) => {
  if (url) {
    previewImageUrl.value = url
    showImageViewer.value = true
  }
}

// 历史记录相关
const showHistory = ref(false)
const currentHistoryResourceId = ref('')

const handleShowHistory = (characterId) => {
  currentHistoryResourceId.value = characterId
  showHistory.value = true
}

const handleHistorySelected = async () => {
  ElMessage.success('已切换到选中的历史版本')
  emit('refresh')
}

// 监听API Key或对话框类型变化，自动加载模型列表
watch([() => formData.value.apiKeyId, () => dialogType.value], async ([newKeyId, newType]) => {
  if (!newKeyId) {
    modelOptions.value = []
    formData.value.model = ''
    return
  }
  
  loadingModels.value = true
  try {
    // 根据对话框类型选择模型类型
    // extract = 提取角色 = 文本模型
    // generate/regenerate/batch = 生成形象 = 图片模型
    const modelType = newType === 'extract' ? 'text' : 'image'
    const models = await api.get(`/api-keys/${newKeyId}/models?type=${modelType}`)
    modelOptions.value = models || []
    if (modelOptions.value.length > 0) {
      formData.value.model = modelOptions.value[0]
    } else {
      formData.value.model = ''
    }
  } catch (error) {
    console.error('获取模型列表失败', error)
    ElMessage.warning('获取模型列表失败')
    modelOptions.value = []
    formData.value.model = ''
  } finally {
    loadingModels.value = false
  }
})

const handleExtractClick = () => {
  dialogType.value = 'extract'
  dialogTitle.value = '提取角色'
  formData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: '',
    prompt: '',
    selectedReferenceIndices: []
  }
  showDialog.value = true
}

const handleGenerateClick = (char) => {
  dialogType.value = 'generate'
  dialogTitle.value = `生成角色形象 - ${char.name}`
  currentCharacter.value = char
  formData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: '',
    prompt: char.generated_prompt || '',
    selectedReferenceIndices: []
  }
  showDialog.value = true
}

const handleRegenerateClick = (char) => {
  dialogType.value = 'regenerate'
  dialogTitle.value = `重新生成角色形象 - ${char.name}`
  currentCharacter.value = char
  formData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: '',
    prompt: char.generated_prompt || '',  // 预填充角色的三视图提示词
    referenceImage: null,
    referenceImagePreview: null,
    selectedReferenceIndex: null
  }
  showDialog.value = true
}

const handleBatchGenerateClick = async () => {
  dialogType.value = 'batch'
  dialogTitle.value = '批量生成角色形象'
  const defaultApiKey = props.apiKeys[0]?.id || ''
  formData.value = {
    apiKeyId: defaultApiKey,
    model: '',
    prompt: '',
    selectedReferenceIndices: []
  }
  
  // 强制重新加载图片模型列表
  if (defaultApiKey) {
    loadingModels.value = true
    try {
      const models = await api.get(`/api-keys/${defaultApiKey}/models?type=image`)
      modelOptions.value = models || []
      if (modelOptions.value.length > 0) {
        formData.value.model = modelOptions.value[0]
      }
    } catch (error) {
      console.error('获取模型列表失败', error)
      ElMessage.warning('获取模型列表失败')
      modelOptions.value = []
    } finally {
      loadingModels.value = false
    }
  }
  
  showDialog.value = true
}

const handleDialogConfirm = () => {
  if (!formData.value.apiKeyId || !formData.value.model) {
    return
  }

  if (dialogType.value === 'extract') {
    emit('extract-characters', formData.value.apiKeyId, formData.value.model)
  } else if (dialogType.value === 'generate' || dialogType.value === 'regenerate') {
    // 传递选中的参考图索引
    emit('generate-avatar', 
      currentCharacter.value.id,
      formData.value.apiKeyId,
      formData.value.model,
      formData.value.prompt,
      null,
      formData.value.selectedReferenceIndices
    )
  } else if (dialogType.value === 'batch') {
    emit('batch-generate', formData.value.apiKeyId, formData.value.model)
  }

  showDialog.value = false
}

// 切换参考图选择（最多3张）
const toggleReferenceSelection = (index) => {
  if (!formData.value.selectedReferenceIndices) {
    formData.value.selectedReferenceIndices = []
  }
  
  const currentIndex = formData.value.selectedReferenceIndices.indexOf(index)
  
  if (currentIndex > -1) {
    // 已选中，取消选择
    formData.value.selectedReferenceIndices.splice(currentIndex, 1)
  } else {
    // 未选中，添加选择
    if (formData.value.selectedReferenceIndices.length >= 3) {
      ElMessage.warning('最多只能选择3张参考图')
      return
    }
    formData.value.selectedReferenceIndices.push(index)
  }
}

// 上传参考图
const handleUploadReferenceImage = async (characterId, file) => {
  try {
    await movieService.uploadReferenceImage(characterId, file.raw)
    ElMessage.success('参考图上传成功')
    
    // 重新加载角色列表
    emit('refresh')
  } catch (error) {
    console.error('上传参考图失败:', error)
    ElMessage.error('上传参考图失败')
  }
}

// 删除参考图
const handleDeleteReferenceImage = async (characterId, imageIndex) => {
  try {
    await ElMessageBox.confirm('确定要删除这张参考图吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/movie/characters/${characterId}/reference-images/${imageIndex}`)
    ElMessage.success('参考图已删除')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除参考图失败')
    }
  }
}
</script>

<style scoped>
.character-panel {
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
  gap: 10px;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.character-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.character-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.character-avatar {
  width: 100%;
  height: 160px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  position: relative;
  cursor: pointer;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  color: #c0c4cc;
}

.preview-overlay {
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
}

.character-avatar:hover .preview-overlay {
  opacity: 1;
}

.character-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.character-info .role {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

.character-info .traits {
  margin: 0;
  font-size: 12px;
  color: #909399;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

.character-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.character-actions .el-button {
  flex: 1;
  min-width: 80px;
}

/* 参考图画廊 */
.reference-gallery {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.gallery-header {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.gallery-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.gallery-item {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.gallery-item:hover {
  transform: scale(1.05);
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gallery-item .delete-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  opacity: 0;
  transition: opacity 0.2s;
  width: 20px;
  height: 20px;
  padding: 0;
  min-height: 20px;
}

.gallery-item:hover .delete-btn {
  opacity: 1;
}

/* 参考图上传区域 */
.reference-image-section {
  width: 100%;
}

.section-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.existing-references {
  margin-bottom: 16px;
}

.reference-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.reference-option {
  position: relative;
  width: 80px;
  height: 80px;
  border: 2px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.reference-option:hover {
  border-color: #409eff;
  transform: scale(1.05);
}

.reference-option.selected {
  border-color: #409eff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.3);
}

.reference-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reference-option .check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  padding: 2px;
  font-size: 14px;
}

.reference-option .selection-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.upload-new-reference {
  margin-top: 12px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reference-uploader {
  width: 100%;
}

.uploaded-previews {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border: 2px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-item .preview-badge {
  position: absolute;
  top: 4px;
  left: 4px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.preview-item .remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  padding: 0;
  min-height: 24px;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 200px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-preview .clear-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.upload-btn-inline {
  display: inline-block;
}

.upload-btn-inline .el-button {
  width: 28px;
  height: 28px;
  padding: 0;
}
</style>
