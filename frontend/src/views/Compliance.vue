<script setup lang="ts">
import ComplianceGauge from '@/components/ComplianceGauge.vue'

const complianceAreas = [
  { name: '建設業法', rate: 92, status: '準拠' },
  { name: '労働安全衛生法', rate: 88, status: '一部未準拠' },
  { name: '環境関連法規', rate: 95, status: '準拠' },
  { name: '個人情報保護法', rate: 78, status: '改善中' },
  { name: '下請法', rate: 85, status: '準拠' },
]
</script>

<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">コンプライアンス管理</h1>

    <v-row>
      <v-col cols="12" md="4">
        <v-card elevation="2" class="text-center pa-4">
          <v-card-title>全体準拠率</v-card-title>
          <v-card-text>
            <ComplianceGauge :value="87" />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>法令別準拠状況</v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>法令・規制</th>
                  <th>準拠率</th>
                  <th>ステータス</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="area in complianceAreas" :key="area.name">
                  <td>{{ area.name }}</td>
                  <td>
                    <v-progress-linear
                      :model-value="area.rate"
                      :color="area.rate >= 90 ? 'success' : area.rate >= 80 ? 'warning' : 'error'"
                      height="20"
                      rounded
                    >
                      <template #default>
                        <strong>{{ area.rate }}%</strong>
                      </template>
                    </v-progress-linear>
                  </td>
                  <td>
                    <v-chip
                      :color="area.status === '準拠' ? 'success' : area.status === '改善中' ? 'warning' : 'info'"
                      size="small"
                    >
                      {{ area.status }}
                    </v-chip>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
