import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'
import router from './router'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1565C0',
          secondary: '#424242',
          accent: '#FF6F00',
          error: '#D32F2F',
          warning: '#FFA000',
          info: '#0288D1',
          success: '#388E3C',
          background: '#FAFAFA',
          surface: '#FFFFFF',
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#42A5F5',
          secondary: '#B0BEC5',
          accent: '#FFB74D',
          error: '#EF5350',
          warning: '#FFB300',
          info: '#29B6F6',
          success: '#66BB6A',
          background: '#121212',
          surface: '#1E1E1E',
        },
      },
    },
  },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
