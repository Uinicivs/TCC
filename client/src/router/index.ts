import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '',
      component: () => import('@/views/home/index.vue'),
    },
    {
      path: '/show/:id',
      name: 'flow-show',
      component: () => import('@/views/flows/show/index.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/register/index.vue'),
    },
  ],
})

export default router
