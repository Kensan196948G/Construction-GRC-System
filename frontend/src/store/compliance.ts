import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getRequirements, getComplianceRate, updateRequirement } from '@/api/compliance'
import type { ComplianceRequirement } from '@/types'
import type { ComplianceRateResponse } from '@/api/compliance'

export const useComplianceStore = defineStore('compliance', () => {
  const requirements = ref<ComplianceRequirement[]>([])
  const complianceRate = ref<ComplianceRateResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  const frameworkGroups = computed(() => {
    const groups: Record<string, ComplianceRequirement[]> = {}
    for (const req of requirements.value) {
      if (!groups[req.framework]) groups[req.framework] = []
      groups[req.framework].push(req)
    }
    return groups
  })

  async function fetchRequirements(params?: { framework?: string; compliance_status?: string }) {
    loading.value = true
    error.value = null
    try {
      const response = await getRequirements(params)
      requirements.value = response.results
      totalCount.value = response.count
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'コンプライアンス要件の取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function fetchComplianceRate() {
    try {
      complianceRate.value = await getComplianceRate()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '準拠率の取得に失敗しました'
    }
  }

  async function updateRequirementStatus(id: string, data: Partial<ComplianceRequirement>) {
    loading.value = true
    error.value = null
    try {
      const updated = await updateRequirement(id, data)
      const idx = requirements.value.findIndex(r => r.id === id)
      if (idx !== -1) requirements.value[idx] = updated
      return updated
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '要件の更新に失敗しました'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    requirements, complianceRate, loading, error, totalCount,
    frameworkGroups,
    fetchRequirements, fetchComplianceRate, updateRequirementStatus,
  }
})
