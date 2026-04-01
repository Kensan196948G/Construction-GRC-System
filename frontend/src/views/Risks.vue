<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRisksStore } from '@/store/risks'
import type { Risk } from '@/store/risks'


const risksStore = useRisksStore()

// フィルタ状態
const categoryFilter = ref<string | null>(null)
const statusFilter = ref<string | null>(null)
const searchQuery = ref('')

// ダイアログ状態
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const selectedRisk = ref<Risk | null>(null)

// テーブル
const itemsPerPage = ref(10)
const page = ref(1)
const sortBy = ref<{ key: string; order: 'asc' | 'desc' }[]>([])

// カテゴリ・ステータス定義
const categories = [
  { title: 'IT', value: 'IT' },
  { title: 'Physical', value: 'Physical' },
  { title: 'Legal', value: 'Legal' },
  { title: 'Construction', value: 'Construction' },
  { title: 'Financial', value: 'Financial' },
  { title: 'Operational', value: 'Operational' },
]

const statuses = [
  { title: 'open', value: 'open' },
  { title: 'in_progress', value: 'in_progress' },
  { title: 'closed', value: 'closed' },
  { title: 'accepted', value: 'accepted' },
]

const treatmentStrategies = [
  { title: '軽減 (mitigate)', value: 'mitigate' },
  { title: '回避 (avoid)', value: 'avoid' },
  { title: '移転 (transfer)', value: 'transfer' },
  { title: '受容 (accept)', value: 'accept' },
]

// テーブルヘッダ
const headers = [
  { title: 'リスクID', key: 'risk_id', sortable: true, width: '120px' },
  { title: 'タイトル', key: 'title', sortable: true },
  { title: 'カテゴリ', key: 'category', sortable: true, width: '120px' },
  { title: 'リスクレベル', key: 'risk_level', sortable: true, width: '130px' },
  { title: 'ステータス', key: 'status', sortable: true, width: '120px' },
  { title: '担当者', key: 'owner', sortable: true, width: '120px' },
  { title: '更新日', key: 'updated_at', sortable: true, width: '120px' },
]

// 新規リスクフォーム
const newRisk = ref({
  risk_id: '',
  title: '',
  description: '',
  category: '' as string,
  likelihood: 3,
  impact: 3,
  treatment_strategy: 'mitigate' as string,
  target_date: '',
  owner: '',
})

// モックデータ
const mockRisks: Risk[] = [
  { risk_id: 'RISK-IT-001', title: 'ランサムウェア攻撃による業務停止', description: '建設プロジェクト管理システムがランサムウェアに感染し、工程管理データが暗号化されるリスク。復旧に数日を要し、工期に重大な影響を与える可能性がある。', category: 'IT', likelihood: 4, impact: 5, risk_level: 'CRITICAL', status: 'open', owner: '田中太郎', created_at: '2026-01-15' },
  { risk_id: 'RISK-IT-002', title: 'クラウドサービス障害', description: 'AWS/Azure等のクラウド基盤障害により、図面管理システムや工程管理ツールが利用不能になるリスク。', category: 'IT', likelihood: 3, impact: 4, risk_level: 'HIGH', status: 'in_progress', owner: '鈴木一郎', created_at: '2026-01-20' },
  { risk_id: 'RISK-IT-003', title: 'BIM データ不正アクセス', description: '建築情報モデリング（BIM）データへの不正アクセスにより、設計情報が漏洩するリスク。', category: 'IT', likelihood: 3, impact: 4, risk_level: 'HIGH', status: 'in_progress', owner: '佐藤花子', created_at: '2026-02-01' },
  { risk_id: 'RISK-PHY-001', title: '建設現場への不正侵入', description: '夜間・休日に建設現場への不正侵入が発生し、資材盗難や破壊行為が行われるリスク。', category: 'Physical', likelihood: 3, impact: 3, risk_level: 'MEDIUM', status: 'in_progress', owner: '高橋健一', created_at: '2026-02-10' },
  { risk_id: 'RISK-PHY-002', title: '現場サーバールーム浸水', description: '現場事務所のサーバールームが豪雨・台風により浸水し、システムが停止するリスク。', category: 'Physical', likelihood: 2, impact: 4, risk_level: 'MEDIUM', status: 'open', owner: '伊藤美咲', created_at: '2026-02-15' },
  { risk_id: 'RISK-LEG-001', title: '建設業法違反（一括下請負）', description: '元請業者が実質的に全ての施工を下請に任せる一括下請負が発覚するリスク。行政処分の対象となる。', category: 'Legal', likelihood: 2, impact: 5, risk_level: 'HIGH', status: 'open', owner: '渡辺法務', created_at: '2026-02-20' },
  { risk_id: 'RISK-LEG-002', title: '労安法違反（安全管理体制不備）', description: '建設現場における安全管理者未配置、安全衛生教育未実施等の労働安全衛生法違反リスク。', category: 'Legal', likelihood: 3, impact: 4, risk_level: 'HIGH', status: 'in_progress', owner: '中村安全', created_at: '2026-03-01' },
  { risk_id: 'RISK-CON-001', title: '基礎工事の地盤沈下', description: '地質調査の不備により、基礎工事後に地盤沈下が発生し、構造物の安全性に影響するリスク。', category: 'Construction', likelihood: 2, impact: 5, risk_level: 'HIGH', status: 'open', owner: '山田建設', created_at: '2026-03-05' },
  { risk_id: 'RISK-CON-002', title: '足場崩壊事故', description: '高所作業用足場の設置不良・老朽化により崩壊事故が発生するリスク。人命に関わる重大事故となる可能性。', category: 'Construction', likelihood: 3, impact: 5, risk_level: 'CRITICAL', status: 'open', owner: '小林現場', created_at: '2026-03-10' },
  { risk_id: 'RISK-FIN-001', title: '資材価格高騰による予算超過', description: '鋼材・木材等の建設資材価格が急騰し、プロジェクト予算を大幅に超過するリスク。', category: 'Financial', likelihood: 4, impact: 4, risk_level: 'CRITICAL', status: 'in_progress', owner: '加藤経理', created_at: '2026-03-12' },
  { risk_id: 'RISK-FIN-002', title: '下請業者の倒産', description: '主要下請業者が経営破綻し、工事の継続が困難になるリスク。代替業者の確保に時間を要する。', category: 'Financial', likelihood: 2, impact: 4, risk_level: 'MEDIUM', status: 'accepted', owner: '松本調達', created_at: '2026-03-15' },
  { risk_id: 'RISK-OPS-001', title: '熟練工の人材不足', description: '建設業界の高齢化に伴い、熟練工が確保できず工期遅延・品質低下が発生するリスク。', category: 'Operational', likelihood: 4, impact: 3, risk_level: 'HIGH', status: 'in_progress', owner: '木村人事', created_at: '2026-03-18' },
  { risk_id: 'RISK-OPS-002', title: 'コミュニケーション不全による手戻り', description: '設計・施工・監理間の情報共有不足により、設計変更の伝達漏れ等で手戻り工事が発生するリスク。', category: 'Operational', likelihood: 3, impact: 3, risk_level: 'MEDIUM', status: 'in_progress', owner: '林プロジェクト', created_at: '2026-03-20' },
  { risk_id: 'RISK-IT-004', title: 'IoTセンサー改ざん', description: '建設現場のIoTセンサー（振動・温度・傾斜計）のデータが改ざんされ、安全判定を誤るリスク。', category: 'IT', likelihood: 2, impact: 4, risk_level: 'MEDIUM', status: 'open', owner: '田中太郎', created_at: '2026-03-22' },
]



// フィルタ済みリスク
const filteredRisks = computed(() => {
  let result = risksStore.risks.length > 0 ? risksStore.risks : mockRisks
  if (categoryFilter.value) {
    result = result.filter((r) => r.category === categoryFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter((r) => r.status === statusFilter.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (r) =>
        r.risk_id.toLowerCase().includes(q) ||
        r.title.toLowerCase().includes(q) ||
        r.owner.toLowerCase().includes(q)
    )
  }
  return result
})

// リスクレベル色
const riskLevelColor = (level: string): string => {
  const colors: Record<string, string> = {
    CRITICAL: 'red',
    HIGH: 'orange',
    MEDIUM: 'yellow',
    LOW: 'green',
  }
  return colors[level] || 'grey'
}

const riskLevelTextColor = (level: string): string => {
  return level === 'MEDIUM' ? 'black' : 'white'
}

// ステータス色
const statusColor = (status: string): string => {
  const colors: Record<string, string> = {
    open: 'blue',
    in_progress: 'orange',
    closed: 'green',
    accepted: 'grey',
  }
  return colors[status] || 'grey'
}

const statusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    open: '未対応',
    in_progress: '対応中',
    closed: '完了',
    accepted: '受容',
  }
  return labels[status] || status
}

// 日付フォーマット
const formatDate = (date: string): string => {
  if (!date) return '-'
  return date.substring(0, 10)
}

// 行クリックで詳細表示
const onRowClick = (_event: Event, row: { item: Risk }) => {
  selectedRisk.value = row.item
  showDetailDialog.value = true
}

// 新規リスク登録
const handleCreate = async () => {
  try {
    await risksStore.createRisk({
      title: newRisk.value.title,
      description: newRisk.value.description,
      category: newRisk.value.category,
      likelihood: newRisk.value.likelihood,
      impact: newRisk.value.impact,
      status: 'open',
      owner: newRisk.value.owner,
    })
    showCreateDialog.value = false
    resetForm()
  } catch {
    // エラーはストアで処理
  }
}

const resetForm = () => {
  newRisk.value = {
    risk_id: '',
    title: '',
    description: '',
    category: '',
    likelihood: 3,
    impact: 3,
    treatment_strategy: 'mitigate',
    target_date: '',
    owner: '',
  }
}

// テーブルデータ読み込み（サーバサイド対応）
const loadItems = async (_options: { page: number; itemsPerPage: number; sortBy: { key: string; order: string }[] }) => {
  try {
    await risksStore.fetchRisks({
      category: categoryFilter.value || undefined,
      status: statusFilter.value || undefined,
    })
  } catch {
    // フォールバックはmockRisksを使用
  }
}

// フィルタ変更時にリロード
watch([categoryFilter, statusFilter], () => {
  page.value = 1
})

onMounted(() => {
  risksStore.fetchRisks()
})
</script>

<template>
  <v-container fluid>
    <!-- ヘッダ -->
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4">リスク管理</h1>
      <v-spacer />
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="showCreateDialog = true"
      >
        新規リスク登録
      </v-btn>
    </div>

    <!-- フィルタバー -->
    <v-row class="mb-4" dense>
      <v-col cols="12" sm="3">
        <v-select
          v-model="categoryFilter"
          :items="categories"
          item-title="title"
          item-value="value"
          label="カテゴリ"
          clearable
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-filter-variant"
        />
      </v-col>
      <v-col cols="12" sm="3">
        <v-select
          v-model="statusFilter"
          :items="statuses"
          item-title="title"
          item-value="value"
          label="ステータス"
          clearable
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-filter-variant"
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field
          v-model="searchQuery"
          label="検索（ID / タイトル / 担当者）"
          density="compact"
          variant="outlined"
          clearable
          prepend-inner-icon="mdi-magnify"
        />
      </v-col>
      <v-col cols="12" sm="2" class="d-flex align-center">
        <v-chip color="primary" variant="tonal" size="small">
          {{ filteredRisks.length }} 件
        </v-chip>
      </v-col>
    </v-row>

    <!-- リスク一覧テーブル -->
    <v-card elevation="2">
      <v-data-table-server
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        v-model:sort-by="sortBy"
        :headers="headers"
        :items="filteredRisks"
        :items-length="filteredRisks.length"
        :loading="risksStore.loading"
        hover
        @update:options="loadItems"
        @click:row="onRowClick"
        class="risk-table"
      >
        <template #item.risk_id="{ item }">
          <span class="font-weight-medium text-primary">{{ item.risk_id }}</span>
        </template>

        <template #item.category="{ item }">
          <v-chip size="small" variant="outlined" label>
            {{ item.category }}
          </v-chip>
        </template>

        <template #item.risk_level="{ item }">
          <v-chip
            :color="riskLevelColor(item.risk_level)"
            :text-color="riskLevelTextColor(item.risk_level)"
            size="small"
            label
          >
            {{ item.risk_level }}
          </v-chip>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="statusColor(item.status)"
            size="small"
            variant="tonal"
            label
          >
            {{ statusLabel(item.status) }}
          </v-chip>
        </template>

        <template #item.updated_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
      </v-data-table-server>
    </v-card>

    <!-- 新規リスク登録ダイアログ -->
    <v-dialog v-model="showCreateDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="d-flex align-center pa-4">
          <v-icon class="mr-2" color="primary">mdi-plus-circle</v-icon>
          新規リスク登録
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showCreateDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <v-form>
            <v-row dense>
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model="newRisk.risk_id"
                  label="リスクID"
                  placeholder="RISK-IT-005"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              <v-col cols="12" sm="8">
                <v-text-field
                  v-model="newRisk.title"
                  label="タイトル"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || 'タイトルは必須です']"
                />
              </v-col>
            </v-row>

            <v-textarea
              v-model="newRisk.description"
              label="説明"
              variant="outlined"
              rows="3"
              class="mt-2"
              density="compact"
            />

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newRisk.category"
                  :items="categories"
                  item-title="title"
                  item-value="value"
                  label="カテゴリ"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || 'カテゴリは必須です']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="newRisk.owner"
                  label="担当者"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <div class="text-caption mb-1">発生可能性: {{ newRisk.likelihood }}</div>
                <v-slider
                  v-model="newRisk.likelihood"
                  :min="1"
                  :max="5"
                  :step="1"
                  thumb-label
                  color="primary"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <div class="text-caption mb-1">影響度: {{ newRisk.impact }}</div>
                <v-slider
                  v-model="newRisk.impact"
                  :min="1"
                  :max="5"
                  :step="1"
                  thumb-label
                  color="primary"
                />
              </v-col>
            </v-row>

            <v-row dense class="mt-1">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="newRisk.treatment_strategy"
                  :items="treatmentStrategies"
                  item-title="title"
                  item-value="value"
                  label="対応戦略"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="newRisk.target_date"
                  label="目標日"
                  type="date"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>

            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mt-3"
            >
              リスクスコア（発生可能性 x 影響度）: <strong>{{ newRisk.likelihood * newRisk.impact }}</strong>
            </v-alert>
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
            @click="handleCreate"
          >
            登録
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- リスク詳細ダイアログ -->
    <v-dialog v-model="showDetailDialog" max-width="700">
      <v-card v-if="selectedRisk">
        <v-card-title class="d-flex align-center pa-4">
          <v-chip
            :color="riskLevelColor(selectedRisk.risk_level)"
            size="small"
            label
            class="mr-3"
          >
            {{ selectedRisk.risk_level }}
          </v-chip>
          {{ selectedRisk.risk_id }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showDetailDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <h3 class="text-h6 mb-3">{{ selectedRisk.title }}</h3>
          <p class="text-body-2 text-medium-emphasis mb-4">{{ selectedRisk.description }}</p>

          <v-row dense>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">カテゴリ</div>
              <v-chip size="small" variant="outlined" label class="mt-1">
                {{ selectedRisk.category }}
              </v-chip>
            </v-col>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">ステータス</div>
              <v-chip
                :color="statusColor(selectedRisk.status)"
                size="small"
                variant="tonal"
                label
                class="mt-1"
              >
                {{ statusLabel(selectedRisk.status) }}
              </v-chip>
            </v-col>
            <v-col cols="6" sm="4">
              <div class="text-caption text-medium-emphasis">担当者</div>
              <div class="text-body-2 mt-1 font-weight-medium">{{ selectedRisk.owner || '-' }}</div>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <v-row dense>
            <v-col cols="4">
              <div class="text-caption text-medium-emphasis">発生可能性</div>
              <div class="text-h5 font-weight-bold mt-1">{{ selectedRisk.likelihood }}</div>
              <v-progress-linear
                :model-value="selectedRisk.likelihood * 20"
                color="blue"
                height="6"
                rounded
                class="mt-1"
              />
            </v-col>
            <v-col cols="4">
              <div class="text-caption text-medium-emphasis">影響度</div>
              <div class="text-h5 font-weight-bold mt-1">{{ selectedRisk.impact }}</div>
              <v-progress-linear
                :model-value="selectedRisk.impact * 20"
                color="orange"
                height="6"
                rounded
                class="mt-1"
              />
            </v-col>
            <v-col cols="4">
              <div class="text-caption text-medium-emphasis">リスクスコア</div>
              <div class="text-h5 font-weight-bold mt-1">{{ selectedRisk.likelihood * selectedRisk.impact }}</div>
              <v-progress-linear
                :model-value="selectedRisk.likelihood * selectedRisk.impact * 4"
                :color="riskLevelColor(selectedRisk.risk_level)"
                height="6"
                rounded
                class="mt-1"
              />
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <v-row dense>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis">登録日</div>
              <div class="text-body-2 mt-1">{{ formatDate(selectedRisk.created_at) }}</div>
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="showDetailDialog = false">閉じる</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.risk-table :deep(tbody tr) {
  cursor: pointer;
}
</style>
