<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <v-icon size="120" color="error" class="mb-4">mdi-shield-lock</v-icon>
        <h1 class="text-h3 font-weight-bold mb-4">403</h1>
        <p class="text-h6 mb-2">アクセス権限がありません</p>
        <p class="text-body-1 text-medium-emphasis mb-8">
          このページを表示する権限がありません。管理者にお問い合わせください。
        </p>
        <v-btn color="primary" size="large" @click="router.push('/')">
          <v-icon start>mdi-home</v-icon>
          ダッシュボードに戻る
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>
