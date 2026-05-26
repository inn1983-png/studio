import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { get } from '@/services/api'

const DEFAULT_BRAND = {
  appName: 'Txtovideo Studio',
  appDescription: '小说短剧工作站',
  logoText: 'Txtovideo Studio',
  copyright: '© 2024-2026 Txtovideo Studio. All rights reserved.'
}

export const useBrandStore = defineStore('brand', () => {
  const brand = ref({ ...DEFAULT_BRAND })
  const loaded = ref(false)

  const appName = computed(() => brand.value.appName)
  const appDescription = computed(() => brand.value.appDescription)
  const logoText = computed(() => brand.value.logoText)
  const copyright = computed(() => brand.value.copyright)
  const pageTitleSuffix = computed(() => appDescription.value)

  const fetchBrand = async () => {
    if (loaded.value) return brand.value
    try {
      const resp = await get('/brand', { timeout: 3000 })
      brand.value = { ...DEFAULT_BRAND, ...resp }
      loaded.value = true
    } catch {
      brand.value = { ...DEFAULT_BRAND }
      loaded.value = true
    }
    return brand.value
  }

  return {
    brand,
    loaded,
    appName,
    appDescription,
    logoText,
    copyright,
    pageTitleSuffix,
    fetchBrand
  }
})
