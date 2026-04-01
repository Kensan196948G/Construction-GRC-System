// リスク関連
export interface Risk {
  id: string
  risk_id: string
  title: string
  description: string
  category: RiskCategory
  likelihood_inherent: number
  impact_inherent: number
  risk_score_inherent: number
  likelihood_residual?: number
  impact_residual?: number
  risk_score_residual?: number
  treatment_strategy: TreatmentStrategy
  treatment_plan: string
  risk_owner: string | null
  target_date: string | null
  status: RiskStatus
  risk_level: RiskLevel
  created_at: string
  updated_at: string
}

export type RiskCategory =
  | 'IT'
  | 'Physical'
  | 'Legal'
  | 'Construction'
  | 'Financial'
  | 'Operational'

export type TreatmentStrategy = 'accept' | 'mitigate' | 'transfer' | 'avoid'

export type RiskStatus = 'open' | 'in_progress' | 'closed' | 'accepted'

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

// ISO27001管理策
export interface ISO27001Control {
  id: string
  control_id: string
  domain: ControlDomain
  title: string
  description: string
  is_applicable: boolean
  exclusion_reason: string
  implementation_status: ImplementationStatus
  owner: string | null
  evidence_required: string[]
  nist_csf_mapping: string[]
}

export type ControlDomain =
  | 'organizational'
  | 'people'
  | 'physical'
  | 'technological'

export type ImplementationStatus =
  | 'not_started'
  | 'in_progress'
  | 'implemented'
  | 'partially_implemented'

// コンプライアンス
export interface ComplianceRequirement {
  id: string
  req_id: string
  framework: string
  category: string
  title: string
  description: string
  article_ref: string
  is_mandatory: boolean
  frequency: string
  owner: string | null
  last_assessed_at: string | null
  compliance_status: ComplianceStatus
}

export type ComplianceStatus =
  | 'compliant'
  | 'non_compliant'
  | 'partial'
  | 'unknown'

// 監査
export interface Audit {
  id: string
  audit_id: string
  title: string
  audit_type: string
  scope: string
  status: string
  target_department: string
  lead_auditor: string | null
  planned_start: string
  planned_end: string
  actual_start: string | null
  actual_end: string | null
  findings_count: number
}

export interface AuditFinding {
  id: string
  finding_id: string
  finding_type: string
  title: string
  description: string
  severity: string
  corrective_action: string
  cap_status: string
  due_date: string | null
  closed_at: string | null
}

// ダッシュボード
export interface DashboardSummary {
  total_risks: number
  critical_risks: number
  compliance_rate: number
  open_findings: number
}

export interface HeatmapCell {
  likelihood: number
  impact: number
  count: number
  risks: Risk[]
}

// API
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  detail: string
  code?: string
}
