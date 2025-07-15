import { eventBus } from '@/events/bus.ts'
import type {Router} from "vue-router";

export const registerEvents = (router: Router) => {
  // Events that are not bound to any component

  eventBus.on('tokenRefreshFailed', async () => {
    await router.push({ name: 'login' })
  })
}
