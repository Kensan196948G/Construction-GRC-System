<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useThemeToggle } from '@/composables/useTheme'
import SkipLink from '@/components/SkipLink.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const drawer = ref(true)
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { toggleTheme, isDark } = useThemeToggle()

const isLoginPage = computed(() => route.path === '/login')

const menuItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/' },
  { title: 'リスク管理', icon: 'mdi-alert-circle', to: '/risks' },
  { title: 'コンプライアンス', icon: 'mdi-check-circle', to: '/compliance' },
  { title: '管理策(ISO27001)', icon: 'mdi-shield-check', to: '/controls' },
  { title: '内部監査', icon: 'mdi-clipboard-text', to: '/audits' },
  { title: 'レポート', icon: 'mdi-chart-bar', to: '/reports' },
  { title: '設定', icon: 'mdi-cog', to: '/settings' },
]

const handleLogout = async () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <v-app>
    <SkipLink />
    <template v-if="!isLoginPage">
      <v-navigation-drawer v-model="drawer" app>
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
        </span>
        <LanguageSwitcher />
        <v-btn
          :icon="isDark() ? 'mdi-weather-night' : 'mdi-weather-sunny'"
          @click="toggleTheme"
          title="テーマ切替"
        />
        <v-btn icon="mdi-logout" @click="handleLogout" />
      </v-app-bar>
    </template>

    <v-main id="main-content">
      <router-view />
    </v-main>
  </v-app>
</template>
