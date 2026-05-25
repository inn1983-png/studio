<template>
  <el-dialog
    v-model="visible"
    :title="`生成历史 - ${mediaTypeLabel}`"
    width="800px"
    @close="handleClose"
  >
    <div
      v-loading="loading"
      class="history-panel"
    >
      <!-- 历史记录列表 -->
      <div
        v-if="histories.length > 0"
        class="history-list"
      >
        <div
          v-for="history in histories"
          :key="history.id"
          class="history-item"
          :class="{ selected: history.is_selected }"
        >
          <!-- 预览区域 -->
          <div class="preview-area">
            <img
              v-if="mediaType === 'image'"
              :src="history.result_url"
              :alt="history.prompt"
              class="preview-image"
              @click="handlePreview(history)"
            >
            <video
              v-else
              :src="history.result_url"
              class="preview-video"
              controls
              @click="handlePreview(history)"
            />
          </div>

          <!-- 信息区域 -->
          <div class="info-area">
            <div class="info-header">
              <el-tag
                v-if="history.is_selected"
                type="success"
                size="small"
              >
                当前使用
              </el-tag>
              <span class="create-time">
                {{ formatTime(history.created_at) }}
              </span>
            </div>

            <div class="prompt-text">
              <el-text
                line-clamp="2"
                :title="history.prompt"
              >
                {{ history.prompt }}
              </el-text>
            </div>

            <div class="info-footer">
              <span
                v-if="history.model"
                class="model-tag"
              >
                {{ history.model }}
              </span>
              <el-button
                v-if="!history.is_selected"
                type="primary"
                size="small"
                @click="handleSelect(history)"
              >
                使用此版本
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="暂无历史记录"
      />
    </div>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="预览"
      width="90%"
    >
      <img
        v-if="previewUrl && mediaType === 'image'"
        :src="previewUrl"
        style="width: 100%"
      >
      <video
        v-else-if="previewUrl && mediaType === 'video'"
        :src="previewUrl"
        style="width: 100%"
        controls
        autoplay
      />
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  resourceType: {
    type: String,
    required: true,
    validator: (value) => ['scene_image', 'shot_keyframe', 'character_avatar', 'transition_video'].includes(value)
  },
  resourceId: {
    type: String,
    required: true
  },
  mediaType: {
    type: String,
    required: true,
    validator: (value) => ['image', 'video'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'selected'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const histories = ref([])
const previewVisible = ref(false)
const previewUrl = ref('')

const mediaTypeLabel = computed(() => {
  const labels = {
    scene_image: '场景图',
    shot_keyframe: '关键帧',
    character_avatar: '角色头像',
    transition_video: '过渡视频'
  }
  return labels[props.resourceType] || '生成记录'
})

// 监听对话框打开，加载历史记录
watch(visible, async (newVal) => {
  if (newVal) {
    await loadHistory()
  }
})

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const endpoint = getHistoryEndpoint()
    const response = await api.get(endpoint)
    // API直接返回数组，不需要 .data
    histories.value = response || []
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

// 获取历史记录端点
const getHistoryEndpoint = () => {
  const endpoints = {
    scene_image: `/movie/generation-history/scenes/${props.resourceId}/images`,
    shot_keyframe: `/movie/generation-history/shots/${props.resourceId}/keyframes`,
    character_avatar: `/movie/generation-history/characters/${props.resourceId}/avatars`,
    transition_video: `/movie/generation-history/transitions/${props.resourceId}/videos`
  }
  return endpoints[props.resourceType]
}

// 选择历史记录
const handleSelect = async (history) => {
  loading.value = true
  try {
    const endpoint = getSelectEndpoint()
    await api.post(endpoint, {
      history_id: history.id
    })
    
    ElMessage.success('已切换到选中的版本')
    
    // 重新加载历史记录
    await loadHistory()
    
    // 通知父组件
    emit('selected', history)
  } catch (error) {
    console.error('选择历史记录失败:', error)
    ElMessage.error('切换失败，请重试')
  } finally {
    loading.value = false
  }
}

// 获取选择端点
const getSelectEndpoint = () => {
  const endpoints = {
    scene_image: `/movie/generation-history/scenes/${props.resourceId}/select-image`,
    shot_keyframe: `/movie/generation-history/shots/${props.resourceId}/select-keyframe`,
    character_avatar: `/movie/generation-history/characters/${props.resourceId}/select-avatar`,
    transition_video: `/movie/generation-history/transitions/${props.resourceId}/select-video`
  }
  return endpoints[props.resourceType]
}

// 预览
const handlePreview = (history) => {
  previewUrl.value = history.result_url
  previewVisible.value = true
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.history-panel {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  }

  &.selected {
    border-color: #67c23a;
    background-color: #f0f9ff;
  }
}

.preview-area {
  flex-shrink: 0;
  width: 200px;
  height: 150px;
  border-radius: 4px;
  overflow: hidden;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;

  .preview-image,
  .preview-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: pointer;
  }
}

.info-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .create-time {
    font-size: 12px;
    color: #909399;
  }
}

.prompt-text {
  flex: 1;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.info-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .model-tag {
    font-size: 12px;
    color: #909399;
    padding: 2px 8px;
    background-color: #f4f4f5;
    border-radius: 4px;
  }
}
</style>
