import '@/assets/main.css'
import { createVueApp } from '@/main.ts'
import { registerEvents } from '@/events/events.ts'

const { app, router } = createVueApp()

router.isReady().then(() => {
  app.mount('#app')
  registerEvents(router)
})
