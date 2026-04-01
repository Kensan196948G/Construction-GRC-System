import { ref, watch } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'

export type ThemeMode = 'light' | 'dark' | 'system'

const themeMode = ref<ThemeMode>(
  (localStorage.getItem('grc-theme') as ThemeMode) || 'light'
)

export function useThemeToggle() {
  const vuetifyTheme = useVuetifyTheme()

  function applyTheme(mode: ThemeMode) {
    if (mode === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      vuetifyTheme.global.name.value = prefersDark ? 'dark' : 'light'
    } else {
      vuetifyTheme.global.name.value = mode
    }
  }

  function setTheme(mode: ThemeMode) {
    themeMode.value = mode
    localStorage.setItem('grc-theme', mode)
    applyTheme(mode)
  }

  function toggleTheme() {
    const next: ThemeMode = vuetifyTheme.global.current.value.dark ? 'light' : 'dark'
    setTheme(next)
  }

  // Initialize
  applyTheme(themeMode.value)

  // Watch system preference changes
  if (themeMode.value === 'system') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      applyTheme('system')
    })
  }

  return {
    themeMode,
    setTheme,
    toggleTheme,
    isDark: () => vuetifyTheme.global.current.value.dark,
  }
}
