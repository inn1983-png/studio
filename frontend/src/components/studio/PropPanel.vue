<template>
  <div class="prop-panel">
    <div class="panel-header">
      <h3>道具管理</h3>
      <div class="actions">
        <el-button
          type="primary"
          :loading="extracting"
          :disabled="!canExtract"
          @click="handleExtractClick"
        >
          提取道具
        </el-button>
        <el-button
          type="success"
          :loading="batchGenerating"
          :disabled="props.length === 0 || batchGenerating"
          @click="handleBatchGenerateClick"
        >
          批量生成图片
        </el-button>
      </div>
    </div>

    <div class="prop-list">
      <el-empty
        v-if="props.length === 0"
        description="暂无道具，请先提取道具"
      />

      <div
        v-else
        class="prop-grid"
      >
        <div
          v-for="prop in props"
          :key="prop.id"
          class="prop-card"
        >
          <div
            class="prop-image"
            @click="handleImagePreview(prop.image_url)"
          >
            <img
              v-if="prop.image_url"
              :src="prop.image_url"
              :alt="prop.name"
            >
            <div
              v-else
              class="image-placeholder"
            >
              <el-icon :size="40">
                <Box />
              </el-icon>
            </div>
            <div
              v-if="prop.image_url"
              class="preview-overlay"
            >
              <el-icon :size="24">
                <ZoomIn />
              </el-icon>
            </div>
          </div>

          <div class="prop-info">
            <h4>{{ prop.name }}</h4>
            <el-tag
              v-if="prop.category"
              size="small"
              type="info"
            >
              {{ prop.category }}
            </el-tag>
            <p class="description">
              {{ prop.description }}
            </p>
            <p
              v-if="prop.visual_traits"
              class="traits"
            >
              {{ prop.visual_traits }}
            </p>
          </div>

          <div class="reference-gallery">
            <div class="gallery-header">
              <span v-if="prop.reference_images && prop.reference_images.length > 0">参考图 ({{ prop.reference_images.length }})</span>
              <span v-else>参考图</span>
              <el-upload
                class="upload-btn-inline"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="(file) => handleUploadReferenceImage(prop.id, file)"
              >
                <el-button
                  size="small"
                  text
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </el-upload>
            </div>
            <div
              v-if="prop.reference_images && prop.reference_images.length > 0"
              class="gallery-images"
            >
              <div
                v-for="(img, idx) in prop.reference_images"
                :key="idx"
                class="gallery-thumb"
                @click="handleImagePreview(img)"
              >
                <img
                  :src="img"
                  :alt="`参考图 ${idx + 1}`"
                >
                <el-button
                  class="delete-thumb"
                  size="small"
                  circle
                  @click.stop="handleDeleteReferenceImage(prop.id, idx)"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <div class="prop-actions">
            <el-button
              type="primary"
              size="small"
              :loading="generatingIds.has(prop.id)"
              :disabled="generatingIds.has(prop.id)"
              @click="handleGenerateClick(prop)"
            >
              {{ prop.image_url ? '重新生成' : '生成图片' }}
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDelete(prop.id)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="previewVisible"
      title="图片预览"
      width="70%"
    >
      <img
        v-if="previewUrl"
        :src="previewUrl"
        style="width: 100%"
      >
    </el-dialog>

    <el-dialog
      v-model="generateDialogVisible"
      title="生成道具图"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="API Key">
          <el-select
            v-model="generateForm.api_key_id"
            placeholder="选择API Key"
            style="width: 100%"
          >
            <el-option
              v-for="key in apiKeys"
              :key="key.id"
              :label="`${key.name || key.provider} (${key.provider})`"
              :value="key.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型">
          <el-input
            v-model="generateForm.model"
            placeholder="留空使用默认模型"
          />
        </el-form-item>
        <el-form-item label="提示词">
          <el-input
            v-model="generateForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="留空使用自动生成的提示词"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="generatingIds.has(currentPropId)"
          @click="handleGenerateConfirm"
        >
          生成
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="extractDialogVisible"
      title="提取道具"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="API Key">
          <el-select
            v-model="extractForm.api_key_id"
            placeholder="选择API Key"
            style="width: 100%"
          >
            <el-option
              v-for="key in apiKeys"
              :key="key.id"
              :label="`${key.name || key.provider} (${key.provider})`"
              :value="key.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型">
          <el-input
            v-model="extractForm.model"
            placeholder="留空使用默认模型"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="extractDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="extracting"
          @click="handleExtractConfirm"
        >
          提取
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, ZoomIn, Plus, Close } from '@element-plus/icons-vue'
import { usePropWorkflow } from '@/composables/usePropWorkflow'
import movieService from '@/services/movie'
import apiService from '@/services/api'

const props = defineProps({
  projectId: { type: String, default: '' },
  chapterId: { type: String, default: '' }
})

const projectIdRef = computed(() => props.projectId)
const { extracting, generatingIds, batchGenerating, loadProps, extractProps, generateImage, batchGenerateImages, deleteProp } = usePropWorkflow(projectIdRef)

const canExtract = computed(() => !!props.chapterId && !!props.projectId)

const apiKeys = ref([])
const previewVisible = ref(false)
const previewUrl = ref('')
const generateDialogVisible = ref(false)
const extractDialogVisible = ref(false)
const currentPropId = ref('')

const generateForm = ref({ api_key_id: '', model: '', prompt: '' })
const extractForm = ref({ api_key_id: '', model: '' })

const loadApiKeys = async () => {
  try {
    const response = await apiService.getApiKeys()
    apiKeys.value = response.api_keys || []
  } catch (error) {
    console.error('Failed to load API keys:', error)
  }
}

const handleImagePreview = (url) => {
  if (!url) return
  previewUrl.value = url
  previewVisible.value = true
}

const handleExtractClick = () => {
  extractDialogVisible.value = true
}

const handleExtractConfirm = async () => {
  if (!extractForm.value.api_key_id) {
    ElMessage.warning('请选择API Key')
    return
  }
  extractDialogVisible.value = false
  await extractProps(props.chapterId, extractForm.value.api_key_id, extractForm.value.model || undefined)
}

const handleGenerateClick = (prop) => {
  currentPropId.value = prop.id
  generateForm.value = {
    api_key_id: '',
    model: '',
    prompt: prop.generated_prompt || ''
  }
  generateDialogVisible.value = true
}

const handleGenerateConfirm = async () => {
  if (!generateForm.value.api_key_id) {
    ElMessage.warning('请选择API Key')
    return
  }
  generateDialogVisible.value = false
  await generateImage(
    currentPropId.value,
    generateForm.value.api_key_id,
    generateForm.value.model || undefined,
    generateForm.value.prompt || undefined,
    'cinematic'
  )
}

const handleBatchGenerateClick = async () => {
  try {
    await ElMessageBox.confirm('确定要批量生成所有未生成图片的道具吗？', '批量生成', {
      type: 'warning'
    })
    if (apiKeys.value.length > 0) {
      const firstKey = apiKeys.value[0]
      await batchGenerateImages(firstKey.id)
    } else {
      ElMessage.warning('请先添加API Key')
    }
  } catch { /* ignore */ }
}

const handleDelete = async (propId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个道具吗？', '删除确认', { type: 'warning' })
    await deleteProp(propId)
  } catch { /* user cancelled */ }
}

const handleUploadReferenceImage = async (propId, file) => {
  try {
    await movieService.uploadPropReferenceImage(propId, file.raw)
    ElMessage.success('参考图上传成功')
    await loadProps()
  } catch (error) {
    ElMessage.error('参考图上传失败')
  }
}

const handleDeleteReferenceImage = async (propId, imageIndex) => {
  try {
    await movieService.deletePropReferenceImage(propId, imageIndex)
    ElMessage.success('参考图删除成功')
    await loadProps()
  } catch (error) {
    ElMessage.error('参考图删除失败')
  }
}

watch(() => props.projectId, (newVal) => {
  if (newVal) {
    loadProps()
  }
})

onMounted(() => {
  loadApiKeys()
  if (props.projectId) {
    loadProps()
  }
})
</script>

<style scoped>
.prop-panel {
  padding: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.actions {
  display: flex;
  gap: 8px;
}

.prop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.prop-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px;
  transition: box-shadow 0.2s;
}

.prop-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.prop-image {
  width: 100%;
  height: 160px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: var(--el-fill-color-lighter);
  margin-bottom: 12px;
}

.prop-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
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

.prop-image:hover .preview-overlay {
  opacity: 1;
}

.prop-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
}

.prop-info .description {
  margin: 4px 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prop-info .traits {
  margin: 4px 0;
  font-size: 12px;
  color: var(--el-text-color-regular);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.reference-gallery {
  margin: 8px 0;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.gallery-images {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.gallery-thumb {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.gallery-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-thumb {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px !important;
  height: 16px !important;
  min-width: 16px !important;
  min-height: 16px !important;
}

.prop-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
</style>
