<script setup lang="ts">
const reports = [
  { id: 1, name: 'リスク評価レポート', description: 'リスク一覧とヒートマップの総合レポート', lastGenerated: '2026-03-20', icon: 'mdi-file-chart' },
  { id: 2, name: 'コンプライアンス準拠状況レポート', description: '法令別準拠率の詳細レポート', lastGenerated: '2026-03-18', icon: 'mdi-file-check' },
  { id: 3, name: 'ISO27001管理策実施状況レポート', description: '93管理策の実施状況サマリ', lastGenerated: '2026-03-15', icon: 'mdi-file-document' },
  { id: 4, name: '内部監査所見レポート', description: '監査所見と是正措置の進捗', lastGenerated: '2026-03-10', icon: 'mdi-file-search' },
  { id: 5, name: 'GRC統合ダッシュボードレポート', description: 'ガバナンス・リスク・コンプライアンスの統合レポート', lastGenerated: '2026-03-01', icon: 'mdi-file-presentation-box' },
]
</script>

<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">レポート</h1>

    <v-row>
      <v-col v-for="report in reports" :key="report.id" cols="12" md="6">
        <v-card elevation="2">
          <v-card-text class="d-flex align-center">
            <v-icon size="48" color="primary" class="mr-4">{{ report.icon }}</v-icon>
            <div class="flex-grow-1">
              <div class="text-h6">{{ report.name }}</div>
              <div class="text-body-2 text-grey">{{ report.description }}</div>
              <div class="text-caption text-grey-darken-1 mt-1">
                最終生成日: {{ report.lastGenerated }}
              </div>
            </div>
            <v-btn color="primary" variant="outlined" size="small">
              生成
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
