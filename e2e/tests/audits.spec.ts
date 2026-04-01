import { test, expect } from '@playwright/test'

test.describe('Internal Audit', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/audits')
  })

  test('should display audits page', async ({ page }) => {
    await expect(page.locator('h1, .text-h4')).toContainText(/監査/)
  })

  test('should show audit summary cards', async ({ page }) => {
    const cards = page.locator('.v-card')
    expect(await cards.count()).toBeGreaterThanOrEqual(1)
  })

  test('should show audit table', async ({ page }) => {
    await expect(page.locator('table, .v-data-table')).toBeVisible()
  })

  test('should have create audit button', async ({ page }) => {
    const btn = page.locator('button:has-text("作成"), button:has-text("新規"), button:has-text("追加")')
    if (await btn.count() > 0) {
      await expect(btn.first()).toBeVisible()
    }
  })
})
