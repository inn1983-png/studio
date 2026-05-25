<template>
  <div class="settings-page">
    <!-- 页面头部信息 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon">
          <Setting />
        </el-icon>
        系统设置
      </h1>
      <p class="page-description">
        管理您的账户和应用程序设置
      </p>
    </div>

    <div class="settings-content">
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="settings-menu">
            <el-menu
              :default-active="activeTab"
              mode="vertical"
              class="settings-nav"
              @select="handleMenuSelect"
            >
              <el-menu-item index="profile">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
              </el-menu-item>
              <el-menu-item index="account">
                <el-icon><Lock /></el-icon>
                <span>账户安全</span>
              </el-menu-item>
              <el-menu-item index="preferences">
                <el-icon><Setting /></el-icon>
                <span>偏好设置</span>
              </el-menu-item>
              <el-menu-item index="brand">
                <el-icon><PriceTag /></el-icon>
                <span>品牌配置</span>
              </el-menu-item>
              <el-menu-item index="system">
                <el-icon><Monitor /></el-icon>
                <span>系统参数</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-col>

        <el-col :span="16">
          <div class="settings-panel">
            <Transition
              name="fade"
              mode="out-in"
            >
              <component :is="currentTabComponent" />
            </Transition>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Setting, User, Lock, PriceTag, Monitor } from '@element-plus/icons-vue'
import ProfileSettings from './settings/ProfileSettings.vue'
import AccountSettings from './settings/AccountSettings.vue'
import PreferenceSettings from './settings/PreferenceSettings.vue'
import BrandSettings from './settings/BrandSettings.vue'
import SystemSettings from './settings/SystemSettings.vue'

const activeTab = ref('profile')

const currentTabComponent = computed(() => {
  switch (activeTab.value) {
    case 'profile':
      return ProfileSettings
    case 'account':
      return AccountSettings
    case 'preferences':
      return PreferenceSettings
    case 'brand':
      return BrandSettings
    case 'system':
      return SystemSettings
    default:
      return ProfileSettings
  }
})

const handleMenuSelect = (index) => {
  activeTab.value = index
}
</script>

<style scoped>
.settings-page {
  padding: var(--space-xl);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-2xl);
  text-align: center;
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-sm) 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
}

.title-icon {
  color: var(--primary-color);
}

.page-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  margin: 0;
}

.settings-content {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
}

.settings-menu {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-primary);
  height: 100%;
}

.settings-nav {
  border-right: none;
}

:deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  margin: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-base);
  color: var(--text-secondary);
}

:deep(.el-menu-item.is-active) {
  background-color: var(--primary-lighter);
  color: var(--primary-color);
  font-weight: 600;
}

:deep(.el-menu-item:hover) {
  background-color: var(--bg-secondary);
}

.settings-panel {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-xl);
  min-height: 500px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .settings-page {
    padding: var(--space-md);
  }

  .el-row {
    flex-direction: column;
  }

  .el-col {
    width: 100% !important;
    margin-bottom: var(--space-lg);
  }

  .settings-menu {
    margin-bottom: var(--space-lg);
  }
}
</style>
