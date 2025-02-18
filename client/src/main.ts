import { createSSRApp } from 'vue'
import App from '@/App.vue'
import newRouter from '@/router'
import { createPinia } from 'pinia'

// SSR requires a fresh app instance per request, therefore we export a function
// that creates a fresh app instance
export function createApp() {
  const app = createSSRApp(App)
  const router = newRouter()
  const pinia = createPinia()
  app.use(router)
  app.use(pinia)

  return { app, router, pinia }
}
