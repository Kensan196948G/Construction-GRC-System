import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

interface User {
  id: number
  username: string
  email: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshTokenValue = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const response = await apiClient.post('/api/v1/auth/token/', {
      username,
      password,
    })
    token.value = response.data.access
    refreshTokenValue.value = response.data.refresh
    user.value = response.data.user
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
  }

  function logout() {
    token.value = null
    refreshTokenValue.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function refreshToken() {
    try {
      const response = await apiClient.post('/api/v1/auth/token/refresh/', {
        refresh: refreshTokenValue.value,
      })
      token.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
    } catch {
      logout()
    }
  }

  async function fetchUser() {
    try {
      const response = await apiClient.get('/api/v1/auth/profile/')
      user.value = response.data
    } catch {
      logout()
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    refreshToken,
    fetchUser,
  }
})
