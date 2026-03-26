<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRisksStore } from '@/store/risks'
import RiskHeatmap from '@/components/RiskHeatmap.vue'
import ComplianceGauge from '@/components/ComplianceGauge.vue'

const risksStore = useRisksStore()

const summary = ref({
  totalRisks: 0,
  criticalCount: 0,
  complianceRate: 0,
  openFindings: 0,
})

const recentActivities = ref([
  { id: 1, text: '新規リスク「足場崩壊リスク」が登録されました', date: '2026-03-25', icon: 'mdi-alert-circle', color: 'error' },
  { id: 2, text: 'ISO27001 A.8.1 管理策が「実施済み」に更新されました', date: '2026-03-24', icon: 'mdi-shield-check', color: 'success' },
  { id: 3, text: '内部監査 #AUD-2026-003 が完了しました', date: '2026-03-23', icon: 'mdi-clipboard-text', color: 'info' },
  { id: 4, text: 'コンプライアンス準拠率が85%に改善しました', date: '2026-03-22', icon: 'mdi-check-circle', color: 'primary' },
  { id: 5, text: 'リスク「資材価格高騰」のレベルがHIGHに変更されました', date: '2026-03-21', icon: 'mdi-alert-circle', color: 'warning' },
])

const summaryCards = ref([
  { title: 'リスク総数', value: 24, icon: 'mdi-alert-circle-outline', color: 'primary' },
  { title: 'CRITICAL', value: 3, icon: 'mdi-alert-octagon', color: 'error' },
  { title: '準拠率', value: '85%', icon: 'mdi-check-circle-outline', color: 'success' },
  { title: '未処理監査所見数', value: 7, icon: 'mdi-clipboard-alert-outline', color: 'warning' },
])

onMounted(async () => {
  await risksStore.fetchHeatmap()
})
</script>

<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">GRC ダッシュボード</h1>

    <!-- サマリカード -->
    <v-row>
      <v-col v-for="card in summaryCards" :key="card.title" cols="12" sm="6" md="3">
        <v-card elevation="2">
          <v-card-text class="d-flex align-center">
            <v-icon :color="card.color" size="48" class="mr-4">{{ card.icon }}</v-icon>
            <div>
              <div class="text-caption text-grey">{{ card.title }}</div>
              <div class="text-h4 font-weight-bold">{{ card.value }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- ヒートマップ & 準拠率ゲージ -->
    <v-row class="mt-4">
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>リスクヒートマップ</v-card-title>
          <v-card-text>
            <RiskHeatmap :heatmap-data="risksStore.heatmap" />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card elevation="2" class="text-center">
          <v-card-title>コンプライアンス準拠率</v-card-title>
          <v-card-text>
            <ComplianceGauge :value="85" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 最近のアクティビティ -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>最近のアクティビティ</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="activity in recentActivities"
                :key="activity.id"
              >
                <template #prepend>
                  <v-icon :color="activity.color">{{ activity.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ activity.text }}</v-list-item-title>
                <v-list-item-subtitle>{{ activity.date }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
