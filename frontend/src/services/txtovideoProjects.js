import { get, post, put, patch, del } from '@/services/api'

const BASE = '/txtovideo/projects'

export const txtovideoProjectsService = {
  listProjects(skip = 0, limit = 20) {
    return get(`${BASE}?skip=${skip}&limit=${limit}`)
  },

  getProject(projectId) {
    return get(`${BASE}/${projectId}`)
  },

  createProject(data) {
    return post(BASE, data)
  },

  updateProject(projectId, data) {
    return patch(`${BASE}/${projectId}`, data)
  },

  deleteProject(projectId) {
    return del(`${BASE}/${projectId}`)
  },

  saveDraft(projectId, draftData) {
    return put(`${BASE}/${projectId}/draft`, draftData)
  },

  getDraft(projectId) {
    return get(`${BASE}/${projectId}/draft`)
  }
}
