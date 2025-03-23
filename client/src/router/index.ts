import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'
import { useNProgress } from '@vueuse/integrations/useNProgress'

const newRouter = () => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  const router = createRouter({
    history: createHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue'),
      },
      {
        path: '/about',
        name: 'about',
        component: () => import('../views/AboutView.vue'),
      },
    ],
  })

  const { start, done } = useNProgress()

  router.beforeEach((to, from, next) => {
    if (!to.hash && typeof document !== 'undefined') {
      start()
    }
    next()
  })

  router.afterEach((to, from) => {
    if (!to.hash && typeof document !== 'undefined') {
      done()
    }
  })

  return router
}

export default newRouter
