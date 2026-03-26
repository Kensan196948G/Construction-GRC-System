import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api/client'

export interface Risk {
  risk_id: string
  title: string
  description: string
  category: string
  likelihood: number
  impact: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  status: string
  owner: string
  created_at: string
}

export interface HeatmapCell {
  likelihood: number
  impact: number
  count: number
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
}

export const useRisksStore = defineStore('risks', () => {
  const risks = ref<Risk[]>([])
  const heatmap = ref<HeatmapCell[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchRisks(params?: { category?: string; status?: string }) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/v1/risks', { params })
      risks.value = response.data
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'リスクの取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function fetchHeatmap() {
    try {
      const response = await apiClient.get('/api/v1/risks/heatmap')
      heatmap.value = response.data
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'ヒートマップの取得に失敗しました'
    }
  }

  async function createRisk(risk: Omit<Risk, 'risk_id' | 'created_at' | 'risk_level'>) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/v1/risks', risk)
      risks.value.push(response.data)
      return response.data
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'リスクの作成に失敗しました'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    risks,
    heatmap,
    loading,
    error,
    fetchRisks,
    fetchHeatmap,
    createRisk,
  }
})
