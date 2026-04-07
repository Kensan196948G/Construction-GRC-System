<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { useComplianceStore } from '@/store/compliance'
import type { ComplianceRequirement, ComplianceStatus } from '@/types'
import ComplianceGauge from '@/components/ComplianceGauge.vue'
import { exportComplianceCSV, exportComplianceExcel } from '@/api/compliance'
import { downloadBlob } from '@/utils/download'

const complianceStore = useComplianceStore()
const { smAndDown } = useDisplay()

// ---------- タブ ----------
const activeTab = ref('all')
const frameworkTabs = [
  { value: 'all', label: '全て', icon: 'mdi-view-list' },
  { value: '建設業法', label: '建設業法', icon: 'mdi-office-building' },
  { value: '品確法', label: '品確法', icon: 'mdi-check-decagram' },
  { value: '労安法', label: '労安法', icon: 'mdi-hard-hat' },
  { value: 'ISO27001', label: 'ISO27001', icon: 'mdi-shield-lock' },
  { value: 'NIST CSF', label: 'NIST CSF', icon: 'mdi-security' },
  { value: '下請法', label: '下請法', icon: 'mdi-handshake' },
  { value: 'ISO20000', label: 'ISO20000', icon: 'mdi-cog' },
]

// ---------- フィルタ ----------
const statusFilter = ref<string | null>(null)
const searchQuery = ref('')

const complianceStatuses = [
  { title: '準拠', value: 'compliant' },
  { title: '非準拠', value: 'non_compliant' },
  { title: '一部準拠', value: 'partial' },
  { title: '未評価', value: 'unknown' },
]

// ---------- テーブル ----------
const itemsPerPage = ref(10)
const page = ref(1)
const sortBy = ref<{ key: string; order: 'asc' | 'desc' }[]>([])

const headers = [
  { title: '要件ID', key: 'req_id', sortable: true, width: '120px' },
  { title: 'タイトル', key: 'title', sortable: true },
  { title: 'カテゴリ', key: 'category', sortable: true, width: '140px' },
  { title: '準拠状況', key: 'compliance_status', sortable: true, width: '130px' },
  { title: '必須/任意', key: 'is_mandatory', sortable: true, width: '100px' },
  { title: '担当者', key: 'owner', sortable: true, width: '120px' },
  { title: '最終評価日', key: 'last_assessed_at', sortable: true, width: '120px' },
]

// ---------- ダイアログ ----------
const showDetailDialog = ref(false)
const selectedRequirement = ref<ComplianceRequirement | null>(null)
const showStatusUpdateDialog = ref(false)
const updatingStatus = ref<ComplianceStatus>('unknown')

// ---------- モックデータ ----------
const mockRequirements: ComplianceRequirement[] = [
  { id: '1', req_id: 'KEN-001', framework: '建設業法', category: '許可・届出', title: '建設業許可の維持', description: '建設業法第3条に基づく建設業許可を適切に維持し、更新手続きを期限内に完了する。', article_ref: '建設業法第3条', is_mandatory: true, frequency: '年次', owner: '法務部', last_assessed_at: '2026-03-15', compliance_status: 'compliant' },
  { id: '2', req_id: 'KEN-002', framework: '建設業法', category: '許可・届出', title: '経営事項審査の受審', description: '公共工事の入札参加に必要な経営事項審査を毎年受審する。', article_ref: '建設業法第27条の23', is_mandatory: true, frequency: '年次', owner: '経営企画部', last_assessed_at: '2026-03-10', compliance_status: 'compliant' },
  { id: '3', req_id: 'KEN-003', framework: '建設業法', category: '施工管理', title: '主任技術者・監理技術者の配置', description: '工事現場ごとに主任技術者または監理技術者を適切に配置する。', article_ref: '建設業法第26条', is_mandatory: true, frequency: '都度', owner: '工事部', last_assessed_at: '2026-03-01', compliance_status: 'partial' },
  { id: '4', req_id: 'KEN-004', framework: '建設業法', category: '下請管理', title: '一括下請負の禁止', description: '元請負人が請け負った工事を一括して下請に出すことの禁止を遵守する。', article_ref: '建設業法第22条', is_mandatory: true, frequency: '常時', owner: '工事部', last_assessed_at: '2026-02-20', compliance_status: 'compliant' },
  { id: '5', req_id: 'KEN-005', framework: '建設業法', category: '契約管理', title: '請負契約の書面化', description: '建設工事の請負契約について所定の事項を書面で締結する。', article_ref: '建設業法第19条', is_mandatory: true, frequency: '都度', owner: '法務部', last_assessed_at: '2026-02-15', compliance_status: 'compliant' },
  { id: '6', req_id: 'HIN-001', framework: '品確法', category: '品質確保', title: '発注者責務の履行', description: '公共工事の品質確保のための発注者としての責務を履行する。', article_ref: '品確法第7条', is_mandatory: true, frequency: '常時', owner: '品質管理部', last_assessed_at: '2026-03-12', compliance_status: 'compliant' },
  { id: '7', req_id: 'HIN-002', framework: '品確法', category: '品質確保', title: '技術的能力の審査', description: '受注者の技術的能力の審査を適切に実施する。', article_ref: '品確法第13条', is_mandatory: true, frequency: '都度', owner: '品質管理部', last_assessed_at: '2026-03-05', compliance_status: 'partial' },
  { id: '8', req_id: 'HIN-003', framework: '品確法', category: '担い手確保', title: '担い手の中長期的な育成・確保', description: '建設工事に従事する者の育成・確保に配慮する。', article_ref: '品確法第3条', is_mandatory: false, frequency: '年次', owner: '人事部', last_assessed_at: '2026-02-28', compliance_status: 'partial' },
  { id: '9', req_id: 'ROU-001', framework: '労安法', category: '安全管理', title: '安全衛生管理体制の構築', description: '事業場における安全衛生管理体制を適切に構築する。', article_ref: '労安法第10条〜第19条', is_mandatory: true, frequency: '常時', owner: '安全管理部', last_assessed_at: '2026-03-20', compliance_status: 'compliant' },
  { id: '10', req_id: 'ROU-002', framework: '労安法', category: '安全管理', title: '安全衛生教育の実施', description: '労働者の雇入れ時・作業内容変更時等に安全衛生教育を実施する。', article_ref: '労安法第59条', is_mandatory: true, frequency: '都度', owner: '安全管理部', last_assessed_at: '2026-03-18', compliance_status: 'compliant' },
  { id: '11', req_id: 'ROU-003', framework: '労安法', category: '健康管理', title: '健康診断の実施', description: '労働者に対する定期健康診断を適切に実施する。', article_ref: '労安法第66条', is_mandatory: true, frequency: '年次', owner: '人事部', last_assessed_at: '2026-03-01', compliance_status: 'compliant' },
  { id: '12', req_id: 'ROU-004', framework: '労安法', category: '危険防止', title: '足場等の安全基準遵守', description: '足場その他の作業設備について安全基準を遵守する。', article_ref: '労安法第20条', is_mandatory: true, frequency: '常時', owner: '工事部', last_assessed_at: '2026-02-25', compliance_status: 'non_compliant' },
  { id: '13', req_id: 'ISO-001', framework: 'ISO27001', category: '情報セキュリティ方針', title: '情報セキュリティ方針の策定', description: '経営陣が承認した情報セキュリティ方針を策定・維持する。', article_ref: 'A.5.1', is_mandatory: true, frequency: '年次', owner: '情報セキュリティ部', last_assessed_at: '2026-03-10', compliance_status: 'compliant' },
  { id: '14', req_id: 'ISO-002', framework: 'ISO27001', category: 'アクセス制御', title: 'アクセス制御方針の実施', description: 'ビジネス要件に基づくアクセス制御方針を策定・実施する。', article_ref: 'A.5.15', is_mandatory: true, frequency: '常時', owner: '情報システム部', last_assessed_at: '2026-03-08', compliance_status: 'compliant' },
  { id: '15', req_id: 'ISO-003', framework: 'ISO27001', category: 'リスク管理', title: '情報セキュリティリスクアセスメント', description: '定期的な情報セキュリティリスクアセスメントを実施する。', article_ref: 'A.5.7', is_mandatory: true, frequency: '半期', owner: '情報セキュリティ部', last_assessed_at: '2026-02-20', compliance_status: 'partial' },
  { id: '16', req_id: 'NIST-001', framework: 'NIST CSF', category: 'GOVERN', title: 'ガバナンス体制の確立', description: 'サイバーセキュリティリスクのガバナンス体制を確立する。', article_ref: 'GV.OC', is_mandatory: false, frequency: '年次', owner: '経営企画部', last_assessed_at: '2026-03-15', compliance_status: 'compliant' },
  { id: '17', req_id: 'NIST-002', framework: 'NIST CSF', category: 'IDENTIFY', title: '資産管理', description: '組織の資産を特定し管理する。', article_ref: 'ID.AM', is_mandatory: false, frequency: '四半期', owner: '情報システム部', last_assessed_at: '2026-03-01', compliance_status: 'partial' },
  { id: '18', req_id: 'NIST-003', framework: 'NIST CSF', category: 'PROTECT', title: '保護対策の実施', description: 'サイバーセキュリティの保護対策を実施する。', article_ref: 'PR.AC', is_mandatory: false, frequency: '常時', owner: '情報セキュリティ部', last_assessed_at: '2026-02-28', compliance_status: 'compliant' },
  { id: '19', req_id: 'SIT-001', framework: '下請法', category: '書面交付', title: '3条書面の交付', description: '下請事業者への発注時に所定の事項を記載した書面を交付する。', article_ref: '下請法第3条', is_mandatory: true, frequency: '都度', owner: '調達部', last_assessed_at: '2026-03-10', compliance_status: 'compliant' },
  { id: '20', req_id: 'SIT-002', framework: '下請法', category: '支払', title: '下請代金の支払期日遵守', description: '下請代金を受領日から60日以内に支払う。', article_ref: '下請法第2条の2', is_mandatory: true, frequency: '常時', owner: '経理部', last_assessed_at: '2026-03-05', compliance_status: 'compliant' },
  { id: '21', req_id: 'SIT-003', framework: '下請法', category: '禁止行為', title: '受領拒否の禁止', description: '下請事業者の責に帰すべき理由がない場合、給付の受領を拒んではならない。', article_ref: '下請法第4条第1項', is_mandatory: true, frequency: '常時', owner: '調達部', last_assessed_at: '2026-02-20', compliance_status: 'unknown' },
  { id: '22', req_id: 'ITSM-001', framework: 'ISO20000', category: 'サービス管理', title: 'サービスマネジメントシステムの確立', description: 'ITサービスマネジメントシステムを確立・維持する。', article_ref: 'ISO20000-1:2018 4.1', is_mandatory: false, frequency: '年次', owner: '情報システム部', last_assessed_at: '2026-03-01', compliance_status: 'partial' },
  { id: '23', req_id: 'ITSM-002', framework: 'ISO20000', category: 'インシデント管理', title: 'インシデント管理プロセス', description: 'ITインシデントの検知・記録・解決のプロセスを確立する。', article_ref: 'ISO20000-1:2018 8.6', is_mandatory: false, frequency: '常時', owner: '情報システム部', last_assessed_at: '2026-02-25', compliance_status: 'compliant' },
]

// ---------- フレームワーク別準拠率計算 ----------
const frameworkRates = computed(() => {
  const data = requirements.value.length > 0 ? requirements.value : mockRequirements
  const groups: Record<string, { total: number; compliant: number; partial: number }> = {}

  for (const req of data) {
    if (!groups[req.framework]) {
      groups[req.framework] = { total: 0, compliant: 0, partial: 0 }
    }
    groups[req.framework].total++
    if (req.compliance_status === 'compliant') groups[req.framework].compliant++
    if (req.compliance_status === 'partial') groups[req.framework].partial++
  }

  return Object.entries(groups).map(([name, g]) => ({
    name,
    rate: Math.round(((g.compliant + g.partial * 0.5) / g.total) * 100),
    total: g.total,
    compliant: g.compliant,
    partial: g.partial,
    nonCompliant: g.total - g.compliant - g.partial,
  }))
})

// ---------- 全体準拠率 ----------
const overallRate = computed(() => {
  if (complianceStore.complianceRate?.rate != null) {
    return Math.round(complianceStore.complianceRate.rate)
  }
  const data = requirements.value.length > 0 ? requirements.value : mockRequirements
  const total = data.length
  if (total === 0) return 0
  const compliant = data.filter(r => r.compliance_status === 'compliant').length
  const partial = data.filter(r => r.compliance_status === 'partial').length
  return Math.round(((compliant + partial * 0.5) / total) * 100)
})

// ---------- ストアまたはモックの要件リスト ----------
const requirements = computed(() => {
  return complianceStore.requirements.length > 0
    ? complianceStore.requirements
    : mockRequirements
})

// ---------- フィルタ済み要件 ----------
const filteredRequirements = computed(() => {
  let result = requirements.value

  // タブフィルタ
  if (activeTab.value !== 'all') {
    result = result.filter(r => r.framework === activeTab.value)
  }

  // ステータスフィルタ
  if (statusFilter.value) {
    result = result.filter(r => r.compliance_status === statusFilter.value)
  }

  // 検索
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      r =>
        r.req_id.toLowerCase().includes(q) ||
        r.title.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q) ||
        (r.owner && r.owner.toLowerCase().includes(q))
    )
  }

  return result
})

// ---------- ステータス表示ヘルパー ----------
const statusColor = (status: ComplianceStatus | string): string => {
  const colors: Record<string, string> = {
    compliant: 'green',
    non_compliant: 'red',
    partial: 'orange',
    unknown: 'grey',
  }
  return colors[status] || 'grey'
}

const statusLabel = (status: ComplianceStatus | string): string => {
  const labels: Record<string, string> = {
    compliant: '準拠',
    non_compliant: '非準拠',
    partial: '一部準拠',
    unknown: '未評価',
  }
  return labels[status] || status
}

const statusIcon = (status: ComplianceStatus | string): string => {
  const icons: Record<string, string> = {
    compliant: 'mdi-check-circle',
    non_compliant: 'mdi-close-circle',
    partial: 'mdi-alert-circle',
    unknown: 'mdi-help-circle',
  }
  return icons[status] || 'mdi-help-circle'
}

const rateColor = (rate: number): string => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'error'
}

// ---------- 日付フォーマット ----------
const formatDate = (date: string | null): string => {
  if (!date) return '-'
  return date.substring(0, 10)
}

// ---------- 行クリックで詳細表示 ----------
const onRowClick = (_event: Event, row: { item: ComplianceRequirement }) => {
  selectedRequirement.value = row.item
  showDetailDialog.value = true
}

// ---------- ステータス更新 ----------
const openStatusUpdate = (req: ComplianceRequirement) => {
  selectedRequirement.value = req
  updatingStatus.value = req.compliance_status
  showStatusUpdateDialog.value = true
}

const handleStatusUpdate = async () => {
  if (!selectedRequirement.value) return
  try {
    await complianceStore.updateRequirementStatus(selectedRequirement.value.id, {
      compliance_status: updatingStatus.value,
    })
    showStatusUpdateDialog.value = false
    // モックデータ更新（API未接続時）
    const idx = mockRequirements.findIndex(r => r.id === selectedRequirement.value!.id)
    if (idx !== -1) {
      mockRequirements[idx].compliance_status = updatingStatus.value
    }
  } catch {
    // モックデータのみ更新
    const idx = mockRequirements.findIndex(r => r.id === selectedRequirement.value!.id)
    if (idx !== -1) {
      mockRequirements[idx].compliance_status = updatingStatus.value
    }
    showStatusUpdateDialog.value = false
  }
}

// ---------- サマリーカード数値 ----------
const summaryCards = computed(() => {
  const data = requirements.value
  return [
    {
      title: '準拠',
      count: data.filter(r => r.compliance_status === 'compliant').length,
      color: 'green',
      icon: 'mdi-check-circle',
    },
    {
      title: '一部準拠',
      count: data.filter(r => r.compliance_status === 'partial').length,
      color: 'orange',
      icon: 'mdi-alert-circle',
    },
    {
      title: '非準拠',
      count: data.filter(r => r.compliance_status === 'non_compliant').length,
      color: 'red',
      icon: 'mdi-close-circle',
    },
    {
      title: '未評価',
      count: data.filter(r => r.compliance_status === 'unknown').length,
      color: 'grey',
      icon: 'mdi-help-circle',
    },
  ]
})

const exportingCSV = ref(false)
const exportingExcel = ref(false)

const handleExportCSV = async () => {
  exportingCSV.value = true
  try {
    const response = await exportComplianceCSV()
    downloadBlob(response.data, 'compliance.csv')
  } finally {
    exportingCSV.value = false
  }
}

const handleExportExcel = async () => {
  exportingExcel.value = true
  try {
    const response = await exportComplianceExcel()
    downloadBlob(response.data, 'compliance.xlsx')
  } finally {
    exportingExcel.value = false
  }
}

// ---------- フィルタ変更時リセット ----------
watch([activeTab, statusFilter], () => {
  page.value = 1
})

// ---------- 初期ロード ----------
onMounted(async () => {
  try {
    await Promise.all([
      complianceStore.fetchRequirements(),
      complianceStore.fetchComplianceRate(),
    ])
  } catch {
    // API接続失敗時はモックデータで表示
  }
})
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-4">
    <!-- ヘッダ -->
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4">コンプライアンス管理</h1>
      <v-spacer />
      <v-btn
        variant="outlined"
        prepend-icon="mdi-file-delimited"
        :loading="exportingCSV"
        class="mr-2"
        @click="handleExportCSV"
      >
        CSV
      </v-btn>
      <v-btn
        variant="outlined"
        prepend-icon="mdi-microsoft-excel"
        :loading="exportingExcel"
        class="mr-2"
        @click="handleExportExcel"
      >
        Excel
      </v-btn>
      <v-chip color="primary" variant="tonal" class="mr-2">
        {{ requirements.length }} 要件
      </v-chip>
    </div>

    <!-- ローディング -->
    <v-progress-linear
      v-if="complianceStore.loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <!-- エラー表示 -->
    <v-alert
      v-if="complianceStore.error"
      type="warning"
      variant="tonal"
      density="compact"
      closable
      class="mb-4"
    >
      {{ complianceStore.error }}（モックデータを表示中）
    </v-alert>

    <!-- サマリーセクション -->
    <v-row class="mb-4">
      <!-- 全体準拠率ゲージ -->
      <v-col cols="12" md="3">
        <v-card elevation="2" class="text-center pa-4" height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">全体準拠率</v-card-title>
          <v-card-text>
            <ComplianceGauge :value="overallRate" />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- ステータス別カード -->
      <v-col cols="12" md="3">
        <v-row dense>
          <v-col
            v-for="card in summaryCards"
            :key="card.title"
            cols="6"
          >
            <v-card
              elevation="2"
              class="text-center pa-3"
            >
              <v-icon :color="card.color" size="28" class="mb-1">{{ card.icon }}</v-icon>
              <div class="text-h5 font-weight-bold">{{ card.count }}</div>
              <div class="text-caption text-medium-emphasis">{{ card.title }}</div>
            </v-card>
          </v-col>
        </v-row>
      </v-col>

      <!-- フレームワーク別準拠率 -->
      <v-col cols="12" md="6">
        <v-card elevation="2" height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-icon class="mr-2" size="20">mdi-chart-bar</v-icon>
            フレームワーク別準拠率
          </v-card-title>
          <v-card-text>
            <div
              v-for="fw in frameworkRates"
              :key="fw.name"
              class="mb-3"
            >
              <div class="d-flex justify-space-between align-center mb-1">
                <span class="text-body-2">{{ fw.name }}</span>
                <span class="text-body-2 font-weight-medium">
                  {{ fw.rate }}%
                  <span class="text-caption text-medium-emphasis ml-1">
                    ({{ fw.compliant }}/{{ fw.total }})
                  </span>
                </span>
              </div>
              <v-progress-linear
                :model-value="fw.rate"
                :color="rateColor(fw.rate)"
                height="10"
                rounded
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- タブ切替 -->
    <v-card elevation="2" class="mb-4">
      <v-tabs
        v-model="activeTab"
        show-arrows
        color="primary"
        density="comfortable"
      >
        <v-tab
          v-for="tab in frameworkTabs"
          :key="tab.value"
          :value="tab.value"
        >
          <v-icon start size="18">{{ tab.icon }}</v-icon>
          {{ tab.label }}
          <v-badge
            v-if="tab.value !== 'all'"
            :content="requirements.filter(r => r.framework === tab.value).length"
            color="grey-lighten-1"
            inline
            class="ml-1"
          />
        </v-tab>
      </v-tabs>
    </v-card>

    <!-- フィルタバー -->
    <v-row class="mb-4" dense>
      <v-col cols="12" sm="3">
        <v-select
          v-model="statusFilter"
          :items="complianceStatuses"
          item-title="title"
          item-value="value"
          label="準拠状況"
          clearable
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-filter-variant"
        />
      </v-col>
      <v-col cols="12" sm="5">
        <v-text-field
          v-model="searchQuery"
          label="検索（ID / タイトル / カテゴリ / 担当者）"
          density="compact"
          variant="outlined"
          clearable
          prepend-inner-icon="mdi-magnify"
        />
      </v-col>
      <v-col cols="12" sm="2" class="d-flex align-center">
        <v-chip color="primary" variant="tonal" size="small">
          {{ filteredRequirements.length }} 件
        </v-chip>
      </v-col>
      <v-col cols="12" sm="2" class="d-flex align-center justify-end">
        <v-btn
          variant="text"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="complianceStore.loading"
          @click="complianceStore.fetchRequirements()"
        >
          更新
        </v-btn>
      </v-col>
    </v-row>

    <!-- 要件一覧テーブル -->
    <v-card elevation="2">
      <v-data-table
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        v-model:sort-by="sortBy"
        :headers="headers"
        :items="filteredRequirements"
        :loading="complianceStore.loading"
        hover
        class="compliance-table"
        :items-per-page-options="[5, 10, 25, 50]"
        @click:row="onRowClick"
      >
        <template #item.req_id="{ item }">
          <span class="font-weight-medium text-primary">{{ item.req_id }}</span>
        </template>

        <template #item.category="{ item }">
          <v-chip size="small" variant="outlined" label>
            {{ item.category }}
          </v-chip>
        </template>

        <template #item.compliance_status="{ item }">
          <v-chip
            :color="statusColor(item.compliance_status)"
            size="small"
            variant="tonal"
            label
            :prepend-icon="statusIcon(item.compliance_status)"
          >
            {{ statusLabel(item.compliance_status) }}
          </v-chip>
        </template>

        <template #item.is_mandatory="{ item }">
          <v-chip
            :color="item.is_mandatory ? 'red' : 'blue-grey'"
            size="small"
            variant="tonal"
            label
          >
            {{ item.is_mandatory ? '必須' : '任意' }}
          </v-chip>
        </template>

        <template #item.owner="{ item }">
          <span v-if="!smAndDown">{{ item.owner || '-' }}</span>
        </template>

        <template #item.last_assessed_at="{ item }">
          <span v-if="!smAndDown">{{ formatDate(item.last_assessed_at) }}</span>
        </template>

        <template #no-data>
          <div class="text-center pa-6 text-medium-emphasis">
            <v-icon size="48" class="mb-2">mdi-file-search-outline</v-icon>
            <div>該当する要件がありません</div>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- 要件詳細ダイアログ -->
    <v-dialog v-model="showDetailDialog" max-width="750">
      <v-card v-if="selectedRequirement">
        <v-card-title class="d-flex align-center pa-4">
          <v-chip
            :color="statusColor(selectedRequirement.compliance_status)"
            size="small"
            label
            :prepend-icon="statusIcon(selectedRequirement.compliance_status)"
            class="mr-3"
          >
            {{ statusLabel(selectedRequirement.compliance_status) }}
          </v-chip>
          {{ selectedRequirement.req_id }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showDetailDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <h3 class="text-h6 mb-3">{{ selectedRequirement.title }}</h3>
          <p class="text-body-2 text-medium-emphasis mb-4">
            {{ selectedRequirement.description }}
          </p>

          <v-row dense>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">フレームワーク</div>
              <v-chip size="small" variant="outlined" label class="mt-1">
                {{ selectedRequirement.framework }}
              </v-chip>
            </v-col>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">カテゴリ</div>
              <v-chip size="small" variant="outlined" label class="mt-1">
                {{ selectedRequirement.category }}
              </v-chip>
            </v-col>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">必須/任意</div>
              <v-chip
                :color="selectedRequirement.is_mandatory ? 'red' : 'blue-grey'"
                size="small"
                variant="tonal"
                label
                class="mt-1"
              >
                {{ selectedRequirement.is_mandatory ? '必須' : '任意' }}
              </v-chip>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <v-row dense>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">条文参照</div>
              <div class="text-body-2 mt-1 font-weight-medium">
                {{ selectedRequirement.article_ref || '-' }}
              </div>
            </v-col>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">評価頻度</div>
              <div class="text-body-2 mt-1 font-weight-medium">
                {{ selectedRequirement.frequency || '-' }}
              </div>
            </v-col>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">担当者</div>
              <div class="text-body-2 mt-1 font-weight-medium">
                {{ selectedRequirement.owner || '-' }}
              </div>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <v-row dense>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis">最終評価日</div>
              <div class="text-body-2 mt-1">
                {{ formatDate(selectedRequirement.last_assessed_at) }}
              </div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis">準拠状況</div>
              <v-chip
                :color="statusColor(selectedRequirement.compliance_status)"
                size="small"
                variant="tonal"
                label
                :prepend-icon="statusIcon(selectedRequirement.compliance_status)"
                class="mt-1"
              >
                {{ statusLabel(selectedRequirement.compliance_status) }}
              </v-chip>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-btn
            color="primary"
            variant="tonal"
            prepend-icon="mdi-pencil"
            @click="showDetailDialog = false; openStatusUpdate(selectedRequirement!)"
          >
            状況を更新
          </v-btn>
          <v-spacer />
          <v-btn variant="text" @click="showDetailDialog = false">閉じる</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 準拠状況更新ダイアログ -->
    <v-dialog v-model="showStatusUpdateDialog" max-width="450" persistent>
      <v-card v-if="selectedRequirement">
        <v-card-title class="d-flex align-center pa-4">
          <v-icon class="mr-2" color="primary">mdi-pencil-circle</v-icon>
          準拠状況の更新
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showStatusUpdateDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <div class="text-subtitle-2 mb-2">{{ selectedRequirement.req_id }}</div>
          <div class="text-body-2 text-medium-emphasis mb-4">{{ selectedRequirement.title }}</div>

          <v-radio-group v-model="updatingStatus" class="mt-2">
            <v-radio value="compliant" color="green">
              <template #label>
                <v-icon color="green" size="18" class="mr-2">mdi-check-circle</v-icon>
                準拠
              </template>
            </v-radio>
            <v-radio value="partial" color="orange">
              <template #label>
                <v-icon color="orange" size="18" class="mr-2">mdi-alert-circle</v-icon>
                一部準拠
              </template>
            </v-radio>
            <v-radio value="non_compliant" color="red">
              <template #label>
                <v-icon color="red" size="18" class="mr-2">mdi-close-circle</v-icon>
                非準拠
              </template>
            </v-radio>
            <v-radio value="unknown" color="grey">
              <template #label>
                <v-icon color="grey" size="18" class="mr-2">mdi-help-circle</v-icon>
                未評価
              </template>
            </v-radio>
          </v-radio-group>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="showStatusUpdateDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-check"
            :loading="complianceStore.loading"
            @click="handleStatusUpdate"
          >
            更新
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.compliance-table :deep(tbody tr) {
  cursor: pointer;
}
</style>
