import apiClient from '@/api/client'

export interface Evidence {
  id: string
  control: string
  title: string
  description: string
  file: string
  file_name: string
  file_size: number
  file_type: string
  uploaded_by: string | null
  created_at: string
  updated_at: string
}

export async function uploadEvidence(
  controlId: string,
  file: File,
  title: string,
  description = ''
): Promise<Evidence> {
  const formData = new FormData()
  formData.append('control', controlId)
  formData.append('file', file)
  formData.append('title', title)
  formData.append('description', description)

  const response = await apiClient.post<Evidence>(
    '/api/v1/controls/evidences/upload/',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

export async function getEvidences(controlId: string): Promise<Evidence[]> {
  const response = await apiClient.get<Evidence[]>(
    '/api/v1/controls/evidences/',
    { params: { control: controlId } }
  )
  return response.data
}

export async function downloadEvidence(evidenceId: string): Promise<Blob> {
  const response = await apiClient.get(
    `/api/v1/controls/evidences/${evidenceId}/download/`,
    { responseType: 'blob' }
  )
  return response.data as Blob
}

export async function deleteEvidence(evidenceId: string): Promise<void> {
  await apiClient.delete(`/api/v1/controls/evidences/${evidenceId}/`)
}
