import apiClient from '@/api/client'
import type { ComplianceRequirement, PaginatedResponse } from '@/types'

export interface ComplianceFilters {
  framework?: string
  category?: string
  compliance_status?: string
  page?: number
  page_size?: number
}

export interface ComplianceRateResponse {
  total: number
  compliant: number
  non_compliant: number
  partial: number
  unknown: number
  rate: number
}

export async function getRequirements(
  filters?: ComplianceFilters
): Promise<PaginatedResponse<ComplianceRequirement>> {
  const response = await apiClient.get<
    PaginatedResponse<ComplianceRequirement>
  >('/api/v1/compliance', { params: filters })
  return response.data
}

export async function getRequirement(
  id: string
): Promise<ComplianceRequirement> {
  const response = await apiClient.get<ComplianceRequirement>(
    `/api/v1/compliance/${id}`
  )
  return response.data
}

export async function updateRequirement(
  id: string,
  data: Partial<ComplianceRequirement>
): Promise<ComplianceRequirement> {
  const response = await apiClient.patch<ComplianceRequirement>(
    `/api/v1/compliance/${id}`,
    data
  )
  return response.data
}

export async function getComplianceRate(): Promise<ComplianceRateResponse> {
  const response = await apiClient.get<ComplianceRateResponse>(
    '/api/v1/compliance/rate'
  )
  return response.data
}
