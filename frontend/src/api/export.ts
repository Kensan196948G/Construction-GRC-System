import apiClient from '@/api/client'

export type ExportFormat = 'csv' | 'excel'

export type ExportResource =
  | 'risks'
  | 'controls'
  | 'compliance'
  | 'audits'
  | 'audit-findings'

const CONTENT_TYPES: Record<ExportFormat, string> = {
  csv: 'text/csv',
  excel:
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

const FILE_EXTENSIONS: Record<ExportFormat, string> = {
  csv: '.csv',
  excel: '.xlsx',
}

/**
 * 指定リソースのCSV/Excelをダウンロードする。
 */
export async function downloadExport(
  resource: ExportResource,
  format: ExportFormat
): Promise<void> {
  const urlMap: Record<ExportResource, string> = {
    risks: `/api/v1/risks/export/${format === 'csv' ? 'csv' : 'excel'}/`,
    controls: `/api/v1/controls/export/${format === 'csv' ? 'csv' : 'excel'}/`,
    compliance: `/api/v1/compliance/export/${format === 'csv' ? 'csv' : 'excel'}/`,
    audits: `/api/v1/audits/export/${format === 'csv' ? 'csv' : 'excel'}/`,
    'audit-findings': `/api/v1/audit-findings/export/${format === 'csv' ? 'csv' : 'excel'}/`,
  }

  const response = await apiClient.get(urlMap[resource], {
    responseType: 'blob',
  })

  const blob = new Blob([response.data], {
    type: CONTENT_TYPES[format],
  })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${resource}${FILE_EXTENSIONS[format]}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
