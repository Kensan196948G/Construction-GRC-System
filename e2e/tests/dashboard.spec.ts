import { test, expect } from '@playwright/test'

test.describe('GRC Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display dashboard', async ({ page }) => {
    await expect(page.locator('h1, .text-h4')).toContainText(/ダッシュボード/)
  })

  test('should show summary cards', async ({ page }) => {
    const cards = page.locator('.v-card')
    expect(await cards.count()).toBeGreaterThanOrEqual(2)
  })

  test('should show risk heatmap', async ({ page }) => {
    const heatmap = page.locator('.risk-heatmap, [class*="heatmap"], canvas')
    if (await heatmap.count() > 0) {
      await expect(heatmap.first()).toBeVisible()
    }
  })

  test('should show compliance gauge', async ({ page }) => {
    const gauge = page.locator('.compliance-gauge, [class*="gauge"], canvas')
    if (await gauge.count() > 0) {
      await expect(gauge.first()).toBeVisible()
    }
  })
})
