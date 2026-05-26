<template>
  <aside
    class="app-sidebar"
    :class="{ collapsed }"
  >
    <!-- Logo区域 -->
    <div class="sidebar-header">
      <div class="logo-container">
        <div class="logo">
          <el-icon class="logo-icon">
            <VideoCamera />
          </el-icon>
          <span
            v-show="!collapsed"
            class="logo-text"
          >{{ brandStore.logoText }}</span>
        </div>
        <button
          v-show="!collapsed"
          class="toggle-btn"
          @click="$emit('toggle')"
        >
          <el-icon><Fold /></el-icon>
        </button>
      </div>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <el-scrollbar class="nav-scrollbar">
        <ul class="nav-list">
          <li
            v-for="item in primaryMenuItems"
            :key="item.path"
            class="nav-item"
          >
            <router-link
              :to="item.path"
              class="nav-link"
              :class="{ active: isActive(item.path) }"
            >
              <el-icon class="nav-icon">
                <component :is="item.icon" />
              </el-icon>
              <span
                v-show="!collapsed"
                class="nav-text"
              >{{ item.title }}</span>
              <span
                v-if="item.badge && !collapsed"
                class="nav-badge"
              >{{ item.badge }}</span>
            </router-link>
          </li>
        </ul>
        <div
          v-show="!collapsed"
          class="experimental-section"
        >
          <button
            class="experimental-toggle"
            type="button"
            @click="experimentalOpen = !experimentalOpen"
          >
            <el-icon class="nav-icon">
              <Operation />
            </el-icon>
            <span class="nav-text">实验功能</span>
            <el-icon
              class="toggle-icon"
              :class="{ open: experimentalOpen }"
            >
              <ArrowDown />
            </el-icon>
          </button>
          <ul
            v-show="experimentalOpen"
            class="nav-list experimental-list"
          >
            <li
              v-for="item in experimentalMenuItems"
              :key="item.path"
              class="nav-item"
            >
              <router-link
                :to="item.path"
                class="nav-link experimental-link"
                :class="{ active: isActive(item.path) }"
              >
                <el-icon class="nav-icon">
                  <component :is="item.icon" />
                </el-icon>
                <span class="nav-text">{{ item.title }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </el-scrollbar>
    </nav>

    <!-- 折叠按钮 -->
    <div
      v-show="collapsed"
      class="collapsed-toggle"
    >
      <button
        class="toggle-btn"
        @click="$emit('toggle')"
      >
        <el-icon><Expand /></el-icon>
      </button>
    </div>

    <!-- 用户信息（展开状态） -->
    <div
      v-show="!collapsed"
      class="sidebar-footer"
    >
      <div class="user-card">
        <el-avatar
          :size="40"
          :src="user?.avatar_url"
        >
          <el-icon><User /></el-icon>
        </el-avatar>
        <div class="user-info">
          <div class="user-name">
            {{ user?.display_name || user?.username }}
          </div>
          <div class="user-role">
            {{ user?.role || '用户' }}
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBrandStore } from '@/stores/brand'
import {
  VideoCamera,
  Fold,
  Expand,
  User,
  House,
  Folder,
  Document,
  Promotion,
  Setting,
  Key,
  Headset,
  Share,
  Download,
  Operation,
  ArrowDown
} from '@element-plus/icons-vue'

// Props
defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

// Emits
defineEmits(['toggle'])

const route = useRoute()
const authStore = useAuthStore()
const brandStore = useBrandStore()
const experimentalOpen = ref(false)

// 计算属性
const user = computed(() => authStore.user)

// 菜单项配置
const primaryMenuItems = [
  {
    title: '项目管理',
    path: '/projects',
    icon: Folder,
    badge: null
  },
  {
    title: '短剧工作台',
    path: '/txtovideo',
    icon: VideoCamera,
    badge: null
  },
  {
    title: '画布工作台',
    path: '/canvas',
    icon: Share,
    badge: null
  },
  {
    title: 'API 密钥设置',
    path: '/api-keys',
    icon: Key,
    badge: null
  },
  {
    title: '导出中心',
    path: '/exports',
    icon: Download,
    badge: null
  },
  {
    title: '系统设置',
    path: '/settings',
    icon: Setting,
    badge: null
  }
]

const experimentalMenuItems = [
  {
    title: '控制台',
    path: '/dashboard',
    icon: House,
    badge: null
  },
  {
    title: '视频生成',
    path: '/generation',
    icon: Document,
    badge: null
  },
  {
    title: '背景音乐',
    path: '/bgm-management',
    icon: Headset,
    badge: null
  },
  {
    title: 'Bilibili 发布',
    path: '/publish',
    icon: Promotion,
    badge: null
  },
  {
    title: 'B站账号',
    path: '/bilibili-accounts',
    icon: User,
    badge: null
  }
]

// 检查当前路径是否激活
const isActive = (path) => {
  if (path === route.path) return true
  // 支持子路径激活，比如 /projects/:id 激活 /projects
  return route.path.startsWith(path + '/')
}
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  z-index: 200;
  transition: width var(--transition-base);
}

.app-sidebar.collapsed {
  width: 64px;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-primary);
  height: 72px;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  cursor: pointer;
  transition: all var(--transition-base);
}

.logo:hover {
  transform: scale(1.02);
}

.logo-icon {
  font-size: 28px;
  color: var(--primary-color);
  padding: var(--space-sm);
  background: rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-lg);
}

.logo-text {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
}

.toggle-btn:hover {
  background: rgba(99, 102, 241, 0.08);
  color: var(--primary-color);
}

/* 导航区域 */
.sidebar-nav {
  flex: 1;
  overflow: hidden;
}

.nav-scrollbar {
  height: 100%;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: var(--space-md) 0;
}

.nav-item {
  margin: var(--space-xs) var(--space-md);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-base);
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.nav-link:hover {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.08);
  transform: translateX(4px);
}

.nav-link.active {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.12);
}

.nav-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-color);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  font-size: 20px;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  background: var(--danger-color);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1;
}

.experimental-section {
  margin: var(--space-sm) var(--space-md) 0;
  padding-top: var(--space-sm);
  border-top: 1px solid var(--border-primary);
}

.experimental-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  width: 100%;
  padding: var(--space-md);
  border: none;
  border-radius: var(--radius-lg);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font: inherit;
  font-weight: 500;
  transition: all var(--transition-base);
}

.experimental-toggle:hover {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.08);
}

.toggle-icon {
  font-size: 14px;
  transition: transform var(--transition-base);
}

.toggle-icon.open {
  transform: rotate(180deg);
}

.experimental-list {
  padding: var(--space-xs) 0 0;
}

.experimental-link {
  font-size: var(--text-sm);
}

/* 折叠状态下的切换按钮 */
.collapsed-toggle {
  padding: var(--space-md);
  border-top: 1px solid var(--border-primary);
  display: flex;
  justify-content: center;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: var(--space-md);
  border-top: 1px solid var(--border-primary);
}

.user-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: rgba(99, 102, 241, 0.05);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.user-card:hover {
  background: rgba(99, 102, 241, 0.08);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--text-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin-top: 2px;
}

/* 折叠状态样式调整 */
.app-sidebar.collapsed .sidebar-header {
  padding: var(--space-md);
  justify-content: center;
}

.app-sidebar.collapsed .logo-container {
  justify-content: center;
}

.app-sidebar.collapsed .nav-item {
  margin: var(--space-xs) var(--space-sm);
}

.app-sidebar.collapsed .nav-link {
  padding: var(--space-md);
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-sidebar {
    transform: translateX(-100%);
  }

  .app-sidebar:not(.collapsed) {
    transform: translateX(0);
    box-shadow: var(--shadow-xl);
  }
}

/* 深色主题 */
@media (prefers-color-scheme: dark) {
  .app-sidebar {
    background: var(--bg-dark);
    border-right-color: var(--border-primary);
  }

  .sidebar-header,
  .sidebar-footer {
    border-color: var(--border-primary);
  }
}

/* 无障碍支持 */
.nav-link:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-color);
  position: relative;
  z-index: 10;
}

.nav-link:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
  border-radius: var(--radius-lg);
}

.toggle-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-color);
}

.toggle-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 动画 */
@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

.app-sidebar:not(.collapsed) {
  animation: slideIn 0.3s ease-out;
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .app-sidebar {
    border-width: 2px;
  }

  .nav-link.active::before {
    width: 4px;
  }
}
</style>
