/**
 * Vue I18n プラグイン
 *
 * vue-i18nライブラリが未インストールの場合でも動作する
 * 軽量なi18nプラグイン実装。
 */
import { ref, type App, type Plugin } from 'vue'
import { messages, type Locale, defaultLocale } from './index'

const currentLocale = ref<Locale>(
  (localStorage.getItem('grc-locale') as Locale) || defaultLocale
)

export function useI18n() {
  function t(key: string): string {
    const keys = key.split('.')
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let result: any = messages[currentLocale.value]
    for (const k of keys) {
      if (result && typeof result === 'object' && k in result) {
        result = result[k]
      } else {
        return key
      }
    }
    return typeof result === 'string' ? result : key
  }

  function setLocale(locale: Locale) {
    currentLocale.value = locale
    localStorage.setItem('grc-locale', locale)
    document.documentElement.lang = locale
  }

  return {
    t,
    locale: currentLocale,
    setLocale,
    availableLocales: ['ja', 'en'] as Locale[],
  }
}

export const i18nPlugin: Plugin = {
  install(app: App) {
    const { t, locale, setLocale, availableLocales } = useI18n()

    // グローバルプロパティとして提供
    app.config.globalProperties.$t = t
    app.config.globalProperties.$locale = locale
    app.config.globalProperties.$setLocale = setLocale

    // provide/inject用
    app.provide('i18n', { t, locale, setLocale, availableLocales })
  }
}
