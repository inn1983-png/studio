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
  },

  getWorkflowSteps(projectId) {
    return get(`${BASE}/${projectId}/steps`)
  },

  updateWorkflowStep(projectId, stepName, data) {
    return put(`${BASE}/${projectId}/steps/${stepName}`, data)
  },

  retryWorkflowStep(projectId, stepName) {
    return post(`${BASE}/${projectId}/steps/${stepName}/retry`)
  },

  markDownstreamStale(projectId, stepName) {
    return post(`${BASE}/${projectId}/steps/mark-stale`, { step_name: stepName })
  },

  getAudioTracks(projectId) {
    return get(`${BASE}/${projectId}/audio-tracks`)
  },

  addAudioTrack(projectId, data) {
    return post(`${BASE}/${projectId}/audio-tracks`, data)
  },

  deleteAudioTrack(projectId, trackId) {
    return del(`${BASE}/${projectId}/audio-tracks/${trackId}`)
  },

  generateCanvas(projectId) {
    return post(`${BASE}/${projectId}/generate-canvas`)
  },

  scoreProjectQuality(projectId) {
    return post(`${BASE}/${projectId}/quality-score`)
  },

  listProjectTemplates() {
    return get(`${BASE}/templates/list`)
  }
}
