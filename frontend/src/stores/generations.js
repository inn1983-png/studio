import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get, post, del } from '@/services/api'

export const useGenerationStore = defineStore('generations', () => {
  const tasks = ref([])
  const currentTask = ref(null)
  const queue = ref([])
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  })

  // 获取任务列表
  const fetchTasks = async (params = {}) => {
    loading.value = true
    try {
      const response = await get('/generation/tasks', { params })
      tasks.value = response.items
      pagination.value = response.pagination
      return response
    } finally {
      loading.value = false
    }
  }

  // 获取任务详情
  const fetchTask = async (id) => {
    loading.value = true
    try {
      const task = await get(`/generation/tasks/${id}`)
      currentTask.value = task
      return task
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData) => {
    const task = await post('/generation/tasks', taskData)
    tasks.value.unshift(task)
    return task
  }

  const startTask = async (id) => {
    const task = await post(`/generation/tasks/${id}/start`)
    updateTaskInList(task)
    return task
  }

  const pauseTask = async (id) => {
    const task = await post(`/generation/tasks/${id}/pause`)
    updateTaskInList(task)
    return task
  }

  const resumeTask = async (id) => {
    const task = await post(`/generation/tasks/${id}/resume`)
    updateTaskInList(task)
    return task
  }

  const cancelTask = async (id) => {
    const task = await post(`/generation/tasks/${id}/cancel`)
    updateTaskInList(task)
    return task
  }

  const deleteTask = async (id) => {
    await del(`/generation/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
    if (currentTask.value?.id === id) {
      currentTask.value = null
    }
  }

  const fetchQueue = async () => {
    const queue_data = await get('/generation/queue')
    queue.value = queue_data
    return queue_data
  }

  // 更新列表中的任务
  const updateTaskInList = (task) => {
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index !== -1) {
      tasks.value[index] = task
    }
    if (currentTask.value?.id === task.id) {
      currentTask.value = task
    }
  }

  return {
    tasks,
    currentTask,
    queue,
    loading,
    pagination,
    fetchTasks,
    fetchTask,
    createTask,
    startTask,
    pauseTask,
    resumeTask,
    cancelTask,
    deleteTask,
    fetchQueue
  }
})