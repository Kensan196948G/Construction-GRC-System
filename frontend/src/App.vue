<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '@/store/auth'
import { useThemeToggle } from '@/composables/useTheme'
import { ROLES, type UserRole } from '@/router'
import SkipLink from '@/components/SkipLink.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const drawer = ref(true)
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { toggleTheme, isDark } = useThemeToggle()
const { smAndDown } = useDisplay()

const isLoginPage = computed(() => route.path === '/login')

const ALL_ROLES: UserRole[] = Object.values(ROLES)

const allMenuItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/', roles: ALL_ROLES },
  { title: 'リスク管理', icon: 'mdi-alert-circle', to: '/risks', roles: [ROLES.GRC_ADMIN, ROLES.RISK_OWNER, ROLES.AUDITOR, ROLES.EXECUTIVE, ROLES.GENERAL] },
  { title: 'コンプライアンス', icon: 'mdi-check-circle', to: '/compliance', roles: ALL_ROLES },
  { title: '管理策(ISO27001)', icon: 'mdi-shield-check', to: '/controls', roles: [ROLES.GRC_ADMIN, ROLES.COMPLIANCE_OFFICER, ROLES.AUDITOR, ROLES.EXECUTIVE] },
  { title: '内部監査', icon: 'mdi-clipboard-text', to: '/audits', roles: [ROLES.GRC_ADMIN, ROLES.AUDITOR, ROLES.EXECUTIVE] },
  { title: 'レポート', icon: 'mdi-chart-bar', to: '/reports', roles: [ROLES.GRC_ADMIN, ROLES.RISK_OWNER, ROLES.COMPLIANCE_OFFICER, ROLES.AUDITOR, ROLES.EXECUTIVE] },
  { title: '変更履歴', icon: 'mdi-history', to: '/activity-log', roles: [ROLES.GRC_ADMIN, ROLES.AUDITOR] },
  { title: '設定', icon: 'mdi-cog', to: '/settings', roles: [ROLES.GRC_ADMIN, ROLES.RISK_OWNER, ROLES.COMPLIANCE_OFFICER, ROLES.AUDITOR, ROLES.GENERAL] },
]

const ROLE_LABELS: Record<string, string> = {
  [ROLES.GRC_ADMIN]: 'GRC管理者',
  [ROLES.RISK_OWNER]: 'リスクオーナー',
  [ROLES.COMPLIANCE_OFFICER]: 'コンプライアンス担当',
  [ROLES.AUDITOR]: '内部監査員',
  [ROLES.EXECUTIVE]: '経営層',
  [ROLES.GENERAL]: '一般部門担当',
}

const menuItems = computed(() => {
  const userRole = authStore.user?.role as UserRole | undefined
  if (!userRole) return allMenuItems
  return allMenuItems.filter(item => item.roles.includes(userRole))
})

const userRoleLabel = computed(() => {
  const role = authStore.user?.role
  return role ? ROLE_LABELS[role] ?? role : ''
})

const handleLogout = async () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <v-app>
    <SkipLink />
    <template v-if="!isLoginPage">
      <v-navigation-drawer v-model="drawer" :mobile-breakpoint="960" temporary app>
        <v-list-item
          title="建設業GRC"
          subtitle="ガバナンス・リスク・コンプライアンス"
          class="pa-4"
        />
        <v-divider />
        <v-list density="compact" nav>
          <v-list-item
            v-for="item in menuItems"
            :key="item.to"
            :prepend-icon="item.icon"
            :title="item.title"
            :to="item.to"
            color="primary"
          />
        </v-list>
      </v-navigation-drawer>

      <v-app-bar app color="primary" density="comfortable">
        <v-app-bar-nav-icon @click="drawer = !drawer" />
        <v-toolbar-title>建設業GRCシステム</v-toolbar-title>
        <v-spacer />
        <span v-if="authStore.user" class="mr-4 text-body-2">
          {{ authStore.user.username }}
          <v-chip v-if="userRoleLabel" size="x-small" variant="outlined" class="ml-1">
            {{ userRoleLabel }}
          </v-chip>
        </span>
        <LanguageSwitcher />
        <v-btn
          :icon="isDark() ? 'mdi-weather-night' : 'mdi-weather-sunny'"
          title="テーマ切替"
          @click="toggleTheme"
        />
        <v-btn icon="mdi-logout" @click="handleLogout" />
      </v-app-bar>
    </template>

    <v-main id="main-content">
      <router-view />
    </v-main>

    <v-bottom-navigation v-if="smAndDown && !isLoginPage" grow>
      <v-btn to="/" icon="mdi-view-dashboard" />
      <v-btn to="/risks" icon="mdi-alert" />
      <v-btn to="/compliance" icon="mdi-check-circle" />
      <v-btn to="/audits" icon="mdi-clipboard-check" />
      <v-btn to="/reports" icon="mdi-file-chart" />
    </v-bottom-navigation>
  </v-app>
</template>
