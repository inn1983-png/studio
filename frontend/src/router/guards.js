import { useAuthStore } from '@/stores/auth'
import { useBrandStore } from '@/stores/brand'

export function setupAuthGuard(router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    const brandStore = useBrandStore()

    if (!brandStore.loaded) {
      await brandStore.fetchBrand()
    }

    // 如果用户已登录但还没有获取用户信息，先获取
    if (authStore.isAuthenticated && !authStore.user) {
      try {
        await authStore.getCurrentUser()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        authStore.logout()
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }

    // 检查是否需要认证
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // 检查是否需要游客状态（已登录用户不能访问登录/注册页面）
    if (to.meta.requiresGuest && authStore.isAuthenticated) {
      next({ name: 'ProjectsPage' })
      return
    }

    // 检查邮箱验证
    if (to.meta.requiresVerified && authStore.user && !authStore.user.is_verified) {
      next({ name: 'SettingsPage' })
      return
    }

    next()
  })

  // 全局后置钩子
  router.afterEach((to) => {
    const brandStore = useBrandStore()
    document.title = `${to.meta.title || brandStore.appName} - ${brandStore.appDescription}`
  })
}

// 权限检查函数
export function hasPermission(user, permission) {
  if (!user) return false

  // 这里可以根据实际的权限系统进行扩展
  switch (permission) {
    case 'admin':
      return user.is_admin || false
    case 'verified':
      return user.is_verified || false
    case 'active':
      return user.is_active || false
    default:
      return true
  }
}

// 角色检查函数
export function hasRole(user, role) {
  if (!user) return false

  // 这里可以根据实际的角色系统进行扩展
  return user.role === role
}
