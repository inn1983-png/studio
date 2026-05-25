import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const DEFAULT_BRAND = {
  appName: 'Txtovideo Studio',
  appDescription: '小说转短剧智能创作工作站',
  logoText: 'Txtovideo',
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
      const resp = await axios.get('/brand', { timeout: 3000 })
      brand.value = { ...DEFAULT_BRAND, ...resp.data }
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
