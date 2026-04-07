import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import RiskHeatmap from '@/components/RiskHeatmap.vue'

const vuetify = createVuetify()

describe('RiskHeatmap', () => {
  it('renders 5x5 grid (25 cells)', () => {
    const wrapper = mount(RiskHeatmap, {
      global: { plugins: [vuetify] },
    })
    const cells = wrapper.findAll('.heatmap-cell')
    expect(cells).toHaveLength(25)
  })

  it('uses pointer cursor on cells', () => {
    const wrapper = mount(RiskHeatmap, {
      global: { plugins: [vuetify] },
    })
    const cell = wrapper.find('.heatmap-cell')
    expect(cell.exists()).toBe(true)
  })

  it('emits cellClick with likelihood and impact when cell is clicked', async () => {
    const wrapper = mount(RiskHeatmap, {
      global: { plugins: [vuetify] },
    })
    const cells = wrapper.findAll('.heatmap-cell')
    // 最初のセル (likelihood=5, impact=1)
    await cells[0].trigger('click')

    const emitted = wrapper.emitted('cellClick')
    expect(emitted).toBeTruthy()
    expect(emitted).toHaveLength(1)
    const payload = (emitted as Array<Array<{ likelihood: number; impact: number; count: number }>>)[0][0]
    expect(payload).toHaveProperty('likelihood', 5)
    expect(payload).toHaveProperty('impact', 1)
    expect(payload).toHaveProperty('count')
  })

  it('emits cellClick with correct impact index for each column', async () => {
    const wrapper = mount(RiskHeatmap, {
      global: { plugins: [vuetify] },
    })
    const cells = wrapper.findAll('.heatmap-cell')
    // 2番目のセル: likelihood=5, impact=2
    await cells[1].trigger('click')

    const emitted = wrapper.emitted('cellClick')
    expect(emitted).toBeTruthy()
    const payload = (emitted as Array<Array<{ likelihood: number; impact: number; count: number }>>)[0][0]
    expect(payload.impact).toBe(2)
    expect(payload.likelihood).toBe(5)
  })

  it('shows demo data count when no heatmapData provided', () => {
    const wrapper = mount(RiskHeatmap, {
      global: { plugins: [vuetify] },
    })
    // デモデータ: '5-5' => 1
    const cells = wrapper.findAll('.heatmap-cell')
    // last cell in first row = impact=5, likelihood=5
    expect(cells[4].text()).toBe('1')
  })

  it('shows real count when heatmapData provided', () => {
    const wrapper = mount(RiskHeatmap, {
      props: {
        heatmapData: [
          { likelihood: 4, impact: 3, count: 7, level: 'HIGH' as const },
        ],
      },
      global: { plugins: [vuetify] },
    })
    // row for likelihood=4 is index 1 (5,4,3,2,1), cell for impact=3 is index 2
    const cells = wrapper.findAll('.heatmap-cell')
    expect(cells[7].text()).toBe('7')
  })
})
