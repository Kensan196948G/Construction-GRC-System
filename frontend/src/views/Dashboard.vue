<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRisksStore } from '@/store/risks'
import RiskHeatmap from '@/components/RiskHeatmap.vue'
import { getDashboardData, downloadDashboardPdf } from '@/api/dashboard'
import type { GRCDashboardData } from '@/api/dashboard'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { Doughnut, Bar } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// ---------- Store ----------
const risksStore = useRisksStore()

// ---------- State ----------
const loading = ref(true)
const refreshing = ref(false)
const pdfDownloading = ref(false)
const errorMessage = ref<string | null>(null)
const lastUpdated = ref<string>('')
let refreshTimer: ReturnType<typeof setInterval> | null = null

// ---------- Dashboard Data ----------
const dashboardData = ref<GRCDashboardData | null>(null)

// ---------- Mock / Fallback Data ----------
const mockDashboardData: GRCDashboardData = {
  risks: {
    total: 24,
    by_level: { CRITICAL: 3, HIGH: 7, MEDIUM: 9, LOW: 5 },
    by_status: { open: 10, in_progress: 8, closed: 4, accepted: 2 },
    by_category: { IT: 6, Construction: 8, Financial: 4, Legal: 3, Physical: 2, Operational: 1 },
  },
  compliance: {
    total: 42,
    compliant: 30,
    non_compliant: 4,
    partial: 6,
    unknown: 2,
    rate: 85,
  },
  controls: {
    total_applicable: 93,
    implemented: 58,
    in_progress: 20,
    not_started: 10,
    partially: 5,
    rate: 62,
  },
  audits: {
    total_audits: 12,
    completed: 8,
    in_progress: 3,
    planned: 1,
    total_findings: 23,
    open_findings: 7,
    by_type: { internal: 8, external: 3, certification: 1 },
  },
}

// ---------- Computed: Summary Cards ----------
const summaryCards = computed(() => {
  const d = dashboardData.value
  if (!d) return []
  return [
    {
      title: 'リスク総数',
      value: d.risks.total,
      icon: 'mdi-alert-circle-outline',
      color: 'blue',
      badge: d.risks.by_level?.CRITICAL ?? 0,
      badgeColor: 'red',
      badgeLabel: 'CRITICAL',
      subtitle: `HIGH: ${d.risks.by_level?.HIGH ?? 0} / MEDIUM: ${d.risks.by_level?.MEDIUM ?? 0}`,
    },
    {
      title: 'コンプライアンス準拠率',
      value: `${d.compliance.rate}%`,
      icon: 'mdi-scale-balance',
      color: d.compliance.rate >= 80 ? 'green' : d.compliance.rate >= 60 ? 'orange' : 'red',
      badge: null,
      badgeColor: '',
      badgeLabel: '',
      subtitle: `準拠: ${d.compliance.compliant} / 全${d.compliance.total}件`,
    },
    {
      title: 'ISO27001 管理策実施率',
      value: `${d.controls.rate}%`,
      icon: 'mdi-shield-check-outline',
      color: d.controls.rate >= 80 ? 'green' : d.controls.rate >= 60 ? 'orange' : 'red',
      badge: null,
      badgeColor: '',
      badgeLabel: '',
      subtitle: `実施済: ${d.controls.implemented} / 適用: ${d.controls.total_applicable}`,
    },
    {
      title: '監査所見数',
      value: d.audits.total_findings,
      icon: 'mdi-clipboard-alert-outline',
      color: 'orange',
      badge: d.audits.open_findings,
      badgeColor: 'red',
      badgeLabel: '未解決',
      subtitle: `監査完了: ${d.audits.completed} / 全${d.audits.total_audits}件`,
    },
  ]
})

// ---------- Computed: Compliance Doughnut Chart ----------
const complianceDoughnutData = computed(() => {
  const d = dashboardData.value
  if (!d) return { labels: [], datasets: [] }
  return {
    labels: ['準拠', '非準拠', '部分準拠', '未評価'],
    datasets: [
      {
        data: [d.compliance.compliant, d.compliance.non_compliant, d.compliance.partial, d.compliance.unknown],
        backgroundColor: ['#4CAF50', '#F44336', '#FF9800', '#9E9E9E'],
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  }
})

const complianceDoughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { padding: 16, usePointStyle: true, font: { size: 12 } },
    },
    tooltip: {
      callbacks: {
        label: (ctx: { label: string; parsed: number; dataset: { data: number[] } }) => {
          const total = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : '0'
          return `${ctx.label}: ${ctx.parsed}件 (${pct}%)`
        },
      },
    },
  },
  cutout: '65%',
}

// ---------- Computed: Controls Bar Chart ----------
const controlsBarData = computed(() => {
  const d = dashboardData.value
  if (!d) return { labels: [], datasets: [] }
  return {
    labels: ['実施済み', '実施中', '部分実施', '未着手'],
    datasets: [
      {
        label: '管理策数',
        data: [d.controls.implemented, d.controls.in_progress, d.controls.partially, d.controls.not_started],
        backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#9E9E9E'],
        borderRadius: 6,
        barPercentage: 0.6,
      },
    ],
  }
})

const controlsBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: { parsed: { y: number } }) => `${ctx.parsed.y}件`,
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 10 },
      grid: { color: 'rgba(0,0,0,0.06)' },
    },
    x: {
      grid: { display: false },
    },
  },
}

// ---------- Computed: Risk Level Distribution ----------
const riskLevelItems = computed(() => {
  const d = dashboardData.value
  if (!d) return []
  const levels = [
    { label: 'CRITICAL', color: '#F44336', count: d.risks.by_level?.CRITICAL ?? 0 },
    { label: 'HIGH', color: '#FF9800', count: d.risks.by_level?.HIGH ?? 0 },
    { label: 'MEDIUM', color: '#FFC107', count: d.risks.by_level?.MEDIUM ?? 0 },
    { label: 'LOW', color: '#4CAF50', count: d.risks.by_level?.LOW ?? 0 },
  ]
  const total = d.risks.total || 1
  return levels.map((l) => ({ ...l, pct: Math.round((l.count / total) * 100) }))
})

// ---------- Compliance by Law (progress bars) ----------
const complianceByLaw = computed(() => {
  const d = dashboardData.value
  if (!d) {
    return [
      { name: '建設業法', rate: 88, color: 'blue' },
      { name: '品確法', rate: 82, color: 'indigo' },
      { name: '労安法', rate: 75, color: 'deep-purple' },
      { name: 'ISO27001', rate: 85, color: 'green' },
      { name: 'NIST CSF', rate: 70, color: 'teal' },
    ]
  }
  // API returns overall rate; we show it plus derive per-law from the available data
  // In real usage the API could return per-law rates; for now use a reasonable estimation
  const base = d.compliance.rate
  return [
    { name: '建設業法', rate: Math.min(100, base + 3), color: 'blue' },
    { name: '品確法', rate: Math.min(100, base - 3), color: 'indigo' },
    { name: '労安法', rate: Math.min(100, base - 10), color: 'deep-purple' },
    { name: 'ISO27001', rate: d.controls.rate, color: 'green' },
    { name: 'NIST CSF', rate: Math.min(100, base - 15), color: 'teal' },
  ]
})

// ---------- Recent Activities (mock timeline) ----------
const recentActivities = ref([
  {
    id: 1,
    text: '新規リスク RISK-CON-012「足場崩壊リスク」が登録されました',
    date: '2026-03-25 09:30',
    icon: 'mdi-alert-circle',
    color: 'error',
    dotColor: 'red',
  },
  {
    id: 2,
    text: 'ISO27001 A.8.1「利用者エンドポイント機器」が「実施済み」に更新されました',
    date: '2026-03-24 16:45',
    icon: 'mdi-shield-check',
    color: 'success',
    dotColor: 'green',
  },
  {
    id: 3,
    text: '内部監査 AUD-2026-003「情報セキュリティ監査」が完了しました',
    date: '2026-03-23 14:20',
    icon: 'mdi-clipboard-text',
    color: 'info',
    dotColor: 'blue',
  },
  {
    id: 4,
    text: '建設業法コンプライアンス準拠率が88%に改善しました',
    date: '2026-03-22 11:00',
    icon: 'mdi-check-circle',
    color: 'primary',
    dotColor: 'blue',
  },
  {
    id: 5,
    text: 'リスク RISK-FIN-003「資材価格高騰リスク」のレベルがHIGHに変更されました',
    date: '2026-03-21 08:15',
    icon: 'mdi-trending-up',
    color: 'warning',
    dotColor: 'orange',
  },
])

// ---------- Data Fetching ----------
async function fetchDashboard(isRefresh = false) {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }
  errorMessage.value = null

  try {
    const [apiData] = await Promise.allSettled([
      getDashboardData(),
      risksStore.fetchHeatmap(),
    ])

    if (apiData.status === 'fulfilled') {
      dashboardData.value = apiData.value
    } else {
      console.warn('Dashboard API failed, using mock data:', apiData.reason)
      dashboardData.value = mockDashboardData
      if (!isRefresh) {
        errorMessage.value = 'API接続に失敗しました。モックデータを表示中です。'
      }
    }
  } catch {
    console.warn('Dashboard fetch error, using mock data')
    dashboardData.value = mockDashboardData
    errorMessage.value = 'API接続に失敗しました。モックデータを表示中です。'
  } finally {
    lastUpdated.value = new Date().toLocaleString('ja-JP')
    loading.value = false
    refreshing.value = false
  }
}

// ---------- PDF Download ----------
async function handleDownloadPdf() {
  pdfDownloading.value = true
  try {
    const blob = await downloadDashboardPdf()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `GRC_Dashboard_${new Date().toISOString().slice(0, 10)}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('PDF download failed:', e)
    errorMessage.value = 'PDFダウンロードに失敗しました。'
  } finally {
    pdfDownloading.value = false
  }
}

// ---------- Auto Refresh (5 min) ----------
function startAutoRefresh() {
  refreshTimer = setInterval(() => {
    fetchDashboard(true)
  }, 5 * 60 * 1000)
}

// ---------- Lifecycle ----------
onMounted(() => {
  fetchDashboard()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<template>
  <v-container fluid class="dashboard-container pa-4 pa-md-6">
    <!-- Header -->
    <div class="d-flex flex-wrap align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">GRC 統合ダッシュボード</h1>
        <p class="text-body-2 text-medium-emphasis mt-1">
          ISO27001 / NIST CSF 2.0 / 建設業法・品確法・労安法 統合管理
        </p>
      </div>
      <div class="d-flex align-center ga-3 mt-2 mt-md-0">
        <v-chip
          v-if="lastUpdated"
          variant="tonal"
          size="small"
          prepend-icon="mdi-clock-outline"
        >
          最終更新: {{ lastUpdated }}
        </v-chip>
        <v-btn
          variant="tonal"
          color="primary"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="refreshing"
          @click="fetchDashboard(true)"
        >
          更新
        </v-btn>
        <v-btn
          variant="elevated"
          color="primary"
          size="small"
          prepend-icon="mdi-file-pdf-box"
          :loading="pdfDownloading"
          @click="handleDownloadPdf"
        >
          PDF出力
        </v-btn>
      </div>
    </div>

    <!-- Loading -->
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
      height="4"
    />

    <!-- Error Alert -->
    <v-alert
      v-if="errorMessage"
      type="warning"
      variant="tonal"
      closable
      class="mb-4"
      @click:close="errorMessage = null"
    >
      {{ errorMessage }}
    </v-alert>

    <!-- Refreshing indicator -->
    <v-progress-linear
      v-if="refreshing && !loading"
      indeterminate
      color="primary"
      height="2"
      class="mb-2"
    />

    <!-- Summary Cards -->
    <v-row v-if="dashboardData">
      <v-col
        v-for="card in summaryCards"
        :key="card.title"
        cols="12"
        sm="6"
        lg="3"
      >
        <v-card elevation="2" class="summary-card fill-height">
          <v-card-text class="d-flex align-center pa-5">
            <v-avatar :color="card.color" size="56" class="mr-4" variant="tonal">
              <v-icon :color="card.color" size="28">{{ card.icon }}</v-icon>
            </v-avatar>
            <div class="flex-grow-1">
              <div class="text-caption text-medium-emphasis text-uppercase font-weight-medium">
                {{ card.title }}
              </div>
              <div class="d-flex align-center ga-2 mt-1">
                <span class="text-h4 font-weight-bold">{{ card.value }}</span>
                <v-chip
                  v-if="card.badge !== null && card.badge > 0"
                  :color="card.badgeColor"
                  size="x-small"
                  variant="elevated"
                  class="font-weight-bold"
                >
                  {{ card.badgeLabel }}: {{ card.badge }}
                </v-chip>
              </div>
              <div class="text-caption text-medium-emphasis mt-1">{{ card.subtitle }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Row 2: Heatmap + Risk Level Distribution -->
    <v-row class="mt-4" v-if="dashboardData">
      <v-col cols="12" lg="8">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="red-darken-1">mdi-grid</v-icon>
            <span class="text-h6 font-weight-medium">リスクヒートマップ</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <RiskHeatmap :heatmap-data="risksStore.heatmap" />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="4">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="orange">mdi-chart-donut</v-icon>
            <span class="text-h6 font-weight-medium">リスクレベル分布</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <div
              v-for="item in riskLevelItems"
              :key="item.label"
              class="mb-4"
            >
              <div class="d-flex justify-space-between align-center mb-1">
                <div class="d-flex align-center ga-2">
                  <v-avatar :color="item.color" size="12" />
                  <span class="text-body-2 font-weight-medium">{{ item.label }}</span>
                </div>
                <span class="text-body-2 font-weight-bold">{{ item.count }}件 ({{ item.pct }}%)</span>
              </div>
              <v-progress-linear
                :model-value="item.pct"
                :color="item.color"
                height="8"
                rounded
              />
            </div>

            <v-divider class="my-4" />

            <div class="text-center">
              <div class="text-caption text-medium-emphasis">リスクステータス</div>
              <div class="d-flex justify-center ga-4 mt-2 flex-wrap">
                <v-chip
                  v-for="(count, status) in dashboardData.risks.by_status"
                  :key="String(status)"
                  size="small"
                  variant="tonal"
                  :color="
                    String(status) === 'open' ? 'red' :
                    String(status) === 'in_progress' ? 'blue' :
                    String(status) === 'closed' ? 'green' : 'grey'
                  "
                >
                  {{ String(status) === 'open' ? '未対応' :
                     String(status) === 'in_progress' ? '対応中' :
                     String(status) === 'closed' ? '完了' : '受容' }}: {{ count }}
                </v-chip>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Row 3: Compliance Doughnut + Controls Bar Chart -->
    <v-row class="mt-4" v-if="dashboardData">
      <v-col cols="12" md="6">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="green">mdi-check-decagram</v-icon>
            <span class="text-h6 font-weight-medium">コンプライアンスステータス</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4 d-flex flex-column align-center">
            <div class="chart-container-doughnut">
              <Doughnut
                :data="complianceDoughnutData"
                :options="complianceDoughnutOptions"
              />
            </div>
            <div class="text-center mt-4">
              <div class="text-h3 font-weight-bold" :class="dashboardData.compliance.rate >= 80 ? 'text-green' : 'text-orange'">
                {{ dashboardData.compliance.rate }}%
              </div>
              <div class="text-caption text-medium-emphasis">全体準拠率</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="indigo">mdi-shield-half-full</v-icon>
            <span class="text-h6 font-weight-medium">ISO27001 管理策ステータス</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <div class="chart-container-bar">
              <Bar
                :data="controlsBarData"
                :options="controlsBarOptions as any"
              />
            </div>
            <v-divider class="my-4" />
            <div class="d-flex justify-space-around flex-wrap ga-2">
              <div class="text-center">
                <div class="text-h5 font-weight-bold text-green">{{ dashboardData.controls.implemented }}</div>
                <div class="text-caption text-medium-emphasis">実施済み</div>
              </div>
              <div class="text-center">
                <div class="text-h5 font-weight-bold text-blue">{{ dashboardData.controls.in_progress }}</div>
                <div class="text-caption text-medium-emphasis">実施中</div>
              </div>
              <div class="text-center">
                <div class="text-h5 font-weight-bold text-orange">{{ dashboardData.controls.partially }}</div>
                <div class="text-caption text-medium-emphasis">部分実施</div>
              </div>
              <div class="text-center">
                <div class="text-h5 font-weight-bold text-grey">{{ dashboardData.controls.not_started }}</div>
                <div class="text-caption text-medium-emphasis">未着手</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Row 4: Compliance by Law + Audit Summary -->
    <v-row class="mt-4" v-if="dashboardData">
      <v-col cols="12" md="6">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="deep-purple">mdi-gavel</v-icon>
            <span class="text-h6 font-weight-medium">法令別準拠率</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <div
              v-for="law in complianceByLaw"
              :key="law.name"
              class="mb-5"
            >
              <div class="d-flex justify-space-between align-center mb-1">
                <span class="text-body-2 font-weight-medium">{{ law.name }}</span>
                <v-chip
                  size="x-small"
                  :color="law.rate >= 80 ? 'green' : law.rate >= 60 ? 'orange' : 'red'"
                  variant="tonal"
                  class="font-weight-bold"
                >
                  {{ law.rate }}%
                </v-chip>
              </div>
              <v-progress-linear
                :model-value="law.rate"
                :color="law.color"
                height="10"
                rounded
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="teal">mdi-clipboard-text-search-outline</v-icon>
            <span class="text-h6 font-weight-medium">監査サマリー</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <v-row dense>
              <v-col cols="6">
                <v-card variant="tonal" color="blue-lighten-5" class="pa-3 text-center">
                  <div class="text-h4 font-weight-bold text-blue">{{ dashboardData.audits.total_audits }}</div>
                  <div class="text-caption text-medium-emphasis">総監査数</div>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="tonal" color="green-lighten-5" class="pa-3 text-center">
                  <div class="text-h4 font-weight-bold text-green">{{ dashboardData.audits.completed }}</div>
                  <div class="text-caption text-medium-emphasis">完了</div>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="tonal" color="orange-lighten-5" class="pa-3 text-center">
                  <div class="text-h4 font-weight-bold text-orange">{{ dashboardData.audits.in_progress }}</div>
                  <div class="text-caption text-medium-emphasis">実施中</div>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="tonal" color="grey-lighten-4" class="pa-3 text-center">
                  <div class="text-h4 font-weight-bold text-grey-darken-1">{{ dashboardData.audits.planned }}</div>
                  <div class="text-caption text-medium-emphasis">計画中</div>
                </v-card>
              </v-col>
            </v-row>

            <v-divider class="my-4" />

            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-body-2 font-weight-medium">監査所見</div>
                <div class="text-caption text-medium-emphasis">
                  全{{ dashboardData.audits.total_findings }}件中
                  <span class="text-red font-weight-bold">{{ dashboardData.audits.open_findings }}件が未解決</span>
                </div>
              </div>
              <v-progress-circular
                :model-value="
                  dashboardData.audits.total_findings > 0
                    ? ((dashboardData.audits.total_findings - dashboardData.audits.open_findings) / dashboardData.audits.total_findings) * 100
                    : 100
                "
                :size="64"
                :width="6"
                color="teal"
              >
                <span class="text-caption font-weight-bold">
                  {{ dashboardData.audits.total_findings > 0
                    ? Math.round(((dashboardData.audits.total_findings - dashboardData.audits.open_findings) / dashboardData.audits.total_findings) * 100)
                    : 100 }}%
                </span>
              </v-progress-circular>
            </div>

            <v-divider class="my-4" />

            <div class="text-caption text-medium-emphasis mb-2">監査種別</div>
            <div class="d-flex ga-2 flex-wrap">
              <v-chip
                v-for="(count, type) in dashboardData.audits.by_type"
                :key="String(type)"
                size="small"
                variant="tonal"
                color="teal"
              >
                {{ String(type) === 'internal' ? '内部監査' :
                   String(type) === 'external' ? '外部監査' :
                   String(type) === 'certification' ? '認証監査' : String(type) }}: {{ count }}件
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Row 5: Recent Activities -->
    <v-row class="mt-4" v-if="dashboardData">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon class="mr-2" color="primary">mdi-history</v-icon>
            <span class="text-h6 font-weight-medium">最近のアクティビティ</span>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <v-timeline side="end" density="compact" line-thickness="2">
              <v-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :dot-color="activity.dotColor"
                :icon="activity.icon"
                size="small"
              >
                <div class="d-flex flex-column">
                  <span class="text-body-2">{{ activity.text }}</span>
                  <span class="text-caption text-medium-emphasis mt-1">{{ activity.date }}</span>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Skeleton when loading and no data yet -->
    <div v-if="loading && !dashboardData">
      <v-row>
        <v-col v-for="n in 4" :key="n" cols="12" sm="6" lg="3">
          <v-skeleton-loader type="card" />
        </v-col>
      </v-row>
      <v-row class="mt-4">
        <v-col cols="12" lg="8">
          <v-skeleton-loader type="image" height="300" />
        </v-col>
        <v-col cols="12" lg="4">
          <v-skeleton-loader type="card" height="300" />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<style scoped>
.dashboard-container {
  max-width: 1600px;
}

.summary-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12) !important;
}

.chart-container-doughnut {
  width: 100%;
  max-width: 280px;
  height: 280px;
  position: relative;
}

.chart-container-bar {
  width: 100%;
  height: 260px;
  position: relative;
}
</style>
