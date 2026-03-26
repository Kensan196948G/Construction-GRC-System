<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRisksStore } from '@/store/risks'
import type { Risk } from '@/store/risks'

const risksStore = useRisksStore()

const showDialog = ref(false)
const categoryFilter = ref<string | null>(null)
const statusFilter = ref<string | null>(null)

const categories = ['安全衛生', '品質', '環境', '法令遵守', '情報セキュリティ', '財務', 'サプライチェーン']
const statuses = ['未対応', '対応中', '対応済み', '受容']

const newRisk = ref({
  title: '',
  description: '',
  category: '',
  likelihood: 3,
  impact: 3,
  status: '未対応',
  owner: '',
})

const headers = [
  { title: 'リスクID', key: 'risk_id', sortable: true },
  { title: 'タイトル', key: 'title', sortable: true },
  { title: 'カテゴリ', key: 'category', sortable: true },
  { title: 'リスクレベル', key: 'risk_level', sortable: true },
  { title: 'ステータス', key: 'status', sortable: true },
  { title: '担当者', key: 'owner', sortable: true },
]

const riskLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    LOW: 'success',
    MEDIUM: 'warning',
    HIGH: 'orange',
    CRITICAL: 'error',
  }
  return colors[level] || 'grey'
}

const filteredRisks = computed(() => {
  let result = risksStore.risks
  if (categoryFilter.value) {
    result = result.filter((r) => r.category === categoryFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter((r) => r.status === statusFilter.value)
  }
  return result
})

const handleCreate = async () => {
  try {
    await risksStore.createRisk(newRisk.value)
    showDialog.value = false
    resetForm()
  } catch {
    // error handled in store
  }
}

const resetForm = () => {
  newRisk.value = {
    title: '',
    description: '',
    category: '',
    likelihood: 3,
    impact: 3,
    status: '未対応',
    owner: '',
  }
}

onMounted(() => {
  risksStore.fetchRisks()
})
</script>

<template>
  <v-container fluid>
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4">リスク管理</h1>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">
        新規リスク登録
      </v-btn>
    </div>

    <!-- フィルタ -->
    <v-row class="mb-4">
      <v-col cols="12" sm="4">
        <v-select
          v-model="categoryFilter"
          :items="categories"
          label="カテゴリ"
          clearable
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-select
          v-model="statusFilter"
          :items="statuses"
          label="ステータス"
          clearable
          density="compact"
          variant="outlined"
        />
      </v-col>
    </v-row>

    <!-- リスク一覧テーブル -->
    <v-card elevation="2">
      <v-data-table
        :headers="headers"
        :items="filteredRisks"
        :loading="risksStore.loading"
        hover
        items-per-page="10"
      >
        <template #item.risk_level="{ item }">
          <v-chip :color="riskLevelColor(item.risk_level)" size="small" label>
            {{ item.risk_level }}
          </v-chip>
        </template>
        <template #item.status="{ item }">
          <v-chip size="small" variant="outlined">
            {{ item.status }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>

    <!-- 新規リスク登録ダイアログ -->
    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>新規リスク登録</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newRisk.title"
            label="タイトル"
            variant="outlined"
            class="mb-2"
          />
          <v-textarea
            v-model="newRisk.description"
            label="説明"
            variant="outlined"
            rows="3"
            class="mb-2"
          />
          <v-select
            v-model="newRisk.category"
            :items="categories"
            label="カテゴリ"
            variant="outlined"
            class="mb-2"
          />
          <v-row>
            <v-col cols="6">
              <v-slider
                v-model="newRisk.likelihood"
                label="発生可能性"
                :min="1"
                :max="5"
                :step="1"
                thumb-label
              />
            </v-col>
            <v-col cols="6">
              <v-slider
                v-model="newRisk.impact"
                label="影響度"
                :min="1"
                :max="5"
                :step="1"
                thumb-label
              />
            </v-col>
          </v-row>
          <v-text-field
            v-model="newRisk.owner"
            label="担当者"
            variant="outlined"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDialog = false">キャンセル</v-btn>
          <v-btn color="primary" variant="flat" @click="handleCreate">登録</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
