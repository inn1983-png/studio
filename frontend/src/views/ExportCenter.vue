<template>
  <div class="export-center">
    <section class="page-header">
      <div>
        <h1>导出中心</h1>
        <p>小说短剧工作站</p>
      </div>
      <el-button
        type="primary"
        :icon="Folder"
        @click="router.push('/projects')"
      >
        选择项目
      </el-button>
    </section>

    <section class="export-grid">
      <div
        v-for="item in exportItems"
        :key="item.title"
        class="export-item"
      >
        <el-icon>
          <component :is="item.icon" />
        </el-icon>
        <div>
          <h2>{{ item.title }}</h2>
          <p>{{ item.status }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Document, Download, Folder, VideoCamera } from '@element-plus/icons-vue'

const router = useRouter()

const exportItems = [
  { title: '视频文件', status: '可从项目详情导出', icon: VideoCamera },
  { title: '剪映素材包', status: '可从导演引擎导出', icon: Download },
  { title: 'Txtovideo 素材包', status: 'Phase 4 接入', icon: Document }
]
</script>

<style scoped>
.export-center {
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

.export-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
}

.export-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-xl);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.export-item .el-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  background: var(--primary-lighter);
  color: var(--primary-color);
  font-size: 22px;
}

.export-item h2 {
  margin: 0 0 var(--space-xs);
  color: var(--text-primary);
  font-size: var(--text-base);
  font-weight: 700;
}

.export-item p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

@media (max-width: 768px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
    padding: var(--space-lg);
  }

  .export-grid {
    grid-template-columns: 1fr;
  }
}
</style>
