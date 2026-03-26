<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRisksStore } from '@/store/risks'
import RiskHeatmap from '@/components/RiskHeatmap.vue'
import type { DashboardSummary } from '@/types'
import apiClient from '@/api/client'

const risksStore = useRisksStore()

const loading = ref(true)

const summary = ref<DashboardSummary>({
  total_risks: 0,
  critical_risks: 0,
  compliance_rate: 0,
  open_findings: 0,
})

const summaryCards = ref([
  { title: 'リスク総数', value: 0, icon: 'mdi-alert-circle', color: 'blue', key: 'total_risks' as const },
  { title: 'CRITICALリスク', value: 0, icon: 'mdi-alert', color: 'red', key: 'critical_risks' as const },
  { title: 'ISO27001準拠率', value: '0%', icon: 'mdi-shield-check', color: 'green', key: 'compliance_rate' as const },
  { title: '未処理監査所見数', value: 0, icon: 'mdi-clipboard-alert', color: 'orange', key: 'open_findings' as const },
])

const complianceByLaw = ref([
  { name: '建設業法', rate: 88, color: 'blue' },
  { name: '品確法', rate: 82, color: 'indigo' },
  { name: '労安法', rate: 75, color: 'deep-purple' },
  { name: 'ISO27001', rate: 85, color: 'green' },
  { name: 'NIST CSF', rate: 70, color: 'teal' },
])

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

const updateSummaryCards = () => {
  summaryCards.value[0].value = summary.value.total_risks
  summaryCards.value[1].value = summary.value.critical_risks
  summaryCards.value[2].value = `${summary.value.compliance_rate}%`
  summaryCards.value[3].value = summary.value.open_findings
}

onMounted(async () => {
  loading.value = true
  try {
    const [summaryRes] = await Promise.allSettled([
      apiClient.get('/api/v1/dashboard/summary'),
      risksStore.fetchHeatmap(),
    ])

    if (summaryRes.status === 'fulfilled') {
      summary.value = summaryRes.value.data
    } else {
      // フォールバック: モックデータ
      summary.value = {
        total_risks: 24,
        critical_risks: 3,
        compliance_rate: 85,
        open_findings: 7,
      }
    }
  } catch {
    // フォールバック: モックデータ
    summary.value = {
      total_risks: 24,
      critical_risks: 3,
      compliance_rate: 85,
      open_findings: 7,
    }
  } finally {
    updateSummaryCards()
    loading.value = false
  }
})
</script>

<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">GRC ダッシュボード</h1>

    <!-- ローディング -->
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <!-- サマリカード -->
    <v-row>
      <v-col
        v-for="card in summaryCards"
        :key="card.title"
        cols="12"
        sm="6"
        md="3"
      >
        <v-card elevation="2" class="summary-card">
          <v-card-text class="d-flex align-center pa-5">
            <v-avatar :color="card.color" size="56" class="mr-4">
              <v-icon color="white" size="28">{{ card.icon }}</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption text-medium-emphasis">{{ card.title }}</div>
              <div class="text-h4 font-weight-bold">{{ card.value }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- ヒートマップ & 法令別準拠率 -->
    <v-row class="mt-4">
      <v-col cols="12" md="7">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-grid</v-icon>
            リスクヒートマップ
          </v-card-title>
          <v-card-text>
            <RiskHeatmap :heatmap-data="risksStore.heatmap" />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card elevation="2" class="fill-height">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="green">mdi-scale-balance</v-icon>
            法令別準拠率
          </v-card-title>
          <v-card-text>
            <div
              v-for="law in complianceByLaw"
              :key="law.name"
              class="mb-5"
            >
              <div class="d-flex justify-space-between mb-1">
                <span class="text-body-2 font-weight-medium">{{ law.name }}</span>
                <span class="text-body-2 font-weight-bold">{{ law.rate }}%</span>
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
    </v-row>

    <!-- 最近のアクティビティ -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-history</v-icon>
            最近のアクティビティ
          </v-card-title>
          <v-card-text>
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
  </v-container>
</template>

<style scoped>
.summary-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
</style>
