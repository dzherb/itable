import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

const DEV_SERVER_URL = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'true'
  },
  server: {
    proxy: {
      '/admin': DEV_SERVER_URL,
      '/static': DEV_SERVER_URL,
      '/api': DEV_SERVER_URL,
    }
  },
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
  ],
  build: {
    emptyOutDir: true,
    outDir: './dist/client/',
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
