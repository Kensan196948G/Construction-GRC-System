import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Role constants matching backend GRCUser.Role
export const ROLES = {
  GRC_ADMIN: 'grc_admin',
  RISK_OWNER: 'risk_owner',
  COMPLIANCE_OFFICER: 'compliance_officer',
  AUDITOR: 'auditor',
  EXECUTIVE: 'executive',
  GENERAL: 'general',
} as const

export type UserRole = (typeof ROLES)[keyof typeof ROLES]

const ALL_ROLES: UserRole[] = Object.values(ROLES)

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
    meta: { requiresAuth: true, allowedRoles: ALL_ROLES },
  },
  {
    path: '/risks',
    name: 'Risks',
    component: () => import('@/views/Risks.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [
        ROLES.GRC_ADMIN, ROLES.RISK_OWNER, ROLES.AUDITOR,
        ROLES.EXECUTIVE, ROLES.GENERAL,
      ],
    },
  },
  {
    path: '/compliance',
    name: 'Compliance',
    component: () => import('@/views/Compliance.vue'),
    meta: { requiresAuth: true, allowedRoles: ALL_ROLES },
  },
  {
    path: '/controls',
    name: 'Controls',
    component: () => import('@/views/Controls.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [
        ROLES.GRC_ADMIN, ROLES.COMPLIANCE_OFFICER, ROLES.AUDITOR,
        ROLES.EXECUTIVE,
      ],
    },
  },
  {
    path: '/audits',
    name: 'Audits',
    component: () => import('@/views/Audits.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [
        ROLES.GRC_ADMIN, ROLES.AUDITOR, ROLES.EXECUTIVE,
      ],
    },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [
        ROLES.GRC_ADMIN, ROLES.RISK_OWNER, ROLES.COMPLIANCE_OFFICER,
        ROLES.AUDITOR, ROLES.EXECUTIVE,
      ],
    },
  },
  {
    path: '/activity-log',
    name: 'ActivityLog',
    component: () => import('@/views/ActivityLog.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [ROLES.GRC_ADMIN, ROLES.AUDITOR],
    },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: [
        ROLES.GRC_ADMIN, ROLES.RISK_OWNER, ROLES.COMPLIANCE_OFFICER,
        ROLES.AUDITOR, ROLES.GENERAL,
      ],
    },
  },
  {
    path: '/forbidden',
    name: 'Forbidden',
    component: () => import('@/views/Forbidden.vue'),
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
    return
  }

  const allowedRoles = to.meta.allowedRoles as UserRole[] | undefined
  if (allowedRoles && authStore.user) {
    const userRole = authStore.user.role as UserRole
    if (!allowedRoles.includes(userRole)) {
      next('/forbidden')
      return
    }
  }

  next()
})

export default router
