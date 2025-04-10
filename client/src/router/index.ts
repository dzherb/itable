import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'
import { useNProgress } from '@vueuse/integrations/useNProgress'
import { useAuthStore } from '@/stores/auth.ts'
import { getAccessToken } from '@/api/authService.ts'

const newRouter = () => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  const router = createRouter({
    history: createHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '',
        name: 'home',
        redirect: { name: 'portfolios' },
        component: () => import('@/components/layouts/BaseLayout.vue'),
        children: [
          {
            path: '/portfolios',
            name: 'portfolios',
            meta: {
              transition: 'slide-left',
              requiresAuth: true,
            },
            component: () => import('@/pages/PortfoliosPage.vue'),
          },
          {
            path: '/tables',
            name: 'tables',
            meta: {
              transition: 'slide-right',
              requiresAuth: true,
            },
            component: () => import('@/pages/TablesPage.vue'),
          },
        ],
      },
      {
        path: '/auth/login',
        name: 'login',
        component: () => import('@/pages/auth/LoginPage.vue'),
      },
    ],
  })

  const { start, done } = useNProgress()

  router.beforeEach(async (to, from, next) => {
    if (!to.hash && !import.meta.env.SSR) {
      start()
    }

    if (!to.meta.requiresAuth || import.meta.env.SSR) {
      next()
    }

    const auth = useAuthStore()

    if (!auth.isAuthenticated && getAccessToken()) {
      try {
        await auth.fetchProfile()
      } catch {
        auth.logout()
      }
    }

    if (!auth.isAuthenticated) {
      next({ name: 'login' })
    } else {
      next()
    }
  })

  router.afterEach((to, from) => {
    if (!to.hash && !import.meta.env.SSR) {
      done()
    }
  })

  return router
}

export default newRouter
