<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch {
    errorMessage.value = 'ログインに失敗しました。ユーザー名とパスワードを確認してください。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="8" class="pa-4">
          <v-card-title class="text-center text-h5 mb-4">
            <v-icon size="32" color="primary" class="mr-2">mdi-shield-check</v-icon>
            建設業GRCシステム
          </v-card-title>
          <v-card-subtitle class="text-center mb-6">
            ガバナンス・リスク・コンプライアンス管理
          </v-card-subtitle>

          <v-card-text>
            <v-alert
              v-if="errorMessage"
              type="error"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="errorMessage = ''"
            >
              {{ errorMessage }}
            </v-alert>

            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="ユーザー名"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                class="mb-2"
                required
              />
              <v-text-field
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                label="パスワード"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                variant="outlined"
                class="mb-4"
                required
                @click:append-inner="showPassword = !showPassword"
              />
              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
              >
                ログイン
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
