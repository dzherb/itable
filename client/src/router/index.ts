import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'
import { useNProgress } from '@vueuse/integrations/useNProgress'
import { useAuthStore } from '@/stores/auth.ts'
import { getAccessToken } from '@/api/authService.ts'

const loadedChunks = new Set<string>()

const lazyLoadWithTracking = (path: string, loader: () => Promise<unknown>) => {
  return () => {
    if (!loadedChunks.has(path)) {
      loadedChunks.add(path)
    }
    return loader()
  }
}

const newRouter = () => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  const router = createRouter({
    history: createHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '',
        name: 'home',
        redirect: { name: 'portfolios' },
        component: lazyLoadWithTracking(
          'home',
          () => import('@/components/layouts/BaseLayout.vue'),
        ),
        children: [
          {
            path: '/portfolios',
            name: 'portfolios',
            meta: {
              // transition: 'slide-left',
              requiresAuth: true,
            },
            component: lazyLoadWithTracking(
              'portfolios',
              () => import('@/pages/PortfoliosPage.vue'),
            ),
          },
          {
            path: '/portfolio',
            name: 'portfolio',
            meta: {
              requiresAuth: true,
              backTo: 'portfolios',
            },
            component: lazyLoadWithTracking('portfolio', () => import('@/pages/PortfolioPage.vue')),
          },
          {
            path: '/tables',
            name: 'tables',
            meta: {
              // transition: 'slide-right',
              requiresAuth: true,
            },
            component: lazyLoadWithTracking('tables', () => import('@/pages/TablesPage.vue')),
          },
        ],
      },
      {
        path: '/auth/login',
        name: 'login',
        component: lazyLoadWithTracking('login', () => import('@/pages/auth/LoginPage.vue')),
      },
    ],
  })

  const { start, done } = useNProgress()

  router.beforeEach(async (to, from, next) => {
    if (!to.hash && !loadedChunks.has(to.name as string) && !import.meta.env.SSR) {
      start()
    }

    if (!to.meta.requiresAuth || import.meta.env.SSR) {
      next()
      return
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

  router.afterEach((to, _) => {
    done()
  })

  return router
}

export default newRouter
