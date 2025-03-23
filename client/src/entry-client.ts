import './assets/main.css'
import { createApp } from './main'

const { app, router } = createApp()

if (import.meta.env.DEV) {
  app.mount('#app')
} else {
  router.isReady().then(() => {
    app.mount('#app')
  })
}
