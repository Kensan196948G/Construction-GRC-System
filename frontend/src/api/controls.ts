import apiClient from '@/api/client'
import type { ISO27001Control, PaginatedResponse } from '@/types'

export interface ControlFilters {
  domain?: string
  implementation_status?: string
  is_applicable?: boolean
  page?: number
  page_size?: number
}

export interface SoAEntry {
  control_id: string
  title: string
  domain: string
  is_applicable: boolean
  exclusion_reason: string
  implementation_status: string
}

export interface ComplianceRateResponse {
  total: number
  implemented: number
  partially_implemented: number
  in_progress: number
  not_started: number
  rate: number
}

export async function getControls(
  filters?: ControlFilters
): Promise<PaginatedResponse<ISO27001Control>> {
  const response = await apiClient.get<PaginatedResponse<ISO27001Control>>(
    '/api/v1/controls',
    { params: filters }
  )
  return response.data
}

export async function getControl(id: string): Promise<ISO27001Control> {
  const response = await apiClient.get<ISO27001Control>(
    `/api/v1/controls/${id}`
  )
  return response.data
}

export async function updateControl(
  id: string,
  data: Partial<ISO27001Control>
): Promise<ISO27001Control> {
  const response = await apiClient.patch<ISO27001Control>(
    `/api/v1/controls/${id}`,
    data
  )
  return response.data
}

export async function getSoA(): Promise<SoAEntry[]> {
  const response = await apiClient.get<SoAEntry[]>('/api/v1/controls/soa')
  return response.data
}

export async function exportSoA(): Promise<Blob> {
  const response = await apiClient.get('/api/v1/controls/soa/export', {
    responseType: 'blob',
  })
  return response.data as Blob
}

export async function getComplianceRate(): Promise<ComplianceRateResponse> {
  const response = await apiClient.get<ComplianceRateResponse>(
    '/api/v1/controls/compliance-rate'
  )
  return response.data
}
