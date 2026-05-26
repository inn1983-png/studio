import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

export { useAuthStore } from './auth'
export { useProjectsStore } from './projects'
export { useBrandStore } from './brand'