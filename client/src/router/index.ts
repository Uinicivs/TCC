import { createRouter, createWebHistory } from 'vue-router'

function isAuthenticated(): boolean {
  const accessToken = localStorage.getItem('access_token')
  const authToken = localStorage.getItem('auth_token')

  return !!(accessToken || authToken)
}

function requiresAuth() {
  return (to: any, from: any, next: any) => {
    if (isAuthenticated()) {
      next()
      return
    }
    next('/login')
  }
}

function isGuest() {
  return (to: any, from: any, next: any) => {
    if (isAuthenticated()) {
      next('/')
      return
    }
    next()
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '',
      component: () => import('@/views/home/index.vue'),
      beforeEnter: requiresAuth(),
    },
    {
      path: '/show/:id',
      name: 'flow-show',
      component: () => import('@/views/flows/show/index.vue'),
      beforeEnter: requiresAuth(),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/index.vue'),
      beforeEnter: isGuest(),
    },
  ],
})

export default router
