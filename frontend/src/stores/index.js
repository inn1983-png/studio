import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

export { useAuthStore } from './auth'
export { useProjectStore } from './projects'
export { useGenerationStore } from './generations'
export { useSettingsStore } from './settings'
export { useBrandStore } from './brand'