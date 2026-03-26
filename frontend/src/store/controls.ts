import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ISO27001Control, ImplementationStatus } from '@/types'
import {
  getControls,
  getComplianceRate,
  updateControl,
  type ComplianceRateResponse,
  type ControlFilters,
} from '@/api/controls'

export const useControlsStore = defineStore('controls', () => {
  const controls = ref<ISO27001Control[]>([])
  const complianceRate = ref<ComplianceRateResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  const implementedCount = computed(
    () => complianceRate.value?.implemented ?? 0
  )

  const compliancePercentage = computed(
    () => complianceRate.value?.rate ?? 0
  )

  async function fetchControls(filters?: ControlFilters): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await getControls(filters)
      controls.value = response.results
      totalCount.value = response.count
    } catch (e: unknown) {
      error.value =
        e instanceof Error ? e.message : '管理策の取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function fetchComplianceRate(): Promise<void> {
    try {
      complianceRate.value = await getComplianceRate()
    } catch (e: unknown) {
      error.value =
        e instanceof Error ? e.message : 'コンプライアンス率の取得に失敗しました'
    }
  }

  async function updateControlStatus(
    id: string,
    status: ImplementationStatus
  ): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await updateControl(id, {
        implementation_status: status,
      })
      const index = controls.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        controls.value[index] = updated
      }
    } catch (e: unknown) {
      error.value =
        e instanceof Error ? e.message : '管理策の更新に失敗しました'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    controls,
    complianceRate,
    loading,
    error,
    totalCount,
    implementedCount,
    compliancePercentage,
    fetchControls,
    fetchComplianceRate,
    updateControlStatus,
  }
})
