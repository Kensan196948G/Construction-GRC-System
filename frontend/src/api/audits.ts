import apiClient from '@/api/client'
import type { Audit, AuditFinding, PaginatedResponse } from '@/types'

export interface AuditFilters {
  status?: string
  target_department?: string
  page?: number
  page_size?: number
}

export interface FindingFilters {
  finding_type?: string
  cap_status?: string
  page?: number
  page_size?: number
}

export async function getAudits(
  filters?: AuditFilters
): Promise<PaginatedResponse<Audit>> {
  const response = await apiClient.get<PaginatedResponse<Audit>>(
    '/api/v1/audits',
    { params: filters }
  )
  return response.data
}

export async function getAudit(id: string): Promise<Audit> {
  const response = await apiClient.get<Audit>(`/api/v1/audits/${id}`)
  return response.data
}

export async function createAudit(
  audit: Omit<Audit, 'id' | 'audit_id' | 'findings_count'>
): Promise<Audit> {
  const response = await apiClient.post<Audit>('/api/v1/audits', audit)
  return response.data
}

export async function getFindings(
  auditId: string,
  filters?: FindingFilters
): Promise<PaginatedResponse<AuditFinding>> {
  const response = await apiClient.get<PaginatedResponse<AuditFinding>>(
    `/api/v1/audits/${auditId}/findings`,
    { params: filters }
  )
  return response.data
}

export async function createFinding(
  auditId: string,
  finding: Omit<AuditFinding, 'id' | 'finding_id'>
): Promise<AuditFinding> {
  const response = await apiClient.post<AuditFinding>(
    `/api/v1/audits/${auditId}/findings`,
    finding
  )
  return response.data
}
