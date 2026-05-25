<template>
  <div class="dashboard">
    <!-- 页面欢迎信息 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon">
          <VideoPlay />
        </el-icon>
        控制台
      </h1>
      <p class="page-description">
        欢迎回来，{{ authStore.user?.display_name || authStore.user?.username }}！开始您的小说短剧创作
      </p>
    </div>

    <!-- 快速操作入口 -->
    <div class="quick-actions">
      <div class="section-header">
        <h2>快速操作</h2>
        <p>选择您需要的功能，快速开始创作</p>
      </div>
      <div class="action-grid">
        <div
          class="quick-action primary-action modern-gradient-1"
          @click="$router.push('/projects')"
        >
          <div class="action-icon-large">
            <el-icon size="32">
              <VideoPlay />
            </el-icon>
          </div>
          <div class="action-content">
            <h3>开始创作</h3>
            <p>小说转短剧制作</p>
          </div>
          <div class="action-badge">
            推荐
          </div>
          <div class="action-glow" />
        </div>

        <div
          class="quick-action modern-gradient-2"
          @click="$router.push('/txtovideo')"
        >
          <div class="action-icon">
            <el-icon size="24">
              <Film />
            </el-icon>
          </div>
          <div class="action-content">
            <h4>短剧工作台</h4>
            <p>剧本与分镜</p>
          </div>
          <div class="action-arrow">
            <el-icon size="16">
              <ArrowRight />
            </el-icon>
          </div>
        </div>

        <div
          class="quick-action modern-gradient-3"
          @click="$router.push('/exports')"
        >
          <div class="action-icon">
            <el-icon size="24">
              <Download />
            </el-icon>
          </div>
          <div class="action-content">
            <h4>导出中心</h4>
            <p>素材包导出</p>
          </div>
          <div class="action-arrow">
            <el-icon size="16">
              <ArrowRight />
            </el-icon>
          </div>
        </div>

        <div
          class="quick-action modern-gradient-4"
          @click="$router.push('/settings')"
        >
          <div class="action-icon">
            <el-icon size="24">
              <Setting />
            </el-icon>
          </div>
          <div class="action-content">
            <h4>系统设置</h4>
            <p>配置管理</p>
          </div>
          <div class="action-arrow">
            <el-icon size="16">
              <ArrowRight />
            </el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 左侧：统计和最近项目 -->
      <div class="left-column">
        <!-- 统计卡片 -->
        <div class="stats-row">
          <div class="mini-stat">
            <div class="mini-stat-icon projects">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="mini-stat-info">
              <div class="mini-stat-number">
                {{ projectCount }}
              </div>
              <div class="mini-stat-label">
                项目
              </div>
            </div>
          </div>

          <div class="mini-stat">
            <div class="mini-stat-icon tasks">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="mini-stat-info">
              <div class="mini-stat-number">
                {{ runningTasks }}
              </div>
              <div class="mini-stat-label">
                进行中
              </div>
            </div>
          </div>

          <div class="mini-stat">
            <div class="mini-stat-icon videos">
              <el-icon><Share /></el-icon>
            </div>
            <div class="mini-stat-info">
              <div class="mini-stat-number">
                {{ generatedVideos }}
              </div>
              <div class="mini-stat-label">
                已生成
              </div>
            </div>
          </div>

          <div class="mini-stat">
            <div class="mini-stat-icon cost">
              <el-icon><Money /></el-icon>
            </div>
            <div class="mini-stat-info">
              <el-tooltip
                content="基于已生成内容的成本估算,非实际扣费金额"
                placement="top"
              >
                <div class="mini-stat-number cost-estimate">
                  ≈¥{{ totalCost.toFixed(2) }}
                </div>
              </el-tooltip>
              <div class="mini-stat-label">
                成本估算
              </div>
            </div>
          </div>
        </div>

        <!-- 最近项目 -->
        <div class="recent-projects">
          <div class="section-header">
            <h3>最近项目</h3>
            <el-button
              link
              @click="$router.push('/projects')"
            >
              查看全部
            </el-button>
          </div>
          <div class="projects-list">
            <div
              v-if="loading"
              class="loading-skeleton"
            >
              <el-skeleton
                :rows="3"
                animated
              />
            </div>
            <div
              v-else-if="recentProjects.length === 0"
              class="empty-projects"
            >
              <el-icon size="32">
                <Document />
              </el-icon>
              <p>暂无项目</p>
              <el-button
                type="primary"
                plain
                @click="$router.push('/projects')"
              >
                创建第一个项目
              </el-button>
            </div>
            <div
              v-else
              class="project-items"
            >
              <div
                v-for="project in recentProjects"
                :key="project.id"
                class="project-item"
                @click="$router.push(`/projects/${project.id}`)"
              >
                <div class="project-info">
                  <h4>{{ project.title }}</h4>
                  <p>{{ project.chapter_count }} 章节 · {{ project.word_count }} 字</p>
                </div>
                <div class="project-meta">
                  <el-tag
                    :type="getStatusType(project.status)"
                    size="small"
                  >
                    {{ getStatusText(project.status) }}
                  </el-tag>
                  <span class="project-time">{{ formatTime(project.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：任务队列和活动 -->
      <div class="right-column">
        <!-- 任务队列 -->
        <div class="task-queue">
          <div class="section-header">
            <h3>
              <el-icon><Timer /></el-icon>
              生成队列
            </h3>
            <el-button
              link
              @click="$router.push('/txtovideo')"
            >
              管理
            </el-button>
          </div>
          <div class="queue-content">
            <div
              v-if="loading"
              class="loading-skeleton"
            >
              <el-skeleton
                :rows="2"
                animated
              />
            </div>
            <div
              v-else-if="!taskQueue || taskQueue.running_tasks === 0"
              class="empty-queue"
            >
              <el-icon size="32">
                <VideoCamera />
              </el-icon>
              <p>队列为空</p>
              <el-button
                type="primary"
                plain
                @click="$router.push('/projects')"
              >
                查看短剧项目
              </el-button>
            </div>
            <div
              v-else
              class="task-items"
            >
              <div
                v-for="task in taskQueue.tasks"
                :key="task.id"
                class="task-item"
              >
                <div class="task-info">
                  <el-icon><Timer /></el-icon>
                  <span>{{ task.title }}</span>
                </div>
                <div class="task-progress">
                  <el-progress
                    :percentage="task.progress"
                    :status="task.progress === 100 ? 'success' : undefined"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 最近活动 -->
        <div class="recent-activity">
          <div class="section-header">
            <h3>
              <el-icon><Clock /></el-icon>
              最近活动
            </h3>
          </div>
          <div class="activity-list">
            <div
              v-if="loading"
              class="loading-skeleton"
            >
              <el-skeleton
                :rows="3"
                animated
              />
            </div>
            <div
              v-else-if="recentActivities.length === 0"
              class="empty-activity"
            >
              <el-icon size="32">
                <Document />
              </el-icon>
              <p>暂无活动记录</p>
            </div>
            <div
              v-else
              class="activity-items"
            >
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-icon">
                  <el-icon :component="getActivityIcon(activity.type)" />
                </div>
                <div class="activity-content">
                  <p class="activity-desc">
                    {{ activity.description }}
                  </p>
                  <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Folder,
  Film,
  VideoPlay,
  Timer,
  Share,
  Setting,
  Download,
  Document,
  ArrowRight,
  Clock,
  VideoCamera,
  Money,
  Refresh
} from '@element-plus/icons-vue'
import { dashboardService } from '@/services/dashboard'

const authStore = useAuthStore()
const router = useRouter()

// 数据状态
const loading = ref(false)
const statistics = ref(null)
const recentProjects = ref([])
const recentActivities = ref([])
const taskQueue = ref(null)

// 计算属性 - 从统计数据中提取值
const projectCount = computed(() => statistics.value?.projects?.total || 0)
const runningTasks = computed(() => statistics.value?.tasks?.running_tasks || 0)
const generatedVideos = computed(() => statistics.value?.generation?.generated_videos || 0)
const totalCost = computed(() => statistics.value?.cost?.total || 0)

// 加载仪表盘数据
const loadDashboardData = async () => {
  loading.value = true
  try {
    // 并行加载所有数据
    const [stats, projects, activities, queue] = await Promise.all([
      dashboardService.getStatistics(),
      dashboardService.getRecentProjects(5),
      dashboardService.getRecentActivities(10),
      dashboardService.getTaskQueue()
    ])

    statistics.value = stats
    recentProjects.value = projects.projects || []
    recentActivities.value = activities.activities || []
    taskQueue.value = queue
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载仪表盘数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await loadDashboardData()
  ElMessage.success('数据已刷新')
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 获取活动类型图标
const getActivityIcon = (type) => {
  switch (type) {
    case 'project_created':
      return Folder
    case 'chapter_confirmed':
      return Document
    case 'video_generated':
      return VideoCamera
    default:
      return Document
  }
}

// 获取状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    uploaded: 'info',
    parsing: 'warning',
    parsed: 'success',
    generating: 'warning',
    completed: 'success',
    failed: 'danger',
    archived: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusTextMap = {
    uploaded: '已上传',
    parsing: '解析中',
    parsed: '已解析',
    generating: '生成中',
    completed: '已完成',
    failed: '失败',
    archived: '已归档'
  }
  return statusTextMap[status] || status
}

defineOptions({
  name: 'Dashboard'
})

// 向MainLayout提供header actions
import { provide } from 'vue'
provide('headerActions', [
  {
    text: '刷新',
    type: 'default',
    icon: Refresh,
    action: refreshData
  },
  {
    text: '项目管理',
    type: 'default',
    icon: Folder,
    action: () => router.push('/projects')
  },
  {
    text: '开始创作',
    type: 'primary',
    icon: VideoPlay,
    action: () => router.push('/txtovideo')
  }
])

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
/* 仪表盘容器 */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* 页面头部信息 */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  font-size: 20px;
  color: var(--primary-color);
  padding: 6px;
  background: rgba(32, 33, 36, 0.1);
  border-radius: var(--radius-md);
}

.page-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

/* 快速操作入口 */
.quick-actions {
  margin-bottom: var(--space-xl);
}

.quick-actions .section-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.quick-actions .section-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-sm) 0;
}

.quick-actions .section-header p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

.action-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: var(--space-lg);
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-xl) var(--space-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-primary);
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.quick-action:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

.quick-action:hover .action-arrow {
  transform: translateX(4px);
}

.primary-action {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  border: none;
  grid-row: span 2;
  box-shadow: var(--shadow-md);
}

.primary-action:hover {
  box-shadow: 0 12px 35px rgba(32, 33, 36, 0.4);
  transform: translateY(-6px);
}

.action-icon-large {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  margin-bottom: var(--space-lg);
  position: relative;
  z-index: 2;
  backdrop-filter: blur(10px);
}

.action-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  margin-bottom: var(--space-md);
  position: relative;
  z-index: 2;
  box-shadow: var(--shadow-sm);
}

.primary-action .action-icon {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.action-content h3 {
  font-size: var(--text-xl);
  font-weight: 700;
  margin: 0 0 var(--space-xs) 0;
  color: var(--text-primary);
  position: relative;
  z-index: 2;
}

.primary-action .action-content h3 {
  color: white;
}

.action-content h4 {
  font-size: var(--text-lg);
  font-weight: 600;
  margin: 0 0 var(--space-xs) 0;
  color: var(--text-primary);
  position: relative;
  z-index: 2;
}

.action-content p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  position: relative;
  z-index: 2;
}

.primary-action .action-content p {
  color: rgba(255, 255, 255, 0.9);
}

.action-badge {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  background: rgba(255, 255, 255, 0.25);
  color: white;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  backdrop-filter: blur(10px);
  z-index: 2;
}

.action-arrow {
  position: absolute;
  bottom: var(--space-md);
  right: var(--space-md);
  color: var(--primary-color);
  transition: all var(--transition-base);
  z-index: 2;
}

.action-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-base);
  z-index: 1;
}

.primary-action:hover .action-glow {
  opacity: 1;
}

/* 主要内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
}

/* 统计行 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}

.mini-stat {
  display: flex;
  align-items: center;
  padding: var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
}

.mini-stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: var(--space-md);
}

.mini-stat-icon.projects {
  background: var(--info-light);
  color: var(--info-dark);
}

.mini-stat-icon.tasks {
  background: var(--secondary-color); /* Grayish */
  color: white;
}

.mini-stat-icon.videos {
  background: var(--primary-light);
  color: white;
}

.mini-stat-icon.cost {
  background: var(--warning-light);
  color: var(--warning-dark);
}

.mini-stat-info {
  flex: 1;
}

.mini-stat-number {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.mini-stat-number.cost-estimate {
  cursor: help;
}

.mini-stat-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

/* 区块样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.recent-projects,
.task-queue,
.recent-activity {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}

/* 空状态样式 */
.empty-projects,
.empty-queue,
.empty-activity {
  text-align: center;
  padding: var(--space-2xl) var(--space-lg);
  color: var(--text-secondary);
}

.empty-projects .el-icon,
.empty-queue .el-icon,
.empty-activity .el-icon {
  color: var(--text-tertiary);
  opacity: 0.6;
  margin-bottom: var(--space-md);
}

.empty-projects p,
.empty-queue p,
.empty-activity p {
  margin: 0 0 var(--space-md) 0;
  font-size: var(--text-base);
}

/* 加载骨架屏 */
.loading-skeleton {
  padding: var(--space-lg);
}

/* 项目列表项 */
.project-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.project-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.project-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  transform: translateX(4px);
}

.project-info h4 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-xs) 0;
}

.project-info p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.project-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-xs);
}

.project-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* 任务列表项 */
.task-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.task-item {
  padding: var(--space-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.task-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.task-progress {
  width: 100%;
}

/* 活动列表项 */
.activity-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  transition: all var(--transition-base);
}

.activity-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-light);
  color: var(--primary-color);
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-desc {
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin: 0 0 var(--space-xs) 0;
}

.activity-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .action-grid {
    grid-template-columns: 1fr 1fr 1fr 1fr;
  }

  .primary-action {
    grid-row: span 1;
  }
}

@media (max-width: 968px) {
  .action-grid {
    grid-template-columns: 1fr 1fr;
  }

  .main-content {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    gap: 2px;
  }

  .page-title {
    font-size: var(--text-lg);
  }

  .title-icon {
    font-size: 16px;
    padding: 4px;
  }

  .page-description {
    font-size: var(--text-xs);
  }

  .action-grid {
    grid-template-columns: 1fr;
    gap: var(--space-md);
  }

  .quick-action {
    padding: var(--space-lg) var(--space-md);
  }

  .action-icon-large {
    width: 48px;
    height: 48px;
  }

  .action-icon {
    width: 40px;
    height: 40px;
  }

  .action-content h3 {
    font-size: var(--text-base);
  }

  .action-content h4 {
    font-size: var(--text-sm);
  }

  .action-content p {
    font-size: var(--text-xs);
  }

  .stats-row {
    grid-template-columns: 1fr;
    gap: var(--space-sm);
  }

  .mini-stat {
    padding: var(--space-sm);
  }

  .mini-stat-icon {
    width: 32px;
    height: 32px;
  }

  .mini-stat-number {
    font-size: var(--text-lg);
  }

  .section-header h3 {
    font-size: var(--text-base);
  }

  .recent-projects,
  .task-queue,
  .recent-activity {
    padding: var(--space-md);
    margin-bottom: var(--space-md);
  }

  .empty-projects,
  .empty-queue,
  .empty-activity {
    padding: var(--space-lg) var(--space-md);
  }
}

@media (max-width: 480px) {
  .action-grid {
    grid-template-columns: 1fr;
  }

  .quick-action {
    padding: var(--space-md);
  }

  .action-icon-large,
  .action-icon {
    width: 36px;
    height: 36px;
  }

  .stats-row {
    margin-bottom: var(--space-lg);
  }

  .recent-projects,
  .task-queue,
  .recent-activity {
    padding: var(--space-sm);
  }
}
</style>
