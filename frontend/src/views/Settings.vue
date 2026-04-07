<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useThemeToggle, type ThemeMode } from '@/composables/useTheme'
import { useI18n } from '@/i18n/plugin'
import type { Locale } from '@/i18n/index'
import { useAuthStore } from '@/store/auth'
import apiClient from '@/api/client'
import { getUserProfile, setup2FA, verify2FA, disable2FA } from '@/api/auth'

// ── Composables ──
const { themeMode, setTheme, isDark } = useThemeToggle()
const { locale, setLocale } = useI18n()
const authStore = useAuthStore()

// ── Tab state ──
const activeTab = ref(0)

// ── A. テーマ設定 ──
const selectedTheme = ref<ThemeMode>(themeMode.value)

watch(selectedTheme, (mode) => {
  setTheme(mode)
})

const themeOptions = [
  { label: 'ライト', value: 'light' as ThemeMode, icon: 'mdi-weather-sunny' },
  { label: 'ダーク', value: 'dark' as ThemeMode, icon: 'mdi-weather-night' },
  { label: 'システム', value: 'system' as ThemeMode, icon: 'mdi-desktop-classic' },
]

// ── B. 言語設定 ──
const selectedLocale = ref<Locale>(locale.value)

watch(selectedLocale, (loc) => {
  setLocale(loc)
})

const localeOptions = [
  { label: '日本語', value: 'ja' as Locale },
  { label: 'English', value: 'en' as Locale },
]

// ── C. 通知設定 ──
interface NotificationSettings {
  emailNotification: boolean
  slackNotification: boolean
  criticalRiskAlert: boolean
  capDeadlineAlert: boolean
  dailyDigest: boolean
}

const NOTIFICATION_STORAGE_KEY = 'grc-notification-settings'

const defaultNotifications: NotificationSettings = {
  emailNotification: true,
  slackNotification: false,
  criticalRiskAlert: true,
  capDeadlineAlert: true,
  dailyDigest: false,
}

function loadNotificationSettings(): NotificationSettings {
  try {
    const stored = localStorage.getItem(NOTIFICATION_STORAGE_KEY)
    if (stored) return { ...defaultNotifications, ...JSON.parse(stored) }
  } catch {
    // ignore
  }
  return { ...defaultNotifications }
}

const notifications = reactive<NotificationSettings>(loadNotificationSettings())
const notificationSaved = ref(false)

function saveNotifications() {
  localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(notifications))
  notificationSaved.value = true
  setTimeout(() => { notificationSaved.value = false }, 2000)
}

const notificationItems = [
  { key: 'emailNotification' as keyof NotificationSettings, label: 'メール通知', icon: 'mdi-email-outline', desc: '重要な変更をメールで受信' },
  { key: 'slackNotification' as keyof NotificationSettings, label: 'Slack通知', icon: 'mdi-slack', desc: 'Slackチャンネルへ通知を送信' },
  { key: 'criticalRiskAlert' as keyof NotificationSettings, label: 'リスクCRITICALアラート', icon: 'mdi-alert-circle', desc: '重大リスク検出時に即座に通知' },
  { key: 'capDeadlineAlert' as keyof NotificationSettings, label: 'CAP期限アラート', icon: 'mdi-calendar-alert', desc: '是正措置の期限が近づいた時に通知' },
  { key: 'dailyDigest' as keyof NotificationSettings, label: '日次ダイジェスト', icon: 'mdi-newspaper', desc: '1日のサマリーを毎朝配信' },
]

// ── D. プロフィール編集 ──
const profile = reactive({
  displayName: '',
  department: '',
  phone: '',
})
const profileSaving = ref(false)
const profileSaved = ref(false)
const profileError = ref('')

const PROFILE_STORAGE_KEY = 'grc-user-profile'

onMounted(() => {
  // ユーザー情報があればプリフィル
  if (authStore.user) {
    profile.displayName = authStore.user.username || ''
  }
  // localStorageから復元
  try {
    const stored = localStorage.getItem(PROFILE_STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      profile.displayName = parsed.displayName || profile.displayName
      profile.department = parsed.department || ''
      profile.phone = parsed.phone || ''
    }
  } catch {
    // ignore
  }
  // 2FAステータスを取得
  fetchTwoFAStatus()
})

async function saveProfile() {
  profileSaving.value = true
  profileError.value = ''
  profileSaved.value = false

  try {
    // API呼び出しを試行
    await apiClient.patch('/api/v1/auth/me', {
      display_name: profile.displayName,
      department: profile.department,
      phone: profile.phone,
    })
    profileSaved.value = true
  } catch {
    // APIが未実装の場合はlocalStorageにフォールバック
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify({
      displayName: profile.displayName,
      department: profile.department,
      phone: profile.phone,
    }))
    profileSaved.value = true
  } finally {
    profileSaving.value = false
    setTimeout(() => { profileSaved.value = false }, 2000)
  }
}

// ── E. システム情報 ──
const systemInfo = {
  version: '1.0.0',
  buildDate: '2026-04-01',
  apiUrl: import.meta.env.VITE_API_BASE_URL || window.location.origin,
  frameworks: [
    { name: 'ISO 27001:2022', controls: '93管理策', icon: 'mdi-shield-check' },
    { name: 'NIST CSF 2.0', controls: '6機能 / 21カテゴリ', icon: 'mdi-security' },
    { name: '建設業法', controls: '建設業許可・施工管理', icon: 'mdi-domain' },
    { name: '品確法', controls: '品質確保促進', icon: 'mdi-check-decagram' },
    { name: '労安法', controls: '労働安全衛生', icon: 'mdi-hard-hat' },
  ],
}

// ── F. 2FA (TOTP) セキュリティ設定 ──
const twoFAEnabled = ref(false)
const twoFALoading = ref(false)
const twoFAError = ref('')
const twoFASuccessMsg = ref('')
const twoFASuccess = computed(() => twoFASuccessMsg.value !== '')

// セットアップダイアログ
const setupDialog = ref(false)
const setupQrCodeBase64 = ref('')
const setupSecret = ref('')
const setupTokenInput = ref('')
const setupVerifying = ref(false)
const setupError = ref('')

// 無効化ダイアログ
const disableDialog = ref(false)
const disableLoading = ref(false)
const disableError = ref('')

async function fetchTwoFAStatus(): Promise<void> {
  try {
    const profile = await getUserProfile()
    twoFAEnabled.value = profile.totp_enabled
  } catch {
    // プロフィール取得失敗時は無効状態として扱う
    twoFAEnabled.value = false
  }
}

async function openSetupDialog(): Promise<void> {
  twoFALoading.value = true
  twoFAError.value = ''
  setupError.value = ''
  setupTokenInput.value = ''
  try {
    const data = await setup2FA()
    setupQrCodeBase64.value = data.qr_code_base64
    setupSecret.value = data.secret
    setupDialog.value = true
  } catch {
    twoFAError.value = '2FA設定の初期化に失敗しました。再度お試しください。'
  } finally {
    twoFALoading.value = false
  }
}

async function confirmSetup(): Promise<void> {
  if (!setupTokenInput.value || setupTokenInput.value.length !== 6) {
    setupError.value = '6桁のコードを入力してください'
    return
  }
  setupVerifying.value = true
  setupError.value = ''
  try {
    await verify2FA(setupTokenInput.value)
    twoFAEnabled.value = true
    setupDialog.value = false
    twoFASuccessMsg.value = '2FAを有効化しました'
    setTimeout(() => { twoFASuccessMsg.value = '' }, 3000)
  } catch (err: unknown) {
    const axiosError = err as { response?: { data?: { error?: string } } }
    setupError.value = axiosError.response?.data?.error ?? '認証コードが正しくありません。再度お試しください。'
  } finally {
    setupVerifying.value = false
  }
}

async function confirmDisable(): Promise<void> {
  disableLoading.value = true
  disableError.value = ''
  try {
    await disable2FA()
    twoFAEnabled.value = false
    disableDialog.value = false
    twoFASuccessMsg.value = '2FAを無効化しました'
    setTimeout(() => { twoFASuccessMsg.value = '' }, 3000)
  } catch {
    disableError.value = '2FAの無効化に失敗しました。再度お試しください。'
  } finally {
    disableLoading.value = false
  }
}

// ── タブ定義 ──
const tabs = [
  { label: 'テーマ', icon: 'mdi-palette' },
  { label: '言語', icon: 'mdi-translate' },
  { label: '通知', icon: 'mdi-bell-outline' },
  { label: 'プロフィール', icon: 'mdi-account-circle' },
  { label: 'セキュリティ', icon: 'mdi-shield-lock-outline' },
  { label: 'システム情報', icon: 'mdi-information-outline' },
]
</script>

<template>
  <v-container fluid class="pa-4 pa-md-6">
    <!-- ヘッダー -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 font-weight-bold">
          <v-icon class="mr-2" size="32">mdi-cog</v-icon>
          設定
        </h1>
        <p class="text-body-2 text-medium-emphasis mt-1">
          システム設定・通知・プロフィールを管理します
        </p>
      </v-col>
    </v-row>

    <!-- タブ切り替え -->
    <v-card>
      <v-tabs v-model="activeTab" color="primary" show-arrows>
        <v-tab v-for="(tab, i) in tabs" :key="i" :value="i">
          <v-icon start>{{ tab.icon }}</v-icon>
          {{ tab.label }}
        </v-tab>
      </v-tabs>

      <v-divider />

      <v-tabs-window v-model="activeTab">
        <!-- A. テーマ設定 -->
        <v-tabs-window-item :value="0">
          <v-card-text class="pa-6">
            <h2 class="text-h6 mb-4">テーマ設定</h2>
            <p class="text-body-2 text-medium-emphasis mb-6">
              画面の表示テーマを選択してください。「システム」を選ぶとOSの設定に従います。
            </p>

            <v-radio-group v-model="selectedTheme" inline>
              <v-radio
                v-for="opt in themeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              >
                <template #label>
                  <v-icon class="mr-1" size="20">{{ opt.icon }}</v-icon>
                  {{ opt.label }}
                </template>
              </v-radio>
            </v-radio-group>

            <!-- プレビュー -->
            <v-card
              class="mt-6 pa-4"
              variant="outlined"
              max-width="400"
            >
              <div class="text-caption text-medium-emphasis mb-2">プレビュー</div>
              <v-chip
                :color="isDark() ? 'blue-grey-darken-3' : 'blue-lighten-4'"
                class="mr-2"
              >
                {{ isDark() ? 'ダークモード' : 'ライトモード' }}
              </v-chip>
              <span class="text-body-2">
                現在のテーマ: <strong>{{ selectedTheme }}</strong>
              </span>
            </v-card>
          </v-card-text>
        </v-tabs-window-item>

        <!-- B. 言語設定 -->
        <v-tabs-window-item :value="1">
          <v-card-text class="pa-6">
            <h2 class="text-h6 mb-4">言語設定</h2>
            <p class="text-body-2 text-medium-emphasis mb-6">
              表示言語を選択してください。
            </p>

            <v-radio-group v-model="selectedLocale">
              <v-radio
                v-for="opt in localeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </v-radio-group>

            <v-alert type="info" variant="tonal" class="mt-4" max-width="500">
              <template #text>
                現在の言語: <strong>{{ locale === 'ja' ? '日本語' : 'English' }}</strong>
              </template>
            </v-alert>
          </v-card-text>
        </v-tabs-window-item>

        <!-- C. 通知設定 -->
        <v-tabs-window-item :value="2">
          <v-card-text class="pa-6">
            <h2 class="text-h6 mb-4">通知設定</h2>
            <p class="text-body-2 text-medium-emphasis mb-6">
              受信する通知の種類を設定します。設定はブラウザに保存されます。
            </p>

            <v-list lines="two" max-width="600">
              <v-list-item
                v-for="item in notificationItems"
                :key="item.key"
              >
                <template #prepend>
                  <v-icon :icon="item.icon" class="mr-4" />
                </template>
                <v-list-item-title>{{ item.label }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.desc }}</v-list-item-subtitle>
                <template #append>
                  <v-switch
                    v-model="notifications[item.key]"
                    color="primary"
                    hide-details
                    density="compact"
                    inset
                  />
                </template>
              </v-list-item>
            </v-list>

            <v-btn
              color="primary"
              class="mt-6"
              prepend-icon="mdi-content-save"
              @click="saveNotifications"
            >
              通知設定を保存
            </v-btn>

            <v-snackbar
              v-model="notificationSaved"
              color="success"
              :timeout="2000"
              location="bottom"
            >
              通知設定を保存しました
            </v-snackbar>
          </v-card-text>
        </v-tabs-window-item>

        <!-- D. プロフィール編集 -->
        <v-tabs-window-item :value="3">
          <v-card-text class="pa-6">
            <h2 class="text-h6 mb-4">プロフィール編集</h2>
            <p class="text-body-2 text-medium-emphasis mb-6">
              表示名や連絡先を更新できます。
            </p>

            <v-form max-width="500" @submit.prevent="saveProfile">
              <v-text-field
                v-model="profile.displayName"
                label="表示名"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                density="comfortable"
                class="mb-3"
              />

              <v-text-field
                v-model="profile.department"
                label="部署"
                prepend-inner-icon="mdi-office-building"
                variant="outlined"
                density="comfortable"
                class="mb-3"
              />

              <v-text-field
                v-model="profile.phone"
                label="電話番号"
                prepend-inner-icon="mdi-phone"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                type="tel"
              />

              <v-text-field
                :model-value="authStore.user?.role || '一般ユーザー'"
                label="ロール"
                prepend-inner-icon="mdi-shield-account"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                readonly
                disabled
              />

              <v-alert
                v-if="profileError"
                type="error"
                variant="tonal"
                class="mb-4"
                closable
                @click:close="profileError = ''"
              >
                {{ profileError }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                :loading="profileSaving"
                prepend-icon="mdi-content-save"
              >
                プロフィールを保存
              </v-btn>
            </v-form>

            <v-snackbar
              v-model="profileSaved"
              color="success"
              :timeout="2000"
              location="bottom"
            >
              プロフィールを保存しました
            </v-snackbar>
          </v-card-text>
        </v-tabs-window-item>

        <!-- F. セキュリティ（2FA） -->
        <v-tabs-window-item :value="4">
          <v-card-text class="pa-6">
            <h2 class="text-h6 mb-2">セキュリティ設定</h2>
            <p class="text-body-2 text-medium-emphasis mb-6">
              二要素認証（2FA）を設定することでアカウントのセキュリティを強化できます。
            </p>

            <!-- 2FA カード -->
            <v-card variant="outlined" max-width="560" class="mb-4">
              <v-card-title class="d-flex align-center ga-2 pt-4 px-4">
                <v-icon color="primary">mdi-two-factor-authentication</v-icon>
                二要素認証（TOTP）
              </v-card-title>
              <v-card-text>
                <p class="text-body-2 text-medium-emphasis mb-4">
                  Google Authenticator や 1Password などの認証アプリと連携し、
                  ログイン時に6桁のワンタイムパスワードを要求します。
                </p>

                <div class="d-flex align-center ga-3 mb-2">
                  <v-chip
                    :color="twoFAEnabled ? 'success' : 'default'"
                    :prepend-icon="twoFAEnabled ? 'mdi-check-circle' : 'mdi-close-circle'"
                    variant="tonal"
                  >
                    {{ twoFAEnabled ? '有効' : '無効' }}
                  </v-chip>
                  <span class="text-body-2 text-medium-emphasis">
                    {{ twoFAEnabled ? '2FAは現在有効です' : '2FAは現在無効です' }}
                  </span>
                </div>

                <v-alert
                  v-if="twoFAError"
                  type="error"
                  variant="tonal"
                  class="mt-3"
                  closable
                  density="compact"
                  @click:close="twoFAError = ''"
                >
                  {{ twoFAError }}
                </v-alert>
              </v-card-text>
              <v-card-actions class="px-4 pb-4">
                <v-btn
                  v-if="!twoFAEnabled"
                  color="primary"
                  variant="elevated"
                  prepend-icon="mdi-qrcode"
                  :loading="twoFALoading"
                  @click="openSetupDialog"
                >
                  2FAを設定する
                </v-btn>
                <v-btn
                  v-else
                  color="error"
                  variant="outlined"
                  prepend-icon="mdi-shield-off-outline"
                  @click="disableDialog = true"
                >
                  2FAを無効にする
                </v-btn>
              </v-card-actions>
            </v-card>

            <!-- 成功スナックバー -->
            <v-snackbar
              v-model="twoFASuccess"
              color="success"
              :timeout="3000"
              location="bottom"
            >
              <v-icon start>mdi-check-circle</v-icon>
              {{ twoFASuccessMsg }}
            </v-snackbar>
          </v-card-text>
        </v-tabs-window-item>

        <!-- E. システム情報 -->
        <v-tabs-window-item :value="5">
          <v-card-text class="pa-6">
            <h2 class="text-h6 mb-4">システム情報</h2>

            <v-table density="comfortable" class="mb-6" max-width="500">
              <tbody>
                <tr>
                  <td class="font-weight-medium">バージョン</td>
                  <td>
                    <v-chip size="small" color="primary" variant="tonal">
                      v{{ systemInfo.version }}
                    </v-chip>
                  </td>
                </tr>
                <tr>
                  <td class="font-weight-medium">ビルド日時</td>
                  <td>{{ systemInfo.buildDate }}</td>
                </tr>
                <tr>
                  <td class="font-weight-medium">API URL</td>
                  <td>
                    <code>{{ systemInfo.apiUrl }}</code>
                  </td>
                </tr>
              </tbody>
            </v-table>

            <h3 class="text-subtitle-1 font-weight-bold mb-3">準拠規格・法令</h3>

            <v-list lines="two" max-width="500" density="compact">
              <v-list-item
                v-for="fw in systemInfo.frameworks"
                :key="fw.name"
              >
                <template #prepend>
                  <v-icon :icon="fw.icon" color="primary" class="mr-3" />
                </template>
                <v-list-item-title class="font-weight-medium">
                  {{ fw.name }}
                </v-list-item-title>
                <v-list-item-subtitle>{{ fw.controls }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card>

    <!-- 2FA セットアップダイアログ -->
    <v-dialog v-model="setupDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center ga-2 pt-5 px-6">
          <v-icon color="primary">mdi-qrcode-scan</v-icon>
          2FAセットアップ
        </v-card-title>
        <v-card-text class="px-6">
          <p class="text-body-2 text-medium-emphasis mb-4">
            以下のQRコードを Google Authenticator などの認証アプリで読み取ってください。
          </p>

          <div class="d-flex justify-center mb-4">
            <img
              v-if="setupQrCodeBase64"
              :src="`data:image/png;base64,${setupQrCodeBase64}`"
              alt="2FA QRコード"
              width="200"
              height="200"
              style="border: 1px solid #e0e0e0; border-radius: 8px;"
            />
            <v-icon v-else size="200" color="grey-lighten-2">mdi-qrcode</v-icon>
          </div>

          <v-expansion-panels variant="accordion" class="mb-4">
            <v-expansion-panel title="手動でシークレットキーを入力する場合">
              <v-expansion-panel-text>
                <code class="text-body-2" style="word-break: break-all;">{{ setupSecret }}</code>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <v-text-field
            v-model="setupTokenInput"
            label="認証アプリの6桁コード"
            prepend-inner-icon="mdi-lock-outline"
            variant="outlined"
            density="comfortable"
            maxlength="6"
            inputmode="numeric"
            pattern="[0-9]*"
            :error-messages="setupError"
            @keyup.enter="confirmSetup"
          />
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-spacer />
          <v-btn
            variant="text"
            @click="setupDialog = false"
          >
            キャンセル
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="setupVerifying"
            @click="confirmSetup"
          >
            確認して有効化
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 2FA 無効化確認ダイアログ -->
    <v-dialog v-model="disableDialog" max-width="420">
      <v-card>
        <v-card-title class="d-flex align-center ga-2 pt-5 px-6">
          <v-icon color="error">mdi-shield-off-outline</v-icon>
          2FAを無効にしますか？
        </v-card-title>
        <v-card-text class="px-6">
          <p class="text-body-2 text-medium-emphasis">
            二要素認証を無効にするとアカウントのセキュリティが低下します。
            本当に無効化しますか？
          </p>
          <v-alert
            v-if="disableError"
            type="error"
            variant="tonal"
            class="mt-3"
            density="compact"
            closable
            @click:close="disableError = ''"
          >
            {{ disableError }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="px-6 pb-5">
          <v-spacer />
          <v-btn
            variant="text"
            @click="disableDialog = false"
          >
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="disableLoading"
            @click="confirmDisable"
          >
            無効にする
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
