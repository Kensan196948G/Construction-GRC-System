<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDisplay } from 'vuetify'
import { useControlsStore } from '@/store/controls'
import type { ISO27001Control, ImplementationStatus, ControlDomain } from '@/types'
import { exportSoA } from '@/api/controls'

const controlsStore = useControlsStore()
const { smAndDown } = useDisplay()

// タブ
const activeTab = ref('all')
const tabs = [
  { value: 'all', label: '全て', icon: 'mdi-view-list' },
  { value: 'organizational', label: '組織的', icon: 'mdi-office-building' },
  { value: 'people', label: '人的', icon: 'mdi-account-group' },
  { value: 'physical', label: '物理的', icon: 'mdi-shield-home' },
  { value: 'technological', label: '技術的', icon: 'mdi-laptop' },
]

// テーブルヘッダ
const headers = [
  { title: '管理策ID', key: 'control_id', sortable: true, width: '100px' },
  { title: 'ドメイン', key: 'domain', sortable: true, width: '110px' },
  { title: '管理策名', key: 'title', sortable: true },
  { title: '説明', key: 'description', sortable: false },
  { title: '実施状況', key: 'implementation_status', sortable: true, width: '150px' },
  { title: '適用', key: 'is_applicable', sortable: true, width: '80px' },
]

// 実施状況の色定義
const statusColor = (status: ImplementationStatus | string): string => {
  const colors: Record<string, string> = {
    implemented: 'green',
    in_progress: 'blue',
    partially_implemented: 'orange',
    not_started: 'grey',
  }
  return colors[status] || 'grey'
}

const statusLabel = (status: ImplementationStatus | string): string => {
  const labels: Record<string, string> = {
    implemented: '実施済み',
    in_progress: '実施中',
    partially_implemented: '一部実施',
    not_started: '未着手',
  }
  return labels[status] || status
}

const domainLabel = (domain: ControlDomain | string): string => {
  const labels: Record<string, string> = {
    organizational: '組織的',
    people: '人的',
    physical: '物理的',
    technological: '技術的',
  }
  return labels[domain] || domain
}

const domainColor = (domain: ControlDomain | string): string => {
  const colors: Record<string, string> = {
    organizational: 'indigo',
    people: 'teal',
    physical: 'brown',
    technological: 'deep-purple',
  }
  return colors[domain] || 'grey'
}

// モックデータ (93管理策)
const mockControls: ISO27001Control[] = [
  // 組織的管理策 (A.5) - 37件
  { id: '1', control_id: 'A.5.1', domain: 'organizational', title: '情報セキュリティのための方針群', description: '情報セキュリティ方針及びトピック固有の方針を定義し承認する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['GV.PO'] },
  { id: '2', control_id: 'A.5.2', domain: 'organizational', title: '情報セキュリティの役割及び責任', description: '情報セキュリティの役割及び責任を定義し割り当てる', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['GV.RR'] },
  { id: '3', control_id: 'A.5.3', domain: 'organizational', title: '職務の分離', description: '相反する職務及び責任範囲を分離する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '人事部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '4', control_id: 'A.5.4', domain: 'organizational', title: '経営陣の責任', description: '全ての従業員に情報セキュリティ方針の遵守を要求する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '経営企画部', evidence_required: [], nist_csf_mapping: ['GV.RR'] },
  { id: '5', control_id: 'A.5.5', domain: 'organizational', title: '関係当局との連絡', description: '関係当局との適切な連絡体制を維持する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '総務部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '6', control_id: 'A.5.6', domain: 'organizational', title: '専門組織との連絡', description: '情報セキュリティに関する専門組織との連絡を維持する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '7', control_id: 'A.5.7', domain: 'organizational', title: '脅威インテリジェンス', description: '情報セキュリティの脅威に関する情報を収集・分析する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['ID.RA'] },
  { id: '8', control_id: 'A.5.8', domain: 'organizational', title: 'プロジェクトマネジメントにおける情報セキュリティ', description: 'プロジェクトマネジメントに情報セキュリティを統合する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: 'PMO', evidence_required: [], nist_csf_mapping: ['GV.PO'] },
  { id: '9', control_id: 'A.5.9', domain: 'organizational', title: '情報及びその他の関連資産の目録', description: '情報及び関連資産の目録を作成し維持する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['ID.AM'] },
  { id: '10', control_id: 'A.5.10', domain: 'organizational', title: '情報及びその他の関連資産の利用の許容範囲', description: '情報及び関連資産の利用の許容範囲を定める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['GV.PO'] },
  { id: '11', control_id: 'A.5.11', domain: 'organizational', title: '資産の返却', description: '雇用・契約の変更・終了時に資産を返却する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '人事部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '12', control_id: 'A.5.12', domain: 'organizational', title: '情報の分類', description: '情報を機密性に基づき分類する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['ID.AM'] },
  { id: '13', control_id: 'A.5.13', domain: 'organizational', title: '情報のラベル付け', description: '情報の分類体系に従いラベル付けする', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['ID.AM'] },
  { id: '14', control_id: 'A.5.14', domain: 'organizational', title: '情報転送', description: '情報転送の規則・手順を整備する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '15', control_id: 'A.5.15', domain: 'organizational', title: 'アクセス制御', description: 'アクセス制御に関する規則を定める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '16', control_id: 'A.5.16', domain: 'organizational', title: 'アイデンティティ管理', description: 'アイデンティティのライフサイクル管理を行う', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '17', control_id: 'A.5.17', domain: 'organizational', title: '認証情報', description: '認証情報の管理プロセスを確立する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '18', control_id: 'A.5.18', domain: 'organizational', title: 'アクセス権', description: 'アクセス権の付与・見直し・削除を管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '19', control_id: 'A.5.19', domain: 'organizational', title: '供給者関係における情報セキュリティ', description: '供給者との関係でリスクを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '調達部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '20', control_id: 'A.5.20', domain: 'organizational', title: '供給者との合意におけるセキュリティ', description: '供給者との合意にセキュリティ要件を含める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '調達部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '21', control_id: 'A.5.21', domain: 'organizational', title: 'ICTサプライチェーンにおけるセキュリティ管理', description: 'ICT製品・サービスのサプライチェーンリスクを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '22', control_id: 'A.5.22', domain: 'organizational', title: '供給者サービスの監視・レビュー・変更管理', description: '供給者のサービスを定期的に監視・レビューする', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '調達部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '23', control_id: 'A.5.23', domain: 'organizational', title: 'クラウドサービスの利用における情報セキュリティ', description: 'クラウドサービスのセキュリティを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '24', control_id: 'A.5.24', domain: 'organizational', title: '情報セキュリティインシデント管理の計画及び準備', description: 'インシデント対応の計画と手順を確立する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['RS.MA'] },
  { id: '25', control_id: 'A.5.25', domain: 'organizational', title: '情報セキュリティ事象の評価及び決定', description: 'セキュリティ事象を評価しインシデントか判断する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['DE.AE'] },
  { id: '26', control_id: 'A.5.26', domain: 'organizational', title: '情報セキュリティインシデントへの対応', description: 'インシデントに手順に従い対応する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['RS.MA'] },
  { id: '27', control_id: 'A.5.27', domain: 'organizational', title: '情報セキュリティインシデントからの学習', description: 'インシデントから得た知識を活用する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['RS.IM'] },
  { id: '28', control_id: 'A.5.28', domain: 'organizational', title: '証拠の収集', description: 'セキュリティ事象に関連する証拠を収集・保全する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['RS.AN'] },
  { id: '29', control_id: 'A.5.29', domain: 'organizational', title: '事業の中断・阻害時の情報セキュリティ', description: '事業継続時の情報セキュリティを維持する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '事業継続部', evidence_required: [], nist_csf_mapping: ['RC.RP'] },
  { id: '30', control_id: 'A.5.30', domain: 'organizational', title: '事業継続のためのICTの備え', description: 'ICTサービスの事業継続を計画する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['RC.RP'] },
  { id: '31', control_id: 'A.5.31', domain: 'organizational', title: '法令・規制及び契約上の要求事項', description: '適用される法的・契約上の要件を特定する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '法務部', evidence_required: [], nist_csf_mapping: ['GV.OC'] },
  { id: '32', control_id: 'A.5.32', domain: 'organizational', title: '知的財産権', description: '知的財産権を保護する手順を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '法務部', evidence_required: [], nist_csf_mapping: ['GV.OC'] },
  { id: '33', control_id: 'A.5.33', domain: 'organizational', title: '記録の保護', description: '記録を紛失・破壊・改ざんから保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '総務部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '34', control_id: 'A.5.34', domain: 'organizational', title: 'プライバシー及びPIIの保護', description: '個人情報の保護に関する要件を遵守する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '法務部', evidence_required: [], nist_csf_mapping: ['GV.OC'] },
  { id: '35', control_id: 'A.5.35', domain: 'organizational', title: '情報セキュリティの独立したレビュー', description: '情報セキュリティの独立したレビューを実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['GV.OV'] },
  { id: '36', control_id: 'A.5.36', domain: 'organizational', title: '情報セキュリティのための方針群への準拠', description: '方針・規則への準拠を定期的にレビューする', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '内部監査部', evidence_required: [], nist_csf_mapping: ['GV.OV'] },
  { id: '37', control_id: 'A.5.37', domain: 'organizational', title: '操作手順書', description: '情報処理設備の操作手順を文書化する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  // 人的管理策 (A.6) - 8件
  { id: '38', control_id: 'A.6.1', domain: 'people', title: '選考', description: '雇用候補者の経歴確認を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '人事部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '39', control_id: 'A.6.2', domain: 'people', title: '雇用条件', description: '雇用契約にセキュリティ責任を含める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '人事部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '40', control_id: 'A.6.3', domain: 'people', title: '情報セキュリティの意識向上・教育及び訓練', description: 'セキュリティの意識向上プログラムを実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '人事部', evidence_required: [], nist_csf_mapping: ['PR.AT'] },
  { id: '41', control_id: 'A.6.4', domain: 'people', title: '懲戒手続', description: 'セキュリティ違反に対する懲戒手続を定める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '人事部', evidence_required: [], nist_csf_mapping: ['GV.PO'] },
  { id: '42', control_id: 'A.6.5', domain: 'people', title: '雇用の終了又は変更後の責任', description: '雇用終了・変更後も有効な責任を定義する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '人事部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '43', control_id: 'A.6.6', domain: 'people', title: '秘密保持契約又は守秘義務契約', description: '秘密保持に関する要件を定め合意する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '法務部', evidence_required: [], nist_csf_mapping: ['GV.PO'] },
  { id: '44', control_id: 'A.6.7', domain: 'people', title: 'リモートワーキング', description: 'リモートワーク時のセキュリティ対策を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '45', control_id: 'A.6.8', domain: 'people', title: '情報セキュリティ事象の報告', description: 'セキュリティ事象を報告する仕組みを整備する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['DE.AE'] },
  // 物理的管理策 (A.7) - 14件
  { id: '46', control_id: 'A.7.1', domain: 'physical', title: '物理的セキュリティ境界', description: 'セキュリティ境界を定義し保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '47', control_id: 'A.7.2', domain: 'physical', title: '物理的入退', description: '物理的なアクセス制御を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '48', control_id: 'A.7.3', domain: 'physical', title: 'オフィス・部屋及び施設のセキュリティ', description: 'オフィス等の物理的セキュリティを確保する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '49', control_id: 'A.7.4', domain: 'physical', title: '物理的セキュリティの監視', description: '施設への不正アクセスを監視する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['DE.CM'] },
  { id: '50', control_id: 'A.7.5', domain: 'physical', title: '物理的及び環境的脅威からの保護', description: '自然災害等の脅威から保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '51', control_id: 'A.7.6', domain: 'physical', title: 'セキュリティを保つべき領域での作業', description: 'セキュリティ領域での作業手順を定める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '52', control_id: 'A.7.7', domain: 'physical', title: 'クリアデスク・クリアスクリーン', description: 'クリアデスク・クリアスクリーン方針を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '53', control_id: 'A.7.8', domain: 'physical', title: '装置の設置及び保護', description: '装置を適切に設置し保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '54', control_id: 'A.7.9', domain: 'physical', title: '構外にある資産のセキュリティ', description: '構外での資産のセキュリティを確保する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '55', control_id: 'A.7.10', domain: 'physical', title: '記憶媒体', description: '記憶媒体のライフサイクルを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '56', control_id: 'A.7.11', domain: 'physical', title: 'サポートユーティリティ', description: '電力・通信等のインフラ障害から保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '57', control_id: 'A.7.12', domain: 'physical', title: 'ケーブル配線のセキュリティ', description: 'ケーブル配線を傍受・妨害から保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '施設管理部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '58', control_id: 'A.7.13', domain: 'physical', title: '装置の保守', description: '装置を正しく保守する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.MA'] },
  { id: '59', control_id: 'A.7.14', domain: 'physical', title: '装置のセキュリティを保った処分又は再利用', description: '装置のデータを安全に消去してから処分する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  // 技術的管理策 (A.8) - 34件
  { id: '60', control_id: 'A.8.1', domain: 'technological', title: '利用者エンドポイント機器', description: 'エンドポイント機器のセキュリティを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '61', control_id: 'A.8.2', domain: 'technological', title: '特権的アクセス権', description: '特権アクセス権の割当を制限・管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '62', control_id: 'A.8.3', domain: 'technological', title: '情報へのアクセス制限', description: 'アクセス制御方針に従い情報へのアクセスを制限する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '63', control_id: 'A.8.4', domain: 'technological', title: 'ソースコードへのアクセス', description: 'ソースコードへの読取・書込アクセスを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '開発部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '64', control_id: 'A.8.5', domain: 'technological', title: 'セキュリティを保った認証', description: '安全な認証技術と手順を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '65', control_id: 'A.8.6', domain: 'technological', title: '容量・能力の管理', description: 'ITリソースの容量を監視・調整する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '66', control_id: 'A.8.7', domain: 'technological', title: 'マルウェアに対する保護', description: 'マルウェア対策を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['DE.CM'] },
  { id: '67', control_id: 'A.8.8', domain: 'technological', title: '技術的脆弱性の管理', description: '技術的脆弱性の情報を取得し対処する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['ID.RA'] },
  { id: '68', control_id: 'A.8.9', domain: 'technological', title: '構成管理', description: 'ハードウェア・ソフトウェアの構成を管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '69', control_id: 'A.8.10', domain: 'technological', title: '情報の削除', description: '不要な情報を適時に削除する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '70', control_id: 'A.8.11', domain: 'technological', title: 'データマスキング', description: '個人情報等をマスキングする', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '71', control_id: 'A.8.12', domain: 'technological', title: 'データ漏えいの防止', description: 'データ漏えい防止策を実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '72', control_id: 'A.8.13', domain: 'technological', title: '情報のバックアップ', description: '情報のバックアップを定期的に実施・検証する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '73', control_id: 'A.8.14', domain: 'technological', title: '情報処理施設の冗長性', description: '可用性要件を満たす冗長性を確保する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '74', control_id: 'A.8.15', domain: 'technological', title: 'ログ取得', description: 'アクティビティ・例外等のログを記録する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['DE.AE'] },
  { id: '75', control_id: 'A.8.16', domain: 'technological', title: '監視活動', description: 'ネットワーク・システムを監視し異常を検知する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['DE.CM'] },
  { id: '76', control_id: 'A.8.17', domain: 'technological', title: 'クロックの同期', description: '情報処理システムのクロックを同期する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '77', control_id: 'A.8.18', domain: 'technological', title: '特権的なユーティリティプログラムの使用', description: '特権ユーティリティの使用を制限・管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.AA'] },
  { id: '78', control_id: 'A.8.19', domain: 'technological', title: '運用システムに関わるソフトウェアの導入', description: '運用システムへのソフトウェア導入を管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '79', control_id: 'A.8.20', domain: 'technological', title: 'ネットワークのセキュリティ', description: 'ネットワーク及びネットワークサービスを保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '80', control_id: 'A.8.21', domain: 'technological', title: 'ネットワークサービスのセキュリティ', description: 'ネットワークサービスのセキュリティを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '81', control_id: 'A.8.22', domain: 'technological', title: 'ネットワークの分離', description: 'ネットワークをグループ分けし分離する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '82', control_id: 'A.8.23', domain: 'technological', title: 'ウェブフィルタリング', description: '外部ウェブサイトへのアクセスを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.IR'] },
  { id: '83', control_id: 'A.8.24', domain: 'technological', title: '暗号の使用', description: '暗号の適切な使用に関する規則を定める', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報セキュリティ部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '84', control_id: 'A.8.25', domain: 'technological', title: 'セキュリティに配慮した開発のライフサイクル', description: 'ソフトウェア開発にセキュリティルールを適用する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '開発部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '85', control_id: 'A.8.26', domain: 'technological', title: 'アプリケーションセキュリティの要求事項', description: 'アプリケーション開発時のセキュリティ要件を定義する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '開発部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '86', control_id: 'A.8.27', domain: 'technological', title: 'セキュリティに配慮したシステムアーキテクチャ及びシステム構築の原則', description: 'セキュアなシステム構築の原則を確立する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '開発部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '87', control_id: 'A.8.28', domain: 'technological', title: 'セキュリティに配慮したコーディング', description: 'セキュアコーディングの原則を適用する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '開発部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '88', control_id: 'A.8.29', domain: 'technological', title: '開発及び受入れにおけるセキュリティ試験', description: '開発中のセキュリティテストを実施する', is_applicable: true, exclusion_reason: '', implementation_status: 'not_started', owner: null, evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '89', control_id: 'A.8.30', domain: 'technological', title: '外部委託による開発', description: '外部委託開発のセキュリティを管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'in_progress', owner: '調達部', evidence_required: [], nist_csf_mapping: ['GV.SC'] },
  { id: '90', control_id: 'A.8.31', domain: 'technological', title: '開発環境・試験環境・運用環境の分離', description: '開発・テスト・運用環境を分離する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '91', control_id: 'A.8.32', domain: 'technological', title: '変更管理', description: '情報処理施設・システムの変更を管理する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '情報システム部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
  { id: '92', control_id: 'A.8.33', domain: 'technological', title: 'テスト情報', description: 'テスト情報を適切に選定・保護する', is_applicable: true, exclusion_reason: '', implementation_status: 'partially_implemented', owner: '開発部', evidence_required: [], nist_csf_mapping: ['PR.DS'] },
  { id: '93', control_id: 'A.8.34', domain: 'technological', title: '監査試験中の情報システムの保護', description: '監査テストによる業務への影響を最小化する', is_applicable: true, exclusion_reason: '', implementation_status: 'implemented', owner: '内部監査部', evidence_required: [], nist_csf_mapping: ['PR.PS'] },
]

// データソース（ストアにデータがあればそちらを使用、なければモック）
const allControls = computed(() => {
  return controlsStore.controls.length > 0 ? controlsStore.controls : mockControls
})

// タブによるフィルタ
const filteredControls = computed(() => {
  if (activeTab.value === 'all') return allControls.value
  return allControls.value.filter((c) => c.domain === activeTab.value)
})

// ステータス別カウント
const statusCounts = computed(() => {
  const all = allControls.value
  return {
    implemented: all.filter((c) => c.implementation_status === 'implemented').length,
    in_progress: all.filter((c) => c.implementation_status === 'in_progress').length,
    partially_implemented: all.filter((c) => c.implementation_status === 'partially_implemented').length,
    not_started: all.filter((c) => c.implementation_status === 'not_started').length,
    total: all.length,
  }
})

// 準拠率
const complianceRate = computed(() => {
  if (statusCounts.value.total === 0) return 0
  return Math.round((statusCounts.value.implemented / statusCounts.value.total) * 100)
})

const complianceRateColor = computed(() => {
  if (complianceRate.value >= 80) return 'green'
  if (complianceRate.value >= 60) return 'orange'
  return 'red'
})

// ドメイン別カウント
const domainCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const c of allControls.value) {
    counts[c.domain] = (counts[c.domain] || 0) + 1
  }
  return counts
})

// SoAエクスポート
const exporting = ref(false)
const handleExportSoA = async () => {
  exporting.value = true
  try {
    const blob = await exportSoA()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `SoA_ISO27001_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch {
    // エクスポートエラー
    alert('SoAエクスポートに失敗しました。バックエンドAPIを確認してください。')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  try {
    await Promise.allSettled([
      controlsStore.fetchControls(),
      controlsStore.fetchComplianceRate(),
    ])
  } catch {
    // フォールバックはモックデータを使用
  }
})
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-4">
    <!-- ヘッダ -->
    <div class="d-flex align-center mb-4">
      <h1 class="text-h4">管理策一覧 (ISO27001:2022)</h1>
      <v-spacer />
      <v-btn
        color="primary"
        variant="outlined"
        prepend-icon="mdi-file-export"
        :loading="exporting"
        @click="handleExportSoA"
      >
        SoAエクスポート
      </v-btn>
    </div>

    <!-- 準拠率サマリバー -->
    <v-card elevation="2" class="mb-4">
      <v-card-text class="pa-4">
        <v-row align="center" dense>
          <v-col cols="12" md="4">
            <div class="d-flex align-center">
              <v-icon color="green" size="28" class="mr-2">mdi-shield-check</v-icon>
              <div>
                <div class="text-caption text-medium-emphasis">全体準拠率</div>
                <div class="text-h5 font-weight-bold">{{ complianceRate }}%</div>
              </div>
            </div>
            <v-progress-linear
              :model-value="complianceRate"
              :color="complianceRateColor"
              height="12"
              rounded
              class="mt-2"
            />
          </v-col>
          <v-col cols="12" md="8">
            <div class="d-flex flex-wrap ga-3 justify-end">
              <v-chip color="green" variant="tonal" size="small" label>
                <v-icon start size="14">mdi-check-circle</v-icon>
                実施済み: {{ statusCounts.implemented }}
              </v-chip>
              <v-chip color="blue" variant="tonal" size="small" label>
                <v-icon start size="14">mdi-progress-clock</v-icon>
                実施中: {{ statusCounts.in_progress }}
              </v-chip>
              <v-chip color="orange" variant="tonal" size="small" label>
                <v-icon start size="14">mdi-progress-alert</v-icon>
                一部実施: {{ statusCounts.partially_implemented }}
              </v-chip>
              <v-chip color="grey" variant="tonal" size="small" label>
                <v-icon start size="14">mdi-minus-circle-outline</v-icon>
                未着手: {{ statusCounts.not_started }}
              </v-chip>
              <v-chip color="primary" variant="outlined" size="small" label>
                合計: {{ statusCounts.total }}
              </v-chip>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- ドメインタブ -->
    <v-tabs v-model="activeTab" color="primary" class="mb-4">
      <v-tab
        v-for="tab in tabs"
        :key="tab.value"
        :value="tab.value"
      >
        <v-icon start>{{ tab.icon }}</v-icon>
        {{ tab.label }}
        <v-chip
          v-if="tab.value !== 'all'"
          size="x-small"
          class="ml-2"
          variant="tonal"
        >
          {{ domainCounts[tab.value] || 0 }}
        </v-chip>
        <v-chip
          v-else
          size="x-small"
          class="ml-2"
          variant="tonal"
        >
          {{ allControls.length }}
        </v-chip>
      </v-tab>
    </v-tabs>

    <!-- 管理策テーブル -->
    <v-card elevation="2">
      <v-data-table
        :headers="headers"
        :items="filteredControls"
        :loading="controlsStore.loading"
        items-per-page="20"
        hover
        class="controls-table"
      >
        <template #item.control_id="{ item }">
          <span class="font-weight-medium text-primary">{{ item.control_id }}</span>
        </template>

        <template #item.domain="{ item }">
          <v-chip
            :color="domainColor(item.domain)"
            size="small"
            variant="tonal"
            label
          >
            {{ domainLabel(item.domain) }}
          </v-chip>
        </template>

        <template #item.implementation_status="{ item }">
          <v-chip
            :color="statusColor(item.implementation_status)"
            size="small"
            label
          >
            {{ statusLabel(item.implementation_status) }}
          </v-chip>
        </template>

        <template #item.is_applicable="{ item }">
          <v-icon
            :color="item.is_applicable ? 'green' : 'grey'"
            size="20"
          >
            {{ item.is_applicable ? 'mdi-check-circle' : 'mdi-close-circle' }}
          </v-icon>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<style scoped>
.controls-table :deep(td) {
  font-size: 0.85rem !important;
}
</style>
