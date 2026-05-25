<template>
  <div class="shot-panel">
    <div class="panel-header">
      <h3>分镜列表</h3>
      <div class="actions">
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
      
      <!-- 按场景分组的折叠面板 -->
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
          
          <!-- 场景描述 -->
          <div class="scene-description">
            <p>{{ group.scene.scene }}</p>
          </div>

          <!-- 该场景的分镜列表 -->
          <div class="shot-grid">
            <div 
              v-for="shot in group.shots" 
              :key="shot.id"
              class="shot-card"
            >
              <div class="shot-header">
                <span class="shot-number">镜头 {{ shot.order_index }}</span>
                <el-tag
                  v-if="shot.keyframe_url"
                  type="success"
                  size="small"
                >
                  已生成关键帧
                </el-tag>
              </div>
              
              <div class="shot-content">
                <p class="shot-description">
                  {{ shot.shot }}
                </p>
                <p
                  v-if="shot.dialogue"
                  class="shot-dialogue"
                >
                  💬 {{ shot.dialogue }}
                </p>
                
                <!-- 显示分镜中的角色 -->
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
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 警告对话框 -->
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
            </el-icon>
            <span>所有现有分镜脚本</span>
          </div>
          <div class="warning-item">
            <el-icon color="#f56c6c">
              <Delete />
            </el-icon>
            <span>所有场景环境图</span>
          </div>
          <div class="warning-item">
            <el-icon color="#f56c6c">
              <Delete />
            </el-icon>
            <span>所有关键帧图片</span>
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
        <div class="dialog-footer">
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
            <el-icon><Delete /></el-icon>
            确认删除并重新提取
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 单场景重新提取警告对话框 -->
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
            </el-icon>
            <span>该场景的所有分镜脚本</span>
          </div>
          <div class="warning-item">
            <el-icon color="#e6a23c">
              <Delete />
            </el-icon>
            <span>该场景的所有关键帧图片</span>
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
        <div class="dialog-footer">
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
            <el-icon><Delete /></el-icon>
            确认删除并重新提取
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- API Key选择对话框 -->
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
import { ElMessage } from 'element-plus'
import { WarningFilled, Delete } from '@element-plus/icons-vue'
import api from '@/services/api'

const props = defineProps({
  sceneGroups: {
    type: Array,
    default: () => []
  },
  extracting: {
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
  },
  extractingScenes: {
    type: Set,
    default: () => new Set()
  }
})

const emit = defineEmits(['extract-shots', 'extract-single-scene-shots'])

const activeScenes = ref([])
const showDialog = ref(false)
const showWarningDialog = ref(false)
const formData = ref({
  apiKeyId: '',
  model: ''
})
const modelOptions = ref([])
const loadingModels = ref(false)
const currentSceneId = ref(null) // 当前要提取的场景ID
const showSingleSceneWarning = ref(false) // 单场景警告对话框

// 计算是否已有分镜
const hasShots = computed(() => {
  return props.sceneGroups.some(group => group.shots && group.shots.length > 0)
})

// 监听API Key变化，自动加载模型列表
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
    ElMessage.warning('获取模型列表失败')
    modelOptions.value = []
    formData.value.model = ''
  } finally {
    loadingModels.value = false
  }
})

const handleExtractClick = () => {
  // 如果已有分镜，先显示警告对话框
  if (hasShots.value) {
    showWarningDialog.value = true
  } else {
    // 没有分镜，直接显示提取对话框
    formData.value = {
      apiKeyId: props.apiKeys[0]?.id || '',
      model: ''
    }
    showDialog.value = true
  }
}

const handleWarningConfirm = () => {
  showWarningDialog.value = false
  // 确认后显示提取对话框
  formData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: ''
  }
  showDialog.value = true
}

const handleDialogConfirm = () => {
  if (!formData.value.apiKeyId || !formData.value.model) {
    return
  }
  emit('extract-shots', formData.value.apiKeyId, formData.value.model)
  showDialog.value = false
}

const handleSingleSceneExtractClick = (sceneId) => {
  currentSceneId.value = sceneId
  showSingleSceneWarning.value = true
}

const handleSingleSceneWarningConfirm = () => {
  showSingleSceneWarning.value = false
  // 确认后显示提取对话框
  formData.value = {
    apiKeyId: props.apiKeys[0]?.id || '',
    model: ''
  }
  showDialog.value = true
}

const handleSingleSceneDialogConfirm = () => {
  if (!formData.value.apiKeyId || !formData.value.model || !currentSceneId.value) {
    return
  }
  emit('extract-single-scene-shots', currentSceneId.value, formData.value.apiKeyId, formData.value.model)
  showDialog.value = false
  currentSceneId.value = null
}
</script>

<style scoped>
.shot-panel {
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

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.shot-number {
  font-weight: 600;
  color: #67c23a;
  font-size: 14px;
}

.shot-content {
  margin-bottom: 12px;
}

.shot-description {
  margin: 0 0 8px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.shot-dialogue {
  margin: 8px 0;
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

/* 折叠面板样式优化 */
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
