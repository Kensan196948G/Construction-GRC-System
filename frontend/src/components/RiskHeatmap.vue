<script setup lang="ts">

import type { HeatmapCell } from '@/store/risks'

interface Props {
  heatmapData?: HeatmapCell[]
}

const props = withDefaults(defineProps<Props>(), {
  heatmapData: () => [],
})

const emit = defineEmits<{
  cellClick: [{ likelihood: number; impact: number; count: number }]
}>()

const onCellClick = (likelihood: number, impact: number) => {
  const count = getCellCount(likelihood, impact)
  emit('cellClick', { likelihood, impact, count })
}

const likelihoodLabels = ['5 - ほぼ確実', '4 - 可能性高', '3 - 可能性中', '2 - 可能性低', '1 - まれ']
const impactLabels = ['1 - 軽微', '2 - 小', '3 - 中', '4 - 大', '5 - 甚大']

const getCellLevel = (likelihood: number, impact: number): string => {
  const score = likelihood * impact
  if (score >= 15) return 'CRITICAL'
  if (score >= 9) return 'HIGH'
  if (score >= 4) return 'MEDIUM'
  return 'LOW'
}

const getCellColor = (likelihood: number, impact: number): string => {
  const level = getCellLevel(likelihood, impact)
  const colors: Record<string, string> = {
    LOW: '#4CAF50',
    MEDIUM: '#FFC107',
    HIGH: '#FF9800',
    CRITICAL: '#F44336',
  }
  return colors[level] || '#E0E0E0'
}

const getCellCount = (likelihood: number, impact: number): number => {
  if (!props.heatmapData || props.heatmapData.length === 0) {
    // デモデータ
    const demo: Record<string, number> = {
      '5-5': 1, '5-4': 0, '5-3': 1, '4-5': 1, '4-4': 2,
      '3-4': 3, '3-3': 2, '3-2': 1, '2-3': 2, '2-2': 4,
      '2-1': 1, '1-2': 3, '1-1': 3,
    }
    return demo[`${likelihood}-${impact}`] || 0
  }
  const cell = props.heatmapData.find(
    (c) => c.likelihood === likelihood && c.impact === impact
  )
  return cell?.count || 0
}
</script>

<template>
  <div class="heatmap-container">
    <table class="heatmap-table">
      <thead>
        <tr>
          <th class="axis-label">発生可能性 ＼ 影響度</th>
          <th v-for="label in impactLabels" :key="label" class="impact-header">
            {{ label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(label, rowIdx) in likelihoodLabels" :key="label">
          <td class="likelihood-label">{{ label }}</td>
          <td
            v-for="impactIdx in 5"
            :key="impactIdx"
            class="heatmap-cell"
            :style="{
              backgroundColor: getCellColor(5 - rowIdx, impactIdx),
              color: getCellLevel(5 - rowIdx, impactIdx) === 'MEDIUM' ? '#333' : '#fff',
            }"
            @click="onCellClick(5 - rowIdx, impactIdx)"
          >
            <span class="cell-count">{{ getCellCount(5 - rowIdx, impactIdx) }}</span>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="legend mt-4 d-flex justify-center ga-4">
      <div class="d-flex align-center">
        <span class="legend-box" style="background: #4CAF50" /><span class="ml-1 text-caption">LOW</span>
      </div>
      <div class="d-flex align-center">
        <span class="legend-box" style="background: #FFC107" /><span class="ml-1 text-caption">MEDIUM</span>
      </div>
      <div class="d-flex align-center">
        <span class="legend-box" style="background: #FF9800" /><span class="ml-1 text-caption">HIGH</span>
      </div>
      <div class="d-flex align-center">
        <span class="legend-box" style="background: #F44336" /><span class="ml-1 text-caption">CRITICAL</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.heatmap-container {
  overflow-x: auto;
}

.heatmap-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.heatmap-table th,
.heatmap-table td {
  border: 1px solid #e0e0e0;
  padding: 8px;
  text-align: center;
  font-size: 0.85rem;
}

.axis-label {
  background: #f5f5f5;
  font-weight: 600;
  min-width: 140px;
}

.impact-header {
  background: #f5f5f5;
  font-weight: 600;
  font-size: 0.75rem !important;
}

.likelihood-label {
  background: #f5f5f5;
  font-weight: 600;
  font-size: 0.75rem;
  text-align: left;
  padding-left: 12px;
}

.heatmap-cell {
  cursor: pointer;
  min-width: 60px;
  height: 60px;
  font-weight: bold;
  font-size: 1.1rem;
  transition: opacity 0.2s;
}

.heatmap-cell:hover {
  opacity: 0.85;
}

.cell-count {
  font-size: 1.2rem;
  font-weight: 700;
}

.legend-box {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 2px;
}
</style>
