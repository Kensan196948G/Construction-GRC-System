import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAudits, getAudit, createAudit, getFindings, createFinding } from '@/api/audits'
import type { Audit, AuditFinding } from '@/types'

export const useAuditsStore = defineStore('audits', () => {
  const audits = ref<Audit[]>([])
  const currentAudit = ref<Audit | null>(null)
  const findings = ref<AuditFinding[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  async function fetchAudits(params?: { status?: string; target_department?: string }) {
    loading.value = true
    error.value = null
    try {
      const response = await getAudits(params)
      audits.value = response.results
      totalCount.value = response.count
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '監査情報の取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function fetchAudit(id: string) {
    loading.value = true
    error.value = null
    try {
      currentAudit.value = await getAudit(id)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '監査詳細の取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function addAudit(audit: Omit<Audit, 'id' | 'audit_id' | 'findings_count'>) {
    loading.value = true
    error.value = null
    try {
      const created = await createAudit(audit)
      audits.value.push(created)
      return created
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '監査の作成に失敗しました'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchFindings(auditId: string) {
    loading.value = true
    error.value = null
    try {
      const response = await getFindings(auditId)
      findings.value = response.results
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '監査所見の取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function addFinding(auditId: string, finding: Omit<AuditFinding, 'id' | 'finding_id'>) {
    loading.value = true
    error.value = null
    try {
      const created = await createFinding(auditId, finding)
      findings.value.push(created)
      return created
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '監査所見の作成に失敗しました'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    audits, currentAudit, findings, loading, error, totalCount,
    fetchAudits, fetchAudit, addAudit, fetchFindings, addFinding,
  }
})
