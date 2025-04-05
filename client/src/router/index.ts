import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'
import { useNProgress } from '@vueuse/integrations/useNProgress'

const newRouter = () => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  const router = createRouter({
    history: createHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '',
        redirect: { name: 'portfolios' },
        component: () => import('@/components/layouts/BaseLayout.vue'),
        children: [
          {
            path: '/portfolios',
            name: 'portfolios',
            meta: {
              transition: 'slide-left'
            },
            component: () => import('@/pages/PortfoliosPage.vue'),
          },
          {
            path: '/tables',
            name: 'tables',
            meta: {
              transition: 'slide-right'
            },
            component: () => import('@/pages/TablesPage.vue'),
          },
        ],
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
