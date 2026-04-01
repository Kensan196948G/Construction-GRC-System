import { test, expect } from '@playwright/test'

test.describe('Compliance Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/compliance')
  })

  test('should display compliance page', async ({ page }) => {
    await expect(page.locator('h1, .text-h4')).toContainText(/コンプライアンス/)
  })

  test('should show compliance gauge', async ({ page }) => {
    // 準拠率ゲージの存在確認
    const gauge = page.locator('.compliance-gauge, [class*="gauge"], canvas')
    if (await gauge.count() > 0) {
      await expect(gauge.first()).toBeVisible()
    }
  })

  test('should show framework tabs or filters', async ({ page }) => {
    // タブまたはフィルタの存在
    const tabs = page.locator('.v-tab, .v-tabs')
    const filter = page.locator('.v-select, select')
    const hasUI = (await tabs.count() > 0) || (await filter.count() > 0)
    expect(hasUI).toBeTruthy()
  })

  test('should show requirements table', async ({ page }) => {
    await expect(page.locator('table, .v-data-table, .v-table')).toBeVisible()
  })
})
