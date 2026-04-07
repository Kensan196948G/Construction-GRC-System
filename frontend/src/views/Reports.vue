<script setup lang="ts">
import { ref, computed } from 'vue'

// レポート種別定義
interface ReportType {
  id: number
  name: string
  description: string
  icon: string
  color: string
  lastGenerated: string | null
  estimatedTime: string
}

interface ReportHistory {
  id: number
  reportType: string
  format: string
  generatedAt: string
  generatedBy: string
  fileSize: string
  status: 'completed' | 'failed' | 'generating'
}

const reportTypes = ref<ReportType[]>([
  {
    id: 1,
    name: 'GRCダッシュボードレポート',
    description: 'ガバナンス・リスク・コンプライアンスの統合レポート。リスクスコア分布、準拠率、所見サマリーを含む。',
    icon: 'mdi-view-dashboard',
    color: 'primary',
    lastGenerated: '2026-03-28',
    estimatedTime: '約30秒',
  },
  {
    id: 2,
    name: 'ISO27001年次レポート',
    description: 'ISO27001:2022全93管理策の実施状況、4ドメイン別進捗、SoA（適用宣言書）を含む年次報告書。',
    icon: 'mdi-shield-check',
    color: 'blue',
    lastGenerated: '2026-03-15',
    estimatedTime: '約45秒',
  },
  {
    id: 3,
    name: '準拠率レポート',
    description: 'NIST CSF 2.0、建設業法、品確法、労安法への準拠状況と法令別準拠率の詳細分析。',
    icon: 'mdi-chart-bar',
    color: 'green',
    lastGenerated: '2026-03-20',
    estimatedTime: '約20秒',
  },
  {
    id: 4,
    name: 'リスクトレンドレポート',
    description: 'リスク評価の推移、カテゴリ別リスクスコア変化、ヒートマップの経時変化を可視化。',
    icon: 'mdi-trending-up',
    color: 'orange',
    lastGenerated: '2026-03-25',
    estimatedTime: '約25秒',
  },
  {
    id: 5,
    name: 'SoA（適用宣言書）',
    description: 'ISO27001:2022対応のStatement of Applicability。管理策の適用可否・除外理由・実施状況を一覧出力。',
    icon: 'mdi-file-document-check',
    color: 'purple',
    lastGenerated: '2026-02-28',
    estimatedTime: '約15秒',
  },
  {
    id: 6,
    name: '監査報告書',
    description: '内部監査結果のサマリー。所見一覧、是正処置状況（CAP）、フォローアップ結果を含む。',
    icon: 'mdi-clipboard-text-search',
    color: 'red',
    lastGenerated: '2026-03-10',
    estimatedTime: '約35秒',
  },
])

// レポート履歴モックデータ
const reportHistory = ref<ReportHistory[]>([
  { id: 1, reportType: 'GRCダッシュボードレポート', format: 'PDF', generatedAt: '2026-03-28 14:30', generatedBy: '佐藤太郎', fileSize: '2.4 MB', status: 'completed' },
  { id: 2, reportType: 'リスクトレンドレポート', format: 'Excel', generatedAt: '2026-03-25 10:15', generatedBy: '鈴木一郎', fileSize: '1.8 MB', status: 'completed' },
  { id: 3, reportType: '準拠率レポート', format: 'PDF', generatedAt: '2026-03-20 16:45', generatedBy: '佐藤太郎', fileSize: '3.1 MB', status: 'completed' },
  { id: 4, reportType: 'ISO27001年次レポート', format: 'PDF', generatedAt: '2026-03-15 09:00', generatedBy: '高橋健一', fileSize: '5.6 MB', status: 'completed' },
  { id: 5, reportType: '監査報告書', format: 'PDF', generatedAt: '2026-03-10 11:30', generatedBy: '田中美咲', fileSize: '4.2 MB', status: 'completed' },
  { id: 6, reportType: 'SoA（適用宣言書）', format: 'Excel', generatedAt: '2026-02-28 15:00', generatedBy: '佐藤太郎', fileSize: '1.2 MB', status: 'completed' },
  { id: 7, reportType: 'GRCダッシュボードレポート', format: 'Excel', generatedAt: '2026-02-25 13:00', generatedBy: '鈴木一郎', fileSize: '2.1 MB', status: 'completed' },
  { id: 8, reportType: 'リスクトレンドレポート', format: 'PDF', generatedAt: '2026-02-20 10:00', generatedBy: '高橋健一', fileSize: '1.5 MB', status: 'failed' },
])

// 状態管理
const generatingReportId = ref<number | null>(null)
const generatingProgress = ref(0)
const showFormatDialog = ref(false)
const selectedReportForGeneration = ref<ReportType | null>(null)
const selectedFormat = ref<'PDF' | 'Excel'>('PDF')
const showHistoryFilter = ref<string | null>(null)

// テーブルヘッダ
const historyHeaders = [
  { title: 'レポート種別', key: 'reportType', sortable: true },
  { title: '形式', key: 'format', sortable: true, width: '100px' },
  { title: '生成日時', key: 'generatedAt', sortable: true, width: '170px' },
  { title: '生成者', key: 'generatedBy', sortable: true, width: '120px' },
  { title: 'サイズ', key: 'fileSize', sortable: true, width: '100px' },
  { title: '状態', key: 'status', sortable: true, width: '110px' },
  { title: '操作', key: 'actions', sortable: false, width: '100px' },
]

// 算出プロパティ
const filteredHistory = computed(() => {
  if (!showHistoryFilter.value) return reportHistory.value
  return reportHistory.value.filter((h) => h.reportType === showHistoryFilter.value)
})

const historyFilterOptions = computed(() => {
  const unique = [...new Set(reportHistory.value.map((h) => h.reportType))]
  return unique.map((name) => ({ title: name, value: name }))
})

// フォーマット色
const formatColor = (format: string): string => {
  return format === 'PDF' ? 'red' : 'green'
}

const formatIcon = (format: string): string => {
  return format === 'PDF' ? 'mdi-file-pdf-box' : 'mdi-file-excel'
}

// ステータス
const historyStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    completed: 'success',
    failed: 'error',
    generating: 'info',
  }
  return colors[status] || 'grey'
}

const historyStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    completed: '完了',
    failed: '失敗',
    generating: '生成中',
  }
  return labels[status] || status
}

// 日付フォーマット
const formatDate = (date: string | null): string => {
  if (!date) return '未生成'
  return date.substring(0, 10)
}

// レポート生成開始（形式選択ダイアログを開く）
const openGenerateDialog = (report: ReportType) => {
  selectedReportForGeneration.value = report
  selectedFormat.value = 'PDF'
  showFormatDialog.value = true
}

// レポート生成実行
const generateReport = () => {
  if (!selectedReportForGeneration.value) return

  const report = selectedReportForGeneration.value
  showFormatDialog.value = false
  generatingReportId.value = report.id
  generatingProgress.value = 0

  // プログレスシミュレーション
  const interval = setInterval(() => {
    generatingProgress.value += Math.random() * 15 + 5
    if (generatingProgress.value >= 100) {
      generatingProgress.value = 100
      clearInterval(interval)

      // 完了処理
      setTimeout(() => {
        // 最終生成日を更新
        const idx = reportTypes.value.findIndex((r) => r.id === report.id)
        if (idx !== -1) {
          reportTypes.value[idx].lastGenerated = new Date().toISOString().substring(0, 10)
        }

        // 履歴に追加
        reportHistory.value.unshift({
          id: reportHistory.value.length + 1,
          reportType: report.name,
          format: selectedFormat.value,
          generatedAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
          generatedBy: 'ログインユーザー',
          fileSize: (Math.random() * 5 + 0.5).toFixed(1) + ' MB',
          status: 'completed',
        })

        generatingReportId.value = null
        generatingProgress.value = 0
      }, 500)
    }
  }, 200)
}

// ダウンロードシミュレーション
const downloadReport = (item: ReportHistory) => {
  // 実際のAPIではファイルダウンロード処理
  console.log(`Downloading ${item.reportType} (${item.format})`)
}
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-4">
    <!-- ヘッダ -->
    <div class="d-flex align-center mb-6">
      <div>
        <h1 class="text-h4">レポート</h1>
        <p class="text-body-2 text-medium-emphasis mt-1">
          GRC関連レポートの生成・管理
        </p>
      </div>
    </div>

    <!-- レポート種別カード -->
    <h2 class="text-h6 mb-3">
      <v-icon class="mr-1">mdi-file-document-multiple</v-icon>
      レポート生成
    </h2>

    <v-row class="mb-8">
      <v-col
        v-for="report in reportTypes"
        :key="report.id"
        cols="12"
        sm="6"
        lg="4"
      >
        <v-card
          elevation="2"
          :class="{ 'generating-card': generatingReportId === report.id }"
        >
          <v-card-text>
            <div class="d-flex align-start">
              <v-avatar :color="report.color" size="48" class="mr-4" rounded="lg">
                <v-icon color="white" size="28">{{ report.icon }}</v-icon>
              </v-avatar>
              <div class="flex-grow-1">
                <div class="text-subtitle-1 font-weight-bold">{{ report.name }}</div>
                <div class="text-body-2 text-medium-emphasis mt-1" style="line-height: 1.4;">
                  {{ report.description }}
                </div>
              </div>
            </div>

            <!-- プログレス表示 -->
            <v-progress-linear
              v-if="generatingReportId === report.id"
              :model-value="generatingProgress"
              color="primary"
              height="6"
              rounded
              class="mt-4"
            />
            <div
              v-if="generatingReportId === report.id"
              class="text-caption text-center text-medium-emphasis mt-1"
            >
              生成中... {{ Math.round(generatingProgress) }}%
            </div>
          </v-card-text>

          <v-divider />

          <v-card-actions class="px-4 py-3">
            <div class="text-caption text-medium-emphasis">
              <v-icon size="14" class="mr-1">mdi-clock-outline</v-icon>
              最終生成: {{ formatDate(report.lastGenerated) }}
            </div>
            <v-spacer />
            <v-chip size="x-small" variant="tonal" class="mr-2">
              {{ report.estimatedTime }}
            </v-chip>
            <v-btn
              color="primary"
              size="small"
              variant="flat"
              :loading="generatingReportId === report.id"
              :disabled="generatingReportId !== null && generatingReportId !== report.id"
              prepend-icon="mdi-file-export"
              @click="openGenerateDialog(report)"
            >
              生成
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- レポート履歴 -->
    <div class="d-flex align-center mb-3">
      <h2 class="text-h6">
        <v-icon class="mr-1">mdi-history</v-icon>
        生成履歴
      </h2>
      <v-spacer />
      <v-select
        v-model="showHistoryFilter"
        :items="historyFilterOptions"
        item-title="title"
        item-value="value"
        label="レポート種別で絞り込み"
        clearable
        density="compact"
        variant="outlined"
        style="max-width: 300px;"
        prepend-inner-icon="mdi-filter-variant"
        hide-details
      />
    </div>

    <v-card elevation="2">
      <v-data-table
        :headers="historyHeaders"
        :items="filteredHistory"
        :items-per-page="10"
        hover
      >
        <template #item.format="{ item }">
          <v-chip
            :color="formatColor(item.format)"
            size="small"
            label
            variant="tonal"
          >
            <v-icon start size="16">{{ formatIcon(item.format) }}</v-icon>
            {{ item.format }}
          </v-chip>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="historyStatusColor(item.status)"
            size="small"
            label
          >
            {{ historyStatusLabel(item.status) }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            v-if="item.status === 'completed'"
            icon="mdi-download"
            size="small"
            variant="text"
            color="primary"
            @click="downloadReport(item)"
          />
          <v-icon
            v-else-if="item.status === 'failed'"
            color="error"
            size="small"
          >
            mdi-alert-circle
          </v-icon>
          <v-progress-circular
            v-else-if="item.status === 'generating'"
            indeterminate
            size="20"
            width="2"
            color="primary"
          />
        </template>
      </v-data-table>
    </v-card>

    <!-- 形式選択ダイアログ -->
    <v-dialog v-model="showFormatDialog" max-width="450">
      <v-card>
        <v-card-title class="d-flex align-center pa-4">
          <v-icon class="mr-2" color="primary">mdi-file-export</v-icon>
          レポート生成
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showFormatDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <div v-if="selectedReportForGeneration" class="mb-4">
            <div class="text-subtitle-1 font-weight-bold">
              {{ selectedReportForGeneration.name }}
            </div>
            <div class="text-body-2 text-medium-emphasis mt-1">
              出力形式を選択してください。
            </div>
          </div>

          <v-radio-group v-model="selectedFormat" inline>
            <v-radio value="PDF">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon color="red" class="mr-2">mdi-file-pdf-box</v-icon>
                  PDF
                </div>
              </template>
            </v-radio>
            <v-radio value="Excel">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon color="green" class="mr-2">mdi-file-excel</v-icon>
                  Excel
                </div>
              </template>
            </v-radio>
          </v-radio-group>

          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            class="mt-2"
          >
            <div class="text-caption">
              推定生成時間: {{ selectedReportForGeneration?.estimatedTime || '-' }}
            </div>
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="showFormatDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-play"
            @click="generateReport"
          >
            生成開始
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.generating-card {
  border: 1px solid rgb(var(--v-theme-primary));
}
</style>
