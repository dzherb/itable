import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'

const newRouter = () => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  return createRouter({
    history: createHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue'),
      },
    ],
  })
}

export default newRouter
