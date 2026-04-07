export const messages = {
  ja: {
    common: {
      save: '保存',
      cancel: 'キャンセル',
      delete: '削除',
      edit: '編集',
      search: '検索',
      filter: 'フィルタ',
      loading: '読み込み中...',
      noData: 'データがありません',
      confirm: '確認',
      close: '閉じる',
    },
    nav: {
      dashboard: 'ダッシュボード',
      risks: 'リスク管理',
      compliance: 'コンプライアンス',
      controls: '管理策',
      audits: '内部監査',
      reports: 'レポート',
      settings: '設定',
    },
    risk: {
      title: 'リスク管理',
      create: 'リスク登録',
      heatmap: 'ヒートマップ',
      level: {
        critical: '重大',
        high: '高',
        medium: '中',
        low: '低',
      },
    },
    compliance: {
      title: 'コンプライアンス管理',
      rate: '準拠率',
      status: {
        compliant: '準拠',
        non_compliant: '非準拠',
        partial: '部分準拠',
        unknown: '未評価',
      },
    },
    audit: {
      title: '内部監査',
      create: '監査作成',
      findings: '監査所見',
      finding_type: {
        major_nc: '重大不適合',
        minor_nc: '軽微不適合',
        observation: '観察事項',
        good_practice: '優良事項',
      },
    },
    dashboard: {
      title: 'GRCダッシュボード',
      riskSummary: 'リスクサマリー',
      complianceRate: '準拠率',
      controlsStatus: '管理策状況',
      auditFindings: '監査所見',
      recentActivity: '最近のアクティビティ',
    },
    report: {
      title: 'レポート',
      generate: '生成',
      download: 'ダウンロード',
      format: { pdf: 'PDF', excel: 'Excel' },
      types: {
        dashboard: 'GRCダッシュボード',
        iso27001: 'ISO27001年次レポート',
        compliance: '準拠率レポート',
        risk: 'リスクトレンド',
        soa: '適用宣言書(SoA)',
        audit: '監査報告書',
      },
    },
    framework: {
      iso27001: 'ISO27001:2022',
      nist_csf: 'NIST CSF 2.0',
      construction_law: '建設業法',
      quality_law: '品確法',
      safety_law: '労安法',
      subcontract_law: '下請法',
      iso20000: 'ISO20000',
    },
    settings: {
      theme: 'テーマ',
      language: '言語',
      light: 'ライト',
      dark: 'ダーク',
      system: 'システム設定',
    },
  },
  en: {
    common: {
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      search: 'Search',
      filter: 'Filter',
      loading: 'Loading...',
      noData: 'No data',
      confirm: 'Confirm',
      close: 'Close',
    },
    nav: {
      dashboard: 'Dashboard',
      risks: 'Risk Management',
      compliance: 'Compliance',
      controls: 'Controls',
      audits: 'Internal Audit',
      reports: 'Reports',
      settings: 'Settings',
    },
    risk: {
      title: 'Risk Management',
      create: 'New Risk',
      heatmap: 'Heatmap',
      level: {
        critical: 'Critical',
        high: 'High',
        medium: 'Medium',
        low: 'Low',
      },
    },
    compliance: {
      title: 'Compliance Management',
      rate: 'Compliance Rate',
      status: {
        compliant: 'Compliant',
        non_compliant: 'Non-Compliant',
        partial: 'Partial',
        unknown: 'Unknown',
      },
    },
    audit: {
      title: 'Internal Audit',
      create: 'New Audit',
      findings: 'Findings',
      finding_type: {
        major_nc: 'Major NC',
        minor_nc: 'Minor NC',
        observation: 'Observation',
        good_practice: 'Good Practice',
      },
    },
    dashboard: {
      title: 'GRC Dashboard',
      riskSummary: 'Risk Summary',
      complianceRate: 'Compliance Rate',
      controlsStatus: 'Controls Status',
      auditFindings: 'Audit Findings',
      recentActivity: 'Recent Activity',
    },
    report: {
      title: 'Reports',
      generate: 'Generate',
      download: 'Download',
      format: { pdf: 'PDF', excel: 'Excel' },
      types: {
        dashboard: 'GRC Dashboard',
        iso27001: 'ISO27001 Annual Report',
        compliance: 'Compliance Rate Report',
        risk: 'Risk Trend',
        soa: 'Statement of Applicability (SoA)',
        audit: 'Audit Report',
      },
    },
    framework: {
      iso27001: 'ISO27001:2022',
      nist_csf: 'NIST CSF 2.0',
      construction_law: 'Construction Business Act',
      quality_law: 'Quality Assurance Act',
      safety_law: 'Industrial Safety Act',
      subcontract_law: 'Subcontract Act',
      iso20000: 'ISO20000',
    },
    settings: {
      theme: 'Theme',
      language: 'Language',
      light: 'Light',
      dark: 'Dark',
      system: 'System Default',
    },
  },
}

export type Locale = 'ja' | 'en'
export const defaultLocale: Locale = 'ja'

export function t(key: string, locale: Locale = defaultLocale): string {
  const keys = key.split('.')
   
  let result: any = messages[locale]
  for (const k of keys) {
    if (result && typeof result === 'object' && k in result) {
      result = result[k]
    } else {
      return key
    }
  }
  return typeof result === 'string' ? result : key
}
