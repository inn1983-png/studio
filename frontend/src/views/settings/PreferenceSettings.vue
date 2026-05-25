<template>
  <div class="setting-section">
    <h2>偏好设置</h2>
    <p>自定义应用程序的外观和行为</p>

    <el-form
      :model="preferencesForm"
      label-width="120px"
      class="preferences-form"
    >
      <el-form-item label="主题模式">
        <el-radio-group
          v-model="preferencesForm.theme"
          @change="savePreferences"
        >
          <el-radio label="light">
            <div class="preference-option">
              <el-icon><Sunny /></el-icon>
              <span>浅色模式</span>
            </div>
          </el-radio>
          <el-radio label="dark">
            <div class="preference-option">
              <el-icon><Moon /></el-icon>
              <span>深色模式</span>
            </div>
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="界面语言">
        <el-select
          v-model="preferencesForm.language"
          placeholder="选择界面语言"
          @change="savePreferences"
        >
          <el-option
            label="简体中文"
            value="zh-CN"
          />
          <el-option
            label="English"
            value="en-US"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="时区">
        <el-select
          v-model="preferencesForm.timezone"
          placeholder="选择时区"
          @change="savePreferences"
        >
          <el-option
            label="Asia/Shanghai"
            value="Asia/Shanghai"
          />
          <el-option
            label="UTC"
            value="UTC"
          />
          <el-option
            label="America/New_York"
            value="America/New_York"
          />
          <el-option
            label="Europe/London"
            value="Europe/London"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="自动保存">
        <el-switch
          v-model="preferencesForm.autoSave"
          @change="savePreferences"
        />
        <span class="setting-description">自动保存您的编辑内容</span>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Sunny, Moon } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

// 偏好设置表单
const preferencesForm = reactive({
  theme: 'light',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  autoSave: true
})

// 应用主题设置
const applyTheme = (theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// 保存偏好设置
const savePreferences = async () => {
  try {
    const updateData = {
      preferences: {
        theme: preferencesForm.theme,
        autoSave: preferencesForm.autoSave
      },
      timezone: preferencesForm.timezone,
      language: preferencesForm.language
    }

    await authStore.updateProfile(updateData)
    applyTheme(preferencesForm.theme)
    ElMessage.success('偏好设置已保存')
  } catch (error) {
    console.error('保存偏好设置失败:', error)
    ElMessage.error('保存偏好设置失败，请重试')
  }
}

// 加载偏好设置
const loadPreferences = async () => {
  try {
    if (authStore.user) {
      if (authStore.user.preferences) {
        preferencesForm.theme = authStore.user.preferences.theme || 'light'
        preferencesForm.autoSave = authStore.user.preferences.autoSave !== undefined ? authStore.user.preferences.autoSave : true
      }

      preferencesForm.language = authStore.user.language || 'zh-CN'
      preferencesForm.timezone = authStore.user.timezone || 'Asia/Shanghai'

      applyTheme(preferencesForm.theme)
    }
  } catch (error) {
    console.error('加载偏好设置失败:', error)
    preferencesForm.theme = 'light'
    preferencesForm.language = 'zh-CN'
    preferencesForm.timezone = 'Asia/Shanghai'
    preferencesForm.autoSave = true
    applyTheme(preferencesForm.theme)
  }
}

onMounted(() => {
  loadPreferences()
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

.preferences-form {
  max-width: 600px;
}

.preference-option {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.setting-description {
  margin-left: var(--space-md);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
