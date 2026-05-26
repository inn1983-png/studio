/**
 * 导出服务 - 处理章节导出相关功能
 */

import { post } from './api'

export const exportService = {
    async exportToJianYing(chapterId) {
        return await post(`/export/jianying/${chapterId}`)
    },

    async exportVideo(chapterId) {
        return await post(`/export/video/${chapterId}`)
    },

    async batchExportVideos(chapterIds) {
        return await post('/export/video/batch', { chapter_ids: chapterIds })
    },

    async downloadFile(downloadUrl, filename) {
        try {
            const { useAuthStore } = await import('@/stores/auth')
            const authStore = useAuthStore()
            const token = authStore.token
            const response = await fetch(downloadUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.status === 401) {
                authStore.logout()
                throw new Error('登录已过期，请重新登录')
            }

            if (!response.ok) {
                throw new Error(`下载失败: ${response.statusText}`)
            }

            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = filename
            link.style.display = 'none'
            document.body.appendChild(link)
            link.click()

            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)
        } catch (error) {
            console.error('文件下载失败:', error)
            throw error
        }
    }
}

export default exportService
