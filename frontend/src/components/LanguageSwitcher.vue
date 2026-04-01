<script setup lang="ts">
import { useI18n } from '@/i18n/plugin'
import type { Locale } from '@/i18n/index'

const { locale, setLocale } = useI18n()

const localeNames: Record<Locale, string> = {
  ja: '日本語',
  en: 'English',
}

function toggleLocale() {
  const next = locale.value === 'ja' ? 'en' : 'ja'
  setLocale(next)
}
</script>

<template>
  <v-btn icon variant="text" @click="toggleLocale" :title="localeNames[locale]">
    <v-icon>mdi-translate</v-icon>
  </v-btn>
</template>
