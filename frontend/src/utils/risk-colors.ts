import type { RiskLevel } from '@/types'

export interface RiskLevelStyle {
  color: string
  background: string
  border: string
}

const RISK_LEVEL_STYLES: Record<RiskLevel, RiskLevelStyle> = {
  LOW: {
    color: '#1B5E20',
    background: '#C8E6C9',
    border: '#4CAF50',
  },
  MEDIUM: {
    color: '#E65100',
    background: '#FFE0B2',
    border: '#FF9800',
  },
  HIGH: {
    color: '#B71C1C',
    background: '#FFCDD2',
    border: '#F44336',
  },
  CRITICAL: {
    color: '#FFFFFF',
    background: '#B71C1C',
    border: '#D50000',
  },
}

const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
  LOW: '低',
  MEDIUM: '中',
  HIGH: '高',
  CRITICAL: '重大',
}

export function getRiskLevelColor(level: RiskLevel): RiskLevelStyle {
  return RISK_LEVEL_STYLES[level]
}

export function getRiskLevelLabel(level: RiskLevel): string {
  return RISK_LEVEL_LABELS[level]
}

/**
 * ヒートマップセルの背景色を返す
 * リスクスコア（likelihood x impact）に基づいて色を決定
 */
export function getHeatmapCellColor(
  likelihood: number,
  impact: number
): string {
  const score = likelihood * impact

  if (score >= 20) return '#B71C1C' // CRITICAL - 濃い赤
  if (score >= 12) return '#F44336' // HIGH - 赤
  if (score >= 6) return '#FF9800' // MEDIUM - オレンジ
  if (score >= 1) return '#4CAF50' // LOW - 緑
  return '#E0E0E0' // スコアなし - グレー
}
