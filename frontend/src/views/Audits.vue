<script setup lang="ts">
const audits = [
  { id: 'AUD-2026-001', title: '情報セキュリティ内部監査', scope: 'ISMS全般', status: '完了', date: '2026-01-15', findings: 3 },
  { id: 'AUD-2026-002', title: '安全衛生監査', scope: '現場安全管理', status: '完了', date: '2026-02-10', findings: 5 },
  { id: 'AUD-2026-003', title: 'コンプライアンス監査', scope: '建設業法準拠', status: '実施中', date: '2026-03-20', findings: 2 },
  { id: 'AUD-2026-004', title: '環境マネジメント監査', scope: '環境法規準拠', status: '計画中', date: '2026-04-15', findings: 0 },
  { id: 'AUD-2026-005', title: '品質マネジメント監査', scope: 'QMS全般', status: '計画中', date: '2026-05-20', findings: 0 },
]

const headers = [
  { title: '監査ID', key: 'id' },
  { title: '監査名', key: 'title' },
  { title: '対象範囲', key: 'scope' },
  { title: 'ステータス', key: 'status' },
  { title: '実施日', key: 'date' },
  { title: '所見数', key: 'findings' },
]

const statusColor = (status: string) => {
  const colors: Record<string, string> = {
    '完了': 'success',
    '実施中': 'info',
    '計画中': 'grey',
  }
  return colors[status] || 'grey'
}
</script>

<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">内部監査</h1>

    <v-card elevation="2">
      <v-data-table :headers="headers" :items="audits" hover>
        <template #item.status="{ item }">
          <v-chip :color="statusColor(item.status)" size="small" label>
            {{ item.status }}
          </v-chip>
        </template>
        <template #item.findings="{ item }">
          <v-chip
            :color="item.findings > 0 ? 'warning' : 'success'"
            size="small"
          >
            {{ item.findings }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>
