<template>
  <div class="workbench-page">
    <section class="page-header">
      <div>
        <h1>短剧工作台</h1>
        <p>小说短剧工作站</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Folder"
          @click="router.push('/projects')"
        >
          选择项目
        </el-button>
      </div>
    </section>

    <section class="workflow-band">
      <el-steps
        :active="0"
        finish-status="success"
        align-center
      >
        <el-step title="原文" />
        <el-step title="剧本" />
        <el-step title="角色" />
        <el-step title="场景" />
        <el-step title="分镜" />
        <el-step title="提示词" />
        <el-step title="导出" />
      </el-steps>
    </section>

    <section class="entry-grid">
      <button
        class="entry-item primary"
        type="button"
        @click="router.push('/projects')"
      >
        <el-icon><VideoCamera /></el-icon>
        <span>进入项目管理</span>
      </button>
      <button
        class="entry-item"
        type="button"
        @click="router.push('/canvas')"
      >
        <el-icon><Share /></el-icon>
        <span>打开画布工作台</span>
      </button>
      <button
        class="entry-item"
        type="button"
        @click="router.push('/exports')"
      >
        <el-icon><Download /></el-icon>
        <span>查看导出中心</span>
      </button>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Download, Folder, Share, VideoCamera } from '@element-plus/icons-vue'

const router = useRouter()
</script>

<style scoped>
.workbench-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-lg);
  padding: var(--space-xl);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.page-header h1 {
  margin: 0 0 var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-2xl);
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

.workflow-band {
  padding: var(--space-xl);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
}

.entry-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  min-height: 88px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--text-base);
  font-weight: 600;
  transition: all var(--transition-base);
}

.entry-item:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.entry-item.primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #fff;
}

.entry-item.primary:hover {
  color: #fff;
  background: var(--primary-hover);
}

@media (max-width: 768px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
    padding: var(--space-lg);
  }

  .entry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
