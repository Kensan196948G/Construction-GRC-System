import apiClient from '@/api/client'
import type {
  Risk,
  HeatmapCell,
  DashboardSummary,
  PaginatedResponse,
} from '@/types'

export interface RiskFilters {
  category?: string
  status?: string
  risk_level?: string
  page?: number
  page_size?: number
}

export async function getRisks(
  filters?: RiskFilters
): Promise<PaginatedResponse<Risk>> {
  const response = await apiClient.get<PaginatedResponse<Risk>>(
    '/api/v1/risks',
    { params: filters }
  )
  return response.data
}

export async function getRisk(id: string): Promise<Risk> {
  const response = await apiClient.get<Risk>(`/api/v1/risks/${id}`)
  return response.data
}

export async function createRisk(
  risk: Omit<Risk, 'id' | 'risk_id' | 'risk_score_inherent' | 'risk_score_residual' | 'risk_level' | 'created_at' | 'updated_at'>
): Promise<Risk> {
  const response = await apiClient.post<Risk>('/api/v1/risks', risk)
  return response.data
}

export async function updateRisk(
  id: string,
  risk: Partial<Risk>
): Promise<Risk> {
  const response = await apiClient.patch<Risk>(`/api/v1/risks/${id}`, risk)
  return response.data
}

export async function deleteRisk(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/risks/${id}`)
}

export async function getHeatmap(): Promise<HeatmapCell[]> {
  const response = await apiClient.get<HeatmapCell[]>(
    '/api/v1/risks/heatmap'
  )
  return response.data
}

export async function getDashboard(): Promise<DashboardSummary> {
  const response = await apiClient.get<DashboardSummary>(
    '/api/v1/dashboard/summary'
  )
  return response.data
}

export const exportRisksCSV = () =>
  apiClient.get('/api/v1/risks/export/csv/', { responseType: 'blob' })

export const exportRisksExcel = () =>
  apiClient.get('/api/v1/risks/export/excel/', { responseType: 'blob' })
