import { get } from './api'

export const txtovideoPromptsService = {
  async listTemplates() {
    return await get('/txtovideo/prompts/templates')
  },

  async getTemplate(templateId) {
    return await get(`/txtovideo/prompts/templates/${templateId}`)
  }
}

export default txtovideoPromptsService

