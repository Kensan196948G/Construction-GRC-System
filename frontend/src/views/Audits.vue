<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAuditsStore } from '@/store/audits'
import type { Audit, AuditFinding } from '@/types'

const auditsStore = useAuditsStore()

// フィルタ状態
const statusFilter = ref<string | null>(null)
const departmentFilter = ref<string | null>(null)
const searchQuery = ref('')

// ダイアログ状態
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showFindingDialog = ref(false)
const selectedAudit = ref<Audit | null>(null)
const selectedFindings = ref<AuditFinding[]>([])

// テーブル
const itemsPerPage = ref(10)
const page = ref(1)

// ステータス定義
const auditStatuses = [
  { title: '計画中', value: '計画中' },
  { title: '実施中', value: '実施中' },
  { title: '完了', value: '完了' },
  { title: 'キャンセル', value: 'キャンセル' },
]

const departments = [
  { title: '情報システム部', value: '情報システム部' },
  { title: '建設事業部', value: '建設事業部' },
  { title: '安全管理部', value: '安全管理部' },
  { title: '品質管理部', value: '品質管理部' },
  { title: '総務部', value: '総務部' },
  { title: '法務部', value: '法務部' },
  { title: '経理部', value: '経理部' },
  { title: '全社', value: '全社' },
]

const auditTypes = [
  { title: '内部監査', value: '内部監査' },
  { title: '外部監査', value: '外部監査' },
  { title: 'サーベイランス監査', value: 'サーベイランス監査' },
  { title: 'フォローアップ監査', value: 'フォローアップ監査' },
]

const findingTypes = [
  { title: '重大な不適合', value: 'major_nc' },
  { title: '軽微な不適合', value: 'minor_nc' },
  { title: '観察事項', value: 'observation' },
  { title: '優良事例', value: 'good_practice' },
]

const severityOptions = [
  { title: '高', value: 'high' },
  { title: '中', value: 'medium' },
  { title: '低', value: 'low' },
]

const capStatuses = [
  { title: '未着手', value: 'not_started' },
  { title: '対応中', value: 'in_progress' },
  { title: '検証待ち', value: 'pending_verification' },
  { title: '完了', value: 'closed' },
]

// テーブルヘッダ
const headers = [
  { title: '監査ID', key: 'audit_id', sortable: true, width: '130px' },
  { title: '監査名', key: 'title', sortable: true },
  { title: '対象部門', key: 'target_department', sortable: true, width: '140px' },
  { title: 'ステータス', key: 'status', sortable: true, width: '120px' },
  { title: '実施予定日', key: 'planned_start', sortable: true, width: '130px' },
  { title: '所見数', key: 'findings_count', sortable: true, width: '100px' },
  { title: '操作', key: 'actions', sortable: false, width: '80px' },
]

const findingHeaders = [
  { title: '所見ID', key: 'finding_id', width: '120px' },
  { title: '種別', key: 'finding_type', width: '130px' },
  { title: 'タイトル', key: 'title' },
  { title: '重大度', key: 'severity', width: '90px' },
  { title: 'CAP状態', key: 'cap_status', width: '120px' },
  { title: '期限', key: 'due_date', width: '120px' },
]

// 新規監査フォーム
const newAudit = ref({
  title: '',
  audit_type: '内部監査',
  scope: '',
  status: '計画中',
  target_department: '',
  lead_auditor: '',
  planned_start: '',
  planned_end: '',
  actual_start: null as string | null,
  actual_end: null as string | null,
})

// 新規所見フォーム
const newFinding = ref({
  finding_type: 'minor_nc',
  title: '',
  description: '',
  severity: 'medium',
  corrective_action: '',
  cap_status: 'not_started',
  due_date: null as string | null,
  closed_at: null as string | null,
})

// フォームバリデーション
const createFormValid = ref(false)
const findingFormValid = ref(false)

// モックデータ
const mockAudits: Audit[] = [
  {
    id: '1', audit_id: 'AUD-2026-001', title: '情報セキュリティ内部監査',
    audit_type: '内部監査', scope: 'ISMS全般', status: '完了',
    target_department: '情報システム部', lead_auditor: '佐藤太郎',
    planned_start: '2026-01-10', planned_end: '2026-01-20',
    actual_start: '2026-01-10', actual_end: '2026-01-18', findings_count: 3,
  },
  {
    id: '2', audit_id: 'AUD-2026-002', title: '安全衛生監査',
    audit_type: '内部監査', scope: '現場安全管理体制', status: '完了',
    target_department: '安全管理部', lead_auditor: '鈴木一郎',
    planned_start: '2026-02-05', planned_end: '2026-02-15',
    actual_start: '2026-02-05', actual_end: '2026-02-14', findings_count: 5,
  },
  {
    id: '3', audit_id: 'AUD-2026-003', title: 'コンプライアンス監査',
    audit_type: '内部監査', scope: '建設業法・品確法準拠', status: '実施中',
    target_department: '法務部', lead_auditor: '高橋健一',
    planned_start: '2026-03-15', planned_end: '2026-03-30',
    actual_start: '2026-03-15', actual_end: null, findings_count: 2,
  },
  {
    id: '4', audit_id: 'AUD-2026-004', title: '環境マネジメント監査',
    audit_type: 'サーベイランス監査', scope: '環境法規準拠状況', status: '計画中',
    target_department: '品質管理部', lead_auditor: null,
    planned_start: '2026-04-15', planned_end: '2026-04-25',
    actual_start: null, actual_end: null, findings_count: 0,
  },
  {
    id: '5', audit_id: 'AUD-2026-005', title: '品質マネジメント監査',
    audit_type: '内部監査', scope: 'QMS全般', status: '計画中',
    target_department: '品質管理部', lead_auditor: null,
    planned_start: '2026-05-20', planned_end: '2026-06-05',
    actual_start: null, actual_end: null, findings_count: 0,
  },
  {
    id: '6', audit_id: 'AUD-2026-006', title: 'ISO27001サーベイランス監査',
    audit_type: '外部監査', scope: 'ISMS認証範囲全体', status: '計画中',
    target_department: '全社', lead_auditor: null,
    planned_start: '2026-06-10', planned_end: '2026-06-15',
    actual_start: null, actual_end: null, findings_count: 0,
  },
]

const mockFindings: Record<string, AuditFinding[]> = {
  '1': [
    { id: '1', finding_id: 'FND-001', finding_type: 'minor_nc', title: 'アクセスログの定期レビュー未実施', description: '特権アカウントのアクセスログレビューが3ヶ月間実施されていない。', severity: 'medium', corrective_action: '月次レビュー手順を策定し、担当者を任命する。', cap_status: 'closed', due_date: '2026-02-15', closed_at: '2026-02-10' },
    { id: '2', finding_id: 'FND-002', finding_type: 'observation', title: 'パスワードポリシー強化の推奨', description: 'パスワード最小長が8文字だが、12文字以上を推奨。', severity: 'low', corrective_action: 'パスワードポリシーの見直しを検討する。', cap_status: 'in_progress', due_date: '2026-03-31', closed_at: null },
    { id: '3', finding_id: 'FND-003', finding_type: 'good_practice', title: 'インシデント対応訓練の定期実施', description: '四半期ごとのインシデント対応訓練が確実に実施されており、記録も整備されている。', severity: 'low', corrective_action: '', cap_status: 'closed', due_date: null, closed_at: null },
  ],
  '2': [
    { id: '4', finding_id: 'FND-004', finding_type: 'major_nc', title: '安全帯使用の不徹底', description: '高所作業（5m以上）において安全帯の未使用が2件確認された。', severity: 'high', corrective_action: '全現場への安全帯使用徹底の再教育を実施する。', cap_status: 'in_progress', due_date: '2026-03-10', closed_at: null },
    { id: '5', finding_id: 'FND-005', finding_type: 'minor_nc', title: 'KY活動記録の不備', description: '朝礼時のKY活動記録が2日分欠落している。', severity: 'medium', corrective_action: '記録管理のダブルチェック体制を構築する。', cap_status: 'closed', due_date: '2026-03-01', closed_at: '2026-02-28' },
    { id: '6', finding_id: 'FND-006', finding_type: 'minor_nc', title: '新規入場者教育の一部省略', description: '新規入場者教育のうち、環境配慮項目が省略されていた。', severity: 'medium', corrective_action: '教育チェックリストを改訂し、必須項目を明確化する。', cap_status: 'pending_verification', due_date: '2026-03-15', closed_at: null },
    { id: '7', finding_id: 'FND-007', finding_type: 'observation', title: '作業手順書の現場掲示', description: '一部の作業手順書が現場に掲示されていない。', severity: 'low', corrective_action: '掲示場所を再確認し、不足分を掲示する。', cap_status: 'closed', due_date: '2026-02-28', closed_at: '2026-02-25' },
    { id: '8', finding_id: 'FND-008', finding_type: 'good_practice', title: '安全パトロールの頻度向上', description: '週次から日次パトロールに変更し、安全意識の向上が見られる。', severity: 'low', corrective_action: '', cap_status: 'closed', due_date: null, closed_at: null },
  ],
  '3': [
    { id: '9', finding_id: 'FND-009', finding_type: 'minor_nc', title: '下請契約書の記載不備', description: '一部の下請契約書に工期の明記がされていない。', severity: 'medium', corrective_action: '契約書テンプレートの改訂と既存契約の補正を行う。', cap_status: 'not_started', due_date: '2026-04-15', closed_at: null },
    { id: '10', finding_id: 'FND-010', finding_type: 'observation', title: '技術者配置の適正確認', description: '主任技術者の専任状況について、一部確認が困難。', severity: 'low', corrective_action: '技術者配置管理台帳の整備を検討する。', cap_status: 'not_started', due_date: '2026-04-30', closed_at: null },
  ],
}

// 算出プロパティ
const allAudits = computed(() => {
  return auditsStore.audits.length > 0 ? auditsStore.audits : mockAudits
})

const filteredAudits = computed(() => {
  let result = allAudits.value
  if (statusFilter.value) {
    result = result.filter((a) => a.status === statusFilter.value)
  }
  if (departmentFilter.value) {
    result = result.filter((a) => a.target_department === departmentFilter.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (a) =>
        a.audit_id.toLowerCase().includes(q) ||
        a.title.toLowerCase().includes(q) ||
        a.target_department.toLowerCase().includes(q)
    )
  }
  return result
})

const summaryCards = computed(() => {
  const all = allAudits.value
  return {
    completed: all.filter((a) => a.status === '完了').length,
    inProgress: all.filter((a) => a.status === '実施中').length,
    planned: all.filter((a) => a.status === '計画中').length,
    total: all.length,
  }
})

// ステータス色
const statusColor = (status: string): string => {
  const colors: Record<string, string> = {
    '完了': 'success',
    '実施中': 'info',
    '計画中': 'grey',
    'キャンセル': 'error',
  }
  return colors[status] || 'grey'
}

const statusIcon = (status: string): string => {
  const icons: Record<string, string> = {
    '完了': 'mdi-check-circle',
    '実施中': 'mdi-progress-clock',
    '計画中': 'mdi-calendar-clock',
    'キャンセル': 'mdi-cancel',
  }
  return icons[status] || 'mdi-help-circle'
}

// 所見種別ラベル・色
const findingTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    major_nc: '重大な不適合',
    minor_nc: '軽微な不適合',
    observation: '観察事項',
    good_practice: '優良事例',
  }
  return labels[type] || type
}

const findingTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    major_nc: 'red',
    minor_nc: 'orange',
    observation: 'blue',
    good_practice: 'green',
  }
  return colors[type] || 'grey'
}

const severityColor = (severity: string): string => {
  const colors: Record<string, string> = {
    high: 'red',
    medium: 'orange',
    low: 'green',
  }
  return colors[severity] || 'grey'
}

const severityLabel = (severity: string): string => {
  const labels: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低',
  }
  return labels[severity] || severity
}

const capStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    not_started: '未着手',
    in_progress: '対応中',
    pending_verification: '検証待ち',
    closed: '完了',
  }
  return labels[status] || status
}

const capStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    not_started: 'grey',
    in_progress: 'blue',
    pending_verification: 'orange',
    closed: 'green',
  }
  return colors[status] || 'grey'
}

// 日付フォーマット
const formatDate = (date: string | null | undefined): string => {
  if (!date) return '-'
  return date.substring(0, 10)
}

// 行クリックで詳細表示
const openDetail = async (audit: Audit) => {
  selectedAudit.value = audit
  // APIからの所見取得を試行、失敗時はモックデータ使用
  try {
    await auditsStore.fetchFindings(audit.id)
    selectedFindings.value = auditsStore.findings.length > 0
      ? auditsStore.findings
      : mockFindings[audit.id] || []
  } catch {
    selectedFindings.value = mockFindings[audit.id] || []
  }
  showDetailDialog.value = true
}

const onRowClick = (_event: Event, row: { item: Audit }) => {
  openDetail(row.item)
}

// 新規監査登録
const handleCreateAudit = async () => {
  try {
    await auditsStore.addAudit({
      title: newAudit.value.title,
      audit_type: newAudit.value.audit_type,
      scope: newAudit.value.scope,
      status: newAudit.value.status,
      target_department: newAudit.value.target_department,
      lead_auditor: newAudit.value.lead_auditor || null,
      planned_start: newAudit.value.planned_start,
      planned_end: newAudit.value.planned_end,
      actual_start: newAudit.value.actual_start,
      actual_end: newAudit.value.actual_end,
    })
    showCreateDialog.value = false
    resetAuditForm()
  } catch {
    // エラーはストアで処理
  }
}

const resetAuditForm = () => {
  newAudit.value = {
    title: '',
    audit_type: '内部監査',
    scope: '',
    status: '計画中',
    target_department: '',
    lead_auditor: '',
    planned_start: '',
    planned_end: '',
    actual_start: null,
    actual_end: null,
  }
}

// 所見登録ダイアログを開く
const openFindingDialog = () => {
  resetFindingForm()
  showFindingDialog.value = true
}

// 所見登録
const handleCreateFinding = async () => {
  if (!selectedAudit.value) return
  try {
    await auditsStore.addFinding(selectedAudit.value.id, {
      finding_type: newFinding.value.finding_type,
      title: newFinding.value.title,
      description: newFinding.value.description,
      severity: newFinding.value.severity,
      corrective_action: newFinding.value.corrective_action,
      cap_status: newFinding.value.cap_status,
      due_date: newFinding.value.due_date,
      closed_at: null,
    })
    // リスト更新
    selectedFindings.value = [...selectedFindings.value, ...auditsStore.findings.slice(-1)]
    showFindingDialog.value = false
    resetFindingForm()
  } catch {
    // エラーはストアで処理
  }
}

const resetFindingForm = () => {
  newFinding.value = {
    finding_type: 'minor_nc',
    title: '',
    description: '',
    severity: 'medium',
    corrective_action: '',
    cap_status: 'not_started',
    due_date: null,
    closed_at: null,
  }
}

// フィルタ変更時にページリセット
watch([statusFilter, departmentFilter], () => {
  page.value = 1
})

onMounted(() => {
  auditsStore.fetchAudits()
})
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-4">
    <!-- ヘッダ -->
    <div class="d-flex align-center mb-6">
      <div>
        <h1 class="text-h4">内部監査</h1>
        <p class="text-body-2 text-medium-emphasis mt-1">
          監査計画の管理、実施状況の追跡、所見の記録
        </p>
      </div>
      <v-spacer />
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="showCreateDialog = true"
      >
        新規監査作成
      </v-btn>
    </div>

    <!-- サマリーカード -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="success" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="40" class="mr-4">mdi-check-circle</v-icon>
            <div>
              <div class="text-h4 font-weight-bold">{{ summaryCards.completed }}</div>
              <div class="text-body-2">完了</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="info" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="40" class="mr-4">mdi-progress-clock</v-icon>
            <div>
              <div class="text-h4 font-weight-bold">{{ summaryCards.inProgress }}</div>
              <div class="text-body-2">実施中</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="grey" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="40" class="mr-4">mdi-calendar-clock</v-icon>
            <div>
              <div class="text-h4 font-weight-bold">{{ summaryCards.planned }}</div>
              <div class="text-body-2">計画中</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="primary" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="40" class="mr-4">mdi-clipboard-list</v-icon>
            <div>
              <div class="text-h4 font-weight-bold">{{ summaryCards.total }}</div>
              <div class="text-body-2">合計</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- フィルタバー -->
    <v-row class="mb-4" dense>
      <v-col cols="12" sm="3">
        <v-select
          v-model="statusFilter"
          :items="auditStatuses"
          item-title="title"
          item-value="value"
          label="ステータス"
          clearable
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-filter-variant"
        />
      </v-col>
      <v-col cols="12" sm="3">
        <v-select
          v-model="departmentFilter"
          :items="departments"
          item-title="title"
          item-value="value"
          label="対象部門"
          clearable
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-domain"
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field
          v-model="searchQuery"
          label="検索（ID / タイトル / 部門）"
          density="compact"
          variant="outlined"
          clearable
          prepend-inner-icon="mdi-magnify"
        />
      </v-col>
      <v-col cols="12" sm="2" class="d-flex align-center">
        <v-chip color="primary" variant="tonal" size="small">
          {{ filteredAudits.length }} 件
        </v-chip>
      </v-col>
    </v-row>

    <!-- ローディング -->
    <v-progress-linear
      v-if="auditsStore.loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <!-- エラー表示 -->
    <v-alert
      v-if="auditsStore.error"
      type="warning"
      variant="tonal"
      closable
      class="mb-4"
    >
      {{ auditsStore.error }}（デモデータを表示しています）
    </v-alert>

    <!-- 監査一覧テーブル -->
    <v-card elevation="2">
      <v-data-table
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        :headers="headers"
        :items="filteredAudits"
        :loading="auditsStore.loading"
        hover
        @click:row="onRowClick"
        class="audit-table"
      >
        <template #item.audit_id="{ item }">
          <span class="font-weight-medium text-primary">{{ item.audit_id }}</span>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="statusColor(item.status)"
            size="small"
            label
            :prepend-icon="statusIcon(item.status)"
          >
            {{ item.status }}
          </v-chip>
        </template>

        <template #item.planned_start="{ item }">
          {{ formatDate(item.planned_start) }}
        </template>

        <template #item.findings_count="{ item }">
          <v-chip
            :color="item.findings_count > 0 ? 'warning' : 'success'"
            size="small"
            variant="tonal"
          >
            {{ item.findings_count }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-eye"
            size="small"
            variant="text"
            @click.stop="openDetail(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <!-- 新規監査作成ダイアログ -->
    <v-dialog v-model="showCreateDialog" max-width="750" persistent>
      <v-card>
        <v-card-title class="d-flex align-center pa-4">
          <v-icon class="mr-2" color="primary">mdi-plus-circle</v-icon>
          新規監査作成
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showCreateDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-form v-model="createFormValid">
            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model="newAudit.title"
                  label="監査名 *"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '監査名は必須です']"
                />
              </v-col>
            </v-row>

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newAudit.audit_type"
                  :items="auditTypes"
                  item-title="title"
                  item-value="value"
                  label="監査種別 *"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '監査種別は必須です']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newAudit.target_department"
                  :items="departments"
                  item-title="title"
                  item-value="value"
                  label="対象部門 *"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '対象部門は必須です']"
                />
              </v-col>
            </v-row>

            <v-textarea
              v-model="newAudit.scope"
              label="監査範囲"
              variant="outlined"
              rows="2"
              class="mt-2"
              density="compact"
            />

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="newAudit.lead_auditor"
                  label="主任監査員"
                  variant="outlined"
                  density="compact"
                  prepend-inner-icon="mdi-account"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newAudit.status"
                  :items="auditStatuses"
                  item-title="title"
                  item-value="value"
                  label="ステータス"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="newAudit.planned_start"
                  label="実施予定開始日 *"
                  type="date"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '開始日は必須です']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="newAudit.planned_end"
                  label="実施予定終了日 *"
                  type="date"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '終了日は必須です']"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="showCreateDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-check"
            :disabled="!createFormValid"
            @click="handleCreateAudit"
          >
            作成
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 監査詳細ダイアログ -->
    <v-dialog v-model="showDetailDialog" max-width="900">
      <v-card v-if="selectedAudit">
        <v-card-title class="d-flex align-center pa-4">
          <v-chip
            :color="statusColor(selectedAudit.status)"
            size="small"
            label
            class="mr-3"
          >
            {{ selectedAudit.status }}
          </v-chip>
          {{ selectedAudit.audit_id }} - {{ selectedAudit.title }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showDetailDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <!-- 基本情報 -->
          <v-row dense>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">監査種別</div>
              <div class="text-body-2 mt-1 font-weight-medium">{{ selectedAudit.audit_type }}</div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">対象部門</div>
              <div class="text-body-2 mt-1 font-weight-medium">{{ selectedAudit.target_department }}</div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">主任監査員</div>
              <div class="text-body-2 mt-1 font-weight-medium">{{ selectedAudit.lead_auditor || '未定' }}</div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">所見数</div>
              <v-chip
                :color="selectedAudit.findings_count > 0 ? 'warning' : 'success'"
                size="small"
                class="mt-1"
              >
                {{ selectedAudit.findings_count }}
              </v-chip>
            </v-col>
          </v-row>

          <v-row dense class="mt-3">
            <v-col cols="12">
              <div class="text-caption text-medium-emphasis">監査範囲</div>
              <div class="text-body-2 mt-1">{{ selectedAudit.scope || '-' }}</div>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <!-- 日程情報 -->
          <v-row dense>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">予定開始日</div>
              <div class="text-body-2 mt-1">{{ formatDate(selectedAudit.planned_start) }}</div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">予定終了日</div>
              <div class="text-body-2 mt-1">{{ formatDate(selectedAudit.planned_end) }}</div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">実施開始日</div>
              <div class="text-body-2 mt-1">{{ formatDate(selectedAudit.actual_start) }}</div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-caption text-medium-emphasis">実施終了日</div>
              <div class="text-body-2 mt-1">{{ formatDate(selectedAudit.actual_end) }}</div>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <!-- 所見一覧 -->
          <div class="d-flex align-center mb-3">
            <h3 class="text-h6">所見一覧</h3>
            <v-spacer />
            <v-btn
              color="primary"
              size="small"
              variant="outlined"
              prepend-icon="mdi-plus"
              @click="openFindingDialog"
            >
              所見登録
            </v-btn>
          </div>

          <v-data-table
            v-if="selectedFindings.length > 0"
            :headers="findingHeaders"
            :items="selectedFindings"
            density="compact"
            :items-per-page="5"
          >
            <template #item.finding_type="{ item }">
              <v-chip
                :color="findingTypeColor(item.finding_type)"
                size="x-small"
                label
              >
                {{ findingTypeLabel(item.finding_type) }}
              </v-chip>
            </template>

            <template #item.severity="{ item }">
              <v-chip
                :color="severityColor(item.severity)"
                size="x-small"
                variant="tonal"
              >
                {{ severityLabel(item.severity) }}
              </v-chip>
            </template>

            <template #item.cap_status="{ item }">
              <v-chip
                :color="capStatusColor(item.cap_status)"
                size="x-small"
                variant="tonal"
              >
                {{ capStatusLabel(item.cap_status) }}
              </v-chip>
            </template>

            <template #item.due_date="{ item }">
              {{ formatDate(item.due_date) }}
            </template>
          </v-data-table>

          <v-alert
            v-else
            type="info"
            variant="tonal"
            density="compact"
          >
            この監査にはまだ所見が登録されていません。
          </v-alert>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="showDetailDialog = false">閉じる</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 所見登録ダイアログ -->
    <v-dialog v-model="showFindingDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="d-flex align-center pa-4">
          <v-icon class="mr-2" color="warning">mdi-file-find</v-icon>
          所見登録
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showFindingDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-form v-model="findingFormValid">
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newFinding.finding_type"
                  :items="findingTypes"
                  item-title="title"
                  item-value="value"
                  label="所見種別 *"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '所見種別は必須です']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newFinding.severity"
                  :items="severityOptions"
                  item-title="title"
                  item-value="value"
                  label="重大度 *"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>

            <v-text-field
              v-model="newFinding.title"
              label="所見タイトル *"
              variant="outlined"
              density="compact"
              class="mt-2"
              :rules="[v => !!v || 'タイトルは必須です']"
            />

            <v-textarea
              v-model="newFinding.description"
              label="所見内容"
              variant="outlined"
              rows="3"
              class="mt-2"
              density="compact"
            />

            <v-textarea
              v-model="newFinding.corrective_action"
              label="是正処置"
              variant="outlined"
              rows="2"
              class="mt-2"
              density="compact"
            />

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newFinding.cap_status"
                  :items="capStatuses"
                  item-title="title"
                  item-value="value"
                  label="CAP状態"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="newFinding.due_date"
                  label="是正期限"
                  type="date"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="showFindingDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-check"
            :disabled="!findingFormValid"
            @click="handleCreateFinding"
          >
            登録
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.audit-table :deep(tbody tr) {
  cursor: pointer;
}
</style>
