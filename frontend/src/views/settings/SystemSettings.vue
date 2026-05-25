<template>
  <div class="setting-section">
    <h2>系统参数</h2>
    <p>配置系统运行参数（需要重启服务生效）</p>

    <el-form
      :model="systemForm"
      label-width="140px"
      class="system-form"
    >
      <el-divider content-position="left">
        任务队列
      </el-divider>

      <el-form-item label="最大重试次数">
        <el-input-number
          v-model="systemForm.maxRetries"
          :min="0"
          :max="10"
        />
        <span class="param-hint">任务失败后最大重试次数</span>
      </el-form-item>

      <el-form-item label="重试延迟(秒)">
        <el-select
          v-model="systemForm.retryDelayPreset"
          @change="handleDelayPresetChange"
        >
          <el-option
            label="快速 (30s/60s/120s)"
            value="fast"
          />
          <el-option
            label="标准 (60s/300s/900s)"
            value="standard"
          />
          <el-option
            label="慢速 (120s/600s/1800s)"
            value="slow"
          />
        </el-select>
        <span class="param-hint">每次重试的等待时间</span>
      </el-form-item>

      <el-divider content-position="left">
        视频生成
      </el-divider>

      <el-form-item label="默认视频模型">
        <el-input
          v-model="systemForm.defaultVideoModel"
          placeholder="留空使用默认"
        />
      </el-form-item>

      <el-form-item label="视频合成超时(秒)">
        <el-input-number
          v-model="systemForm.videoTimeout"
          :min="60"
          :max="3600"
          :step="60"
        />
      </el-form-item>

      <el-divider content-position="left">
        存储
      </el-divider>

      <el-form-item label="MinIO 端点">
        <el-input
          v-model="systemForm.minioEndpoint"
          placeholder="localhost:9000"
        />
      </el-form-item>

      <el-form-item label="文件桶名">
        <el-input
          v-model="systemForm.filesBucket"
          placeholder="txtovideo-files"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="saving"
          @click="saveSystem"
        >
          保存参数
        </el-button>
        <el-button @click="resetSystem">
          重置默认
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const saving = ref(false)

const systemForm = reactive({
  maxRetries: 3,
  retryDelayPreset: 'standard',
  defaultVideoModel: '',
  videoTimeout: 600,
  minioEndpoint: 'localhost:9000',
  filesBucket: 'txtovideo-files'
})

const handleDelayPresetChange = (val) => {
  systemForm.retryDelayPreset = val
}

const loadSystem = () => {
  const saved = localStorage.getItem('system_params')
  if (saved) {
    try {
      const data = JSON.parse(saved)
      Object.assign(systemForm, data)
    } catch { /* ignore parse errors */ }
  }
}

const saveSystem = async () => {
  saving.value = true
  try {
    localStorage.setItem('system_params', JSON.stringify(systemForm))
    ElMessage.success('系统参数已保存（部分参数需要重启服务生效）')
  } catch (error) {
    ElMessage.error('保存系统参数失败')
  } finally {
    saving.value = false
  }
}

const resetSystem = () => {
  systemForm.maxRetries = 3
  systemForm.retryDelayPreset = 'standard'
  systemForm.defaultVideoModel = ''
  systemForm.videoTimeout = 600
  systemForm.minioEndpoint = 'localhost:9000'
  systemForm.filesBucket = 'txtovideo-files'
  localStorage.removeItem('system_params')
  ElMessage.info('已重置为默认参数')
}

onMounted(() => {
  loadSystem()
})
</script>

<style scoped>
.setting-section {
  animation: fadeIn 0.3s ease-in-out;
}

.setting-section h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
}

.setting-section > p {
  color: var(--text-secondary);
  margin-bottom: var(--space-xl);
}

.system-form {
  max-width: 600px;
}

.param-hint {
  margin-left: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
