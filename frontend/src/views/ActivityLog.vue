<template>
  <v-container fluid class="pa-2 pa-sm-4">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">アクティビティログ</h1>
      </v-col>
    </v-row>

    <!-- フィルタ -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title class="text-subtitle-1">
            <v-icon start>mdi-filter</v-icon>
            フィルタ
          </v-card-title>
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.modelName"
                  :items="modelNameOptions"
                  label="モデル名"
                  clearable
                  density="compact"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.action"
                  :items="actionOptions"
                  label="アクション"
                  clearable
                  density="compact"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.timestampFrom"
                  label="開始日時"
                  type="datetime-local"
                  density="compact"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.timestampTo"
                  label="終了日時"
                  type="datetime-local"
                  density="compact"
                  variant="outlined"
                />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" class="d-flex justify-end ga-2">
                <v-btn variant="outlined" @click="resetFilters">
                  リセット
                </v-btn>
                <v-btn color="primary" @click="fetchLogs">
                  <v-icon start>mdi-magnify</v-icon>
                  検索
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 表示切替 -->
    <v-row>
      <v-col cols="12">
        <v-btn-toggle v-model="viewMode" mandatory color="primary" density="compact">
          <v-btn value="table">
            <v-icon start>mdi-table</v-icon>
            テーブル
          </v-btn>
          <v-btn value="timeline">
            <v-icon start>mdi-timeline</v-icon>
            タイムライン
          </v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>

    <!-- テーブル表示 -->
    <v-row v-if="viewMode === 'table'">
      <v-col cols="12">
        <v-card>
          <v-data-table
            :headers="headers"
            :items="logs"
            :loading="loading"
            :items-per-page="20"
            class="elevation-1"
          >
            <template #item.action="{ item }">
              <v-chip :color="actionColor(item.action)" size="small" label>
                {{ actionLabel(item.action) }}
              </v-chip>
            </template>
            <template #item.timestamp="{ item }">
              {{ formatDateTime(item.timestamp) }}
            </template>
            <template #item.user_display="{ item }">
              <v-icon start size="small">mdi-account</v-icon>
              {{ item.user_display || 'システム' }}
            </template>
            <template #item.changes="{ item }">
              <v-btn
                v-if="item.changes && Object.keys(item.changes).length > 0"
                size="small"
                variant="text"
                color="primary"
                @click="showChanges(item)"
              >
                詳細
              </v-btn>
              <span v-else class="text-grey">-</span>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- タイムライン表示 -->
    <v-row v-if="viewMode === 'timeline'">
      <v-col cols="12" md="8" offset-md="2">
        <v-card class="pa-4">
          <v-timeline density="compact" side="end">
            <v-timeline-item
              v-for="log in logs"
              :key="log.id"
              :dot-color="actionColor(log.action)"
              size="small"
            >
              <template #opposite>
                <span class="text-caption text-grey">
                  {{ formatDateTime(log.timestamp) }}
                </span>
              </template>
              <v-card variant="outlined" class="mb-2">
                <v-card-text class="py-2 px-3">
                  <div class="d-flex align-center ga-2 mb-1">
                    <v-chip :color="actionColor(log.action)" size="x-small" label>
                      {{ actionLabel(log.action) }}
                    </v-chip>
                    <strong>{{ log.model_name }}</strong>
                  </div>
                  <div class="text-body-2">{{ log.object_repr }}</div>
                  <div class="text-caption text-grey mt-1">
                    <v-icon size="x-small">mdi-account</v-icon>
                    {{ log.user_display || 'システム' }}
                  </div>
                  <div
                    v-if="log.changes && Object.keys(log.changes).length > 0"
                    class="mt-2"
                  >
                    <v-btn
                      size="x-small"
                      variant="text"
                      color="primary"
                      @click="showChanges(log)"
                    >
                      変更内容を表示
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </v-timeline-item>
          </v-timeline>
          <div v-if="logs.length === 0 && !loading" class="text-center text-grey pa-8">
            ログが見つかりません
          </div>
          <div v-if="loading" class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 変更詳細ダイアログ -->
    <v-dialog v-model="changesDialog" max-width="600">
      <v-card>
        <v-card-title>変更内容</v-card-title>
        <v-card-text>
          <div v-if="selectedLog" class="mb-3">
            <div class="text-subtitle-2 mb-1">
              {{ selectedLog.model_name }} - {{ selectedLog.object_repr }}
            </div>
            <div class="text-caption text-grey mb-3">
              {{ formatDateTime(selectedLog.timestamp) }}
              / {{ selectedLog.user_display || 'システム' }}
            </div>
          </div>
          <v-table v-if="selectedLog" density="compact">
            <thead>
              <tr>
                <th>フィールド</th>
                <th>値</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(value, key) in selectedLog.changes" :key="key">
                <td class="font-weight-medium">{{ key }}</td>
                <td>
                  <template v-if="typeof value === 'object' && value !== null">
                    <pre class="text-body-2">{{ JSON.stringify(value, null, 2) }}</pre>
                  </template>
                  <template v-else>
                    {{ value }}
                  </template>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="changesDialog = false">閉じる</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface ActivityLogItem {
  id: string
  user: string | null
  user_display: string
  action: string
  model_name: string
  object_id: string
  object_repr: string
  changes: Record<string, unknown>
  ip_address: string | null
  timestamp: string
}

const logs = ref<ActivityLogItem[]>([])
const loading = ref(false)
const viewMode = ref('table')
const changesDialog = ref(false)
const selectedLog = ref<ActivityLogItem | null>(null)

const filters = ref({
  modelName: null as string | null,
  action: null as string | null,
  timestampFrom: '',
  timestampTo: '',
})

const modelNameOptions = [
  { title: 'リスク', value: 'Risk' },
  { title: '管理策', value: 'Control' },
  { title: 'コンプライアンス', value: 'ComplianceRequirement' },
  { title: '監査', value: 'Audit' },
  { title: '監査所見', value: 'AuditFinding' },
  { title: 'レポート', value: 'Report' },
]

const actionOptions = [
  { title: '作成', value: 'create' },
  { title: '更新', value: 'update' },
  { title: '削除', value: 'delete' },
  { title: 'ステータス変更', value: 'status_change' },
  { title: 'ログイン', value: 'login' },
  { title: 'エクスポート', value: 'export' },
]

const headers = [
  { title: '日時', key: 'timestamp', width: '180px' },
  { title: 'ユーザー', key: 'user_display', width: '140px' },
  { title: 'アクション', key: 'action', width: '130px' },
  { title: 'モデル', key: 'model_name', width: '160px' },
  { title: '対象', key: 'object_repr' },
  { title: '変更内容', key: 'changes', width: '100px', sortable: false },
]

function actionColor(action: string): string {
  const colorMap: Record<string, string> = {
    create: 'success',
    update: 'info',
    delete: 'error',
    status_change: 'warning',
    login: 'purple',
    export: 'teal',
  }
  return colorMap[action] || 'grey'
}

function actionLabel(action: string): string {
  const labelMap: Record<string, string> = {
    create: '作成',
    update: '更新',
    delete: '削除',
    status_change: 'ステータス変更',
    login: 'ログイン',
    export: 'エクスポート',
  }
  return labelMap[action] || action
}

function formatDateTime(dt: string): string {
  if (!dt) return '-'
  const d = new Date(dt)
  return d.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function showChanges(log: ActivityLogItem) {
  selectedLog.value = log
  changesDialog.value = true
}

function resetFilters() {
  filters.value = {
    modelName: null,
    action: null,
    timestampFrom: '',
    timestampTo: '',
  }
  fetchLogs()
}

async function fetchLogs() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filters.value.modelName) params.model_name = filters.value.modelName
    if (filters.value.action) params.action = filters.value.action
    if (filters.value.timestampFrom) params.timestamp_from = filters.value.timestampFrom
    if (filters.value.timestampTo) params.timestamp_to = filters.value.timestampTo

    const response = await axios.get('/api/v1/audits/activity-logs/', { params })
    logs.value = response.data.results ?? response.data
  } catch (error) {
    console.error('Failed to fetch activity logs:', error)
    logs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>
