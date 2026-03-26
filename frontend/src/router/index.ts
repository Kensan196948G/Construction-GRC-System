import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/risks',
    name: 'Risks',
    component: () => import('@/views/Risks.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/compliance',
    name: 'Compliance',
    component: () => import('@/views/Compliance.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/controls',
    name: 'Controls',
    component: () => import('@/views/Controls.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/audits',
    name: 'Audits',
    component: () => import('@/views/Audits.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
