<template>
  <div class="setting-section">
    <h2>品牌配置</h2>
    <p>自定义应用程序的品牌信息（需要管理员权限）</p>

    <el-form
      v-loading="loading"
      :model="brandForm"
      label-width="120px"
      class="brand-form"
    >
      <el-divider content-position="left">
        基本信息
      </el-divider>

      <el-form-item label="应用名称">
        <el-input
          v-model="brandForm.appName"
          placeholder="应用名称"
        />
      </el-form-item>

      <el-form-item label="应用描述">
        <el-input
          v-model="brandForm.appDescription"
          placeholder="应用描述"
        />
      </el-form-item>

      <el-form-item label="Logo 文字">
        <el-input
          v-model="brandForm.logoText"
          placeholder="Logo 文字"
        />
      </el-form-item>

      <el-form-item label="版权声明">
        <el-input
          v-model="brandForm.copyright"
          placeholder="版权声明"
        />
      </el-form-item>

      <el-divider content-position="left">
        预览
      </el-divider>

      <div class="brand-preview">
        <div class="preview-sidebar">
          <div class="preview-logo">
            {{ brandForm.logoText }}
          </div>
        </div>
        <div class="preview-info">
          <h3>{{ brandForm.appName }}</h3>
          <p>{{ brandForm.appDescription }}</p>
          <span class="preview-copyright">{{ brandForm.copyright }}</span>
        </div>
      </div>

      <el-form-item>
        <el-button
          type="primary"
          :loading="saving"
          @click="saveBrand"
        >
          保存品牌配置
        </el-button>
        <el-button @click="resetBrand">
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useBrandStore } from '@/stores/brand'

const brandStore = useBrandStore()
const loading = ref(false)
const saving = ref(false)

const brandForm = reactive({
  appName: '',
  appDescription: '',
  logoText: '',
  copyright: ''
})

const loadBrand = async () => {
  loading.value = true
  try {
    await brandStore.fetchBrand()
    brandForm.appName = brandStore.name
    brandForm.appDescription = brandStore.description
    brandForm.logoText = brandStore.logoText
    brandForm.copyright = brandStore.copyright
  } catch (error) {
    console.error('加载品牌配置失败:', error)
  } finally {
    loading.value = false
  }
}

const saveBrand = async () => {
  saving.value = true
  try {
    brandStore.name = brandForm.appName
    brandStore.description = brandForm.appDescription
    brandStore.logoText = brandForm.logoText
    brandStore.copyright = brandForm.copyright

    localStorage.setItem('brand_config', JSON.stringify({
      appName: brandForm.appName,
      appDescription: brandForm.appDescription,
      logoText: brandForm.logoText,
      copyright: brandForm.copyright
    }))

    ElMessage.success('品牌配置已保存（本地覆盖）')
  } catch (error) {
    ElMessage.error('保存品牌配置失败')
  } finally {
    saving.value = false
  }
}

const resetBrand = async () => {
  localStorage.removeItem('brand_config')
  await loadBrand()
  ElMessage.info('已重置为服务端默认配置')
}

onMounted(() => {
  loadBrand()
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

.brand-form {
  max-width: 600px;
}

.brand-preview {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 20px;
}

.preview-sidebar {
  width: 60px;
  height: 40px;
  background: var(--primary-color, #409eff);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

.preview-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.preview-info p {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.preview-copyright {
  font-size: 11px;
  color: var(--text-tertiary);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
