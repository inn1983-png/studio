import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  base: '/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    strictPort: true,
    host: '0.0.0.0',
    hmr: {
      overlay: true
    },
    watch: {
      usePolling: false,
      interval: 100
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: process.env.NODE_ENV !== 'production',
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('element-plus')) {
              if (id.includes('@element-plus/icons-vue')) {
                return 'element-icons'
              }
              if (id.includes('element-plus/es/components')) {
                const match = id.match(/element-plus\/es\/components\/([^/]+)/)
                if (match) {
                  const component = match[1]
                  const heavyComponents = ['table', 'virtual-list', 'tree', 'cascader', 'time-picker', 'date-picker']
                  if (heavyComponents.includes(component)) {
                    return `element-${component}`
                  }
                }
              }
              return 'element-core'
            }
            if (id.includes('konva') || id.includes('vue-konva')) {
              return 'konva'
            }
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vue-vendor'
            }
            if (id.includes('axios')) {
              return 'axios'
            }
            return 'vendor-other'
          }
        }
      }
    }
  }
})
